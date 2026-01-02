"""
Dijkstra寻路策略实现
使用通用算法模块
"""

from typing import List, Set, Optional
from ...data_models import Position
from ...algorithms import dijkstra_find_path, get_sorted_directions
from ..pathfinding_utils import is_valid_position
from ..pathfinding_validator import PathfindingValidator
from .base import PathfindingStrategy


class DijkstraPathfindingStrategy(PathfindingStrategy):
    """Dijkstra寻路策略 - 针对CTF游戏场景优化"""
    
    def find_path(self, start: Position, end: Position,
                  obstacles: Set[Position],
                  width: int,
                  height: int,
                  extra_obstacles: Optional[Set[Position]] = None) -> List[Position]:
        """
        使用Dijkstra算法寻找路径 - 针对网格地图优化
        
        优化点：
        1. 使用 parent 字典重建路径，避免存储完整路径列表（节省内存）
        2. 方向优先级：优先探索朝向目标的方向
        3. 早期终止：找到目标立即返回
        4. 曼哈顿距离排序：优化方向探索顺序
        """
        # 参数校验
        is_valid, result_path, all_obstacles = PathfindingValidator.validate_pathfinding_params(
            start, end, obstacles, width, height, extra_obstacles, "Dijkstra路径规划"
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
        
        # 使用通用 Dijkstra 算法
        max_iterations = width * height * 2
        
        def on_path_found(path: List[Position], iterations: int):
            # 成功时静默，不输出日志
            pass
        
        def on_no_path(iterations: int, visited_count: int):
            # 找不到路径时静默，不输出日志
            pass
        
        return dijkstra_find_path(
            start=start,
            end=end,
            is_valid_position=is_valid_pos,
            max_iterations=max_iterations,
            sorted_directions=sorted_directions,
            on_path_found=on_path_found,
            on_no_path=on_no_path,
        )

