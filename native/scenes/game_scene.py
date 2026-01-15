"""Main game scene"""

import pygame
from typing import Optional
from .base_scene import BaseScene
from .game_scene_network import GameSceneNetworkController
from .game_scene_physics import GameScenePhysicsController
from .game_scene_setup import GameSceneSetupHelper
from ..game.game import CTFGame
from ..renderer.renderer import Renderer
from ..utils import Team, Direction, GameStats, get_config
from ..managers import InputManager, InputObserver, MapManager, UIManager, GameStateManager


class GameScene(BaseScene, InputObserver):
    """Main game scene - handles game logic and rendering."""

    def __init__(self, scene_manager):
        super().__init__('Game', scene_manager)
        self.game: Optional[CTFGame] = None
        self.renderer: Optional[Renderer] = None
        self.input_manager: Optional[InputManager] = None
        self.map_manager: Optional[MapManager] = None
        self.game_stats: Optional[GameStats] = None
        self.ui_manager: Optional[UIManager] = None
        self.game_state_manager: Optional[GameStateManager] = None
        self.initialized = False

        # Controllers
        self._network = GameSceneNetworkController(self)
        self._physics = GameScenePhysicsController(self)
        self._setup_helper = GameSceneSetupHelper(self)

    def preload(self):
        pass

    def create(self):
        """Create game scene."""
        if hasattr(self, '_game_over_handled'):
            delattr(self, '_game_over_handled')

        if self.initialized:
            print("[Game] Scene already initialized, resetting game state")
            if self.game:
                self.game.state.game_started = False
                self.game.state.game_paused = False
                self.game.state.game_over = False
                self.game.state.winner = None
                self.game.state.left_team_score = 0
                self.game.state.right_team_score = 0
            return

        print("[Game] Creating game scene")
        config = get_config()
        map_width, map_height = config.map_width, config.map_height
        print(f"[Game] Map size from config: {map_width}x{map_height}")

        # Setup map manager
        self.map_manager = self._setup_helper.setup_map_manager()
        self.map_manager.map_width = map_width
        self.map_manager.map_height = map_height

        # Generate map data
        walls, left_target, right_target, left_prison, right_prison = \
            self._setup_helper.generate_map_data(self.map_manager, map_width, map_height)

        game_map = self.map_manager.game_map
        if not game_map:
            raise RuntimeError("Map generation failed!")

        print(f"[Game] Map generated: {map_width}x{map_height}")

        # Create game
        self.game = CTFGame(game_map)
        self.game.initialize(num_players=config.num_players, num_flags=config.num_flags)

        # Setup GameStateManager
        self.game_state_manager = GameStateManager.get_instance()
        self.game_state_manager.generate_team_states(map_width, map_height)

        # Create renderer
        if self.screen:
            self.renderer = Renderer(self.game, self.screen.get_width(),
                                     self.screen.get_height(), self.map_manager)

        # Setup managers
        self.input_manager = self._setup_helper.setup_input_manager(
            self._on_game_start, self._on_game_pause, self)
        self._physics.setup()
        self.game_stats = GameStats()

        # Setup network
        self._network.game_state_manager = self.game_state_manager
        self._network.setup_socket_manager(map_width, map_height, walls,
                                           left_target, right_target, left_prison, right_prison)

        # Setup UI
        if self.screen:
            print(f"[Game] Screen set: {self.screen.get_width()}x{self.screen.get_height()}")
            self.ui_manager = self._setup_helper.setup_ui_manager()
        else:
            print("[Game] Warning: Screen not set, cannot create UI manager")

        self.initialized = True
        print("[Game] Game scene created")

    def _on_game_start(self):
        """Game start callback."""
        if self.game and not self.game.state.game_started:
            self.game.state.game_started = True
            if self.game_stats:
                self.game_stats.start_game()
            self._network.reset_elapsed_time()
            if self.ui_manager:
                self.ui_manager.hide_component('tutorial')
            print("[Game] Game started")

    def _on_game_pause(self):
        """Game pause/resume callback."""
        if self.game and self.game.state.game_started:
            self.game.state.game_paused = not self.game.state.game_paused
            status = "paused" if self.game.state.game_paused else "resumed"
            print(f"[Game] Game {status}")

    def _end_game(self, winner: Team):
        """End the game."""
        if self.game:
            self.game.state.game_over = True
            self.game.state.winner = winner
            if self.game_stats:
                self.game_stats.end_game(winner)
            print(f"[Game] Game over, {winner.value} team wins!")

    def update(self, delta_time: int):
        """Update game scene."""
        if not self.input_manager or not self.game:
            return

        if not self.game.state.game_started:
            self.input_manager.update(delta_time)
            if self.ui_manager:
                self.ui_manager.show_component('tutorial')
                self.ui_manager.hide_component('game_over')
            return

        if self.game.state.game_paused:
            return

        self.input_manager.update(delta_time)

        # Update players
        for player in self.game.state.left_team_players + self.game.state.right_team_players:
            player.update(delta_time)

        # Update physics
        self._physics.update()

        # Update flag positions
        for flag in self.game.state.get_all_flags():
            if flag.is_picked_up and flag.carried_by:
                flag.update_position(flag.carried_by.pixel_x, flag.carried_by.pixel_y)

        # Network updates
        self._network.update_elapsed_time(delta_time)
        self._network.apply_backend_actions()
        if self._network.is_any_team_connected():
            self._network.send_game_status()

        # Update UI
        self._update_ui()

        # Check game over
        if self.game.state.game_over and not hasattr(self, '_game_over_handled'):
            winner = self.game.state.winner
            if winner:
                self._game_over_handled = True
                self._network.send_game_finished(self.game.state.left_team_score,
                                                  self.game.state.right_team_score)
                self.start_scene('GameOver', {
                    'winner': winner,
                    'stats': self.game_stats.get_summary() if self.game_stats else None,
                })

    def _update_ui(self):
        """Update UI components."""
        if not self.ui_manager or not self.game:
            return

        if self.game.state.game_over:
            self.ui_manager.show_component('game_over')
            winner = self.game.state.winner.value if self.game.state.winner else None
            self.ui_manager.update_component('game_over', winner)
            self.ui_manager.hide_component('tutorial')
        elif not self.game.state.game_started:
            self.ui_manager.show_component('tutorial')
            self.ui_manager.hide_component('game_over')
        else:
            self.ui_manager.hide_component('tutorial')
            self.ui_manager.hide_component('game_over')

    def handle_event(self, event: pygame.event.Event):
        """Handle pygame events."""
        if not self.game:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif self.game.state.game_started and not self.game.state.game_paused:
                self._handle_keyboard_input(event.key)

        if self.input_manager:
            self.input_manager.handle_event(event)

    def _handle_keyboard_input(self, key):
        """Handle keyboard input for player control."""
        key_mapping = {
            pygame.K_w: ("L0", Direction.UP), pygame.K_s: ("L0", Direction.DOWN),
            pygame.K_a: ("L0", Direction.LEFT), pygame.K_d: ("L0", Direction.RIGHT),
            pygame.K_UP: ("R0", Direction.UP), pygame.K_DOWN: ("R0", Direction.DOWN),
            pygame.K_LEFT: ("R0", Direction.LEFT), pygame.K_RIGHT: ("R0", Direction.RIGHT),
        }
        if key in key_mapping:
            player_name, direction = key_mapping[key]
            self._handle_player_input(player_name, direction)

    def on_input_change(self, direction: Direction):
        """Input change callback (InputObserver interface)."""
        pass

    def _handle_player_input(self, player_name: str, direction: Direction):
        """Handle player input."""
        if not self.game or not self.game.state.game_started or direction == Direction.STAY:
            return

        for player in self.game.state.left_team_players + self.game.state.right_team_players:
            if player.name == player_name and not player.in_prison:
                dx, dy = direction.to_vector()
                new_x, new_y = player.grid_x + dx, player.grid_y + dy
                if self.game.game_map.is_valid_position(new_x, new_y):
                    self.game.set_player_action(player.name, direction)
                break

    def render(self):
        """Render game scene."""
        if self.renderer and self.screen:
            self.renderer.render(self.screen)
        if self.ui_manager:
            self.ui_manager.render()

    def destroy(self):
        """Destroy game scene."""
        if self.input_manager:
            self.input_manager.unsubscribe(self)
        if self.ui_manager:
            self.ui_manager.destroy_all()
        self._network.destroy()
        self.input_manager = None
        self.ui_manager = None
        self.game = None
        self.renderer = None
        self.initialized = False
        super().destroy()
