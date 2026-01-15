"""
边界图层
渲染地图边界线
"""

import pygame
from typing import Tuple
from .map_layer import MapLayer


class BoundaryLayer(MapLayer):
    """
    边界图层
    渲染地图边界线（中心分隔线）
    """

    def __init__(self, center_x: int, start_y: int, end_y: int,
                 color: Tuple[int, int, int] = (0, 0, 0)):
        """
        初始化边界图层

        Args:
            center_x: 中心线X坐标
            start_y: 起始Y坐标
            end_y: 结束Y坐标
            color: 线条颜色
        """
        self.center_x = center_x
        self.start_y = start_y
        self.end_y = end_y
        self.color = color

    def render(self, surface: pygame.Surface, offset_x: int = 0, offset_y: int = 0):
        """渲染边界线"""
        pygame.draw.line(
            surface,
            self.color,
            (self.center_x - offset_x, self.start_y - offset_y),
            (self.center_x - offset_x, self.end_y - offset_y),
            1
        )

    def update(self, delta_time: int):
        """边界不需要更新"""
        pass

    def destroy(self):
        """销毁图层"""
        pass
