"""
队伍名称文本组件
"""

import pygame
from typing import Optional

from .base import UIComponent, TEXT_OUTLINE_OFFSETS
from ...utils.enums import Team


class TeamNameTextComponent(UIComponent):
    """队伍名称文本组件"""

    def __init__(
        self,
        team: Team,
        x: int,
        y: int,
        font: Optional[pygame.font.Font] = None
    ):
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
        self.visible = True

    def hide(self) -> None:
        self.visible = False

    def update(self, who: str) -> None:
        """更新队伍名称"""
        self.text = who
        self._update_text()

    def destroy(self) -> None:
        self.visible = False

    def render(self, screen: pygame.Surface) -> None:
        if not self.visible:
            return

        for offset_x, offset_y in TEXT_OUTLINE_OFFSETS:
            screen.blit(
                self.text_surface_outline,
                (self.x + offset_x, self.y + offset_y)
            )
        screen.blit(self.text_surface, (self.x, self.y))
