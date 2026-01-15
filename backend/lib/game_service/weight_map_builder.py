"""
权重地图构建模块
用于构建不同策略的权重地图，辅助路径规划
"""

from typing import Dict, List, Optional, Set

from ..data_models import Position, Team
from ..algorithms import bfs_expand
from ..map_service.map import GameMap
from .game import World


class WeightMapBuilder:
    """权重地图构建器，用于构建进攻和防御策略的权重地图"""
    
    def __init__(self, world: World, game_map: GameMap):
        self.world = world
        self.map = game_map
    
    def build_offensive_weight_map(self, extra_obstacles: Optional[Set[Position]] = None) -> List[List[float]]:
        """构建进攻权重地图：避开敌人势力范围，优先选择安全路径"""
        width, height = self.map.width, self.map.height
        weight_map = [[1.0 for _ in range(height)] for _ in range(width)]
        
        self._set_obstacle_weights(weight_map, extra_obstacles, width, height)
        self._set_target_weights(weight_map, width, height)
        self._apply_enemy_influence(weight_map, width, height, extra_obstacles, influence_radius=2)
        
        return weight_map
    
    def build_defence_weight_map(self, extra_obstacles: Optional[Set[Position]] = None) -> List[List[float]]:
        """构建防御权重地图：在己方领地内，敌人周围的位置权重更高"""
        width, height = self.map.width, self.map.height
        my_team = self._get_my_team()
        
        if not my_team:
            return [[1.0 for _ in range(height)] for _ in range(width)]
        
        weight_map = self._init_territory_weights(my_team, width, height)
        self._set_obstacle_weights(weight_map, extra_obstacles, width, height)
        
        obstacles_set = self._create_obstacles_set(extra_obstacles)
        # 直接从敌方玩家字典获取不在监狱的敌人
        opponents = [p for p in self.world.enemy_players.values() if not p.is_in_prison]
        
        for enemy in opponents:
            if not self._is_valid_position(enemy.position, width, height):
                continue
            
            distance_map = self._bfs_expand(enemy.position, obstacles_set, width, height, max_distance=2)
            for pos, dist in distance_map.items():
                if self.map.is_in_team_territory(pos, my_team):
                    enemy_weight = {0: 1.5, 1: 1.4, 2: 1.3}.get(dist, 1.0)
                    weight_map[pos.x][pos.y] = max(weight_map[pos.x][pos.y], enemy_weight)
        
        return weight_map
    
    def _apply_enemy_influence(self, weight_map: List[List[float]], width: int, height: int,
                               extra_obstacles: Optional[Set[Position]], influence_radius: int = 2) -> None:
        """应用敌人影响力到权重地图：距离越近权重越低（越危险）"""
        my_team = self._get_my_team()
        if not my_team:
            return
        
        obstacles_set = self._create_obstacles_set(extra_obstacles)
        # 直接从敌方玩家字典获取不在监狱的敌人
        opponents = [p for p in self.world.enemy_players.values() if not p.is_in_prison]
        
        for enemy in opponents:
            if not self._is_valid_position(enemy.position, width, height):
                continue
            
            distance_map = self._bfs_expand(enemy.position, obstacles_set, width, height, max_distance=influence_radius)
            for pos, dist in distance_map.items():
                enemy_weight = {0: 0.0, 1: 0.25, 2: 0.5}.get(dist, 1.0)
                weight_map[pos.x][pos.y] = min(weight_map[pos.x][pos.y], enemy_weight)
    
    def _get_my_team(self) -> Optional[Team]:
        """获取己方队伍"""
        # 检查哪个队伍有玩家
        if self.world.my_players:
            return Team.from_name(self.world.my_team_name)
        elif self.world.enemy_players:
            return Team.from_name(self.world.my_team_name).get_enemy()
        return None
    
    def _get_enemy_team(self, my_team: Team) -> Team:
        """获取敌方队伍"""
        return Team.RIGHT if my_team == Team.LEFT else Team.LEFT
    
    def _create_obstacles_set(self, extra_obstacles: Optional[Set[Position]]) -> Set[Position]:
        """创建障碍物集合"""
        obstacles_set = self.map.walls.copy()
        if extra_obstacles:
            obstacles_set.update(extra_obstacles)
        return obstacles_set
    
    def _init_territory_weights(self, my_team: Team, width: int, height: int) -> List[List[float]]:
        """初始化领地权重：敌方领地0.1，己方领地1.0"""
        weight_map = [[0.1 for _ in range(height)] for _ in range(width)]
        for x in range(width):
            for y in range(height):
                if self.map.is_in_team_territory(Position(x, y), my_team):
                    weight_map[x][y] = 1.0
        return weight_map
    
    def _set_obstacle_weights(self, weight_map: List[List[float]], 
                              extra_obstacles: Optional[Set[Position]], 
                              width: int, height: int) -> None:
        """设置障碍物权重为0"""
        for pos in self.map.walls:
            if self._is_valid_position(pos, width, height):
                weight_map[pos.x][pos.y] = 0.0
        
        if extra_obstacles:
            for pos in extra_obstacles:
                if self._is_valid_position(pos, width, height):
                    weight_map[pos.x][pos.y] = 0.0
    
    def _set_target_weights(self, weight_map: List[List[float]], width: int, height: int) -> None:
        """设置目标区域权重为1"""
        my_team = self._get_my_team()
        if not my_team:
            return
        
        for team in [my_team, self._get_enemy_team(my_team)]:
            for pos in self.map.get_team_target_positions(team):
                if self._is_valid_position(pos, width, height):
                    weight_map[pos.x][pos.y] = 1.0
    
    def _is_valid_position(self, position: Position, width: int, height: int) -> bool:
        """检查位置是否在边界内"""
        return 0 <= position.x < width and 0 <= position.y < height
    
    def _bfs_expand(self, start: Position, obstacles: Set[Position], 
                   width: int, height: int, max_distance: int) -> Dict[Position, int]:
        """使用BFS从起始位置向外扩展，返回距离映射"""
        def is_valid_pos(pos: Position) -> bool:
            return (self._is_valid_position(pos, width, height) and pos not in obstacles)
        
        return bfs_expand(
            start=start,
            is_valid_position=is_valid_pos,
            max_distance=max_distance,
        )

