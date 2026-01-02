"""
玩家队伍关系类
负责管理玩家与队伍的关系判断
"""

from typing import List, Optional, TYPE_CHECKING
from ..enums import Team
from ..position import Position

if TYPE_CHECKING:
    from .player import Player
    from ..flag import Flag


class PlayerTeamRelations:
    """玩家队伍关系管理器 - 负责管理玩家与队伍的关系判断"""
    
    def __init__(self, player: 'Player'):
        self.player = player
    
    def belongs_to_team(self, team: Team) -> bool:
        """检查玩家是否属于指定队伍"""
        return self.player.team == team
    
    def is_enemy_of(self, other_player: 'Player') -> bool:
        """检查是否是另一个玩家的敌人"""
        return self.player.team != other_player.team
    
    def is_teammate_of(self, other_player: 'Player') -> bool:
        """检查是否是另一个玩家的队友"""
        return self.player.team == other_player.team
    
    def is_enemy_team(self, team: Team) -> bool:
        """检查是否是指定队伍的敌人"""
        return self.player.team != team
    
    def is_my_team(self, team: Team) -> bool:
        """检查是否是指定队伍的己方"""
        return self.player.team == team
    
    def find_closest_opponent(self, opponents: List['Player']) -> Optional['Player']:
        """找到最近的敌人"""
        enemy_opponents = [opp for opp in opponents if self.is_enemy_of(opp)]
        if not enemy_opponents:
            return None
        return min(
            enemy_opponents,
            key=lambda opp: self.player.position.manhattan_distance(opp.position),
            default=None
        )
    
    def find_closest_flag(self, flags: List['Flag']) -> Optional['Flag']:
        """找到最近的旗帜"""
        if not flags:
            return None
        return min(
            flags,
            key=lambda flag: self.player.position.manhattan_distance(flag.position),
            default=None
        )
