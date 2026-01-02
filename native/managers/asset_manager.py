"""
资源管理器
参考 frontend 资源管理实现
设计模式：单例模式 + 缓存模式

职责：
- 管理游戏资源的加载、缓存和释放
- 支持图片、配置文件等资源类型
- 提供统一的资源访问接口
"""

import pygame
from pathlib import Path
from typing import Optional, Dict, Any, Callable
from enum import Enum


class AssetType(Enum):
    """资源类型"""
    IMAGE = 'image'
    SPRITESHEET = 'spritesheet'
    CONFIG = 'config'
    SOUND = 'sound'
    FONT = 'font'


class AssetManager:
    """
    资源管理器
    使用单例模式确保全局唯一实例
    """

    _instance: Optional['AssetManager'] = None

    # 资源目录
    ASSETS_DIR = Path(__file__).parent.parent / "assets"

    # 预定义资源路径
    ASSET_PATHS = {
        # 精灵图
        'characters': 'characters.png',
        'characters_red_flag': 'characters_red_flag.png',
        'characters_yellow_flag': 'characters_yellow_flag.png',
        'tiles': 'tiles.png',
        # 旗帜
        'red_flag': 'red_flag_32_32.png',
        'yellow_flag': 'yellow_flag_32_32.png',
        # 配置
        'game_config': '../game_config.json',
    }

    # 精灵图配置
    SPRITE_SIZE = 32
    CHARACTERS_PER_ROW = 4
    CHARACTER_ROWS = 18
    FRAMES_PER_CHARACTER = 12
    FRAMES_PER_DIRECTION = 3

    def __new__(cls) -> 'AssetManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # 资源缓存
        self._image_cache: Dict[str, pygame.Surface] = {}
        self._spritesheet_cache: Dict[str, pygame.Surface] = {}
        self._config_cache: Dict[str, Any] = {}

        # 加载状态
        self._loaded_assets: set = set()
        self._loading_progress: float = 0.0

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

    # ========== 加载进度 ==========

    def set_progress_callback(self, callback: Callable[[float], None]) -> None:
        """设置进度回调"""
        self._on_progress = callback

    def set_complete_callback(self, callback: Callable[[], None]) -> None:
        """设置完成回调"""
        self._on_complete = callback

    def get_loading_progress(self) -> float:
        """获取加载进度 (0.0 - 1.0)"""
        return self._loading_progress

    # ========== 路径工具 ==========

    def get_asset_path(self, key: str) -> Path:
        """
        获取资源路径

        Args:
            key: 资源键名

        Returns:
            资源路径
        """
        if key in self.ASSET_PATHS:
            return self.ASSETS_DIR / self.ASSET_PATHS[key]
        # 如果不是预定义的，直接作为相对路径
        return self.ASSETS_DIR / key

    # ========== 图片加载 ==========

    def load_image(self, key: str, path: Optional[str] = None,
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
        if key in self._image_cache:
            return self._image_cache[key]

        # 获取路径
        asset_path = Path(path) if path else self.get_asset_path(key)

        try:
            if not asset_path.exists():
                print(f"[AssetManager] 图片不存在: {asset_path}")
                return None

            image = pygame.image.load(str(asset_path))
            if convert_alpha:
                image = image.convert_alpha()
            else:
                image = image.convert()

            # 缓存
            self._image_cache[key] = image
            self._loaded_assets.add(key)

            return image

        except Exception as e:
            print(f"[AssetManager] 加载图片失败 {key}: {e}")
            return None

    def get_image(self, key: str) -> Optional[pygame.Surface]:
        """
        获取已加载的图片

        Args:
            key: 资源键名

        Returns:
            pygame.Surface 或 None
        """
        return self._image_cache.get(key)

    # ========== 精灵图加载 ==========

    def load_spritesheet(self, key: str, path: Optional[str] = None) -> Optional[pygame.Surface]:
        """
        加载精灵图

        Args:
            key: 资源键名
            path: 自定义路径（可选）

        Returns:
            pygame.Surface 或 None
        """
        # 检查缓存
        if key in self._spritesheet_cache:
            return self._spritesheet_cache[key]

        image = self.load_image(key, path)
        if image:
            self._spritesheet_cache[key] = image
        return image

    def get_spritesheet(self, key: str) -> Optional[pygame.Surface]:
        """获取已加载的精灵图"""
        return self._spritesheet_cache.get(key)

    def get_sprite_frame(self, spritesheet_key: str, x: int, y: int,
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
        spritesheet = self.get_spritesheet(spritesheet_key)
        if not spritesheet:
            spritesheet = self.load_spritesheet(spritesheet_key)
        if not spritesheet:
            return None

        width = width or self.SPRITE_SIZE
        height = height or self.SPRITE_SIZE

        try:
            frame = pygame.Surface((width, height), pygame.SRCALPHA)
            frame.blit(spritesheet, (0, 0), (x, y, width, height))
            return frame
        except Exception as e:
            print(f"[AssetManager] 获取精灵帧失败: {e}")
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
        if has_flag and flag_team:
            if flag_team == 'L':
                spritesheet_key = 'characters_red_flag'
            else:
                spritesheet_key = 'characters_yellow_flag'
        else:
            spritesheet_key = 'characters'

        # 计算帧坐标
        x, y = self._get_character_frame_index(sprite_choice, direction, frame)

        return self.get_sprite_frame(spritesheet_key, x, y)

    def _get_character_frame_index(self, sprite_choice: int, direction: str,
                                   frame: int = 0) -> tuple:
        """计算角色帧索引"""
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

        row = min(row, self.CHARACTER_ROWS - 1)
        col = min(col, self.CHARACTERS_PER_ROW - 1)

        x = col * self.SPRITE_SIZE
        y = row * self.SPRITE_SIZE

        return (x, y)

    # ========== 配置加载 ==========

    def load_config(self, key: str, path: Optional[str] = None) -> Optional[Dict]:
        """
        加载配置文件

        Args:
            key: 资源键名
            path: 自定义路径（可选）

        Returns:
            配置字典或 None
        """
        import json

        # 检查缓存
        if key in self._config_cache:
            return self._config_cache[key]

        # 获取路径
        asset_path = Path(path) if path else self.get_asset_path(key)

        try:
            if not asset_path.exists():
                print(f"[AssetManager] 配置文件不存在: {asset_path}")
                return None

            with open(asset_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # 缓存
            self._config_cache[key] = config
            self._loaded_assets.add(key)

            return config

        except Exception as e:
            print(f"[AssetManager] 加载配置失败 {key}: {e}")
            return None

    def get_config(self, key: str) -> Optional[Dict]:
        """获取已加载的配置"""
        return self._config_cache.get(key)

    # ========== 批量加载 ==========

    def preload_all(self) -> bool:
        """
        预加载所有常用资源

        Returns:
            是否全部加载成功
        """
        assets_to_load = [
            ('characters', AssetType.SPRITESHEET),
            ('characters_red_flag', AssetType.SPRITESHEET),
            ('characters_yellow_flag', AssetType.SPRITESHEET),
            ('tiles', AssetType.SPRITESHEET),
            ('red_flag', AssetType.IMAGE),
            ('yellow_flag', AssetType.IMAGE),
        ]

        total = len(assets_to_load)
        loaded = 0
        success = True

        for key, asset_type in assets_to_load:
            try:
                if asset_type == AssetType.SPRITESHEET:
                    result = self.load_spritesheet(key)
                elif asset_type == AssetType.IMAGE:
                    result = self.load_image(key)
                else:
                    result = None

                if result is None:
                    print(f"[AssetManager] 预加载失败: {key}")
                    success = False

            except Exception as e:
                print(f"[AssetManager] 预加载异常 {key}: {e}")
                success = False

            loaded += 1
            self._loading_progress = loaded / total

            if self._on_progress:
                self._on_progress(self._loading_progress)

        if self._on_complete:
            self._on_complete()

        return success

    def is_loaded(self, key: str) -> bool:
        """检查资源是否已加载"""
        return key in self._loaded_assets

    # ========== 缓存管理 ==========

    def clear_cache(self) -> None:
        """清除所有缓存"""
        self._image_cache.clear()
        self._spritesheet_cache.clear()
        self._config_cache.clear()
        self._loaded_assets.clear()
        self._loading_progress = 0.0

    def remove_from_cache(self, key: str) -> None:
        """从缓存中移除指定资源"""
        self._image_cache.pop(key, None)
        self._spritesheet_cache.pop(key, None)
        self._config_cache.pop(key, None)
        self._loaded_assets.discard(key)

    def get_cache_size(self) -> int:
        """获取缓存中的资源数量"""
        return len(self._loaded_assets)

    # ========== 旗帜图片便捷方法 ==========

    def get_flag_image(self, team: str) -> Optional[pygame.Surface]:
        """
        获取旗帜图片

        Args:
            team: 队伍 ("L" 或 "R")

        Returns:
            pygame.Surface 或 None
        """
        key = 'red_flag' if team == 'L' else 'yellow_flag'
        return self.get_image(key) or self.load_image(key)
