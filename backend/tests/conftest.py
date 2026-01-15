"""
pytest 共享 fixtures
"""

import pytest
from lib.data_models import Team, Position, TargetArea, PrisonArea
from lib.map_service import GameMap
from lib.game_service import World


@pytest.fixture
def test_map():
    """创建标准测试地图"""
    game_map = GameMap()
    game_map.width = 20
    game_map.height = 20
    game_map.middle_line = 10.0
    game_map.walls = set()
    left_target = {Position(2, 2), Position(2, 3), Position(5, 5), Position(5, 6), Position(6, 5), Position(6, 6)}
    game_map.left_team_target = TargetArea(Team.LEFT, left_target)
    right_target = {Position(17, 17), Position(17, 18), Position(15, 15), Position(15, 16), Position(16, 15), Position(16, 16)}
    game_map.right_team_target = TargetArea(Team.RIGHT, right_target)
    left_prison = {Position(0, 0), Position(0, 1), Position(1, 0), Position(1, 1)}
    game_map.left_team_prison = PrisonArea(Team.LEFT, left_prison)
    right_prison = {Position(18, 18), Position(18, 19), Position(19, 18), Position(19, 19)}
    game_map.right_team_prison = PrisonArea(Team.RIGHT, right_prison)
    return game_map


def _standard_init_req():
    """标准初始化请求"""
    return {
        "myteamName": "L",
        "numPlayers": 3,
        "numFlags": 9,
        "map": {"width": 20, "height": 20, "walls": [], "obstacles": []},
        "myteamTarget": [{"x": 2, "y": 2}, {"x": 2, "y": 3}, {"x": 5, "y": 5}],
        "myteamPrison": [{"x": 0, "y": 0}, {"x": 0, "y": 1}],
        "opponentTarget": [{"x": 17, "y": 17}, {"x": 17, "y": 18}, {"x": 15, "y": 15}],
        "opponentPrison": [{"x": 18, "y": 18}, {"x": 18, "y": 19}]
    }


@pytest.fixture
def uninitialized_world(test_map):
    """创建未初始化的 World 实例（用于测试 init 方法）"""
    return World(test_map)


@pytest.fixture
def world(test_map):
    """创建已初始化的 World 实例"""
    w = World(test_map)
    w.init(_standard_init_req())
    return w


@pytest.fixture
def test_map_with_walls(test_map):
    """创建带障碍物的测试地图"""
    for pos in [Position(4, 5), Position(5, 4), Position(6, 5), Position(7, 6)]:
        test_map.walls.add(pos)
    return test_map
