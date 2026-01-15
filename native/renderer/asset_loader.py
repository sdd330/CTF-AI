"""
Asset loader for game rendering
Handles loading sprite sheets and images
"""

import pygame
from typing import Optional
from ..utils.assets import (
    CHARACTERS_SPRITESHEET, CHARACTERS_RED_FLAG, CHARACTERS_YELLOW_FLAG,
    RED_FLAG_IMG, YELLOW_FLAG_IMG, TILES_SPRITESHEET
)


class AssetLoader:
    """Asset loader for game rendering"""

    def __init__(self):
        """Initialize asset loader"""
        self.character_spritesheet: Optional[pygame.Surface] = None
        self.character_red_flag: Optional[pygame.Surface] = None
        self.character_yellow_flag: Optional[pygame.Surface] = None
        self.red_flag_img: Optional[pygame.Surface] = None
        self.yellow_flag_img: Optional[pygame.Surface] = None
        self.tiles_spritesheet: Optional[pygame.Surface] = None

    def load_all(self) -> None:
        """Load all game assets"""
        try:
            self._load_character_sprites()
            self._load_flag_images()
            self._load_tile_sprites()
        except Exception as e:
            print(f"Warning: Failed to load assets: {e}")
            print("Will use default rendering")

    def _load_character_sprites(self) -> None:
        """Load character sprite sheets"""
        if CHARACTERS_SPRITESHEET.exists():
            try:
                self.character_spritesheet = pygame.image.load(
                    str(CHARACTERS_SPRITESHEET)
                ).convert_alpha()
            except pygame.error:
                print(f"Warning: Cannot load {CHARACTERS_SPRITESHEET.name}")

        if CHARACTERS_RED_FLAG.exists():
            try:
                self.character_red_flag = pygame.image.load(
                    str(CHARACTERS_RED_FLAG)
                ).convert_alpha()
            except pygame.error:
                pass

        if CHARACTERS_YELLOW_FLAG.exists():
            try:
                self.character_yellow_flag = pygame.image.load(
                    str(CHARACTERS_YELLOW_FLAG)
                ).convert_alpha()
            except pygame.error:
                pass

    def _load_flag_images(self) -> None:
        """Load flag images"""
        if RED_FLAG_IMG.exists():
            try:
                self.red_flag_img = pygame.image.load(
                    str(RED_FLAG_IMG)
                ).convert_alpha()
            except pygame.error:
                pass

        if YELLOW_FLAG_IMG.exists():
            try:
                self.yellow_flag_img = pygame.image.load(
                    str(YELLOW_FLAG_IMG)
                ).convert_alpha()
            except pygame.error:
                pass

    def _load_tile_sprites(self) -> None:
        """Load tile sprite sheets"""
        if TILES_SPRITESHEET.exists():
            try:
                self.tiles_spritesheet = pygame.image.load(
                    str(TILES_SPRITESHEET)
                ).convert_alpha()
            except pygame.error:
                pass

    def get_player_sprite_sheet(self, team_value: str, has_flag: bool) -> Optional[pygame.Surface]:
        """
        Get appropriate sprite sheet for player

        Args:
            team_value: Team value ("L" or "R")
            has_flag: Whether player has flag

        Returns:
            Sprite sheet surface or None
        """
        if has_flag:
            if team_value == "L" and self.character_yellow_flag:
                return self.character_yellow_flag
            elif team_value == "R" and self.character_red_flag:
                return self.character_red_flag
        return self.character_spritesheet

    def get_flag_image(self, team_value: str) -> Optional[pygame.Surface]:
        """
        Get flag image for team

        Args:
            team_value: Team value ("L" or "R")

        Returns:
            Flag image surface or None
        """
        if team_value == "L":
            return self.red_flag_img
        return self.yellow_flag_img
