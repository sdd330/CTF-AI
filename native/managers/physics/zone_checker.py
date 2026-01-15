"""
区域检查模块
处理目标区域（得分）和监狱区域（营救）的碰撞检测
"""

import pygame
from typing import Optional, Set, TYPE_CHECKING

from ...utils import Team, PlayerState
from ...objects.player import Player
from ...objects.flag import Flag

if TYPE_CHECKING:
    from .callbacks import CollisionCallbacks


class ZoneChecker:
    """处理区域碰撞检测"""

    def __init__(self, callbacks: "CollisionCallbacks"):
        self.callbacks = callbacks

    def check_target_zone_collisions(self,
                                      left_team_players: pygame.sprite.Group,
                                      right_team_players: pygame.sprite.Group,
                                      left_team_flags: pygame.sprite.Group,
                                      right_team_flags: pygame.sprite.Group,
                                      left_team_target_positions: Set[tuple[int, int]],
                                      right_team_target_positions: Set[tuple[int, int]]):
        """检查玩家与目标区域的碰撞（得分）"""
        # 检查L队玩家是否在L队目标区域
        for player in left_team_players:
            if (player.has_flag and
                not player.in_prison and
                (player.grid_x, player.grid_y) in left_team_target_positions):
                print(f"[ZoneChecker] L team player {player.name} scored at ({player.grid_x}, {player.grid_y})")
                self._handle_flag_scored(
                    player,
                    left_team_flags, right_team_flags,
                    left_team_target_positions
                )

        # 检查R队玩家是否在R队目标区域
        for player in right_team_players:
            if (player.has_flag and
                not player.in_prison and
                (player.grid_x, player.grid_y) in right_team_target_positions):
                print(f"[ZoneChecker] R team player {player.name} scored at ({player.grid_x}, {player.grid_y})")
                self._handle_flag_scored(
                    player,
                    left_team_flags, right_team_flags,
                    right_team_target_positions
                )

    def _handle_flag_scored(self,
                            player: Player,
                            left_team_flags: pygame.sprite.Group,
                            right_team_flags: pygame.sprite.Group,
                            target_positions: Set[tuple[int, int]]):
        """处理旗帜得分"""
        if not player.has_flag:
            print(f"[ZoneChecker] Warning: Player {player.name} has no flag, cannot score")
            return

        player.drop_flag()
        print(f"[ZoneChecker] Player {player.name} dropped flag")

        # 找到玩家携带的旗帜并标记为已得分
        flag_groups = [left_team_flags, right_team_flags]
        for flag_group in flag_groups:
            if not flag_group:
                continue
            for flag in flag_group:
                if flag.is_picked_up and flag.carried_by == player:
                    flag.score()
                    print(f"[ZoneChecker] Flag {flag.flag_id} marked as scored")
                    break

        # 确定敌方队伍和目标区域
        if player.team == Team.LEFT:
            enemy_team = Team.RIGHT
            flag_group = right_team_flags
        else:
            enemy_team = Team.LEFT
            flag_group = left_team_flags

        # 查找可用的目标位置
        spot = self._find_available_target_tile(enemy_team, target_positions, flag_group)
        print(f"[ZoneChecker] Creating new flag at ({spot[0]}, {spot[1]})")

        # 创建新旗帜（不可拾取，表示已得分）
        if self.callbacks.on_create_flag:
            new_flag = self.callbacks.on_create_flag(spot[0], spot[1], enemy_team, False)
            if new_flag and flag_group:
                flag_group.add(new_flag)
                print(f"[ZoneChecker] New flag created and added to group")
        else:
            print(f"[ZoneChecker] Warning: on_create_flag callback not set")

        # 触发得分回调
        if self.callbacks.on_score_update:
            print(f"[ZoneChecker] Triggering score callback: {player.team.value} team scored")
            self.callbacks.on_score_update(player.team)
        else:
            print(f"[ZoneChecker] Warning: on_score_update callback not set!")

    def _find_available_target_tile(self,
                                     team: Team,
                                     target_positions: Set[tuple[int, int]],
                                     flag_group: pygame.sprite.Group) -> tuple[int, int]:
        """查找可用的目标位置（用于放置旗帜）"""
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

    def check_prison_zone_collisions(self,
                                      left_team_players: pygame.sprite.Group,
                                      right_team_players: pygame.sprite.Group,
                                      left_prison_positions: Set[tuple[int, int]],
                                      right_prison_positions: Set[tuple[int, int]]):
        """检查玩家与监狱区域的碰撞（营救队友）"""
        # 检查L队玩家是否在R队监狱（营救L队队友）
        for player in left_team_players:
            if (not player.in_prison and
                (player.grid_x, player.grid_y) in right_prison_positions):
                self._handle_player_rescue(player, Team.LEFT, left_team_players)

        # 检查R队玩家是否在L队监狱（营救R队队友）
        for player in right_team_players:
            if (not player.in_prison and
                (player.grid_x, player.grid_y) in left_prison_positions):
                self._handle_player_rescue(player, Team.RIGHT, right_team_players)

    def _handle_player_rescue(self,
                               rescuer: Player,
                               team: Team,
                               team_players: pygame.sprite.Group):
        """处理玩家营救"""
        if rescuer.in_prison:
            return

        if not team_players:
            return

        rescued_count = 0
        for teammate in team_players:
            if teammate.in_prison:
                teammate.in_prison = False
                teammate.state = PlayerState.FREE
                teammate.prison_time_left = 0
                rescued_count += 1

        if rescued_count > 0:
            print(f"[ZoneChecker] Player {rescuer.name} rescued {rescued_count} teammates")
