"""
MapManager 核心功能单元测试
测试地图管理器的初始化、参数设置等基础功能
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from native.managers import MapManager
from native.utils import TILE_SIZE


@pytest.mark.unit
class TestMapManagerCore:
    """MapManager 核心功能测试"""

    def test_singleton_pattern(self):
        """测试单例模式"""
        MapManager._instance = None
        manager1 = MapManager()
        manager2 = MapManager()

        # 应该是同一个实例
        assert manager1 is manager2

        # 清理
        MapManager._instance = None

    def test_initialization(self):
        """测试初始化"""
        MapManager._instance = None
        manager = MapManager()

        assert manager.map_width == 0
        assert manager.map_height == 0
        assert manager.tile_size == TILE_SIZE
        assert manager.game_map is None
        assert len(manager.layers) == 0

        # 清理
        MapManager._instance = None

    def test_set_map_params(self):
        """测试设置地图参数"""
        MapManager._instance = None
        manager = MapManager()

        params = {
            "mapWidth": 30,
            "mapHeight": 20,
            "mapX": 10,
            "mapY": 10,
            "tileSize": 32,
            "centerX": 480,
            "centerY": 320
        }

        manager.set_map_params(params)

        assert manager.map_width == 30
        assert manager.map_height == 20
        assert manager.map_x == 10
        assert manager.map_y == 10
        assert manager.tile_size == 32
        assert manager.center_x == 480
        assert manager.center_y == 320

        # 清理
        if hasattr(manager, 'destroy'):
            manager.destroy()
        MapManager._instance = None

    def test_get_map_params(self):
        """测试获取地图参数"""
        MapManager._instance = None
        manager = MapManager()

        # 先设置参数
        params = {
            "mapWidth": 30,
            "mapHeight": 20,
            "mapX": 10,
            "mapY": 10,
            "tileSize": 32,
            "centerX": 480,
            "centerY": 320
        }
        manager.set_map_params(params)

        # 获取参数
        result = manager.get_map_params()

        assert result["mapWidth"] == 30
        assert result["mapHeight"] == 20
        assert result["mapX"] == 10
        assert result["mapY"] == 10
        assert result["tileSize"] == 32
        assert result["centerX"] == 480
        assert result["centerY"] == 320

        # 清理
        if hasattr(manager, 'destroy'):
            manager.destroy()
        MapManager._instance = None

    def test_update(self):
        """测试更新地图"""
        MapManager._instance = None
        manager = MapManager()

        # 创建 mock 图层
        mock_layer1 = MagicMock()
        mock_layer2 = MagicMock()
        manager.layers = [mock_layer1, mock_layer2]

        # 更新地图
        manager.update(100)

        # 验证所有图层的 update 被调用
        mock_layer1.update.assert_called_once_with(100)
        mock_layer2.update.assert_called_once_with(100)

        # 清理
        MapManager._instance = None

    def test_destroy(self):
        """测试销毁地图管理器"""
        MapManager._instance = None
        manager = MapManager()

        # 创建 mock 图层
        mock_layer = MagicMock()
        mock_layer.destroy = MagicMock()
        manager.layers = [mock_layer]

        # 设置其他属性
        manager.ground_layer = MagicMock()
        manager.level_layer = MagicMock()
        manager.boundary_layer = MagicMock()
        manager.game_map = MagicMock()

        # 销毁管理器
        manager.destroy()

        # 验证图层 destroy 被调用
        mock_layer.destroy.assert_called_once()

        # 验证属性被清空
        assert len(manager.layers) == 0
        assert manager.ground_layer is None
        assert manager.level_layer is None
        assert manager.boundary_layer is None
        assert manager.game_map is None

        # 清理
        MapManager._instance = None
