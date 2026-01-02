"""
路径规划参数校验器
统一处理路径规划算法的参数校验逻辑
"""

from typing import List, Set, Optional, Tuple
from ..data_models import Position
from .pathfinding_utils import merge_obstacles, is_valid_position


class PathfindingValidator:
    """路径规划参数校验器"""
    
    @staticmethod
    def validate_pathfinding_params(
        start: Position,
        end: Position,
        obstacles: Set[Position],
        width: int,
        height: int,
        extra_obstacles: Optional[Set[Position]] = None,
        algorithm_name: str = "路径规划"
    ) -> Tuple[bool, Optional[List[Position]], Optional[Set[Position]]]:
        """统一校验路径规划参数"""
        if not PathfindingValidator._validate_position(start, width, height, algorithm_name, "起点"):
            return False, None, None
        
        if not PathfindingValidator._validate_position(end, width, height, algorithm_name, "终点"):
            return False, None, None
        
        if start == end:
            return True, [start], None
        
        all_obstacles = merge_obstacles(obstacles, extra_obstacles)
        
        if start in all_obstacles:
            return False, None, None
        
        if end in all_obstacles:
            return False, None, None
        
        return True, None, all_obstacles
    
    @staticmethod
    def _validate_position(pos: Position, width: int, height: int, 
                           algorithm_name: str, pos_type: str) -> bool:
        """验证位置是否在边界内"""
        if not is_valid_position(pos, width, height, set()):
            return False
        return True
    
    @staticmethod
    def validate_position(
        pos: Position,
        width: int,
        height: int,
        obstacles: Set[Position],
        algorithm_name: str = "路径规划"
    ) -> bool:
        """校验单个位置是否有效"""
        if not is_valid_position(pos, width, height, obstacles):
            return False
        return True

