"""
UI 组件基础类型和接口
"""

import pygame
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any


class UIComponentType(Enum):
    """UI 组件类型"""
    SCORE_TEXT = 'score_text'
    TUTORIAL_TEXT = 'tutorial_text'
    GAME_OVER_TEXT = 'game_over_text'
    TEAM_NAME_TEXT = 'team_name_text'


class UIComponent(ABC):
    """UI 组件接口"""

    @abstractmethod
    def show(self) -> None:
        """显示组件"""
        pass

    @abstractmethod
    def hide(self) -> None:
        """隐藏组件"""
        pass

    @abstractmethod
    def update(self, data: Any = None) -> None:
        """更新组件数据"""
        pass

    @abstractmethod
    def destroy(self) -> None:
        """销毁组件"""
        pass

    @abstractmethod
    def render(self, screen: pygame.Surface) -> None:
        """渲染组件"""
        pass


# 描边偏移量常量（用于文本渲染）
TEXT_OUTLINE_OFFSETS = [
    (-2, -2), (-2, 0), (-2, 2),
    (0, -2), (0, 2),
    (2, -2), (2, 0), (2, 2)
]
