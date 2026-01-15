"""
奖励计算模块
用于计算强化学习中的奖励信号

奖励设计（聚焦基地插旗得分，兼顾稳定性）：
- 步惩罚: -0.02
- 拾旗奖励: +10.0
- 得分奖励: +150.0
- 持有旗帜时接近基地: +3.0~+25.0
- 进入基地区域（持有旗帜）: +40.0
- 失去旗帜惩罚: -40.0
- 被捕获惩罚: -25.0
"""

from typing import Optional, TYPE_CHECKING
from ..data_models import Position, Team, Strategy

if TYPE_CHECKING:
    from ..data_models.player import Player
    from ..game_engine import World


def calculate_reward(player: 'Player', world: 'World',
                     prev_state_dict: Optional[dict] = None,
                     current_action: Optional[int] = None) -> float:
    """计算奖励"""
    if prev_state_dict is None:
        return -0.02

    reward = -0.02
    reward += _calc_event_rewards(player, world, prev_state_dict)

    if current_action is not None:
        reward += _calc_action_rewards(player, world, current_action)
    elif not player.has_flag:
        reward += _calc_distance_reward_to_flag(player, world)

    if player.has_flag:
        reward += _calc_flag_holder_reward(player, world)

    return max(min(reward, 200.0), -50.0)


def _calc_event_rewards(player: 'Player', world: 'World', prev_state: dict) -> float:
    """计算事件奖励"""
    reward = 0.0
    prev_flag = prev_state.get("hasFlag", False)
    prev_prison = prev_state.get("inPrison", False)

    if player.has_flag and not prev_flag:
        reward += 10.0
    if not player.has_flag and prev_flag:
        reward -= 40.0
    if player.is_in_prison and not prev_prison:
        reward -= 25.0

    my_team = Team.LEFT if world.my_team_name == "L" else Team.RIGHT
    prev_score = prev_state.get("team_score")
    current_score = world.left_team_score if my_team == Team.LEFT else world.right_team_score

    if prev_score is not None and current_score > prev_score:
        reward += 150.0
        print(f"[Reward] 🎉 得分奖励！{my_team.value}队得分: {prev_score} -> {current_score}")

    if prev_flag:
        reward += _check_base_entry(player, world, prev_state, my_team)

    return reward


def _check_base_entry(player: 'Player', world: 'World', prev_state: dict, my_team: Team) -> float:
    """检查是否进入基地区域"""
    prev_pos = Position(prev_state["posX"], prev_state["posY"])
    targets = world.map.get_team_target_positions(my_team)
    if player.position in targets and prev_pos not in targets:
        print(f"[Reward] 🏁 进入基地区域（持有旗帜）！奖励: +40.0")
        return 40.0
    return 0.0


def _calc_action_rewards(player: 'Player', world: 'World', action: int) -> float:
    """计算基于动作的奖励"""
    my_team = Team.LEFT if world.my_team_name == "L" else Team.RIGHT

    if action == Strategy.DEFENCE.value:
        return _calc_defence_reward(player, world, my_team)
    elif action == Strategy.SCORING.value:
        return _calc_scoring_reward(player, world, my_team)
    elif action == Strategy.SAVING.value:
        return _calc_saving_reward(player, world, my_team)
    return 0.0


def _calc_defence_reward(player: 'Player', world: 'World', my_team: Team) -> float:
    """计算防御奖励"""
    enemies = [p for p in world.enemy_players.values()
               if not p.is_in_prison and world.map.is_in_team_territory(p.position, my_team)]
    if not enemies:
        return 0.0
    reward = 3.0
    if any(e.has_flag for e in enemies):
        reward += 10.0
    return reward


def _calc_scoring_reward(player: 'Player', world: 'World', my_team: Team) -> float:
    """计算抢旗奖励"""
    pos = player.position
    if not player.has_flag:
        return _calc_approach_flag_reward(pos, world)
    return _calc_approach_base_reward(pos, world, my_team)


def _calc_approach_flag_reward(pos: Position, world: 'World') -> float:
    """计算接近旗帜的奖励"""
    flags = [f for f in world.enemy_flags.values() if f.can_pickup]
    if not flags:
        return 0.0
    min_dist = min(pos.manhattan_distance(f.position) for f in flags)
    reward_map = {1: 2.0, 2: 1.5, 3: 0.7, 5: 0.3}
    reward = next((v for d, v in sorted(reward_map.items()) if min_dist <= d), 0.0)
    return reward + 0.05 / (1.0 + min_dist)


def _calc_approach_base_reward(pos: Position, world: 'World', my_team: Team) -> float:
    """计算持旗时接近基地的奖励"""
    targets = list(world.map.get_team_target_positions(my_team))
    if not targets:
        return 0.0
    min_dist = min(pos.manhattan_distance(t) for t in targets)
    reward_map = {1: 25.0, 2: 18.0, 3: 10.0, 5: 3.0}
    reward = next((v for d, v in sorted(reward_map.items()) if min_dist <= d), 0.0)
    return reward + 0.8 / (1.0 + min_dist)


def _calc_saving_reward(player: 'Player', world: 'World', my_team: Team) -> float:
    """计算营救奖励"""
    in_prison = [p for p in world.my_players.values() if p.is_in_prison]
    if not in_prison:
        return 0.0
    active = len([p for p in world.my_players.values() if not p.is_in_prison])
    reward = {1: 6.0, 2: 3.0}.get(active, 1.0)

    enemy_prison = world.map.get_team_prison_area(my_team.get_enemy())
    if enemy_prison:
        min_dist = min(player.position.manhattan_distance(p) for p in enemy_prison.positions)
        if min_dist <= 2:
            reward += 1.0
    return reward


def _calc_distance_reward_to_flag(player: 'Player', world: 'World') -> float:
    """计算到旗帜距离的连续奖励"""
    flags = [f for f in world.enemy_flags.values() if f.can_pickup]
    if not flags:
        return 0.0
    min_dist = min(player.position.manhattan_distance(f.position) for f in flags)
    return 0.05 / (1.0 + min_dist)


def _calc_flag_holder_reward(player: 'Player', world: 'World') -> float:
    """计算持有旗帜时的连续奖励"""
    my_team = Team.LEFT if world.my_team_name == "L" else Team.RIGHT
    targets = list(world.map.get_team_target_positions(my_team))
    if not targets:
        return 0.0
    min_dist = min(player.position.manhattan_distance(t) for t in targets)
    return 0.5 / (1.0 + min_dist) if min_dist <= 10 else 0.0
