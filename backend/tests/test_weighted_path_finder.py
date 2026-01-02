"""
WeightedPathFinder 功能测试
验证代码优化后功能是否正常
"""

import unittest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.data_models import Position, Team
from lib.map_service import GameMap
from lib.game_service import World
from lib.pathfinding_service import WeightedPathFinder


class TestWeightedPathFinder(unittest.TestCase):
    """WeightedPathFinder 功能测试"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建一个简单的测试地图
        self.test_map = GameMap()
        self.test_map.width = 10
        self.test_map.height = 10
        self.test_map.walls = set()
        
        # 创建World对象
        self.world = World(self.test_map)
        
        # 初始化World（需要基本的地图配置）
        init_req = {
            "map": {
                "width": 10,
                "height": 10,
                "walls": [],
                "targets": {
                    "L": [[0, 0], [0, 1]],
                    "R": [[9, 9], [9, 8]]
                },
                "prisons": {
                    "L": [[0, 2]],
                    "R": [[9, 7]]
                }
            },
            "team": {
                "name": "L",
                "numPlayers": 2,
                "numFlags": 9
            }
        }
        self.world.init(init_req)
        
        # 创建WeightedPathFinder
        self.path_finder = WeightedPathFinder(self.world)
    
    def test_init_weight_map(self):
        """测试权重地图初始化"""
        weight_map = self.path_finder._init_weight_map(5, 5, default_value=1.0)
        self.assertEqual(len(weight_map), 5)
        self.assertEqual(len(weight_map[0]), 5)
        self.assertEqual(weight_map[0][0], 1.0)
        
        weight_map2 = self.path_finder._init_weight_map(3, 3, default_value=0.5)
        self.assertEqual(weight_map2[0][0], 0.5)
    
    def test_is_valid_map_position(self):
        """测试地图位置验证"""
        # 有效位置
        self.assertTrue(self.path_finder._is_valid_map_position(Position(0, 0), 10, 10))
        self.assertTrue(self.path_finder._is_valid_map_position(Position(5, 5), 10, 10))
        self.assertTrue(self.path_finder._is_valid_map_position(Position(9, 9), 10, 10))
        
        # 无效位置
        self.assertFalse(self.path_finder._is_valid_map_position(Position(-1, 0), 10, 10))
        self.assertFalse(self.path_finder._is_valid_map_position(Position(0, -1), 10, 10))
        self.assertFalse(self.path_finder._is_valid_map_position(Position(10, 0), 10, 10))
        self.assertFalse(self.path_finder._is_valid_map_position(Position(0, 10), 10, 10))
    
    def test_get_enemy_opponents(self):
        """测试获取敌方玩家"""
        # 添加一些玩家
        from lib.data_models import Player
        
        # 添加L队玩家
        l_player = Player("L0", Position(1, 1), Team.LEFT)
        self.world.players["L0"] = l_player
        
        # 添加R队玩家
        r_player = Player("R0", Position(8, 8), Team.RIGHT)
        self.world.players["R0"] = r_player
        
        # 获取L队的敌人（应该是R队玩家）
        enemies = self.path_finder._get_enemy_opponents(Team.LEFT)
        self.assertEqual(len(enemies), 1)
        self.assertEqual(enemies[0].name, "R0")
        
        # 获取R队的敌人（应该是L队玩家）
        enemies2 = self.path_finder._get_enemy_opponents(Team.RIGHT)
        self.assertEqual(len(enemies2), 1)
        self.assertEqual(enemies2[0].name, "L0")
    
    def test_apply_weight_to_map_min_mode(self):
        """测试权重应用 - min模式"""
        weight_map = self.path_finder._init_weight_map(5, 5, default_value=1.0)
        
        # 应用较小权重（应该取min）
        self.path_finder._apply_weight_to_map(weight_map, Position(0, 0), 0.5, 5, 5, mode='min')
        self.assertEqual(weight_map[0][0], 0.5)
        
        # 再次应用更小权重
        self.path_finder._apply_weight_to_map(weight_map, Position(0, 0), 0.3, 5, 5, mode='min')
        self.assertEqual(weight_map[0][0], 0.3)
        
        # 应用更大权重（应该保持较小值）
        self.path_finder._apply_weight_to_map(weight_map, Position(0, 0), 0.8, 5, 5, mode='min')
        self.assertEqual(weight_map[0][0], 0.3)
    
    def test_apply_weight_to_map_max_mode(self):
        """测试权重应用 - max模式"""
        weight_map = self.path_finder._init_weight_map(5, 5, default_value=1.0)
        
        # 应用较大权重（应该取max）
        self.path_finder._apply_weight_to_map(weight_map, Position(0, 0), 1.5, 5, 5, mode='max')
        self.assertEqual(weight_map[0][0], 1.5)
        
        # 再次应用更大权重
        self.path_finder._apply_weight_to_map(weight_map, Position(0, 0), 2.0, 5, 5, mode='max')
        self.assertEqual(weight_map[0][0], 2.0)
        
        # 应用更小权重（应该保持较大值）
        self.path_finder._apply_weight_to_map(weight_map, Position(0, 0), 1.2, 5, 5, mode='max')
        self.assertEqual(weight_map[0][0], 2.0)
    
    def test_apply_weight_to_map_obstacle_protection(self):
        """测试权重应用 - 障碍物保护"""
        weight_map = self.path_finder._init_weight_map(5, 5, default_value=1.0)
        
        # 设置障碍物
        weight_map[2][2] = 0.0
        
        # 尝试覆盖障碍物（应该失败）
        self.path_finder._apply_weight_to_map(weight_map, Position(2, 2), 0.5, 5, 5, mode='min')
        self.assertEqual(weight_map[2][2], 0.0)  # 应该保持为0
    
    def test_build_safe_weight_map(self):
        """测试构建安全权重地图"""
        from lib.data_models import Player
        
        # 添加R队玩家作为敌人
        r_player = Player("R0", Position(5, 5), Team.RIGHT)
        self.world.players["R0"] = r_player
        
        # 添加L队玩家
        l_player = Player("L0", Position(1, 1), Team.LEFT)
        self.world.players["L0"] = l_player
        
        # 构建安全权重地图
        influence_map = self.path_finder._calculate_enemy_influence_zone(Team.LEFT)
        weight_map = self.path_finder._build_safe_weight_map(influence_map, None, Team.LEFT)
        
        # 验证权重地图已创建
        self.assertEqual(len(weight_map), 10)
        self.assertEqual(len(weight_map[0]), 10)
        
        # 验证敌人附近权重较低
        # 注意：由于影响区域计算，敌人附近的权重应该小于1.0


if __name__ == '__main__':
    unittest.main()
