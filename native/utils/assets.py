"""
资源路径管理
"""

import os
from pathlib import Path

# 获取资源目录路径
ASSETS_DIR = Path(__file__).parent.parent / "assets"

# 资源文件路径
CHARACTERS_SPRITESHEET = ASSETS_DIR / "characters.png"
CHARACTERS_RED_FLAG = ASSETS_DIR / "characters_red_flag.png"
CHARACTERS_YELLOW_FLAG = ASSETS_DIR / "characters_yellow_flag.png"
RED_FLAG_IMG = ASSETS_DIR / "red_flag_32_32.png"
YELLOW_FLAG_IMG = ASSETS_DIR / "yellow_flag_32_32.png"
TILES_SPRITESHEET = ASSETS_DIR / "tiles.png"

# 精灵图配置
SPRITE_SIZE = 32  # 每个精灵的大小（像素）
CHARACTERS_PER_ROW = 4  # 每行精灵数量（实际 sprite sheet 每行只有 4 个精灵）
CHARACTER_ROWS = 18  # 精灵行数（实际 sprite sheet 有 18 行）

# 角色精灵索引计算
# 每个角色有 12 帧，分为 3 行，每行 4 个精灵（4 个方向）
# 每个方向有 3 帧动画（frame 0, 1, 2）
# 每个角色占 3 行：行0=第1帧, 行1=第2帧, 行2=第3帧
FRAMES_PER_CHARACTER = 12
FRAMES_PER_DIRECTION = 3  # 每个方向有 3 帧动画

def get_character_frame_index(sprite_choice: int, direction: str, frame: int = 0) -> tuple[int, int]:
    """
    获取角色精灵帧的坐标
    
    根据 frontend 实现：
    - frames: [(i - 1) * 12 + j, (i - 1) * 12 + j + 4, (i - 1) * 12 + j + 8]
    - 对于角色1 (i=1), 方向 left (j=0): 帧 0, 4, 8
    - 对于角色1, 方向 down (j=1): 帧 1, 5, 9
    - 对于角色1, 方向 up (j=2): 帧 2, 6, 10
    - 对于角色1, 方向 right (j=3): 帧 3, 7, 11
    
    Sprite sheet 布局（每行4个精灵）：
    - 行0: left(0), down(1), up(2), right(3) - 第1帧
    - 行1: left(4), down(5), up(6), right(7) - 第2帧
    - 行2: left(8), down(9), up(10), right(11) - 第3帧
    
    Args:
        sprite_choice: 角色选择（1-8）
        direction: 方向 ("up", "down", "left", "right")
        frame: 帧数（0-2，用于动画）
    
    Returns:
        (x, y) 在精灵图中的坐标（像素）
    """
    # 方向映射到列（每行 4 个精灵）
    # 根据 frontend: dirChoices = ['left', 'down', 'up', 'right']
    direction_map = {
        "left": 0,   # 列 0: 向左
        "down": 1,   # 列 1: 向下
        "up": 2,     # 列 2: 向上
        "right": 3   # 列 3: 向右
    }
    
    col = direction_map.get(direction, 0)
    
    # 根据 frontend 的帧索引计算：
    # 帧索引 = (sprite_choice - 1) * 12 + direction_index + frame * 4
    # 转换为行列：
    # row = 帧索引 // 4
    # col = 帧索引 % 4
    
    # 每个角色有 12 帧，占 3 行（12 / 4 = 3）
    # 每个角色从 base_frame = (sprite_choice - 1) * 12 开始
    base_frame = (sprite_choice - 1) * 12
    direction_index = col
    frame_index = base_frame + direction_index + frame * 4
    
    # 转换为行列坐标
    row = frame_index // 4
    col = frame_index % 4
    
    # 限制在有效范围内
    row = min(row, CHARACTER_ROWS - 1)
    col = min(col, CHARACTERS_PER_ROW - 1)
    
    x = col * SPRITE_SIZE
    y = row * SPRITE_SIZE
    
    return (x, y)

def get_flag_image_path(team: str) -> Path:
    """
    获取旗帜图片路径
    
    Args:
        team: 队伍 ("L" 或 "R")
    
    Returns:
        图片路径
    """
    if team == "L":
        return RED_FLAG_IMG
    else:
        return YELLOW_FLAG_IMG

