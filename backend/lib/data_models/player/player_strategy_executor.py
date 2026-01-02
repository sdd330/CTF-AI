"""
玩家策略执行类
负责执行各种策略
"""

from typing import Optional, List, TYPE_CHECKING
from ..enums import Strategy, Direction, Action
from ..position import Position
from ...utils import list_players, list_flags, can_tag_enemy, can_rescue_teammate, can_pickup_flag
from ...utils.distance_calculator import DistanceCalculator

if TYPE_CHECKING:
    from .player import Player


class PlayerStrategyExecutor:
    """玩家策略执行器 - 负责执行各种策略"""
    
    def __init__(self, player: 'Player'):
        self.player = player
    
    def execute_saving_strategy(self) -> Optional[Direction]:
        """执行营救策略"""
        # 找到在监狱中的队友
        teammates_in_prison = list_players(
            self.player.world.players,
            self.player.team,
            in_prison=True,
            has_flag=None
        )
        if not teammates_in_prison:
            return None
        
        # 找到最近的队友
        nearest_teammate = DistanceCalculator.find_closest_player(
            self.player.position,
            teammates_in_prison
        )
        if not nearest_teammate:
            return None
        
        # 移动到队友位置
        path = self.player.world.find_path_to(
            self.player.position,
            nearest_teammate.position,
            player_name=self.player.name
        )
        if path and len(path) > 1:
            self.player.world._current_paths[self.player.name] = path
            if len(path) == 2 and can_rescue_teammate(
                self.player, nearest_teammate, self.player.world
            ):
                if self.player._actions.execute_rescue_teammate(nearest_teammate):
                    self.player._behavior.stats.record_action(Action.RESCUE_TEAMMATE)
                return Direction.STAY
            return self.player.position.direction_to(path[1])
        
        return None
    
    def execute_defence_strategy(self) -> Optional[Direction]:
        """执行防守策略"""
        enemy_team = self.player.team.get_enemy()
        enemies = list_players(
            self.player.world.players,
            enemy_team,
            in_prison=False,
            has_flag=None
        )
        
        # 找到在己方领地内的敌人
        enemies_in_territory = [
            e for e in enemies
            if self.player.world.is_in_team_territory(e.position, self.player.team)
        ]
        if not enemies_in_territory:
            return None
        
        # 找到最近的敌人
        nearest_enemy = DistanceCalculator.find_closest_player(
            self.player.position,
            enemies_in_territory
        )
        if not nearest_enemy:
            return None
        
        # 移动到敌人位置
        path = self.player.world.find_path_to(
            self.player.position,
            nearest_enemy.position,
            player_name=self.player.name
        )
        if path and len(path) > 1:
            self.player.world._current_paths[self.player.name] = path
            if len(path) == 2 and can_tag_enemy(
                self.player, nearest_enemy, self.player.world
            ):
                if self.player._actions.execute_tag_enemy(nearest_enemy):
                    self.player._behavior.stats.record_action(Action.TAG_ENEMY)
                return Direction.STAY
            return self.player.position.direction_to(path[1])
        
        return None
    
    def execute_scoring_strategy(self) -> Optional[Direction]:
        """执行抢旗策略（考虑路径安全性、团队协作和避免多人抢同一面旗）"""
        # 找到可拾取的敌方旗帜
        enemy_flags = list_flags(
            self.player.world.flags,
            self.player.team,
            is_enemy=True,
            can_pickup=True
        )
        if not enemy_flags:
            return None
        
        # 检查其他队友的目标旗帜（通过检查他们的路径终点）
        teammates = list_players(
            self.player.world.players,
            self.player.team,
            in_prison=False,
            has_flag=False
        )
        flags_targeted_by_teammates = set()
        for teammate in teammates:
            if teammate.name != self.player.name:
                # 检查队友的路径目标
                teammate_path = self.player.world._current_paths.get(teammate.name, [])
                if teammate_path and len(teammate_path) > 0:
                    teammate_target = teammate_path[-1]  # 路径的终点
                    # 检查这个目标是否是某面旗帜的位置
                    for flag in enemy_flags:
                        if flag.position == teammate_target:
                            flags_targeted_by_teammates.add(flag.position)
                            break
        
        # 选择最佳旗帜（考虑距离、路径安全性和是否被队友盯上）
        # 优先选择没有被队友盯上的旗帜
        best_flag = None
        best_score = float('-inf')
        
        # 先尝试找没有被队友盯上的旗帜
        untargeted_flags = [f for f in enemy_flags if f.position not in flags_targeted_by_teammates]
        flags_to_consider = untargeted_flags if untargeted_flags else enemy_flags  # 如果所有旗帜都被盯上，才考虑被盯上的
        
        for flag in flags_to_consider:
            # 如果这面旗帜已经被队友盯上，大幅降低分数（但不要完全排除，以防队友失败）
            is_targeted = flag.position in flags_targeted_by_teammates
            teammate_penalty = -100.0 if is_targeted else 0.0  # 增加惩罚力度
            
            dist = self.player.position.manhattan_distance(flag.position)
            path = self.player.world.find_path_to(
                self.player.position,
                flag.position,
                player_name=self.player.name
            )
            if not path or len(path) < 2:
                continue
            
            safety_score = self._evaluate_path_safety(path)
            # 基础分数：距离越近分数越高，路径越安全分数越高
            # 如果被队友盯上，大幅降低分数
            score = (100.0 / (1.0 + dist)) + safety_score * 20.0 + teammate_penalty
            
            if score > best_score:
                best_score = score
                best_flag = flag
        
        if not best_flag:
            return None
        
        # 移动到最佳旗帜位置
        path = self.player.world.find_path_to(
            self.player.position,
            best_flag.position,
            player_name=self.player.name
        )
        if path and len(path) > 1:
            self.player.world._current_paths[self.player.name] = path
            if len(path) == 2 and can_pickup_flag(self.player, best_flag):
                if self.player._actions.execute_pickup_flag(best_flag):
                    self.player._behavior.stats.record_action(Action.PICKUP_FLAG)
                return Direction.STAY
            return self.player.position.direction_to(path[1])
        
        return None
    
    def _evaluate_path_safety(self, path: List[Position]) -> float:
        """评估路径的安全性"""
        if not path or len(path) == 0:
            return 0.0
        
        enemy_team = self.player.team.get_enemy()
        enemies = list_players(
            self.player.world.players,
            enemy_team,
            in_prison=False,
            has_flag=None
        )
        
        if not enemies:
            return 1.0
        
        check_length = min(len(path), 10)
        danger_count = 0
        
        for pos in path[:check_length]:
            for enemy in enemies:
                if pos.manhattan_distance(enemy.position) <= 2:
                    danger_count += 1
                    break
        
        safety_ratio = 1.0 - (danger_count / check_length)
        return max(0.0, safety_ratio)
    
    def return_to_base(self) -> Direction:
        """玩家持有旗帜时，立即返回基地"""
        from ...utils import can_score_flag
        
        # 检查是否已在基地内
        if self.player._state_manager.is_in_base():
            if self.player._state_manager.has_flag and can_score_flag(self.player):
                if self.player._actions.execute_score_flag():
                    self.player._behavior.stats.record_action(Action.SCORE_FLAG)
            return Direction.STAY
        
        # 使用玩家对象上的基地区域
        if not self.player.base_area or not self.player.base_area.positions:
            return Direction.STAY
        
        # 找到最近的基地位置
        base_positions = list(self.player.base_area.positions)
        target_base_pos = DistanceCalculator.find_closest_position(
            self.player.position,
            base_positions
        )
        
        if target_base_pos:
            path = self.player.world.find_path_to(
                self.player.position,
                target_base_pos,
                player_name=self.player.name
            )
            if path and len(path) > 1:
                self.player.world._current_paths[self.player.name] = path
                return self.player.position.direction_to(path[1])
        
        return Direction.STAY
