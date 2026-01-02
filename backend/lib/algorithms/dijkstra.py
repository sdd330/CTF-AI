"""
Dijkstra 寻路算法通用实现
提供可复用的 Dijkstra 算法功能
"""

import heapq
from typing import List, Callable, Optional, Dict
from ..data_models import Position
from .bfs import get_sorted_directions


def reconstruct_path(parent: Dict[Position, Position], start: Position, end: Position) -> List[Position]:
    """
    从 parent 字典重建路径
    
    Args:
        parent: 父节点映射字典
        start: 起始位置
        end: 目标位置
    
    Returns:
        路径位置列表
    """
    path = []
    node = end
    while node is not None:
        path.append(node)
        if node == start:
            break
        node = parent.get(node)
    path.reverse()
    return path


def dijkstra_find_path(
    start: Position,
    end: Position,
    is_valid_position: Callable[[Position], bool],
    max_iterations: Optional[int] = None,
    sorted_directions: Optional[List[tuple]] = None,
    on_path_found: Optional[Callable[[List[Position], int], None]] = None,
    on_no_path: Optional[Callable[[int, int], None]] = None,
) -> List[Position]:
    """
    使用 Dijkstra 算法查找从起点到终点的路径
    
    Args:
        start: 起始位置
        end: 目标位置
        is_valid_position: 判断位置是否有效的函数
        max_iterations: 最大迭代次数，默认为 None（无限制）
        sorted_directions: 可选的方向列表（已排序），默认为 None（使用默认排序）
        on_path_found: 找到路径时的回调函数 (path, iterations)
        on_no_path: 未找到路径时的回调函数 (iterations, visited_count)
    
    Returns:
        路径位置列表，如果无法找到路径则返回空列表
    """
    if start == end:
        return [start]
    
    # 计算方向优先级并排序
    if sorted_directions is None:
        from ..constants import DIRECTIONS
        dx_total = end.x - start.x
        dy_total = end.y - start.y
        sorted_directions = get_sorted_directions(dx_total, dy_total)
    
    parent: Dict[Position, Position] = {}
    cost: Dict[Position, int] = {start: 0}
    
    counter = 0
    heap = [(0, counter, start)]
    iterations = 0
    
    while heap:
        if max_iterations is not None and iterations >= max_iterations:
            if on_no_path:
                on_no_path(iterations, len(cost))
            return []
        
        iterations += 1
        current_cost, _, curr = heapq.heappop(heap)
        
        if curr == end:
            path = reconstruct_path(parent, start, end)
            if on_path_found:
                on_path_found(path, iterations)
            return path
        
        if current_cost > cost.get(curr, float('inf')):
            continue
        
        for dx, dy in sorted_directions:
            next_pos = Position(curr.x + dx, curr.y + dy)
            
            if is_valid_position(next_pos):
                new_cost = current_cost + 1
                
                if next_pos not in cost or new_cost < cost[next_pos]:
                    cost[next_pos] = new_cost
                    parent[next_pos] = curr
                    counter += 1
                    heapq.heappush(heap, (new_cost, counter, next_pos))
    
    if on_no_path:
        on_no_path(iterations, len(cost))
    return []


def dijkstra_find_weighted_path(
    start: Position,
    end: Position,
    is_valid_position: Callable[[Position], bool],
    get_cost: Callable[[Position], float],
    max_iterations: Optional[int] = None,
    sorted_directions: Optional[List[tuple]] = None,
    on_path_found: Optional[Callable[[List[Position], int], None]] = None,
    on_no_path: Optional[Callable[[int, int], None]] = None,
) -> List[Position]:
    """
    使用带权重的 Dijkstra 算法查找从起点到终点的路径
    
    Args:
        start: 起始位置
        end: 目标位置
        is_valid_position: 判断位置是否有效的函数
        get_cost: 获取位置成本的函数，返回float类型成本值
        max_iterations: 最大迭代次数，默认为 None（无限制）
        sorted_directions: 可选的方向列表（已排序），默认为 None（使用默认排序）
        on_path_found: 找到路径时的回调函数 (path, iterations)
        on_no_path: 未找到路径时的回调函数 (iterations, visited_count)
    
    Returns:
        路径位置列表，如果无法找到路径则返回空列表
    """
    if start == end:
        return [start]
    
    if sorted_directions is None:
        from ..constants import DIRECTIONS
        dx_total = end.x - start.x
        dy_total = end.y - start.y
        sorted_directions = get_sorted_directions(dx_total, dy_total)
    
    parent: Dict[Position, Position] = {}
    cost: Dict[Position, float] = {start: 0.0}
    
    counter = 0
    heap = [(0.0, counter, start)]
    iterations = 0
    
    while heap:
        if max_iterations is not None and iterations >= max_iterations:
            if on_no_path:
                on_no_path(iterations, len(cost))
            return []
        
        iterations += 1
        current_cost, _, curr = heapq.heappop(heap)
        
        if curr == end:
            path = reconstruct_path(parent, start, end)
            if on_path_found:
                on_path_found(path, iterations)
            return path
        
        if current_cost > cost.get(curr, float('inf')):
            continue
        
        for dx, dy in sorted_directions:
            next_pos = Position(curr.x + dx, curr.y + dy)
            
            if is_valid_position(next_pos):
                pos_cost = get_cost(next_pos)
                
                if pos_cost <= 0.0:
                    continue
                
                new_cost = current_cost + pos_cost
                
                if next_pos not in cost or new_cost < cost[next_pos]:
                    cost[next_pos] = new_cost
                    parent[next_pos] = curr
                    counter += 1
                    heapq.heappush(heap, (new_cost, counter, next_pos))
    
    if on_no_path:
        on_no_path(iterations, len(cost))
    return []

