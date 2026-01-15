"""
玩家策略执行类
负责执行各种策略
"""

from typing import Optional, List, TYPE_CHECKING
from ..enums import Strategy, Direction, Action
from ..position import Position
from ...utils import can_tag_enemy, can_rescue_teammate, can_pickup_flag
from ...utils.distance_calculator import DistanceCalculator

if TYPE_CHECKING:
    from .player import Player


class PlayerStrategyExecutor:
    """玩家策略执行器 - 负责执行各种策略"""

    def __init__(self, player: 'Player'):
        self.player = player

    def execute_saving_strategy(self) -> Optional[Direction]:
        teammates = [p for p in self.player.world.my_players.values() if p.is_in_prison]
        if not teammates:
            return None

        target = DistanceCalculator.find_closest_player(self.player.position, teammates)
        if not target:
            return None

        return self._move_to_target(target.position, target, can_rescue_teammate,
                                     Action.RESCUE_TEAMMATE, self.player._actions.execute_rescue_teammate)

    def execute_defence_strategy(self) -> Optional[Direction]:
        enemies = [p for p in self.player.world.enemy_players.values()
                   if not p.is_in_prison and
                   self.player.world.map.is_in_team_territory(p.position, self.player.team)]
        if not enemies:
            return None

        target = DistanceCalculator.find_closest_player(self.player.position, enemies)
        if not target:
            return None

        return self._move_to_target(target.position, target, can_tag_enemy,
                                     Action.TAG_ENEMY, self.player._actions.execute_tag_enemy)

    def execute_scoring_strategy(self) -> Optional[Direction]:
        enemy_flags = [f for f in self.player.world.enemy_flags.values() if f.can_pickup]
        if not enemy_flags:
            return None

        self._warn_flag_bug(enemy_flags)
        best_flag = self._find_best_flag(enemy_flags)
        if not best_flag:
            return None

        return self._move_to_target(best_flag.position, best_flag, can_pickup_flag,
                                     Action.PICKUP_FLAG, self.player._actions.execute_pickup_flag)

    def _move_to_target(self, target_pos: Position, target, can_act_func,
                        action_type: Action, execute_func) -> Optional[Direction]:
        """移动到目标位置，到达时执行动作"""
        path = self.player.world.find_path_to(self.player.position, target_pos,
                                               player_name=self.player.name)
        if not path or len(path) < 2:
            return None

        self.player.world._current_paths[self.player.name] = path

        if len(path) == 2 and can_act_func(self.player, target, *([self.player.world]
                                           if action_type in (Action.TAG_ENEMY, Action.RESCUE_TEAMMATE) else [])):
            if execute_func(target):
                self.player._behavior.stats.record_action(action_type)
            return Direction.STAY

        return self.player.position.direction_to(path[1])

    def _warn_flag_bug(self, enemy_flags: List) -> None:
        """警告旗帜归属错误"""
        if not hasattr(self.player.world, '_flag_bug_warned_players'):
            self.player.world._flag_bug_warned_players = set()

        bug_key = f"{self.player.team.value}_{self.player.name}"
        if bug_key in self.player.world._flag_bug_warned_players:
            return

        for flag in enemy_flags:
            if flag.belongs_to == self.player.team:
                print(f"🚨 [BUG] {self.player.name} 的敌方旗帜列表中包含了己方旗帜: {flag.flag_id}", flush=True)
                self.player.world._flag_bug_warned_players.add(bug_key)
                break

    def _find_best_flag(self, enemy_flags: List):
        """寻找最佳旗帜"""
        teammates = [p for p in self.player.world.my_players.values()
                     if not p.is_in_prison and not p.has_flag and p.name != self.player.name]
        targeted = self._get_targeted_flags(teammates, enemy_flags)

        # 调试日志
        prefix = f"{self.player.team.value}队"
        if targeted:
            print(f"🎯 [{prefix}] [Player.{self.player.name}] 发现队友已瞄准旗帜: {[str(p) for p in targeted]}", flush=True)

        untargeted = [f for f in enemy_flags if f.position not in targeted]
        flags_to_check = untargeted if untargeted else enemy_flags
        
        print(f"🎯 [{prefix}] [Player.{self.player.name}] 可选旗帜: 总共{len(enemy_flags)}个, 未被瞄准{len(untargeted)}个", flush=True)

        best_flag, best_score = None, float('-inf')
        for flag in flags_to_check:
            path = self.player.world.find_path_to(self.player.position, flag.position,
                                                   player_name=self.player.name)
            if not path or len(path) < 2:
                continue

            dist = self.player.position.manhattan_distance(flag.position)
            safety = self._evaluate_path_safety(path)
            penalty = -100.0 if flag.position in targeted else 0.0
            score = (100.0 / (1.0 + dist)) + safety * 20.0 + penalty

            if score > best_score:
                best_score, best_flag = score, flag
        
        if best_flag:
            print(f"✅ [{prefix}] [Player.{self.player.name}] 选择旗帜: {best_flag.position}, 得分: {best_score:.1f}", flush=True)
        return best_flag

    def _get_targeted_flags(self, teammates: List, flags: List) -> set:
        """获取队友已瞄准的旗帜位置"""
        targeted = set()
        prefix = f"{self.player.team.value}队"
        
        for t in teammates:
            path = self.player.world._current_paths.get(t.name, [])
            if path:
                for f in flags:
                    if f.position == path[-1]:
                        targeted.add(f.position)
                        print(f"🔍 [{prefix}] [Player.{self.player.name}] 检测到{t.name}正在追{f.position}", flush=True)
                        break
            # else:
            #     print(f"🔍 [{prefix}] [Player.{self.player.name}] {t.name}还没有路径", flush=True)
        
        return targeted

    def _evaluate_path_safety(self, path: List[Position]) -> float:
        """评估路径安全性"""
        if not path:
            return 0.0

        enemies = [p for p in self.player.world.enemy_players.values() if not p.is_in_prison]
        if not enemies:
            return 1.0

        check_len = min(len(path), 10)
        danger = sum(1 for pos in path[:check_len]
                     if any(pos.manhattan_distance(e.position) <= 2 for e in enemies))
        return max(0.0, 1.0 - danger / check_len)

    def return_to_base(self) -> Direction:
        from ...utils import can_score_flag
        prefix = f"{self.player.team.value}队"

        if self.player._state_manager.is_in_base():
            if self.player._state_manager.has_flag and can_score_flag(self.player):
                if self.player._actions.execute_score_flag():
                    self.player._behavior.stats.record_action(Action.SCORE_FLAG)
                    print(f"🎯 [{prefix}] [Player.{self.player.name}] 在基地内得分！", flush=True)
            return Direction.STAY

        if not self.player.base_area or not self.player.base_area.positions:
            print(f"⚠️  [{prefix}] [Player.{self.player.name}] 没有基地信息", flush=True)
            return Direction.STAY

        target = DistanceCalculator.find_closest_position(
            self.player.position, list(self.player.base_area.positions))
        if not target:
            return Direction.STAY

        path = self.player.world.find_path_to(self.player.position, target,
                                               player_name=self.player.name)
        if path and len(path) > 1:
            self.player.world._current_paths[self.player.name] = path
            direction = self.player.position.direction_to(path[1])
            print(f"🏠 [{prefix}] [Player.{self.player.name}] 返回基地: {self.player.position} → {target}", flush=True)
            return direction

        return Direction.STAY
