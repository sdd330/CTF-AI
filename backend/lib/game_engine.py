"""
Capture the Flag 游戏引擎 - 统一入口模块
导出所有游戏相关的类和函数
"""

# 导出数据模型
from .data_models import (
    Team,
    Direction,
    Action,
    PlayerState,
    Position,
    Player,
    Flag,
    TargetArea,
    PrisonArea,
)

# 导出寻路模块
from .pathfinding_service import (
    PathfindingStrategy,
    BFSPathfindingStrategy,
    AStarPathfindingStrategy,
    DijkstraPathfindingStrategy,
    Pathfinder,
)

# 导出地图模块
from .map_service import GameMap

# 导出游戏逻辑模块
from .game_service import World


# 导出服务器模块
from .server import run_game_server

# 导出状态管理
from .utils import StateManager

# 导出常量模块
from . import constants

__all__ = [
    # 数据模型
    'Team',
    'Direction',
    'Action',
    'PlayerState',
    'Position',
    'Player',
    'Flag',
    'TargetArea',
    'PrisonArea',
    # 寻路
    'PathfindingStrategy',
    'BFSPathfindingStrategy',
    'AStarPathfindingStrategy',
    'DijkstraPathfindingStrategy',
    'Pathfinder',
    # 地图
    'GameMap',
    # 游戏逻辑
    'World',
    # 服务器
    'run_game_server',
    # 状态管理
    'StateManager',
]
