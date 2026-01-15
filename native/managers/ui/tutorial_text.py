"""
教程文本组件
"""

import pygame
from typing import Optional, List

from .base import UIComponent, TEXT_OUTLINE_OFFSETS


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
        self.font = self._init_font(font)
        self.visible = True
        self.text = "Arrow keys to move!\nPress Spacebar to Start"
        self.text_surfaces: List[pygame.Surface] = []
        self.text_surfaces_outline: List[pygame.Surface] = []
        self._update_text()
        print(f"[TutorialTextComponent] 初始化完成: x={x}, y={y}, "
              f"visible={self.visible}, text_lines={len(self.text_surfaces)}")

    def _init_font(self, font: Optional[pygame.font.Font]) -> pygame.font.Font:
        """初始化字体，带有多级回退"""
        if font:
            return font
        try:
            return pygame.font.Font(None, 48)
        except Exception:
            try:
                return pygame.font.SysFont('arial', 48)
            except Exception:
                return pygame.font.Font(pygame.font.get_default_font(), 48)

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
            self._render_line(line)

    def _render_line(self, line: str) -> None:
        """渲染单行文本"""
        try:
            surface = self.font.render(line, True, (255, 255, 255))
            surface_outline = self.font.render(line, True, (0, 0, 0))
            if surface.get_width() == 0 or surface.get_height() == 0:
                print(f"[TutorialTextComponent] 警告: 文本表面尺寸为 0, line='{line}'")
            self.text_surfaces.append(surface)
            self.text_surfaces_outline.append(surface_outline)
            print(f"[TutorialTextComponent] 成功渲染文本行: '{line}', "
                  f"尺寸: {surface.get_size()}")
        except Exception as e:
            print(f"[TutorialTextComponent] 渲染文本失败: {e}, line='{line}'")
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

        if not hasattr(self, 'text_surfaces') or not self.text_surfaces:
            print("[TutorialTextComponent] 警告: text_surfaces 为空，无法渲染")
            return

        total_height, line_heights = self._calculate_heights()
        start_y = self.y - total_height // 2

        y_offset = 0
        for i, (surface, surface_outline) in enumerate(
            zip(self.text_surfaces, self.text_surfaces_outline)
        ):
            self._render_single_line(screen, surface, surface_outline,
                                     start_y + y_offset)
            y_offset += line_heights[i]
            if i < len(self.text_surfaces) - 1:
                y_offset += 10  # 行间距

    def _calculate_heights(self) -> tuple:
        """计算所有行的高度"""
        total_height = 0
        line_heights = []
        for surface in self.text_surfaces:
            height = surface.get_height()
            line_heights.append(height)
            total_height += height
        if len(self.text_surfaces) > 1:
            total_height += 10 * (len(self.text_surfaces) - 1)
        return total_height, line_heights

    def _render_single_line(self, screen: pygame.Surface,
                            surface: pygame.Surface,
                            surface_outline: pygame.Surface,
                            y: int) -> None:
        """渲染单行文本"""
        text_width = surface.get_width()
        x = self.x - text_width // 2

        # 绘制描边
        for offset_x, offset_y in TEXT_OUTLINE_OFFSETS:
            screen.blit(surface_outline, (x + offset_x, y + offset_y))

        # 绘制主文本
        screen.blit(surface, (x, y))
