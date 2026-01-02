"""
玩家行为统计类
负责记录和统计玩家的行为表现
"""

from typing import Dict, Deque, List, Optional, TYPE_CHECKING
from collections import deque
from dataclasses import dataclass, field
from ..enums import Action, Direction, Strategy

if TYPE_CHECKING:
    from .player import Player


@dataclass
class BehaviorAttitude:
    """行为态度 - 玩家的行为倾向和偏好"""
    aggressiveness: float = 0.5  # 攻击性 (0.0-1.0, 越高越激进)
    defensiveness: float = 0.5    # 防守性 (0.0-1.0, 越高越保守)
    cooperation: float = 0.5      # 合作性 (0.0-1.0, 越高越愿意配合队友)
    risk_tolerance: float = 0.5   # 风险承受度 (0.0-1.0, 越高越愿意冒险)
    patience: float = 0.5         # 耐心度 (0.0-1.0, 越高越有耐心)


@dataclass
class BehaviorPerformance:
    """行为表现 - 玩家的行为统计数据"""
    # 举动统计
    actions_executed: Dict[Action, int] = field(default_factory=lambda: {
        Action.PICKUP_FLAG: 0,
        Action.DROP_FLAG: 0,
        Action.RESCUE_TEAMMATE: 0,
        Action.TAG_ENEMY: 0,
        Action.SCORE_FLAG: 0,
    })
    
    # 行动统计
    total_movements: int = 0
    total_distance: float = 0.0
    movements_by_direction: Dict[Direction, int] = field(default_factory=lambda: {
        Direction.UP: 0,
        Direction.DOWN: 0,
        Direction.LEFT: 0,
        Direction.RIGHT: 0,
        Direction.STAY: 0,
    })
    
    # 表现统计
    flags_picked_up: int = 0
    flags_scored: int = 0
    enemies_tagged: int = 0
    teammates_rescued: int = 0
    times_captured: int = 0
    times_in_prison: int = 0
    
    # 策略使用统计
    strategy_usage: Dict[Strategy, int] = field(default_factory=lambda: {
        Strategy.SCORING: 0,
        Strategy.DEFENCE: 0,
        Strategy.SAVING: 0,
    })


class PlayerBehaviorStats:
    """玩家行为统计器 - 负责记录和统计玩家的行为表现"""
    
    def __init__(self, player: 'Player'):
        self.player = player
        self.attitude = BehaviorAttitude()
        self.performance = BehaviorPerformance()
        self.action_history: Deque[Action] = deque(maxlen=50)
        self.movement_history: Deque[Direction] = deque(maxlen=50)
        self.behavior_patterns: Dict[str, int] = {}
    
    def record_action(self, action: Action) -> None:
        """记录玩家的举动"""
        self.performance.actions_executed[action] = \
            self.performance.actions_executed.get(action, 0) + 1
        self.action_history.append(action)
        
        # 根据动作更新表现统计
        if action == Action.PICKUP_FLAG:
            self.performance.flags_picked_up += 1
        elif action == Action.SCORE_FLAG:
            self.performance.flags_scored += 1
        elif action == Action.TAG_ENEMY:
            self.performance.enemies_tagged += 1
        elif action == Action.RESCUE_TEAMMATE:
            self.performance.teammates_rescued += 1
    
    def record_movement(self, direction: Direction, distance: float = 1.0) -> None:
        """记录玩家的行动（移动）"""
        if direction != Direction.STAY:
            self.performance.total_movements += 1
            self.performance.total_distance += distance
        self.performance.movements_by_direction[direction] = \
            self.performance.movements_by_direction.get(direction, 0) + 1
        self.movement_history.append(direction)
    
    def record_capture(self) -> None:
        """记录被捕获"""
        self.performance.times_captured += 1
        self.performance.times_in_prison += 1
    
    def record_strategy_usage(self, strategy: Strategy) -> None:
        """记录策略使用"""
        current_count = self.performance.strategy_usage.get(strategy, 0)
        self.performance.strategy_usage[strategy] = current_count + 1
    
    def get_action_count(self, action: Action) -> int:
        """获取某个动作的执行次数"""
        return self.performance.actions_executed.get(action, 0)
    
    def get_recent_actions(self, count: int = 10) -> List[Action]:
        """获取最近的动作历史"""
        return list(self.action_history)[-count:]
    
    def get_movement_statistics(self) -> Dict[str, any]:
        """获取移动统计信息"""
        return {
            "total_movements": self.performance.total_movements,
            "total_distance": self.performance.total_distance,
            "by_direction": dict(self.performance.movements_by_direction),
            "average_distance_per_move": (
                self.performance.total_distance / self.performance.total_movements
                if self.performance.total_movements > 0 else 0.0
            )
        }
    
    def get_recent_movements(self, count: int = 10) -> List[Direction]:
        """获取最近的移动历史"""
        return list(self.movement_history)[-count:]
    
    def get_performance_summary(self) -> Dict[str, any]:
        """获取表现摘要"""
        return {
            "flags_picked_up": self.performance.flags_picked_up,
            "flags_scored": self.performance.flags_scored,
            "enemies_tagged": self.performance.enemies_tagged,
            "teammates_rescued": self.performance.teammates_rescued,
            "times_captured": self.performance.times_captured,
            "times_in_prison": self.performance.times_in_prison,
            "strategy_usage": dict(self.performance.strategy_usage),
            "actions_executed": dict(self.performance.actions_executed),
        }
    
    def get_movement_pattern(self) -> Optional[Direction]:
        """分析移动模式，返回最常见的移动方向"""
        if not self.movement_history:
            return None
        
        direction_counts = {}
        for direction in self.movement_history:
            direction_counts[direction] = direction_counts.get(direction, 0) + 1
        
        if direction_counts:
            return max(direction_counts.items(), key=lambda x: x[1])[0]
        return None
    
    def set_attitude(self, aggressiveness: Optional[float] = None,
                    defensiveness: Optional[float] = None,
                    cooperation: Optional[float] = None,
                    risk_tolerance: Optional[float] = None,
                    patience: Optional[float] = None) -> None:
        """设置玩家态度"""
        if aggressiveness is not None:
            self.attitude.aggressiveness = max(0.0, min(1.0, aggressiveness))
        if defensiveness is not None:
            self.attitude.defensiveness = max(0.0, min(1.0, defensiveness))
        if cooperation is not None:
            self.attitude.cooperation = max(0.0, min(1.0, cooperation))
        if risk_tolerance is not None:
            self.attitude.risk_tolerance = max(0.0, min(1.0, risk_tolerance))
        if patience is not None:
            self.attitude.patience = max(0.0, min(1.0, patience))
    
    def get_attitude(self) -> BehaviorAttitude:
        """获取玩家态度"""
        return self.attitude
    
    def adjust_attitude_by_experience(self) -> None:
        """根据经验调整态度"""
        if self.performance.times_captured > 3:
            self.attitude.defensiveness = min(1.0, self.attitude.defensiveness + 0.1)
            self.attitude.risk_tolerance = max(0.0, self.attitude.risk_tolerance - 0.1)
        
        if self.performance.flags_scored > 2:
            self.attitude.aggressiveness = min(1.0, self.attitude.aggressiveness + 0.05)
    
    def update_behavior_pattern(self, pattern_name: str, value: int = 1) -> None:
        """更新行为模式"""
        self.behavior_patterns[pattern_name] = \
            self.behavior_patterns.get(pattern_name, 0) + value
    
    def analyze_behavior_pattern(self) -> Dict[str, any]:
        """分析行为模式（举止）"""
        patterns = {}
        
        # 分析移动模式
        movement_pattern = self.get_movement_pattern()
        if movement_pattern:
            patterns["preferred_direction"] = movement_pattern.value
        
        # 分析策略偏好
        if self.performance.strategy_usage:
            preferred_strategy = max(
                self.performance.strategy_usage.items(),
                key=lambda x: x[1]
            )[0]
            patterns["preferred_strategy"] = (
                preferred_strategy.value
                if isinstance(preferred_strategy, Strategy)
                else str(preferred_strategy)
            )
        
        # 分析行为风格（基于态度）
        if self.attitude.aggressiveness > 0.7:
            patterns["style"] = "aggressive"
        elif self.attitude.defensiveness > 0.7:
            patterns["style"] = "defensive"
        elif self.attitude.cooperation > 0.7:
            patterns["style"] = "cooperative"
        else:
            patterns["style"] = "balanced"
        
        return patterns
