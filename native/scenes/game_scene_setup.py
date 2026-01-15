"""Game scene setup helper - initialization methods"""

import pygame
from typing import List, Tuple, TYPE_CHECKING
from ..utils import TILE_SIZE, get_config
from ..managers import (
    MapManager, UIManager, UIComponentType, InputManager,
    KeyboardInputStrategy, RemoteInputStrategy, HybridInputStrategy,
)

if TYPE_CHECKING:
    from .game_scene import GameScene


def create_3x3_grid(center_x: int, center_y: int) -> List[Tuple[int, int]]:
    """Create 3x3 grid positions (matching frontend: create3x3grid)."""
    return [
        (center_x - 1, center_y - 1), (center_x, center_y - 1), (center_x + 1, center_y - 1),
        (center_x - 1, center_y), (center_x, center_y), (center_x + 1, center_y),
        (center_x - 1, center_y + 1), (center_x, center_y + 1), (center_x + 1, center_y + 1)
    ]


class GameSceneSetupHelper:
    """Helper for setting up game scene components."""

    def __init__(self, scene: 'GameScene'):
        self.scene = scene

    def setup_map_manager(self) -> MapManager:
        """Setup and configure map manager."""
        config = get_config()
        map_manager = MapManager()
        map_manager.map_width = config.map_width
        map_manager.map_height = config.map_height
        map_manager.tile_size = TILE_SIZE

        # Load tiles image
        tiles_image = self._load_tiles_image()
        if tiles_image:
            map_manager.initialize_layers(tiles_image)
        else:
            print("[Game] Warning: Cannot load tiles.png, background layers won't render")

        # Set map params if screen available
        screen = self.scene.screen
        if screen:
            map_manager.set_map_params({
                "mapWidth": map_manager.map_width,
                "mapHeight": map_manager.map_height,
                "mapX": 0, "mapY": 0,
                "tileSize": map_manager.tile_size,
                "centerX": screen.get_width() // 2,
                "centerY": screen.get_height() // 2
            })

        print(f"[Game] Map manager setup: {map_manager.map_width}x{map_manager.map_height}, tile size: {map_manager.tile_size}")
        return map_manager

    def _load_tiles_image(self):
        """Load tiles spritesheet image."""
        from ..utils.assets import TILES_SPRITESHEET
        if TILES_SPRITESHEET.exists():
            try:
                tiles_image = pygame.image.load(str(TILES_SPRITESHEET)).convert_alpha()
                print(f"[Game] Loaded tiles.png: {TILES_SPRITESHEET}")
                return tiles_image
            except Exception as e:
                print(f"[Game] Failed to load tiles.png: {e}")
        else:
            print(f"[Game] tiles.png not found: {TILES_SPRITESHEET}")
        return None

    def generate_map_data(self, map_manager: MapManager, map_width: int, map_height: int):
        """Generate map with walls, obstacles, targets, and prisons."""
        map_manager.generate_map_from_config()

        target_y = map_height // 2
        prison_y = map_height - 3
        left_target = create_3x3_grid(2, target_y)
        right_target = create_3x3_grid(map_width - 3, target_y)
        left_prison = create_3x3_grid(2, prison_y)
        right_prison = create_3x3_grid(map_width - 3, prison_y)

        walls = map_manager.get_walls()
        obstacles_data = map_manager.get_obstacles()
        obstacles = obstacles_data.get("obstacles1", []) + obstacles_data.get("obstacles2", [])

        map_manager.generate_map(walls=walls, obstacles=obstacles,
                                  left_target=left_target, right_target=right_target,
                                  left_prison=left_prison, right_prison=right_prison)

        return walls, left_target, right_target, left_prison, right_prison

    def setup_ui_manager(self) -> UIManager:
        """Setup UI manager with components."""
        screen = self.scene.screen
        if not screen:
            print("[Game] Warning: _setup_ui_manager called but screen is None")
            return None

        screen_width = screen.get_width()
        screen_height = screen.get_height()
        print(f"[Game] Setting up UI manager: screen={screen_width}x{screen_height}")

        ui_manager = UIManager(screen)

        # Create tutorial text (centered)
        tutorial = ui_manager.create_component('tutorial', UIComponentType.TUTORIAL_TEXT,
                                               screen_width // 2, screen_height // 2)
        ui_manager.show_component('tutorial')
        print(f"[Game] Tutorial component created: x={screen_width // 2}, y={screen_height // 2}")

        # Create game over text (centered, slightly above)
        ui_manager.create_component('game_over', UIComponentType.GAME_OVER_TEXT,
                                    screen_width // 2, screen_height // 2 - 50)
        ui_manager.hide_component('game_over')

        print("[Game] UI manager setup complete")
        return ui_manager

    def setup_input_manager(self, game_start_callback, game_pause_callback, observer) -> InputManager:
        """Setup input manager with hybrid strategy."""
        keyboard_strategy = KeyboardInputStrategy()
        remote_strategy = RemoteInputStrategy()
        hybrid_strategy = HybridInputStrategy(keyboard_strategy, remote_strategy)

        input_manager = InputManager(hybrid_strategy)
        input_manager.set_game_start_callback(game_start_callback)
        input_manager.set_game_pause_callback(game_pause_callback)
        input_manager.subscribe(observer)

        print("[Game] Input manager setup (keyboard + remote control)")
        return input_manager
