"""
Player.action 旗帜相关测试
测试拾取、放下、得分等旗帜操作
"""

import pytest
from lib.data_models import Player, Team, Position, Action, Flag
from lib.game_service import World


def test_action_pickup_flag(test_map):
    """测试action方法 - PICKUP_FLAG：验证拾取结果"""
    world = World(test_map)
    player = Player("L0", Team.LEFT, Position(7, 5), world)
    flag = Flag('flag1', Team.RIGHT, Position(7, 5))
    world.enemy_flags[flag.flag_id] = flag

    result = player.action(Action.PICKUP_FLAG, flag=flag)
    assert result is True
    player.update_from_dict(
        {"name": "L0", "team": "L", "posX": 7, "posY": 5, "hasFlag": True, "inPrison": False},
        world.enemy_flags
    )
    assert player.has_flag is True
    assert flag.carried_by == player


def test_action_drop_flag(test_map):
    """测试action方法 - DROP_FLAG"""
    world = World(test_map)
    player = Player("L0", Team.LEFT, Position(5, 5), world)
    flag = Flag('flag1', Team.RIGHT, Position(5, 5))
    world.enemy_flags[flag.flag_id] = flag

    player.action(Action.PICKUP_FLAG, flag=flag)
    player.update_from_dict(
        {"name": "L0", "team": "L", "posX": 5, "posY": 5, "hasFlag": True, "inPrison": False},
        world.enemy_flags
    )
    assert player.has_flag is True

    result = player.action(Action.DROP_FLAG)
    assert result is True
    player.update_from_dict(
        {"name": "L0", "team": "L", "posX": 5, "posY": 5, "hasFlag": False, "inPrison": False},
        world.enemy_flags
    )
    assert player.has_flag is False
    assert flag.carried_by is None


def test_action_score_flag(test_map):
    """测试action方法 - SCORE_FLAG：验证得分结果"""
    world = World(test_map)
    player = Player("L0", Team.LEFT, Position(5, 5), world)
    player.set_base_area(world.map.left_team_target)
    flag = Flag('flag1', Team.RIGHT, Position(5, 5))
    flag.pick_up_by(player)
    world.enemy_flags[flag.flag_id] = flag
    player.update_from_dict(
        {"name": "L0", "team": "L", "posX": 5, "posY": 5, "hasFlag": True, "inPrison": False},
        world.enemy_flags
    )

    result = player.action(Action.SCORE_FLAG)
    assert result is True
    player.update_from_dict(
        {"name": "L0", "team": "L", "posX": 5, "posY": 5, "hasFlag": False, "inPrison": False},
        world.enemy_flags
    )
    assert player.has_flag is False
    assert world.left_team_score == 1


def test_action_pickup_own_flag_fails(test_map):
    """测试action方法 - 不能拾取己方旗帜：验证拾取失败结果"""
    world = World(test_map)
    player = Player("L0", Team.LEFT, Position(7, 5), world)
    own_flag = Flag('flag1', Team.LEFT, Position(7, 5))
    world.my_flags[own_flag.flag_id] = own_flag

    result = player.action(Action.PICKUP_FLAG, flag=own_flag)
    assert result is False
    assert player.has_flag is False


def test_action_invalid_parameters(test_map):
    """测试action方法 - 缺少参数"""
    world = World(test_map)
    player = Player("L0", Team.LEFT, Position(5, 5), world)

    assert player.action(Action.PICKUP_FLAG) is False
    assert player.action(Action.TAG_ENEMY) is False
    assert player.action(Action.RESCUE_TEAMMATE) is False


def test_pickup_flag_with_wall(test_map_with_walls):
    """测试有墙时拾取旗帜：验证拾取结果"""
    world = World(test_map_with_walls)
    player = Player("L0", Team.LEFT, Position(5, 5), world)
    flag = Flag('flag1', Team.RIGHT, Position(5, 5))
    world.enemy_flags[flag.flag_id] = flag

    result = player.action(Action.PICKUP_FLAG, flag=flag)
    assert result is True
    player.update_from_dict(
        {"name": "L0", "team": "L", "posX": 5, "posY": 5, "hasFlag": True, "inPrison": False},
        world.enemy_flags
    )
    assert player.has_flag is True


def test_score_flag_with_wall_blocking(test_map_with_walls):
    """测试有墙阻挡时得分：验证得分结果"""
    world = World(test_map_with_walls)
    player = Player("L0", Team.LEFT, Position(5, 6), world)
    player.set_base_area(world.map.left_team_target)
    flag = Flag('flag1', Team.RIGHT, Position(5, 6))
    flag.pick_up_by(player)
    world.enemy_flags[flag.flag_id] = flag
    player.update_from_dict(
        {"name": "L0", "team": "L", "posX": 5, "posY": 6, "hasFlag": True, "inPrison": False},
        world.enemy_flags
    )

    result = player.action(Action.SCORE_FLAG)
    assert result is True
    player.update_from_dict(
        {"name": "L0", "team": "L", "posX": 5, "posY": 6, "hasFlag": False, "inPrison": False},
        world.enemy_flags
    )
    assert player.has_flag is False
    assert world.left_team_score == 1
