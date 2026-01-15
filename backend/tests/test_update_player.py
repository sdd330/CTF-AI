"""
World.update 玩家更新场景测试
测试玩家状态、监狱和位置更新
"""

import pytest
from lib.data_models import Player, Team, Position, Action


def _make_update_req(time=1.0, my_players=None, enemy_players=None, my_flags=None, enemy_flags=None):
    """创建更新请求"""
    return {
        "time": time,
        "myteamPlayer": my_players or [],
        "opponentPlayer": enemy_players or [],
        "myteamFlag": my_flags or [],
        "opponentFlag": enemy_flags or []
    }


def test_update_players_from_request_existing_player(world):
    """测试现有玩家更新场景"""
    assert "L0" in world.my_players

    req = _make_update_req(
        my_players=[{"name": "L0", "team": "L", "posX": 6, "posY": 6, "hasFlag": False, "inPrison": False}]
    )

    result = world.update(req)
    assert result is True
    assert world.my_players["L0"].position == Position(6, 6)


def test_update_player_pickup_flag(world):
    """测试玩家拾取旗帜场景"""
    enemy_flag = next(iter(world.enemy_flags.values()))
    assert enemy_flag is not None

    req = _make_update_req(
        my_players=[{
            "name": "L0", "team": "L",
            "posX": enemy_flag.position.x, "posY": enemy_flag.position.y,
            "hasFlag": True, "inPrison": False
        }],
        enemy_flags=[{"posX": enemy_flag.position.x, "posY": enemy_flag.position.y, "canPickup": False}]
    )

    result = world.update(req)
    assert result is True
    assert world.my_players["L0"].has_flag is True


def test_update_player_drop_flag(world):
    """测试玩家放下旗帜场景"""
    enemy_flag = next(iter(world.enemy_flags.values()))
    player = world.my_players["L0"]
    player.action(Action.PICKUP_FLAG, flag=enemy_flag)

    req = _make_update_req(
        my_players=[{
            "name": "L0", "team": "L",
            "posX": enemy_flag.position.x, "posY": enemy_flag.position.y,
            "hasFlag": False, "inPrison": False
        }],
        enemy_flags=[{"posX": enemy_flag.position.x, "posY": enemy_flag.position.y, "canPickup": True}]
    )

    result = world.update(req)
    assert result is True
    assert world.my_players["L0"].has_flag is False


def test_update_player_sent_to_prison(world, test_map):
    """测试玩家被抓进监狱场景"""
    req = _make_update_req(
        my_players=[{"name": "L0", "team": "L", "posX": 18, "posY": 18, "hasFlag": False, "inPrison": True}]
    )

    result = world.update(req)
    assert result is True
    assert world.my_players["L0"].is_in_prison is True
    # 验证玩家在敌方监狱（R队监狱）
    r_prison = test_map.right_team_prison.positions
    assert world.my_players["L0"].position in r_prison


def test_update_player_rescued_from_prison(world):
    """测试玩家被营救场景"""
    player = world.my_players["L0"]
    player.send_to_prison(Position(18, 18))

    req = _make_update_req(
        my_players=[{"name": "L0", "team": "L", "posX": 5, "posY": 5, "hasFlag": False, "inPrison": False}]
    )

    result = world.update(req)
    assert result is True
    assert world.my_players["L0"].is_in_prison is False
