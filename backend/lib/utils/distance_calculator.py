"""
距离计算工具类
提供各种距离计算和最近实体查找功能
"""

from typing import List, Optional, Callable, TypeVar, TYPE_CHECKING
from ..data_models import Position

if TYPE_CHECKING:
    from ..data_models import Player, Flag

T = TypeVar('T')


class DistanceCalculator:
    """距离计算器 - 单一职责：计算距离和查找最近实体"""
    
    @staticmethod
    def find_closest_position(start: Position, targets: List[Position]) -> Optional[Position]:
        """
        找到最近的目标位置
        
        使用曼哈顿距离计算，返回距离最近的目标
        
        Args:
            start: 起始位置
            targets: 目标位置列表
        Returns:
            最近的目标位置，如果没有目标则返回None
        """
        if not targets:
            return None
        
        return min(targets, key=lambda t: start.manhattan_distance(t), default=None)
    
    @staticmethod
    def find_closest_entity(start: Position, entities: List[T], 
                           position_getter: Callable[[T], Position]) -> Optional[T]:
        """
        找到最近的实体（通用方法）
        
        Args:
            start: 起始位置
            entities: 实体列表
            position_getter: 获取实体位置的函数
        Returns:
            最近的实体，如果没有实体则返回None
        """
        if not entities:
            return None
        
        return min(entities, key=lambda e: start.manhattan_distance(position_getter(e)), default=None)
    
    @staticmethod
    def find_closest_opponent(player_pos: Position, opponents: List['Player']) -> Optional['Player']:
        """
        找到最近的敌人
        
        Args:
            player_pos: 玩家位置
            opponents: 敌人列表
        Returns:
            最近的敌人，如果没有敌人则返回None
        """
        return DistanceCalculator.find_closest_entity(
            player_pos, opponents, lambda p: p.position
        )
    
    @staticmethod
    def find_closest_flag(player_pos: Position, flags: List['Flag']) -> Optional['Flag']:
        """
        找到最近的旗帜
        
        Args:
            player_pos: 玩家位置
            flags: 旗帜列表
        Returns:
            最近的旗帜，如果没有旗帜则返回None
        """
        return DistanceCalculator.find_closest_entity(
            player_pos, flags, lambda f: f.position
        )
    
    @staticmethod
    def find_closest_player(start_pos: Position, players: List['Player']) -> Optional['Player']:
        """
        找到最近的玩家
        
        Args:
            start_pos: 起始位置
            players: 玩家列表
        Returns:
            最近的玩家，如果没有玩家则返回None
        """
        return DistanceCalculator.find_closest_entity(
            start_pos, players, lambda p: p.position
        )
    
    @staticmethod
    def calculate_distance(pos1: Position, pos2: Position) -> int:
        """
        计算两个位置之间的曼哈顿距离
        
        Args:
            pos1: 位置1
            pos2: 位置2
        Returns:
            曼哈顿距离
        """
        return pos1.manhattan_distance(pos2)
    
    @staticmethod
    def sort_by_distance(start: Position, targets: List[Position], 
                        reverse: bool = False) -> List[Position]:
        """
        按距离排序目标位置列表
        
        Args:
            start: 起始位置
            targets: 目标位置列表
            reverse: 是否降序排列（距离远的在前）
        Returns:
            排序后的位置列表
        """
        return sorted(targets, key=lambda t: start.manhattan_distance(t), reverse=reverse)

