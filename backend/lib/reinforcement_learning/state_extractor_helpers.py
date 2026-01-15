"""
状态特征提取辅助函数
用于提取各类状态特征
"""

import numpy as np
from typing import TYPE_CHECKING, List, Tuple

if TYPE_CHECKING:
    from ..data_models.player import Player
    from ..data_models import Position, Team, Flag
    from ..game_engine import World


def normalize_position(x: float, y: float, width: int, height: int) -> Tuple[float, float]:
    """归一化位置到[0,1]范围"""
    norm_x = (x + 0.5) / max(width + 1, 1)
    norm_y = (y + 0.5) / max(height + 1, 1)
    return max(0.0, min(1.0, norm_x)), max(0.0, min(1.0, norm_y))


def normalize_distance(dist: float, max_dist: float) -> float:
    """归一化距离到[0,1]范围"""
    if max_dist <= 0:
        return 0.0
    return min(dist / max(max_dist, 1), 1.0)


def get_direction_encoding(dx: float, dy: float) -> List[float]:
    """获取方向的one-hot编码 [right, down, left, up]"""
    if dx == 0 and dy == 0:
        return [0.0, 0.0, 0.0, 0.0]
    if abs(dx) > abs(dy):
        return [1.0, 0.0, 0.0, 0.0] if dx > 0 else [0.0, 0.0, 1.0, 0.0]
    return [0.0, 1.0, 0.0, 0.0] if dy > 0 else [0.0, 0.0, 0.0, 1.0]


def extract_player_features(player: 'Player', world: 'World') -> List[float]:
    """提取玩家自身信息 (5维)"""
    pos_x, pos_y = normalize_position(
        player.position.x, player.position.y,
        world.map.width, world.map.height
    )
    has_flag = 1.0 if player.has_flag else 0.0
    in_prison = 1.0 if player.is_in_prison else 0.0
    in_enemy = 1.0 if world.map.is_in_enemy_territory(player.position, player.team) else 0.0
    return [pos_x, pos_y, has_flag, in_prison, in_enemy]


def extract_target_features(player: 'Player', world: 'World', my_team: 'Team') -> List[float]:
    """提取目标信息 (6维: 1距离 + 4方向 + 1flag_dist)"""
    enemy_flags = [f for f in world.enemy_flags.values() if f.can_pickup]
    my_targets = list(world.map.get_team_target_positions(my_team))
    max_dist = world.map.width + world.map.height

    if enemy_flags:
        min_dist = float('inf')
        nearest_pos = None
        for flag in enemy_flags:
            dist = player.position.manhattan_distance(flag.position)
            if dist < min_dist:
                min_dist = dist
                nearest_pos = flag.position.to_tuple()

        flag_dist = normalize_distance(min_dist, max_dist)
        if nearest_pos:
            dx = nearest_pos[0] - player.position.x
            dy = nearest_pos[1] - player.position.y
            flag_dir = get_direction_encoding(dx, dy)
        else:
            flag_dir = [0.0, 0.0, 0.0, 0.0]
    else:
        flag_dist = 1.0
        flag_dir = [0.0, 0.0, 0.0, 0.0]

    # 如果玩家有flag，计算到目标区域的距离
    if player.has_flag and my_targets:
        target = my_targets[0]
        to_target_dist = player.position.manhattan_distance(target)
        to_target_dist = normalize_distance(to_target_dist, max_dist)
    else:
        to_target_dist = 0.0

    return [flag_dist] + flag_dir + [to_target_dist]


def extract_opponent_features(player: 'Player', world: 'World', my_team: 'Team') -> List[float]:
    """提取对手信息 (4维)"""
    opponents = [p for p in world.enemy_players.values() if not p.is_in_prison]
    my_flags = list(world.my_flags.values())
    max_dist = world.map.width + world.map.height

    if opponents:
        min_dist = float('inf')
        nearest = None
        for opp in opponents:
            dist = player.position.manhattan_distance(opp.position)
            if dist < min_dist:
                min_dist = dist
                nearest = opp

        enemy_dist = normalize_distance(min_dist, max_dist)
        enemy_danger = _calc_enemy_danger(nearest, my_flags, my_team, world) if nearest else 0.0
        enemy_has_flag = 1.0 if any(opp.has_flag for opp in opponents) else 0.0
    else:
        enemy_dist = 1.0
        enemy_danger = 0.0
        enemy_has_flag = 0.0

    enemies_in_prison = [p for p in world.enemy_players.values() if p.is_in_prison]
    enemy_in_prison = 1.0 if enemies_in_prison else 0.0

    return [enemy_dist, enemy_danger, enemy_has_flag, enemy_in_prison]


def _calc_enemy_danger(enemy: 'Player', my_flags: List['Flag'], my_team: 'Team', world: 'World') -> float:
    """计算敌人危险度"""
    if not my_flags:
        return 0.0
    min_dist = min(enemy.position.manhattan_distance(f.position) for f in my_flags)
    in_my_territory = world.map.is_in_team_territory(enemy.position, my_team)
    danger_base = 1.0 / (min_dist + 1.0)
    multiplier = 2.0 if in_my_territory else 1.0
    return min(danger_base * multiplier / 2.0, 1.0)
