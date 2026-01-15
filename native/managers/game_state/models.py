"""
Game state data models.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List

from .enums import GameFlowState, GameFlowSubState
from ...utils import Team


@dataclass
class Position:
    """Position data."""
    x: int
    y: int


@dataclass
class PlayerPosition:
    """Player position data."""
    name: str
    x: int
    y: int


@dataclass
class TeamState:
    """Team state."""
    score: int = 0
    player_sprite_choice: int = 1
    flags: List[Position] = field(default_factory=list)
    players: List[PlayerPosition] = field(default_factory=list)
    target: List[Position] = field(default_factory=list)
    prison: List[Position] = field(default_factory=list)


@dataclass
class GameConfig:
    """Game configuration."""
    num_players: int = 3
    num_flags: int = 9
    use_random_flags: bool = True
    map_width: int = 20
    map_height: int = 20
    servers: Dict[str, str] = field(default_factory=dict)
    teams: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class StateSnapshot:
    """Game state snapshot for GameStateManager internal state tracking."""
    # Game state
    game_started: bool = False
    game_paused: bool = False
    game_over: bool = False
    winner: Optional[Team] = None

    # Team scores
    l_team_score: int = 0
    r_team_score: int = 0

    # Configuration
    config: Optional[GameConfig] = None

    # WebSocket connection state
    l_team_connected: bool = False
    r_team_connected: bool = False
    l_team_who: str = '-'
    r_team_who: str = '-'

    # Game flow state
    flow_state: GameFlowState = GameFlowState.LOADING
    flow_sub_state: Optional[GameFlowSubState] = GameFlowSubState.LOADING_ASSETS
    current_scene: str = 'Boot'
    initialized: bool = False
    assets_loaded: bool = False
    config_loaded: bool = False
    error: Optional[str] = None

    # Team state
    l_team_state: TeamState = field(
        default_factory=lambda: TeamState(player_sprite_choice=1)
    )
    r_team_state: TeamState = field(
        default_factory=lambda: TeamState(player_sprite_choice=4)
    )

    # Map data
    walls: List[Position] = field(default_factory=list)
    obstacles1: List[Position] = field(default_factory=list)
    obstacles2: List[Position] = field(default_factory=list)
