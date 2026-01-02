"""
UI 管理器
参考 frontend/src/game/managers/UIManager.ts
设计模式：工厂模式 + 组件化
"""

import pygame
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, Dict, Any

from ..utils.enums import Team


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


class ScoreTextComponent(UIComponent):
    """分数文本组件"""
    
    def __init__(self, team: Team, x: int, y: int, font: Optional[pygame.font.Font] = None):
        """
        初始化分数文本组件
        
        Args:
            team: 队伍
            x: X 坐标
            y: Y 坐标
            font: 字体（如果为 None，使用默认字体）
        """
        self.team = team
        self.x = x
        self.y = y
        self.font = font or pygame.font.Font(None, 36)
        self.visible = True
        self.score = 0
        self._update_text()
    
    def _update_text(self) -> None:
        """更新文本内容"""
        team_str = "L" if self.team == Team.LEFT else "R"
        self.text_surface = self.font.render(
            f"{team_str}Team #Flags: {self.score}",
            True,
            (255, 255, 255)  # 白色
        )
        # 添加黑色描边效果（简单实现：绘制多次偏移的文本）
        self.text_surface_outline = self.font.render(
            f"{team_str}Team #Flags: {self.score}",
            True,
            (0, 0, 0)  # 黑色
        )
    
    def show(self) -> None:
        """显示组件"""
        self.visible = True
    
    def hide(self) -> None:
        """隐藏组件"""
        self.visible = False
    
    def update(self, score: int) -> None:
        """更新分数"""
        self.score = score
        self._update_text()
    
    def destroy(self) -> None:
        """销毁组件"""
        self.visible = False
    
    def render(self, screen: pygame.Surface) -> None:
        """渲染组件"""
        if not self.visible:
            return
        
        # 绘制描边（简单实现：绘制多次偏移的文本）
        offsets = [(-2, -2), (-2, 0), (-2, 2), (0, -2), (0, 2), (2, -2), (2, 0), (2, 2)]
        for offset_x, offset_y in offsets:
            screen.blit(self.text_surface_outline, (self.x + offset_x, self.y + offset_y))
        
        # 绘制主文本
        screen.blit(self.text_surface, (self.x, self.y))


class TutorialTextComponent(UIComponent):
    """教程文本组件"""
    
    def __init__(self, x: int, y: int, font: Optional[pygame.font.Font] = None):
        """
        初始化教程文本组件
        
        Args:
            x: X 坐标
            y: Y 坐标
            font: 字体（如果为 None，使用默认字体）
        """
        self.x = x
        self.y = y
        # 确保字体已初始化
        try:
            self.font = font or pygame.font.Font(None, 48)
        except:
            # 如果默认字体失败，尝试使用系统字体
            try:
                self.font = pygame.font.SysFont('arial', 48)
            except:
                # 最后的回退方案
                self.font = pygame.font.Font(pygame.font.get_default_font(), 48)
        self.visible = True
        self.text = "Arrow keys to move!\nPress Spacebar to Start"
        self._update_text()
        print(f"[TutorialTextComponent] 初始化完成: x={x}, y={y}, visible={self.visible}, text_lines={len(self.text_surfaces)}")
    
    def _update_text(self) -> None:
        """更新文本内容"""
        if not self.font:
            print("[TutorialTextComponent] 警告: 字体未初始化，无法渲染文本")
            self.text_surfaces = []
            self.text_surfaces_outline = []
            return
        
        lines = self.text.split('\n')
        self.text_surfaces = []
        self.text_surfaces_outline = []
        
        for line in lines:
            try:
                # 使用白色文本和黑色描边，确保在任何背景下都可见
                surface = self.font.render(line, True, (255, 255, 255))  # 白色
                surface_outline = self.font.render(line, True, (0, 0, 0))  # 黑色描边
                if surface.get_width() == 0 or surface.get_height() == 0:
                    print(f"[TutorialTextComponent] 警告: 文本表面尺寸为 0, line='{line}'")
                self.text_surfaces.append(surface)
                self.text_surfaces_outline.append(surface_outline)
                print(f"[TutorialTextComponent] 成功渲染文本行: '{line}', 尺寸: {surface.get_size()}")
            except Exception as e:
                print(f"[TutorialTextComponent] 渲染文本失败: {e}, line='{line}'")
                # 创建一个空的表面作为占位符
                empty_surface = pygame.Surface((100, 20))
                empty_surface.fill((255, 255, 255))
                self.text_surfaces.append(empty_surface)
                self.text_surfaces_outline.append(empty_surface)
    
    def show(self) -> None:
        """显示组件"""
        self.visible = True
    
    def hide(self) -> None:
        """隐藏组件"""
        self.visible = False
    
    def update(self, text: Optional[str] = None) -> None:
        """更新文本"""
        if text is not None:
            self.text = text
            self._update_text()
    
    def destroy(self) -> None:
        """销毁组件"""
        self.visible = False
    
    def render(self, screen: pygame.Surface) -> None:
        """渲染组件（多行文本整体居中）"""
        if not self.visible:
            return
        
        # 检查是否有文本表面
        if not hasattr(self, 'text_surfaces') or not self.text_surfaces:
            print("[TutorialTextComponent] 警告: text_surfaces 为空，无法渲染")
            return
        
        # 计算所有行的总高度（用于整体居中）
        total_height = 0
        line_heights = []
        for surface in self.text_surfaces:
            height = surface.get_height()
            line_heights.append(height)
            total_height += height
        # 添加行间距（除了最后一行）
        if len(self.text_surfaces) > 1:
            total_height += 10 * (len(self.text_surfaces) - 1)
        
        # 从中心向上偏移一半高度，使文本整体居中
        start_y = self.y - total_height // 2
        
        y_offset = 0
        for i, (surface, surface_outline) in enumerate(zip(self.text_surfaces, self.text_surfaces_outline)):
            # 计算居中位置
            text_width = surface.get_width()
            x = self.x - text_width // 2
            
            # 绘制描边
            offsets = [(-2, -2), (-2, 0), (-2, 2), (0, -2), (0, 2), (2, -2), (2, 0), (2, 2)]
            for offset_x, offset_y in offsets:
                screen.blit(surface_outline, (x + offset_x, start_y + y_offset + offset_y))
            
            # 绘制主文本
            screen.blit(surface, (x, start_y + y_offset))
            
            y_offset += line_heights[i] + (10 if i < len(self.text_surfaces) - 1 else 0)


class GameOverTextComponent(UIComponent):
    """游戏结束文本组件"""
    
    def __init__(self, x: int, y: int, font: Optional[pygame.font.Font] = None):
        """
        初始化游戏结束文本组件
        
        Args:
            x: X 坐标
            y: Y 坐标
            font: 字体（如果为 None，使用默认字体）
        """
        self.x = x
        self.y = y
        self.font = font or pygame.font.Font(None, 64)
        self.visible = False
        self.text = "Game Over"
        self._update_text()
    
    def _update_text(self) -> None:
        """更新文本内容"""
        self.text_surface = self.font.render(self.text, True, (255, 255, 255))
        self.text_surface_outline = self.font.render(self.text, True, (0, 0, 0))
    
    def show(self) -> None:
        """显示组件"""
        self.visible = True
    
    def hide(self) -> None:
        """隐藏组件"""
        self.visible = False
    
    def update(self, winner: Optional[str] = None) -> None:
        """更新文本"""
        if winner:
            self.text = f"{winner}Team Won!"
        else:
            self.text = "Game Over"
        self._update_text()
    
    def destroy(self) -> None:
        """销毁组件"""
        self.visible = False
    
    def render(self, screen: pygame.Surface) -> None:
        """渲染组件"""
        if not self.visible:
            return
        
        # 计算居中位置
        text_width = self.text_surface.get_width()
        x = self.x - text_width // 2
        
        # 绘制描边
        offsets = [(-2, -2), (-2, 0), (-2, 2), (0, -2), (0, 2), (2, -2), (2, 0), (2, 2)]
        for offset_x, offset_y in offsets:
            screen.blit(self.text_surface_outline, (x + offset_x, self.y + offset_y))
        
        # 绘制主文本
        screen.blit(self.text_surface, (x, self.y))


class TeamNameTextComponent(UIComponent):
    """队伍名称文本组件"""
    
    def __init__(self, team: Team, x: int, y: int, font: Optional[pygame.font.Font] = None):
        """
        初始化队伍名称文本组件
        
        Args:
            team: 队伍
            x: X 坐标
            y: Y 坐标
            font: 字体（如果为 None，使用默认字体）
        """
        self.team = team
        self.x = x
        self.y = y
        self.font = font or pygame.font.Font(None, 36)
        self.visible = True
        self.text = "-"
        self._update_text()
    
    def _update_text(self) -> None:
        """更新文本内容"""
        self.text_surface = self.font.render(self.text, True, (255, 255, 255))
        self.text_surface_outline = self.font.render(self.text, True, (0, 0, 0))
    
    def show(self) -> None:
        """显示组件"""
        self.visible = True
    
    def hide(self) -> None:
        """隐藏组件"""
        self.visible = False
    
    def update(self, who: str) -> None:
        """更新队伍名称"""
        self.text = who
        self._update_text()
    
    def destroy(self) -> None:
        """销毁组件"""
        self.visible = False
    
    def render(self, screen: pygame.Surface) -> None:
        """渲染组件"""
        if not self.visible:
            return
        
        # 绘制描边
        offsets = [(-2, -2), (-2, 0), (-2, 2), (0, -2), (0, 2), (2, -2), (2, 0), (2, 2)]
        for offset_x, offset_y in offsets:
            screen.blit(self.text_surface_outline, (self.x + offset_x, self.y + offset_y))
        
        # 绘制主文本
        screen.blit(self.text_surface, (self.x, self.y))


class UIComponentFactory:
    """UI 组件工厂"""
    
    @staticmethod
    def create(
        component_type: UIComponentType,
        *args: Any,
        **kwargs: Any
    ) -> UIComponent:
        """
        创建 UI 组件
        
        Args:
            component_type: 组件类型
            *args: 位置参数
            **kwargs: 关键字参数
        
        Returns:
            UI 组件实例
        """
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
    """
    UI 管理器
    参考 frontend/src/game/managers/UIManager.ts
    """
    
    def __init__(self, screen: pygame.Surface, font: Optional[pygame.font.Font] = None):
        """
        初始化 UI 管理器
        
        Args:
            screen: pygame 屏幕表面
            font: 默认字体（如果为 None，使用系统默认字体）
        """
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
        """
        创建并注册 UI 组件
        
        Args:
            component_id: 组件 ID
            component_type: 组件类型
            *args: 位置参数
            **kwargs: 关键字参数
        
        Returns:
            UI 组件实例
        """
        if 'font' not in kwargs and self.default_font:
            kwargs['font'] = self.default_font
        
        component = UIComponentFactory.create(component_type, *args, **kwargs)
        self.components[component_id] = component
        return component
    
    def get_component(self, component_id: str) -> Optional[UIComponent]:
        """
        获取组件
        
        Args:
            component_id: 组件 ID
        
        Returns:
            UI 组件实例，如果不存在返回 None
        """
        return self.components.get(component_id)
    
    def update_component(self, component_id: str, data: Any = None) -> None:
        """
        更新组件
        
        Args:
            component_id: 组件 ID
            data: 更新数据
        """
        component = self.components.get(component_id)
        if component:
            component.update(data)
    
    def show_component(self, component_id: str) -> None:
        """
        显示组件
        
        Args:
            component_id: 组件 ID
        """
        component = self.components.get(component_id)
        if component:
            component.show()
    
    def hide_component(self, component_id: str) -> None:
        """
        隐藏组件
        
        Args:
            component_id: 组件 ID
        """
        component = self.components.get(component_id)
        if component:
            component.hide()
    
    def destroy_component(self, component_id: str) -> None:
        """
        销毁指定组件
        
        Args:
            component_id: 组件 ID
        """
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
        for component_id, component in self.components.items():
            if hasattr(component, 'visible') and component.visible:
                component.render(self.screen)

