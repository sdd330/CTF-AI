"""Player serialization - dict conversion and status methods"""

from typing import Dict, TYPE_CHECKING
from ..enums import PlayerState
from ..position import Position
from ..status import PlayerStatus

if TYPE_CHECKING:
    from .player import Player
    from ..flag import Flag


class PlayerSerializer:
    """Handles player data serialization and deserialization."""

    def __init__(self, player: 'Player'):
        self.player = player

    def update_from_dict(self, p_data: Dict, flags: Dict[str, 'Flag']) -> None:
        """Update player state from dictionary data."""
        p = self.player
        p.position = Position(p_data["posX"], p_data["posY"])
        old_has_flag = p._has_flag
        p._in_prison = p_data.get("inPrison", False)
        p.prison_time_left = p_data.get("inPrisonTimeLeft", 0)
        p.prison_duration = p_data.get("inPrisonDuration", 20000)
        p._has_flag = p_data.get("hasFlag", False)

        if p._has_flag and not old_has_flag:
            p._flag_manager.associate_flag_from_dict(flags)

        if p._in_prison:
            p.state = PlayerState.IN_PRISON
        elif p._has_flag:
            p.state = PlayerState.CARRYING_FLAG
        else:
            p.state = PlayerState.FREE

    def get_status(self) -> PlayerStatus:
        """Get player status matching frontend PlayerStatus interface."""
        p = self.player
        return PlayerStatus(
            name=p.name,
            team=p.team.value,
            posX=p.position.x,
            posY=p.position.y,
            hasFlag=p.has_flag,
            inPrison=p.is_in_prison,
            inPrisonTimeLeft=p.prison_time_left,
            inPrisonDuration=p.prison_duration,
        )

    def to_dict(self) -> Dict:
        """Convert player to dictionary."""
        p = self.player
        return {
            "name": p.name, "team": p.team.value,
            "posX": p.position.x, "posY": p.position.y,
            "hasFlag": p.has_flag, "inPrison": p.is_in_prison,
            "inPrisonTimeLeft": p.prison_time_left,
            "inPrisonDuration": p.prison_duration
        }
