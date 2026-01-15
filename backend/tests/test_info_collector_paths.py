"""
GameInfoCollector 路径收集测试
测试 collect_paths_for_visualization 方法
"""

import pytest
from lib.data_models import Position
from lib.game_service import GameInfoCollector


def test_collect_paths_for_visualization_my_team(world):
    """测试收集己方玩家的路径"""
    collector = GameInfoCollector(world)
    path = [Position(5, 5), Position(6, 5), Position(7, 5)]
    world._current_paths["L0"] = path

    collector.collect_paths_for_visualization()

    assert "L0" in world._paths
    assert len(world._paths["L0"]) == 3
    assert world._paths["L0"][0] == {"x": 5, "y": 5}
    assert world._paths["L0"][1] == {"x": 6, "y": 5}
    assert world._paths["L0"][2] == {"x": 7, "y": 5}


def test_collect_paths_for_visualization_opponent_player(world):
    """测试跳过非己方玩家的路径"""
    collector = GameInfoCollector(world)
    path = [Position(15, 15), Position(16, 15)]
    world._current_paths["R0"] = path
    world._paths.clear()

    collector.collect_paths_for_visualization()

    assert "R0" not in world._paths
    assert len(world._paths) == 0


def test_collect_paths_for_visualization_nonexistent_player(world):
    """测试跳过不存在玩家的路径"""
    collector = GameInfoCollector(world)
    world._current_paths["NONEXISTENT"] = [Position(10, 10)]
    world._paths.clear()

    collector.collect_paths_for_visualization()

    assert "NONEXISTENT" not in world._paths


def test_collect_paths_for_visualization_empty_path(world):
    """测试跳过空路径"""
    collector = GameInfoCollector(world)
    world._current_paths["L0"] = []
    world._paths.clear()

    collector.collect_paths_for_visualization()

    assert "L0" not in world._paths or len(world._paths.get("L0", [])) == 0


def test_collect_paths_for_visualization_multiple_players(world):
    """测试收集多个玩家的路径"""
    collector = GameInfoCollector(world)
    world._current_paths["L0"] = [Position(5, 5), Position(6, 5)]
    world._current_paths["L1"] = [Position(7, 7), Position(8, 7)]
    world._current_paths["L2"] = [Position(9, 9), Position(10, 9)]

    collector.collect_paths_for_visualization()

    assert len(world._paths) == 3
    assert "L0" in world._paths
    assert "L1" in world._paths
    assert "L2" in world._paths
