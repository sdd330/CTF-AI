"""
Game scene input handling mixin.
Handles keyboard and remote input processing.
"""

import pygame

from ...utils import Direction
from ...managers import (
    InputManager,
    KeyboardInputStrategy,
    RemoteInputStrategy,
    HybridInputStrategy,
    InputObserver,
)


class GameSceneInputMixin:
    """
    Mixin providing input handling functionality.
    Handles keyboard events and player movement input.
    """

    def _setup_input_manager(self):
        """Setup input manager with hybrid strategy (keyboard + remote)."""
        # Create keyboard input strategy (WASD and arrow keys)
        keyboard_strategy = KeyboardInputStrategy()

        # Create remote control strategy
        remote_strategy = RemoteInputStrategy()

        # Create hybrid strategy (keyboard priority)
        hybrid_strategy = HybridInputStrategy(keyboard_strategy, remote_strategy)

        # Create input manager
        self.input_manager = InputManager(hybrid_strategy)

        # Set game control callbacks
        self.input_manager.set_game_start_callback(self._on_game_start)
        self.input_manager.set_game_pause_callback(self._on_game_pause)

        # Register as observer (listen for input changes)
        self.input_manager.subscribe(self)

        print("[Game] Input manager configured (keyboard + remote)")

    def handle_event(self, event: pygame.event.Event):
        """Handle pygame events."""
        if not self.game:
            return

        # Handle keyboard input (distinguish WASD and arrow keys)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # ESC to quit game
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif self.game.state.game_started and not self.game.state.game_paused:
                # WASD controls L0 player
                if event.key == pygame.K_w:
                    self._handle_player_input("L0", Direction.UP)
                elif event.key == pygame.K_s:
                    self._handle_player_input("L0", Direction.DOWN)
                elif event.key == pygame.K_a:
                    self._handle_player_input("L0", Direction.LEFT)
                elif event.key == pygame.K_d:
                    self._handle_player_input("L0", Direction.RIGHT)
                # Arrow keys control R0 player
                elif event.key == pygame.K_UP:
                    self._handle_player_input("R0", Direction.UP)
                elif event.key == pygame.K_DOWN:
                    self._handle_player_input("R0", Direction.DOWN)
                elif event.key == pygame.K_LEFT:
                    self._handle_player_input("R0", Direction.LEFT)
                elif event.key == pygame.K_RIGHT:
                    self._handle_player_input("R0", Direction.RIGHT)

        # Pass other events to input manager (space, P key, etc.)
        if self.input_manager:
            self.input_manager.handle_event(event)

    def on_input_change(self, direction: Direction):
        """
        Input change callback (implements InputObserver interface).

        Args:
            direction: New input direction
        """
        if not self.game or not self.game.state.game_started:
            return
        # Currently no action needed - handled by direct key events
        pass

    def _handle_player_input(self, player_name: str, direction: Direction):
        """
        Handle player input.

        Args:
            player_name: Player name (e.g., "L0", "R0")
            direction: Input direction
        """
        if not self.game or not self.game.state.game_started:
            return

        if direction == Direction.STAY:
            return

        # Find the corresponding player
        all_players = (
            self.game.state.left_team_players + self.game.state.right_team_players
        )
        for player in all_players:
            if player.name == player_name and not player.in_prison:
                # Check if target position is valid (not a wall)
                dx, dy = direction.to_vector()
                new_x = player.grid_x + dx
                new_y = player.grid_y + dy

                if self.game.game_map.is_valid_position(new_x, new_y):
                    self.game.set_player_action(player.name, direction)
                break
