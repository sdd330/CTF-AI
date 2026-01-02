"""
寻路器
使用策略模式封装寻路算法
"""

from typing import Optional, List, Set
from ..data_models import Position
from .strategies import PathfindingStrategy, BFSPathfindingStrategy


class Pathfinder:
    """寻路算法类 - 使用策略模式"""
    
    def __init__(self, strategy: Optional[PathfindingStrategy] = None):
        """
        初始化寻路器
        Args:
            strategy: 寻路策略，默认为BFS算法（简化路径规划）
        """
        self.strategy = strategy or BFSPathfindingStrategy()
    
    def set_strategy(self, strategy: PathfindingStrategy):
        """设置寻路策略"""
        self.strategy = strategy
    
    def find_path(self, start: Position, end: Position,
                  obstacles: Set[Position],
                  width: int,
                  height: int,
                  extra_obstacles: Optional[Set[Position]] = None) -> List[Position]:
        """寻找路径"""
        return self.strategy.find_path(
            start, end, obstacles, width, height, extra_obstacles
        )
    
    @staticmethod
    def get_direction(current: Position, next_pos: Position) -> str:
        """获取方向字符串"""
        from ...constants import DIRECTION_NAMES
        
        dx = next_pos.x - current.x
        dy = next_pos.y - current.y
        direction_key = (dx, dy)
        
        return DIRECTION_NAMES.get(direction_key, "")

