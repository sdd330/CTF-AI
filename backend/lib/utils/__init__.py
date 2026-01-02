"""
工具模块
统一导出所有工具函数和类
"""

# 工具类
from .distance_calculator import DistanceCalculator
from .path_utils import PathUtils
from .game_statistics import GameStatistics
# StrategyEvaluator 延迟导入以避免循环依赖
# from .strategy_evaluator import StrategyEvaluator
from .player_utils import (
    list_players, 
    list_flags,
    can_tag_enemy,
    can_rescue_teammate,
    can_pickup_flag,
    can_score_flag
)

# 常量（从 lib.constants 导入，不在此处导入以避免循环依赖）

# 状态管理
from .state_manager import StateManager


__all__ = [
    # 工具类
    'DistanceCalculator',
    'PathUtils',
    'GameStatistics',
    # 'StrategyEvaluator',  # 延迟导入，避免循环依赖
    # 游戏查询工具
    'list_players',
    'list_flags',
    # 游戏规则检查工具
    'can_tag_enemy',
    'can_rescue_teammate',
    'can_pickup_flag',
    'can_score_flag',
    # 状态管理
    'StateManager',
]

