"""
寻路工具函数
"""

from typing import Set, Optional
from ..data_models import Position


def merge_obstacles(obstacles: Set[Position], extra_obstacles: Optional[Set[Position]]) -> Set[Position]:
    """合并障碍物集合"""
    all_obstacles = obstacles.copy()
    if extra_obstacles:
        all_obstacles.update(extra_obstacles)
    return all_obstacles


def is_valid_position(pos: Position, width: int, height: int, obstacles: Set[Position]) -> bool:
    """检查位置是否有效"""
    return (0 <= pos.x < width and 
            0 <= pos.y < height and
            pos not in obstacles)

