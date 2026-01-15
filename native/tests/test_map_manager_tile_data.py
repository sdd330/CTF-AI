"""
TileData 和 MapLayer 单元测试
测试图块数据和图层接口
"""

import pytest
from native.managers import MapManager, MapLayer, TileData
from native.utils import TILE_SIZE


@pytest.mark.unit
class TestTileData:
    """TileData 测试"""

    def test_tile_data_creation(self):
        """测试图块数据创建"""
        TileData._cache.clear()
        tile = TileData(1, False)
        assert tile.tile_id == 1
        assert tile.is_collidable is False

    def test_get_tile_data_flyweight(self):
        """测试享元模式"""
        TileData._cache.clear()
        tile1 = TileData.get_tile_data(1, False)
        tile2 = TileData.get_tile_data(1, False)

        # 应该是同一个实例
        assert tile1 is tile2

    def test_get_tile_data_different_keys(self):
        """测试不同键返回不同实例"""
        TileData._cache.clear()
        tile1 = TileData.get_tile_data(1, False)
        tile2 = TileData.get_tile_data(1, True)
        tile3 = TileData.get_tile_data(2, False)

        # 应该是不同的实例
        assert tile1 is not tile2
        assert tile1 is not tile3
        assert tile2 is not tile3


@pytest.mark.unit
class TestMapLayer:
    """MapLayer 接口测试"""

    def test_map_layer_interface(self):
        """测试 MapLayer 接口方法存在"""
        # 创建一个简单的实现
        class TestLayer(MapLayer):
            def render(self, surface, offset_x=0, offset_y=0):
                pass

            def update(self, delta_time):
                pass

            def destroy(self):
                pass

        layer = TestLayer()
        assert isinstance(layer, MapLayer)
