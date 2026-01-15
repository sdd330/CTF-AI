"""Renderer class - main game rendering coordinator"""

import pygame
from typing import Optional
from ..utils import TILE_SIZE, MAP_MARGIN, COLOR_BACKGROUND
from ..game.game import CTFGame
from ..managers.map_manager import MapManager
from .asset_loader import AssetLoader
from .map_renderer import MapRenderer
from .entity_renderer import EntityRenderer


class Renderer:
    """Main renderer class that coordinates all rendering components."""

    def __init__(self, game: CTFGame, screen_width: int, screen_height: int,
                 map_manager: Optional[MapManager] = None):
        """
        Initialize renderer.

        Args:
            game: Game instance
            screen_width: Screen width
            screen_height: Screen height
            map_manager: Map manager (optional)
        """
        self.game = game
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.map_manager = map_manager

        # Calculate map display area
        if map_manager and map_manager.map_width > 0 and map_manager.map_height > 0:
            self.map_offset_x = map_manager.map_x
            self.map_offset_y = map_manager.map_y
            self.map_pixel_width = map_manager.map_width * map_manager.tile_size
            self.map_pixel_height = map_manager.map_height * map_manager.tile_size
        else:
            self.map_offset_x = MAP_MARGIN
            self.map_offset_y = MAP_MARGIN
            self.map_pixel_width = game.game_map.width * TILE_SIZE
            self.map_pixel_height = game.game_map.height * TILE_SIZE

        # Initialize sub-renderers
        self._init_sub_renderers()

    def _init_sub_renderers(self):
        """Initialize sub-renderer components."""
        # Load assets
        self.assets = AssetLoader()
        self.assets.load_all()

        # Expose assets for backward compatibility
        self.character_spritesheet = self.assets.character_spritesheet
        self.character_red_flag = self.assets.character_red_flag
        self.character_yellow_flag = self.assets.character_yellow_flag
        self.red_flag_img = self.assets.red_flag_img
        self.yellow_flag_img = self.assets.yellow_flag_img
        self.tiles_spritesheet = self.assets.tiles_spritesheet

        # Create map renderer
        self._map_renderer = MapRenderer(
            self.map_offset_x, self.map_offset_y,
            self.map_pixel_width, self.map_pixel_height,
            self.map_manager
        )

        # Create entity renderer
        self._entity_renderer = EntityRenderer(
            self.map_offset_x, self.map_offset_y, self.assets
        )

    def render(self, screen: pygame.Surface):
        """
        Render the game.

        Args:
            screen: pygame Surface object
        """
        # Clear screen
        screen.fill(COLOR_BACKGROUND)

        # Render map (including background, walls, obstacles, targets, prisons)
        map_handled = self._map_renderer.render_map(
            screen, self.game.game_map,
            self.game.game_map.width, self.game.game_map.height
        )

        # Render areas fallback if MapManager didn't render them
        if not map_handled:
            self._map_renderer.render_areas(screen, self.game.game_map)

        # Render flags
        self._entity_renderer.render_flags(
            screen, self.game.state.get_all_flags(), self.game.game_map
        )

        # Render players
        self._entity_renderer.render_players(
            screen, self.game.state.get_all_players()
        )
