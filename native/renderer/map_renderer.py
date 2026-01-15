"""
Map renderer for game rendering
Handles rendering of map elements: grid, areas, walls
"""

import pygame
from typing import Optional, List, Tuple
from ..utils import (
    TILE_SIZE, COLOR_GRID, COLOR_TARGET_L, COLOR_TARGET_R,
    COLOR_PRISON_L, COLOR_PRISON_R, COLOR_WALL, Team
)
from ..managers.map_manager import MapManager


class MapRenderer:
    """Map renderer for game elements"""

    def __init__(
        self,
        map_offset_x: int,
        map_offset_y: int,
        map_pixel_width: int,
        map_pixel_height: int,
        map_manager: Optional[MapManager] = None
    ):
        """
        Initialize map renderer

        Args:
            map_offset_x: Map X offset in pixels
            map_offset_y: Map Y offset in pixels
            map_pixel_width: Map width in pixels
            map_pixel_height: Map height in pixels
            map_manager: Optional map manager for tile-based rendering
        """
        self.map_offset_x = map_offset_x
        self.map_offset_y = map_offset_y
        self.map_pixel_width = map_pixel_width
        self.map_pixel_height = map_pixel_height
        self.map_manager = map_manager
        self._map_render_debug = False

    def render_map(self, screen: pygame.Surface, game_map, map_width: int, map_height: int) -> bool:
        """
        Render map elements

        Args:
            screen: Pygame surface to render on
            game_map: GameMap instance
            map_width: Map width in tiles
            map_height: Map height in tiles

        Returns:
            True if MapManager handled rendering, False if fallback used
        """
        if self.map_manager and self.map_manager.ground_layer:
            self._render_with_map_manager(screen, game_map)
            return True
        else:
            self._render_grid_fallback(screen, map_width, map_height)
            return False

    def _render_with_map_manager(self, screen: pygame.Surface, game_map) -> None:
        """Render map using MapManager with tile-based graphics"""
        clip_rect = pygame.Rect(
            self.map_offset_x,
            self.map_offset_y,
            self.map_pixel_width,
            self.map_pixel_height
        )
        old_clip = screen.get_clip()
        screen.set_clip(clip_rect)

        # Get area positions
        left_target = [(pos.x, pos.y) for pos in game_map.get_team_target_positions(Team.LEFT)]
        right_target = [(pos.x, pos.y) for pos in game_map.get_team_target_positions(Team.RIGHT)]
        left_prison = [(pos.x, pos.y) for pos in game_map.get_team_prison_positions(Team.LEFT)]
        right_prison = [(pos.x, pos.y) for pos in game_map.get_team_prison_positions(Team.RIGHT)]

        # Get obstacles
        obstacles_data = self.map_manager.get_obstacles()
        obstacles1 = self._normalize_obstacles(obstacles_data.get("obstacles1", []))
        obstacles2 = self._normalize_obstacles(obstacles_data.get("obstacles2", []))

        self._debug_print(left_target, right_target, left_prison, right_prison, obstacles1, obstacles2)

        # Render map
        self.map_manager.render_map(
            screen,
            offset_x=self.map_offset_x,
            offset_y=self.map_offset_y,
            left_target=left_target,
            right_target=right_target,
            left_prison=left_prison,
            right_prison=right_prison,
            obstacles1=obstacles1,
            obstacles2=obstacles2
        )

        screen.set_clip(old_clip)

    def _normalize_obstacles(self, obstacles: List) -> List[Tuple[int, int]]:
        """Convert obstacle data to tuple format if needed"""
        if obstacles and len(obstacles) > 0 and isinstance(obstacles[0], dict):
            return [(obs["x"], obs["y"]) for obs in obstacles]
        return obstacles

    def _debug_print(self, left_target, right_target, left_prison, right_prison, obs1, obs2):
        """Print debug info once"""
        if not self._map_render_debug:
            print(f"[Renderer] Rendering map data:")
            print(f"  left_target: {len(left_target)}")
            print(f"  right_target: {len(right_target)}")
            print(f"  left_prison: {len(left_prison)}")
            print(f"  right_prison: {len(right_prison)}")
            print(f"  obstacles1: {len(obs1)}")
            print(f"  obstacles2: {len(obs2)}")
            print(f"  offset: ({self.map_offset_x}, {self.map_offset_y})")
            print(f"  level_layer exists: {self.map_manager.level_layer is not None}")
            self._map_render_debug = True

    def _render_grid_fallback(self, screen: pygame.Surface, map_width: int, map_height: int) -> None:
        """Render simple grid when MapManager unavailable"""
        for x in range(map_width + 1):
            start_pos = (self.map_offset_x + x * TILE_SIZE, self.map_offset_y)
            end_pos = (self.map_offset_x + x * TILE_SIZE, self.map_offset_y + self.map_pixel_height)
            pygame.draw.line(screen, COLOR_GRID, start_pos, end_pos)

        for y in range(map_height + 1):
            start_pos = (self.map_offset_x, self.map_offset_y + y * TILE_SIZE)
            end_pos = (self.map_offset_x + self.map_pixel_width, self.map_offset_y + y * TILE_SIZE)
            pygame.draw.line(screen, COLOR_GRID, start_pos, end_pos)

    def render_areas(self, screen: pygame.Surface, game_map) -> None:
        """Render target areas and prisons (fallback method)"""
        self._render_area_list(screen, game_map.left_team_target, COLOR_TARGET_L)
        self._render_area_list(screen, game_map.right_team_target, COLOR_TARGET_R)
        self._render_area_list(screen, game_map.left_team_prison, COLOR_PRISON_L)
        self._render_area_list(screen, game_map.right_team_prison, COLOR_PRISON_R)

    def _render_area_list(self, screen: pygame.Surface, positions, color) -> None:
        """Render a list of positions with given color"""
        for pos in positions:
            x = self.map_offset_x + pos.x * TILE_SIZE
            y = self.map_offset_y + pos.y * TILE_SIZE
            pygame.draw.rect(screen, color, (x, y, TILE_SIZE, TILE_SIZE))

    def render_walls(self, screen: pygame.Surface, walls) -> None:
        """Render wall positions"""
        for wall in walls:
            x = self.map_offset_x + wall.x * TILE_SIZE
            y = self.map_offset_y + wall.y * TILE_SIZE
            pygame.draw.rect(screen, COLOR_WALL, (x, y, TILE_SIZE, TILE_SIZE))
