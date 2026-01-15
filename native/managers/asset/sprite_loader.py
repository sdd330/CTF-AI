"""
精灵图加载器

职责:
- 加载精灵图 (spritesheet)
- 从精灵图中提取单帧
- 提供角色精灵帧的便捷访问
"""

import pygame
from typing import Optional

from .asset_cache import AssetCache
from .image_loader import ImageLoader
from .asset_types import SPRITE_SIZE, CHARACTERS_PER_ROW, CHARACTER_ROWS


class SpriteLoader:
    """
    精灵图加载器

    负责加载精灵图并提取单个精灵帧
    """

    def __init__(self, cache: AssetCache, image_loader: ImageLoader):
        """
        初始化精灵图加载器

        Args:
            cache: 资源缓存实例
            image_loader: 图片加载器实例
        """
        self._cache = cache
        self._image_loader = image_loader

    def load(self, key: str, path: Optional[str] = None) -> Optional[pygame.Surface]:
        """
        加载精灵图

        Args:
            key: 资源键名
            path: 自定义路径（可选）

        Returns:
            pygame.Surface 或 None
        """
        # 检查缓存
        if self._cache.has_spritesheet(key):
            return self._cache.get_spritesheet(key)

        image = self._image_loader.load(key, path)
        if image:
            self._cache.set_spritesheet(key, image)
        return image

    def get(self, key: str) -> Optional[pygame.Surface]:
        """获取已加载的精灵图"""
        return self._cache.get_spritesheet(key)

    def get_frame(self, spritesheet_key: str, x: int, y: int,
                  width: int = None, height: int = None) -> Optional[pygame.Surface]:
        """
        从精灵图中获取一帧

        Args:
            spritesheet_key: 精灵图键名
            x: X 坐标（像素）
            y: Y 坐标（像素）
            width: 宽度（默认 SPRITE_SIZE）
            height: 高度（默认 SPRITE_SIZE）

        Returns:
            pygame.Surface 或 None
        """
        spritesheet = self.get(spritesheet_key)
        if not spritesheet:
            spritesheet = self.load(spritesheet_key)
        if not spritesheet:
            return None

        width = width or SPRITE_SIZE
        height = height or SPRITE_SIZE

        try:
            frame = pygame.Surface((width, height), pygame.SRCALPHA)
            frame.blit(spritesheet, (0, 0), (x, y, width, height))
            return frame
        except pygame.error as e:
            print(f"[SpriteLoader] 获取精灵帧失败: {e}")
            return None

    def get_character_frame(self, sprite_choice: int, direction: str,
                            frame: int = 0, has_flag: bool = False,
                            flag_team: str = None) -> Optional[pygame.Surface]:
        """
        获取角色精灵帧

        Args:
            sprite_choice: 角色选择（1-8）
            direction: 方向 ("up", "down", "left", "right")
            frame: 动画帧（0-2）
            has_flag: 是否持有旗帜
            flag_team: 旗帜所属队伍（如果持有旗帜）

        Returns:
            pygame.Surface 或 None
        """
        # 选择精灵图
        spritesheet_key = self._get_character_spritesheet_key(has_flag, flag_team)

        # 计算帧坐标
        x, y = self._get_character_frame_position(sprite_choice, direction, frame)

        return self.get_frame(spritesheet_key, x, y)

    def _get_character_spritesheet_key(self, has_flag: bool,
                                       flag_team: str) -> str:
        """获取角色对应的精灵图键名"""
        if has_flag and flag_team:
            if flag_team == 'L':
                return 'characters_red_flag'
            else:
                return 'characters_yellow_flag'
        return 'characters'

    def _get_character_frame_position(self, sprite_choice: int, direction: str,
                                      frame: int = 0) -> tuple:
        """计算角色帧在精灵图中的像素位置"""
        direction_map = {
            "left": 0,
            "down": 1,
            "up": 2,
            "right": 3
        }

        col = direction_map.get(direction, 1)
        base_frame = (sprite_choice - 1) * 12
        direction_index = col
        frame_index = base_frame + direction_index + frame * 4

        row = frame_index // 4
        col = frame_index % 4

        row = min(row, CHARACTER_ROWS - 1)
        col = min(col, CHARACTERS_PER_ROW - 1)

        x = col * SPRITE_SIZE
        y = row * SPRITE_SIZE

        return (x, y)
