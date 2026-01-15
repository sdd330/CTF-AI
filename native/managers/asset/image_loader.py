"""
图片加载器

职责:
- 从文件系统加载图片
- 支持 alpha 通道转换
- 与缓存系统集成
"""

import pygame
from pathlib import Path
from typing import Optional

from .asset_cache import AssetCache
from .asset_types import get_asset_path


class ImageLoader:
    """
    图片加载器

    负责加载图片文件并与缓存系统集成
    """

    def __init__(self, cache: AssetCache):
        """
        初始化图片加载器

        Args:
            cache: 资源缓存实例
        """
        self._cache = cache

    def load(self, key: str, path: Optional[str] = None,
             convert_alpha: bool = True) -> Optional[pygame.Surface]:
        """
        加载图片

        Args:
            key: 资源键名
            path: 自定义路径（可选）
            convert_alpha: 是否转换为带 alpha 通道的格式

        Returns:
            pygame.Surface 或 None
        """
        # 检查缓存
        if self._cache.has_image(key):
            return self._cache.get_image(key)

        # 获取路径
        asset_path = Path(path) if path else get_asset_path(key)

        try:
            if not asset_path.exists():
                print(f"[ImageLoader] 图片不存在: {asset_path}")
                return None

            image = pygame.image.load(str(asset_path))
            if convert_alpha:
                image = image.convert_alpha()
            else:
                image = image.convert()

            # 缓存
            self._cache.set_image(key, image)

            return image

        except pygame.error as e:
            print(f"[ImageLoader] 加载图片失败 {key}: {e}")
            return None

    def get(self, key: str) -> Optional[pygame.Surface]:
        """
        获取已加载的图片

        Args:
            key: 资源键名

        Returns:
            pygame.Surface 或 None
        """
        return self._cache.get_image(key)

    def get_flag_image(self, team: str) -> Optional[pygame.Surface]:
        """
        获取旗帜图片

        Args:
            team: 队伍 ("L" 或 "R")

        Returns:
            pygame.Surface 或 None
        """
        key = 'red_flag' if team == 'L' else 'yellow_flag'
        return self.get(key) or self.load(key)
