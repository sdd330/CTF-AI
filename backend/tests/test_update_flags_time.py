"""
World.update 旗帜和时间更新场景测试
测试旗帜更新、时间验证和得分检测
"""

import pytest
from lib.data_models import Position, Action


def _make_update_req(time=1.0, my_players=None, enemy_players=None, my_flags=None, enemy_flags=None):
    """创建更新请求"""
    return {
        "time": time,
        "myteamPlayer": my_players or [],
        "opponentPlayer": enemy_players or [],
        "myteamFlag": my_flags or [],
        "opponentFlag": enemy_flags or []
    }


def test_update_flags_from_request(world):
    """测试旗帜更新场景"""
    req = _make_update_req(
        my_flags=[{"posX": 5, "posY": 5, "canPickup": True}],
        enemy_flags=[{"posX": 15, "posY": 15, "canPickup": True}]
    )

    result = world.update(req)
    assert result is True
    assert len(world.my_flags) >= 1
    assert len(world.enemy_flags) >= 1


def test_update_time_validation(world):
    """测试时间验证场景"""
    req = _make_update_req(time=0.5)

    # 第一次更新
    result1 = world.update(req)
    assert result1 is True
    assert world.current_time == 0.5

    # 第二次更新（时间倒退，应该失败）
    req["time"] = 0.3
    result2 = world.update(req)
    assert result2 is False
    assert world.current_time == 0.5  # 时间不应该更新


def test_update_scoring_detection(world):
    """测试得分检测场景"""
    enemy_flag = next(iter(world.enemy_flags.values()))
    player = world.my_players["L0"]
    player.action(Action.PICKUP_FLAG, flag=enemy_flag)

    # 移动到己方基地
    base_pos = Position(2, 2)
    player.position = base_pos

    req = _make_update_req(
        my_players=[{"name": "L0", "team": "L", "posX": 2, "posY": 2, "hasFlag": True, "inPrison": False}],
        enemy_flags=[{"posX": 2, "posY": 2, "canPickup": False}]
    )

    initial_score = world.left_team_score
    result = world.update(req)
    assert result is True
    assert world.left_team_score >= initial_score
