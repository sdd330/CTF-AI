"""
广度优先搜索（BFS）算法通用实现
提供可复用的 BFS 功能，包括路径查找和区域扩展
"""

from collections import deque
from typing import List, Set, Optional, Dict, Callable, Tuple
from ..data_models import Position
from ..constants import DIRECTIONS


def calculate_direction_priority(dx: int, dy: int, dx_total: int, dy_total: int) -> int:
    """
    计算方向优先级：朝向目标的方向优先级更高，水平方向优先于垂直方向
    
    Args:
        dx: 当前方向的 x 偏移
        dy: 当前方向的 y 偏移
        dx_total: 目标的总 x 偏移
        dy_total: 目标的总 y 偏移
    
    Returns:
        优先级值（数值越大优先级越高）
    """
    priority = 0
    if (dx_total > 0 and dx > 0) or (dx_total < 0 and dx < 0):
        priority += 20
    if (dy_total > 0 and dy > 0) or (dy_total < 0 and dy < 0):
        priority += 10
    return priority


def get_sorted_directions(dx_total: int, dy_total: int, 
                          directions: Optional[List[Tuple[int, int]]] = None) -> List[Tuple[int, int]]:
    """
    获取按优先级排序的方向列表
    
    Args:
        dx_total: 目标的总 x 偏移
        dy_total: 目标的总 y 偏移
        directions: 可选的方向列表，默认为 DIRECTIONS
    
    Returns:
        按优先级排序的方向列表
    """
    if directions is None:
        directions = DIRECTIONS
    
    sorted_directions = sorted(
        directions, 
        key=lambda d: -calculate_direction_priority(d[0], d[1], dx_total, dy_total)
    )
    return sorted_directions


def bfs_find_path(
    start: Position,
    end: Position,
    is_valid_position: Callable[[Position], bool],
    max_iterations: Optional[int] = None,
    sorted_directions: Optional[List[Tuple[int, int]]] = None,
    on_path_found: Optional[Callable[[List[Position], int], None]] = None,
    on_no_path: Optional[Callable[[int], None]] = None,
) -> List[Position]:
    """
    使用 BFS 查找从起点到终点的路径
    
    Args:
        start: 起始位置
        end: 目标位置
        is_valid_position: 判断位置是否有效的函数
        max_iterations: 最大迭代次数，默认为 None（无限制）
        sorted_directions: 可选的方向列表（已排序），默认为 None（使用默认排序）
        on_path_found: 找到路径时的回调函数 (path, iterations)
        on_no_path: 未找到路径时的回调函数 (iterations)
    
    Returns:
        路径位置列表，如果无法找到路径则返回空列表
    """
    if start == end:
        return [start]
    
    # 计算方向优先级并排序
    if sorted_directions is None:
        dx_total = end.x - start.x
        dy_total = end.y - start.y
        sorted_directions = get_sorted_directions(dx_total, dy_total)
    
    queue = deque([[start]])
    seen = {start}
    iterations = 0
    
    while queue:
        if max_iterations is not None and iterations >= max_iterations:
            if on_no_path:
                on_no_path(iterations)
            return []
        
        iterations += 1
        path = queue.popleft()
        curr = path[-1]
        
        if curr == end:
            if on_path_found:
                on_path_found(path, iterations)
            return path
        
        for dx, dy in sorted_directions:
            next_pos = Position(curr.x + dx, curr.y + dy)
            if is_valid_position(next_pos) and next_pos not in seen:
                queue.append(path + [next_pos])
                seen.add(next_pos)
    
    if on_no_path:
        on_no_path(iterations)
    return []


def bfs_expand(
    start: Position,
    is_valid_position: Callable[[Position], bool],
    max_distance: Optional[int] = None,
    directions: Optional[List[Tuple[int, int]]] = None,
) -> Dict[Position, int]:
    """
    使用 BFS 从指定位置向外扩展，返回距离映射
    
    Args:
        start: 起始位置
        is_valid_position: 判断位置是否有效的函数
        max_distance: 最大扩展距离，默认为 None（无限制）
        directions: 可选的方向列表，默认为 [(0, -1), (0, 1), (-1, 0), (1, 0)]
    
    Returns:
        位置到距离的映射字典
    """
    if directions is None:
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
    
    distance_map: Dict[Position, int] = {start: 0}
    queue = deque([(start, 0)])
    
    while queue:
        pos, dist = queue.popleft()
        
        if max_distance is not None and dist >= max_distance:
            continue
        
        for dx, dy in directions:
            next_pos = Position(pos.x + dx, pos.y + dy)
            if (is_valid_position(next_pos) and 
                next_pos not in distance_map):
                distance_map[next_pos] = dist + 1
                queue.append((next_pos, dist + 1))
    
    return distance_map

