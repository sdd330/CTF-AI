"""
游戏状态管理器
设计模式：单例模式 + 观察者模式

此模块已重构为多个小文件，位于 managers/game_state/ 目录下。
此文件保留用于向后兼容。
"""

from .game_state import (
    GameStateManager,
    StateChangeListener,
    GameFlowState,
    GameFlowSubState,
    Position,
    PlayerPosition,
    TeamState,
    GameConfig,
    StateSnapshot,
    ConfigLoader,
    TeamGenerator,
    FlowControlMixin,
)

__all__ = [
    'GameStateManager',
    'StateChangeListener',
    'GameFlowState',
    'GameFlowSubState',
    'Position',
    'PlayerPosition',
    'TeamState',
    'GameConfig',
    'StateSnapshot',
    'ConfigLoader',
    'TeamGenerator',
    'FlowControlMixin',
]
