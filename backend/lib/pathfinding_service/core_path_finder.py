"""
核心路径查找器
负责基础的路径查找逻辑
"""

from typing import List, Optional, Set, Dict, Tuple, TYPE_CHECKING
import time
from ..data_models import Position, Team
from .pathfinder import Pathfinder

if TYPE_CHECKING:
    from ..game_engine import World


class CorePathFinder:
    """核心路径查找器 - 单一职责：基础路径查找"""
    
    def __init__(self, world: 'World', pathfinder: Pathfinder):
        self.world = world
        self.pathfinder = pathfinder
    
    def find_path_to(self, start: Position, end: Position,
                    extra_obstacles: Optional[Set[Position]] = None,
                    player_name: Optional[str] = None,
                    team_prefix: str = "") -> Tuple[List[Position], Dict[str, float]]:
        """
        寻找路径
        
        Args:
            start: 起始位置
            end: 目标位置
            extra_obstacles: 额外的障碍物集合
            player_name: 玩家名称（可选，用于过滤障碍物）
        
        Returns:
            (路径位置列表, 耗时信息字典)，如果无法找到路径则返回空列表
        """
        timings = {}
        total_start = time.perf_counter()
        
        my_team = None
        if player_name:
            player = self.world.my_players.get(player_name) or self.world.enemy_players.get(player_name)
            if player:
                my_team = player.team
        
        # 过滤障碍物：如果障碍物是敌方玩家且在我方领地内，则忽略
        filter_start = time.perf_counter()
        filtered_obstacles = extra_obstacles
        if extra_obstacles and my_team:
            filtered_obstacles = set()
            for pos in extra_obstacles:
                if not self._is_enemy_player_in_my_territory(pos, my_team):
                    filtered_obstacles.add(pos)
        timings['obstacle_filter'] = (time.perf_counter() - filter_start) * 1000
        
        # 直接调用 pathfinder 查找路径
        pathfind_start = time.perf_counter()
        result = self.pathfinder.find_path(
            start, end,
            self.world.map.walls,
            self.world.map.width,
            self.world.map.height,
            filtered_obstacles
        )
        timings['pathfinding'] = (time.perf_counter() - pathfind_start) * 1000
        timings['total'] = (time.perf_counter() - total_start) * 1000
        
        return (result if result else []), timings
    
    def _is_enemy_player_in_my_territory(self, position: Position, my_team: Team) -> bool:
        """检查位置是否是对方玩家且在我方领地内"""
        # 只检查敌方玩家（因为是我方领地，敌方玩家才可能在这里）
        for player in self.world.enemy_players.values():
            if player.position == position:
                return self.world.map.is_in_team_territory(position, my_team)
        return False
