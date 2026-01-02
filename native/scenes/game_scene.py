"""
主游戏场景
"""

import pygame
from typing import Optional, List, Tuple, Dict, Any
from queue import Queue
from .base_scene import BaseScene
from ..game.game import CTFGame
from ..map.map import GameMap
from ..renderer.renderer import Renderer
from ..utils import Team, Direction, GameStats, get_config, TILE_SIZE
from ..managers import (
    InputManager,
    KeyboardInputStrategy,
    RemoteInputStrategy,
    HybridInputStrategy,
    InputObserver,
    PhysicsManager,
    CollisionCallbacks,
    MapManager,
    UIManager,
    UIComponentType,
    SocketManager,
    SocketEvent,
    GameStateManager,
)


class GameScene(BaseScene, InputObserver):
    """
    主游戏场景
    负责游戏的主要逻辑和渲染
    实现 InputObserver 接口以接收输入变化通知
    """
    
    def __init__(self, scene_manager):
        super().__init__('Game', scene_manager)
        self.game: Optional[CTFGame] = None
        self.renderer: Optional[Renderer] = None
        self.input_manager: Optional[InputManager] = None
        self.physics_manager: Optional[PhysicsManager] = None
        self.map_manager: Optional[MapManager] = None
        self.game_stats: Optional[GameStats] = None
        self.ui_manager: Optional[UIManager] = None
        self.socket_manager: Optional[SocketManager] = None
        self.game_state_manager: Optional[GameStateManager] = None
        # 累积的游戏时间（毫秒），用于 WebSocket status 消息中的 time 字段
        self._elapsed_time_ms: int = 0
        # 后端返回的待处理动作队列（由 WebSocket 线程写入，主线程消费）
        self._pending_actions: "Queue[Dict[str, Any]]" = Queue()
        self.initialized = False
        
        # pygame sprite groups
        self.left_team_players_group: Optional[pygame.sprite.Group] = None
        self.right_team_players_group: Optional[pygame.sprite.Group] = None
        self.left_team_flags_group: Optional[pygame.sprite.Group] = None
        self.right_team_flags_group: Optional[pygame.sprite.Group] = None
    
    def preload(self):
        """预加载游戏场景资源"""
        # 游戏资源已在 Preloader 场景加载
        pass
    
    def create(self):
        """创建游戏场景"""
        # 重置游戏结束处理标志（从 GameOver 重新开始时需要）
        if hasattr(self, '_game_over_handled'):
            delattr(self, '_game_over_handled')
        
        if self.initialized:
            # 如果已经初始化，需要重新初始化游戏状态
            print("[Game] 游戏场景已初始化，重新初始化游戏状态")
            if self.game:
                # 重置游戏状态
                self.game.state.game_started = False
                self.game.state.game_paused = False
                self.game.state.game_over = False
                self.game.state.winner = None
                self.game.state.left_team_score = 0
                self.game.state.right_team_score = 0
            return
        
        print("[Game] 创建游戏场景")
        
        # 初始化地图管理器
        # 创建地图和游戏（从配置读取）
        config = get_config()
        
        # 从配置文件读取地图尺寸（必须从配置文件读取）
        map_width = config.map_width
        map_height = config.map_height
        print(f"[Game] 从配置文件读取地图尺寸: {map_width}x{map_height}")
        
        # 设置 MapManager（使用配置中的地图尺寸）
        self._setup_map_manager()
        
        # 确保 MapManager 使用配置文件中的尺寸
        self.map_manager.map_width = map_width
        self.map_manager.map_height = map_height
        
        # 使用 MapManager 生成地图（参考 frontend 的 generateMap 逻辑）
        # 生成墙壁和障碍物
        self.map_manager.generate_map_from_config()
        
        # 获取目标区域和监狱位置（参考 frontend: generateTargetsAndPrisons）
        # Frontend 使用 create3x3grid 创建 3x3 网格
        # 目标区域 Y 坐标: mapHeight / 2 (floor)
        # 监狱 Y 坐标: mapHeight - 3 (floor)
        # L队 X 坐标: 2
        # R队 X 坐标: mapWidth - 3
        
        def create_3x3_grid(center_x: int, center_y: int) -> List[Tuple[int, int]]:
            """
            创建 3x3 网格位置（参考 frontend: create3x3grid）
            顺序必须与 frontend 完全一致：
            [0] (x-1, y-1), [1] (x, y-1), [2] (x+1, y-1)
            [3] (x-1, y),   [4] (x, y),   [5] (x+1, y)
            [6] (x-1, y+1), [7] (x, y+1), [8] (x+1, y+1)
            """
            return [
                (center_x - 1, center_y - 1), (center_x, center_y - 1), (center_x + 1, center_y - 1),
                (center_x - 1, center_y),     (center_x, center_y),     (center_x + 1, center_y),
                (center_x - 1, center_y + 1), (center_x, center_y + 1), (center_x + 1, center_y + 1)
            ]
        
        target_y = map_height // 2  # floor(mapHeight / 2)
        prison_y = map_height - 3   # floor(mapHeight - 3)
        
        left_target = create_3x3_grid(2, target_y)
        right_target = create_3x3_grid(map_width - 3, target_y)
        left_prison = create_3x3_grid(2, prison_y)
        right_prison = create_3x3_grid(map_width - 3, prison_y)
        
        # 获取生成的地图数据
        walls = self.map_manager.get_walls()
        obstacles_data = self.map_manager.get_obstacles()
        obstacles = obstacles_data.get("obstacles1", []) + obstacles_data.get("obstacles2", [])
        
        # 使用 MapManager 生成完整地图数据
        self.map_manager.generate_map(
            walls=walls,
            obstacles=obstacles,
            left_target=left_target,
            right_target=right_target,
            left_prison=left_prison,
            right_prison=right_prison
        )
        
        # 使用 MapManager 的 game_map
        game_map = self.map_manager.game_map
        if not game_map:
            raise RuntimeError("地图生成失败！无法从配置文件生成地图。")
        
        print(f"[Game] 使用配置文件生成地图: {map_width}x{map_height}")
        
        self.game = CTFGame(game_map)
        self.game.initialize(
            num_players=config.num_players,
            num_flags=config.num_flags
        )

        # 初始化 GameStateManager（用于与前端/SocketManager 状态对齐）
        self.game_state_manager = GameStateManager.get_instance()
        # 将地图和团队区域信息写入 GameStateManager，方便其他系统使用
        self.game_state_manager.generate_team_states(map_width, map_height)

        # 创建渲染器（传入 MapManager）
        if self.screen:
            screen_width = self.screen.get_width()
            screen_height = self.screen.get_height()
            self.renderer = Renderer(self.game, screen_width, screen_height, self.map_manager)
        
        # 创建输入管理器（使用混合策略：键盘 + 远程控制）
        self._setup_input_manager()
        
        # 创建物理系统管理器
        self._setup_physics_manager()
        
        # 创建游戏统计系统
        self.game_stats = GameStats()

        # 设置 WebSocket 连接并向 Backend 发送 init 消息
        self._setup_socket_manager_and_send_init(
            map_width=map_width,
            map_height=map_height,
            walls=walls,
            left_target=left_target,
            right_target=right_target,
            left_prison=left_prison,
            right_prison=right_prison,
        )

        # 创建 UI 管理器
        if self.screen:
            print(f"[Game] Screen 已设置: {self.screen.get_width()}x{self.screen.get_height()}")
            self._setup_ui_manager()
        else:
            print("[Game] 警告: Screen 未设置，无法创建 UI 管理器")
        
        self.initialized = True
        print("[Game] 游戏场景创建完成")

    def _setup_socket_manager_and_send_init(
        self,
        map_width: int,
        map_height: int,
        walls,
        left_target,
        right_target,
        left_prison,
        right_prison,
    ):
        """
        设置 SocketManager，并向 Backend 发送 init 消息。
        参考 frontend SocketManager 实现以及 todo/3.14, 3.21 中的协议说明。
        """
        config = get_config()

        # 获取每个队伍的服务器 URL（如果未配置，则不启用 socket）
        l_url = config.get_team_server_url("L")
        r_url = config.get_team_server_url("R")

        if not l_url and not r_url:
            print("[Game] 未配置 WebSocket 服务器地址，跳过 SocketManager 初始化")
            return

        print(f"[Game] 配置的 WebSocket 服务器: L={l_url}, R={r_url}")

        self.socket_manager = SocketManager()

        # 订阅连接/错误/动作事件，用 GameStateManager 跟踪连接状态，并把动作推送到队列
        if not self.game_state_manager:
            self.game_state_manager = GameStateManager.get_instance()

        def _on_connect(team: Team):
            print(f"[Game] {team.value} 队 WebSocket 已连接")
            if team == Team.LEFT:
                self.game_state_manager.set_l_team_connection(True)
            else:
                self.game_state_manager.set_r_team_connection(True)

        def _on_disconnect(team: Team):
            print(f"[Game] {team.value} 队 WebSocket 已断开")
            if team == Team.LEFT:
                self.game_state_manager.set_l_team_connection(False)
            else:
                self.game_state_manager.set_r_team_connection(False)

        def _on_error(team: Team, error: Any):
            print(f"[Game] {team.value} 队 WebSocket 错误: {error}")
            # 记录错误信息，但不让游戏崩溃
            self.game_state_manager.set_error(str(error))

        def _on_actions_received(team: Team, actions: Dict[str, Any]):
            """
            WebSocket 线程回调：只把数据放入线程安全队列，实际更新在主线程执行。
            actions: {"players": {...}, "paths": {...}, "timings": {...}?}
            """
            self._pending_actions.put({"team": team, "actions": actions})

        self.socket_manager.on(SocketEvent.CONNECT, _on_connect)
        self.socket_manager.on(SocketEvent.DISCONNECT, _on_disconnect)
        self.socket_manager.on(SocketEvent.ERROR, _on_error)
        self.socket_manager.on(SocketEvent.ACTIONS_RECEIVED, _on_actions_received)

        # 建立连接
        if l_url:
            self.socket_manager.connect_team(Team.LEFT, l_url)
        if r_url:
            self.socket_manager.connect_team(Team.RIGHT, r_url)

        # 构建 init 消息 payload 并发送
        # walls 已经是 {"x": int, "y": int} 列表（来自 MapManager）
        obstacles_data = self.map_manager.get_obstacles() if self.map_manager else {}
        obstacles1 = obstacles_data.get("obstacles1", [])
        obstacles2 = obstacles_data.get("obstacles2", [])

        params: Dict[str, Any] = {
            "map_width": map_width,
            "map_height": map_height,
            "walls": walls,
            "obstacles1": obstacles1,
            "obstacles2": obstacles2,
            "lteam_prison": left_prison,
            "lteam_target": left_target,
            "rteam_prison": right_prison,
            "rteam_target": right_target,
            "num_players": config.num_players,
            "num_flags": config.num_flags,
        }

        # init 消息是单向的，Backend 不会返回响应
        self.socket_manager.send_game_init(params)
    
    def _setup_map_manager(self):
        """设置地图管理器"""
        # 获取 MapManager 实例（单例）
        self.map_manager = MapManager()
        
        # 获取配置
        config = get_config()
        
        # 从配置文件读取地图尺寸（优先使用配置）
        config_map_width = config.map_width
        config_map_height = config.map_height
        
        # 设置地图参数
        self.map_manager.map_width = config_map_width
        self.map_manager.map_height = config_map_height
        self.map_manager.tile_size = TILE_SIZE
        
        # 加载 tiles.png 图片
        from ..utils.assets import TILES_SPRITESHEET
        tiles_image = None
        if TILES_SPRITESHEET.exists():
            try:
                tiles_image = pygame.image.load(str(TILES_SPRITESHEET)).convert_alpha()
                print(f"[Game] 加载 tiles.png 成功: {TILES_SPRITESHEET}")
            except Exception as e:
                print(f"[Game] 加载 tiles.png 失败: {e}")
        else:
            print(f"[Game] tiles.png 不存在: {TILES_SPRITESHEET}")
        
        # 初始化图层
        if tiles_image:
            self.map_manager.initialize_layers(tiles_image)
        else:
            print("[Game] 警告：无法加载 tiles.png，背景图层将无法渲染")
        
        # 设置地图参数（窗口大小等于地图大小，地图从 (0, 0) 开始）
        if self.screen:
            screen_width = self.screen.get_width()
            screen_height = self.screen.get_height()
            center_x = screen_width // 2
            center_y = screen_height // 2
            
            map_width = self.map_manager.map_width
            map_height = self.map_manager.map_height
            tile_size = self.map_manager.tile_size
            
            # 窗口大小等于地图大小，地图从 (0, 0) 开始
            map_x = 0
            map_y = 0
            
            self.map_manager.set_map_params({
                "mapWidth": map_width,
                "mapHeight": map_height,
                "mapX": map_x,
                "mapY": map_y,
                "tileSize": tile_size,
                "centerX": center_x,
                "centerY": center_y
            })
        
        print(f"[Game] 地图管理器已设置: {self.map_manager.map_width}x{self.map_manager.map_height}, 图块大小: {self.map_manager.tile_size}")
    
    def _setup_physics_manager(self):
        """设置物理系统管理器"""
        if not self.game:
            return
        
        # 创建 sprite groups
        self.left_team_players_group = pygame.sprite.Group()
        self.right_team_players_group = pygame.sprite.Group()
        self.left_team_flags_group = pygame.sprite.Group()
        self.right_team_flags_group = pygame.sprite.Group()
        
        # 将玩家和旗帜添加到 groups
        for player in self.game.state.left_team_players:
            self.left_team_players_group.add(player)
        for player in self.game.state.right_team_players:
            self.right_team_players_group.add(player)
        for flag in self.game.state.left_team_flags:
            self.left_team_flags_group.add(flag)
        for flag in self.game.state.right_team_flags:
            self.right_team_flags_group.add(flag)
        
        # 创建碰撞回调
        callbacks = CollisionCallbacks()
        callbacks.on_score_update = self._on_score_update
        callbacks.on_create_flag = self._on_create_flag
        
        # 创建物理系统管理器
        self.physics_manager = PhysicsManager(self.game.game_map, callbacks)
        self.physics_manager.set_game_objects(
            self.left_team_players_group,
            self.right_team_players_group,
            self.left_team_flags_group,
            self.right_team_flags_group
        )
        
        # 设置区域（从地图获取位置）
        left_target_positions = self.game.game_map.get_team_target_positions(Team.LEFT)
        right_target_positions = self.game.game_map.get_team_target_positions(Team.RIGHT)
        left_prison_positions = self.game.game_map.get_team_prison_positions(Team.LEFT)
        right_prison_positions = self.game.game_map.get_team_prison_positions(Team.RIGHT)
        
        left_target = [(pos.x, pos.y) for pos in left_target_positions]
        right_target = [(pos.x, pos.y) for pos in right_target_positions]
        left_prison = [(pos.x, pos.y) for pos in left_prison_positions]
        right_prison = [(pos.x, pos.y) for pos in right_prison_positions]
        
        self.physics_manager.set_zones(
            left_target, right_target, left_prison, right_prison
        )
        
        print("[Game] 物理系统管理器已设置")
    
    def _setup_ui_manager(self):
        """设置 UI 管理器"""
        if not self.screen:
            print("[Game] 警告: _setup_ui_manager 被调用但 screen 为 None")
            return
        
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        print(f"[Game] 开始设置 UI 管理器: screen={screen_width}x{screen_height}")
        
        # 创建 UI 管理器
        self.ui_manager = UIManager(self.screen)
        print(f"[Game] UI 管理器已创建")
        
        # 创建教程文本组件（居中显示，参考 frontend）
        tutorial_component = self.ui_manager.create_component(
            'tutorial',
            UIComponentType.TUTORIAL_TEXT,
            screen_width // 2,
            screen_height // 2
        )
        # 确保教程文本默认显示（参考 frontend，tutorial 组件创建后默认可见）
        self.ui_manager.show_component('tutorial')
        print(f"[Game] Tutorial 组件已创建: x={screen_width // 2}, y={screen_height // 2}, visible={tutorial_component.visible if tutorial_component else 'None'}")
        
        # 创建游戏结束文本组件（居中显示）
        self.ui_manager.create_component(
            'game_over',
            UIComponentType.GAME_OVER_TEXT,
            screen_width // 2,
            screen_height // 2 - 50
        )
        
        # 初始隐藏游戏结束文本
        self.ui_manager.hide_component('game_over')
        
        print("[Game] UI 管理器已设置")
    
    def _on_score_update(self, team: Team):
        """
        得分更新回调（完全参考 frontend: updateTeamScore）
        
        Frontend 逻辑：
        1. 更新 GameStateManager 分数
        2. 更新 UI
        3. 检查游戏结束条件（newScore === NUM_FLAGS）
        """
        if not self.game:
            return
        
        # 更新分数（参考 frontend: gameState.updateLTeamScore(newScore)）
        if team == Team.LEFT:
            new_score = self.game.state.left_team_score + 1
            self.game.state.left_team_score = new_score
        else:
            new_score = self.game.state.right_team_score + 1
            self.game.state.right_team_score = new_score
        
        # 记录统计
        if self.game_stats:
            self.game_stats.record_score(team)
        
        print(f"[Game] {team.value}队得分！当前比分: L={self.game.state.left_team_score}, R={self.game.state.right_team_score}")
        
        # 检查游戏结束条件（参考 frontend: if (newScore === this.NUM_FLAGS)）
        # Frontend 中，当分数等于旗帜数量时游戏结束
        num_flags = self.game.state.num_flags
        if new_score == num_flags:
            print(f"[Game] {team.value}队达到胜利条件（{new_score}/{num_flags}）！游戏结束")
            self._end_game(team)
    
    def _on_create_flag(self, x: int, y: int, team: Team, can_pickup: bool):
        """
        创建旗帜回调
        
        Args:
            x: X坐标（格子坐标）
            y: Y坐标（格子坐标）
            team: 队伍
            can_pickup: 是否可以拾取
        
        Returns:
            创建的旗帜对象
        """
        from ..objects.flag import Flag
        
        # 生成旗帜ID
        flag_id = f"{team.value}{len(self.game.state.get_all_flags())}"
        
        # 创建旗帜
        flag = Flag(flag_id, team, x, y)
        
        # 设置是否可以拾取
        if not can_pickup:
            flag.is_scored = True
        
        # 添加到对应的旗帜组
        if team == Team.LEFT:
            self.game.state.left_team_flags.append(flag)
            if self.left_team_flags_group:
                self.left_team_flags_group.add(flag)
        else:
            self.game.state.right_team_flags.append(flag)
            if self.right_team_flags_group:
                self.right_team_flags_group.add(flag)
        
        return flag
    
    def _setup_input_manager(self):
        """设置输入管理器"""
        # 创建键盘输入策略（支持WASD和方向键）
        keyboard_strategy = KeyboardInputStrategy()
        
        # 创建远程控制策略
        remote_strategy = RemoteInputStrategy()
        
        # 创建混合策略（键盘优先）
        hybrid_strategy = HybridInputStrategy(keyboard_strategy, remote_strategy)
        
        # 创建输入管理器
        self.input_manager = InputManager(hybrid_strategy)
        
        # 设置游戏控制回调
        self.input_manager.set_game_start_callback(self._on_game_start)
        self.input_manager.set_game_pause_callback(self._on_game_pause)
        
        # 注册为观察者（监听输入变化）
        self.input_manager.subscribe(self)
        
        print("[Game] 输入管理器已设置（键盘 + 远程控制）")
    
    def _on_game_start(self):
        """游戏开始回调（参考 frontend: startGame）"""
        if self.game and not self.game.state.game_started:
            self.game.state.game_started = True
            if self.game_stats:
                self.game_stats.start_game()
            # 游戏开始时重置时间计数，用于 status 消息中的 time 字段
            self._elapsed_time_ms = 0
            # 隐藏教程文本（参考 frontend: this.uiManager.hideComponent('tutorial')）
            if self.ui_manager:
                self.ui_manager.hide_component('tutorial')
            print("[Game] 游戏开始")
    
    def _on_game_pause(self):
        """游戏暂停/继续回调"""
        if self.game and self.game.state.game_started:
            self.game.state.game_paused = not self.game.state.game_paused
            status = "暂停" if self.game.state.game_paused else "继续"
            print(f"[Game] 游戏{status}")
    
    def _end_game(self, winner: Team):
        """
        结束游戏
        
        注意：这里只设置游戏状态，不切换场景
        场景切换在 update() 方法中统一处理，避免重复切换
        """
        if self.game:
            self.game.state.game_over = True
            self.game.state.winner = winner
            if self.game_stats:
                self.game_stats.end_game(winner)
            print(f"[Game] 游戏结束，{winner.value}队获胜！")
    
    
    def update(self, delta_time: int):
        """
        更新游戏场景
        
        Args:
            delta_time: 时间增量（毫秒）
        """
        if not self.input_manager or not self.game:
            return
        
        # 即使游戏未开始，也要更新输入管理器（用于处理空格键开始游戏）
        # 参考 frontend: if (!this.gameStarted) { this.inputManager.update(time, delta); return }
        if not self.game.state.game_started:
            self.input_manager.update(delta_time)
            # 更新 UI 以显示教程文本（参考 frontend）
            if self.ui_manager:
                self.ui_manager.show_component('tutorial')
                self.ui_manager.hide_component('game_over')
            return
        
        if self.game.state.game_paused:
            return
        
        # 更新输入管理器
        self.input_manager.update(delta_time)
        
        # 更新所有玩家
        for player in self.game.state.left_team_players:
            player.update(delta_time)
        
        for player in self.game.state.right_team_players:
            player.update(delta_time)
        
        # 更新物理系统（碰撞检测）
        if self.physics_manager:
            self.physics_manager.update()
        
        # 更新旗帜位置（如果被携带）
        for flag in self.game.state.get_all_flags():
            if flag.is_picked_up and flag.carried_by:
                flag.update_position(
                    flag.carried_by.pixel_x,
                    flag.carried_by.pixel_y
                )

        # 累积时间，用于发送给 Backend 的 time 字段（毫秒）
        self._elapsed_time_ms += delta_time

        # 先应用 Backend 返回的动作，再根据最新状态发送 status
        self._apply_backend_actions()

        # 向 Backend 发送当前状态（仅在至少有一队已连接时发送）
        if self.socket_manager and (
            self.socket_manager.is_connected(Team.LEFT)
            or self.socket_manager.is_connected(Team.RIGHT)
        ):
            self._send_game_status_to_backend()

        # 更新 UI
        if self.ui_manager and self.game:
            # 更新游戏状态显示
            if self.game.state.game_over:
                # 显示游戏结束文本
                self.ui_manager.show_component('game_over')
                winner = self.game.state.winner.value if self.game.state.winner else None
                self.ui_manager.update_component('game_over', winner)
                # 隐藏教程文本
                self.ui_manager.hide_component('tutorial')
            elif not self.game.state.game_started:
                # 显示教程文本
                self.ui_manager.show_component('tutorial')
                self.ui_manager.hide_component('game_over')
            else:
                # 游戏进行中，隐藏教程和游戏结束文本
                self.ui_manager.hide_component('tutorial')
                self.ui_manager.hide_component('game_over')
        
        # 检查游戏是否结束（只切换一次，避免重复切换）
        if self.game.state.game_over and not hasattr(self, '_game_over_handled'):
            winner = self.game.state.winner
            if winner:
                # 标记已处理，避免重复切换场景
                self._game_over_handled = True

                # 游戏结束时发送 finished 消息给 Backend
                if self.socket_manager:
                    self.socket_manager.send_game_finished(
                        self.game.state.left_team_score,
                        self.game.state.right_team_score,
                    )

                self.start_scene(
                    'GameOver',
                    {
                        'winner': winner,
                        'stats': self.game_stats.get_summary()
                        if self.game_stats
                        else None,
                    },
                )

    def _apply_backend_actions(self):
        """
        应用 Backend 返回的玩家动作。
        从队列中取出所有待处理的动作，并更新玩家方向。
        """
        if not self.game:
            # 没有游戏实例时，清空队列即可
            while not self._pending_actions.empty():
                self._pending_actions.get()
            return

        # 构建玩家名称到对象的映射，加速查找
        players_by_name = {
            player.name: player
            for player in (
                self.game.state.left_team_players
                + self.game.state.right_team_players
            )
        }

        while not self._pending_actions.empty():
            item = self._pending_actions.get()
            actions = item.get("actions", {})
            players_obj: Dict[str, str] = (
                actions.get("players", {}) if isinstance(actions, dict) else {}
            )

            for player_name, direction_str in players_obj.items():
                player = players_by_name.get(player_name)
                if not player:
                    continue
                # 将方向字符串转换为 Direction 枚举
                direction = Direction.STAY
                if direction_str == "up":
                    direction = Direction.UP
                elif direction_str == "down":
                    direction = Direction.DOWN
                elif direction_str == "left":
                    direction = Direction.LEFT
                elif direction_str == "right":
                    direction = Direction.RIGHT

                if direction != Direction.STAY:
                    # 复用已有的动作设置逻辑
                    self.game.set_player_action(player_name, direction)

    def _send_game_status_to_backend(self):
        """
        构建并发送当前游戏状态到 Backend。
        消息格式与 Backend/Frontend 保持一致（参见 todo/3.14, 3.21）。
        """
        if not self.game or not self.socket_manager:
            return

        # 构建玩家和旗帜状态
        def _build_player_status(team: Team):
            players = (
                self.game.state.left_team_players
                if team == Team.LEFT
                else self.game.state.right_team_players
            )
            result: List[Dict[str, Any]] = []
            for p in players:
                result.append(
                    {
                        "name": p.name,
                        "posX": int(p.grid_x),
                        "posY": int(p.grid_y),
                        "inPrison": bool(p.in_prison),
                        "hasFlag": bool(p.has_flag),
                    }
                )
            return result

        def _build_flag_status(team: Team):
            flags = (
                self.game.state.left_team_flags
                if team == Team.LEFT
                else self.game.state.right_team_flags
            )
            result: List[Dict[str, Any]] = []
            for f in flags:
                result.append(
                    {
                        "posX": int(f.grid_x),
                        "posY": int(f.grid_y),
                        "canPickup": bool(f.can_pickup),
                        "pickedUp": bool(f.is_picked_up),
                    }
                )
            return result

        params = {
            "time": int(self._elapsed_time_ms),
            "lteam_player_status": _build_player_status(Team.LEFT),
            "lteam_flag_status": _build_flag_status(Team.LEFT),
            "rteam_player_status": _build_player_status(Team.RIGHT),
            "rteam_flag_status": _build_flag_status(Team.RIGHT),
            "lteam_score": int(self.game.state.left_team_score),
            "rteam_score": int(self.game.state.right_team_score),
        }

        self.socket_manager.send_game_status(params)
    
    def handle_event(self, event: pygame.event.Event):
        """处理事件"""
        if not self.game:
            return
        
        # 处理键盘输入（区分 WASD 和方向键）
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # ESC 退出游戏
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif self.game.state.game_started and not self.game.state.game_paused:
                # WASD 控制 L0 玩家
                if event.key == pygame.K_w:
                    self._handle_player_input("L0", Direction.UP)
                elif event.key == pygame.K_s:
                    self._handle_player_input("L0", Direction.DOWN)
                elif event.key == pygame.K_a:
                    self._handle_player_input("L0", Direction.LEFT)
                elif event.key == pygame.K_d:
                    self._handle_player_input("L0", Direction.RIGHT)
                # 方向键控制 R0 玩家
                elif event.key == pygame.K_UP:
                    self._handle_player_input("R0", Direction.UP)
                elif event.key == pygame.K_DOWN:
                    self._handle_player_input("R0", Direction.DOWN)
                elif event.key == pygame.K_LEFT:
                    self._handle_player_input("R0", Direction.LEFT)
                elif event.key == pygame.K_RIGHT:
                    self._handle_player_input("R0", Direction.RIGHT)
        
        # 将其他事件传递给输入管理器处理（如空格键、P键等）
        if self.input_manager:
            self.input_manager.handle_event(event)
    
    def on_input_change(self, direction: Direction):
        """
        输入变化回调（实现 InputObserver 接口）
        
        Args:
            direction: 新的输入方向
        """
        if not self.game or not self.game.state.game_started:
            return
        
        pass
    
    def _handle_player_input(self, player_name: str, direction: Direction):
        """
        处理玩家输入
        
        Args:
            player_name: 玩家名称（如 "L0", "R0"）
            direction: 输入方向
        """
        if not self.game or not self.game.state.game_started:
            return
        
        if direction == Direction.STAY:
            return
        
        # 找到对应的玩家
        all_players = self.game.state.left_team_players + self.game.state.right_team_players
        for player in all_players:
            if player.name == player_name and not player.in_prison:
                # 检查目标位置是否有效（不是墙壁）
                dx, dy = direction.to_vector()
                new_x = player.grid_x + dx
                new_y = player.grid_y + dy
                
                if self.game.game_map.is_valid_position(new_x, new_y):
                    self.game.set_player_action(player.name, direction)
                break
    
    def render(self):
        """渲染游戏场景"""
        if self.renderer and self.screen:
            # 渲染游戏内容（不包括 UI）
            self.renderer.render(self.screen)
        
        # 渲染 UI（使用 UIManager）- 必须在最后渲染，确保显示在地图上方
        if self.ui_manager:
            self.ui_manager.render()
            # 调试：检查 tutorial 组件状态
            tutorial = self.ui_manager.get_component('tutorial')
            if tutorial:
                if not hasattr(tutorial, 'visible') or not tutorial.visible:
                    print(f"[Game] 警告: Tutorial 组件存在但不可见")
                elif not hasattr(tutorial, 'text_surfaces') or not tutorial.text_surfaces:
                    print(f"[Game] 警告: Tutorial 组件可见但 text_surfaces 为空")
    
    def destroy(self):
        """销毁游戏场景"""
        if self.input_manager:
            self.input_manager.unsubscribe(self)
        if self.ui_manager:
            self.ui_manager.destroy_all()
        if self.socket_manager:
            # 确保断开所有 WebSocket 连接并清理监听器
            self.socket_manager.disconnect_all()
        self.input_manager = None
        self.ui_manager = None
        self.game = None
        self.renderer = None
        self.initialized = False
        super().destroy()

