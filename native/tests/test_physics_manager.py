"""
PhysicsManager 单元测试
测试物理系统管理器的所有功能
"""

import pytest
from unittest.mock import Mock, MagicMock
from native.managers import PhysicsManager, CollisionCallbacks
from native.objects import Player, Flag
from native.map.map import GameMap
from native.utils import Team, TILE_SIZE


@pytest.mark.unit
@pytest.mark.physics
class TestCollisionCallbacks:
    """CollisionCallbacks 测试"""
    
    def test_initialization(self):
        """测试初始化"""
        callbacks = CollisionCallbacks()
        assert callbacks.on_score_update is None
        assert callbacks.on_create_flag is None


@pytest.mark.unit
@pytest.mark.physics
class TestPhysicsManager:
    """PhysicsManager 测试"""
    
    @pytest.fixture
    def physics_manager_setup(self, mock_pygame):
        """设置物理管理器"""
        # 创建测试地图
        game_map = GameMap(20, 20)
        map_data = {
            "walls": [],
            "obstacles": []
        }
        left_target = [(2, 10), (2, 11), (3, 10), (3, 11)]
        right_target = [(17, 10), (17, 11), (18, 10), (18, 11)]
        left_prison = [(1, 10), (1, 11)]
        right_prison = [(19, 10), (19, 11)]
        game_map.initialize(map_data, left_target, right_target, left_prison, right_prison)
        
        # 创建物理系统管理器
        callbacks = CollisionCallbacks()
        physics_manager = PhysicsManager(game_map, callbacks)
        
        # 创建 sprite groups
        import pygame
        left_players = pygame.sprite.Group()
        right_players = pygame.sprite.Group()
        left_flags = pygame.sprite.Group()
        right_flags = pygame.sprite.Group()
        
        physics_manager.set_game_objects(
            left_players,
            right_players,
            left_flags,
            right_flags
        )
        
        # 设置区域
        left_target_positions = [(pos.x, pos.y) for pos in game_map.get_team_target_positions(Team.LEFT)]
        right_target_positions = [(pos.x, pos.y) for pos in game_map.get_team_target_positions(Team.RIGHT)]
        left_prison_positions = [(pos.x, pos.y) for pos in game_map.get_team_prison_positions(Team.LEFT)]
        right_prison_positions = [(pos.x, pos.y) for pos in game_map.get_team_prison_positions(Team.RIGHT)]
        
        physics_manager.set_zones(
            left_target_positions,
            right_target_positions,
            left_prison_positions,
            right_prison_positions
        )
        
        yield {
            'game_map': game_map,
            'callbacks': callbacks,
            'physics_manager': physics_manager,
            'left_players': left_players,
            'right_players': right_players,
            'left_flags': left_flags,
            'right_flags': right_flags
        }
        
        # 清理
        left_players.clear()
        right_players.clear()
        left_flags.clear()
        right_flags.clear()
        if hasattr(physics_manager, '_dropped_flags_this_frame'):
            physics_manager._dropped_flags_this_frame.clear()
    
    def test_set_game_objects(self, physics_manager_setup):
        """测试设置游戏对象"""
        pm = physics_manager_setup['physics_manager']
        assert pm.left_team_players is not None
        assert pm.right_team_players is not None
        assert pm.left_team_flags is not None
        assert pm.right_team_flags is not None
    
    def test_set_zones(self, physics_manager_setup):
        """测试设置区域"""
        pm = physics_manager_setup['physics_manager']
        assert len(pm.left_team_target_positions) > 0
        assert len(pm.right_team_target_positions) > 0
        assert len(pm.left_team_prison_positions) > 0
        assert len(pm.right_team_prison_positions) > 0
    
    def test_player_collision_same_team(self, physics_manager_setup):
        """测试同队玩家碰撞（不应该处理）"""
        pm = physics_manager_setup['physics_manager']
        left_players = physics_manager_setup['left_players']
        
        player1 = Player("L0", Team.LEFT, 10, 10)
        player2 = Player("L1", Team.LEFT, 10, 10)
        
        left_players.add(player1)
        left_players.add(player2)
        
        # 更新物理系统
        pm.update()
        
        # 同队玩家不应该被抓捕
        assert player1.in_prison is False
        assert player2.in_prison is False
    
    def test_player_collision_different_teams(self, physics_manager_setup):
        """测试不同队伍玩家碰撞（抓捕）"""
        pm = physics_manager_setup['physics_manager']
        left_players = physics_manager_setup['left_players']
        right_players = physics_manager_setup['right_players']
        
        player1 = Player("L0", Team.LEFT, 5, 10)  # 左侧
        player1.in_prison = False
        player2 = Player("R0", Team.RIGHT, 5, 10)  # 左侧
        player2.in_prison = False
        
        left_players.add(player1)
        right_players.add(player2)
        
        # 更新物理系统
        pm.update()
        
        # R队玩家在左侧应该被抓捕
        assert player2.in_prison is True
        assert player1.in_prison is False
    
    def test_player_collision_with_flag(self, physics_manager_setup):
        """测试玩家碰撞时掉落旗帜"""
        pm = physics_manager_setup['physics_manager']
        left_players = physics_manager_setup['left_players']
        right_players = physics_manager_setup['right_players']
        right_flags = physics_manager_setup['right_flags']
        
        player1 = Player("L0", Team.LEFT, 5, 10)
        player1.in_prison = False
        player2 = Player("R0", Team.RIGHT, 5, 10)
        player2.in_prison = False
        
        # 创建旗帜并让玩家携带
        flag = Flag("R0", Team.RIGHT, 15, 10)
        flag.pick_up_by(player2)
        player2.has_flag = True
        flag.carried_by = player2
        right_flags.add(flag)
        
        left_players.add(player1)
        right_players.add(player2)
        
        # 更新物理系统
        pm.update()
        
        # 玩家被抓捕，旗帜应该被掉落
        assert player2.has_flag is False
    
    def test_flag_collection(self, physics_manager_setup):
        """测试旗帜收集"""
        pm = physics_manager_setup['physics_manager']
        left_players = physics_manager_setup['left_players']
        right_flags = physics_manager_setup['right_flags']
        
        player = Player("L0", Team.LEFT, 15, 10)
        player.in_prison = False
        player.has_flag = False
        flag = Flag("R0", Team.RIGHT, 15, 10)
        # 确保旗帜可以拾取（默认 is_picked_up=False, is_scored=False）
        
        left_players.add(player)
        right_flags.add(flag)
        
        # 更新物理系统
        pm.update()
        
        # 玩家应该拾取旗帜
        assert player.has_flag is True
        assert flag.is_picked_up is True
        assert flag.carried_by == player
    
    def test_flag_collection_same_team(self, physics_manager_setup):
        """测试同队旗帜不能收集"""
        pm = physics_manager_setup['physics_manager']
        left_players = physics_manager_setup['left_players']
        left_flags = physics_manager_setup['left_flags']
        
        player = Player("L0", Team.LEFT, 2, 10)
        flag = Flag("L0", Team.LEFT, 2, 10)
        
        left_players.add(player)
        left_flags.add(flag)
        
        # 更新物理系统
        pm.update()
        
        # 同队旗帜不应该被收集
        assert player.has_flag is False
        assert flag.is_picked_up is False
    
    def test_flag_collection_player_in_prison(self, physics_manager_setup):
        """测试监狱中的玩家不能收集旗帜"""
        pm = physics_manager_setup['physics_manager']
        left_players = physics_manager_setup['left_players']
        right_flags = physics_manager_setup['right_flags']
        
        player = Player("L0", Team.LEFT, 15, 10)
        player.in_prison = True
        flag = Flag("R0", Team.RIGHT, 15, 10)
        
        left_players.add(player)
        right_flags.add(flag)
        
        # 更新物理系统
        pm.update()
        
        # 监狱中的玩家不应该收集旗帜
        assert player.has_flag is False
        assert flag.is_picked_up is False
    
    def test_flag_scoring(self, physics_manager_setup):
        """测试旗帜得分"""
        pm = physics_manager_setup['physics_manager']
        callbacks = physics_manager_setup['callbacks']
        left_players = physics_manager_setup['left_players']
        right_flags = physics_manager_setup['right_flags']
        
        player = Player("L0", Team.LEFT, 2, 10)
        player.has_flag = True
        
        flag = Flag("R0", Team.RIGHT, 15, 10)
        flag.pick_up_by(player)
        
        left_players.add(player)
        right_flags.add(flag)
        
        # 设置得分回调
        score_called = [False]
        def on_score(team):
            score_called[0] = True
            assert team == Team.LEFT
        
        callbacks.on_score_update = on_score
        
        # 更新物理系统
        pm.update()
        
        # 应该触发得分回调
        assert score_called[0] is True
        assert player.has_flag is False
        assert flag.is_scored is True
    
    def test_player_rescue(self, physics_manager_setup):
        """测试玩家营救"""
        pm = physics_manager_setup['physics_manager']
        left_players = physics_manager_setup['left_players']
        
        rescuer = Player("L0", Team.LEFT, 19, 10)  # 在R队监狱
        teammate = Player("L1", Team.LEFT, 19, 10)
        teammate.in_prison = True
        
        left_players.add(rescuer)
        left_players.add(teammate)
        
        # 更新物理系统
        pm.update()
        
        # 队友应该被营救
        assert teammate.in_prison is False
    
    def test_find_available_prison_tile(self, physics_manager_setup):
        """测试查找可用监狱位置"""
        pm = physics_manager_setup['physics_manager']
        right_players = physics_manager_setup['right_players']
        
        # 创建一个在监狱的玩家
        player = Player("R0", Team.RIGHT, 19, 10)
        player.in_prison = True
        right_players.add(player)
        
        # 查找可用位置
        prison_positions = {(19, 10), (19, 11)}
        pos = pm._find_available_prison_tile(Team.RIGHT, prison_positions)
        
        # 应该返回可用位置
        assert pos in prison_positions
    
    def test_find_available_target_tile(self, physics_manager_setup):
        """测试查找可用目标位置"""
        pm = physics_manager_setup['physics_manager']
        right_flags = physics_manager_setup['right_flags']
        
        # 创建一个已放置的旗帜
        flag = Flag("R0", Team.RIGHT, 17, 10)
        flag.is_scored = True
        right_flags.add(flag)
        
        # 查找可用位置
        target_positions = {(17, 10), (17, 11), (18, 10), (18, 11)}
        pos = pm._find_available_target_tile(Team.RIGHT, target_positions)
        
        # 应该返回可用位置
        assert pos in target_positions
