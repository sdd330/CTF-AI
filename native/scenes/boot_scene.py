"""
启动场景
"""

import pygame
from .base_scene import BaseScene


class BootScene(BaseScene):
    """
    启动场景
    这是游戏的第一个场景，用于初始化并启动预加载场景
    """
    
    def __init__(self, scene_manager):
        super().__init__('Boot', scene_manager)
        self.font: pygame.font.Font = None
        self._switched = False  # 标记是否已切换到 Preloader
    
    def preload(self):
        """预加载启动场景所需的资源"""
        # Boot 场景通常用于加载预加载器所需的资源
        # 这里可以加载游戏 logo 或背景等小文件
        self.font = pygame.font.Font(None, 36)
    
    def create(self):
        """创建启动场景"""
        # 不立即切换场景，让 Boot 场景先渲染至少一帧
        print("[Boot] 启动场景已创建")
    
    def update(self, delta_time: int):
        """更新启动场景"""
        # 在第一帧更新后切换到 Preloader 场景
        # 这样确保 Boot 场景至少渲染了一帧
        if not self._switched:
            self._switched = True
            print("[Boot] 启动预加载场景")
            self.start_scene('Preloader')
    
    def render(self):
        """渲染启动场景"""
        if self.screen and self.font:
            self.screen.fill((30, 30, 30))  # 深灰色背景
            
            text = self.font.render("Loading...", True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.screen.get_width() // 2, 
                                              self.screen.get_height() // 2))
            self.screen.blit(text, text_rect)

