"""
图块提取器混入类

职责：
- 提供从 spritesheet 提取图块的通用方法
- 管理图块缓存
"""

import pygame
from typing import Dict, Optional


class TileExtractorMixin:
    """
    图块提取器混入类
    为需要从 tiles.png 提取图块的图层提供共享实现
    """

    # tiles.png 的布局：12 列 x 11 行 = 132 个瓦片
    TILES_PER_ROW = 12

    def init_tile_extractor(
        self,
        tiles_image: pygame.Surface,
        tile_width: int = 32,
        tile_height: int = 32
    ):
        """
        初始化图块提取器

        Args:
            tiles_image: tiles.png 图片 Surface（spritesheet）
            tile_width: 瓦片宽度（默认 32）
            tile_height: 瓦片高度（默认 32）
        """
        self._tiles_image = tiles_image
        self._tile_width = tile_width
        self._tile_height = tile_height
        self._tile_cache: Dict[int, Optional[pygame.Surface]] = {}
        self._extract_error_logged = False

    def _extract_tile(self, tile_index: int) -> Optional[pygame.Surface]:
        """
        从 tiles.png 中提取指定索引的瓦片

        Args:
            tile_index: 瓦片索引（1-based，与 Tiled 编辑器一致）

        Returns:
            瓦片 Surface 或 None（如果提取失败）
        """
        if tile_index in self._tile_cache:
            return self._tile_cache[tile_index]

        # tile_index 从 1 开始，转换为 0-based
        index = tile_index - 1

        # 计算瓦片在 spritesheet 中的位置
        row = index // self.TILES_PER_ROW
        col = index % self.TILES_PER_ROW

        # 计算像素坐标
        x = col * self._tile_width
        y = row * self._tile_height

        # 检查边界
        img_width = self._tiles_image.get_width()
        img_height = self._tiles_image.get_height()

        if x + self._tile_width <= img_width and y + self._tile_height <= img_height:
            try:
                tile = self._tiles_image.subsurface(
                    (x, y, self._tile_width, self._tile_height)
                )
                self._tile_cache[tile_index] = tile
                return tile
            except Exception as e:
                self._log_extract_error(tile_index, row, col, x, y, str(e))
        else:
            self._log_boundary_error(tile_index, row, col, x, y, img_width, img_height)

        return None

    def _log_extract_error(
        self,
        tile_index: int,
        row: int,
        col: int,
        x: int,
        y: int,
        error: str
    ):
        """记录图块提取错误（仅记录一次）"""
        if not self._extract_error_logged:
            class_name = self.__class__.__name__
            print(
                f"[{class_name}] 提取 tile {tile_index} 失败: {error}, "
                f"位置=(row={row}, col={col}, pixel=({x}, {y}))"
            )
            self._extract_error_logged = True

    def _log_boundary_error(
        self,
        tile_index: int,
        row: int,
        col: int,
        x: int,
        y: int,
        img_width: int,
        img_height: int
    ):
        """记录边界检查错误（仅记录一次）"""
        if not self._extract_error_logged:
            class_name = self.__class__.__name__
            print(
                f"[{class_name}] tile {tile_index} 超出边界: "
                f"位置=(row={row}, col={col}, pixel=({x}, {y})), "
                f"图片尺寸=({img_width}, {img_height})"
            )
            self._extract_error_logged = True

    def clear_tile_cache(self):
        """清空图块缓存"""
        self._tile_cache.clear()
