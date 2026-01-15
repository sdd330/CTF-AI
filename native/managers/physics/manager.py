"""
物理系统管理器
基于 Pygame Sprite/Group 实现碰撞系统
"""

import pygame
from typing import Optional, List, Set

from ...utils import Team
from ...objects.flag import Flag
from ...map.map import GameMap
from .callbacks import CollisionCallbacks
from .collision_handler import CollisionHandler
from .zone_checker import ZoneChecker


class PhysicsManager:
    """
    物理系统管理器
    基于 Pygame Sprite/Group 实现碰撞检测和处理
    """

    def __init__(self, game_map: GameMap, callbacks: Optional[CollisionCallbacks] = None):
        self.game_map = game_map
        self.callbacks = callbacks or CollisionCallbacks()

        # 游戏对象组
        self.left_team_players: Optional[pygame.sprite.Group] = None
        self.right_team_players: Optional[pygame.sprite.Group] = None
        self.left_team_flags: Optional[pygame.sprite.Group] = None
        self.right_team_flags: Optional[pygame.sprite.Group] = None

        # 区域位置
        self.left_team_target_positions: Set[tuple[int, int]] = set()
        self.right_team_target_positions: Set[tuple[int, int]] = set()
        self.left_team_prison_positions: Set[tuple[int, int]] = set()
        self.right_team_prison_positions: Set[tuple[int, int]] = set()

        # 组件
        self._collision_handler = CollisionHandler(self.callbacks)
        self._zone_checker = ZoneChecker(self.callbacks)

        # 本帧掉落的旗帜（防止同一帧被拾取）
        self._dropped_flags_this_frame: Set[Flag] = set()

    def set_game_objects(self,
                        left_team_players: pygame.sprite.Group,
                        right_team_players: pygame.sprite.Group,
                        left_team_flags: pygame.sprite.Group,
                        right_team_flags: pygame.sprite.Group):
        """设置游戏对象组"""
        self.left_team_players = left_team_players
        self.right_team_players = right_team_players
        self.left_team_flags = left_team_flags
        self.right_team_flags = right_team_flags

    def set_zones(self,
                  left_team_target: List[tuple[int, int]],
                  right_team_target: List[tuple[int, int]],
                  left_team_prison: List[tuple[int, int]],
                  right_team_prison: List[tuple[int, int]]):
        """设置目标区域和监狱区域"""
        self.left_team_target_positions = set(left_team_target)
        self.right_team_target_positions = set(right_team_target)
        self.left_team_prison_positions = set(left_team_prison)
        self.right_team_prison_positions = set(right_team_prison)

    def update(self):
        """更新物理系统，检查所有碰撞"""
        if not self._has_game_objects():
            return

        # 同步回调引用（支持运行时替换回调）
        self._collision_handler.callbacks = self.callbacks
        self._zone_checker.callbacks = self.callbacks

        self._collision_handler.clear_dropped_flags()

        # 检查玩家之间的碰撞
        self._collision_handler.check_player_collisions(
            self.left_team_players, self.right_team_players,
            self.left_team_flags, self.right_team_flags,
            self.left_team_prison_positions, self.right_team_prison_positions,
            self.game_map.middle_line
        )

        # 检查玩家与旗帜的碰撞
        self._collision_handler.check_flag_collisions(
            self.left_team_players, self.right_team_players,
            self.left_team_flags, self.right_team_flags
        )

        # 检查目标区域碰撞（得分）
        self._zone_checker.check_target_zone_collisions(
            self.left_team_players, self.right_team_players,
            self.left_team_flags, self.right_team_flags,
            self.left_team_target_positions, self.right_team_target_positions
        )

        # 检查监狱区域碰撞（营救）
        self._zone_checker.check_prison_zone_collisions(
            self.left_team_players, self.right_team_players,
            self.left_team_prison_positions, self.right_team_prison_positions
        )

    def _has_game_objects(self) -> bool:
        """检查是否已设置游戏对象"""
        return (self.left_team_players is not None and
                self.right_team_players is not None and
                self.left_team_flags is not None and
                self.right_team_flags is not None)

    def _find_available_prison_tile(self, team: Team,
                                    prison_positions: Set[tuple[int, int]]) -> tuple[int, int]:
        """查找可用的监狱位置（向后兼容）"""
        team_players = (self.left_team_players if team == Team.LEFT
                       else self.right_team_players)

        if not team_players:
            return next(iter(prison_positions)) if prison_positions else (0, 0)

        occupied_positions = {
            (p.grid_x, p.grid_y)
            for p in team_players
            if hasattr(p, 'in_prison') and p.in_prison
        }

        for pos in prison_positions:
            if pos not in occupied_positions:
                return pos

        return next(iter(prison_positions)) if prison_positions else (0, 0)

    def _find_available_target_tile(self, team: Team,
                                    target_positions: Set[tuple[int, int]]) -> tuple[int, int]:
        """查找可用的目标位置（向后兼容）"""
        flag_group = (self.left_team_flags if team == Team.LEFT
                     else self.right_team_flags)

        if not flag_group:
            return next(iter(target_positions)) if target_positions else (0, 0)

        occupied_positions = {
            (f.grid_x, f.grid_y)
            for f in flag_group
            if not f.can_pickup
        }

        for pos in target_positions:
            if pos not in occupied_positions:
                return pos

        return next(iter(target_positions)) if target_positions else (0, 0)
