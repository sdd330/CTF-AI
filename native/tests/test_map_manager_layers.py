"""
MapManager 图层功能单元测试
测试地图管理器的图层初始化、渲染等功能
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from native.managers import MapManager


@pytest.mark.unit
class TestMapManagerLayers:
    """MapManager 图层功能测试"""

    @patch('native.managers.map.manager.pygame.image.load')
    def test_initialize_layers(self, mock_image_load):
        """测试初始化图层"""
        MapManager._instance = None
        manager = MapManager()

        # Mock tiles image - 需要设置 get_width 和 get_height 返回值
        mock_tiles_image = MagicMock()
        mock_tiles_image.get_width.return_value = 384  # tiles.png 宽度
        mock_tiles_image.get_height.return_value = 352  # tiles.png 高度
        mock_image_load.return_value = mock_tiles_image

        # 设置地图尺寸
        manager.map_width = 30
        manager.map_height = 20

        # 初始化图层
        manager.initialize_layers(mock_tiles_image)

        # 验证图层被创建
        assert manager.ground_layer is not None
        assert manager.level_layer is not None
        assert len(manager.layers) > 0

        # 清理
        if hasattr(manager, 'destroy'):
            manager.destroy()
        MapManager._instance = None

    def test_initialize_layers_no_map(self):
        """测试未设置地图尺寸时初始化图层"""
        MapManager._instance = None
        manager = MapManager()

        # 不设置地图尺寸，直接初始化图层（应该失败或返回）
        manager.map_width = 0
        manager.map_height = 0
        manager.initialize_layers()

        # 如果没有 tiles image，图层可能不会被创建
        # 这个测试主要检查不会崩溃
        assert manager.layers is not None

        # 清理
        MapManager._instance = None

    def test_generate_map(self):
        """测试生成地图数据"""
        MapManager._instance = None
        manager = MapManager()

        # 先设置地图尺寸
        manager.map_width = 30
        manager.map_height = 20

        walls = [{"x": 0, "y": 0, "tileId": 45}]
        obstacles = [(5, 5), (10, 10)]
        left_target = [(2, 10), (2, 11)]
        right_target = [(28, 10), (28, 11)]
        left_prison = [(1, 10)]
        right_prison = [(29, 10)]

        manager.generate_map(
            walls, obstacles, left_target, right_target, left_prison, right_prison
        )

        # 验证游戏地图被创建
        assert manager.game_map is not None

        # 验证关卡图层的墙壁被设置
        if manager.level_layer:
            assert len(manager.level_layer.walls) == 1

        # 清理
        if hasattr(manager, 'destroy'):
            manager.destroy()
        MapManager._instance = None

    def test_render_map(self):
        """测试渲染地图"""
        MapManager._instance = None
        manager = MapManager()

        # 创建 mock surface
        mock_surface = MagicMock()

        # 创建 mock 图层（render_map 会调用 ground_layer 和 level_layer）
        mock_ground_layer = MagicMock()
        mock_ground_layer.render = MagicMock()
        mock_level_layer = MagicMock()
        mock_level_layer.set_walls = MagicMock()
        mock_level_layer.render_walls = MagicMock()

        manager.ground_layer = mock_ground_layer
        manager.level_layer = mock_level_layer

        # 渲染地图
        manager.render_map(mock_surface, offset_x=0, offset_y=0)

        # 验证图层 render 被调用
        mock_ground_layer.render.assert_called_once_with(mock_surface, 0, 0)
        mock_level_layer.render_walls.assert_called_once_with(mock_surface, 0, 0)

        # 清理
        MapManager._instance = None

    def test_render_targets_and_prisons(self):
        """测试渲染目标区域和监狱"""
        MapManager._instance = None
        manager = MapManager()

        # 创建 mock surface
        mock_surface = MagicMock()

        # 创建 mock 关卡图层
        mock_level_layer = MagicMock()
        mock_level_layer.render_targets = MagicMock()
        mock_level_layer.render_prisons = MagicMock()
        manager.level_layer = mock_level_layer

        left_target = [(2, 10)]
        right_target = [(28, 10)]
        left_prison = [(1, 10)]
        right_prison = [(29, 10)]

        manager.render_targets_and_prisons(
            mock_surface, left_target, right_target, left_prison, right_prison
        )

        # 验证方法被调用
        mock_level_layer.render_targets.assert_called_once()
        mock_level_layer.render_prisons.assert_called_once()

        # 清理
        MapManager._instance = None
