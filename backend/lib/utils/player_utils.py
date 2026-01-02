"""
游戏查询工具模块
提供玩家和旗帜查询相关的工具函数，以及游戏规则检查函数
"""

from typing import Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..data_models import Team, Player, Flag
    from ..map_service import GameMap
else:
    Team = None
    Player = None
    Flag = None
    GameMap = None


def list_players(players: Dict[str, Player], team: Team, 
                 in_prison: Optional[bool] = None,
                 has_flag: Optional[bool] = None) -> List[Player]:
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
    from ..data_models import Team, Flag
    
    result = []
    for f in flags.values():
        if is_enemy is None:
            # 不筛选，返回所有旗帜
            result.append(f)
        elif is_enemy:
            # 敌方旗帜
            if f.is_enemy_flag_for(team):
                result.append(f)
        else:
            # 己方旗帜
            if f.belongs_to_team(team):
                result.append(f)
    
    if can_pickup is not None:
        result = [f for f in result if f.can_pickup == can_pickup]
    
    return result


# ========== 游戏规则检查工具函数 ==========

def can_tag_enemy(tagger: 'Player', target: 'Player', world: 'World') -> bool:
    from ..data_models import Player
    if TYPE_CHECKING:
        from ..game_engine import World
    """
    检查是否可以标记敌方玩家
    
    Args:
        tagger: 标记者
        target: 目标玩家
        world: World对象
    Returns:
        是否可以标记
    """
    # 检查是否是敌方
    if not tagger.is_enemy_of(target):
        return False
    
    # 检查是否在同一位置
    if tagger.position != target.position:
        return False
    
    # 检查是否都在己方领地内
    is_tagger_in_territory = world.is_in_team_territory(tagger.position, tagger.team)
    is_target_in_territory = world.is_in_team_territory(target.position, tagger.team)
    if not (is_tagger_in_territory and is_target_in_territory):
        return False
    
    # 检查玩家状态
    if not tagger.is_free or not target.is_free:
        return False
    
    return True


def can_rescue_teammate(rescuer: 'Player', teammate: 'Player', game_map: 'GameMap') -> bool:
    from ..data_models import Player
    from ..map_service import GameMap
    """
    检查是否可以救援队友
    
    Args:
        rescuer: 救援者
        teammate: 队友
        game_map: 游戏地图
    Returns:
        是否可以救援
    """
    # 检查是否是队友
    if not rescuer.is_teammate_of(teammate):
        return False
    
    # 检查是否在同一位置
    if rescuer.position != teammate.position:
        return False
    
    # 检查救援者是否在敌方监狱内
    enemy_team = rescuer.team.get_enemy()
    enemy_prison_area = game_map.get_team_prison_area(enemy_team)
    if not enemy_prison_area or rescuer.position not in enemy_prison_area.positions:
        return False
    
    # 检查救援者状态
    if not rescuer.is_free:
        return False
    
    return True


def can_pickup_flag(player: 'Player', flag: 'Flag') -> bool:
    from ..data_models import Player, Flag
    """
    检查是否可以拾取旗帜
    
    Args:
        player: 玩家
        flag: 旗帜
    Returns:
        是否可以拾取
    """
    # 检查玩家状态
    if not player.is_free or player.has_flag:
        return False
    
    # 检查是否在旗帜位置
    if player.position != flag.position:
        return False
    
    # 检查旗帜是否可拾取且是敌方旗帜
    if not flag.can_pickup:
        return False
    
    if not flag.is_enemy_flag_for(player.team):
        return False
    
    return True


def can_score_flag(player: 'Player') -> bool:
    from ..data_models import Player, Team
    """
    检查是否可以得分
    
    Args:
        player: 玩家
    Returns:
        是否可以得分
    """
    # 检查是否持有旗帜
    if not player.has_flag:
        return False
    
    # 验证旗帜归属
    if player.carried_flag:
        flag = player.carried_flag
        expected_enemy = Team.RIGHT if player.team == Team.LEFT else Team.LEFT
        if flag.belongs_to != expected_enemy:
            return False
        if not flag.is_enemy_flag_for(player.team):
            return False
    
    # 检查是否在己方基地内（使用玩家对象自己的方法）
    return player.is_in_base()
