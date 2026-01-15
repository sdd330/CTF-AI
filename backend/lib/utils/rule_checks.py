"""
游戏规则检查工具函数
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..data_models import Team, Player, Flag
    from ..game_engine import World


def can_tag_enemy(tagger: 'Player', target: 'Player', world: 'World') -> bool:
    """
    检查是否可以标记敌方玩家

    Args:
        tagger: 标记者
        target: 目标玩家
        world: World对象
    Returns:
        是否可以标记
    """
    if not tagger.is_enemy_of(target):
        return False
    if tagger.position != target.position:
        return False

    is_tagger_in = world.map.is_in_team_territory(tagger.position, tagger.team)
    is_target_in = world.map.is_in_team_territory(target.position, tagger.team)
    if not (is_tagger_in and is_target_in):
        return False

    if not tagger.is_free or not target.is_free:
        return False

    return True


def can_rescue_teammate(rescuer: 'Player', teammate: 'Player', world: 'World') -> bool:
    """
    检查是否可以救援队友

    Args:
        rescuer: 救援者
        teammate: 队友
        world: 游戏世界对象
    Returns:
        是否可以救援
    """
    if not rescuer.is_teammate_of(teammate):
        return False
    if rescuer.position != teammate.position:
        return False

    enemy_team = rescuer.team.get_enemy()
    enemy_prison = world.map.get_team_prison_area(enemy_team)
    if not enemy_prison or rescuer.position not in enemy_prison.positions:
        return False

    if not rescuer.is_free:
        return False

    return True


def can_pickup_flag(player: 'Player', flag: 'Flag') -> bool:
    """
    检查是否可以拾取旗帜

    Args:
        player: 玩家
        flag: 旗帜
    Returns:
        是否可以拾取
    """
    if not player.is_free or player.has_flag:
        return False
    if player.position != flag.position:
        return False
    if not flag.can_pickup:
        return False
    if flag.belongs_to == player.team:
        return False

    return True


def can_score_flag(player: 'Player') -> bool:
    """
    检查是否可以得分

    Args:
        player: 玩家
    Returns:
        是否可以得分
    """
    from ..data_models import Team

    if not player.has_flag:
        return False

    flag = player._flag_manager._get_carried_flag()
    if flag:
        expected_enemy = Team.RIGHT if player.team == Team.LEFT else Team.LEFT
        if flag.belongs_to != expected_enemy:
            return False

    return player.is_in_base()
