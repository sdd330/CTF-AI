"""
UI 管理器 - 重导出模块
为保持向后兼容性，从 ui 子模块重导出
"""

from .ui import (
    UIComponent,
    UIComponentType,
    TEXT_OUTLINE_OFFSETS,
    ScoreTextComponent,
    TutorialTextComponent,
    GameOverTextComponent,
    TeamNameTextComponent,
    UIManager,
    UIComponentFactory,
)

__all__ = [
    'UIComponent',
    'UIComponentType',
    'TEXT_OUTLINE_OFFSETS',
    'ScoreTextComponent',
    'TutorialTextComponent',
    'GameOverTextComponent',
    'TeamNameTextComponent',
    'UIManager',
    'UIComponentFactory',
]
