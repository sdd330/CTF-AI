"""
玩家类
继承 pygame.sprite.Sprite 以支持碰撞检测
"""

import pygame
from typing import Optional
from ..utils import Team, Direction, PlayerState, TILE_SIZE, PLAYER_SIZE, PLAYER_SPEED, DEFAULT_PRISON_DURATION
from ..utils.assets import get_character_frame_index, CHARACTERS_SPRITESHEET, CHARACTERS_RED_FLAG, CHARACTERS_YELLOW_FLAG, SPRITE_SIZE


class Player(pygame.sprite.Sprite):
    """玩家类"""
    
    def __init__(self, name: str, team: Team, x: int, y: int):
        """
        初始化玩家
        
        Args:
            name: 玩家名称
            team: 所属队伍
            x: 初始X坐标（格子坐标）
            y: 初始Y坐标（格子坐标）
        """
        super().__init__()
        self.name = name
        self.team = team
        self.grid_x = x
        self.grid_y = y
        self.pixel_x = x * TILE_SIZE + TILE_SIZE // 2
        self.pixel_y = y * TILE_SIZE + TILE_SIZE // 2
        
        self.state = PlayerState.FREE
        self.has_flag = False
        self.in_prison = False
        self.prison_time_left = 0
        self.prison_duration = DEFAULT_PRISON_DURATION
        
        # 移动相关
        self.target_grid_x = x
        self.target_grid_y = y
        self.target_pixel_x = self.pixel_x
        self.target_pixel_y = self.pixel_y
        
        # 移动速度（像素/秒）
        self.move_speed = 300.0
        
        # 精灵图相关
        self.sprite_choice = 1 if team == Team.LEFT else 4  # L队默认1，R队默认4
        self.current_direction = "down"
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 100  # 动画切换速度（毫秒）- 与 frontend 保持一致（frameRate: 10 = 100ms/帧）
        
        # pygame.sprite.Sprite 需要的 rect 属性
        self.rect = pygame.Rect(
            self.pixel_x - PLAYER_SIZE // 2,
            self.pixel_y - PLAYER_SIZE // 2,
            PLAYER_SIZE,
            PLAYER_SIZE
        )
        
    def update(self, delta_time: int):
        """
        更新玩家状态
        
        Args:
            delta_time: 时间增量（毫秒）
        """
        # 更新监狱时间
        if self.in_prison:
            self.prison_time_left = max(0, self.prison_time_left - delta_time)
            if self.prison_time_left <= 0:
                self.in_prison = False
                self.state = PlayerState.FREE
                self.prison_time_left = 0
        
        # 移动逻辑
        if not self.in_prison:
            self._move_towards_target(delta_time)
            self._update_direction()
            
            # 检查是否正在移动（目标格子与当前格子不同，或者像素位置在移动）
            grid_moving = (self.target_grid_x != self.grid_x or 
                          self.target_grid_y != self.grid_y)
            pixel_moving = not self.is_at_target()
            is_moving = grid_moving or pixel_moving
            
            # 更新动画（只在移动时播放）
            if is_moving:
                # 玩家正在移动，播放动画
                self.animation_timer += delta_time
                if self.animation_timer >= self.animation_speed:
                    self.animation_timer = 0
                    self.animation_frame = (self.animation_frame + 1) % 3
            else:
                # 玩家静止，显示第一帧
                self.animation_frame = 0
                self.animation_timer = 0
    
    def _move_towards_target(self, delta_time: int):
        """
        向目标位置平滑移动
        
        Args:
            delta_time: 时间增量（毫秒）
        """
        dx = self.target_pixel_x - self.pixel_x
        dy = self.target_pixel_y - self.pixel_y
        
        # 如果已经到达目标，不移动
        EPSILON = 0.1
        if abs(dx) < EPSILON and abs(dy) < EPSILON:
            self.pixel_x = self.target_pixel_x
            self.pixel_y = self.target_pixel_y
            self.grid_x = self.target_grid_x
            self.grid_y = self.target_grid_y
            self.rect.center = (self.pixel_x, self.pixel_y)
            return
        
        # 计算移动距离（move_speed 是像素/秒，delta_time 是毫秒）
        move_distance = (self.move_speed * delta_time) / 1000.0
        
        # 计算移动方向
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance > 0:
            # 归一化方向向量
            move_x = (dx / distance) * min(move_distance, abs(dx))
            move_y = (dy / distance) * min(move_distance, abs(dy))
            
            self.pixel_x += move_x
            self.pixel_y += move_y
            
            # 更新 rect 位置
            self.rect.center = (self.pixel_x, self.pixel_y)
    
    def _update_direction(self):
        """更新移动方向（用于动画）"""
        dx = self.target_pixel_x - self.pixel_x
        dy = self.target_pixel_y - self.pixel_y
        
        if abs(dx) > abs(dy):
            self.current_direction = "right" if dx > 0 else "left"
        elif abs(dy) > 0:
            self.current_direction = "down" if dy > 0 else "up"
    
    def get_sprite_rect(self) -> tuple[int, int, int, int]:
        """
        获取当前精灵图矩形区域
        
        Returns:
            (x, y, width, height) 在精灵图中的位置
        """
        if self.in_prison:
            # 在监狱时显示静止状态
            direction = "down"
            frame = 0
        else:
            direction = self.current_direction
            frame = self.animation_frame
        
        x, y = get_character_frame_index(self.sprite_choice, direction, frame)
        return (x, y, SPRITE_SIZE, SPRITE_SIZE)
    
    def get_sprite_sheet_path(self) -> str:
        """获取当前使用的精灵图路径"""
        if self.has_flag:
            if self.team == Team.LEFT:
                return str(CHARACTERS_YELLOW_FLAG)
            else:
                return str(CHARACTERS_RED_FLAG)
        else:
            return str(CHARACTERS_SPRITESHEET)
    
    def set_direction(self, direction: Direction):
        """
        设置移动方向
        
        Args:
            direction: 移动方向
        """
        if self.in_prison:
            return
        
        dx, dy = direction.to_vector()
        if dx == 0 and dy == 0:
            return
        
        # 计算下一个目标位置
        next_grid_x = self.grid_x + dx
        next_grid_y = self.grid_y + dy
        
        self.target_grid_x = next_grid_x
        self.target_grid_y = next_grid_y
        self.target_pixel_x = self.target_grid_x * TILE_SIZE + TILE_SIZE // 2
        self.target_pixel_y = self.target_grid_y * TILE_SIZE + TILE_SIZE // 2
    
    def is_at_target(self) -> bool:
        """检查是否到达目标位置"""
        EPSILON = 0.1
        dx = abs(self.target_pixel_x - self.pixel_x)
        dy = abs(self.target_pixel_y - self.pixel_y)
        return dx < EPSILON and dy < EPSILON
    
    def pick_up_flag(self):
        """拾取旗帜"""
        if not self.in_prison:
            self.has_flag = True
            self.state = PlayerState.CARRYING_FLAG
    
    def drop_flag(self):
        """放下旗帜"""
        self.has_flag = False
        if self.state == PlayerState.CARRYING_FLAG:
            self.state = PlayerState.FREE
    
    def send_to_prison(self, prison_x: int, prison_y: int):
        """
        送入监狱（完全参考 frontend: toPrison）
        
        Frontend 逻辑：
        1. 设置目标位置
        2. 设置当前位置
        3. 设置 inPrison = true
        4. 设置 inPrisonTimeLeft = inPrisonDuration
        
        注意：frontend 中，旗帜在 handlePlayerHit 中已经处理，所以这里不需要处理旗帜
        
        Args:
            prison_x: 监狱X坐标（格子坐标）
            prison_y: 监狱Y坐标（格子坐标）
        """
        # 设置位置（参考 frontend: this.target.x = this.mapOffset.x + (prisonX * this.mapOffset.tileSize)）
        self.grid_x = prison_x
        self.grid_y = prison_y
        self.pixel_x = prison_x * TILE_SIZE + TILE_SIZE // 2
        self.pixel_y = prison_y * TILE_SIZE + TILE_SIZE // 2
        self.target_grid_x = prison_x
        self.target_grid_y = prison_y
        self.target_pixel_x = self.pixel_x
        self.target_pixel_y = self.pixel_y
        
        # 更新 rect 位置
        self.rect.center = (self.pixel_x, self.pixel_y)
        
        # 设置监狱状态（参考 frontend: this.inPrison = true, this.inPrisonTimeLeft = this.inPrisonDuration）
        self.in_prison = True
        self.state = PlayerState.IN_PRISON
        self.prison_time_left = self.prison_duration
        
        # 注意：frontend 中，旗帜在 handlePlayerHit 中已经处理（创建新旗帜并设置 hasFlag = false）
        # 所以这里不需要再次处理旗帜
    
    def get_position(self) -> tuple[int, int]:
        """获取格子坐标"""
        return (self.grid_x, self.grid_y)
    
    def get_pixel_position(self) -> tuple[float, float]:
        """获取像素坐标"""
        return (self.pixel_x, self.pixel_y)
    
    def __repr__(self) -> str:
        return f"Player(name={self.name}, team={self.team.value}, pos=({self.grid_x}, {self.grid_y}), state={self.state.value}, has_flag={self.has_flag})"

