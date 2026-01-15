"""
资源缓存管理

职责:
- 管理图片、精灵图、配置文件的缓存
- 提供缓存的增删查操作
- 跟踪已加载资源
"""

import pygame
from typing import Optional, Dict, Any


class AssetCache:
    """
    资源缓存管理类

    管理不同类型资源的缓存存储和状态跟踪
    """

    def __init__(self):
        # 资源缓存
        self._image_cache: Dict[str, pygame.Surface] = {}
        self._spritesheet_cache: Dict[str, pygame.Surface] = {}
        self._config_cache: Dict[str, Any] = {}

        # 加载状态
        self._loaded_assets: set = set()
        self._loading_progress: float = 0.0

    # ========== 图片缓存 ==========

    def get_image(self, key: str) -> Optional[pygame.Surface]:
        """获取缓存的图片"""
        return self._image_cache.get(key)

    def set_image(self, key: str, image: pygame.Surface) -> None:
        """设置图片缓存"""
        self._image_cache[key] = image
        self._loaded_assets.add(key)

    def has_image(self, key: str) -> bool:
        """检查图片是否在缓存中"""
        return key in self._image_cache

    # ========== 精灵图缓存 ==========

    def get_spritesheet(self, key: str) -> Optional[pygame.Surface]:
        """获取缓存的精灵图"""
        return self._spritesheet_cache.get(key)

    def set_spritesheet(self, key: str, spritesheet: pygame.Surface) -> None:
        """设置精灵图缓存"""
        self._spritesheet_cache[key] = spritesheet

    def has_spritesheet(self, key: str) -> bool:
        """检查精灵图是否在缓存中"""
        return key in self._spritesheet_cache

    # ========== 配置缓存 ==========

    def get_config(self, key: str) -> Optional[Dict]:
        """获取缓存的配置"""
        return self._config_cache.get(key)

    def set_config(self, key: str, config: Dict) -> None:
        """设置配置缓存"""
        self._config_cache[key] = config
        self._loaded_assets.add(key)

    def has_config(self, key: str) -> bool:
        """检查配置是否在缓存中"""
        return key in self._config_cache

    # ========== 加载状态 ==========

    def is_loaded(self, key: str) -> bool:
        """检查资源是否已加载"""
        return key in self._loaded_assets

    def mark_loaded(self, key: str) -> None:
        """标记资源为已加载"""
        self._loaded_assets.add(key)

    def get_loading_progress(self) -> float:
        """获取加载进度 (0.0 - 1.0)"""
        return self._loading_progress

    def set_loading_progress(self, progress: float) -> None:
        """设置加载进度"""
        self._loading_progress = progress

    def get_cache_size(self) -> int:
        """获取缓存中的资源数量"""
        return len(self._loaded_assets)

    # ========== 缓存管理 ==========

    def clear(self) -> None:
        """清除所有缓存"""
        self._image_cache.clear()
        self._spritesheet_cache.clear()
        self._config_cache.clear()
        self._loaded_assets.clear()
        self._loading_progress = 0.0

    def remove(self, key: str) -> None:
        """从缓存中移除指定资源"""
        self._image_cache.pop(key, None)
        self._spritesheet_cache.pop(key, None)
        self._config_cache.pop(key, None)
        self._loaded_assets.discard(key)
