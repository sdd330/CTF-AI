"""
碰撞处理模块
处理玩家与玩家、玩家与旗帜的碰撞
"""

import pygame
from typing import Optional, Set, TYPE_CHECKING

from ...utils import Team, PlayerState
from ...objects.player import Player
from ...objects.flag import Flag

if TYPE_CHECKING:
    from .callbacks import CollisionCallbacks


class CollisionHandler:
    """处理游戏中的碰撞事件"""

    def __init__(self, callbacks: "CollisionCallbacks"):
        self.callbacks = callbacks
        self._dropped_flags_this_frame: Set[Flag] = set()

    def clear_dropped_flags(self):
        """清空本帧掉落的旗帜集合"""
        self._dropped_flags_this_frame.clear()

    def check_player_collisions(self,
                                 left_team_players: pygame.sprite.Group,
                                 right_team_players: pygame.sprite.Group,
                                 left_team_flags: pygame.sprite.Group,
                                 right_team_flags: pygame.sprite.Group,
                                 left_prison_positions: Set[tuple[int, int]],
                                 right_prison_positions: Set[tuple[int, int]],
                                 middle_line: int):
        """检查玩家之间的碰撞（抓捕）"""
        collisions = pygame.sprite.groupcollide(
            left_team_players,
            right_team_players,
            False, False,
            self._collide_players
        )

        for left_player, right_players in collisions.items():
            for right_player in right_players:
                self._handle_player_hit(
                    left_player, right_player,
                    left_team_flags, right_team_flags,
                    left_prison_positions, right_prison_positions,
                    middle_line
                )

    def _collide_players(self, player1: Player, player2: Player) -> bool:
        """检查两个玩家是否碰撞"""
        return (player1.grid_x == player2.grid_x and
                player1.grid_y == player2.grid_y)

    def _handle_player_hit(self,
                           player1: Player,
                           player2: Player,
                           left_team_flags: pygame.sprite.Group,
                           right_team_flags: pygame.sprite.Group,
                           left_prison_positions: Set[tuple[int, int]],
                           right_prison_positions: Set[tuple[int, int]],
                           middle_line: int):
        """处理玩家碰撞（抓捕）"""
        if player1.team == player2.team:
            return

        if player1.in_prison or player2.in_prison:
            return

        center_x = middle_line
        player_center_x = (player1.grid_x + player2.grid_x) / 2

        if player_center_x < center_x:
            caught_player = player1 if player1.team == Team.RIGHT else player2
            enemy_team = Team.LEFT
            enemy_flag_group = left_team_flags
            prison_positions = right_prison_positions
        else:
            caught_player = player1 if player1.team == Team.LEFT else player2
            enemy_team = Team.RIGHT
            enemy_flag_group = right_team_flags
            prison_positions = left_prison_positions

        if caught_player.has_flag:
            self._drop_flag_on_capture(
                caught_player, enemy_team, enemy_flag_group,
                left_team_flags, right_team_flags
            )

        if prison_positions:
            prison_pos = self._find_available_prison_tile(
                caught_player.team, prison_positions,
                left_team_flags if caught_player.team == Team.LEFT else right_team_flags
            )
            caught_player.send_to_prison(prison_pos[0], prison_pos[1])
            print(f"[CollisionHandler] Player {caught_player.name} sent to prison ({prison_pos[0]}, {prison_pos[1]})")

    def _drop_flag_on_capture(self,
                               caught_player: Player,
                               enemy_team: Team,
                               enemy_flag_group: pygame.sprite.Group,
                               left_team_flags: pygame.sprite.Group,
                               right_team_flags: pygame.sprite.Group):
        """处理被抓玩家掉落旗帜"""
        flag_groups = [left_team_flags, right_team_flags]
        for flag_group in flag_groups:
            if not flag_group:
                continue
            for flag in flag_group:
                if flag.is_picked_up and flag.carried_by == caught_player:
                    if self.callbacks.on_create_flag:
                        new_flag = self.callbacks.on_create_flag(
                            caught_player.grid_x,
                            caught_player.grid_y,
                            enemy_team,
                            True
                        )
                        if new_flag and enemy_flag_group:
                            enemy_flag_group.add(new_flag)
                            self._dropped_flags_this_frame.add(new_flag)
                    caught_player.drop_flag()
                    flag.drop_at(caught_player.grid_x, caught_player.grid_y)
                    break

    def _find_available_prison_tile(self,
                                     team: Team,
                                     prison_positions: Set[tuple[int, int]],
                                     team_players: pygame.sprite.Group) -> tuple[int, int]:
        """查找可用的监狱位置"""
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

    def check_flag_collisions(self,
                               left_team_players: pygame.sprite.Group,
                               right_team_players: pygame.sprite.Group,
                               left_team_flags: pygame.sprite.Group,
                               right_team_flags: pygame.sprite.Group):
        """检查玩家与旗帜的碰撞（拾取旗帜）"""
        # L队玩家与R队旗帜
        collisions_lr = pygame.sprite.groupcollide(
            left_team_players, right_team_flags,
            False, False, self._collide_player_flag
        )

        for player, flags in collisions_lr.items():
            for flag in flags:
                self._handle_flag_collected(player, flag)

        # R队玩家与L队旗帜
        collisions_rl = pygame.sprite.groupcollide(
            right_team_players, left_team_flags,
            False, False, self._collide_player_flag
        )

        for player, flags in collisions_rl.items():
            for flag in flags:
                self._handle_flag_collected(player, flag)

    def _collide_player_flag(self, player: Player, flag: Flag) -> bool:
        """检查玩家与旗帜是否碰撞"""
        return (player.grid_x == flag.grid_x and
                player.grid_y == flag.grid_y)

    def _handle_flag_collected(self, player: Player, flag: Flag):
        """处理旗帜收集"""
        if player.team == flag.team:
            return
        if player.in_prison:
            return
        if player.has_flag:
            return
        if not flag.can_pickup:
            return
        if flag in self._dropped_flags_this_frame:
            return

        flag.pick_up_by(player)
        player.pick_up_flag()
