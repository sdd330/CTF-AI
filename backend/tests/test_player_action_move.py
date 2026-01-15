"""
Player.action 移动和抓捕相关测试
测试移动、抓捕和营救操作
"""

import pytest
from lib.data_models import Player, Team, Position, Action, Direction
from lib.game_service import World


def test_action_tag_enemy(test_map):
    """测试action方法 - TAG_ENEMY：验证抓捕结果"""
    world = World(test_map)
    tagger = Player('L0', Team.LEFT, Position(5, 5), world)
    target = Player('R0', Team.RIGHT, Position(5, 5), world)
    world.my_players[tagger.name] = tagger
    world.enemy_players[target.name] = target

    result = tagger.action(Action.TAG_ENEMY, target=target)
    assert result is True
    assert target.is_in_prison is True


def test_l_team_defence_capture_r_player_in_l_territory(test_map):
    """测试防守：验证L队抓捕R队玩家后，R队玩家被送到L队监狱"""
    world = World(test_map)
    l_player = Player('L0', Team.LEFT, Position(5, 5), world)
    r_player = Player('R0', Team.RIGHT, Position(5, 5), world)
    world.my_players[l_player.name] = l_player
    world.enemy_players[r_player.name] = r_player

    result = l_player.action(Action.TAG_ENEMY, target=r_player)
    assert result is True
    assert r_player.is_in_prison is True

    # 验证R队玩家在L队监狱（敌方监狱）
    l_prison_positions = test_map.left_team_prison.positions
    assert r_player.position in l_prison_positions

    # 验证R队玩家不在R队监狱
    r_prison_positions = test_map.right_team_prison.positions
    assert r_player.position not in r_prison_positions


def test_action_rescue_teammate(test_map):
    """测试action方法 - RESCUE_TEAMMATE"""
    world = World(test_map)
    prison_pos = Position(18, 18)
    rescuer = Player('L0', Team.LEFT, prison_pos, world)
    teammate = Player('L1', Team.LEFT, prison_pos, world)
    world.my_players[rescuer.name] = rescuer
    world.my_players[teammate.name] = teammate

    teammate.send_to_prison(prison_pos)
    assert teammate.is_in_prison is True

    result = rescuer.action(Action.RESCUE_TEAMMATE, teammate=teammate)
    assert result is True
    assert teammate.is_in_prison is False


def test_move_blocked_by_wall(test_map_with_walls):
    """测试移动被墙阻挡"""
    world = World(test_map_with_walls)
    player = Player("L0", Team.LEFT, Position(3, 5), world)

    result = player.move(Direction.RIGHT)
    assert result is False, "应该被墙阻挡"
    assert player.position == Position(3, 5), "位置不应该改变"


def test_move_around_wall(test_map_with_walls):
    """测试绕开墙移动：验证玩家能到达目标位置"""
    world = World(test_map_with_walls)
    player = Player("L0", Team.LEFT, Position(5, 5), world)
    assert player.position == Position(5, 5)


def test_move_to_boundary(test_map):
    """测试移动到地图边界"""
    world = World(test_map)
    player = Player("L0", Team.LEFT, Position(0, 0), world)

    assert player.move(Direction.LEFT) is False
    assert player.position == Position(0, 0)

    assert player.move(Direction.UP) is False
    assert player.position == Position(0, 0)

    assert player.move(Direction.RIGHT) is True
    assert player.position == Position(1, 0)

    assert player.move(Direction.DOWN) is True
    assert player.position == Position(1, 1)


def test_move_to_map_edge(test_map):
    """测试移动到地图边缘"""
    world = World(test_map)
    player = Player("L0", Team.LEFT, Position(19, 19), world)

    assert player.move(Direction.RIGHT) is False
    assert player.position == Position(19, 19)

    assert player.move(Direction.DOWN) is False
    assert player.position == Position(19, 19)

    assert player.move(Direction.LEFT) is True
    assert player.position == Position(18, 19)

    assert player.move(Direction.UP) is True
    assert player.position == Position(18, 18)
