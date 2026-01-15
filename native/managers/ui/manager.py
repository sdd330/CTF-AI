"""
UI 管理器
参考 frontend/src/game/managers/UIManager.ts
"""

import pygame
from typing import Optional, Dict, Any

from .base import UIComponent, UIComponentType
from .score_text import ScoreTextComponent
from .tutorial_text import TutorialTextComponent
from .game_over_text import GameOverTextComponent
from .team_name_text import TeamNameTextComponent


class UIComponentFactory:
    """UI 组件工厂"""

    @staticmethod
    def create(
        component_type: UIComponentType,
        *args: Any,
        **kwargs: Any
    ) -> UIComponent:
        """创建 UI 组件"""
        if component_type == UIComponentType.SCORE_TEXT:
            return ScoreTextComponent(args[0], args[1], args[2], kwargs.get('font'))
        elif component_type == UIComponentType.TUTORIAL_TEXT:
            return TutorialTextComponent(args[0], args[1], kwargs.get('font'))
        elif component_type == UIComponentType.GAME_OVER_TEXT:
            return GameOverTextComponent(args[0], args[1], kwargs.get('font'))
        elif component_type == UIComponentType.TEAM_NAME_TEXT:
            return TeamNameTextComponent(args[0], args[1], args[2], kwargs.get('font'))
        else:
            raise ValueError(f"Unknown UI component type: {component_type}")


class UIManager:
    """UI 管理器"""

    def __init__(self, screen: pygame.Surface, font: Optional[pygame.font.Font] = None):
        self.screen = screen
        self.default_font = font
        self.components: Dict[str, UIComponent] = {}

    def create_component(
        self,
        component_id: str,
        component_type: UIComponentType,
        *args: Any,
        **kwargs: Any
    ) -> UIComponent:
        """创建并注册 UI 组件"""
        if 'font' not in kwargs and self.default_font:
            kwargs['font'] = self.default_font

        component = UIComponentFactory.create(component_type, *args, **kwargs)
        self.components[component_id] = component
        return component

    def get_component(self, component_id: str) -> Optional[UIComponent]:
        """获取组件"""
        return self.components.get(component_id)

    def update_component(self, component_id: str, data: Any = None) -> None:
        """更新组件"""
        component = self.components.get(component_id)
        if component:
            component.update(data)

    def show_component(self, component_id: str) -> None:
        """显示组件"""
        component = self.components.get(component_id)
        if component:
            component.show()

    def hide_component(self, component_id: str) -> None:
        """隐藏组件"""
        component = self.components.get(component_id)
        if component:
            component.hide()

    def destroy_component(self, component_id: str) -> None:
        """销毁指定组件"""
        component = self.components.get(component_id)
        if component:
            component.destroy()
            del self.components[component_id]

    def destroy_all(self) -> None:
        """销毁所有组件"""
        for component in self.components.values():
            component.destroy()
        self.components.clear()

    def render(self) -> None:
        """渲染所有可见的组件"""
        for component in self.components.values():
            if hasattr(component, 'visible') and component.visible:
                component.render(self.screen)
