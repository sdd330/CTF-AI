"""
输入管理器 - 重导出模块
为保持向后兼容性，从 input 子模块重导出
"""

from .input import (
    InputStrategy,
    InputObserver,
    KeyboardInputStrategy,
    RemoteInputStrategy,
    HybridInputStrategy,
    InputManager,
)

__all__ = [
    'InputStrategy',
    'InputObserver',
    'KeyboardInputStrategy',
    'RemoteInputStrategy',
    'HybridInputStrategy',
    'InputManager',
]
