"""
预加载场景
"""

import pygame
from .base_scene import BaseScene
from ..utils.assets import (
    CHARACTERS_SPRITESHEET, CHARACTERS_RED_FLAG, CHARACTERS_YELLOW_FLAG,
    RED_FLAG_IMG, YELLOW_FLAG_IMG, TILES_SPRITESHEET
)


class PreloaderScene(BaseScene):
    """
    预加载场景
    用于加载游戏资源，显示加载进度
    """
    
    def __init__(self, scene_manager):
        super().__init__('Preloader', scene_manager)
        self.font: pygame.font.Font = None
        self.small_font: pygame.font.Font = None
        self.progress = 0.0
        self.loading_text = "Loading assets..."
        self.assets_loaded = False
        self._switched = False  # 标记是否已切换到 Game
    
    def preload(self):
        """预加载资源"""
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 24)
        
        # 这里可以添加资源加载逻辑
        # 由于 pygame 是同步加载，我们直接在这里加载
        self._load_assets()
    
    def _load_assets(self):
        """加载游戏资源"""
        assets = [
            ("Characters", CHARACTERS_SPRITESHEET),
            ("Characters Red Flag", CHARACTERS_RED_FLAG),
            ("Characters Yellow Flag", CHARACTERS_YELLOW_FLAG),
            ("Red Flag", RED_FLAG_IMG),
            ("Yellow Flag", YELLOW_FLAG_IMG),
            ("Tiles", TILES_SPRITESHEET),
        ]
        
        total = len(assets)
        loaded = 0
        
        for name, path in assets:
            try:
                if path.exists():
                    # 尝试加载图片以验证文件
                        try:
                            img = pygame.image.load(str(path))
                            img.convert()  # 验证图片有效
                            loaded += 1
                            print(f"[Preloader] 已加载: {name}")
                        except pygame.error as e:
                            # pygame 可能缺少图像支持，但不影响游戏运行
                            print(f"[Preloader] 警告: 无法加载 {name} (将使用默认渲染): {e}")
                else:
                    print(f"[Preloader] 警告: {name} 文件不存在 ({path})")
            except Exception as e:
                print(f"[Preloader] 错误: 无法加载 {name}: {e}")
            
            self.progress = loaded / total
        
        self.assets_loaded = True
        print(f"[Preloader] 资源加载完成 ({loaded}/{total})")
    
    def create(self):
        """创建预加载场景"""
        # 不在这里切换场景，让 Preloader 至少渲染一帧
        print("[Preloader] 预加载场景已创建")
    
    def update(self, delta_time: int):
        """更新预加载场景"""
        # 如果资源已加载且未切换过，切换到游戏场景
        # 延迟一帧确保 Preloader 至少渲染了一次
        if self.assets_loaded and self.progress >= 1.0 and not self._switched:
            self._switched = True
            print("[Preloader] 资源加载完成，切换到 Game 场景")
            self.start_scene('Game')
    
    def render(self):
        """渲染预加载场景"""
        if not self.screen:
            return
        
        # 清空屏幕
        self.screen.fill((30, 30, 30))
        
        # 显示加载文本
        loading_text_surface = self.font.render(self.loading_text, True, (255, 255, 255))
        loading_rect = loading_text_surface.get_rect(
            center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 50)
        )
        self.screen.blit(loading_text_surface, loading_rect)
        
        # 显示进度条
        bar_width = 400
        bar_height = 30
        bar_x = (self.screen.get_width() - bar_width) // 2
        bar_y = self.screen.get_height() // 2
        
        # 背景
        pygame.draw.rect(self.screen, (100, 100, 100), 
                        (bar_x, bar_y, bar_width, bar_height))
        
        # 进度
        progress_width = int(bar_width * self.progress)
        pygame.draw.rect(self.screen, (0, 200, 0), 
                        (bar_x, bar_y, progress_width, bar_height))
        
        # 边框
        pygame.draw.rect(self.screen, (255, 255, 255), 
                        (bar_x, bar_y, bar_width, bar_height), 2)
        
        # 百分比文本
        percent_text = f"{int(self.progress * 100)}%"
        percent_surface = self.small_font.render(percent_text, True, (255, 255, 255))
        percent_rect = percent_surface.get_rect(
            center=(self.screen.get_width() // 2, bar_y + bar_height + 20)
        )
        self.screen.blit(percent_surface, percent_rect)

