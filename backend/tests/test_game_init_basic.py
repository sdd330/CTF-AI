"""
World 初始化基础测试
测试 my_team_name、玩家和旗帜的创建
"""

import pytest
from lib.data_models import Team, Position


def _make_init_req(team="L", num_players=2, num_flags=2):
    """创建初始化请求"""
    return {
        "myteamName": team,
        "numPlayers": num_players,
        "numFlags": num_flags,
        "map": {"width": 20, "height": 20, "walls": [], "obstacles": []},
        "myteamTarget": [{"x": 2, "y": 2}],
        "myteamPrison": [{"x": 0, "y": 0}],
        "opponentTarget": [{"x": 17, "y": 17}],
        "opponentPrison": [{"x": 18, "y": 18}]
    }


def test_init_sets_my_team_name(uninitialized_world):
    """测试初始化设置 my_team_name"""
    uninitialized_world.init(_make_init_req())
    assert uninitialized_world.my_team_name == "L"


def test_init_creates_players_from_num_players(uninitialized_world):
    """测试根据 numPlayers 创建玩家"""
    uninitialized_world.init(_make_init_req(num_players=3))

    assert len(uninitialized_world.my_players) == 3
    assert len(uninitialized_world.enemy_players) == 3

    # 检查己方玩家
    for i in range(3):
        assert f"L{i}" in uninitialized_world.my_players
        assert uninitialized_world.my_players[f"L{i}"].team == Team.LEFT

    # 检查敌方玩家
    for i in range(3):
        assert f"R{i}" in uninitialized_world.enemy_players
        assert uninitialized_world.enemy_players[f"R{i}"].team == Team.RIGHT


def test_init_creates_flags_from_num_flags(uninitialized_world):
    """测试根据 numFlags 创建旗帜"""
    uninitialized_world.init(_make_init_req(num_flags=5))

    assert len(uninitialized_world.my_flags) == 5
    assert len(uninitialized_world.enemy_flags) == 5

    # 检查己方旗帜
    for i in range(5):
        flag_id = f"FLAG_L_{i}"
        assert flag_id in uninitialized_world.my_flags
        assert uninitialized_world.my_flags[flag_id].team == Team.LEFT

    # 检查敌方旗帜
    for i in range(5):
        flag_id = f"FLAG_R_{i}"
        assert flag_id in uninitialized_world.enemy_flags
        assert uninitialized_world.enemy_flags[flag_id].team == Team.RIGHT


def test_init_players_have_base_area(uninitialized_world):
    """测试初始化的玩家有基地区域"""
    uninitialized_world.init(_make_init_req())

    l0 = uninitialized_world.my_players["L0"]
    assert l0.base_area is not None

    r0 = uninitialized_world.enemy_players["R0"]
    assert r0.base_area is not None


def test_init_for_right_team(uninitialized_world):
    """测试为 R 队初始化"""
    req = {
        "myteamName": "R",
        "numPlayers": 2,
        "numFlags": 2,
        "map": {"width": 20, "height": 20, "walls": [], "obstacles": []},
        "myteamTarget": [{"x": 17, "y": 17}],
        "myteamPrison": [{"x": 18, "y": 18}],
        "opponentTarget": [{"x": 2, "y": 2}],
        "opponentPrison": [{"x": 0, "y": 0}]
    }

    uninitialized_world.init(req)

    assert uninitialized_world.my_team_name == "R"
    assert len(uninitialized_world.my_players) == 2
    assert len(uninitialized_world.enemy_players) == 2
    assert len(uninitialized_world.my_flags) == 2
    assert len(uninitialized_world.enemy_flags) == 2
