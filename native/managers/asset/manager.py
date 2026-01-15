"""
资源管理器
参考 frontend 资源管理实现
设计模式：单例模式 + 组合模式
"""

import pygame
import json
from pathlib import Path
from typing import Optional, Dict, Any, Callable

from .asset_cache import AssetCache
from .image_loader import ImageLoader
from .sprite_loader import SpriteLoader
from .asset_types import get_asset_path, ASSETS_DIR


class AssetManager:
    """
    资源管理器
    使用单例模式确保全局唯一实例
    """

    _instance: Optional['AssetManager'] = None

    def __new__(cls) -> 'AssetManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # 组件
        self._cache = AssetCache()
        self._image_loader = ImageLoader(self._cache)
        self._sprite_loader = SpriteLoader(self._cache, self._image_loader)

        # 回调
        self._on_progress: Optional[Callable[[float], None]] = None
        self._on_complete: Optional[Callable[[], None]] = None

        self._initialized = True

    @classmethod
    def get_instance(cls) -> 'AssetManager':
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """重置单例实例（用于测试）"""
        if cls._instance is not None:
            cls._instance.clear_cache()
        cls._instance = None

    # ========== 委托方法 ==========

    def load_image(self, key: str, path: Optional[str] = None,
                   convert_alpha: bool = True) -> Optional[pygame.Surface]:
        """加载图片"""
        return self._image_loader.load(key, path, convert_alpha)

    def get_image(self, key: str) -> Optional[pygame.Surface]:
        """获取已加载的图片"""
        return self._cache.get_image(key)

    def load_spritesheet(self, key: str, path: Optional[str] = None) -> Optional[pygame.Surface]:
        """加载精灵图"""
        return self._sprite_loader.load(key, path)

    def get_spritesheet(self, key: str) -> Optional[pygame.Surface]:
        """获取已加载的精灵图"""
        return self._cache.get_spritesheet(key)

    def get_sprite_frame(self, spritesheet_key: str, x: int, y: int,
                         width: int = None, height: int = None) -> Optional[pygame.Surface]:
        """从精灵图中获取一帧"""
        return self._sprite_loader.get_frame(spritesheet_key, x, y, width, height)

    def get_character_frame(self, sprite_choice: int, direction: str,
                            frame: int = 0, has_flag: bool = False,
                            flag_team: str = None) -> Optional[pygame.Surface]:
        """获取角色精灵帧"""
        return self._sprite_loader.get_character_frame(
            sprite_choice, direction, frame, has_flag, flag_team
        )

    def get_flag_image(self, team: str) -> Optional[pygame.Surface]:
        """获取旗帜图片"""
        return self._image_loader.get_flag_image(team)

    # ========== 配置加载 ==========

    def load_config(self, key: str, path: Optional[str] = None) -> Optional[Dict]:
        """加载配置文件"""
        if self._cache.has_config(key):
            return self._cache.get_config(key)

        config_path = Path(path) if path else get_asset_path(key)

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            self._cache.set_config(key, config)
            return config
        except Exception as e:
            print(f"[AssetManager] 加载配置失败 {key}: {e}")
            return None

    def get_config(self, key: str) -> Optional[Dict]:
        """获取已加载的配置"""
        return self._cache.get_config(key)

    # ========== 路径和状态 ==========

    def get_asset_path(self, key: str) -> Path:
        """获取资源路径"""
        return get_asset_path(key)

    def is_loaded(self, key: str) -> bool:
        """检查资源是否已加载"""
        return self._cache.is_loaded(key)

    def get_loading_progress(self) -> float:
        """获取加载进度"""
        return self._cache.get_loading_progress()

    def set_progress_callback(self, callback: Callable[[float], None]) -> None:
        """设置进度回调"""
        self._on_progress = callback

    def set_complete_callback(self, callback: Callable[[], None]) -> None:
        """设置完成回调"""
        self._on_complete = callback

    # ========== 缓存管理 ==========

    def clear_cache(self) -> None:
        """清除所有缓存"""
        self._cache.clear()
