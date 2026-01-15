"""
MapManager 单元测试
测试地图管理器的所有功能
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from native.managers import MapManager, MapLayer, TileData
from native.map.map import GameMap, Position
from native.utils import Team, TILE_SIZE


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


@pytest.mark.unit
class TestMapManager:
    """MapManager 测试"""
    
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
