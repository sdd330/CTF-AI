"""
分数文本组件
"""

import pygame
from typing import Optional

from .base import UIComponent, TEXT_OUTLINE_OFFSETS
from ...utils.enums import Team


class ScoreTextComponent(UIComponent):
    """分数文本组件"""

    def __init__(
        self,
        team: Team,
        x: int,
        y: int,
        font: Optional[pygame.font.Font] = None
    ):
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
        text = f"{team_str}Team #Flags: {self.score}"
        self.text_surface = self.font.render(text, True, (255, 255, 255))
        self.text_surface_outline = self.font.render(text, True, (0, 0, 0))

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

        # 绘制描边
        for offset_x, offset_y in TEXT_OUTLINE_OFFSETS:
            screen.blit(
                self.text_surface_outline,
                (self.x + offset_x, self.y + offset_y)
            )

        # 绘制主文本
        screen.blit(self.text_surface, (self.x, self.y))
