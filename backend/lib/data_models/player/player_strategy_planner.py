"""
玩家策略规划类
负责生成和选择策略
"""

from typing import Optional, TYPE_CHECKING
from ..enums import Strategy

if TYPE_CHECKING:
    from .player import Player


class PlayerStrategyPlanner:
    """玩家策略规划器 - 负责生成和选择策略"""
    
    def __init__(self, player: 'Player'):
        self.player = player
    
    def generate_strategy(self) -> Strategy:
        """
        根据 world 状态生成策略 - 完全基于 World 状态的自驱动决策
        
        Returns:
            策略枚举：Strategy.DEFENCE/SCORING/SAVING
        """
        from ...utils.strategy_evaluator import StrategyEvaluator
        
        evaluator = StrategyEvaluator(self.player.world)
        return evaluator.select_best_strategy(self.player)
