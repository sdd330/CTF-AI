"""
背景图层

职责：
- 使用 backgroundTiles 随机填充整个地图
- 渲染地图背景
"""

import random
import pygame
from typing import Dict

from .map_layer import MapLayer
from .tile_extractor import TileExtractorMixin


class GroundLayer(MapLayer, TileExtractorMixin):
    """
    背景图层
    使用 backgroundTiles 随机填充整个地图
    """

    # 背景图块ID列表（加权随机，数字越多出现概率越高）
    BACKGROUND_TILES = [
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        2, 2, 2, 2, 2, 2, 2, 2,
        3, 44
    ]

    def __init__(
        self,
        tiles_image: pygame.Surface,
        map_width: int,
        map_height: int,
        tile_size: int = 32
    ):
        """
        初始化背景图层

        Args:
            tiles_image: tiles.png 图片 Surface（spritesheet）
            map_width: 地图宽度（格子数）
            map_height: 地图高度（格子数）
            tile_size: 瓦片大小（默认 32x32）
        """
        self.map_width = map_width
        self.map_height = map_height

        # 初始化图块提取器
        self.init_tile_extractor(tiles_image, tile_size, tile_size)

        # 生成随机背景图块
        self.generated_tiles = self._generate_random_tiles()

        # 预提取所有使用的瓦片（缓存）
        for tile_index in set(self.BACKGROUND_TILES):
            self._extract_tile(tile_index)

    def _generate_random_tiles(self) -> Dict[tuple, int]:
        """
        生成随机背景图块

        Returns:
            位置到图块ID的映射字典
        """
        tiles = {}
        for y in range(self.map_height):
            for x in range(self.map_width):
                tile_index = random.choice(self.BACKGROUND_TILES)
                tiles[(x, y)] = tile_index
        return tiles

    def render(self, surface: pygame.Surface, offset_x: int = 0, offset_y: int = 0):
        """
        渲染背景图层

        Args:
            surface: pygame Surface 对象
            offset_x: X偏移量（地图起始位置）
            offset_y: Y偏移量（地图起始位置）
        """
        for (x, y), tile_index in self.generated_tiles.items():
            tile = self._extract_tile(tile_index)
            if tile:
                pixel_x = offset_x + x * self._tile_width
                pixel_y = offset_y + y * self._tile_height
                surface.blit(tile, (pixel_x, pixel_y))

    def update(self, delta_time: int):
        """背景图层不需要更新"""
        pass

    def destroy(self):
        """销毁图层，释放资源"""
        self.generated_tiles = None
        self.clear_tile_cache()
