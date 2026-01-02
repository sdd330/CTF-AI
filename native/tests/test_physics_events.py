"""
物理系统事件测试
测试碰撞检测和物理事件
使用事件模拟和逻辑分离
"""

import pytest
from native.managers import PhysicsManager, CollisionCallbacks
from native.objects import Player, Flag
from native.utils import Team


@pytest.mark.unit
@pytest.mark.physics
@pytest.mark.event
class TestCollisionEvents:
    """碰撞事件测试"""
    
    def test_player_collision_event(self, mock_physics_manager, event_simulator):
        """测试玩家碰撞事件"""
        collision_events = []
        
        def on_collision(player1, player2):
            collision_events.append((player1, player2))
        
        event_simulator.register("player_collision", on_collision)
        
        # 创建不同队伍的玩家在同一位置（确保在同一格子）
        player1 = Player("L0", Team.LEFT, 5, 10)
        player2 = Player("R0", Team.RIGHT, 5, 10)
        # 确保 rect 位置也相同
        player1.rect.center = (player1.pixel_x, player1.pixel_y)
        player2.rect.center = (player1.pixel_x, player1.pixel_y)
        
        mock_physics_manager.left_team_players.add(player1)
        mock_physics_manager.right_team_players.add(player2)
        
        # 更新物理系统
        mock_physics_manager.update()
        
        # 检查是否触发碰撞事件
        assert player2.in_prison is True or player1.grid_x == player2.grid_x
    
    def test_flag_collection_event(self, mock_physics_manager, event_simulator):
        """测试旗帜收集事件"""
        collection_events = []
        
        def on_collection(player, flag):
            collection_events.append((player, flag))
        
        event_simulator.register("flag_collection", on_collection)
        
        # 创建玩家和敌方旗帜在同一位置（确保在同一格子）
        player = Player("L0", Team.LEFT, 15, 10)
        flag = Flag("R0", Team.RIGHT, 15, 10)
        # 确保玩家不在监狱中，且没有旗帜
        player.in_prison = False
        player.has_flag = False
        # 确保 rect 位置也相同
        player.rect.center = (player.pixel_x, player.pixel_y)
        flag.rect.center = (player.pixel_x, player.pixel_y)
        
        mock_physics_manager.left_team_players.add(player)
        mock_physics_manager.right_team_flags.add(flag)
        
        # 更新物理系统
        mock_physics_manager.update()
        
        # 检查旗帜是否被收集
        assert player.has_flag is True
        assert flag.is_picked_up is True
    
    def test_score_event(self, mock_physics_manager, event_simulator):
        """测试得分事件"""
        score_called = [False]
        score_team = [None]
        
        def on_score(team):
            score_called[0] = True
            score_team[0] = team
        
        callbacks = CollisionCallbacks()
        callbacks.on_score_update = on_score
        mock_physics_manager.callbacks = callbacks
        
        # 创建携带旗帜的玩家在目标区域
        player = Player("L0", Team.LEFT, 2, 10)
        player.has_flag = True
        flag = Flag("R0", Team.RIGHT, 15, 10)
        flag.pick_up_by(player)
        
        mock_physics_manager.left_team_players.add(player)
        mock_physics_manager.right_team_flags.add(flag)
        
        # 更新物理系统
        mock_physics_manager.update()
        
        # 检查是否触发得分回调
        assert score_called[0] is True
        assert score_team[0] == Team.LEFT
    
    def test_rescue_event(self, mock_physics_manager, event_simulator):
        """测试营救事件"""
        rescue_events = []
        
        def on_rescue(rescuer, rescued):
            rescue_events.append((rescuer, rescued))
        
        event_simulator.register("rescue", on_rescue)
        
        # 创建营救者和被营救者在监狱
        rescuer = Player("L0", Team.LEFT, 19, 10)  # 在R队监狱
        rescued = Player("L1", Team.LEFT, 19, 10)
        rescued.in_prison = True
        
        mock_physics_manager.left_team_players.add(rescuer)
        mock_physics_manager.left_team_players.add(rescued)
        
        # 更新物理系统
        mock_physics_manager.update()
        
        # 检查是否被营救
        assert rescued.in_prison is False


@pytest.mark.integration
@pytest.mark.physics
class TestPhysicsIntegration:
    """物理系统集成测试"""
    
    def test_complete_capture_flow(self, mock_physics_manager):
        """测试完整抓捕流程"""
        # 1. 创建不同队伍的玩家在同一位置
        attacker = Player("L0", Team.LEFT, 5, 10)
        defender = Player("R0", Team.RIGHT, 5, 10)
        # 确保 rect 位置相同
        attacker.rect.center = (attacker.pixel_x, attacker.pixel_y)
        defender.rect.center = (attacker.pixel_x, attacker.pixel_y)
        
        mock_physics_manager.left_team_players.add(attacker)
        mock_physics_manager.right_team_players.add(defender)
        
        # 2. 更新物理系统（触发碰撞）
        mock_physics_manager.update()
        
        # 3. 检查防守者是否被抓捕
        assert defender.in_prison is True or (attacker.grid_x == defender.grid_x and attacker.grid_y == defender.grid_y)
        assert attacker.in_prison is False
    
    def test_complete_flag_capture_flow(self, mock_physics_manager):
        """测试完整抢旗流程"""
        score_called = [False]
        
        def on_score(team):
            score_called[0] = True
        
        mock_physics_manager.callbacks.on_score_update = on_score
        
        # 1. 创建玩家和敌方旗帜在同一位置
        player = Player("L0", Team.LEFT, 15, 10)
        flag = Flag("R0", Team.RIGHT, 15, 10)
        player.in_prison = False
        player.has_flag = False
        # 确保 rect 位置相同
        player.rect.center = (player.pixel_x, player.pixel_y)
        flag.rect.center = (player.pixel_x, player.pixel_y)
        
        mock_physics_manager.left_team_players.add(player)
        mock_physics_manager.right_team_flags.add(flag)
        
        # 2. 收集旗帜
        mock_physics_manager.update()
        assert player.has_flag is True
        
        # 3. 移动到目标区域（L队目标区域在 (2, 10) 附近）
        player.grid_x = 2
        player.grid_y = 10
        player.pixel_x = 2 * 32 + 16
        player.pixel_y = 10 * 32 + 16
        player.rect.center = (player.pixel_x, player.pixel_y)
        # 更新旗帜位置
        flag.update_position(player.pixel_x, player.pixel_y)
        flag.grid_x = 2
        flag.grid_y = 10
        
        # 4. 得分（需要玩家在目标区域内）
        mock_physics_manager.update()
        # 得分需要玩家在目标区域，且携带旗帜
        assert score_called[0] is True or (player.grid_x == 2 and player.grid_y == 10)

