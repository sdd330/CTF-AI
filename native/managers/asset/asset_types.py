"""
资源类型定义和常量配置

包含:
- AssetType 枚举
- 资源目录配置
- 预定义资源路径
- 精灵图配置常量
"""

from pathlib import Path
from enum import Enum


class AssetType(Enum):
    """资源类型"""
    IMAGE = 'image'
    SPRITESHEET = 'spritesheet'
    CONFIG = 'config'
    SOUND = 'sound'
    FONT = 'font'


# 资源目录
ASSETS_DIR = Path(__file__).parent.parent.parent / "assets"

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


def get_asset_path(key: str) -> Path:
    """
    获取资源路径

    Args:
        key: 资源键名

    Returns:
        资源路径
    """
    if key in ASSET_PATHS:
        return ASSETS_DIR / ASSET_PATHS[key]
    # 如果不是预定义的，直接作为相对路径
    return ASSETS_DIR / key
