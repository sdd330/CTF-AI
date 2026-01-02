"""
CTF游戏后端库
提供游戏引擎、强化学习等核心功能
"""

# 导出游戏引擎
from . import game_engine
from .game_engine import (
    # 数据模型
    Team,
    PlayerState,
    Position,
    Player,
    Flag,
    # 寻路
    PathfindingStrategy,
    BFSPathfindingStrategy,
    AStarPathfindingStrategy,
    DijkstraPathfindingStrategy,
    Pathfinder,
    # 地图
    GameMap,
    # 游戏逻辑
    World,
    # 服务器
    run_game_server,
)

# 导出强化学习模块（可选，需要torch）
try:
    from . import reinforcement_learning as RL
    from .reinforcement_learning import (
        DQNAgent,
        DQN,
        ReplayBuffer,
        extract_state_features,
    )
    _RL_AVAILABLE = True
except ImportError:
    _RL_AVAILABLE = False
    RL = None


__all__ = [
    # 游戏引擎模块
    'game_engine',
    # 数据模型
    'Team',
    'PlayerState',
    'Position',
    'Player',
    'Flag',
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
]

# 如果RL模块可用，添加到导出列表
if _RL_AVAILABLE:
    __all__.extend([
        'RL',
        'DQNAgent',
        'DQN',
        'ReplayBuffer',
        'extract_state_features',
    ])

