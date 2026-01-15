"""
Game flow control mixin for GameStateManager.
"""

from typing import Optional

from .enums import GameFlowState, GameFlowSubState
from .models import StateSnapshot, GameConfig
from .team_generator import TeamGenerator


class FlowControlMixin:
    """Mixin providing game flow control methods."""

    _state: StateSnapshot

    def _notify_listeners(self) -> None:
        """Notify all listeners (to be implemented by main class)."""
        raise NotImplementedError

    # ========== Flow State Management ==========

    def set_flow_state(
        self,
        flow_state: GameFlowState,
        sub_state: Optional[GameFlowSubState] = None
    ) -> None:
        """Set game flow state."""
        self._state.flow_state = flow_state
        self._state.flow_sub_state = sub_state
        self._notify_listeners()

    def set_assets_loaded(self, loaded: bool = True) -> None:
        """Set assets loaded state."""
        self._state.assets_loaded = loaded
        if loaded and self._state.flow_sub_state == GameFlowSubState.LOADING_ASSETS:
            self._state.flow_sub_state = GameFlowSubState.LOADING_CONFIG
        self._notify_listeners()

    def set_initialized(self, initialized: bool = True) -> None:
        """Set initialization state."""
        self._state.initialized = initialized
        if initialized:
            self._state.flow_state = GameFlowState.READY
            self._state.flow_sub_state = None
        self._notify_listeners()

    def set_error(self, error: Optional[str]) -> None:
        """Set error state."""
        self._state.error = error
        self._notify_listeners()

    def set_current_scene(self, scene: str) -> None:
        """Set current scene."""
        self._state.current_scene = scene
        self._notify_listeners()

    # ========== Team State Generation ==========

    def generate_targets_and_prisons(
        self, map_width: int, map_height: int
    ) -> None:
        """Generate target areas and prison positions."""
        l_target, l_prison, r_target, r_prison = \
            TeamGenerator.generate_targets_and_prisons(map_width, map_height)

        self._state.l_team_state.target = l_target
        self._state.l_team_state.prison = l_prison
        self._state.r_team_state.target = r_target
        self._state.r_team_state.prison = r_prison
        self._notify_listeners()

    def generate_players(self, map_width: int) -> None:
        """Generate player positions."""
        config = self._state.config or GameConfig()
        l_players, r_players = TeamGenerator.generate_players(map_width, config)

        self._state.l_team_state.players = l_players
        self._state.r_team_state.players = r_players
        self._notify_listeners()

    def generate_flags(self, map_width: int, map_height: int) -> None:
        """Generate flag positions."""
        config = self._state.config or GameConfig()
        l_flags, r_flags = TeamGenerator.generate_flags(
            map_width,
            map_height,
            config,
            self._state.obstacles1,
            self._state.obstacles2
        )

        self._state.l_team_state.flags = l_flags
        self._state.r_team_state.flags = r_flags
        self._notify_listeners()

    def generate_team_states(self, map_width: int, map_height: int) -> None:
        """Generate all team states."""
        self.generate_flags(map_width, map_height)
        self.generate_players(map_width)
        self.generate_targets_and_prisons(map_width, map_height)

    # ========== Computed Properties ==========

    def is_game_active(self) -> bool:
        """Check if game is active."""
        return (self._state.game_started and
                not self._state.game_paused and
                not self._state.game_over)

    def is_loading(self) -> bool:
        """Check if in loading state."""
        return self._state.flow_state == GameFlowState.LOADING

    def is_playing(self) -> bool:
        """Check if playing."""
        return self._state.flow_state == GameFlowState.PLAYING

    def is_paused(self) -> bool:
        """Check if paused."""
        return (self._state.flow_state == GameFlowState.PLAYING and
                self._state.flow_sub_state == GameFlowSubState.PAUSED)

    def is_running(self) -> bool:
        """Check if running."""
        return (self._state.flow_state == GameFlowState.PLAYING and
                self._state.flow_sub_state == GameFlowSubState.RUNNING)

    def is_ended(self) -> bool:
        """Check if ended."""
        return self._state.flow_state == GameFlowState.ENDED

    def is_ready(self) -> bool:
        """Check if ready."""
        return self._state.flow_state == GameFlowState.READY
