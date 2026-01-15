"""
World 初始化状态测试
测试位置初始化、状态重置和路径服务
"""

import pytest
from lib.data_models import Position


def _make_init_req():
    """创建标准初始化请求"""
    return {
        "myteamName": "L",
        "numPlayers": 2,
        "numFlags": 2,
        "map": {"width": 20, "height": 20, "walls": [], "obstacles": []},
        "myteamTarget": [{"x": 2, "y": 2}],
        "myteamPrison": [{"x": 0, "y": 0}],
        "opponentTarget": [{"x": 17, "y": 17}],
        "opponentPrison": [{"x": 18, "y": 18}]
    }


def test_init_players_use_temporary_position(uninitialized_world):
    """测试初始化的玩家使用临时位置 (0, 0)"""
    uninitialized_world.init(_make_init_req())

    l0 = uninitialized_world.my_players["L0"]
    assert l0.position == Position(0, 0)

    r0 = uninitialized_world.enemy_players["R0"]
    assert r0.position == Position(0, 0)


def test_init_flags_use_temporary_position(uninitialized_world):
    """测试初始化的旗帜使用临时位置 (0, 0)"""
    uninitialized_world.init(_make_init_req())

    flag_l_0 = uninitialized_world.my_flags["FLAG_L_0"]
    assert flag_l_0.position == Position(0, 0)

    flag_r_0 = uninitialized_world.enemy_flags["FLAG_R_0"]
    assert flag_r_0.position == Position(0, 0)


def test_init_resets_game_state(uninitialized_world):
    """测试初始化重置游戏状态"""
    # 先设置一些状态
    uninitialized_world.left_team_score = 5
    uninitialized_world.right_team_score = 3
    uninitialized_world.current_time = 10.0
    uninitialized_world.my_players["test"] = None
    uninitialized_world.enemy_players["test2"] = None
    uninitialized_world.my_flags["test"] = None
    uninitialized_world.enemy_flags["test2"] = None

    uninitialized_world.init(_make_init_req())

    # 应该重置得分和时间
    assert uninitialized_world.left_team_score == 0
    assert uninitialized_world.right_team_score == 0
    assert uninitialized_world.current_time == 0.0

    # 玩家和旗帜应该被清除
    assert "test" not in uninitialized_world.my_players
    assert "test" not in uninitialized_world.enemy_players
    assert "test" not in uninitialized_world.my_flags
    assert "test" not in uninitialized_world.enemy_flags


def test_init_initializes_pathfinding_service(uninitialized_world):
    """测试初始化路径查找服务"""
    uninitialized_world.init(_make_init_req())
    assert uninitialized_world._pathfinding_service is not None
