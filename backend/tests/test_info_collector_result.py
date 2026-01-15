"""
GameInfoCollector 结果构建测试
测试 build_result_from_actions 方法
"""

import pytest
from lib.data_models import Position
from lib.game_service import GameInfoCollector


def test_build_result_from_actions_my_team_only(world):
    """测试构建结果只包含己方玩家"""
    collector = GameInfoCollector(world)

    actions = {"L0": "right", "L1": "up", "R0": "left", "R1": "down"}
    world._current_paths["L0"] = [Position(5, 5), Position(6, 5)]
    world._current_paths["L1"] = [Position(7, 7), Position(8, 7)]
    world._current_paths["R0"] = [Position(15, 15), Position(16, 15)]
    world._path_timings["L0"] = {"algorithm": "astar", "total": 1.5}
    world._path_timings["R0"] = {"algorithm": "astar", "total": 2.0}

    result = collector.build_result_from_actions(actions)

    assert "actions" in result
    assert "paths" in result
    assert "timings" in result

    # 验证动作只包含己方玩家
    assert "L0" in result["actions"]
    assert "L1" in result["actions"]
    assert "R0" not in result["actions"]
    assert "R1" not in result["actions"]

    # 验证路径只包含己方玩家
    assert "L0" in result["paths"]
    assert "L1" in result["paths"]
    assert "R0" not in result["paths"]

    # 验证耗时信息只包含己方玩家
    assert "L0" in result["timings"]
    assert "R0" not in result["timings"]


def test_build_result_from_actions_empty_input(world):
    """测试构建空输入的结果"""
    collector = GameInfoCollector(world)

    result = collector.build_result_from_actions({})

    assert "actions" in result
    assert "paths" in result
    assert "timings" in result
    assert len(result["actions"]) == 0
    assert len(result["paths"]) == 0
    assert len(result["timings"]) == 0


def test_build_result_from_actions_with_timings(world):
    """测试构建包含耗时信息的结果"""
    collector = GameInfoCollector(world)
    actions = {"L0": "right"}
    world._current_paths["L0"] = [Position(5, 5), Position(6, 5)]
    world._path_timings["L0"] = {
        "algorithm": "astar", "total": 1.5, "pathfinding": 1.2, "weight_map": 0.3
    }

    result = collector.build_result_from_actions(actions)

    assert "L0" in result["timings"]
    assert result["timings"]["L0"]["algorithm"] == "astar"
    assert result["timings"]["L0"]["total"] == 1.5
    assert result["timings"]["L0"]["pathfinding"] == 1.2
    assert result["timings"]["L0"]["weight_map"] == 0.3


def test_build_result_from_actions_clears_paths(world):
    """测试构建结果时清空路径"""
    collector = GameInfoCollector(world)
    world._paths["L0"] = [{"x": 1, "y": 1}]
    world._paths["L1"] = [{"x": 2, "y": 2}]
    world._current_paths["L0"] = [Position(5, 5), Position(6, 5)]

    result = collector.build_result_from_actions({"L0": "right"})

    assert "L1" not in result["paths"]  # 旧路径被清空
    assert "L0" in result["paths"]  # 新路径被收集
    assert len(result["paths"]["L0"]) == 2
