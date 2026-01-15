"""
地图图层基类和图块数据

职责：
- 定义地图图层的抽象接口（组合模式）
- 提供图块数据的享元实现
"""

import pygame
from abc import ABC, abstractmethod
from typing import Dict


class MapLayer(ABC):
    """
    地图图层接口（组合模式）
    所有地图图层都必须实现这些方法
    """

    @abstractmethod
    def render(self, surface: pygame.Surface, offset_x: int = 0, offset_y: int = 0):
        """渲染图层到 Surface"""
        pass

    @abstractmethod
    def update(self, delta_time: int):
        """更新图层状态"""
        pass

    @abstractmethod
    def destroy(self):
        """销毁图层，释放资源"""
        pass


class TileData:
    """
    图块数据（享元模式）
    缓存图块数据，避免重复创建相同的图块实例
    """

    _cache: Dict[int, 'TileData'] = {}

    def __init__(self, tile_id: int, is_collidable: bool = False):
        """
        初始化图块数据

        Args:
            tile_id: 图块ID
            is_collidable: 是否可碰撞
        """
        self.tile_id = tile_id
        self.is_collidable = is_collidable

    @classmethod
    def get_tile_data(cls, tile_id: int, is_collidable: bool = False) -> 'TileData':
        """
        获取图块数据（享元工厂方法）

        Args:
            tile_id: 图块ID
            is_collidable: 是否可碰撞

        Returns:
            TileData 实例（从缓存获取或新创建）
        """
        key = tile_id * 1000 + (1 if is_collidable else 0)
        if key not in cls._cache:
            cls._cache[key] = cls(tile_id, is_collidable)
        return cls._cache[key]

    @classmethod
    def clear_cache(cls):
        """清空图块数据缓存"""
        cls._cache.clear()
