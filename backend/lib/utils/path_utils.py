"""
路径工具类
提供路径相关的工具函数
"""

from typing import List, Optional, TYPE_CHECKING
from ..data_models import Position, Team

if TYPE_CHECKING:
    from ..map_service import GameMap
else:
    GameMap = None


class PathUtils:
    """路径工具类 - 单一职责：处理路径相关操作"""
    
    @staticmethod
    def filter_path_by_territory(path: List[Position], game_map: GameMap, 
                                 team: Team, keep_my_territory: bool = True) -> List[Position]:
        """
        根据领地过滤路径
        
        Args:
            path: 原始路径
            game_map: 地图实例
            team: 队伍
            keep_my_territory: 是否保留己方领地的部分
        Returns:
            过滤后的路径
        """
        if not path:
            return []
        
        filtered = []
        for pos in path:
            is_in_my_territory = game_map.is_in_team_territory(pos, team)
            if (keep_my_territory and is_in_my_territory) or \
               (not keep_my_territory and not is_in_my_territory):
                filtered.append(pos)
            elif not keep_my_territory:
                # 如果遇到敌方领地，停止
                break
        
        return filtered if filtered else path
    
    @staticmethod
    def find_intersection_with_middle_line(path: List[Position], 
                                          middle_line: float) -> Optional[Position]:
        """
        找到路径与中线的交点
        
        Args:
            path: 路径列表
            middle_line: 中线x坐标
        Returns:
            交点位置，如果没有交点则返回None
        """
        if not path:
            return None
        
        prev_pos = path[0]
        for pos in path[1:]:
            # 检查是否跨越中线
            if (prev_pos.x < middle_line <= pos.x) or (prev_pos.x >= middle_line > pos.x):
                # 返回更接近中线的位置
                if abs(prev_pos.x - middle_line) < abs(pos.x - middle_line):
                    return prev_pos
                else:
                    return pos
            prev_pos = pos
        
        return None
    
    @staticmethod
    def simplify_path(path: List[Position], max_length: Optional[int] = None) -> List[Position]:
        """
        简化路径，移除冗余点
        
        Args:
            path: 原始路径
            max_length: 最大长度（可选）
        Returns:
            简化后的路径
        """
        if not path:
            return []
        
        if max_length and len(path) <= max_length:
            return path
        
        # 简单的简化：只保留起点、终点和关键转折点
        if len(path) <= 2:
            return path
        
        simplified = [path[0]]
        for i in range(1, len(path) - 1):
            prev = simplified[-1]
            curr = path[i]
            next_pos = path[i + 1]
            
            # 如果当前点不是直线上的点，保留它
            dx1 = curr.x - prev.x
            dy1 = curr.y - prev.y
            dx2 = next_pos.x - curr.x
            dy2 = next_pos.y - curr.y
            
            if dx1 != dx2 or dy1 != dy2:
                simplified.append(curr)
        
        simplified.append(path[-1])
        
        if max_length and len(simplified) > max_length:
            # 如果还是太长，均匀采样
            step = len(simplified) / max_length
            return [simplified[int(i * step)] for i in range(max_length)]
        
        return simplified
    
    @staticmethod
    def get_path_length(path: List[Position]) -> int:
        """
        计算路径长度（步数）
        
        Args:
            path: 路径列表
        Returns:
            路径长度
        """
        if len(path) <= 1:
            return 0
        
        return len(path) - 1

