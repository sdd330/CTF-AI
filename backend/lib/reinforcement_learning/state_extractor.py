"""
状态特征提取模块
用于从游戏状态中提取强化学习所需的状态特征向量
"""

import numpy as np
from typing import TYPE_CHECKING, List

from ..data_models import Team
from .state_extractor_helpers import (
    extract_player_features,
    extract_target_features,
    extract_opponent_features,
)

if TYPE_CHECKING:
    from ..data_models.player import Player
    from ..game_engine import World


STATE_DIM = 19  # 5(玩家) + 6(目标) + 4(对手) + 4(全局)


def extract_state_features(player: 'Player', world: 'World') -> np.ndarray:
    """
    提取玩家的状态特征向量

    Args:
        player: Player对象
        world: World对象

    Returns:
        numpy array: 状态特征向量（19维）
    """
    my_team = Team.LEFT if world.my_team_name == "L" else Team.RIGHT
    opponent_team = Team.RIGHT if my_team == Team.LEFT else Team.LEFT

    features: List[float] = []

    # 玩家自身信息 (5维)
    features.extend(extract_player_features(player, world))

    # 目标信息 (6维)
    features.extend(extract_target_features(player, world, my_team))

    # 对手信息 (4维)
    features.extend(extract_opponent_features(player, world, my_team))

    # 全局信息 (4维)
    features.extend(_extract_global_features(world, my_team, opponent_team))

    return _validate_features(features, player)


def _extract_global_features(world: 'World', my_team: 'Team', opponent_team: 'Team') -> List[float]:
    """提取全局信息 (4维)"""
    my_flags = list(world.my_flags.values())
    enemy_flags = list(world.enemy_flags.values())

    # flag数量（归一化，假设最多3个flag）
    my_flags_count = min(len(my_flags) / 3.0, 1.0) if my_flags else 0.0
    enemy_flags_count = min(len(enemy_flags) / 3.0, 1.0) if enemy_flags else 0.0

    # 得分（从flag位置推断）
    my_targets = world.map.get_team_target_positions(my_team)
    enemy_targets = world.map.get_team_target_positions(opponent_team)

    my_score = sum(1.0 for f in my_flags if f.position in my_targets)
    enemy_score = sum(1.0 for f in enemy_flags if f.position in enemy_targets)

    # 归一化得分（假设最多3分）
    my_score = min(my_score / 3.0, 1.0)
    enemy_score = min(enemy_score / 3.0, 1.0)

    return [my_flags_count, enemy_flags_count, my_score, enemy_score]


def _validate_features(features: List[float], player: 'Player') -> np.ndarray:
    """验证并修复特征向量维度"""
    feature_array = np.array(features, dtype=np.float32)

    if len(feature_array) != STATE_DIM:
        print(f"⚠️  警告：状态特征向量维度不匹配！")
        print(f"   玩家: {player.name}, 在prison: {player.is_in_prison}")
        print(f"   期望维度: {STATE_DIM}, 实际维度: {len(feature_array)}")

        if len(feature_array) < STATE_DIM:
            feature_array = np.pad(feature_array, (0, STATE_DIM - len(feature_array)), 'constant')
        else:
            feature_array = feature_array[:STATE_DIM]
        print(f"   已修复为: {len(feature_array)}维")

    return feature_array
