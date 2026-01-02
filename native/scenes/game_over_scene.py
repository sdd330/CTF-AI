"""
游戏结束场景
"""

import pygame
from typing import Optional, Dict, Any
from .base_scene import BaseScene
from ..utils import Team
from ..managers import UIManager, UIComponentType


class GameOverScene(BaseScene):
    """
    游戏结束场景
    显示游戏结果和重新开始选项
    使用 UIManager 管理 UI 组件
    """
    
    def __init__(self, scene_manager):
        super().__init__('GameOver', scene_manager)
        self.ui_manager: Optional[UIManager] = None
        self.winner: Optional[Team] = None
    
    def preload(self):
        """预加载游戏结束场景资源"""
        pass
    
    def create(self):
        """创建游戏结束场景"""
        # 获取传递的数据
        data = getattr(self, '_scene_data', {})
        self.winner = data.get('winner')
        
        # 设置 UI 管理器
        if self.screen:
            self._setup_ui_manager()
        
        # 安全地获取获胜者文本
        if self.winner:
            winner_text_str = f"{self.winner.value}Team Won!"
        else:
            winner_text_str = "Game Over"
        print(f"[GameOver] 游戏结束，获胜者: {winner_text_str}")
    
    def _setup_ui_manager(self):
        """设置 UI 管理器"""
        if not self.screen:
            return
        
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        # 创建 UI 管理器
        self.ui_manager = UIManager(self.screen)
        
        # 创建游戏结束文本组件
        self.ui_manager.create_component(
            'game_over',
            UIComponentType.GAME_OVER_TEXT,
            screen_width // 2,
            screen_height // 2 - 50
        )
        
        # 更新游戏结束文本
        winner_str = self.winner.value if self.winner else None
        self.ui_manager.update_component('game_over', winner_str)
        
        # 创建提示文本（使用教程文本组件）
        self.ui_manager.create_component(
            'hint',
            UIComponentType.TUTORIAL_TEXT,
            screen_width // 2,
            screen_height // 2 + 50
        )
        self.ui_manager.update_component('hint', "Press R to Restart\nPress L to Reload")
    
    def set_data(self, data: Dict[str, Any]):
        """
        设置场景数据（由场景管理器调用）
        
        Args:
            data: 场景数据
        """
        self._scene_data = data
        if 'winner' in data:
            self.winner = data['winner']
            # 更新 UI
            if self.ui_manager:
                winner_str = self.winner.value if self.winner else None
                self.ui_manager.update_component('game_over', winner_str)
    
    def handle_event(self, event: pygame.event.Event):
        """处理事件"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                # R 键重新开始
                print("[GameOver] 重新开始游戏")
                self.start_scene('Game')
            elif event.key == pygame.K_l:
                # L 键重新加载（回到 Boot 场景）
                print("[GameOver] 重新加载游戏")
                self.start_scene('Boot')
            elif event.key == pygame.K_ESCAPE:
                # ESC 退出游戏
                pygame.event.post(pygame.event.Event(pygame.QUIT))
    
    def render(self):
        """渲染游戏结束场景"""
        if not self.screen:
            return
        
        # 清空屏幕
        self.screen.fill((30, 30, 30))
        
        # 渲染 UI（使用 UIManager）
        if self.ui_manager:
            self.ui_manager.render()
    
    def destroy(self):
        """销毁场景"""
        if self.ui_manager:
            self.ui_manager.destroy_all()
        self.ui_manager = None
        super().destroy()
