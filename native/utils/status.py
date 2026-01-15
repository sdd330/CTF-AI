"""
Status dataclasses for API serialization.
These match the frontend TypeScript interfaces (PlayerStatus, FlagStatus).
"""

from dataclasses import dataclass
from typing import Literal


TeamValue = Literal["L", "R"]


@dataclass(frozen=True)
class PlayerStatus:
    """
    Player status for WebSocket communication.
    Matches frontend PlayerStatus interface.
    """
    name: str
    team: TeamValue
    posX: int
    posY: int
    hasFlag: bool
    inPrison: bool
    inPrisonTimeLeft: int
    inPrisonDuration: int

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "team": self.team,
            "posX": self.posX,
            "posY": self.posY,
            "hasFlag": self.hasFlag,
            "inPrison": self.inPrison,
            "inPrisonTimeLeft": self.inPrisonTimeLeft,
            "inPrisonDuration": self.inPrisonDuration,
        }


@dataclass(frozen=True)
class FlagStatus:
    """
    Flag status for WebSocket communication.
    Matches frontend FlagStatus interface.
    """
    canPickup: bool
    posX: int
    posY: int

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "canPickup": self.canPickup,
            "posX": self.posX,
            "posY": self.posY,
        }
