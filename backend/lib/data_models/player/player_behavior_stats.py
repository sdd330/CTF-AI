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
    aggressiveness: float = 0.5
    defensiveness: float = 0.5
    cooperation: float = 0.5
    risk_tolerance: float = 0.5
    patience: float = 0.5


@dataclass
class BehaviorPerformance:
    """行为表现 - 玩家的行为统计数据"""
    actions_executed: Dict[Action, int] = field(default_factory=lambda: {a: 0 for a in Action})
    total_movements: int = 0
    total_distance: float = 0.0
    movements_by_direction: Dict[Direction, int] = field(default_factory=lambda: {d: 0 for d in Direction})
    flags_picked_up: int = 0
    flags_scored: int = 0
    enemies_tagged: int = 0
    teammates_rescued: int = 0
    times_captured: int = 0
    times_in_prison: int = 0
    strategy_usage: Dict[Strategy, int] = field(default_factory=lambda: {s: 0 for s in Strategy})


class PlayerBehaviorStats:
    """玩家行为统计器"""

    def __init__(self, player: 'Player'):
        self.player = player
        self.attitude = BehaviorAttitude()
        self.performance = BehaviorPerformance()
        self.action_history: Deque[Action] = deque(maxlen=50)
        self.movement_history: Deque[Direction] = deque(maxlen=50)
        self.behavior_patterns: Dict[str, int] = {}

    def record_action(self, action: Action) -> None:
        """记录玩家的举动"""
        self.performance.actions_executed[action] = self.performance.actions_executed.get(action, 0) + 1
        self.action_history.append(action)

        action_stats = {
            Action.PICKUP_FLAG: 'flags_picked_up',
            Action.SCORE_FLAG: 'flags_scored',
            Action.TAG_ENEMY: 'enemies_tagged',
            Action.RESCUE_TEAMMATE: 'teammates_rescued',
        }
        if action in action_stats:
            setattr(self.performance, action_stats[action],
                    getattr(self.performance, action_stats[action]) + 1)

    def record_movement(self, direction: Direction, distance: float = 1.0) -> None:
        """记录玩家的行动"""
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
        self.performance.strategy_usage[strategy] = self.performance.strategy_usage.get(strategy, 0) + 1

    def get_action_count(self, action: Action) -> int:
        return self.performance.actions_executed.get(action, 0)

    def get_recent_actions(self, count: int = 10) -> List[Action]:
        return list(self.action_history)[-count:]

    def get_recent_movements(self, count: int = 10) -> List[Direction]:
        return list(self.movement_history)[-count:]

    def get_movement_statistics(self) -> Dict:
        return {
            "total_movements": self.performance.total_movements,
            "total_distance": self.performance.total_distance,
            "by_direction": dict(self.performance.movements_by_direction),
            "average_distance_per_move": (self.performance.total_distance / self.performance.total_movements
                                          if self.performance.total_movements > 0 else 0.0)
        }

    def get_performance_summary(self) -> Dict:
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
        """返回最常见的移动方向"""
        if not self.movement_history:
            return None
        counts = {}
        for d in self.movement_history:
            counts[d] = counts.get(d, 0) + 1
        return max(counts.items(), key=lambda x: x[1])[0] if counts else None

    def set_attitude(self, **kwargs) -> None:
        """设置玩家态度"""
        for attr in ['aggressiveness', 'defensiveness', 'cooperation', 'risk_tolerance', 'patience']:
            if attr in kwargs:
                setattr(self.attitude, attr, max(0.0, min(1.0, kwargs[attr])))

    def get_attitude(self) -> BehaviorAttitude:
        return self.attitude

    def adjust_attitude_by_experience(self) -> None:
        """根据经验调整态度"""
        if self.performance.times_captured > 3:
            self.attitude.defensiveness = min(1.0, self.attitude.defensiveness + 0.1)
            self.attitude.risk_tolerance = max(0.0, self.attitude.risk_tolerance - 0.1)
        if self.performance.flags_scored > 2:
            self.attitude.aggressiveness = min(1.0, self.attitude.aggressiveness + 0.05)

    def update_behavior_pattern(self, pattern_name: str, value: int = 1) -> None:
        self.behavior_patterns[pattern_name] = self.behavior_patterns.get(pattern_name, 0) + value

    def analyze_behavior_pattern(self) -> Dict:
        """分析行为模式"""
        patterns = {}
        movement_pattern = self.get_movement_pattern()
        if movement_pattern:
            patterns["preferred_direction"] = movement_pattern.value

        if self.performance.strategy_usage:
            preferred = max(self.performance.strategy_usage.items(), key=lambda x: x[1])[0]
            patterns["preferred_strategy"] = preferred.value if isinstance(preferred, Strategy) else str(preferred)

        if self.attitude.aggressiveness > 0.7:
            patterns["style"] = "aggressive"
        elif self.attitude.defensiveness > 0.7:
            patterns["style"] = "defensive"
        elif self.attitude.cooperation > 0.7:
            patterns["style"] = "cooperative"
        else:
            patterns["style"] = "balanced"

        return patterns
