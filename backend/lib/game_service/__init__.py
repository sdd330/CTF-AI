"""
游戏服务模块
统一导出所有游戏相关的类和函数
"""

# 游戏主类
from .game import World

# 权重地图构建
from .weight_map_builder import WeightMapBuilder

# 游戏信息收集器
from .game_info_collector import GameInfoCollector

# 游戏日志记录器
from .game_logger import GameLogger

__all__ = [
    # 游戏主类
    'World',
    # 权重地图构建
    'WeightMapBuilder',
    # 游戏信息收集器
    'GameInfoCollector',
    # 游戏日志记录器
    'GameLogger',
]

