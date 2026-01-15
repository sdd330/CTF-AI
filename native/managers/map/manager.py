"""地图管理器 - 单例模式"""

import pygame
from typing import Optional, Dict, List, Tuple, Any
from ...utils import TILE_SIZE
from ...utils.assets import TILES_SPRITESHEET
from ...map.map import GameMap
from .map_layer import MapLayer
from .ground_layer import GroundLayer
from .level_layer import LevelLayer
from .boundary_layer import BoundaryLayer


class MapManager:
    """地图管理器（单例模式）"""
    _instance: Optional['MapManager'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self.layers: List[MapLayer] = []
        self.ground_layer: Optional[GroundLayer] = None
        self.level_layer: Optional[LevelLayer] = None
        self.boundary_layer: Optional[BoundaryLayer] = None
        self.map_x = self.map_y = self.map_width = self.map_height = self.center_x = self.center_y = 0
        self.tile_size = TILE_SIZE
        self.game_map: Optional[GameMap] = None
        self._generated_walls: List[Dict] = []
        self._generated_obstacles1: List[Dict] = []
        self._generated_obstacles2: List[Dict] = []
        self._initialized = True

    def set_map_params(self, params: Dict[str, int]):
        self.map_width = params.get("mapWidth", self.map_width)
        self.map_height = params.get("mapHeight", self.map_height)
        self.map_x = params.get("mapX", self.map_x)
        self.map_y = params.get("mapY", self.map_y)
        self.tile_size = params.get("tileSize", self.tile_size)
        self.center_x = params.get("centerX", self.center_x)
        self.center_y = params.get("centerY", self.center_y)

    def get_map_params(self) -> Dict[str, int]:
        return {"mapWidth": self.map_width, "mapHeight": self.map_height,
                "mapX": self.map_x, "mapY": self.map_y, "tileSize": self.tile_size,
                "centerX": self.center_x, "centerY": self.center_y}

    def initialize_layers(self, tiles_image: Optional[pygame.Surface] = None):
        if self.map_width <= 0 or self.map_height <= 0:
            return
        if tiles_image is None:
            if TILES_SPRITESHEET.exists():
                tiles_image = pygame.image.load(str(TILES_SPRITESHEET)).convert_alpha()
            else:
                return
        self.ground_layer = GroundLayer(tiles_image, self.map_width, self.map_height, self.tile_size)
        self.layers.append(self.ground_layer)
        self.level_layer = LevelLayer(tiles_image, self.map_width, self.map_height, self.tile_size)
        self.layers.append(self.level_layer)
        if self.center_x > 0:
            self.boundary_layer = BoundaryLayer(self.center_x, 0, self.map_height * self.tile_size)
            self.layers.append(self.boundary_layer)

    def get_walls(self) -> List[Dict[str, Any]]:
        if self._generated_walls:
            return self._generated_walls
        return self.level_layer.walls if self.level_layer and self.level_layer.walls else []

    def get_obstacles(self) -> Dict[str, List[Tuple[int, int]]]:
        return {"obstacles1": [(o["x"], o["y"]) for o in self._generated_obstacles1],
                "obstacles2": [(o["x"], o["y"]) for o in self._generated_obstacles2]}

    def generate_map_from_config(self):
        self._generate_walls()
        self._generate_obstacles()

    def _generate_walls(self):
        w, h = self.map_width, self.map_height
        walls = [{"x": 0, "y": 0, "tileId": 45}, {"x": w-1, "y": 0, "tileId": 47},
                 {"x": 0, "y": h-1, "tileId": 69}, {"x": w-1, "y": h-1, "tileId": 71}]
        walls.extend([{"x": i+1, "y": 0, "tileId": 46} for i in range(w-2)])
        walls.extend([{"x": i+1, "y": h-1, "tileId": 46} for i in range(w-2)])
        walls.extend([{"x": 0, "y": i+1, "tileId": 57} for i in range(h-2)])
        walls.extend([{"x": w-1, "y": i+1, "tileId": 59} for i in range(h-2)])
        self._generated_walls = walls

    def _generate_obstacles(self):
        import random
        w, h = self.map_width, self.map_height
        not_in = lambda arr, x, y: not any(p["x"] == x and p["y"] == y for p in arr)
        obs1, obs2 = [], []
        for _ in range(8):
            for _ in range(100):
                x, y = random.randint(4, w-5), random.randint(1, h-2)
                if not_in(obs1, x, y):
                    obs1.append({"x": x, "y": y}); break
        for _ in range(4):
            for _ in range(100):
                x, y = random.randint(4, w-5), random.randint(1, h-3)
                if not_in(obs1, x, y) and not_in(obs1, x, y+1) and not_in(obs2, x, y-1) and not_in(obs2, x, y):
                    obs2.append({"x": x, "y": y}); break
        self._generated_obstacles1, self._generated_obstacles2 = obs1, obs2

    def render_map(self, surface: pygame.Surface, offset_x: int = 0, offset_y: int = 0,
                   left_target=None, right_target=None, left_prison=None,
                   right_prison=None, obstacles1=None, obstacles2=None):
        if self.ground_layer:
            self.ground_layer.render(surface, offset_x, offset_y)
        if self.level_layer:
            self.level_layer.set_walls(self.get_walls())
            self.level_layer.render_walls(surface, offset_x, offset_y)
            if left_prison and right_prison:
                self.level_layer.render_prisons(surface, left_prison, right_prison, offset_x, offset_y)
            if left_target and right_target:
                self.level_layer.render_targets(surface, left_target, right_target, offset_x, offset_y)
            if obstacles1 and obstacles2:
                self.level_layer.render_obstacles(surface, obstacles1, obstacles2, offset_x, offset_y)
        if self.boundary_layer:
            self.boundary_layer.render(surface, offset_x, offset_y)

    def is_wall(self, x: int, y: int) -> bool:
        return self.level_layer.is_wall(x, y) if self.level_layer else False

    def get_tile_at(self, x: int, y: int) -> Optional[Dict]:
        return self.level_layer.get_tile_at(x // self.tile_size, y // self.tile_size) if self.level_layer else None

    def get_tile_at_grid(self, grid_x: int, grid_y: int) -> Optional[Dict]:
        return self.level_layer.get_tile_at(grid_x, grid_y) if self.level_layer else None

    def generate_map(self, walls: List[Dict], obstacles: List[Tuple[int, int]],
                     left_target: List[Tuple[int, int]], right_target: List[Tuple[int, int]],
                     left_prison: List[Tuple[int, int]], right_prison: List[Tuple[int, int]]):
        if not self.game_map:
            self.game_map = GameMap(self.map_width, self.map_height)
        self.game_map.initialize({"walls": walls, "obstacles": obstacles}, left_target, right_target, left_prison, right_prison)
        if self.level_layer:
            self.level_layer.set_walls(walls)

    def render_targets_and_prisons(self, surface: pygame.Surface, left_target: List[Tuple[int, int]],
                                   right_target: List[Tuple[int, int]], left_prison: List[Tuple[int, int]],
                                   right_prison: List[Tuple[int, int]], offset_x: int = 0, offset_y: int = 0):
        if self.level_layer:
            self.level_layer.render_targets(surface, left_target, right_target, offset_x, offset_y)
            self.level_layer.render_prisons(surface, left_prison, right_prison, offset_x, offset_y)

    def update(self, delta_time: int):
        for layer in self.layers:
            layer.update(delta_time)

    def destroy(self):
        for layer in self.layers:
            layer.destroy()
        self.layers.clear()
        self.ground_layer = self.level_layer = self.boundary_layer = self.game_map = None
