"""
游戏结束文本组件
"""

import pygame
from typing import Optional

from .base import UIComponent, TEXT_OUTLINE_OFFSETS


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
        for offset_x, offset_y in TEXT_OUTLINE_OFFSETS:
            screen.blit(
                self.text_surface_outline,
                (x + offset_x, self.y + offset_y)
            )

        # 绘制主文本
        screen.blit(self.text_surface, (x, self.y))
