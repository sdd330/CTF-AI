"""
关卡图层渲染器
职责：渲染目标区域、监狱区域、障碍物、墙壁
"""

import random
import pygame
from typing import Dict, List, Tuple, Optional, Any


class LevelLayerRenderer:
    """关卡图层渲染器"""

    WALL_TILES = [45, 46, 47, 57, 59, 69, 70, 71]
    TARGET_TILES = [13, 14, 15, 25, 26, 27, 37, 38, 39]
    PRISON_TILES = [97, 98, 99, 109, 110, 111, 121, 122, 123]
    TREE1_TILES = [6, 18, 30, 29, 28]
    TREE2_TILES = [[4, 16], [5, 17]]

    def __init__(self, extract_tile_func, tile_width: int, tile_height: int):
        self._extract_tile = extract_tile_func
        self._tile_width = tile_width
        self._tile_height = tile_height
        self._obstacle_tile_cache: Dict[Tuple[int, int], int] = {}
        self._obstacle2_tile_cache: Dict[Tuple[int, int], List[int]] = {}
        self._debug_logged = False

    def _blit_tile(self, surface: pygame.Surface, tile_id: int,
                   x: int, y: int, offset_x: int, offset_y: int) -> bool:
        """渲染单个图块，返回是否成功"""
        tile = self._extract_tile(tile_id)
        if tile:
            px = offset_x + x * self._tile_width
            py = offset_y + y * self._tile_height
            surface.blit(tile, (px, py))
            return True
        return False

    def render_walls(self, surface: pygame.Surface, walls: List[Dict[str, Any]],
                     offset_x: int = 0, offset_y: int = 0):
        """渲染墙壁"""
        success, failed = 0, 0
        for wall in walls:
            x, y = wall.get("x", 0), wall.get("y", 0)
            tile_id = wall.get("tileId", self.WALL_TILES[0] if self.WALL_TILES else 0)
            if tile_id > 0:
                if self._blit_tile(surface, tile_id, x, y, offset_x, offset_y):
                    success += 1
                else:
                    failed += 1
        self._log_once(f"[LevelLayer] 渲染墙壁: 总数={len(walls)}, 成功={success}, 失败={failed}")

    def render_targets(self, surface: pygame.Surface,
                       left_target: List[Tuple[int, int]],
                       right_target: List[Tuple[int, int]],
                       offset_x: int = 0, offset_y: int = 0):
        """渲染目标区域"""
        self._render_area(surface, left_target, self.TARGET_TILES, offset_x, offset_y)
        self._render_area(surface, right_target, self.TARGET_TILES, offset_x, offset_y)

    def render_prisons(self, surface: pygame.Surface,
                       left_prison: List[Tuple[int, int]],
                       right_prison: List[Tuple[int, int]],
                       offset_x: int = 0, offset_y: int = 0):
        """渲染监狱区域"""
        self._render_area(surface, left_prison, self.PRISON_TILES, offset_x, offset_y)
        self._render_area(surface, right_prison, self.PRISON_TILES, offset_x, offset_y)

    def _render_area(self, surface: pygame.Surface, positions: List[Tuple[int, int]],
                     tile_ids: List[int], offset_x: int, offset_y: int) -> Tuple[int, int]:
        """渲染区域的通用方法"""
        success, failed = 0, 0
        for i, (x, y) in enumerate(positions):
            if i < len(tile_ids):
                if self._blit_tile(surface, tile_ids[i], x, y, offset_x, offset_y):
                    success += 1
                else:
                    failed += 1
        return success, failed

    def render_obstacles(self, surface: pygame.Surface,
                         obstacles1: List[Tuple[int, int]],
                         obstacles2: List[Tuple[int, int]],
                         offset_x: int = 0, offset_y: int = 0):
        """渲染障碍物"""
        for x, y in obstacles1:
            pos = (x, y)
            if pos not in self._obstacle_tile_cache:
                self._obstacle_tile_cache[pos] = random.choice(self.TREE1_TILES)
            self._blit_tile(surface, self._obstacle_tile_cache[pos], x, y, offset_x, offset_y)

        for x, y in obstacles2:
            pos = (x, y)
            if pos not in self._obstacle2_tile_cache:
                self._obstacle2_tile_cache[pos] = random.choice(self.TREE2_TILES)
            tree_tile = self._obstacle2_tile_cache[pos]
            self._blit_tile(surface, tree_tile[0], x, y, offset_x, offset_y)
            self._blit_tile(surface, tree_tile[1], x, y + 1, offset_x, offset_y)

    def clear_obstacle_cache(self):
        """清空障碍物缓存"""
        self._obstacle_tile_cache.clear()
        self._obstacle2_tile_cache.clear()

    def _log_once(self, message: str):
        """只记录一次日志"""
        if not self._debug_logged:
            print(message)
            self._debug_logged = True
