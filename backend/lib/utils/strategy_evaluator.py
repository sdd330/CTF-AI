"""
策略评估器
用于评估和优化策略选择，提供更智能的策略驱动决策
"""

from typing import Optional, List, Dict, Tuple, TYPE_CHECKING
from ..data_models import Team, Strategy, Position

if TYPE_CHECKING:
    from ..data_models.player import Player
    from ..data_models.flag import Flag
    from ..game_engine import World

from .player_utils import list_players, list_flags
from .distance_calculator import DistanceCalculator


class StrategyEvaluator:
    """策略评估器 - 提供更智能的策略选择"""
    
    def __init__(self, world: 'World'):
        """
        初始化策略评估器
        
        Args:
            world: World对象
        """
        self.world = world
    
    def evaluate_strategy(self, player: 'Player', strategy: Strategy) -> float:
        """
        评估策略的适用性分数
        
        Args:
            player: 玩家对象
            strategy: 策略类型
            
        Returns:
            策略适用性分数（越高越好）
        """
        if strategy == Strategy.SAVING:
            # 只有己方有队友在监狱时，这个分数才会 > 0
            return self._evaluate_saving_strategy(player)
        elif strategy == Strategy.DEFENCE:
            return self._evaluate_defence_strategy(player)
        elif strategy == Strategy.SCORING:
            return self._evaluate_scoring_strategy(player)
        else:
            return 0.0
    
    def _evaluate_saving_strategy(self, player: 'Player') -> float:
        """评估营救策略的适用性"""
        my_team = player.team
        teammates_in_prison = list_players(self.world.players, my_team, in_prison=True, has_flag=None)
        
        if not teammates_in_prison:
            return 0.0
        
        # 计算营救紧迫性
        urgency_score = 0.0
        
        # 1. 考虑监狱中的队友数量
        prison_count = len(teammates_in_prison)
        free_count = len(list_players(self.world.players, my_team, in_prison=False, has_flag=False))
        total_count = prison_count + free_count
        
        if total_count > 0:
            # 如果大部分队友在监狱，营救更紧迫
            prison_ratio = prison_count / total_count
            urgency_score += prison_ratio * 50.0
        
        # 2. 考虑玩家到监狱的距离
        enemy_team = my_team.get_enemy()
        enemy_prison_area = self.world.get_team_prison_area(enemy_team)
        if enemy_prison_area:
            min_prison_dist = float('inf')
            for prison_pos in enemy_prison_area.positions:
                dist = player.position.manhattan_distance(prison_pos)
                min_prison_dist = min(min_prison_dist, dist)
            
            # 距离越近，分数越高
            if min_prison_dist < float('inf'):
                distance_score = max(0, 30.0 - min_prison_dist * 2)
                urgency_score += distance_score
        
        # 3. 考虑是否有其他队友在营救
        other_rescuers = 0
        for teammate in list_players(self.world.players, my_team, in_prison=False, has_flag=False):
            if teammate.name != player.name:
                # 简单检查：如果队友也在监狱附近，可能也在营救
                if enemy_prison_area:
                    for prison_pos in enemy_prison_area.positions:
                        if teammate.position.manhattan_distance(prison_pos) <= 5:
                            other_rescuers += 1
                            break
        
        # 如果有很多队友在营救，降低紧迫性
        if other_rescuers > 0:
            urgency_score *= (1.0 / (1.0 + other_rescuers * 0.3))
        
        return urgency_score
    
    def _evaluate_defence_strategy(self, player: 'Player') -> float:
        """评估防守策略的适用性"""
        my_team = player.team
        enemy_team = my_team.get_enemy()
        enemies = list_players(self.world.players, enemy_team, in_prison=False, has_flag=None)
        
        # 找到在己方领地内的敌人
        enemies_in_territory = [e for e in enemies if self.world.is_in_team_territory(e.position, my_team)]
        
        if not enemies_in_territory:
            return 0.0
        
        # 计算防守紧迫性
        urgency_score = 0.0
        
        # 1. 考虑敌人数量
        enemy_count = len(enemies_in_territory)
        free_teammates = list_players(self.world.players, my_team, in_prison=False, has_flag=False)
        free_count = len(free_teammates)
        
        if free_count > 0:
            # 如果敌人数量多，防守更紧迫
            enemy_ratio = enemy_count / free_count
            urgency_score += enemy_ratio * 40.0
        
        # 2. 考虑敌人是否持旗
        flag_carriers = [e for e in enemies_in_territory if e.has_flag]
        if flag_carriers:
            urgency_score += 30.0  # 持旗敌人威胁更大
        
        # 3. 考虑玩家到敌人的距离
        min_enemy_dist = float('inf')
        for enemy in enemies_in_territory:
            dist = player.position.manhattan_distance(enemy.position)
            min_enemy_dist = min(min_enemy_dist, dist)
        
        if min_enemy_dist < float('inf'):
            # 距离越近，分数越高
            distance_score = max(0, 20.0 - min_enemy_dist * 2)
            urgency_score += distance_score
        
        # 4. 考虑是否有其他队友在防守
        other_defenders = 0
        for teammate in free_teammates:
            if teammate.name != player.name:
                # 检查队友是否也在敌人附近
                for enemy in enemies_in_territory:
                    if teammate.position.manhattan_distance(enemy.position) <= 3:
                        other_defenders += 1
                        break
        
        # 如果有很多队友在防守，降低紧迫性
        if other_defenders > 0:
            urgency_score *= (1.0 / (1.0 + other_defenders * 0.3))
        
        return urgency_score
    
    def _evaluate_scoring_strategy(self, player: 'Player') -> float:
        """评估抢旗策略的适用性"""
        my_team = player.team
        enemy_flags = list_flags(self.world.flags, my_team, is_enemy=True, can_pickup=True)
        
        if not enemy_flags:
            return 0.0
        
        # 计算抢旗价值
        value_score = 0.0
        
        # 1. 考虑玩家到旗帜的距离
        min_flag_dist = float('inf')
        nearest_flag = None
        for flag in enemy_flags:
            dist = player.position.manhattan_distance(flag.position)
            if dist < min_flag_dist:
                min_flag_dist = dist
                nearest_flag = flag
        
        if min_flag_dist < float('inf'):
            # 距离越近，分数越高
            distance_score = max(0, 30.0 - min_flag_dist * 1.5)
            value_score += distance_score
        
        # 2. 考虑比分差距（如果落后，抢旗更紧迫）
        my_score = self.world.left_team_score if my_team == Team.LEFT else self.world.right_team_score
        enemy_score = self.world.right_team_score if my_team == Team.LEFT else self.world.left_team_score
        score_diff = my_score - enemy_score
        
        if score_diff < 0:
            # 落后时，抢旗更紧迫
            value_score += abs(score_diff) * 10.0
        elif score_diff == 0:
            # 平局时，保持抢旗
            value_score += 5.0
        
        # 3. 考虑是否有其他队友在抢旗
        free_teammates = list_players(self.world.players, my_team, in_prison=False, has_flag=False)
        other_scorers = 0
        for teammate in free_teammates:
            if teammate.name != player.name:
                # 检查队友是否也在旗帜附近
                if nearest_flag:
                    if teammate.position.manhattan_distance(nearest_flag.position) <= 5:
                        other_scorers += 1
        
        # 如果有很多队友在抢旗，降低价值
        if other_scorers > 0:
            value_score *= (1.0 / (1.0 + other_scorers * 0.2))
        
        return value_score
    
    def select_best_strategy(self, player: 'Player', suggested_strategy: Optional[Strategy] = None) -> Strategy:
        """
        选择最佳策略
        
        Args:
            player: 玩家对象
            suggested_strategy: 外部建议的策略（如RL输出）
            
        Returns:
            最佳策略
        """
        # 如果玩家持有旗帜，必须返回基地
        if player.has_flag:
            return Strategy.SCORING  # 返回基地也是SCORING策略的一部分
        
        # 如果玩家在监狱中，无法行动
        if player.is_in_prison:
            return Strategy.SCORING  # 在监狱中暂不行动，保持默认策略
        
        # 评估所有策略：营救 + 防守 + 抢旗
        strategies = [Strategy.SAVING, Strategy.DEFENCE, Strategy.SCORING]
        strategy_scores = {}
        
        for strategy in strategies:
            score = self.evaluate_strategy(player, strategy)
            strategy_scores[strategy] = score
        
        # 如果提供了建议策略，给予额外权重
        if suggested_strategy is not None:
            if suggested_strategy in strategy_scores:
                strategy_scores[suggested_strategy] *= 1.2  # 增加20%权重
        
        # 排除分数为0的策略（如没有队友在监狱时，SAVING策略分数为0）
        valid_strategies = {k: v for k, v in strategy_scores.items() if v > 0}
        
        # 如果没有有效策略，使用默认的SCORING策略
        if not valid_strategies:
            return Strategy.SCORING
        
        # 选择分数最高的策略
        best_strategy = max(valid_strategies.items(), key=lambda x: x[1])[0]
        
        # 如果最高分数太低，使用默认策略
        if strategy_scores[best_strategy] < 5.0:
            best_strategy = Strategy.SCORING
        
        return best_strategy
    
    def get_strategy_priority(self, player: 'Player') -> List[Tuple[Strategy, float]]:
        """
        获取策略优先级列表
        
        Args:
            player: 玩家对象
            
        Returns:
            策略和分数的列表，按分数降序排列
        """
        if player.has_flag:
            return [(Strategy.SCORING, 100.0)]  # 返回基地最高优先级
        
        if player.is_in_prison:
            return [(Strategy.SCORING, 0.0)]
        
        # 返回 营救 + 防守 + 抢旗 的优先级
        strategies = [Strategy.SAVING, Strategy.DEFENCE, Strategy.SCORING]
        scores = [(s, self.evaluate_strategy(player, s)) for s in strategies]
        scores.sort(key=lambda x: x[1], reverse=True)
        
        return scores
