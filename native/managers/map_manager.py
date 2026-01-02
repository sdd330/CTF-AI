"""
地图管理器
直接使用 tiles.png spritesheet

职责：
- 管理地图参数（mapWidth, mapHeight, mapX, mapY, tileSize, centerX, centerY）
- 生成地图数据（墙壁、障碍物）
- 渲染地图图层（背景、关卡、边界）
- 提供地图数据访问接口

设计模式：单例模式 + 组合模式 + 享元模式
"""

import pygame
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Set, Any
from abc import ABC, abstractmethod
from ..utils import Team, TILE_SIZE
from ..utils.assets import TILES_SPRITESHEET
from ..map.map import GameMap, Position


class MapLayer(ABC):
    """
    地图图层接口（组合模式）
    """
    
    @abstractmethod
    def render(self, surface: pygame.Surface, offset_x: int = 0, offset_y: int = 0):
        """渲染图层"""
        pass
    
    @abstractmethod
    def update(self, delta_time: int):
        """更新图层"""
        pass
    
    @abstractmethod
    def destroy(self):
        """销毁图层"""
        pass


class TileData:
    """
    图块数据（享元模式）
    缓存图块数据，避免重复创建
    """
    
    _cache: Dict[int, 'TileData'] = {}
    
    def __init__(self, tile_id: int, is_collidable: bool = False):
        self.tile_id = tile_id
        self.is_collidable = is_collidable
    
    @classmethod
    def get_tile_data(cls, tile_id: int, is_collidable: bool = False) -> 'TileData':
        """
        获取图块数据（享元工厂方法）
        
        Args:
            tile_id: 图块ID
            is_collidable: 是否可碰撞
        
        Returns:
            TileData 实例
        """
        key = tile_id * 1000 + (1 if is_collidable else 0)
        if key not in cls._cache:
            cls._cache[key] = cls(tile_id, is_collidable)
        return cls._cache[key]


class GroundLayer(MapLayer):
    """
    背景图层
    使用 backgroundTiles 随机填充整个地图
    """
    
    def __init__(self, tiles_image: pygame.Surface, map_width: int, map_height: int, tile_size: int = 32):
        """
        初始化背景图层
        
        Args:
            tiles_image: tiles.png 图片 Surface（spritesheet）
            map_width: 地图宽度（格子数）
            map_height: 地图高度（格子数）
            tile_size: 瓦片大小（默认 32x32）
        """
        import random
        
        self.tiles_image = tiles_image
        self.map_width = map_width
        self.map_height = map_height
        self.tile_width = tile_size
        self.tile_height = tile_size
        
        # tiles.png 的布局：12 列 x 11 行 = 132 个瓦片
        self.tiles_per_row = 12
        
        self.background_tiles = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 3, 44]
        
        self.generated_tiles = {}
        for y in range(map_height):
            for x in range(map_width):
                # 随机选择背景图块
                tile_index = random.choice(self.background_tiles)
                self.generated_tiles[(x, y)] = tile_index
        
        # 预提取瓦片图像（缓存）
        self._tile_cache = {}
        for tile_index in set(self.background_tiles):
            self._extract_tile(tile_index)
    
    def _extract_tile(self, tile_index: int) -> Optional[pygame.Surface]:
        """
        从 tiles.png 中提取指定索引的瓦片
        
        Args:
            tile_index: 瓦片索引（1-based）
        
        Returns:
            瓦片 Surface 或 None
        """
        if tile_index in self._tile_cache:
            return self._tile_cache[tile_index]
        
        # tile_index 从 1 开始，转换为 0-based
        index = tile_index - 1
        
        # 计算瓦片在 spritesheet 中的位置
        row = index // self.tiles_per_row
        col = index % self.tiles_per_row
        
        # 计算像素坐标
        x = col * self.tile_width
        y = row * self.tile_height
        
        # 检查边界
        if (x + self.tile_width <= self.tiles_image.get_width() and 
            y + self.tile_height <= self.tiles_image.get_height()):
            try:
                tile = self.tiles_image.subsurface((x, y, self.tile_width, self.tile_height))
                self._tile_cache[tile_index] = tile
                return tile
            except Exception as e:
                # 调试：输出提取失败的原因（仅 LevelLayer 输出，避免 GroundLayer 输出太多）
                if hasattr(self, 'target_tiles') and not hasattr(self, '_extract_error_logged'):
                    print(f"[LevelLayer] 提取 tile {tile_index} 失败: {e}, "
                          f"位置=(row={row}, col={col}, pixel=({x}, {y})), "
                          f"图片尺寸=({self.tiles_image.get_width()}, {self.tiles_image.get_height()})")
                    self._extract_error_logged = True
        else:
            # 调试：输出边界检查失败（仅 LevelLayer 输出）
            if hasattr(self, 'target_tiles') and not hasattr(self, '_extract_error_logged'):
                print(f"[LevelLayer] tile {tile_index} 超出边界: "
                      f"位置=(row={row}, col={col}, pixel=({x}, {y})), "
                      f"图片尺寸=({self.tiles_image.get_width()}, {self.tiles_image.get_height()})")
                self._extract_error_logged = True
        
        return None
    
    def render(self, surface: pygame.Surface, offset_x: int = 0, offset_y: int = 0):
        """渲染背景图层"""
        for (x, y), tile_index in self.generated_tiles.items():
            tile = self._extract_tile(tile_index)
            if tile:
                # offset_x 和 offset_y 是地图的起始位置，应该加上而不是减去
                pixel_x = offset_x + x * self.tile_width
                pixel_y = offset_y + y * self.tile_height
                surface.blit(tile, (pixel_x, pixel_y))
    
    def update(self, delta_time: int):
        """背景图层不需要更新"""
        pass
    
    def destroy(self):
        """销毁图层"""
        self.generated_tiles = None
        self._tile_cache = None


class LevelLayer(MapLayer):
    """
    关卡图层（组合模式：包含多个子图层）
    渲染墙壁、障碍物、目标区域、监狱等
    """
    
    def __init__(self, tiles_image: pygame.Surface, map_width: int, map_height: int, tile_size: int = 32):
        """
        初始化关卡图层
        
        Args:
            tiles_image: tiles.png 图片 Surface（spritesheet）
            map_width: 地图宽度（格子数）
            map_height: 地图高度（格子数）
            tile_size: 瓦片大小（默认 32x32）
        """
        self.tiles_image = tiles_image
        self.map_width = map_width
        self.map_height = map_height
        self.tile_width = tile_size
        self.tile_height = tile_size
        
        # tiles.png 的布局：12 列 x 11 行 = 132 个瓦片
        self.tiles_per_row = 12
        
        # 墙壁位置
        self.walls: List[Dict[str, Any]] = []
        
        # 图块ID配置
        self.wall_tiles: List[int] = [45, 46, 47, 57, 59, 69, 70, 71]
        self.target_tiles: List[int] = [13, 14, 15, 25, 26, 27, 37, 38, 39]
        self.prison_tiles: List[int] = [97, 98, 99, 109, 110, 111, 121, 122, 123]
        self.tree1_tiles: List[int] = [6, 18, 30, 29, 28]
        self.tree2_tiles: List[List[int]] = [[4, 16], [5, 17]]
        
        # 瓦片缓存
        self._tile_cache: Dict[int, Optional[pygame.Surface]] = {}
        
        # 障碍物瓦片缓存（参考 frontend：只在初始化时随机选择一次）
        # Frontend 的 renderObstacles 只在 renderMap() 中调用一次（初始化时）
        # 之后 Phaser 自动渲染，tile.index 保持不变
        # Native 需要每帧手动 blit，所以需要缓存瓦片 ID
        self._obstacle_tile_cache: Dict[Tuple[int, int], int] = {}
        self._obstacle2_tile_cache: Dict[Tuple[int, int], List[int]] = {}
    
    def _extract_tile(self, tile_index: int) -> Optional[pygame.Surface]:
        """
        从 tiles.png 中提取指定索引的瓦片
        
        Args:
            tile_index: 瓦片索引（1-based）
        
        Returns:
            瓦片 Surface 或 None
        """
        if tile_index in self._tile_cache:
            return self._tile_cache[tile_index]
        
        # tile_index 从 1 开始，转换为 0-based
        index = tile_index - 1
        
        # 计算瓦片在 spritesheet 中的位置
        row = index // self.tiles_per_row
        col = index % self.tiles_per_row
        
        # 计算像素坐标
        x = col * self.tile_width
        y = row * self.tile_height
        
        # 检查边界
        if (x + self.tile_width <= self.tiles_image.get_width() and 
            y + self.tile_height <= self.tiles_image.get_height()):
            try:
                tile = self.tiles_image.subsurface((x, y, self.tile_width, self.tile_height))
                self._tile_cache[tile_index] = tile
                return tile
            except Exception as e:
                # 调试：输出提取失败的原因（仅 LevelLayer 输出，避免 GroundLayer 输出太多）
                if hasattr(self, 'target_tiles') and not hasattr(self, '_extract_error_logged'):
                    print(f"[LevelLayer] 提取 tile {tile_index} 失败: {e}, "
                          f"位置=(row={row}, col={col}, pixel=({x}, {y})), "
                          f"图片尺寸=({self.tiles_image.get_width()}, {self.tiles_image.get_height()})")
                    self._extract_error_logged = True
        else:
            # 调试：输出边界检查失败（仅 LevelLayer 输出）
            if hasattr(self, 'target_tiles') and not hasattr(self, '_extract_error_logged'):
                print(f"[LevelLayer] tile {tile_index} 超出边界: "
                      f"位置=(row={row}, col={col}, pixel=({x}, {y})), "
                      f"图片尺寸=({self.tiles_image.get_width()}, {self.tiles_image.get_height()})")
                self._extract_error_logged = True
        
        return None
    
    def set_walls(self, walls: List[Dict[str, Any]]):
        """
        设置墙壁
        
        Args:
            walls: 墙壁列表，每个元素包含 x, y, tileId（可选）
        """
        self.walls = walls
    
    def render(self, surface: pygame.Surface, offset_x: int = 0, offset_y: int = 0):
        """渲染关卡图层（不在这里渲染，由外部调用具体的渲染方法）"""
        # 参考 frontend: render() 方法为空，由外部调用 renderWalls, renderPrisons 等
        pass
    
    def render_walls(self, surface: pygame.Surface, offset_x: int = 0, offset_y: int = 0):
        """渲染墙壁（参考 frontend: renderWalls）"""
        rendered_count = 0
        failed_count = 0
        
        for wall in self.walls:
            x = wall.get("x", 0)
            y = wall.get("y", 0)
            tile_id = wall.get("tileId", self.wall_tiles[0] if self.wall_tiles else 0)
            
            if tile_id > 0:
                tile = self._extract_tile(tile_id)
                if tile:
                    pixel_x = offset_x + x * self.tile_width
                    pixel_y = offset_y + y * self.tile_height
                    # 调试：输出前几个墙壁的位置
                    if rendered_count < 3 and not hasattr(self, '_walls_render_debug'):
                        print(f"[LevelLayer] 墙壁 {rendered_count}: 格子=({x}, {y}), 像素=({pixel_x}, {pixel_y}), tile_id={tile_id}")
                    surface.blit(tile, (pixel_x, pixel_y))
                    rendered_count += 1
                else:
                    failed_count += 1
                    # 调试：输出失败的瓦片ID
                    if not hasattr(self, '_walls_render_debug'):
                        print(f"[LevelLayer] 警告：无法提取墙壁瓦片 tile_id={tile_id}, 位置=({x}, {y})")
        
        # 调试输出（仅第一次）
        if not hasattr(self, '_walls_render_debug'):
            print(f"[LevelLayer] 渲染墙壁: 总数={len(self.walls)}, 成功={rendered_count}, 失败={failed_count}")
            print(f"[LevelLayer] offset=({offset_x}, {offset_y}), tile_size=({self.tile_width}, {self.tile_height})")
            if failed_count > 0:
                print(f"[LevelLayer] 警告：{failed_count} 个墙壁瓦片提取失败")
            self._walls_render_debug = True
    
    def render_targets(self, surface: pygame.Surface, 
                      left_target: List[Tuple[int, int]], 
                      right_target: List[Tuple[int, int]],
                      offset_x: int = 0, offset_y: int = 0):
        """
        渲染目标区域（完全参考 frontend: renderTargets）
        
        Frontend 实现:
        renderTargets(lTeamTarget: Position[], rTeamTarget: Position[]): void {
          lTeamTarget.forEach((target, i) => {
            const tile = this.layer.getTileAt(target.x, target.y)
            if (tile && i < this.targetTiles.length) {
              tile.index = this.targetTiles[i]
            }
          })
          rTeamTarget.forEach((target, i) => {
            const tile = this.layer.getTileAt(target.x, target.y)
            if (tile && i < this.targetTiles.length) {
              tile.index = this.targetTiles[i]
            }
          })
        }
        
        Frontend targetTiles: [13, 14, 15, 25, 26, 27, 37, 38, 39]
        Frontend create3x3grid 顺序: [0] (x-1, y-1), ..., [6] (x-1, y+1)
        """
        # 调试：输出渲染信息（仅第一次）
        if not hasattr(self, '_target_render_debug'):
            print(f"[LevelLayer] 开始渲染目标区域: L队={len(left_target)}个, R队={len(right_target)}个")
            print(f"[LevelLayer] target_tiles={self.target_tiles}")
            self._target_render_debug = True
        
        l_success = 0
        l_failed = 0
        for i, (x, y) in enumerate(left_target):
            if i < len(self.target_tiles):
                tile_id = self.target_tiles[i]
                tile = self._extract_tile(tile_id)
                if tile:
                    pixel_x = offset_x + x * self.tile_width
                    pixel_y = offset_y + y * self.tile_height
                    surface.blit(tile, (pixel_x, pixel_y))
                    l_success += 1
                else:
                    # 调试：输出提取失败的 tile
                    row, col = (tile_id - 1) // self.tiles_per_row, (tile_id - 1) % self.tiles_per_row
                    print(f"[LevelLayer] 警告：无法提取 L 队目标 tile_id={tile_id}, 位置=({x}, {y}), index={i}, "
                          f"spritesheet位置=(row={row}, col={col}, pixel=({col*32}, {row*32}))")
                    l_failed += 1
        
        r_success = 0
        r_failed = 0
        for i, (x, y) in enumerate(right_target):
            if i < len(self.target_tiles):
                tile_id = self.target_tiles[i]
                tile = self._extract_tile(tile_id)
                if tile:
                    pixel_x = offset_x + x * self.tile_width
                    pixel_y = offset_y + y * self.tile_height
                    surface.blit(tile, (pixel_x, pixel_y))
                    r_success += 1
                else:
                    # 调试：输出提取失败的 tile
                    row, col = (tile_id - 1) // self.tiles_per_row, (tile_id - 1) % self.tiles_per_row
                    print(f"[LevelLayer] 警告：无法提取 R 队目标 tile_id={tile_id}, 位置=({x}, {y}), index={i}, "
                          f"spritesheet位置=(row={row}, col={col}, pixel=({col*32}, {row*32}))")
                    r_failed += 1
        
        # 调试：输出渲染结果（仅第一次）
        if not hasattr(self, '_target_render_result_logged'):
            print(f"[LevelLayer] 目标区域渲染完成: L队成功={l_success}, 失败={l_failed}, R队成功={r_success}, 失败={r_failed}")
            # 输出前几个位置的详细信息
            if left_target:
                print(f"[LevelLayer] L队目标位置示例: {left_target[:3]} -> tile_ids={self.target_tiles[:3]}")
            if right_target:
                print(f"[LevelLayer] R队目标位置示例: {right_target[:3]} -> tile_ids={self.target_tiles[:3]}")
            self._target_render_result_logged = True
    
    def render_prisons(self, surface: pygame.Surface,
                      left_prison: List[Tuple[int, int]],
                      right_prison: List[Tuple[int, int]],
                      offset_x: int = 0, offset_y: int = 0):
        """渲染监狱区域（参考 frontend: renderPrisons）"""
        # Frontend 的 create3x3grid 顺序：
        # [0] (x-1, y-1), [1] (x, y-1), [2] (x+1, y-1)
        # [3] (x-1, y),   [4] (x, y),   [5] (x+1, y)
        # [6] (x-1, y+1), [7] (x, y+1), [8] (x+1, y+1)
        # prisonTiles 也是按这个顺序：[97, 98, 99, 109, 110, 111, 121, 122, 123]
        for i, (x, y) in enumerate(left_prison):
            if i < len(self.prison_tiles):
                tile_id = self.prison_tiles[i]
                tile = self._extract_tile(tile_id)
                if tile:
                    pixel_x = offset_x + x * self.tile_width
                    pixel_y = offset_y + y * self.tile_height
                    surface.blit(tile, (pixel_x, pixel_y))
                elif not hasattr(self, '_prison_extract_debug'):
                    # 调试：输出提取失败的 tile
                    row, col = (tile_id - 1) // self.tiles_per_row, (tile_id - 1) % self.tiles_per_row
                    print(f"[LevelLayer] 警告：无法提取 L 队监狱 tile_id={tile_id}, 位置=({x}, {y}), index={i}, "
                          f"spritesheet位置=(row={row}, col={col}, pixel=({col*32}, {row*32}))")
        
        for i, (x, y) in enumerate(right_prison):
            if i < len(self.prison_tiles):
                tile_id = self.prison_tiles[i]
                tile = self._extract_tile(tile_id)
                if tile:
                    pixel_x = offset_x + x * self.tile_width
                    pixel_y = offset_y + y * self.tile_height
                    surface.blit(tile, (pixel_x, pixel_y))
                elif not hasattr(self, '_prison_extract_debug'):
                    # 调试：输出提取失败的 tile
                    row, col = (tile_id - 1) // self.tiles_per_row, (tile_id - 1) % self.tiles_per_row
                    print(f"[LevelLayer] 警告：无法提取 R 队监狱 tile_id={tile_id}, 位置=({x}, {y}), index={i}, "
                          f"spritesheet位置=(row={row}, col={col}, pixel=({col*32}, {row*32}))")
        
        if not hasattr(self, '_prison_extract_debug'):
            print(f"[LevelLayer] 渲染监狱区域: left={len(left_prison)}, right={len(right_prison)}")
            # 输出前几个位置的详细信息
            if left_prison:
                print(f"[LevelLayer] L队监狱位置示例: {left_prison[:3]} -> tile_ids={self.prison_tiles[:3]}")
            if right_prison:
                print(f"[LevelLayer] R队监狱位置示例: {right_prison[:3]} -> tile_ids={self.prison_tiles[:3]}")
            self._prison_extract_debug = True
    
    def render_obstacles(self, surface: pygame.Surface,
                        obstacles1: List[Tuple[int, int]],
                        obstacles2: List[Tuple[int, int]],
                        offset_x: int = 0, offset_y: int = 0):
        """
        渲染障碍物（参考 frontend: renderObstacles）
        
        Frontend 实现:
        renderObstacles(obstacles1: Position[], obstacles2: Position[]): void {
          obstacles1.forEach(obs => {
            const tile = this.layer.getTileAt(obs.x, obs.y)
            if (tile) {
              tile.index = Phaser.Math.RND.pick(this.tree1Tiles)
            }
          })
          obstacles2.forEach(obs => {
            const treeTile = Phaser.Math.RND.pick(this.tree2Tiles)
            const tile1 = this.layer.getTileAt(obs.x, obs.y)
            const tile2 = this.layer.getTileAt(obs.x, obs.y + 1)
            if (tile1 && tile2) {
              tile1.index = treeTile[0]
              tile2.index = treeTile[1]
            }
          })
        }
        
        注意：Frontend 只在初始化时调用一次，之后 tile.index 保持不变
        所以我们需要缓存每个障碍物的瓦片 ID，避免每帧重新随机选择
        """
        import random
        
        # 障碍物瓦片缓存已在 __init__ 中初始化
        # 参考 frontend：renderObstacles 只在初始化时调用一次
        # 之后 tile.index 保持不变，Phaser 自动渲染
        # Native 需要每帧手动 blit，所以使用缓存避免每帧重新随机选择
        
        for x, y in obstacles1:
            pos = (x, y)
            # 如果缓存中没有，随机选择一个并缓存
            if pos not in self._obstacle_tile_cache:
                self._obstacle_tile_cache[pos] = random.choice(self.tree1_tiles)
            
            tile_id = self._obstacle_tile_cache[pos]
            tile = self._extract_tile(tile_id)
            if tile:
                pixel_x = offset_x + x * self.tile_width
                pixel_y = offset_y + y * self.tile_height
                surface.blit(tile, (pixel_x, pixel_y))
        
        for x, y in obstacles2:
            pos = (x, y)
            # 如果缓存中没有，随机选择一个并缓存
            if pos not in self._obstacle2_tile_cache:
                self._obstacle2_tile_cache[pos] = random.choice(self.tree2_tiles)
            
            tree_tile = self._obstacle2_tile_cache[pos]
            tile1 = self._extract_tile(tree_tile[0])
            if tile1:
                pixel_x = offset_x + x * self.tile_width
                pixel_y = offset_y + y * self.tile_height
                surface.blit(tile1, (pixel_x, pixel_y))
            tile2 = self._extract_tile(tree_tile[1])
            if tile2:
                pixel_x = offset_x + x * self.tile_width
                pixel_y = offset_y + (y + 1) * self.tile_height
                surface.blit(tile2, (pixel_x, pixel_y))
    
    def is_wall(self, x: int, y: int) -> bool:
        """
        检查位置是否是墙
        
        Args:
            x: X坐标（格子坐标）
            y: Y坐标（格子坐标）
        
        Returns:
            如果是墙返回True
        """
        # 检查是否在墙壁列表中
        for wall in self.walls:
            if wall.get("x") == x and wall.get("y") == y:
                return True
        
        return False
    
    def get_tile_at(self, x: int, y: int) -> Optional[Dict[str, Any]]:
        """
        获取指定位置的图块信息
        
        Args:
            x: X坐标（格子坐标）
            y: Y坐标（格子坐标）
        
        Returns:
            图块信息字典
        """
        if not (0 <= x < self.map_width and 0 <= y < self.map_height):
            return None
        
        # 检查是否在墙壁列表中
        for wall in self.walls:
            if wall.get("x") == x and wall.get("y") == y:
                return {
                    "gid": wall.get("tileId", 0),
                    "x": x,
                    "y": y,
                    "is_wall": True
                }
        
        return None
    
    def update(self, delta_time: int):
        """关卡图层不需要更新"""
        pass
    
    def destroy(self):
        """销毁图层"""
        self._tile_cache = None


class BoundaryLayer(MapLayer):
    """
    边界图层
    渲染地图边界线
    """
    
    def __init__(self, center_x: int, start_y: int, end_y: int, color: Tuple[int, int, int] = (0, 0, 0)):
        """
        初始化边界图层
        
        Args:
            center_x: 中心线X坐标
            start_y: 起始Y坐标
            end_y: 结束Y坐标
            color: 线条颜色
        """
        self.center_x = center_x
        self.start_y = start_y
        self.end_y = end_y
        self.color = color
    
    def render(self, surface: pygame.Surface, offset_x: int = 0, offset_y: int = 0):
        """渲染边界线"""
        pygame.draw.line(surface, self.color,
                        (self.center_x - offset_x, self.start_y - offset_y),
                        (self.center_x - offset_x, self.end_y - offset_y),
                        1)
    
    def update(self, delta_time: int):
        """边界不需要更新"""
        pass
    
    def destroy(self):
        """销毁图层"""
        pass


class MapManager:
    """地图管理器（单例模式）"""
    
    _instance: Optional['MapManager'] = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化地图管理器"""
        # 避免重复初始化
        if hasattr(self, '_initialized'):
            return
        
        # 地图渲染相关属性
        self.layers: List[MapLayer] = []
        self.ground_layer: Optional[GroundLayer] = None
        self.level_layer: Optional[LevelLayer] = None
        self.boundary_layer: Optional[BoundaryLayer] = None
        
        # 地图参数（由 MapManager 统一管理）
        self.map_x: int = 0
        self.map_y: int = 0
        self.map_width: int = 0
        self.map_height: int = 0
        self.tile_size: int = TILE_SIZE
        self.center_x: int = 0
        self.center_y: int = 0
        
        # 游戏地图对象
        self.game_map: Optional[GameMap] = None
        
        self._initialized = True
    
    def initialize_layers(self, tiles_image: Optional[pygame.Surface] = None):
        """
        初始化地图图层
        
        Args:
            tiles_image: tiles.png 图片 Surface（如果为 None，则从文件加载）
        """
        # 如果没有传入 tiles_image，从文件加载
        if tiles_image is None:
            if TILES_SPRITESHEET.exists():
                try:
                    tiles_image = pygame.image.load(str(TILES_SPRITESHEET)).convert_alpha()
                    print(f"[MapManager] 从文件加载 tiles.png: {TILES_SPRITESHEET}")
                except Exception as e:
                    print(f"[MapManager] 无法加载 tiles.png: {e}")
                    return
            else:
                print(f"[MapManager] 错误：tiles.png 不存在: {TILES_SPRITESHEET}")
                return
        
        # 创建背景图层
        try:
            self.ground_layer = GroundLayer(
                tiles_image,
                self.map_width, 
                self.map_height,
                self.tile_size
            )
            self.layers.append(self.ground_layer)
            print(f"[MapManager] 背景图层创建成功: {self.map_width}x{self.map_height}")
        except Exception as e:
            print(f"[MapManager] 创建背景图层失败: {e}")
            import traceback
            traceback.print_exc()
        
        # 创建关卡图层
        try:
            self.level_layer = LevelLayer(
                tiles_image,
                self.map_width,
                self.map_height,
                self.tile_size
            )
            self.layers.append(self.level_layer)
            print(f"[MapManager] 关卡图层创建成功: {self.map_width}x{self.map_height}")
        except Exception as e:
            print(f"[MapManager] 创建关卡图层失败: {e}")
            import traceback
            traceback.print_exc()
        
        # 创建边界图层
        if self.center_x > 0:
            self.boundary_layer = BoundaryLayer(
                self.center_x,
                0,
                self.map_height * self.tile_size
            )
            self.layers.append(self.boundary_layer)
        
        print(f"[MapManager] 图层初始化完成，共 {len(self.layers)} 个图层")
    
    def set_map_params(self, params: Dict[str, int]):
        """
        设置地图参数
        
        Args:
            params: 参数字典，包含 mapWidth, mapHeight, mapX, mapY, tileSize, centerX, centerY
        """
        self.map_width = params.get("mapWidth", self.map_width)
        self.map_height = params.get("mapHeight", self.map_height)
        self.map_x = params.get("mapX", self.map_x)
        self.map_y = params.get("mapY", self.map_y)
        self.tile_size = params.get("tileSize", self.tile_size)
        self.center_x = params.get("centerX", self.center_x)
        self.center_y = params.get("centerY", self.center_y)
    
    def get_map_params(self) -> Dict[str, int]:
        """
        获取地图参数
        
        Returns:
            地图参数字典
        """
        return {
            "mapWidth": self.map_width,
            "mapHeight": self.map_height,
            "mapX": self.map_x,
            "mapY": self.map_y,
            "tileSize": self.tile_size,
            "centerX": self.center_x,
            "centerY": self.center_y
        }
    
    def get_walls(self) -> List[Dict[str, Any]]:
        """
        获取墙壁列表
        
        Returns:
            墙壁列表
        """
        # 优先使用生成的地图数据（从配置文件生成）
        if hasattr(self, '_generated_walls') and self._generated_walls:
            return self._generated_walls
        # 其次使用 level_layer 的墙壁
        if self.level_layer and self.level_layer.walls:
            return self.level_layer.walls
        return []
    
    def get_obstacles(self) -> Dict[str, List[Tuple[int, int]]]:
        """
        获取障碍物列表
        
        Returns:
            障碍物字典，包含 obstacles1 和 obstacles2
        """
        # 优先使用生成的地图数据（从配置文件生成）
        if hasattr(self, '_generated_obstacles1') and hasattr(self, '_generated_obstacles2'):
            obstacles1 = [(obs["x"], obs["y"]) for obs in self._generated_obstacles1]
            obstacles2 = [(obs["x"], obs["y"]) for obs in self._generated_obstacles2]
            return {
                "obstacles1": obstacles1,
                "obstacles2": obstacles2
            }
        
        # 如果没有生成的地图数据，返回空列表
        return {
            "obstacles1": [],
            "obstacles2": []
        }
    
    def generate_walls(self):
        """生成墙壁"""
        map_width = self.map_width
        map_height = self.map_height
        
        walls = [
            {"x": 0, "y": 0, "tileId": 45},
            {"x": map_width - 1, "y": 0, "tileId": 47},
            {"x": 0, "y": map_height - 1, "tileId": 69},
            {"x": map_width - 1, "y": map_height - 1, "tileId": 71}
        ]
        
        walls.extend([{"x": i + 1, "y": 0, "tileId": 46} for i in range(map_width - 2)])
        walls.extend([{"x": i + 1, "y": map_height - 1, "tileId": 46} for i in range(map_width - 2)])
        walls.extend([{"x": 0, "y": i + 1, "tileId": 57} for i in range(map_height - 2)])
        walls.extend([{"x": map_width - 1, "y": i + 1, "tileId": 59} for i in range(map_height - 2)])
        
        # 存储生成的地图数据
        self._generated_walls = walls
        
        print(f"[MapManager] 生成墙壁: {len(walls)} 个")
    
    def generate_obstacles(self):
        """生成障碍物"""
        import random
        
        map_width = self.map_width
        map_height = self.map_height
        
        num_obstacles1 = 8
        num_obstacles2 = 4
        
        obstacles1 = []
        obstacles2 = []
        OBSTACLE_MAX_RETRIES = 1000
        
        def not_contains(arr, x, y):
            return not any(pos["x"] == x and pos["y"] == y for pos in arr)
        
        for i in range(num_obstacles1):
            retries = 0
            while retries < OBSTACLE_MAX_RETRIES:
                x = random.randint(4, map_width - 5)
                y = random.randint(1, map_height - 2)
                if not_contains(obstacles1, x, y):
                    obstacles1.append({"x": x, "y": y})
                    break
                retries += 1
        
        for i in range(num_obstacles2):
            retries = 0
            while retries < OBSTACLE_MAX_RETRIES:
                x = random.randint(4, map_width - 5)
                y = random.randint(1, map_height - 3)
                if (not_contains(obstacles1, x, y) and
                    not_contains(obstacles1, x, y + 1) and
                    not_contains(obstacles2, x, y - 1) and
                    not_contains(obstacles2, x, y)):
                    obstacles2.append({"x": x, "y": y})
                    break
                retries += 1
        
        # 存储生成的地图数据
        self._generated_obstacles1 = obstacles1
        self._generated_obstacles2 = obstacles2
        
        print(f"[MapManager] 生成障碍物: obstacles1={len(obstacles1)}, obstacles2={len(obstacles2)}")
    
    def generate_map_from_config(self):
        """从配置文件生成地图数据"""
        self.generate_walls()
        self.generate_obstacles()
        
        map_width = self.map_width
        map_height = self.map_height
        walls_count = len(self._generated_walls) if hasattr(self, '_generated_walls') else 0
        obs1_count = len(self._generated_obstacles1) if hasattr(self, '_generated_obstacles1') else 0
        obs2_count = len(self._generated_obstacles2) if hasattr(self, '_generated_obstacles2') else 0
        
        print(f"[MapManager] 从配置文件生成地图完成: {map_width}x{map_height}, 墙壁: {walls_count}, 障碍物1: {obs1_count}, 障碍物2: {obs2_count}")
    
    def generate_map(self, walls: List[Dict[str, Any]], 
                    obstacles: List[Tuple[int, int]],
                    left_target: List[Tuple[int, int]],
                    right_target: List[Tuple[int, int]],
                    left_prison: List[Tuple[int, int]],
                    right_prison: List[Tuple[int, int]]):
        """
        生成地图数据
        
        Args:
            walls: 墙壁列表
            obstacles: 障碍物列表
            left_target: L队目标区域
            right_target: R队目标区域
            left_prison: L队监狱
            right_prison: R队监狱
        """
        if not self.game_map:
            self.game_map = GameMap(self.map_width, self.map_height)
        
        # 初始化地图数据
        map_data = {
            "walls": walls,
            "obstacles": obstacles
        }
        self.game_map.initialize(map_data, left_target, right_target, left_prison, right_prison)
        
        # 设置关卡图层的墙壁
        if self.level_layer:
            self.level_layer.set_walls(walls)
        
        print(f"[MapManager] 地图数据生成完成")
    
    def render_map(self, surface: pygame.Surface, offset_x: int = 0, offset_y: int = 0,
                  left_target: Optional[List[Tuple[int, int]]] = None,
                  right_target: Optional[List[Tuple[int, int]]] = None,
                  left_prison: Optional[List[Tuple[int, int]]] = None,
                  right_prison: Optional[List[Tuple[int, int]]] = None,
                  obstacles1: Optional[List[Tuple[int, int]]] = None,
                  obstacles2: Optional[List[Tuple[int, int]]] = None):
        """
        渲染地图
        
        Args:
            surface: pygame Surface 对象
            offset_x: X偏移量
            offset_y: Y偏移量
            left_target: L队目标区域（可选）
            right_target: R队目标区域（可选）
            left_prison: L队监狱（可选）
            right_prison: R队监狱（可选）
            obstacles1: 障碍物1列表（可选）
            obstacles2: 障碍物2列表（可选）
        """
        if not self.level_layer:
            return
        
        # 渲染背景图层
        if self.ground_layer:
            self.ground_layer.render(surface, offset_x, offset_y)
        
        # 设置并渲染墙壁
        walls = self.get_walls()
        self.level_layer.set_walls(walls)
        self.level_layer.render_walls(surface, offset_x, offset_y)
        
        # 渲染监狱和目标区域（如果提供）
        if left_prison is not None and right_prison is not None:
            if len(left_prison) > 0 or len(right_prison) > 0:
                self.level_layer.render_prisons(surface, left_prison, right_prison, offset_x, offset_y)
        
        if left_target is not None and right_target is not None:
            if len(left_target) > 0 or len(right_target) > 0:
                self.level_layer.render_targets(surface, left_target, right_target, offset_x, offset_y)
        
        # 渲染障碍物（如果提供）
        if obstacles1 is not None and obstacles2 is not None:
            if len(obstacles1) > 0 or len(obstacles2) > 0:
                self.level_layer.render_obstacles(surface, obstacles1, obstacles2, offset_x, offset_y)
        
        # 渲染边界图层
        if self.boundary_layer:
            self.boundary_layer.render(surface, offset_x, offset_y)
    
    def render_targets_and_prisons(self, surface: pygame.Surface,
                                   left_target: List[Tuple[int, int]],
                                   right_target: List[Tuple[int, int]],
                                   left_prison: List[Tuple[int, int]],
                                   right_prison: List[Tuple[int, int]],
                                   offset_x: int = 0, offset_y: int = 0):
        """
        渲染目标区域和监狱
        
        Args:
            surface: pygame Surface 对象
            left_target: L队目标区域
            right_target: R队目标区域
            left_prison: L队监狱
            right_prison: R队监狱
            offset_x: X偏移量
            offset_y: Y偏移量
        """
        if self.level_layer:
            self.level_layer.render_targets(surface, left_target, right_target, offset_x, offset_y)
            self.level_layer.render_prisons(surface, left_prison, right_prison, offset_x, offset_y)
    
    def get_tile_at(self, x: int, y: int) -> Optional[Dict[str, Any]]:
        """
        获取指定位置的图块信息
        
        Args:
            x: X坐标（像素坐标）
            y: Y坐标（像素坐标）
        
        Returns:
            图块信息字典
        """
        if not self.level_layer:
            return None
        
        # 转换为格子坐标
        grid_x = x // self.tile_size
        grid_y = y // self.tile_size
        
        return self.level_layer.get_tile_at(grid_x, grid_y)
    
    def get_tile_at_grid(self, grid_x: int, grid_y: int) -> Optional[Dict[str, Any]]:
        """
        获取指定格子位置的图块信息
        
        Args:
            grid_x: X坐标（格子坐标）
            grid_y: Y坐标（格子坐标）
        
        Returns:
            图块信息字典
        """
        if not self.level_layer:
            return None
        
        return self.level_layer.get_tile_at(grid_x, grid_y)
    
    def is_wall(self, x: int, y: int) -> bool:
        """
        检查位置是否是墙
        
        Args:
            x: X坐标（格子坐标）
            y: Y坐标（格子坐标）
        
        Returns:
            如果是墙返回True
        """
        if self.level_layer:
            return self.level_layer.is_wall(x, y)
        return False
    
    def update(self, delta_time: int):
        """
        更新地图
        
        Args:
            delta_time: 时间增量（毫秒）
        """
        for layer in self.layers:
            layer.update(delta_time)
    
    def destroy(self):
        """销毁地图管理器"""
        for layer in self.layers:
            layer.destroy()
        self.layers.clear()
        self.ground_layer = None
        self.level_layer = None
        self.boundary_layer = None
        self.game_map = None

