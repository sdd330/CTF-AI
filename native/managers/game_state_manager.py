"""
游戏状态管理器
参考 frontend/src/game/managers/GameStateManager.ts
设计模式：单例模式 + 观察者模式

职责：
- 管理所有游戏状态（gameStarted, gamePaused, gameOver, winner）
- 管理队伍分数（lTeamScore, rTeamScore）
- 管理玩家和旗帜状态
- 管理游戏配置
- 管理 WebSocket 连接状态
- 管理游戏流程状态
"""

import json
from enum import Enum
from typing import Optional, Dict, List, Any, Callable, Set, Tuple
from dataclasses import dataclass, field
from pathlib import Path

from ..utils import Team


class GameFlowState(Enum):
    """游戏流程状态"""
    LOADING = 'loading'
    READY = 'ready'
    PLAYING = 'playing'
    ENDED = 'ended'


class GameFlowSubState(Enum):
    """游戏流程子状态"""
    LOADING_ASSETS = 'loadingAssets'
    LOADING_CONFIG = 'loadingConfig'
    RUNNING = 'running'
    PAUSED = 'paused'


@dataclass
class Position:
    """位置数据"""
    x: int
    y: int


@dataclass
class PlayerPosition:
    """玩家位置数据"""
    name: str
    x: int
    y: int


@dataclass
class TeamState:
    """团队状态"""
    score: int = 0
    player_sprite_choice: int = 1
    flags: List[Position] = field(default_factory=list)
    players: List[PlayerPosition] = field(default_factory=list)
    target: List[Position] = field(default_factory=list)
    prison: List[Position] = field(default_factory=list)


@dataclass
class GameConfig:
    """游戏配置"""
    num_players: int = 3
    num_flags: int = 9
    use_random_flags: bool = True
    map_width: int = 20
    map_height: int = 20
    servers: Dict[str, str] = field(default_factory=dict)
    teams: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class StateSnapshot:
    """游戏状态快照（用于 GameStateManager 内部状态追踪）"""
    # 游戏状态
    game_started: bool = False
    game_paused: bool = False
    game_over: bool = False
    winner: Optional[Team] = None

    # 队伍分数
    l_team_score: int = 0
    r_team_score: int = 0

    # 配置
    config: Optional[GameConfig] = None

    # WebSocket 连接状态
    l_team_connected: bool = False
    r_team_connected: bool = False
    l_team_who: str = '-'
    r_team_who: str = '-'

    # 游戏流程状态
    flow_state: GameFlowState = GameFlowState.LOADING
    flow_sub_state: Optional[GameFlowSubState] = GameFlowSubState.LOADING_ASSETS
    current_scene: str = 'Boot'
    initialized: bool = False
    assets_loaded: bool = False
    config_loaded: bool = False
    error: Optional[str] = None

    # 团队状态
    l_team_state: TeamState = field(default_factory=lambda: TeamState(player_sprite_choice=1))
    r_team_state: TeamState = field(default_factory=lambda: TeamState(player_sprite_choice=4))

    # 地图数据
    walls: List[Position] = field(default_factory=list)
    obstacles1: List[Position] = field(default_factory=list)
    obstacles2: List[Position] = field(default_factory=list)


# 状态变化监听器类型
StateChangeListener = Callable[[StateSnapshot], None]


class GameStateManager:
    """
    游戏状态管理器
    使用单例模式确保全局唯一实例
    """

    _instance: Optional['GameStateManager'] = None

    def __new__(cls) -> 'GameStateManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._state = StateSnapshot()
        self._listeners: Set[StateChangeListener] = set()
        self._initialized = True

    @classmethod
    def get_instance(cls) -> 'GameStateManager':
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """重置单例实例（用于测试）"""
        cls._instance = None

    def get_state(self) -> StateSnapshot:
        """获取当前状态"""
        return self._state

    def _notify_listeners(self) -> None:
        """通知所有监听器状态已变化"""
        for listener in self._listeners:
            try:
                listener(self._state)
            except Exception as e:
                print(f"[GameStateManager] 通知监听器出错: {e}")

    def on_state_change(self, listener: StateChangeListener) -> Callable[[], None]:
        """
        订阅状态变化

        Args:
            listener: 状态变化回调函数

        Returns:
            取消订阅的函数
        """
        self._listeners.add(listener)
        return lambda: self._listeners.discard(listener)

    # ========== 配置相关 ==========

    def load_config(self, config_path: str = 'game_config.json') -> GameConfig:
        """
        加载游戏配置

        Args:
            config_path: 配置文件路径

        Returns:
            游戏配置
        """
        try:
            path = Path(config_path)
            if not path.exists():
                # 尝试在 native 目录下查找
                native_path = Path(__file__).parent.parent / config_path
                if native_path.exists():
                    path = native_path
                else:
                    raise FileNotFoundError(f"配置文件不存在: {config_path}")

            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            setup = data.get('setup', {})
            config = GameConfig(
                num_players=setup.get('numPlayers', 3),
            num_flags=setup.get('numFlags', 9),
                use_random_flags=setup.get('useRandomFlags', True),
                map_width=setup.get('mapWidth', 20),
                map_height=setup.get('mapHeight', 20),
                servers=data.get('servers', {}),
                teams=data.get('teams', [])
            )

            self.set_config(config)
            self._state.config_loaded = True
            self._notify_listeners()

            print(f"[GameStateManager] 配置加载成功: {config}")
            return config

        except Exception as e:
            print(f"[GameStateManager] 加载配置失败，使用默认配置: {e}")

            # 使用默认配置
            config = GameConfig()
            self.set_config(config)
            self._state.config_loaded = True
            self._notify_listeners()

            return config

    def get_config(self) -> Optional[GameConfig]:
        """获取当前配置"""
        return self._state.config

    def set_config(self, config: GameConfig) -> None:
        """设置配置"""
        self._state.config = config
        self._notify_listeners()

    # ========== 游戏控制 ==========

    def start_game(self) -> None:
        """开始游戏"""
        self._state.game_started = True
        self._state.game_paused = False
        self._state.game_over = False
        self._state.flow_state = GameFlowState.PLAYING
        self._state.flow_sub_state = GameFlowSubState.RUNNING
        self._notify_listeners()

    def pause_game(self) -> None:
        """暂停/继续游戏"""
        self._state.game_paused = not self._state.game_paused
        if self._state.game_paused:
            self._state.flow_sub_state = GameFlowSubState.PAUSED
        else:
            self._state.flow_sub_state = GameFlowSubState.RUNNING
        self._notify_listeners()

    def end_game(self, winner: Team) -> None:
        """结束游戏"""
        self._state.game_over = True
        self._state.winner = winner
        self._state.game_started = False
        self._state.flow_state = GameFlowState.ENDED
        self._state.flow_sub_state = None
        self._notify_listeners()

    def reset(self) -> None:
        """重置游戏状态"""
        config = self._state.config
        self._state = StateSnapshot()
        self._state.config = config
        self._notify_listeners()

    def reset_game_state(self) -> None:
        """重置游戏状态（保留配置和团队状态）"""
        self._state.game_started = False
        self._state.game_paused = False
        self._state.game_over = False
        self._state.winner = None
        self._state.l_team_score = 0
        self._state.r_team_score = 0
        self._state.l_team_state.score = 0
        self._state.r_team_state.score = 0
        self._notify_listeners()

    # ========== 分数更新 ==========

    def update_l_team_score(self, score: int) -> None:
        """更新 L 队分数"""
        self._state.l_team_score = score
        self._state.l_team_state.score = score
        self._notify_listeners()

    def update_r_team_score(self, score: int) -> None:
        """更新 R 队分数"""
        self._state.r_team_score = score
        self._state.r_team_state.score = score
        self._notify_listeners()

    # ========== 连接状态更新 ==========

    def set_l_team_connection(self, connected: bool, who: str = '-') -> None:
        """设置 L 队连接状态"""
        self._state.l_team_connected = connected
        self._state.l_team_who = who
        self._notify_listeners()

    def set_r_team_connection(self, connected: bool, who: str = '-') -> None:
        """设置 R 队连接状态"""
        self._state.r_team_connected = connected
        self._state.r_team_who = who
        self._notify_listeners()

    # ========== 团队状态管理 ==========

    def set_l_team_state(self, **kwargs) -> None:
        """设置 L 队状态"""
        for key, value in kwargs.items():
            if hasattr(self._state.l_team_state, key):
                setattr(self._state.l_team_state, key, value)
        self._notify_listeners()

    def set_r_team_state(self, **kwargs) -> None:
        """设置 R 队状态"""
        for key, value in kwargs.items():
            if hasattr(self._state.r_team_state, key):
                setattr(self._state.r_team_state, key, value)
        self._notify_listeners()

    def get_team_states(self) -> Tuple[TeamState, TeamState]:
        """获取团队状态"""
        return self._state.l_team_state, self._state.r_team_state

    # ========== 地图状态管理 ==========

    def set_map_data(self, walls: List[Position] = None,
                     obstacles1: List[Position] = None,
                     obstacles2: List[Position] = None) -> None:
        """设置地图数据"""
        if walls is not None:
            self._state.walls = walls
        if obstacles1 is not None:
            self._state.obstacles1 = obstacles1
        if obstacles2 is not None:
            self._state.obstacles2 = obstacles2
        self._notify_listeners()

    # ========== 游戏流程管理 ==========

    def set_flow_state(self, flow_state: GameFlowState,
                       sub_state: Optional[GameFlowSubState] = None) -> None:
        """设置游戏流程状态"""
        self._state.flow_state = flow_state
        self._state.flow_sub_state = sub_state
        self._notify_listeners()

    def set_assets_loaded(self, loaded: bool = True) -> None:
        """设置资源加载状态"""
        self._state.assets_loaded = loaded
        if loaded and self._state.flow_sub_state == GameFlowSubState.LOADING_ASSETS:
            self._state.flow_sub_state = GameFlowSubState.LOADING_CONFIG
        self._notify_listeners()

    def set_initialized(self, initialized: bool = True) -> None:
        """设置初始化状态"""
        self._state.initialized = initialized
        if initialized:
            self._state.flow_state = GameFlowState.READY
            self._state.flow_sub_state = None
        self._notify_listeners()

    def set_error(self, error: Optional[str]) -> None:
        """设置错误状态"""
        self._state.error = error
        self._notify_listeners()

    def set_current_scene(self, scene: str) -> None:
        """设置当前场景"""
        self._state.current_scene = scene
        self._notify_listeners()

    # ========== TeamStates 生成 ==========

    def generate_targets_and_prisons(self, map_width: int, map_height: int) -> None:
        """
        生成目标区域和监狱位置
        参考 frontend GameStateManager.generateTargetsAndPrisons
        """
        target_y = map_height // 2
        prison_y = map_height - 3

        l_target = self._create_3x3_grid(2, target_y)
        l_prison = self._create_3x3_grid(2, prison_y)
        r_target = self._create_3x3_grid(map_width - 3, target_y)
        r_prison = self._create_3x3_grid(map_width - 3, prison_y)

        self._state.l_team_state.target = l_target
        self._state.l_team_state.prison = l_prison
        self._state.r_team_state.target = r_target
        self._state.r_team_state.prison = r_prison
        self._notify_listeners()

    def generate_players(self, map_width: int) -> None:
        """
        生成玩家位置
        参考 frontend GameStateManager.generatePlayers
        """
        config = self._state.config or GameConfig()
        num_players = config.num_players
        use_random_flags = config.use_random_flags

        if use_random_flags:
            l_players = [PlayerPosition(name=f"L{i}", x=1, y=i + 1) for i in range(num_players)]
            r_players = [PlayerPosition(name=f"R{i}", x=map_width - 2, y=i + 1) for i in range(num_players)]
        else:
            l_players = [PlayerPosition(name=f"L{i}", x=2, y=i + 1) for i in range(num_players)]
            r_players = [PlayerPosition(name=f"R{i}", x=map_width - 3, y=i + 1) for i in range(num_players)]

        self._state.l_team_state.players = l_players
        self._state.r_team_state.players = r_players
        self._notify_listeners()

    def generate_flags(self, map_width: int, map_height: int) -> None:
        """
        生成旗帜位置
        参考 frontend GameStateManager.generateFlags
        """
        import random

        config = self._state.config or GameConfig()
        num_flags = config.num_flags
        use_random_flags = config.use_random_flags

        middle_line = map_width / 2.0
        l_max_x = int(middle_line - 0.1)
        r_min_x = int(middle_line + 0.5)

        obstacles1 = self._state.obstacles1
        obstacles2 = self._state.obstacles2

        def not_contains(arr: List[Position], x: int, y: int) -> bool:
            return not any(p.x == x and p.y == y for p in arr)

        if use_random_flags:
            l_flags = []
            r_flags = []
            max_retries = 1000

            # L队旗帜
            for i in range(num_flags):
                for _ in range(max_retries):
                    x = random.randint(2, l_max_x)
                    y = random.randint(1, map_height - 3)
                    if (not_contains(obstacles1, x, y) and
                        not_contains(obstacles2, x, y - 1) and
                        not_contains(obstacles2, x, y) and
                        not_contains(l_flags, x, y)):
                        l_flags.append(Position(x=x, y=y))
                        break
                else:
                    l_flags.append(Position(x=min(1, l_max_x), y=i + 1))

            # R队旗帜
            for i in range(num_flags):
                for _ in range(max_retries):
                    x = random.randint(r_min_x, map_width - 2)
                    y = random.randint(1, map_height - 3)
                    if (not_contains(obstacles1, x, y) and
                        not_contains(obstacles2, x, y - 1) and
                        not_contains(obstacles2, x, y) and
                        not_contains(r_flags, x, y)):
                        r_flags.append(Position(x=x, y=y))
                        break
                else:
                    r_flags.append(Position(x=max(r_min_x, map_width - 2), y=i + 1))
        else:
            l_flags = [Position(x=min(1, l_max_x), y=i + 1) for i in range(num_flags)]
            r_flags = [Position(x=max(r_min_x, map_width - 2), y=i + 1) for i in range(num_flags)]

        self._state.l_team_state.flags = l_flags
        self._state.r_team_state.flags = r_flags
        self._notify_listeners()

    def generate_team_states(self, map_width: int, map_height: int) -> None:
        """生成所有团队状态"""
        self.generate_flags(map_width, map_height)
        self.generate_players(map_width)
        self.generate_targets_and_prisons(map_width, map_height)

    def _create_3x3_grid(self, center_x: int, center_y: int) -> List[Position]:
        """创建 3x3 网格位置"""
        return [
            Position(x=center_x - 1, y=center_y - 1),
            Position(x=center_x, y=center_y - 1),
            Position(x=center_x + 1, y=center_y - 1),
            Position(x=center_x - 1, y=center_y),
            Position(x=center_x, y=center_y),
            Position(x=center_x + 1, y=center_y),
            Position(x=center_x - 1, y=center_y + 1),
            Position(x=center_x, y=center_y + 1),
            Position(x=center_x + 1, y=center_y + 1),
        ]

    # ========== 计算属性 ==========

    def is_game_active(self) -> bool:
        """检查游戏是否激活"""
        return (self._state.game_started and
                not self._state.game_paused and
                not self._state.game_over)

    def is_loading(self) -> bool:
        """检查是否在加载状态"""
        return self._state.flow_state == GameFlowState.LOADING

    def is_playing(self) -> bool:
        """检查是否在游戏中"""
        return self._state.flow_state == GameFlowState.PLAYING

    def is_paused(self) -> bool:
        """检查是否暂停"""
        return (self._state.flow_state == GameFlowState.PLAYING and
                self._state.flow_sub_state == GameFlowSubState.PAUSED)

    def is_running(self) -> bool:
        """检查是否运行中"""
        return (self._state.flow_state == GameFlowState.PLAYING and
                self._state.flow_sub_state == GameFlowSubState.RUNNING)

    def is_ended(self) -> bool:
        """检查是否已结束"""
        return self._state.flow_state == GameFlowState.ENDED

    def is_ready(self) -> bool:
        """检查是否准备就绪"""
        return self._state.flow_state == GameFlowState.READY
