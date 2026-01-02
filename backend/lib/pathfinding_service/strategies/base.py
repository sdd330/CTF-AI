"""
寻路策略基类
"""

from abc import ABC, abstractmethod
from typing import List, Set, Optional
from ...data_models import Position


class PathfindingStrategy(ABC):
    """寻路策略抽象基类"""
    
    @abstractmethod
    def find_path(self, start: Position, end: Position, 
                  obstacles: Set[Position],
                  width: int,
                  height: int,
                  extra_obstacles: Optional[Set[Position]] = None) -> List[Position]:
        """
        寻找从起点到终点的路径
        Args:
            start: 起点位置
            end: 终点位置
            obstacles: 障碍物集合
            width: 地图宽度
            height: 地图高度
            extra_obstacles: 额外的障碍物集合
        Returns:
            路径列表，包含起点和终点，如果找不到路径则返回空列表
        """
        pass

