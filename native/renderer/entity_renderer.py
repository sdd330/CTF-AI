"""
Entity renderer for game rendering
Handles rendering of flags and players
"""

import pygame
from typing import Optional
from ..utils import (
    TILE_SIZE, PLAYER_SIZE, FLAG_SIZE,
    COLOR_FLAG_L, COLOR_FLAG_R, COLOR_LEFT_TEAM, COLOR_RIGHT_TEAM
)
from .asset_loader import AssetLoader


class EntityRenderer:
    """Entity renderer for flags and players"""

    def __init__(
        self,
        map_offset_x: int,
        map_offset_y: int,
        asset_loader: AssetLoader
    ):
        """
        Initialize entity renderer

        Args:
            map_offset_x: Map X offset in pixels
            map_offset_y: Map Y offset in pixels
            asset_loader: Asset loader instance
        """
        self.map_offset_x = map_offset_x
        self.map_offset_y = map_offset_y
        self.assets = asset_loader

    def render_flags(self, screen: pygame.Surface, flags, game_map) -> None:
        """
        Render all flags

        Args:
            screen: Pygame surface to render on
            flags: List of flag objects
            game_map: GameMap instance for target area checks
        """
        from ..map.map import Position

        for flag in flags:
            if flag.is_scored:
                flag_pos = Position(flag.grid_x, flag.grid_y)
                is_in_target = (
                    flag_pos in game_map.left_team_target_set or
                    flag_pos in game_map.right_team_target_set
                )
                if not is_in_target:
                    continue

            self._render_single_flag(screen, flag)

    def _render_single_flag(self, screen: pygame.Surface, flag) -> None:
        """Render a single flag"""
        x = self.map_offset_x + flag.pixel_x - FLAG_SIZE // 2
        y = self.map_offset_y + flag.pixel_y - FLAG_SIZE // 2

        flag_img = self.assets.get_flag_image(flag.team.value)

        if flag_img:
            scaled_img = pygame.transform.scale(flag_img, (FLAG_SIZE, FLAG_SIZE))
            screen.blit(scaled_img, (x, y))
        else:
            color = COLOR_FLAG_L if flag.team.value == "L" else COLOR_FLAG_R
            pygame.draw.rect(screen, color, (x, y, FLAG_SIZE, FLAG_SIZE))

        if flag.is_picked_up:
            pygame.draw.circle(
                screen, (255, 255, 0),
                (int(x + FLAG_SIZE // 2), int(y + FLAG_SIZE // 2)),
                FLAG_SIZE // 4, 2
            )

    def render_players(self, screen: pygame.Surface, players) -> None:
        """
        Render all players

        Args:
            screen: Pygame surface to render on
            players: List of player objects
        """
        for player in players:
            self._render_single_player(screen, player)

    def _render_single_player(self, screen: pygame.Surface, player) -> None:
        """Render a single player"""
        x = self.map_offset_x + player.pixel_x - PLAYER_SIZE // 2
        y = self.map_offset_y + player.pixel_y - PLAYER_SIZE // 2

        sprite_sheet = self.assets.get_player_sprite_sheet(
            player.team.value, player.has_flag
        )

        if sprite_sheet:
            sprite_surface = self._extract_sprite(sprite_sheet, player)
            if sprite_surface:
                self._render_player_sprite(screen, sprite_surface, player, x, y)
                return

        self._render_player_fallback(screen, player, x, y)

    def _extract_sprite(self, sprite_sheet: pygame.Surface, player) -> Optional[pygame.Surface]:
        """Extract sprite from sprite sheet"""
        sprite_rect = player.get_sprite_rect()
        sprite_x, sprite_y, sprite_w, sprite_h = sprite_rect
        sheet_width, sheet_height = sprite_sheet.get_size()

        # Boundary checks
        sprite_x = max(0, min(sprite_x, sheet_width - sprite_w))
        sprite_y = max(0, min(sprite_y, sheet_height - sprite_h))
        sprite_w = min(sprite_w, sheet_width - sprite_x)
        sprite_h = min(sprite_h, sheet_height - sprite_y)

        try:
            return sprite_sheet.subsurface(
                pygame.Rect(sprite_x, sprite_y, sprite_w, sprite_h)
            )
        except (ValueError, pygame.error) as e:
            print(f"[Renderer] Warning: Cannot extract sprite: {e}")
            return None

    def _render_player_sprite(
        self,
        screen: pygame.Surface,
        sprite_surface: pygame.Surface,
        player,
        x: float,
        y: float
    ) -> None:
        """Render player using sprite"""
        if player.in_prison:
            sprite_surface = sprite_surface.copy()
            sprite_surface.set_alpha(128)

        scaled_sprite = pygame.transform.scale(sprite_surface, (PLAYER_SIZE, PLAYER_SIZE))
        screen.blit(scaled_sprite, (x, y))

    def _render_player_fallback(self, screen: pygame.Surface, player, x: float, y: float) -> None:
        """Render player using simple shapes (fallback)"""
        color = COLOR_LEFT_TEAM if player.team.value == "L" else COLOR_RIGHT_TEAM

        if player.in_prison:
            color = tuple(max(0, c - 100) for c in color)

        pygame.draw.circle(
            screen, color,
            (int(x + PLAYER_SIZE // 2), int(y + PLAYER_SIZE // 2)),
            PLAYER_SIZE // 2
        )

        if player.has_flag:
            pygame.draw.circle(
                screen, (255, 255, 0),
                (int(x + PLAYER_SIZE // 2), int(y + PLAYER_SIZE // 2)),
                PLAYER_SIZE // 3, 2
            )
