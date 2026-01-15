"""
权重路径查找器 - 使用权重地图进行路径规划
"""

from typing import List, Optional, Set, Dict, Tuple, TYPE_CHECKING
import time
from ..data_models import Position, Team
from ..algorithms import bfs_expand, dijkstra_find_weighted_path
from .pathfinding_validator import PathfindingValidator

if TYPE_CHECKING:
    from ..game_engine import World
    from ..data_models import Player


class WeightedPathFinder:
    """权重路径查找器：使用权重地图进行路径规划"""

    def __init__(self, world: 'World'):
        self.world = world

    def find_safe_path(self, start: Position, end: Position, extra_obstacles: Optional[Set[Position]] = None,
                       player_name: Optional[str] = None, team_prefix: str = "") -> Tuple[List[Position], Dict[str, float]]:
        """寻找安全路径（避开敌人势力范围）"""
        timings = {}
        total_start = time.perf_counter()

        player = self._get_player(player_name)
        if not player:
            return [], {}
        my_team = player.team
        team_prefix = team_prefix or f"{my_team.value}队"

        t = time.perf_counter()
        influence_map = self._calculate_enemy_influence_zone(my_team, extra_obstacles, 2, team_prefix)
        timings['influence_zone'] = (time.perf_counter() - t) * 1000

        t = time.perf_counter()
        weight_map = self._build_safe_weight_map(influence_map, extra_obstacles, my_team)
        timings['weight_map'] = (time.perf_counter() - t) * 1000

        t = time.perf_counter()
        path = self._find_weighted_path(start, end, weight_map, extra_obstacles, player_name, team_prefix)
        timings['pathfinding'] = (time.perf_counter() - t) * 1000
        timings['total'] = (time.perf_counter() - total_start) * 1000

        return path, timings

    def find_defence_path(self, start: Position, end: Position, extra_obstacles: Optional[Set[Position]] = None,
                          player_name: Optional[str] = None) -> Tuple[List[Position], Dict[str, float]]:
        """寻找防御路径（优先接近敌人）"""
        timings = {}
        total_start = time.perf_counter()

        player = self._get_player(player_name)
        if not player:
            return [], {}
        my_team = player.team
        team_prefix = f"{my_team.value}队"

        t = time.perf_counter()
        weight_map = self._build_defence_weight_map(extra_obstacles, my_team)
        timings['weight_map'] = (time.perf_counter() - t) * 1000

        t = time.perf_counter()
        path = self._find_weighted_path(start, end, weight_map, extra_obstacles, player_name, team_prefix)
        timings['pathfinding'] = (time.perf_counter() - t) * 1000
        timings['total'] = (time.perf_counter() - total_start) * 1000

        return path, timings

    def _get_player(self, player_name: Optional[str]) -> Optional['Player']:
        """获取玩家对象"""
        if not player_name:
            return None
        return self.world.my_players.get(player_name) or self.world.enemy_players.get(player_name)

    def _calculate_enemy_influence_zone(self, my_team: Team, extra_obstacles: Optional[Set[Position]],
                                         influence_radius: int, team_prefix: str) -> Dict[Position, float]:
        """计算敌方影响区域"""
        obstacles_set = self._create_obstacles_set(extra_obstacles)
        opponents = self._get_enemy_opponents(my_team)
        weight_map = {0: 0.1, 1: 0.3, 2: 0.6}
        influence_map: Dict[Position, float] = {}

        for enemy in opponents:
            if not self._is_valid_position(enemy.position):
                continue
            try:
                distance_map = self._bfs_expand_from_position(enemy.position, obstacles_set, influence_radius)
                for pos, dist in distance_map.items():
                    enemy_weight = weight_map.get(dist, 1.0)
                    if pos not in influence_map or enemy_weight < influence_map[pos]:
                        influence_map[pos] = enemy_weight
            except Exception:
                continue
        return influence_map

    def _build_safe_weight_map(self, influence_map: Dict[Position, float], extra_obstacles: Optional[Set[Position]],
                                my_team: Team) -> List[List[float]]:
        """构建安全权重地图"""
        w, h = self.world.map.width, self.world.map.height
        weight_map = [[1.0] * h for _ in range(w)]
        self._set_obstacle_weights(weight_map, extra_obstacles, w, h)
        for pos, weight in influence_map.items():
            self._apply_weight(weight_map, pos, weight, w, h, 'min', 0.1)
        return weight_map

    def _build_defence_weight_map(self, extra_obstacles: Optional[Set[Position]], my_team: Team) -> List[List[float]]:
        """构建防御权重地图"""
        w, h = self.world.map.width, self.world.map.height
        weight_map = [[0.1] * h for _ in range(w)]
        for x in range(w):
            for y in range(h):
                if self.world.map.is_in_team_territory(Position(x, y), my_team):
                    weight_map[x][y] = 1.0
        self._set_obstacle_weights(weight_map, extra_obstacles, w, h)

        obstacles_set = self._create_obstacles_set(extra_obstacles)
        enemy_weights = {0: 1.5, 1: 1.4, 2: 1.3}
        for enemy in self._get_enemy_opponents(my_team):
            if not self._is_valid_position(enemy.position):
                continue
            for pos, dist in self._bfs_expand_from_position(enemy.position, obstacles_set, 2).items():
                if self.world.map.is_in_team_territory(pos, my_team):
                    self._apply_weight(weight_map, pos, enemy_weights.get(dist, 1.0), w, h, 'max')
        return weight_map

    def _find_weighted_path(self, start: Position, end: Position, weight_map: List[List[float]],
                            extra_obstacles: Optional[Set[Position]], player_name: Optional[str],
                            team_prefix: str = "") -> List[Position]:
        """使用权重地图规划路径"""
        w, h = self.world.map.width, self.world.map.height
        is_valid, result_path, all_obstacles = PathfindingValidator.validate_pathfinding_params(
            start, end, self.world.map.walls, w, h, extra_obstacles, "权重路径规划")
        if not is_valid:
            return []
        if result_path is not None:
            return result_path

        def is_valid_pos(pos: Position) -> bool:
            return self._is_valid_position(pos) and pos not in all_obstacles

        def get_cost(pos: Position) -> float:
            if not (0 <= pos.x < w and 0 <= pos.y < h):
                return 0.0
            pw = weight_map[pos.x][pos.y]
            return 0.0 if pw == 0.0 else 1.0 + max(0, 1.0 - pw) * 2.0

        return dijkstra_find_weighted_path(start, end, is_valid_pos, get_cost, w * h * 2)

    def _bfs_expand_from_position(self, start_pos: Position, obstacles_set: Set[Position],
                                   max_distance: int) -> Dict[Position, int]:
        """BFS扩展"""
        return bfs_expand(start_pos, lambda p: self._is_valid_position(p) and p not in obstacles_set, max_distance)

    def _set_obstacle_weights(self, weight_map: List[List[float]], extra_obstacles: Optional[Set[Position]],
                               w: int, h: int) -> None:
        """设置障碍物权重为0"""
        for pos in self.world.map.walls:
            if 0 <= pos.x < w and 0 <= pos.y < h:
                weight_map[pos.x][pos.y] = 0.0
        if extra_obstacles:
            for pos in extra_obstacles:
                if 0 <= pos.x < w and 0 <= pos.y < h:
                    weight_map[pos.x][pos.y] = 0.0

    def _create_obstacles_set(self, extra_obstacles: Optional[Set[Position]]) -> Set[Position]:
        """创建障碍物集合"""
        obstacles = self.world.map.walls.copy()
        if extra_obstacles:
            obstacles.update(extra_obstacles)
        return obstacles

    def _is_valid_position(self, position: Position) -> bool:
        """检查位置是否有效"""
        try:
            return self.world.map.is_valid_position(position)
        except Exception:
            return False

    def _get_enemy_opponents(self, my_team: Team) -> List['Player']:
        """获取敌方玩家列表"""
        if my_team == self.world._get_my_team():
            opponents = self.world.enemy_players.values()
        else:
            opponents = self.world.my_players.values()
        return [p for p in opponents if not p.is_in_prison]

    def _apply_weight(self, weight_map: List[List[float]], pos: Position, weight: float,
                      w: int, h: int, mode: str = 'min', min_weight: float = 0.1) -> None:
        """应用权重到地图"""
        if not (0 <= pos.x < w and 0 <= pos.y < h) or weight_map[pos.x][pos.y] == 0.0:
            return
        if mode == 'min':
            weight_map[pos.x][pos.y] = min(weight_map[pos.x][pos.y], max(weight, min_weight))
        elif mode == 'max':
            weight_map[pos.x][pos.y] = max(weight_map[pos.x][pos.y], weight)
