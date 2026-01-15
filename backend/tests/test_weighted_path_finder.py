"""
WeightedPathFinder 功能测试
验证代码优化后功能是否正常
"""

import pytest
from lib.data_models import Position, Team
from lib.pathfinding_service import WeightedPathFinder


def test_is_valid_position(world, path_finder):
    """测试地图位置验证"""
    w, h = world.map.width, world.map.height

    # 有效位置
    assert path_finder._is_valid_position(Position(0, 0)) is True
    assert path_finder._is_valid_position(Position(5, 5)) is True
    assert path_finder._is_valid_position(Position(w - 1, h - 1)) is True

    # 无效位置
    assert path_finder._is_valid_position(Position(-1, 0)) is False
    assert path_finder._is_valid_position(Position(0, -1)) is False
    assert path_finder._is_valid_position(Position(w, 0)) is False
    assert path_finder._is_valid_position(Position(0, h)) is False


def test_get_enemy_opponents(world, path_finder):
    """测试获取敌方玩家"""
    l_player = world.my_players["L0"]
    l_player.position = Position(1, 1)

    r_player = world.enemy_players["R0"]
    r_player.position = Position(8, 8)

    enemies = path_finder._get_enemy_opponents(Team.LEFT)
    assert len(enemies) >= 1
    assert any(e.name == "R0" for e in enemies)

    enemies2 = path_finder._get_enemy_opponents(Team.RIGHT)
    assert len(enemies2) >= 1
    assert any(e.name == "L0" for e in enemies2)


def test_apply_weight_min_mode(world, path_finder):
    """测试权重应用 - min模式"""
    weight_map = [[1.0] * 5 for _ in range(5)]

    path_finder._apply_weight(weight_map, Position(0, 0), 0.5, 5, 5, mode='min')
    assert weight_map[0][0] == 0.5

    path_finder._apply_weight(weight_map, Position(0, 0), 0.3, 5, 5, mode='min')
    assert weight_map[0][0] == 0.3

    path_finder._apply_weight(weight_map, Position(0, 0), 0.8, 5, 5, mode='min')
    assert weight_map[0][0] == 0.3


def test_apply_weight_max_mode(world, path_finder):
    """测试权重应用 - max模式"""
    weight_map = [[1.0] * 5 for _ in range(5)]

    path_finder._apply_weight(weight_map, Position(0, 0), 1.5, 5, 5, mode='max')
    assert weight_map[0][0] == 1.5

    path_finder._apply_weight(weight_map, Position(0, 0), 2.0, 5, 5, mode='max')
    assert weight_map[0][0] == 2.0

    path_finder._apply_weight(weight_map, Position(0, 0), 1.2, 5, 5, mode='max')
    assert weight_map[0][0] == 2.0


def test_apply_weight_obstacle_protection(world, path_finder):
    """测试权重应用 - 障碍物保护"""
    weight_map = [[1.0] * 5 for _ in range(5)]
    weight_map[2][2] = 0.0

    path_finder._apply_weight(weight_map, Position(2, 2), 0.5, 5, 5, mode='min')
    assert weight_map[2][2] == 0.0


def test_build_safe_weight_map(world, path_finder):
    """测试构建安全权重地图"""
    w, h = world.map.width, world.map.height

    r_player = world.enemy_players["R0"]
    r_player.position = Position(5, 5)

    l_player = world.my_players["L0"]
    l_player.position = Position(1, 1)

    influence_map = path_finder._calculate_enemy_influence_zone(
        Team.LEFT, None, 2, "L队"
    )
    weight_map = path_finder._build_safe_weight_map(influence_map, None, Team.LEFT)

    assert len(weight_map) == w
    assert len(weight_map[0]) == h


def test_find_safe_path(world, path_finder):
    """测试寻找安全路径"""
    l_player = world.my_players["L0"]
    l_player.position = Position(1, 1)

    path, timings = path_finder.find_safe_path(
        Position(1, 1), Position(8, 8), player_name="L0"
    )

    assert isinstance(path, list)
    assert isinstance(timings, dict)
    if path:
        assert path[0] == Position(1, 1)
        assert path[-1] == Position(8, 8)


@pytest.fixture
def path_finder(world):
    """创建 WeightedPathFinder 实例"""
    return WeightedPathFinder(world)
