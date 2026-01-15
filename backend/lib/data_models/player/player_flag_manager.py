from typing import Optional, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from .player import Player
    from ..flag import Flag
    from ..position import Position


class PlayerFlagManager:
    def __init__(self, player: 'Player'):
        self.player = player
    
    def _get_carried_flag(self) -> Optional['Flag']:
        if not self.player._has_flag:
            return None
        
        is_my_player = False
        if self.player.name in self.player.world.my_players:
            is_my_player = True
        elif self.player.world.my_team_name and self.player.name.startswith(self.player.world.my_team_name):
            is_my_player = True
        elif self.player.world.my_players:
            first_my_player = next(iter(self.player.world.my_players.values()), None)
            if first_my_player and first_my_player.team == self.player.team:
                is_my_player = True
        elif not self.player.world.my_players and not self.player.world.enemy_players:
            if self.player.name and self.player.name[0] in ['L', 'R']:
                from ..enums import Team
                team_from_name = Team.from_name(self.player.name[0])
                if self.player.world.my_team_name:
                    is_my_player = (team_from_name.value == self.player.world.my_team_name)
                else:
                    is_my_player = (team_from_name == Team.LEFT)
        
        flags = self.player.world.enemy_flags if is_my_player else self.player.world.my_flags
        
        for flag in flags.values():
            if flag.carried_by == self.player:
                return flag
        return None
    
    def pick_up_flag(self, flag: 'Flag') -> None:
        if self.player._state_manager.is_free and not self.player._state_manager.has_flag:
            flag.pick_up_by(self.player)
    
    def drop_flag(self, drop_position: Optional['Position'] = None) -> Optional['Flag']:
        flag = self._get_carried_flag()
        if flag:
            from ..position import Position
            drop_pos = drop_position if drop_position is not None else self.player.position
            flag.drop_at(drop_pos)
            return flag
        return None
    
    def associate_flag_from_dict(self, flags: Dict[str, 'Flag']) -> bool:
        existing_flag = self._get_carried_flag()
        if existing_flag and existing_flag.is_picked_up:
            return True
        
        for flag in flags.values():
            if flag.is_picked_up and flag.carried_by == self.player:
                return True
        
        for flag in flags.values():
            if flag.is_picked_up:
                flag.carried_by = self.player
                flag.position = self.player.position
                return True
        
        return False
