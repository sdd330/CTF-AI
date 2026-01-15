"""
游戏查询工具模块
提供玩家和旗帜查询相关的工具函数
"""

from typing import Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..data_models import Team, Player, Flag


def list_players(players: Dict[str, 'Player'], team: 'Team',
                 in_prison: Optional[bool] = None,
                 has_flag: Optional[bool] = None) -> List['Player']:
    """
    获取队伍玩家列表

    Args:
        players: 玩家字典
        team: 队伍
        in_prison: 是否在监狱中（None表示不筛选）
        has_flag: 是否持有旗帜（None表示不筛选）
    Returns:
        玩家列表
    """
    result = [p for p in players.values() if p.belongs_to_team(team)]

    if in_prison is not None:
        result = [p for p in result if p.is_in_prison == in_prison]
    if has_flag is not None:
        result = [p for p in result if p.has_flag == has_flag]

    return result


def list_flags(flags: Dict[str, 'Flag'], team: 'Team',
               is_enemy: Optional[bool] = None,
               can_pickup: Optional[bool] = None) -> List['Flag']:
    """
    获取旗帜列表

    Args:
        flags: 旗帜字典
        team: 队伍（用于判断敌方/己方）
        is_enemy: 是否敌方旗帜（None表示不筛选，True表示敌方，False表示己方）
        can_pickup: 是否可以拾取（None表示不筛选）
    Returns:
        旗帜列表
    """
    result = []
    for f in flags.values():
        if is_enemy is None:
            result.append(f)
        elif is_enemy:
            if f.belongs_to != team:
                result.append(f)
        else:
            if f.belongs_to == team:
                result.append(f)

    if can_pickup is not None:
        result = [f for f in result if f.can_pickup == can_pickup]

    return result


# Re-export rule check functions for backwards compatibility
from .rule_checks import can_tag_enemy, can_rescue_teammate, can_pickup_flag, can_score_flag

__all__ = [
    'list_players',
    'list_flags',
    'can_tag_enemy',
    'can_rescue_teammate',
    'can_pickup_flag',
    'can_score_flag',
]
