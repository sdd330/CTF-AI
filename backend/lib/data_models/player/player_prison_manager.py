from typing import TYPE_CHECKING
from ..enums import PlayerState
from ..position import Position

if TYPE_CHECKING:
    from .player import Player


class PlayerPrisonManager:
    def __init__(self, player: 'Player'):
        self.player = player
    
    def send_to_prison(self, prison_position: Position) -> None:
        if self.player._state_manager.has_flag:
            caught_position = self.player.position
            self.player._flag_manager.drop_flag(drop_position=caught_position)
            print(
                f"🚩 [Player.{self.player.name}] 被抓，"
                f"旗帜保留在被抓位置: {caught_position}",
                flush=True
            )
        
        self.player._state_manager.set_prison_state(prison_position)
        self.player._behavior.record_capture()
    
    def rescue(self) -> None:
        if self.player._state_manager.is_in_prison:
            self.player._state_manager.set_free_state()
