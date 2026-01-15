"""
物理系统管理器 - 重导出模块
为保持向后兼容性，从 physics 子模块重导出
"""

from .physics import (
    PhysicsManager,
    CollisionCallbacks,
    CollisionHandler,
    ZoneChecker,
)

__all__ = [
    'PhysicsManager',
    'CollisionCallbacks',
    'CollisionHandler',
    'ZoneChecker',
]
