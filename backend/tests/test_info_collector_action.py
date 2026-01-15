"""
GameInfoCollector 动作收集测试
测试 collect_action 方法
"""

import pytest
from lib.data_models import Direction
from lib.game_service import GameInfoCollector


def test_collector_initialization(world):
    """测试收集器初始化"""
    collector = GameInfoCollector(world)
    assert collector.world == world


def test_collect_action_my_team_player(world):
    """测试收集己方玩家的动作"""
    collector = GameInfoCollector(world)
    my_player = world.my_players["L0"]

    collector.collect_action(my_player, Direction.RIGHT)

    assert "L0" in world._actions
    assert world._actions["L0"] == "right"


def test_collect_action_opponent_player(world):
    """测试跳过非己方玩家的动作"""
    collector = GameInfoCollector(world)
    enemy_player = world.enemy_players["R0"]
    world._actions.clear()

    collector.collect_action(enemy_player, Direction.LEFT)

    assert "R0" not in world._actions
    assert len(world._actions) == 0


def test_collect_action_none_direction(world):
    """测试收集 None 方向（应转换为 STAY）"""
    collector = GameInfoCollector(world)
    my_player = world.my_players["L0"]

    collector.collect_action(my_player, None)

    assert "L0" in world._actions
    assert world._actions["L0"] == ""  # Direction.STAY.value == ""


def test_collect_action_stay_direction(world):
    """测试收集 STAY 方向"""
    collector = GameInfoCollector(world)
    my_player = world.my_players["L0"]

    collector.collect_action(my_player, Direction.STAY)

    assert "L0" in world._actions
    assert world._actions["L0"] == ""


def test_collect_action_multiple_players(world):
    """测试收集多个玩家的动作"""
    collector = GameInfoCollector(world)

    collector.collect_action(world.my_players["L0"], Direction.RIGHT)
    collector.collect_action(world.my_players["L1"], Direction.UP)
    collector.collect_action(world.my_players["L2"], Direction.DOWN)

    assert len(world._actions) == 3
    assert world._actions["L0"] == "right"
    assert world._actions["L1"] == "up"
    assert world._actions["L2"] == "down"
