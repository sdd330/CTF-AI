"""
Team 类面向对象方法的单元测试
测试 Team.get_enemy() 和 Team.from_name() 方法
"""

import unittest
from lib.data_models import Team


class TestTeamMethods(unittest.TestCase):
    """Team 类方法测试"""
    
    def test_get_enemy_left(self):
        """测试 LEFT 队伍的 get_enemy() 方法"""
        self.assertEqual(Team.LEFT.get_enemy(), Team.RIGHT)
    
    def test_get_enemy_right(self):
        """测试 RIGHT 队伍的 get_enemy() 方法"""
        self.assertEqual(Team.RIGHT.get_enemy(), Team.LEFT)
    
    def test_get_enemy_symmetry(self):
        """测试 get_enemy() 的对称性"""
        self.assertEqual(Team.LEFT.get_enemy().get_enemy(), Team.LEFT)
        self.assertEqual(Team.RIGHT.get_enemy().get_enemy(), Team.RIGHT)
    
    def test_from_name_left(self):
        """测试 from_name() 方法 - L"""
        self.assertEqual(Team.from_name("L"), Team.LEFT)
    
    def test_from_name_right(self):
        """测试 from_name() 方法 - R"""
        self.assertEqual(Team.from_name("R"), Team.RIGHT)
    
    def test_from_name_invalid(self):
        """测试 from_name() 方法 - 无效输入"""
        self.assertIsNone(Team.from_name("X"))
        self.assertIsNone(Team.from_name(""))
        self.assertIsNone(Team.from_name("left"))
        self.assertIsNone(Team.from_name("right"))
    
    def test_from_name_case_sensitive(self):
        """测试 from_name() 方法 - 大小写敏感"""
        self.assertIsNone(Team.from_name("l"))
        self.assertIsNone(Team.from_name("r"))
    
    def test_team_enum_values(self):
        """测试 Team 枚举值"""
        self.assertEqual(Team.LEFT.value, "L")
        self.assertEqual(Team.RIGHT.value, "R")


if __name__ == '__main__':
    unittest.main()

