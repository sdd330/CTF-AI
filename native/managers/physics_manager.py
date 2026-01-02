"""
物理系统管理器
基于 Pygame Sprite/Group 实现碰撞系统
"""

import pygame
from typing import Optional, List, Callable, Dict, Set
from ..utils import Team, TILE_SIZE, PlayerState
from ..objects.player import Player
from ..objects.flag import Flag
from ..map.map import GameMap, Position


class CollisionCallbacks:
    """碰撞回调接口"""
    
    def __init__(self):
        self.on_score_update: Optional[Callable[[Team], None]] = None
        self.on_create_flag: Optional[Callable[[int, int, Team, bool], Flag]] = None


class PhysicsManager:
    """
    物理系统管理器
    基于 Pygame Sprite/Group 实现碰撞检测和处理
    
    职责：
    - 管理物理世界的配置
    - 设置碰撞检测
    - 处理碰撞逻辑（玩家碰撞、旗帜收集、旗帜放置、玩家释放）
    """
    
    def __init__(self, game_map: GameMap, callbacks: Optional[CollisionCallbacks] = None):
        """
        初始化物理系统管理器
        
        Args:
            game_map: 游戏地图
            callbacks: 碰撞回调
        """
        self.game_map = game_map
        self.callbacks = callbacks or CollisionCallbacks()
        
        # 游戏对象组（使用 pygame.sprite.Group）
        self.left_team_players: Optional[pygame.sprite.Group] = None
        self.right_team_players: Optional[pygame.sprite.Group] = None
        self.left_team_flags: Optional[pygame.sprite.Group] = None
        self.right_team_flags: Optional[pygame.sprite.Group] = None
        
        # 目标区域和监狱区域（使用集合存储位置）
        self.left_team_target_positions: Set[tuple[int, int]] = set()
        self.right_team_target_positions: Set[tuple[int, int]] = set()
        self.left_team_prison_positions: Set[tuple[int, int]] = set()
        self.right_team_prison_positions: Set[tuple[int, int]] = set()
        
        # 本帧刚掉落的旗帜（防止同一帧被拾取）
        self._dropped_flags_this_frame: Set[Flag] = set()
    
    def set_game_objects(self,
                        left_team_players: pygame.sprite.Group,
                        right_team_players: pygame.sprite.Group,
                        left_team_flags: pygame.sprite.Group,
                        right_team_flags: pygame.sprite.Group):
        """
        设置游戏对象组
        
        Args:
            left_team_players: L队玩家组
            right_team_players: R队玩家组
            left_team_flags: L队旗帜组
            right_team_flags: R队旗帜组
        """
        self.left_team_players = left_team_players
        self.right_team_players = right_team_players
        self.left_team_flags = left_team_flags
        self.right_team_flags = right_team_flags
    
    def set_zones(self,
                  left_team_target: List[tuple[int, int]],
                  right_team_target: List[tuple[int, int]],
                  left_team_prison: List[tuple[int, int]],
                  right_team_prison: List[tuple[int, int]]):
        """
        设置目标区域和监狱区域
        
        Args:
            left_team_target: L队目标区域位置列表
            right_team_target: R队目标区域位置列表
            left_team_prison: L队监狱位置列表
            right_team_prison: R队监狱位置列表
        """
        self.left_team_target_positions = set(left_team_target)
        self.right_team_target_positions = set(right_team_target)
        self.left_team_prison_positions = set(left_team_prison)
        self.right_team_prison_positions = set(right_team_prison)
    
    def update(self):
        """
        更新物理系统
        检查所有碰撞
        """
        if (self.left_team_players is None or self.right_team_players is None or
            self.left_team_flags is None or self.right_team_flags is None):
            return
        
        # 清空本帧掉落的旗帜集合
        self._dropped_flags_this_frame.clear()
        
        # 检查玩家之间的碰撞
        self._check_player_collisions()
        
        # 检查玩家与旗帜的碰撞
        self._check_flag_collisions()
        
        # 检查玩家与目标区域的碰撞（得分）
        self._check_target_zone_collisions()
        
        # 检查玩家与监狱区域的碰撞（营救）
        self._check_prison_zone_collisions()
    
    def _check_player_collisions(self):
        """检查玩家之间的碰撞（抓捕）"""
        if self.left_team_players is None or self.right_team_players is None:
            return
        
        # 使用 pygame.sprite.groupcollide 检测碰撞
        collisions = pygame.sprite.groupcollide(
            self.left_team_players,
            self.right_team_players,
            False,  # dokill1
            False,  # dokill2
            self._collide_players  # collided callback
        )
        
        # 处理碰撞
        for left_player, right_players in collisions.items():
            for right_player in right_players:
                self._handle_player_hit(left_player, right_player)
    
    def _collide_players(self, player1: Player, player2: Player) -> bool:
        """
        检查两个玩家是否碰撞
        
        Args:
            player1: 玩家1
            player2: 玩家2
        
        Returns:
            如果碰撞返回True
        """
        # 检查是否在同一格子位置
        return (player1.grid_x == player2.grid_x and 
                player1.grid_y == player2.grid_y)
    
    def _handle_player_hit(self, player1: Player, player2: Player):
        """
        处理玩家碰撞（抓捕）（完全参考 frontend: handlePlayerHit）
        
        Frontend 逻辑：
        1. 检查是否是不同队伍的玩家
        2. 检查是否在监狱中（如果在监狱中，不处理）
        3. 根据玩家中心位置判断在哪个队伍的领地
        4. 如果被抓玩家有旗帜，在当前位置创建新旗帜（敌方旗帜，canPickup=true）
        5. 将被抓玩家送到监狱
        
        Args:
            player1: 玩家1
            player2: 玩家2
        """
        # 必须是不同队伍的玩家（参考 frontend: if (player1.team === player2.team) return）
        if player1.team == player2.team:
            return
        
        # 监狱中的玩家不能被抓捕（参考 frontend: if (player1.inPrison || player2.inPrison) return）
        if player1.in_prison or player2.in_prison:
            return
        
        # 判断在哪个队伍的领地（参考 frontend: playerCenterX < centerX）
        center_x = self.game_map.middle_line
        player_center_x = (player1.grid_x + player2.grid_x) / 2
        
        if player_center_x < center_x:
            # 在左侧，R队玩家被抓（参考 frontend: const caughtPlayer = player1.team === 'R' ? player1 : player2）
            caught_player = player1 if player1.team == Team.RIGHT else player2
            tagger_player = player2 if player1.team == Team.RIGHT else player1
            # 被抓玩家所属的敌方队伍（用于创建旗帜）
            enemy_team = Team.LEFT
            enemy_flag_group = self.left_team_flags
        else:
            # 在右侧，L队玩家被抓（参考 frontend: const caughtPlayer = player1.team === 'L' ? player1 : player2）
            caught_player = player1 if player1.team == Team.LEFT else player2
            tagger_player = player2 if player1.team == Team.LEFT else player1
            # 被抓玩家所属的敌方队伍（用于创建旗帜）
            enemy_team = Team.RIGHT
            enemy_flag_group = self.right_team_flags
        
        # 如果被抓玩家有旗帜，在当前位置创建新旗帜（参考 frontend: createFlag(tile.x, tile.y, enemyTeam, true)）
        if caught_player.has_flag:
            # 找到玩家携带的旗帜
            flag_groups = [self.left_team_flags, self.right_team_flags]
            for flag_group in flag_groups:
                if not flag_group:
                    continue
                for flag in flag_group:
                    if flag.is_picked_up and flag.carried_by == caught_player:
                        # 在当前位置创建新旗帜（敌方旗帜，canPickup=true）
                        if self.callbacks.on_create_flag:
                            new_flag = self.callbacks.on_create_flag(
                                caught_player.grid_x, 
                                caught_player.grid_y, 
                                enemy_team, 
                                True
                            )
                            if new_flag and enemy_flag_group:
                                enemy_flag_group.add(new_flag)
                                print(f"[PhysicsManager] 玩家 {caught_player.name} 被抓，在位置 ({caught_player.grid_x}, {caught_player.grid_y}) 创建新旗帜")
                        # 玩家放下旗帜（参考 frontend: caughtPlayer.hasFlag = false）
                        caught_player.drop_flag()
                        # 原旗帜标记为已拾取状态已清除（实际上原旗帜应该被移除，但 native 中我们保留它）
                        flag.drop_at(caught_player.grid_x, caught_player.grid_y)
                        break
        
        # 将被抓玩家送到监狱（参考 frontend: caughtPlayer.toPrison(spot.x, spot.y)）
        prison_positions = (self.right_team_prison_positions 
                          if caught_player.team == Team.RIGHT 
                          else self.left_team_prison_positions)
        
        if prison_positions:
            prison_pos = self._find_available_prison_tile(
                caught_player.team, prison_positions
            )
            caught_player.send_to_prison(prison_pos[0], prison_pos[1])
            print(f"[PhysicsManager] 玩家 {caught_player.name} 被送到监狱 ({prison_pos[0]}, {prison_pos[1]})")
    
    def _check_flag_collisions(self):
        """检查玩家与旗帜的碰撞（拾取旗帜）"""
        if (self.left_team_players is None or self.right_team_players is None or
            self.left_team_flags is None or self.right_team_flags is None):
            return
        
        # L队玩家与R队旗帜
        collisions_lr = pygame.sprite.groupcollide(
            self.left_team_players,
            self.right_team_flags,
            False,
            False,
            self._collide_player_flag
        )
        
        for player, flags in collisions_lr.items():
            for flag in flags:
                self._handle_flag_collected(player, flag)
        
        # R队玩家与L队旗帜
        collisions_rl = pygame.sprite.groupcollide(
            self.right_team_players,
            self.left_team_flags,
            False,
            False,
            self._collide_player_flag
        )
        
        for player, flags in collisions_rl.items():
            for flag in flags:
                self._handle_flag_collected(player, flag)
    
    def _collide_player_flag(self, player: Player, flag: Flag) -> bool:
        """
        检查玩家与旗帜是否碰撞
        
        Args:
            player: 玩家
            flag: 旗帜
        
        Returns:
            如果碰撞返回True
        """
        return (player.grid_x == flag.grid_x and 
                player.grid_y == flag.grid_y)
    
    def _handle_flag_collected(self, player: Player, flag: Flag):
        """
        处理旗帜收集
        
        Args:
            player: 玩家
            flag: 旗帜
        """
        # 必须是敌方旗帜
        if player.team == flag.team:
            return
        
        # 玩家不能在监狱中
        if player.in_prison:
            return
        
        # 玩家不能已经持有旗帜
        if player.has_flag:
            return
        
        # 旗帜必须可以拾取
        if not flag.can_pickup:
            return
        
        # 如果旗帜本帧刚被掉落，不能立即拾取
        if flag in self._dropped_flags_this_frame:
            return
        
        # 拾取旗帜
        flag.pick_up_by(player)
        player.pick_up_flag()
    
    def _check_target_zone_collisions(self):
        """检查玩家与目标区域的碰撞（得分）"""
        if self.left_team_players is None or self.right_team_players is None:
            return
        
        # 检查L队玩家是否在L队目标区域
        for player in self.left_team_players:
            if (player.has_flag and 
                not player.in_prison and
                (player.grid_x, player.grid_y) in self.left_team_target_positions):
                # 调试：输出得分信息
                if not hasattr(self, '_score_debug_logged'):
                    print(f"[PhysicsManager] L队玩家 {player.name} 在目标区域得分！位置=({player.grid_x}, {player.grid_y})")
                self._handle_flag_scored(player)
        
        # 检查R队玩家是否在R队目标区域
        for player in self.right_team_players:
            if (player.has_flag and 
                not player.in_prison and
                (player.grid_x, player.grid_y) in self.right_team_target_positions):
                # 调试：输出得分信息
                if not hasattr(self, '_score_debug_logged'):
                    print(f"[PhysicsManager] R队玩家 {player.name} 在目标区域得分！位置=({player.grid_x}, {player.grid_y})")
                self._handle_flag_scored(player)
    
    def _handle_flag_scored(self, player: Player):
        """
        处理旗帜得分（完全参考 frontend: handleFlagDropped）
        
        Frontend 逻辑：
        1. player.dropFlag() - 玩家放下旗帜
        2. 查找可用的目标位置
        3. 创建新旗帜（敌方旗帜，canPickup=false）在目标区域
        4. 触发得分回调
        
        Args:
            player: 玩家
        """
        if not player.has_flag:
            print(f"[PhysicsManager] 警告：玩家 {player.name} 没有旗帜，无法得分")
            return
        
        # 玩家放下旗帜（参考 frontend: player.dropFlag()）
        player.drop_flag()
        print(f"[PhysicsManager] 玩家 {player.name} 放下旗帜")
        
        # 找到玩家携带的旗帜并标记为已得分（参考 frontend: removeFlagItem）
        # 注意：frontend 中，旗帜在 collect() 时就被移除了
        # 但 native 中，我们保留旗帜但标记为已得分，这样它就不会再被拾取
        flag_groups = [self.left_team_flags, self.right_team_flags]
        for flag_group in flag_groups:
            if not flag_group:
                continue
            for flag in flag_group:
                if flag.is_picked_up and flag.carried_by == player:
                    # 标记旗帜为已得分（这样它就不会再被拾取）
                    flag.score()
                    print(f"[PhysicsManager] 原旗帜 {flag.flag_id} 已标记为已得分")
                    break
        
        # 确定敌方队伍和目标区域（参考 frontend 逻辑）
        if player.team == Team.LEFT:
            # L队玩家得分，在L队目标区域创建R队旗帜（不可拾取）
            enemy_team = Team.RIGHT
            target_positions = self.left_team_target_positions
            flag_group = self.right_team_flags
        else:
            # R队玩家得分，在R队目标区域创建L队旗帜（不可拾取）
            enemy_team = Team.LEFT
            target_positions = self.right_team_target_positions
            flag_group = self.left_team_flags
        
        # 查找可用的目标位置（参考 frontend: findAvailableFlagTile）
        spot = self._find_available_target_tile(enemy_team, target_positions)
        print(f"[PhysicsManager] 在目标位置 ({spot[0]}, {spot[1]}) 创建新旗帜（已得分）")
        
        # 创建新旗帜（不可拾取，表示已得分）（参考 frontend: createFlag(spot.x, spot.y, enemyTeam, false)）
        if self.callbacks.on_create_flag:
            new_flag = self.callbacks.on_create_flag(spot[0], spot[1], enemy_team, False)
            if new_flag and flag_group:
                flag_group.add(new_flag)
                print(f"[PhysicsManager] 新旗帜已创建并添加到组")
        else:
            print(f"[PhysicsManager] 警告：on_create_flag 回调未设置")
        
        # 触发得分回调（参考 frontend: onScoreUpdate(team)）
        if self.callbacks.on_score_update:
            print(f"[PhysicsManager] 触发得分回调：{player.team.value}队得分")
            self.callbacks.on_score_update(player.team)
        else:
            print(f"[PhysicsManager] 警告：on_score_update 回调未设置！")
    
    def _check_prison_zone_collisions(self):
        """
        检查玩家与监狱区域的碰撞（营救队友）（完全参考 frontend: handlePlayerFreed）
        
        Frontend 逻辑：
        1. 如果营救者在监狱中，不处理（if (player.inPrison) return）
        2. 找到同队的所有玩家
        3. 将所有在监狱中的队友释放（p.inPrison = false）
        """
        if self.left_team_players is None or self.right_team_players is None:
            return
        
        # 检查L队玩家是否在R队监狱（营救L队队友）
        enemy_prison = self.right_team_prison_positions
        for player in self.left_team_players:
            if (not player.in_prison and
                (player.grid_x, player.grid_y) in enemy_prison):
                self._handle_player_rescue(player, Team.LEFT)
        
        # 检查R队玩家是否在L队监狱（营救R队队友）
        enemy_prison = self.left_team_prison_positions
        for player in self.right_team_players:
            if (not player.in_prison and
                (player.grid_x, player.grid_y) in enemy_prison):
                self._handle_player_rescue(player, Team.RIGHT)
    
    def _handle_player_rescue(self, rescuer: Player, team: Team):
        """
        处理玩家营救（完全参考 frontend: handlePlayerFreed）
        
        Frontend 逻辑：
        1. 如果营救者在监狱中，不处理（if (player.inPrison) return）
        2. 找到同队的所有玩家（const teamPlayers = player.team === 'L' ? this.lteamPlayers : this.rteamPlayers）
        3. 将所有在监狱中的队友释放（p.inPrison = false）
        
        Args:
            rescuer: 营救者
            team: 被营救的队伍
        """
        # 如果营救者在监狱中，不处理（参考 frontend: if (player.inPrison) return）
        if rescuer.in_prison:
            return
        
        # 找到同队的所有玩家（参考 frontend: const teamPlayers = player.team === 'L' ? this.lteamPlayers : this.rteamPlayers）
        team_players = (self.left_team_players if team == Team.LEFT 
                       else self.right_team_players)
        
        if not team_players:
            return
        
        # 将所有在监狱中的队友释放（参考 frontend: p.inPrison = false）
        rescued_count = 0
        for teammate in team_players:
            if teammate.in_prison:
                teammate.in_prison = False
                teammate.state = PlayerState.FREE
                teammate.prison_time_left = 0
                rescued_count += 1
        
        if rescued_count > 0:
            print(f"[PhysicsManager] 玩家 {rescuer.name} 营救了 {rescued_count} 名队友")
    
    def _drop_flag_from_player(self, player: Player):
        """
        从玩家身上掉落旗帜
        
        Args:
            player: 玩家
        """
        # 找到玩家携带的旗帜
        flag_groups = [self.left_team_flags, self.right_team_flags]
        for flag_group in flag_groups:
            if not flag_group:
                continue
            for flag in flag_group:
                if flag.is_picked_up and flag.carried_by == player:
                    # 在当前位置放下旗帜
                    flag.drop_at(player.grid_x, player.grid_y)
                    player.drop_flag()
                    # 标记为本帧掉落的旗帜
                    self._dropped_flags_this_frame.add(flag)
                    return
    
    def _find_available_prison_tile(self, team: Team, 
                                    prison_positions: Set[tuple[int, int]]) -> tuple[int, int]:
        """
        查找可用的监狱位置
        
        Args:
            team: 队伍
            prison_positions: 监狱位置集合
        
        Returns:
            可用的监狱位置
        """
        team_players = (self.left_team_players if team == Team.LEFT 
                       else self.right_team_players)
        
        if not team_players:
            return next(iter(prison_positions)) if prison_positions else (0, 0)
        
        # 查找未被占用的监狱位置
        occupied_positions = {
            (p.grid_x, p.grid_y) 
            for p in team_players 
            if p.in_prison
        }
        
        for pos in prison_positions:
            if pos not in occupied_positions:
                return pos
        
        # 如果所有位置都被占用，返回第一个位置
        return next(iter(prison_positions)) if prison_positions else (0, 0)
    
    def _find_available_target_tile(self, team: Team,
                                    target_positions: Set[tuple[int, int]]) -> tuple[int, int]:
        """
        查找可用的目标位置（用于放置旗帜）
        
        Args:
            team: 队伍
            target_positions: 目标位置集合
        
        Returns:
            可用的目标位置
        """
        flag_group = (self.left_team_flags if team == Team.LEFT 
                     else self.right_team_flags)
        
        if not flag_group:
            return next(iter(target_positions)) if target_positions else (0, 0)
        
        # 查找未被占用的目标位置
        occupied_positions = {
            (f.grid_x, f.grid_y) 
            for f in flag_group 
            if not f.can_pickup
        }
        
        for pos in target_positions:
            if pos not in occupied_positions:
                return pos
        
        # 如果所有位置都被占用，返回第一个位置
        return next(iter(target_positions)) if target_positions else (0, 0)

