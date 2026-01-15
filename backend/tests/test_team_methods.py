"""
Team 类面向对象方法的单元测试
测试 Team.get_enemy() 和 Team.from_name() 方法
"""

import pytest
from lib.data_models import Team


def test_get_enemy_left():
    """测试 LEFT 队伍的 get_enemy() 方法"""
    assert Team.LEFT.get_enemy() == Team.RIGHT


def test_get_enemy_right():
    """测试 RIGHT 队伍的 get_enemy() 方法"""
    assert Team.RIGHT.get_enemy() == Team.LEFT


def test_get_enemy_symmetry():
    """测试 get_enemy() 的对称性"""
    assert Team.LEFT.get_enemy().get_enemy() == Team.LEFT
    assert Team.RIGHT.get_enemy().get_enemy() == Team.RIGHT


def test_from_name_left():
    """测试 from_name() 方法 - L"""
    assert Team.from_name("L") == Team.LEFT


def test_from_name_right():
    """测试 from_name() 方法 - R"""
    assert Team.from_name("R") == Team.RIGHT


def test_from_name_invalid():
    """测试 from_name() 方法 - 无效输入"""
    assert Team.from_name("X") is None
    assert Team.from_name("") is None
    assert Team.from_name("left") is None
    assert Team.from_name("right") is None


def test_from_name_case_sensitive():
    """测试 from_name() 方法 - 大小写敏感"""
    assert Team.from_name("l") is None
    assert Team.from_name("r") is None


def test_team_enum_values():
    """测试 Team 枚举值"""
    assert Team.LEFT.value == "L"
    assert Team.RIGHT.value == "R"
