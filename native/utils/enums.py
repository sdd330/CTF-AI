"""
枚举类型定义
"""

from enum import Enum


class Team(Enum):
    """队伍枚举"""
    LEFT = "L"
    RIGHT = "R"
    
    def get_enemy(self) -> 'Team':
        """获取敌方队伍"""
        return Team.RIGHT if self == Team.LEFT else Team.LEFT
    
    @classmethod
    def from_name(cls, team_name: str) -> 'Team | None':
        """从队伍名称获取Team枚举"""
        if team_name == "L":
            return cls.LEFT
        elif team_name == "R":
            return cls.RIGHT
        return None


class Direction(Enum):
    """方向枚举"""
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    STAY = ""  # 保持不动
    
    def to_vector(self) -> tuple[int, int]:
        """转换为向量 (dx, dy)"""
        if self == Direction.UP:
            return (0, -1)
        elif self == Direction.DOWN:
            return (0, 1)
        elif self == Direction.LEFT:
            return (-1, 0)
        elif self == Direction.RIGHT:
            return (1, 0)
        else:
            return (0, 0)


class PlayerState(Enum):
    """玩家状态枚举"""
    FREE = "free"
    IN_PRISON = "in_prison"
    CARRYING_FLAG = "carrying_flag"

