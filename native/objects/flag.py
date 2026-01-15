"""
旗帜类
继承 pygame.sprite.Sprite 以支持碰撞检测
"""

import pygame
from ..utils import Team, TILE_SIZE, FLAG_SIZE
from ..utils.status import FlagStatus


class Flag(pygame.sprite.Sprite):
    """旗帜类"""
    
    def __init__(self, flag_id: str, team: Team, x: int, y: int):
        """
        初始化旗帜
        
        Args:
            flag_id: 旗帜ID
            team: 所属队伍
            x: X坐标（格子坐标）
            y: Y坐标（格子坐标）
        """
        super().__init__()
        self.flag_id = flag_id
        self.team = team
        self.belongs_to = team
        self.grid_x = x
        self.grid_y = y
        self.pixel_x = x * TILE_SIZE + TILE_SIZE // 2
        self.pixel_y = y * TILE_SIZE + TILE_SIZE // 2
        
        self.original_x = x
        self.original_y = y
        self.is_picked_up = False
        self.is_scored = False
        self.carried_by = None
        
        # pygame.sprite.Sprite 需要的 rect 属性
        self.rect = pygame.Rect(
            self.pixel_x - FLAG_SIZE // 2,
            self.pixel_y - FLAG_SIZE // 2,
            FLAG_SIZE,
            FLAG_SIZE
        )
    
    def belongs_to_team(self, team: Team) -> bool:
        """检查旗帜是否属于指定队伍"""
        return self.belongs_to == team
    
    def is_enemy_flag_for(self, team: Team) -> bool:
        """检查旗帜是否是指定队伍的敌方旗帜"""
        return self.belongs_to != team
    
    @property
    def can_pickup(self) -> bool:
        """是否可以拾取"""
        return not self.is_picked_up and not self.is_scored
    
    def pick_up_by(self, player):
        """被玩家拾取"""
        if self.can_pickup:
            self.is_picked_up = True
            self.carried_by = player
    
    def drop_at(self, x: int, y: int):
        """在指定位置放下旗帜"""
        self.is_picked_up = False
        self.carried_by = None
        self.grid_x = x
        self.grid_y = y
        self.pixel_x = x * TILE_SIZE + TILE_SIZE // 2
        self.pixel_y = y * TILE_SIZE + TILE_SIZE // 2
        
        # 更新 rect 位置
        self.rect.center = (self.pixel_x, self.pixel_y)
    
    def score(self):
        """得分"""
        self.is_scored = True
        self.is_picked_up = False
        self.carried_by = None
        self.grid_x = self.original_x
        self.grid_y = self.original_y
        self.pixel_x = self.original_x * TILE_SIZE + TILE_SIZE // 2
        self.pixel_y = self.original_y * TILE_SIZE + TILE_SIZE // 2
        
        # 更新 rect 位置
        self.rect.center = (self.pixel_x, self.pixel_y)
    
    def reset(self):
        """重置旗帜"""
        self.is_picked_up = False
        self.is_scored = False
        self.carried_by = None
        self.grid_x = self.original_x
        self.grid_y = self.original_y
        self.pixel_x = self.original_x * TILE_SIZE + TILE_SIZE // 2
        self.pixel_y = self.original_y * TILE_SIZE + TILE_SIZE // 2
        
        # 更新 rect 位置
        self.rect.center = (self.pixel_x, self.pixel_y)
    
    def update_position(self, player_pixel_x: float, player_pixel_y: float):
        """更新位置（当被携带时）"""
        if self.is_picked_up:
            self.pixel_x = player_pixel_x
            self.pixel_y = player_pixel_y
            self.grid_x = int(self.pixel_x / TILE_SIZE)
            self.grid_y = int(self.pixel_y / TILE_SIZE)
            
            # 更新 rect 位置
            self.rect.center = (self.pixel_x, self.pixel_y)
    
    def get_position(self) -> tuple[int, int]:
        """获取格子坐标"""
        return (self.grid_x, self.grid_y)
    
    def get_pixel_position(self) -> tuple[float, float]:
        """获取像素坐标"""
        return (self.pixel_x, self.pixel_y)

    def get_status(self) -> FlagStatus:
        """Get flag status matching frontend FlagStatus interface."""
        return FlagStatus(
            canPickup=self.can_pickup,
            posX=self.grid_x,
            posY=self.grid_y,
        )

    def __repr__(self) -> str:
        return f"Flag(id={self.flag_id}, team={self.team.value}, pos=({self.grid_x}, {self.grid_y}), picked_up={self.is_picked_up}, scored={self.is_scored})"

