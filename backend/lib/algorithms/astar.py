"""
A* 寻路算法通用实现
提供可复用的 A* 算法功能
"""

import heapq
from typing import List, Callable, Optional, Dict
from ..data_models import Position
from ..constants import DIRECTIONS
from .bfs import get_sorted_directions


def manhattan_distance(pos1: Position, pos2: Position) -> int:
    """
    计算两个位置之间的曼哈顿距离
    
    Args:
        pos1: 第一个位置
        pos2: 第二个位置
    
    Returns:
        曼哈顿距离
    """
    return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)


def astar_find_path(
    start: Position,
    end: Position,
    is_valid_position: Callable[[Position], bool],
    heuristic: Optional[Callable[[Position], int]] = None,
    max_iterations: Optional[int] = None,
    sorted_directions: Optional[List[tuple]] = None,
    on_path_found: Optional[Callable[[List[Position], int], None]] = None,
    on_no_path: Optional[Callable[[int, int], None]] = None,
) -> List[Position]:
    """
    使用 A* 算法查找从起点到终点的路径
    
    Args:
        start: 起始位置
        end: 目标位置
        is_valid_position: 判断位置是否有效的函数
        heuristic: 启发式函数，默认为曼哈顿距离
        max_iterations: 最大迭代次数，默认为 None（无限制）
        sorted_directions: 可选的方向列表（已排序），默认为 None（使用默认排序）
        on_path_found: 找到路径时的回调函数 (path, iterations)
        on_no_path: 未找到路径时的回调函数 (iterations, seen_count)
    
    Returns:
        路径位置列表，如果无法找到路径则返回空列表
    """
    if start == end:
        return [start]
    
    # 使用默认启发式函数（曼哈顿距离）
    if heuristic is None:
        def heuristic_func(pos: Position) -> int:
            return manhattan_distance(pos, end)
    else:
        heuristic_func = heuristic
    
    # 计算方向优先级并排序
    if sorted_directions is None:
        dx_total = end.x - start.x
        dy_total = end.y - start.y
        sorted_directions = get_sorted_directions(dx_total, dy_total)
    
    counter = 0
    initial_h = heuristic_func(start)
    heap = [(initial_h, counter, 0, [start])]
    seen: Dict[Position, int] = {start: 0}
    iterations = 0
    
    while heap:
        if max_iterations is not None and iterations >= max_iterations:
            if on_no_path:
                on_no_path(iterations, len(seen))
            return []
        
        iterations += 1
        f_cost, _, g_cost, path = heapq.heappop(heap)
        curr = path[-1]
        
        if curr == end:
            if on_path_found:
                on_path_found(path, iterations)
            return path
        
        for dx, dy in sorted_directions:
            next_pos = Position(curr.x + dx, curr.y + dy)
            
            if is_valid_position(next_pos):
                new_g_cost = g_cost + 1
                
                if next_pos not in seen or new_g_cost < seen[next_pos]:
                    seen[next_pos] = new_g_cost
                    new_path = path + [next_pos]
                    new_f_cost = new_g_cost + heuristic_func(next_pos)
                    counter += 1
                    heapq.heappush(heap, (new_f_cost, counter, new_g_cost, new_path))
    
    if on_no_path:
        on_no_path(iterations, len(seen))
    return []

