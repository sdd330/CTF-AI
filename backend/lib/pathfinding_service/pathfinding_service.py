"""
路径查找服务
负责路径规划
整合敌方影响区域、安全路径和防御路径功能
"""

from typing import List, Optional, Set, Dict, Tuple, TYPE_CHECKING
from ..data_models import Position
from .pathfinder import Pathfinder
from .strategies import PathfindingStrategy
from .core_path_finder import CorePathFinder
from .weighted_path_finder import WeightedPathFinder

if TYPE_CHECKING:
    from ..game_engine import World


class PathFindingService:
    """路径查找服务 - 整合路径查找相关功能"""
    
    def __init__(self, world: 'World', 
                 pathfinding_strategy: Optional[PathfindingStrategy] = None):
        """
        初始化路径查找服务
        
        Args:
            world: 游戏世界对象
            pathfinding_strategy: 寻路策略，默认为BFS算法
        """
        self.world = world
        
        # 初始化各个组件
        self.pathfinder = Pathfinder(pathfinding_strategy)
        self.core_finder = CorePathFinder(world, self.pathfinder)
        self.weighted_finder = WeightedPathFinder(world)
    
    def find_path_to(self, start: Position, end: Position,
                    extra_obstacles: Optional[Set[Position]] = None,
                    player_name: Optional[str] = None,
                    team_prefix: str = "") -> Tuple[List[Position], Dict[str, float]]:
        """
        寻找路径：使用安全路径规划
        
        如果玩家名称有效，使用安全路径规划（避开敌人势力范围）
        否则使用基础路径规划
        
        Args:
            team_prefix: 队伍名称前缀（用于日志）
        
        Returns:
            (路径列表, 耗时信息字典)
        """
        # 如果提供了玩家名称，使用安全路径规划
        if player_name and player_name in self.world.players:
            path, timings = self.weighted_finder.find_safe_path(start, end, extra_obstacles, player_name, team_prefix)
            timings['algorithm'] = 'safe_pathfinding'
            return path, timings
        
        # 没有玩家名称时，使用基础路径规划
        path, timings = self.core_finder.find_path_to(start, end, extra_obstacles, player_name, team_prefix)
        timings['algorithm'] = 'basic_pathfinding'
        return path, timings
    
    def get_direction(self, current: Position, next_pos: Position) -> str:
        """获取方向字符串"""
        return self.pathfinder.get_direction(current, next_pos)

