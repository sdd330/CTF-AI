"""
游戏服务模块
统一导出所有游戏相关的类和函数
"""

# 游戏主类
from .game import World

# 游戏组件
from .game_initializer import GameInitializer
from .game_state_updater import GameStateUpdater

# 权重地图构建
from .weight_map_builder import WeightMapBuilder

__all__ = [
    # 游戏主类
    'World',
    # 游戏组件
    'GameInitializer',
    'GameStateUpdater',
    # 权重地图构建
    'WeightMapBuilder',
]

