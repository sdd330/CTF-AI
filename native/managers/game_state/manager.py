"""Game state manager - singleton"""

from typing import Optional, Callable, Set, Tuple, List
from .enums import GameFlowState, GameFlowSubState
from .models import Position, TeamState, GameConfig, StateSnapshot
from .config_loader import ConfigLoader
from .team_generator import TeamGenerator
from ...utils import Team

StateChangeListener = Callable[[StateSnapshot], None]


class GameStateManager:
    """Game state manager (singleton)"""
    _instance: Optional['GameStateManager'] = None

    def __new__(cls) -> 'GameStateManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._state = StateSnapshot()
        self._listeners: Set[StateChangeListener] = set()
        self._initialized = True

    @classmethod
    def get_instance(cls) -> 'GameStateManager':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset singleton instance (for testing)."""
        cls._instance = None

    def get_state(self) -> StateSnapshot:
        """Get current state."""
        return self._state

    def _notify_listeners(self) -> None:
        """Notify all listeners of state change."""
        for listener in self._listeners:
            try:
                listener(self._state)
            except Exception as e:
                print(f"[GameStateManager] Error notifying listener: {e}")

    def on_state_change(self, listener: StateChangeListener) -> Callable[[], None]:
        """Subscribe to state changes. Returns unsubscribe function."""
        self._listeners.add(listener)
        return lambda: self._listeners.discard(listener)

    # ========== Configuration ==========

    def load_config(self, config_path: str = 'game_config.json') -> GameConfig:
        """Load game configuration."""
        config = ConfigLoader.load(config_path)
        if config is None:
            config = ConfigLoader.get_default()

        self.set_config(config)
        self._state.config_loaded = True
        self._notify_listeners()
        return config

    def get_config(self) -> Optional[GameConfig]:
        """Get current configuration."""
        return self._state.config

    def set_config(self, config: GameConfig) -> None:
        """Set configuration."""
        self._state.config = config
        self._notify_listeners()

    # ========== Game Control ==========

    def start_game(self) -> None:
        """Start the game."""
        self._state.game_started = True
        self._state.game_paused = False
        self._state.game_over = False
        self._state.flow_state = GameFlowState.PLAYING
        self._state.flow_sub_state = GameFlowSubState.RUNNING
        self._notify_listeners()

    def pause_game(self) -> None:
        """Toggle pause state."""
        self._state.game_paused = not self._state.game_paused
        if self._state.game_paused:
            self._state.flow_sub_state = GameFlowSubState.PAUSED
        else:
            self._state.flow_sub_state = GameFlowSubState.RUNNING
        self._notify_listeners()

    def end_game(self, winner: Team) -> None:
        """End the game."""
        self._state.game_over = True
        self._state.winner = winner
        self._state.game_started = False
        self._state.flow_state = GameFlowState.ENDED
        self._state.flow_sub_state = None
        self._notify_listeners()

    def reset(self) -> None:
        """Reset game state."""
        config = self._state.config
        self._state = StateSnapshot()
        self._state.config = config
        self._notify_listeners()

    def reset_game_state(self) -> None:
        """Reset game state (preserving config and team state)."""
        self._state.game_started = False
        self._state.game_paused = False
        self._state.game_over = False
        self._state.winner = None
        self._state.l_team_score = 0
        self._state.r_team_score = 0
        self._state.l_team_state.score = 0
        self._state.r_team_state.score = 0
        self._notify_listeners()

    # ========== Score Updates ==========

    def update_l_team_score(self, score: int) -> None:
        """Update L team score."""
        self._state.l_team_score = score
        self._state.l_team_state.score = score
        self._notify_listeners()

    def update_r_team_score(self, score: int) -> None:
        """Update R team score."""
        self._state.r_team_score = score
        self._state.r_team_state.score = score
        self._notify_listeners()

    # ========== Connection State ==========

    def set_l_team_connection(self, connected: bool, who: str = '-') -> None:
        """Set L team connection state."""
        self._state.l_team_connected = connected
        self._state.l_team_who = who
        self._notify_listeners()

    def set_r_team_connection(self, connected: bool, who: str = '-') -> None:
        """Set R team connection state."""
        self._state.r_team_connected = connected
        self._state.r_team_who = who
        self._notify_listeners()

    # ========== Team State Management ==========

    def set_l_team_state(self, **kwargs) -> None:
        """Set L team state."""
        for key, value in kwargs.items():
            if hasattr(self._state.l_team_state, key):
                setattr(self._state.l_team_state, key, value)
        self._notify_listeners()

    def set_r_team_state(self, **kwargs) -> None:
        """Set R team state."""
        for key, value in kwargs.items():
            if hasattr(self._state.r_team_state, key):
                setattr(self._state.r_team_state, key, value)
        self._notify_listeners()

    def get_team_states(self) -> Tuple[TeamState, TeamState]:
        """Get team states."""
        return self._state.l_team_state, self._state.r_team_state

    # ========== Map State Management ==========

    def set_map_data(
        self,
        walls: List[Position] = None,
        obstacles1: List[Position] = None,
        obstacles2: List[Position] = None
    ) -> None:
        """Set map data."""
        if walls is not None:
            self._state.walls = walls
        if obstacles1 is not None:
            self._state.obstacles1 = obstacles1
        if obstacles2 is not None:
            self._state.obstacles2 = obstacles2
        self._notify_listeners()
