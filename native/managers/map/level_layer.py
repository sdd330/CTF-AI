"""
关卡图层
使用组合模式，集成 TileExtractor 和 LevelLayerRenderer
"""

import pygame
from typing import Dict, List, Tuple, Optional, Any

from .map_layer import MapLayer
from .tile_extractor import TileExtractorMixin
from .level_layer_renderer import LevelLayerRenderer


class LevelLayer(MapLayer, TileExtractorMixin):
    """
    关卡图层（组合模式）
    渲染墙壁、障碍物、目标区域、监狱等
    """

    def __init__(self, tiles_image: pygame.Surface, map_width: int,
                 map_height: int, tile_size: int = 32):
        """
        初始化关卡图层

        Args:
            tiles_image: tiles.png 图片 Surface
            map_width: 地图宽度（格子数）
            map_height: 地图高度（格子数）
            tile_size: 瓦片大小
        """
        # 初始化 TileExtractor
        self.init_tile_extractor(tiles_image, tile_size, tile_size)

        self.map_width = map_width
        self.map_height = map_height
        self.walls: List[Dict[str, Any]] = []

        # 创建渲染器
        self._renderer = LevelLayerRenderer(
            self._extract_tile, tile_size, tile_size
        )

    def set_walls(self, walls: List[Dict[str, Any]]):
        """设置墙壁列表"""
        self.walls = walls

    def render(self, surface: pygame.Surface, offset_x: int = 0, offset_y: int = 0):
        """渲染图层（由外部调用具体渲染方法）"""
        pass

    def render_walls(self, surface: pygame.Surface, offset_x: int = 0, offset_y: int = 0):
        """渲染墙壁"""
        self._renderer.render_walls(surface, self.walls, offset_x, offset_y)

    def render_targets(self, surface: pygame.Surface,
                       left_target: List[Tuple[int, int]],
                       right_target: List[Tuple[int, int]],
                       offset_x: int = 0, offset_y: int = 0):
        """渲染目标区域"""
        self._renderer.render_targets(surface, left_target, right_target, offset_x, offset_y)

    def render_prisons(self, surface: pygame.Surface,
                       left_prison: List[Tuple[int, int]],
                       right_prison: List[Tuple[int, int]],
                       offset_x: int = 0, offset_y: int = 0):
        """渲染监狱区域"""
        self._renderer.render_prisons(surface, left_prison, right_prison, offset_x, offset_y)

    def render_obstacles(self, surface: pygame.Surface,
                         obstacles1: List[Tuple[int, int]],
                         obstacles2: List[Tuple[int, int]],
                         offset_x: int = 0, offset_y: int = 0):
        """渲染障碍物"""
        self._renderer.render_obstacles(surface, obstacles1, obstacles2, offset_x, offset_y)

    def is_wall(self, x: int, y: int) -> bool:
        """检查位置是否是墙"""
        return any(w.get("x") == x and w.get("y") == y for w in self.walls)

    def get_tile_at(self, x: int, y: int) -> Optional[Dict[str, Any]]:
        """获取指定位置的图块信息"""
        if not (0 <= x < self.map_width and 0 <= y < self.map_height):
            return None
        for wall in self.walls:
            if wall.get("x") == x and wall.get("y") == y:
                return {"gid": wall.get("tileId", 0), "x": x, "y": y, "is_wall": True}
        return None

    def update(self, delta_time: int):
        """关卡图层不需要更新"""
        pass

    def destroy(self):
        """销毁图层"""
        self.clear_tile_cache()
