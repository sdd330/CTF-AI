"""
地图服务模块
统一导出所有地图相关的类和函数
"""

from .map import GameMap

# WeightMapBuilder 已移至 game_service 包
# 如需使用，请从 ..game_service.weight_map_builder 或 ..game_service 导入

__all__ = [
    'GameMap',
]

