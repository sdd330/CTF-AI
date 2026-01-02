"""
渲染器类
"""

import pygame
from typing import Tuple, Optional
from pathlib import Path
from ..utils import (
    TILE_SIZE, MAP_MARGIN, COLOR_LEFT_TEAM, COLOR_RIGHT_TEAM,
    COLOR_WALL, COLOR_TARGET_L, COLOR_TARGET_R, COLOR_PRISON_L, COLOR_PRISON_R,
    COLOR_FLAG_L, COLOR_FLAG_R, COLOR_BACKGROUND, COLOR_GRID, COLOR_TEXT,
    PLAYER_SIZE, FLAG_SIZE, Team
)
from ..utils.assets import (
    CHARACTERS_SPRITESHEET, CHARACTERS_RED_FLAG, CHARACTERS_YELLOW_FLAG,
    RED_FLAG_IMG, YELLOW_FLAG_IMG, TILES_SPRITESHEET, SPRITE_SIZE
)
from ..game.game import CTFGame
from ..map.map import GameMap
from ..managers.map_manager import MapManager


class Renderer:
    """渲染器类"""
    
    def __init__(self, game: CTFGame, screen_width: int, screen_height: int, map_manager: Optional[MapManager] = None):
        """
        初始化渲染器
        
        Args:
            game: 游戏实例
            screen_width: 屏幕宽度
            screen_height: 屏幕高度
            map_manager: 地图管理器（可选）
        """
        self.game = game
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.map_manager = map_manager
        
        # 计算地图显示区域
        # 如果有 MapManager，使用 MapManager 的地图位置和尺寸
        if map_manager and map_manager.map_width > 0 and map_manager.map_height > 0:
            self.map_offset_x = map_manager.map_x
            self.map_offset_y = map_manager.map_y
            self.map_pixel_width = map_manager.map_width * map_manager.tile_size
            self.map_pixel_height = map_manager.map_height * map_manager.tile_size
        else:
            # 否则使用默认边距和 game_map 的尺寸
            self.map_offset_x = MAP_MARGIN
            self.map_offset_y = MAP_MARGIN
            self.map_pixel_width = game.game_map.width * TILE_SIZE
            self.map_pixel_height = game.game_map.height * TILE_SIZE
        
        # 加载图片资源
        self._load_assets()
    
    def _load_assets(self):
        """加载游戏资源"""
        self.character_spritesheet: Optional[pygame.Surface] = None
        self.character_red_flag: Optional[pygame.Surface] = None
        self.character_yellow_flag: Optional[pygame.Surface] = None
        self.red_flag_img: Optional[pygame.Surface] = None
        self.yellow_flag_img: Optional[pygame.Surface] = None
        self.tiles_spritesheet: Optional[pygame.Surface] = None
        
        try:
            if CHARACTERS_SPRITESHEET.exists():
                try:
                    self.character_spritesheet = pygame.image.load(str(CHARACTERS_SPRITESHEET)).convert_alpha()
                except pygame.error:
                    print(f"警告：无法加载 {CHARACTERS_SPRITESHEET.name}，将使用默认渲染")
            if CHARACTERS_RED_FLAG.exists():
                try:
                    self.character_red_flag = pygame.image.load(str(CHARACTERS_RED_FLAG)).convert_alpha()
                except pygame.error:
                    pass
            if CHARACTERS_YELLOW_FLAG.exists():
                try:
                    self.character_yellow_flag = pygame.image.load(str(CHARACTERS_YELLOW_FLAG)).convert_alpha()
                except pygame.error:
                    pass
            if RED_FLAG_IMG.exists():
                try:
                    self.red_flag_img = pygame.image.load(str(RED_FLAG_IMG)).convert_alpha()
                except pygame.error:
                    pass
            if YELLOW_FLAG_IMG.exists():
                try:
                    self.yellow_flag_img = pygame.image.load(str(YELLOW_FLAG_IMG)).convert_alpha()
                except pygame.error:
                    pass
            if TILES_SPRITESHEET.exists():
                try:
                    self.tiles_spritesheet = pygame.image.load(str(TILES_SPRITESHEET)).convert_alpha()
                except pygame.error:
                    pass
        except Exception as e:
            print(f"警告：无法加载资源文件: {e}")
            print("将使用默认渲染方式")
    
    def render(self, screen: pygame.Surface):
        """
        渲染游戏
        
        Args:
            screen: pygame Surface对象
        """
        # 清空屏幕
        screen.fill(COLOR_BACKGROUND)
        
        # 渲染地图（包括背景、墙壁、障碍物、目标区域、监狱）
        self._render_map(screen)
        
        # 渲染目标区域和监狱（如果 MapManager 未渲染，使用回退方法）
        if not (self.map_manager and self.map_manager.ground_layer):
            self._render_areas(screen)
        
        # 渲染旗帜
        self._render_flags(screen)
        
        # 渲染玩家
        self._render_players(screen)
    
    def _render_map(self, screen: pygame.Surface):
        """渲染地图"""
        # 如果有 MapManager，使用它渲染地图
        if self.map_manager and self.map_manager.ground_layer:
            # 直接在地图区域渲染地图图层
            # 创建一个裁剪区域，只在地图范围内渲染
            clip_rect = pygame.Rect(
                self.map_offset_x, 
                self.map_offset_y,
                self.map_pixel_width,
                self.map_pixel_height
            )
            old_clip = screen.get_clip()
            screen.set_clip(clip_rect)
            
            # 渲染地图图层（直接渲染到屏幕，使用偏移量）
            # 获取目标区域和监狱位置
            # 注意：get_team_*_positions() 现在返回有序列表，顺序与 create_3x3_grid 一致
            left_target_positions = self.game.game_map.get_team_target_positions(Team.LEFT)
            right_target_positions = self.game.game_map.get_team_target_positions(Team.RIGHT)
            left_prison_positions = self.game.game_map.get_team_prison_positions(Team.LEFT)
            right_prison_positions = self.game.game_map.get_team_prison_positions(Team.RIGHT)
            
            # 直接转换为元组列表（保持顺序）
            left_target = [(pos.x, pos.y) for pos in left_target_positions]
            right_target = [(pos.x, pos.y) for pos in right_target_positions]
            left_prison = [(pos.x, pos.y) for pos in left_prison_positions]
            right_prison = [(pos.x, pos.y) for pos in right_prison_positions]
            
            # 获取障碍物
            obstacles_data = self.map_manager.get_obstacles()
            obstacles1 = obstacles_data.get("obstacles1", [])
            obstacles2 = obstacles_data.get("obstacles2", [])
            
            # 确保障碍物格式正确（从字典转换为元组）
            if obstacles1 and len(obstacles1) > 0 and isinstance(obstacles1[0], dict):
                obstacles1 = [(obs["x"], obs["y"]) for obs in obstacles1]
            if obstacles2 and len(obstacles2) > 0 and isinstance(obstacles2[0], dict):
                obstacles2 = [(obs["x"], obs["y"]) for obs in obstacles2]
            
            # 调试输出（仅第一次）
            if not hasattr(self, '_map_render_debug'):
                print(f"[Renderer] 渲染地图数据:")
                print(f"  left_target: {len(left_target)} 个 {left_target[:3] if left_target else '[]'}")
                print(f"  right_target: {len(right_target)} 个 {right_target[:3] if right_target else '[]'}")
                print(f"  left_prison: {len(left_prison)} 个 {left_prison[:3] if left_prison else '[]'}")
                print(f"  right_prison: {len(right_prison)} 个 {right_prison[:3] if right_prison else '[]'}")
                print(f"  obstacles1: {len(obstacles1)} 个 {obstacles1[:3] if obstacles1 else '[]'}")
                print(f"  obstacles2: {len(obstacles2)} 个 {obstacles2[:3] if obstacles2 else '[]'}")
                print(f"  offset: ({self.map_offset_x}, {self.map_offset_y})")
                print(f"  level_layer exists: {self.map_manager.level_layer is not None}")
                self._map_render_debug = True
            
            # 渲染地图（包括背景、墙壁、障碍物、目标区域、监狱）
            self.map_manager.render_map(
                screen, 
                offset_x=self.map_offset_x, 
                offset_y=self.map_offset_y,
                left_target=left_target,
                right_target=right_target,
                left_prison=left_prison,
                right_prison=right_prison,
                obstacles1=obstacles1,
                obstacles2=obstacles2
            )
            
            # 恢复裁剪区域
            screen.set_clip(old_clip)
            
            # MapManager 已经渲染了所有地图元素，不需要再调用 _render_areas 和 _render_walls
            return
        else:
            # 回退到网格渲染
            for x in range(self.game.game_map.width + 1):
                start_pos = (self.map_offset_x + x * TILE_SIZE, self.map_offset_y)
                end_pos = (self.map_offset_x + x * TILE_SIZE, 
                           self.map_offset_y + self.map_pixel_height)
                pygame.draw.line(screen, COLOR_GRID, start_pos, end_pos)
            
            for y in range(self.game.game_map.height + 1):
                start_pos = (self.map_offset_x, self.map_offset_y + y * TILE_SIZE)
                end_pos = (self.map_offset_x + self.map_pixel_width,
                           self.map_offset_y + y * TILE_SIZE)
                pygame.draw.line(screen, COLOR_GRID, start_pos, end_pos)
    
    def _render_areas(self, screen: pygame.Surface):
        """渲染目标区域和监狱"""
        # L队目标区域
        for pos in self.game.game_map.left_team_target:
            x = self.map_offset_x + pos.x * TILE_SIZE
            y = self.map_offset_y + pos.y * TILE_SIZE
            pygame.draw.rect(screen, COLOR_TARGET_L, 
                           (x, y, TILE_SIZE, TILE_SIZE))
        
        # R队目标区域
        for pos in self.game.game_map.right_team_target:
            x = self.map_offset_x + pos.x * TILE_SIZE
            y = self.map_offset_y + pos.y * TILE_SIZE
            pygame.draw.rect(screen, COLOR_TARGET_R, 
                           (x, y, TILE_SIZE, TILE_SIZE))
        
        # L队监狱
        for pos in self.game.game_map.left_team_prison:
            x = self.map_offset_x + pos.x * TILE_SIZE
            y = self.map_offset_y + pos.y * TILE_SIZE
            pygame.draw.rect(screen, COLOR_PRISON_L, 
                           (x, y, TILE_SIZE, TILE_SIZE))
        
        # R队监狱
        for pos in self.game.game_map.right_team_prison:
            x = self.map_offset_x + pos.x * TILE_SIZE
            y = self.map_offset_y + pos.y * TILE_SIZE
            pygame.draw.rect(screen, COLOR_PRISON_R, 
                           (x, y, TILE_SIZE, TILE_SIZE))
    
    def _render_walls(self, screen: pygame.Surface):
        """渲染墙壁"""
        for wall in self.game.game_map.walls:
            x = self.map_offset_x + wall.x * TILE_SIZE
            y = self.map_offset_y + wall.y * TILE_SIZE
            pygame.draw.rect(screen, COLOR_WALL, 
                           (x, y, TILE_SIZE, TILE_SIZE))
    
    def _render_flags(self, screen: pygame.Surface):
        """渲染旗帜"""
        for flag in self.game.state.get_all_flags():
            # 如果已得分，需要判断是原旗帜还是新创建的得分旗帜
            if flag.is_scored:
                # 检查是否在目标区域内
                # 如果在目标区域内，说明是新创建的得分旗帜（需要渲染）
                # 如果不在目标区域内，说明是原旗帜回到了初始位置（不渲染）
                is_in_target = False
                from ..map.map import Position
                flag_pos = Position(flag.grid_x, flag.grid_y)
                
                # 检查是否在L队或R队目标区域内
                if (flag_pos in self.game.game_map.left_team_target_set or 
                    flag_pos in self.game.game_map.right_team_target_set):
                    is_in_target = True
                
                # 如果不在目标区域内，说明是原旗帜（不渲染）
                if not is_in_target:
                    continue
            
            x = self.map_offset_x + flag.pixel_x - FLAG_SIZE // 2
            y = self.map_offset_y + flag.pixel_y - FLAG_SIZE // 2
            
            # 使用图片资源
            flag_img = None
            if flag.team.value == "L" and self.red_flag_img:
                flag_img = self.red_flag_img
            elif flag.team.value == "R" and self.yellow_flag_img:
                flag_img = self.yellow_flag_img
            
            if flag_img:
                # 缩放图片到合适大小
                scaled_img = pygame.transform.scale(flag_img, (FLAG_SIZE, FLAG_SIZE))
                # 正常渲染，不设置半透明
                screen.blit(scaled_img, (x, y))
            else:
                # 回退到默认渲染
                color = COLOR_FLAG_L if flag.team.value == "L" else COLOR_FLAG_R
                pygame.draw.rect(screen, color, (x, y, FLAG_SIZE, FLAG_SIZE))
            
            # 如果被拾取，画一个小标记
            if flag.is_picked_up:
                pygame.draw.circle(screen, (255, 255, 0), 
                                 (int(x + FLAG_SIZE // 2), int(y + FLAG_SIZE // 2)), 
                                 FLAG_SIZE // 4, 2)
    
    def _render_players(self, screen: pygame.Surface):
        """渲染玩家"""
        for player in self.game.state.get_all_players():
            x = self.map_offset_x + player.pixel_x - PLAYER_SIZE // 2
            y = self.map_offset_y + player.pixel_y - PLAYER_SIZE // 2
            
            # 使用精灵图渲染
            sprite_sheet = None
            if player.has_flag:
                if player.team.value == "L" and self.character_yellow_flag:
                    sprite_sheet = self.character_yellow_flag
                elif player.team.value == "R" and self.character_red_flag:
                    sprite_sheet = self.character_red_flag
            
            if not sprite_sheet and self.character_spritesheet:
                sprite_sheet = self.character_spritesheet
            
            if sprite_sheet:
                # 获取精灵图矩形区域
                sprite_rect = player.get_sprite_rect()
                sprite_x, sprite_y, sprite_w, sprite_h = sprite_rect
                
                # 获取 sprite sheet 的实际大小
                sheet_width, sheet_height = sprite_sheet.get_size()
                
                # 检查边界，确保不超出 sprite sheet 范围
                if sprite_x + sprite_w > sheet_width:
                    sprite_x = max(0, sheet_width - sprite_w)
                if sprite_y + sprite_h > sheet_height:
                    sprite_y = max(0, sheet_height - sprite_h)
                
                # 确保坐标不为负
                sprite_x = max(0, sprite_x)
                sprite_y = max(0, sprite_y)
                
                # 确保宽度和高度不超过剩余空间
                sprite_w = min(sprite_w, sheet_width - sprite_x)
                sprite_h = min(sprite_h, sheet_height - sprite_y)
                
                # 从精灵图中提取当前帧
                try:
                    sprite_surface = sprite_sheet.subsurface(pygame.Rect(sprite_x, sprite_y, sprite_w, sprite_h))
                except (ValueError, pygame.error) as e:
                    # 如果仍然失败，使用默认渲染
                    print(f"[Renderer] 警告：无法提取精灵图 ({sprite_x}, {sprite_y}, {sprite_w}, {sprite_h})，使用默认渲染: {e}")
                    sprite_surface = None
                
                if sprite_surface:
                    # 如果在监狱，变暗
                    if player.in_prison:
                        sprite_surface = sprite_surface.copy()
                        sprite_surface.set_alpha(128)
                    
                    # 缩放并渲染
                    scaled_sprite = pygame.transform.scale(sprite_surface, (PLAYER_SIZE, PLAYER_SIZE))
                    screen.blit(scaled_sprite, (x, y))
                else:
                    # 如果提取失败，使用默认渲染
                    sprite_sheet = None
            else:
                # 回退到默认渲染
                color = COLOR_LEFT_TEAM if player.team.value == "L" else COLOR_RIGHT_TEAM
                
                # 如果在监狱，用不同颜色
                if player.in_prison:
                    color = tuple(max(0, c - 100) for c in color)
                
                # 绘制玩家
                pygame.draw.circle(screen, color, 
                                 (int(x + PLAYER_SIZE // 2), int(y + PLAYER_SIZE // 2)),
                                 PLAYER_SIZE // 2)
            
            # 如果有旗帜，画一个标记
            if player.has_flag and not sprite_sheet:
                pygame.draw.circle(screen, (255, 255, 0),
                                 (int(x + PLAYER_SIZE // 2), int(y + PLAYER_SIZE // 2)),
                                 PLAYER_SIZE // 3, 2)
            

