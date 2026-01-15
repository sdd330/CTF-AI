"""
资源管理器 - 重导出模块
为保持向后兼容性，从 asset 子模块重导出
"""

from .asset import (
    AssetType,
    ASSETS_DIR,
    ASSET_PATHS,
    SPRITE_SIZE,
    CHARACTERS_PER_ROW,
    CHARACTER_ROWS,
    FRAMES_PER_CHARACTER,
    FRAMES_PER_DIRECTION,
    get_asset_path,
    AssetCache,
    ImageLoader,
    SpriteLoader,
    AssetManager,
)

__all__ = [
    'AssetType',
    'ASSETS_DIR',
    'ASSET_PATHS',
    'SPRITE_SIZE',
    'CHARACTERS_PER_ROW',
    'CHARACTER_ROWS',
    'FRAMES_PER_CHARACTER',
    'FRAMES_PER_DIRECTION',
    'get_asset_path',
    'AssetCache',
    'ImageLoader',
    'SpriteLoader',
    'AssetManager',
]
