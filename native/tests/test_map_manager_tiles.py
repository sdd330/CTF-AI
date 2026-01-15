"""
MapManager 图块查询功能单元测试
测试地图管理器的图块获取、墙壁检查等功能
"""

import pytest
from unittest.mock import Mock, MagicMock
from native.managers import MapManager


@pytest.mark.unit
class TestMapManagerTiles:
    """MapManager 图块查询测试"""

    def test_get_tile_at(self):
        """测试获取图块（像素坐标）"""
        MapManager._instance = None
        manager = MapManager()

        # 创建 mock 关卡图层
        mock_level_layer = MagicMock()
        mock_level_layer.get_tile_at = MagicMock(return_value={"gid": 1, "x": 5, "y": 5})
        manager.level_layer = mock_level_layer
        manager.tile_size = 32

        # 获取图块（像素坐标 160, 160 对应格子坐标 5, 5）
        result = manager.get_tile_at(160, 160)

        # 验证方法被调用
        mock_level_layer.get_tile_at.assert_called_once_with(5, 5)
        assert result is not None

        # 清理
        MapManager._instance = None

    def test_get_tile_at_grid(self):
        """测试获取图块（格子坐标）"""
        MapManager._instance = None
        manager = MapManager()

        # 创建 mock 关卡图层
        mock_level_layer = MagicMock()
        mock_level_layer.get_tile_at = MagicMock(return_value={"gid": 1, "x": 5, "y": 5})
        manager.level_layer = mock_level_layer

        # 获取图块
        result = manager.get_tile_at_grid(5, 5)

        # 验证方法被调用
        mock_level_layer.get_tile_at.assert_called_once_with(5, 5)
        assert result is not None

        # 清理
        MapManager._instance = None

    def test_get_tile_at_no_layer(self):
        """测试没有图层时获取图块"""
        MapManager._instance = None
        manager = MapManager()
        manager.level_layer = None

        result = manager.get_tile_at(100, 100)
        assert result is None

        result = manager.get_tile_at_grid(5, 5)
        assert result is None

        # 清理
        MapManager._instance = None

    def test_is_wall(self):
        """测试检查是否是墙"""
        MapManager._instance = None
        manager = MapManager()

        # 创建 mock 关卡图层
        mock_level_layer = MagicMock()
        mock_level_layer.is_wall = MagicMock(return_value=True)
        manager.level_layer = mock_level_layer

        result = manager.is_wall(5, 5)

        assert result is True
        mock_level_layer.is_wall.assert_called_once_with(5, 5)

        # 清理
        MapManager._instance = None

    def test_is_wall_no_layer(self):
        """测试没有图层时检查是否是墙"""
        MapManager._instance = None
        manager = MapManager()
        manager.level_layer = None

        result = manager.is_wall(5, 5)
        assert result is False

        # 清理
        MapManager._instance = None


@pytest.mark.unit
class TestLevelLayer:
    """LevelLayer 测试"""

    def test_level_layer_set_walls(self, mock_pygame):
        """测试设置墙壁"""
        from native.managers.map_manager import LevelLayer

        # Mock tiles image
        mock_tiles_image = MagicMock()
        mock_tiles_image.get_width.return_value = 384
        mock_tiles_image.get_height.return_value = 352

        layer = LevelLayer(mock_tiles_image, 30, 20, 32)

        walls = [{"x": 0, "y": 0, "tileId": 45}]
        layer.set_walls(walls)

        assert len(layer.walls) == 1
        assert layer.walls[0]["x"] == 0
        assert layer.walls[0]["y"] == 0


@pytest.mark.unit
class TestBoundaryLayer:
    """BoundaryLayer 测试"""

    def test_boundary_layer_creation(self):
        """测试边界图层创建"""
        from native.managers.map_manager import BoundaryLayer

        layer = BoundaryLayer(480, 0, 640, (0, 0, 0))

        assert layer is not None
        assert layer.center_x == 480
        assert layer.start_y == 0
        assert layer.end_y == 640

    def test_boundary_layer_render(self, mock_pygame):
        """测试边界图层渲染"""
        from native.managers.map_manager import BoundaryLayer
        import pygame

        layer = BoundaryLayer(480, 0, 640, (0, 0, 0))

        # Mock surface
        mock_surface = MagicMock()

        # 渲染
        layer.render(mock_surface, offset_x=0, offset_y=0)

        # 验证 draw.line 被调用
        pygame.draw.line.assert_called_once()
