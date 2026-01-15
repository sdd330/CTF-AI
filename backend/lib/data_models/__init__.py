"""
游戏基础数据模型
统一导出所有数据模型
"""

# 从拆分的模块中导入并重新导出
from .enums import Team, Direction, PlayerState, Action, Strategy
from .position import Position
from .areas import TargetArea, PrisonArea
from .player.player import Player
from .flag import Flag
from .status import PlayerStatus, FlagStatus

# 导出所有类
__all__ = [
    'Team',
    'Direction',
    'PlayerState',
    'Action',
    'Strategy',
    'Position',
    'TargetArea',
    'PrisonArea',
    'Player',
    'Flag',
    'PlayerStatus',
    'FlagStatus',
]

