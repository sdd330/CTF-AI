"""
权重路径查找器
负责使用权重地图进行路径规划（安全路径、防御路径等）
"""

from typing import List, Optional, Set, Dict, Tuple, TYPE_CHECKING
import time
from ..data_models import Position, Team
from ..utils import list_players
from ..algorithms import bfs_expand, dijkstra_find_weighted_path
from .pathfinding_validator import PathfindingValidator

if TYPE_CHECKING:
    from ..game_engine import World


class WeightedPathFinder:
    """权重路径查找器：使用权重地图进行路径规划"""
    
    def __init__(self, world: 'World'):
        self.world = world
    
    def find_safe_path(self, start: Position, end: Position,
                      extra_obstacles: Optional[Set[Position]] = None,
                      player_name: Optional[str] = None,
                      team_prefix: str = "") -> tuple[List[Position], Dict[str, float]]:
        """
        寻找安全路径（避开敌人势力范围）
        
        Returns:
            (路径列表, 耗时信息字典)
        """
        timings = {}
        total_start = time.perf_counter()
        
        if not self._validate_player(player_name):
            return [], {}
        
        my_team = self.world.players[player_name].team
        team_prefix = team_prefix or f"{my_team.value}队"
        
        # 测量敌方影响区域计算耗时
        influence_start = time.perf_counter()
        influence_map = self._calculate_enemy_influence_zone(my_team, extra_obstacles, influence_radius=2, team_prefix=team_prefix)
        timings['influence_zone'] = (time.perf_counter() - influence_start) * 1000
        
        # 测量权重地图构建耗时
        weight_map_start = time.perf_counter()
        weight_map = self._build_safe_weight_map(influence_map, extra_obstacles, my_team)
        timings['weight_map'] = (time.perf_counter() - weight_map_start) * 1000
        
        # 测量路径查找耗时
        pathfind_start = time.perf_counter()
        path = self._find_weighted_path(start, end, weight_map, extra_obstacles, player_name, team_prefix)
        timings['pathfinding'] = (time.perf_counter() - pathfind_start) * 1000
        
        timings['total'] = (time.perf_counter() - total_start) * 1000
        
        # 失败时也静默，不输出日志
        
        return path, timings
    
    def find_defence_path(self, start: Position, end: Position,
                         extra_obstacles: Optional[Set[Position]] = None,
                         player_name: Optional[str] = None) -> Tuple[List[Position], Dict[str, float]]:
        """寻找防御路径（优先接近敌人）"""
        timings = {}
        total_start = time.perf_counter()
        
        if not self._validate_player(player_name):
            return [], {}
        
        my_team = self.world.players[player_name].team
        team_prefix = f"{my_team.value}队"
        
        weight_map_start = time.perf_counter()
        weight_map = self._build_defence_weight_map(extra_obstacles, my_team)
        timings['weight_map'] = (time.perf_counter() - weight_map_start) * 1000
        
        pathfind_start = time.perf_counter()
        path = self._find_weighted_path(start, end, weight_map, extra_obstacles, player_name, team_prefix)
        timings['pathfinding'] = (time.perf_counter() - pathfind_start) * 1000
        timings['total'] = (time.perf_counter() - total_start) * 1000
        
        return path, timings
    
    def _calculate_enemy_influence_zone(self, my_team: Team, extra_obstacles: Optional[Set[Position]] = None, 
                                       influence_radius: int = 2, team_prefix: str = "") -> Dict[Position, float]:
        """计算敌方影响区域"""
        obstacles_set = self._create_obstacles_set(extra_obstacles)
        opponents = self._get_enemy_opponents(my_team)
        
        team_prefix = team_prefix or f"{my_team.value}队"
        
        influence_map: Dict[Position, float] = {}
        # 调整权重：距离敌人越近，权重越低（但最小0.1，避免路径被完全阻塞）
        weight_map = {0: 0.1, 1: 0.3, 2: 0.6}
        
        for i, enemy in enumerate(opponents):
            if not self._is_valid_position(enemy.position):
                continue
            
            try:
                distance_map = self._bfs_expand_from_position(enemy.position, obstacles_set, influence_radius)
            except Exception as e:
                print(f"❌ [{team_prefix}] [敌方影响区域] 处理敌人 {enemy.name} 时出错: {e}", flush=True)
                import traceback
                traceback.print_exc()
                continue
            for pos, dist in distance_map.items():
                enemy_weight = weight_map.get(dist, 1.0)
                if pos not in influence_map or enemy_weight < influence_map[pos]:
                    influence_map[pos] = enemy_weight
        
        return influence_map
    
    def _build_safe_weight_map(self, influence_map: Dict[Position, float], 
                               extra_obstacles: Optional[Set[Position]], 
                               my_team: Team) -> List[List[float]]:
        """构建安全权重地图（避开敌人势力范围）"""
        width = self.world.width
        height = self.world.height
        weight_map = self._init_weight_map(width, height, default_value=1.0)
        
        self._set_obstacle_weights(weight_map, extra_obstacles, width, height)
        
        for pos, weight in influence_map.items():
            self._apply_weight_to_map(weight_map, pos, weight, width, height, mode='min', min_weight=0.1)
        
        return weight_map
    
    def _build_defence_weight_map(self, extra_obstacles: Optional[Set[Position]], 
                                  my_team: Team) -> List[List[float]]:
        """构建防御权重地图（优先接近敌人）"""
        width = self.world.width
        height = self.world.height
        weight_map = self._init_territory_weights(my_team, width, height)
        self._set_obstacle_weights(weight_map, extra_obstacles, width, height)
        
        obstacles_set = self._create_obstacles_set(extra_obstacles)
        opponents = self._get_enemy_opponents(my_team)
        enemy_weight_map = {0: 1.5, 1: 1.4, 2: 1.3}
        
        for enemy in opponents:
            if not self._is_valid_position(enemy.position):
                continue
            
            distance_map = self._bfs_expand_from_position(enemy.position, obstacles_set, max_distance=2)
            for pos, dist in distance_map.items():
                if self.world.is_in_team_territory(pos, my_team):
                    enemy_weight = enemy_weight_map.get(dist, 1.0)
                    self._apply_weight_to_map(weight_map, pos, enemy_weight, width, height, mode='max')
        
        return weight_map
    
    def _find_weighted_path(self, start: Position, end: Position,
                           weight_map: List[List[float]],
                           extra_obstacles: Optional[Set[Position]],
                           player_name: Optional[str],
                           team_prefix: str = "") -> List[Position]:
        """使用权重地图规划路径（Dijkstra算法）"""
        width = self.world.width
        height = self.world.height
        
        # 参数校验
        is_valid, result_path, all_obstacles = PathfindingValidator.validate_pathfinding_params(
            start, end, self.world.walls, width, height, extra_obstacles, "权重路径规划"
        )
        if not is_valid:
            return []
        if result_path is not None:
            return result_path
        
        # 定义位置有效性检查函数
        def is_valid_position(pos: Position) -> bool:
            if not self._is_valid_position(pos):
                return False
            if pos in all_obstacles:
                return False
            return True
        
        # 定义成本计算函数
        def get_cost(pos: Position) -> float:
            if not self._is_valid_map_position(pos, width, height):
                return 0.0
            
            pos_weight = weight_map[pos.x][pos.y]
            
            # 如果权重为0（障碍物），返回0表示不可通过
            if pos_weight == 0.0:
                return 0.0
            
            # 计算成本：基础成本 + 权重调整
            # 权重越小（越危险），成本越高
            base_cost = 1.0
            weight_penalty = max(0, 1.0 - pos_weight)  # 权重越小，惩罚越大
            return base_cost + weight_penalty * 2.0
        
        # 使用算法库的Dijkstra实现
        max_iterations = width * height * 2
        path = dijkstra_find_weighted_path(
            start=start,
            end=end,
            is_valid_position=is_valid_position,
            get_cost=get_cost,
            max_iterations=max_iterations
        )
        
        return path
    
    def _bfs_expand_from_position(self, start_pos: Position, obstacles_set: Set[Position], 
                                   max_distance: int) -> Dict[Position, int]:
        """BFS扩展，返回距离映射"""
        def is_valid_pos(pos: Position) -> bool:
            return (self._is_valid_position(pos) and pos not in obstacles_set)
        
        expand_start = time.perf_counter()
        result = bfs_expand(
            start=start_pos,
            is_valid_position=is_valid_pos,
            max_distance=max_distance,
        )
        return result
    
    def _set_obstacle_weights(self, weight_map: List[List[float]], 
                              extra_obstacles: Optional[Set[Position]], 
                              width: int, height: int) -> None:
        """设置障碍物权重为0"""
        for pos in self.world.walls:
            if self._is_valid_map_position(pos, width, height):
                weight_map[pos.x][pos.y] = 0.0
        
        if extra_obstacles:
            for pos in extra_obstacles:
                if self._is_valid_map_position(pos, width, height):
                    weight_map[pos.x][pos.y] = 0.0
    
    def _validate_player(self, player_name: Optional[str]) -> bool:
        return player_name is not None and player_name in self.world.players
    
    def _create_obstacles_set(self, extra_obstacles: Optional[Set[Position]]) -> Set[Position]:
        obstacles_set = self.world.walls.copy()
        if extra_obstacles:
            obstacles_set.update(extra_obstacles)
        return obstacles_set
    
    def _init_territory_weights(self, my_team: Team, width: int, height: int) -> List[List[float]]:
        """初始化领地权重：敌方领地0.1，己方领地1.0"""
        weight_map = self._init_weight_map(width, height, default_value=0.1)
        for x in range(width):
            for y in range(height):
                if self.world.is_in_team_territory(Position(x, y), my_team):
                    weight_map[x][y] = 1.0
        return weight_map
    
    def _is_valid_position(self, position: Position) -> bool:
        """检查位置是否有效（在地图范围内）"""
        try:
            return self.world.is_valid_position(position)
        except Exception as e:
            print(f"❌ [WeightedPathFinder] _is_valid_position 错误: {e}", flush=True)
            return False
    
    def _is_valid_map_position(self, pos: Position, width: int, height: int) -> bool:
        """检查位置是否在地图范围内"""
        return 0 <= pos.x < width and 0 <= pos.y < height
    
    def _init_weight_map(self, width: int, height: int, default_value: float = 1.0) -> List[List[float]]:
        """初始化权重地图"""
        return [[default_value for _ in range(height)] for _ in range(width)]
    
    def _get_enemy_opponents(self, my_team: Team) -> List:
        """获取敌方玩家列表（排除监狱中的）"""
        enemy_team = my_team.get_enemy()
        return list_players(self.world.players, enemy_team, in_prison=False, has_flag=None)
    
    def _apply_weight_to_map(self, weight_map: List[List[float]], pos: Position, weight: float, 
                             width: int, height: int, mode: str = 'min', min_weight: float = 0.1) -> None:
        """
        统一应用权重到地图位置的逻辑
        
        Args:
            weight_map: 权重地图
            pos: 位置
            weight: 权重值
            width: 地图宽度
            height: 地图高度
            mode: 应用模式，'min'表示取最小值（安全路径，避开危险），'max'表示取最大值（防御路径，接近敌人）
            min_weight: 最小权重值（仅用于min模式，避免路径被完全阻塞）
        """
        if not self._is_valid_map_position(pos, width, height):
            return
        
        # 如果当前位置已经是障碍物（权重为0），不要覆盖
        if weight_map[pos.x][pos.y] == 0.0:
            return
        
        if mode == 'min':
            # 确保权重不会太小，避免路径被完全阻塞（最小0.1）
            weight_map[pos.x][pos.y] = min(weight_map[pos.x][pos.y], max(weight, min_weight))
        elif mode == 'max':
            weight_map[pos.x][pos.y] = max(weight_map[pos.x][pos.y], weight)

