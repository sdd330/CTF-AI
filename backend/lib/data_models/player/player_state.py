from typing import Optional, TYPE_CHECKING
from ..enums import Team, PlayerState
from ..position import Position
from ..areas import TargetArea

if TYPE_CHECKING:
    from .player import Player


class PlayerStateManager:
    def __init__(self, player: 'Player'):
        self.player = player
    
    @property
    def is_free(self) -> bool:
        return not self.player._in_prison
    
    @property
    def is_in_prison(self) -> bool:
        return self.player._in_prison
    
    @property
    def has_flag(self) -> bool:
        return self.player._has_flag
    
    def set_prison_state(self, prison_position: Position) -> None:
        self.player._in_prison = True
        self.player.state = PlayerState.IN_PRISON
        self.player.position = prison_position
    
    def set_free_state(self) -> None:
        self.player._in_prison = False
        self.player.state = PlayerState.FREE
    
    def set_carrying_flag_state(self) -> None:
        self.player.state = PlayerState.CARRYING_FLAG
    
    def set_base_area(self, base_area: TargetArea) -> None:
        if base_area and not base_area.belongs_to_team(self.player.team):
            raise ValueError(
                f"玩家 {self.player.name} ({self.player.team.value}队) "
                f"不能设置 {base_area.belongs_to.value}队的基地"
            )
        self.player.base_area = base_area
    
    def is_in_base(self) -> bool:
        if not self.player.base_area:
            return False
        return self.player.base_area.contains(self.player.position)
