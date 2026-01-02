"""
BFS寻路策略实现
使用通用算法模块
"""

from typing import List, Set, Optional
from ...data_models import Position
from ...algorithms import bfs_find_path, get_sorted_directions
from ..pathfinding_utils import is_valid_position
from ..pathfinding_validator import PathfindingValidator
from .base import PathfindingStrategy


class BFSPathfindingStrategy(PathfindingStrategy):
    """广度优先搜索（BFS）寻路策略"""
    
    def find_path(self, start: Position, end: Position,
                  obstacles: Set[Position],
                  width: int,
                  height: int,
                  extra_obstacles: Optional[Set[Position]] = None) -> List[Position]:
        """使用BFS寻找路径"""
        is_valid, result_path, all_obstacles = PathfindingValidator.validate_pathfinding_params(
            start, end, obstacles, width, height, extra_obstacles, "BFS路径规划"
        )
        if not is_valid:
            return []
        if result_path is not None:
            return result_path
        
        # 创建位置验证函数
        def is_valid_pos(pos: Position) -> bool:
            return is_valid_position(pos, width, height, all_obstacles)
        
        # 计算方向优先级
        dx_total = end.x - start.x
        dy_total = end.y - start.y
        sorted_directions = get_sorted_directions(dx_total, dy_total)
        
        # 使用通用 BFS 算法
        max_iterations = width * height * 2
        
        def on_path_found(path: List[Position], iterations: int):
            # 成功时静默，不输出日志
            pass
        
        def on_no_path(iterations: int):
            # 找不到路径时静默，不输出日志
            pass
        
        return bfs_find_path(
            start=start,
            end=end,
            is_valid_position=is_valid_pos,
            max_iterations=max_iterations,
            sorted_directions=sorted_directions,
            on_path_found=on_path_found,
            on_no_path=on_no_path,
        )

