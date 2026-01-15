"""
策略调度辅助函数
"""

from typing import Optional, Set, List, TYPE_CHECKING
from ..data_models import Strategy, Team

if TYPE_CHECKING:
    from ..data_models.player import Player
    from ..data_models.flag import Flag
    from ..game_engine import World


def find_best_opponent(player: 'Player', opponents: List['Player'],
                       assigned: Set[str], world: 'World', my_team: 'Team') -> Optional['Player']:
    """找到最佳防御目标（优先己方领地内的敌人）"""
    best = None
    min_dist = float('inf')

    # 先找己方领地内的敌人
    for opp in opponents:
        if opp.name in assigned:
            continue
        if world.map.is_in_team_territory(opp.position, my_team):
            dist = player.position.manhattan_distance(opp.position)
            if dist < min_dist:
                min_dist = dist
                best = opp

    # 没找到则找最近的敌人
    if best is None:
        for opp in opponents:
            if opp.name in assigned:
                continue
            dist = player.position.manhattan_distance(opp.position)
            if dist < min_dist:
                min_dist = dist
                best = opp

    return best


def find_best_flag(player: 'Player', flags: List['Flag'],
                   assigned: Set[tuple]) -> Optional['Flag']:
    """找到最近的未分配敌方旗帜"""
    best = None
    min_dist = float('inf')

    for flag in flags:
        pos_tuple = flag.position.to_tuple()
        if pos_tuple in assigned:
            continue
        dist = player.position.manhattan_distance(flag.position)
        if dist < min_dist:
            min_dist = dist
            best = flag

    return best


def get_scoring_target(player: 'Player', world: 'World', my_team: 'Team',
                       enemy_flags: List['Flag'], assigned_flags: Set[tuple]):
    """获取得分目标（有旗返回基地，无旗找旗）"""
    if player.has_flag:
        targets = list(world.map.get_team_target_positions(my_team))
        if targets:
            return targets[0].to_tuple(), None
    else:
        best_flag = find_best_flag(player, enemy_flags, assigned_flags)
        if best_flag:
            return best_flag.to_dict(), best_flag.position.to_tuple()
    return None, None


def create_schedule_entry(strategy: Strategy, player: 'Player', target):
    """创建调度表条目"""
    return (strategy, player.to_dict(), target)
