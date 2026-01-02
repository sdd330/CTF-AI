"""
位置坐标类
定义位置相关的数据结构和操作
"""

from dataclasses import dataclass
from .enums import Direction


@dataclass
class Position:
    """
    位置坐标类 - 面向对象设计
    
    设计原则：
    1. 封装：位置相关的所有操作都在类中
    2. 单一职责：只负责位置相关的计算和操作
    """
    x: int
    y: int
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def __eq__(self, other):
        if isinstance(other, Position):
            return self.x == other.x and self.y == other.y
        elif isinstance(other, tuple) and len(other) == 2:
            return self.x == other[0] and self.y == other[1]
        return False
    
    def to_tuple(self) -> tuple[int, int]:
        """转换为元组"""
        return (self.x, self.y)
    
    def manhattan_distance(self, other: 'Position') -> int:
        """
        计算曼哈顿距离 - 面向对象设计
        
        Args:
            other: 另一个位置
        Returns:
            曼哈顿距离
        """
        return abs(self.x - other.x) + abs(self.y - other.y)
    
    def direction_to(self, target: 'Position') -> Direction:
        """
        计算到目标位置的方向 - 面向对象设计
        
        注意：游戏只支持单一方向移动（上下左右），不支持对角线移动
        如果目标位置需要对角线移动，优先选择主要方向（距离变化更大的方向）
        
        Args:
            target: 目标位置
        Returns:
            Direction枚举
        """
        dx = target.x - self.x
        dy = target.y - self.y
        
        # 如果目标位置就是当前位置，返回STAY
        if dx == 0 and dy == 0:
            return Direction.STAY
        
        # 如果只需要移动一个方向，直接返回该方向
        if dx == 0:
            return Direction.DOWN if dy > 0 else Direction.UP
        if dy == 0:
            return Direction.RIGHT if dx > 0 else Direction.LEFT
        
        # 如果需要同时移动两个方向（不应该发生，但为了健壮性处理）
        # 优先选择距离变化更大的方向
        if abs(dx) > abs(dy):
            return Direction.RIGHT if dx > 0 else Direction.LEFT
        elif abs(dy) > abs(dx):
            return Direction.DOWN if dy > 0 else Direction.UP
        else:
            # 距离相等，优先选择x方向
            return Direction.RIGHT if dx > 0 else Direction.LEFT
    
    def __repr__(self) -> str:
        """字符串表示"""
        return f"Position(x={self.x}, y={self.y})"

