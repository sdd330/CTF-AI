"""
游戏逻辑模块
World 类整合了所有游戏功能
"""

from typing import Dict, List, Optional, Set, Tuple
import time
from ..data_models import Position, Team, Player, Flag, Direction, Action
from ..map_service import GameMap
from ..pathfinding_service import PathfindingStrategy, PathFindingService
from ..utils import (
    list_players, 
    list_flags,
    can_score_flag
)
from ..utils.distance_calculator import DistanceCalculator
from .game_initializer import GameInitializer
from .game_state_updater import GameStateUpdater


class World:
    """Capture the Flag 游戏主类 - 整合所有游戏功能"""
    
    def __init__(self, game_map: GameMap, 
                 pathfinding_strategy: Optional[PathfindingStrategy] = None):
        """
        初始化游戏
        Args:
            game_map: 游戏地图
            pathfinding_strategy: 寻路策略，默认为BFS算法
        """
        self.game_map = game_map
        self.players: Dict[str, Player] = {}
        self.flags: Dict[str, Flag] = {}
        self.left_team_score = 0
        self.right_team_score = 0
        self.current_time = 0.0
        self.my_team_name = ""
        
        # 路径查找服务
        self._pathfinding_service = None
        self._pathfinding_strategy = pathfinding_strategy
        
        # 动作收集器（用于 plan_actions）
        self._actions: Dict[str, str] = {}
        self._paths: Dict[str, List[Dict[str, int]]] = {}
        self._path_timings: Dict[str, Dict[str, float]] = {}  # 存储每个玩家的详细路径计算耗时（毫秒）
        
        # 存储当前帧的路径（用于前端可视化）
        self._current_paths: Dict[str, List[Position]] = {}
        
        # 初始化各个功能模块
        self._initializer = GameInitializer(self)
        self._state_updater = GameStateUpdater(self)
    
    def init(self, req: Dict):
        """从请求初始化游戏（委托给 GameInitializer）"""
        self._initializer.init(req)
    
    def update(self, req: Dict) -> bool:
        """从请求更新游戏状态（my_team_name 已在 init 中设置，不可更改）"""
        if req.get("time", 0) < self.current_time:
            return False
        
        delta_time = int((req.get("time", 0) - self.current_time) * 1000)
        self.current_time = req.get("time", 0)
        
        # 更新旗帜状态
        self._state_updater._update_flags_from_request(req)
        
        # 更新玩家状态
        self._state_updater._update_players_from_request(req)
        
        # 检测得分
        self._check_scoring()
        
        # 更新监狱时间
        for player in self.players.values():
            player.update_prison_time(delta_time)
        
        return True
    
    def plan_actions(self, req: Dict) -> Dict[str, Dict]:
        """
        计划下一步动作
        
        Args:
            req: 游戏状态请求
        Returns:
            包含 actions 和 paths 的字典
        """
        # 1. 更新游戏状态
        if not self.update(req):
            return {"actions": {}, "paths": {}}
        
        # 2. 获取己方队伍（协议保证 my_team 一定存在）
        my_team = self._get_my_team()
        
        # 3. 获取己方玩家列表（排除监狱中的玩家）
        # 监狱中的玩家不能移动，不能规划路径，忽略执行任何策略
        my_players = list_players(self.players, my_team, in_prison=False, has_flag=None)
        
        # 4. 重置动作收集器
        self._actions.clear()
        self._paths.clear()
        self._path_timings.clear()
        self._current_paths.clear()
        
        # 5. 为每个玩家规划动作
        team_prefix = f"{my_team.value}队"
        for player in my_players:
            direction_enum = self._plan_player_action(player)
            self._collect_action(player, direction_enum)
        
        # 6. 基于已收集的数据构造返回结果
        return self.build_result_from_actions(self._actions)
    
    def _plan_player_action(self, player: Player) -> Optional[Direction]:
        """
        规划单个玩家的动作
        
        Player 是自驱动的：根据 World 状态自主生成策略并执行。
        这里只是调用 player.plan()，不干预策略生成过程。
        
        Args:
            player: 玩家对象（自驱动，根据 world 状态规划）
            
        Returns:
            方向枚举，如果无法规划则返回None
        """
        # 监狱中的玩家不能移动，不能规划路径，忽略执行任何策略
        if player.is_in_prison:
            return Direction.STAY
        
        # 如果玩家正拿着旗帜，则优先执行“返回基地”逻辑
        if player.has_flag:
            return self._return_to_base(player)
        
        # 否则交给 Player 自驱动决策
        # plan() 会根据 world 状态自动生成策略并执行相应行为
        direction_enum = player.plan()
        return direction_enum if direction_enum is not None else Direction.STAY
    
    def _return_to_base(self, player: Player) -> Direction:
        """玩家持有旗帜时，立即返回基地"""
        # 检查是否已在基地内
        if player.is_in_base():
            if player.has_flag:
                if can_score_flag(player):
                    player.action(Action.SCORE_FLAG)
            return Direction.STAY
        
        # 使用玩家对象上的基地区域
        if not player.base_area or not player.base_area.positions:
            return Direction.STAY
        
        # 找到最近的基地位置
        base_positions = list(player.base_area.positions)
        target_base_pos = DistanceCalculator.find_closest_position(player.position, base_positions)
        if not target_base_pos:
            return Direction.STAY
        
        # 计算路径
        enemy_team = player.team.get_enemy()
        enemy_players = list_players(self.players, enemy_team, in_prison=False, has_flag=None)
        enemy_positions = {enemy.position for enemy in enemy_players}
        
        path = self.find_path_to(player.position, target_base_pos, 
                                extra_obstacles=enemy_positions, 
                                player_name=player.name)
        
        if not path or len(path) < 2:
            return Direction.STAY
        
        # 验证路径的第一个位置是否等于玩家当前位置
        if path[0] != player.position:
            # 如果路径的第一个位置不等于玩家当前位置，尝试找到玩家位置在路径中的索引
            try:
                player_index = path.index(player.position)
                path = path[player_index:]
            except ValueError:
                return Direction.STAY
        
        # 保存路径用于可视化
        self._current_paths[player.name] = path
        
        # 获取方向：找到路径中第一个不等于当前位置的位置
        next_pos = None
        for pos in path:
            if pos != player.position:
                next_pos = pos
                break
        
        if not next_pos:
            return Direction.STAY
        
        # 验证下一个位置是否与当前位置相邻（曼哈顿距离为1）
        manhattan_dist = abs(next_pos.x - player.position.x) + abs(next_pos.y - player.position.y)
        if manhattan_dist != 1:
            # 如果距离大于1，尝试找到路径中第一个相邻的位置
            for pos in path:
                dist = abs(pos.x - player.position.x) + abs(pos.y - player.position.y)
                if dist == 1:
                    next_pos = pos
                    break
            else:
                # 如果找不到相邻位置，计算应该移动的方向
                dx = next_pos.x - player.position.x
                dy = next_pos.y - player.position.y
                if abs(dx) > abs(dy):
                    next_pos = Position(player.position.x + (1 if dx > 0 else -1), player.position.y)
                else:
                    next_pos = Position(player.position.x, player.position.y + (1 if dy > 0 else -1))
        
        direction = player.position.direction_to(next_pos)
        return direction if direction else Direction.STAY
    
    def _collect_action(self, player: Player, direction: Optional[Direction]) -> None:
        """收集玩家的动作（只收集己方队伍）"""
        my_team = self._get_my_team()
        if my_team and player.belongs_to_team(my_team):
            self._actions[player.name] = (direction or Direction.STAY).value
        else:
            team_prefix = f"{my_team.value}队"
            print(f"⚠️  [{team_prefix}] [World] 跳过收集非己方玩家动作: {player.name} ({player.team.value}队)", flush=True)
    
    def _collect_paths_for_visualization(self) -> None:
        """收集路径数据用于前端可视化（只收集己方队伍）"""
        my_team = self._get_my_team()
        
        for player_name, path in self._current_paths.items():
            # 验证玩家是否属于己方队伍
            if player_name not in self.players:
                continue
            
            player = self.players[player_name]
            if not player.belongs_to_team(my_team):
                continue
            
            if path and len(path) > 0:
                self._paths[player_name] = [
                    {"x": pos.x, "y": pos.y} 
                    for pos in path
                ]
                # 收集耗时信息（如果存在）
                if player_name in self._path_timings:
                    # 将耗时信息添加到路径数据中（作为元数据）
                    pass  # 耗时信息将在返回的 timings 字段中单独传递
    
    def build_result_from_actions(self, actions: Dict[str, str]) -> Dict[str, Dict]:
        """
        基于传入的动作字典和当前帧收集到的路径/耗时，构造返回给前端的结果。
        
        - 只返回己方队伍玩家的数据
        - 路径来源于 self._current_paths / self._paths
        - 耗时信息来源于 self._path_timings
        
        方便在不同的决策入口（普通对战 / Gym 训练桥接）之间复用。
        """
        my_team = self._get_my_team()
        
        # 基于当前帧的 _current_paths 收集可视化路径
        self._paths.clear()
        self._collect_paths_for_visualization()
        
        filtered_actions: Dict[str, str] = {}
        filtered_paths: Dict[str, List[Dict[str, int]]] = {}
        filtered_timings: Dict[str, Dict[str, float]] = {}
        
        # 过滤动作：仅保留己方玩家
        for player_name, direction in actions.items():
            if player_name in self.players and self.players[player_name].belongs_to_team(my_team):
                filtered_actions[player_name] = direction
        
        # 过滤路径：_collect_paths_for_visualization 已经过滤了一次，这里再做一层防御性过滤
        for player_name, path in self._paths.items():
            if player_name in self.players and self.players[player_name].belongs_to_team(my_team):
                filtered_paths[player_name] = path
        
        # 过滤耗时信息：仅保留己方玩家
        for player_name, timings in self._path_timings.items():
            if player_name in self.players and self.players[player_name].belongs_to_team(my_team):
                filtered_timings[player_name] = timings
        
        return {
            "actions": filtered_actions,
            "paths": filtered_paths,
            "timings": filtered_timings,
        }
    
    def _get_my_team(self) -> Team:
        """获取己方队伍（协议保证 my_team_name 始终有效）"""
        return Team.from_name(self.my_team_name)
    
    def _get_teams(self) -> Tuple[Team, Team]:
        """获取己方和敌方队伍（协议保证 my_team_name 始终有效）"""
        my_team = Team.from_name(self.my_team_name)
        enemy_team = my_team.get_enemy()
        return my_team, enemy_team
    
    # ========== 查询方法 ==========
    
    def get_team_target_positions(self, team: Team) -> List[Position]:
        """获取队伍目标位置列表"""
        return list(self.game_map.get_team_target_positions(team))
    
    def get_team_prison_positions(self, team: Team) -> List[Position]:
        """获取队伍监狱位置列表"""
        return list(self.game_map.get_team_prison_positions(team))
    
    def is_in_team_territory(self, position: Position, team: Team) -> bool:
        """检查位置是否在指定队伍的领地内"""
        return self.game_map.is_in_team_territory(position, team)
    
    def is_in_enemy_territory(self, position: Position, team: Team) -> bool:
        """检查位置是否在指定队伍的敌方领地内"""
        return self.game_map.is_in_enemy_territory(position, team)
    
    @property
    def width(self) -> int:
        """获取地图宽度"""
        return self.game_map.width
    
    @property
    def height(self) -> int:
        """获取地图高度"""
        return self.game_map.height
    
    @property
    def walls(self) -> Set[Position]:
        """获取墙壁位置集合"""
        return self.game_map.walls
    
    def is_valid_position(self, position: Position) -> bool:
        """检查位置是否有效"""
        return self.game_map.is_valid_position(position)
    
    def is_wall(self, position: Position) -> bool:
        """检查位置是否是墙"""
        return self.game_map.is_wall(position)
    
    def get_team_target_area(self, team: Team):
        """获取队伍目标区域"""
        return self.game_map.get_team_target_area(team)
    
    def get_team_prison_area(self, team: Team):
        """获取队伍监狱区域"""
        return self.game_map.get_team_prison_area(team)
    
    def initialize_map(self, map_data: Dict, my_team_name: str,
                      my_team_target: list, opponent_target: list,
                      my_team_prison: list, opponent_prison: list):
        """初始化地图"""
        self.game_map.initialize(
            map_data=map_data,
            my_team_name=my_team_name,
            my_team_target=my_team_target,
            opponent_target=opponent_target,
            my_team_prison=my_team_prison,
            opponent_prison=opponent_prison
        )
    
    def _check_scoring(self) -> None:
        """检测得分"""
        for player in self.players.values():
            if player.has_flag and can_score_flag(player):
                success = player.action(Action.SCORE_FLAG)
                if success:
                    team_prefix = f"{player.team.value}队"
                    print(f"🎉 [{team_prefix}] [World] 玩家 {player.name} ({player.team.value}队) 在己方基地插旗得分！当前得分: L={self.left_team_score}, R={self.right_team_score}", flush=True)
    
    # ========== 路径查找 ==========
    
    def _ensure_pathfinding_service(self) -> PathFindingService:
        """确保路径查找服务已初始化"""
        if not self._pathfinding_service:
            self._pathfinding_service = PathFindingService(
                self,  # 传入 world 对象
                pathfinding_strategy=self._pathfinding_strategy
            )
        return self._pathfinding_service
    
    def find_path_to(self, start: Position, end: Position,
                    extra_obstacles: Optional[Set[Position]] = None,
                    player_name: Optional[str] = None) -> List[Position]:
        """寻找路径（委托给 PathFindingService），并记录详细耗时（只处理己方队伍）"""
        # 获取队伍名称前缀（my_team_name 已在 init 中设置）
        team_prefix = f"{self.my_team_name}队"
        
        # 验证玩家是否属于己方队伍（协议保证 my_team 始终存在）
        my_team = self._get_my_team()
        if player_name and player_name in self.players:
            player = self.players[player_name]
            if not player.belongs_to_team(my_team):
                return []
            
            # 监狱中的玩家不能规划路径
            if player.is_in_prison:
                return []
        
        path, timings = self._ensure_pathfinding_service().find_path_to(start, end, extra_obstacles, player_name, team_prefix)
        
        # 如果提供了玩家名称且属于己方队伍，记录详细耗时
        if player_name and player_name in self.players:
            player = self.players[player_name]
            if player.belongs_to_team(my_team):
                # 累加各项耗时（因为一个玩家可能在同一帧中调用多次路径规划）
                if player_name not in self._path_timings:
                    self._path_timings[player_name] = {}
                
                for key, value in timings.items():
                    if key in self._path_timings[player_name]:
                        self._path_timings[player_name][key] += value
                    else:
                        self._path_timings[player_name][key] = value
        
        return path
    
    def get_direction(self, current: Position, next_pos: Position) -> str:
        """获取方向（委托给 PathFindingService）"""
        return self._ensure_pathfinding_service().get_direction(current, next_pos)
