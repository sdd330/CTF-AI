"""
策略评估器
用于评估和优化策略选择，提供更智能的策略驱动决策
"""

from typing import Optional, List, Tuple, TYPE_CHECKING
from ..data_models import Team, Strategy

if TYPE_CHECKING:
    from ..data_models.player import Player
    from ..game_engine import World


class StrategyEvaluator:
    """策略评估器 - 提供更智能的策略选择"""

    def __init__(self, world: 'World'):
        self.world = world

    def evaluate_strategy(self, player: 'Player', strategy: Strategy) -> float:
        """评估策略的适用性分数"""
        evaluators = {
            Strategy.SAVING: self._evaluate_saving_strategy,
            Strategy.DEFENCE: self._evaluate_defence_strategy,
            Strategy.SCORING: self._evaluate_scoring_strategy,
        }
        return evaluators.get(strategy, lambda p: 0.0)(player)

    def _evaluate_saving_strategy(self, player: 'Player') -> float:
        """评估营救策略的适用性"""
        teammates_in_prison = [p for p in self.world.my_players.values() if p.is_in_prison]
        if not teammates_in_prison:
            return 0.0

        free_players = [p for p in self.world.my_players.values()
                        if not p.is_in_prison and not p.has_flag]
        prison_ratio = len(teammates_in_prison) / max(1, len(teammates_in_prison) + len(free_players))
        urgency_score = prison_ratio * 50.0

        urgency_score += self._calc_prison_distance_score(player)
        urgency_score *= self._calc_rescuer_discount(player, free_players)

        return urgency_score

    def _evaluate_defence_strategy(self, player: 'Player') -> float:
        """评估防守策略的适用性"""
        my_team = player.team
        enemies = [p for p in self.world.enemy_players.values() if not p.is_in_prison]
        enemies_in_territory = [e for e in enemies
                                 if self.world.map.is_in_team_territory(e.position, my_team)]

        if not enemies_in_territory:
            return 0.0

        free_teammates = [p for p in self.world.my_players.values()
                          if not p.is_in_prison and not p.has_flag]
        enemy_ratio = len(enemies_in_territory) / max(1, len(free_teammates))
        urgency_score = enemy_ratio * 40.0

        if any(e.has_flag for e in enemies_in_territory):
            urgency_score += 30.0

        min_dist = min((player.position.manhattan_distance(e.position) for e in enemies_in_territory),
                       default=float('inf'))
        urgency_score += max(0, 20.0 - min_dist * 2)
        urgency_score *= self._calc_defender_discount(player, free_teammates, enemies_in_territory)

        return urgency_score

    def _evaluate_scoring_strategy(self, player: 'Player') -> float:
        """评估抢旗策略的适用性"""
        enemy_flags = [f for f in self.world.enemy_flags.values() if f.can_pickup]
        if not enemy_flags:
            return 0.0

        nearest_flag = min(enemy_flags, key=lambda f: player.position.manhattan_distance(f.position))
        min_dist = player.position.manhattan_distance(nearest_flag.position)
        value_score = max(0, 30.0 - min_dist * 1.5)

        my_team = player.team
        my_score = self.world.left_team_score if my_team == Team.LEFT else self.world.right_team_score
        enemy_score = self.world.right_team_score if my_team == Team.LEFT else self.world.left_team_score

        if my_score < enemy_score:
            value_score += abs(my_score - enemy_score) * 10.0
        elif my_score == enemy_score:
            value_score += 5.0

        value_score *= self._calc_scorer_discount(player, nearest_flag)
        return value_score

    def _calc_prison_distance_score(self, player: 'Player') -> float:
        """计算到监狱的距离分数"""
        enemy_prison = self.world.map.get_team_prison_area(player.team.get_enemy())
        if not enemy_prison:
            return 0.0
        min_dist = min((player.position.manhattan_distance(pos) for pos in enemy_prison.positions),
                       default=float('inf'))
        return max(0, 30.0 - min_dist * 2) if min_dist < float('inf') else 0.0

    def _calc_rescuer_discount(self, player: 'Player', free_players: List) -> float:
        """计算营救者折扣"""
        enemy_prison = self.world.map.get_team_prison_area(player.team.get_enemy())
        if not enemy_prison:
            return 1.0
        other_rescuers = sum(1 for t in free_players if t.name != player.name
                             and any(t.position.manhattan_distance(pos) <= 5
                                     for pos in enemy_prison.positions))
        return 1.0 / (1.0 + other_rescuers * 0.3)

    def _calc_defender_discount(self, player: 'Player', teammates: List, enemies: List) -> float:
        """计算防守者折扣"""
        other_defenders = sum(1 for t in teammates if t.name != player.name
                              and any(t.position.manhattan_distance(e.position) <= 3 for e in enemies))
        return 1.0 / (1.0 + other_defenders * 0.3)

    def _calc_scorer_discount(self, player: 'Player', nearest_flag) -> float:
        """计算抢旗者折扣"""
        free_teammates = [p for p in self.world.my_players.values()
                          if not p.is_in_prison and not p.has_flag]
        other_scorers = sum(1 for t in free_teammates if t.name != player.name
                            and t.position.manhattan_distance(nearest_flag.position) <= 5)
        return 1.0 / (1.0 + other_scorers * 0.2)

    def select_best_strategy(self, player: 'Player',
                              suggested_strategy: Optional[Strategy] = None) -> Strategy:
        """选择最佳策略"""
        if player.has_flag or player.is_in_prison:
            return Strategy.SCORING

        strategies = [Strategy.SAVING, Strategy.DEFENCE, Strategy.SCORING]
        scores = {s: self.evaluate_strategy(player, s) for s in strategies}

        if suggested_strategy and suggested_strategy in scores:
            scores[suggested_strategy] *= 1.2

        valid = {k: v for k, v in scores.items() if v > 0}
        if not valid:
            return Strategy.SCORING

        best = max(valid.items(), key=lambda x: x[1])[0]
        return best if scores[best] >= 5.0 else Strategy.SCORING

    def get_strategy_priority(self, player: 'Player') -> List[Tuple[Strategy, float]]:
        """获取策略优先级列表"""
        if player.has_flag:
            return [(Strategy.SCORING, 100.0)]
        if player.is_in_prison:
            return [(Strategy.SCORING, 0.0)]

        strategies = [Strategy.SAVING, Strategy.DEFENCE, Strategy.SCORING]
        scores = [(s, self.evaluate_strategy(player, s)) for s in strategies]
        return sorted(scores, key=lambda x: x[1], reverse=True)
