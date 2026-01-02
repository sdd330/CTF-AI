"""
枚举类型定义
定义游戏中使用的所有枚举类型
"""

from enum import Enum


class Team(Enum):
    """队伍枚举 - 面向对象设计"""
    LEFT = "L"
    RIGHT = "R"
    
    def get_enemy(self) -> 'Team':
        """
        获取敌方队伍 - 面向对象设计，将工具函数移到类中
        
        Returns:
            敌方队伍
        """
        return Team.RIGHT if self == Team.LEFT else Team.LEFT
    
    @classmethod
    def from_name(cls, team_name: str) -> 'Team | None':
        """
        从队伍名称获取Team枚举 - 面向对象设计
        
        Args:
            team_name: 队伍名称 ("L" 或 "R")
        Returns:
            Team枚举，如果无效则返回None
        """
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


class PlayerState(Enum):
    """玩家状态枚举"""
    FREE = "free"
    IN_PRISON = "in_prison"
    CARRYING_FLAG = "carrying_flag"


class Action(Enum):
    """动作枚举 - 玩家可执行的具体动作"""
    PICKUP_FLAG = "pickup_flag"  # 拾取旗帜
    DROP_FLAG = "drop_flag"  # 放下旗帜
    RESCUE_TEAMMATE = "rescue_teammate"  # 营救队友
    TAG_ENEMY = "tag_enemy"  # 标记敌人
    SCORE_FLAG = "score_flag"  # 得分


class Strategy(Enum):
    """策略枚举 - 用于智能体决策"""
    DEFENCE = 0  # 防守
    SCORING = 1  # 抢旗
    SAVING = 2   # 营救

