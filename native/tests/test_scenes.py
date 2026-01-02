"""
场景系统测试
测试游戏场景的生命周期和事件处理
使用事件模拟和逻辑分离
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from native.scenes.base_scene import BaseScene
from native.utils import Team, Direction


@pytest.mark.unit
class TestBaseScene:
    """BaseScene 基础场景测试"""
    
    def test_scene_initialization(self):
        """测试场景初始化"""
        scene_manager = Mock()
        
        class TestScene(BaseScene):
            def create(self):
                pass  # 实现抽象方法
        
        scene = TestScene("TestScene", scene_manager)
        
        assert scene.scene_key == "TestScene"
        assert scene.scene_manager == scene_manager
    
    def test_scene_lifecycle_methods(self):
        """测试场景生命周期方法"""
        scene_manager = Mock()
        
        class TestScene(BaseScene):
            def preload(self):
                self.preloaded = True
            
            def create(self):
                self.created = True
            
            def update(self, delta_time):
                self.updated = True
            
            def render(self, screen):
                self.rendered = True
            
            def destroy(self):
                self.destroyed = True
        
        scene = TestScene("TestScene", scene_manager)
        
        # 测试生命周期方法
        scene.preload()
        assert scene.preloaded is True
        
        scene.create()
        assert scene.created is True
        
        scene.update(100)
        assert scene.updated is True
        
        scene.render(Mock())
        assert scene.rendered is True
        
        scene.destroy()
        assert scene.destroyed is True


@pytest.mark.unit
@pytest.mark.event
class TestEventHandling:
    """事件处理测试"""
    
    def test_event_simulator_register(self, event_simulator):
        """测试事件注册"""
        callback_called = [False]
        
        def callback():
            callback_called[0] = True
        
        event_simulator.register("test_event", callback)
        
        assert "test_event" in event_simulator.callbacks
        assert len(event_simulator.callbacks["test_event"]) == 1
    
    def test_event_simulator_emit(self, event_simulator):
        """测试事件触发"""
        callback_called = [False]
        callback_args = []
        
        def callback(*args, **kwargs):
            callback_called[0] = True
            callback_args.extend(args)
            callback_args.append(kwargs)
        
        event_simulator.register("test_event", callback)
        event_simulator.emit("test_event", "arg1", "arg2", key="value")
        
        assert callback_called[0] is True
        assert "arg1" in callback_args
        assert "arg2" in callback_args
    
    def test_event_simulator_multiple_callbacks(self, event_simulator):
        """测试多个回调"""
        callbacks_called = [False, False]
        
        def callback1():
            callbacks_called[0] = True
        
        def callback2():
            callbacks_called[1] = True
        
        event_simulator.register("test_event", callback1)
        event_simulator.register("test_event", callback2)
        
        event_simulator.emit("test_event")
        
        assert all(callbacks_called)
    
    def test_event_simulator_get_events(self, event_simulator):
        """测试获取事件历史"""
        event_simulator.emit("event1", "arg1")
        event_simulator.emit("event2", "arg2")
        event_simulator.emit("event1", "arg3")
        
        all_events = event_simulator.get_events()
        assert len(all_events) == 3
        
        event1_events = event_simulator.get_events("event1")
        assert len(event1_events) == 2
    
    def test_event_simulator_clear(self, event_simulator):
        """测试清空事件历史"""
        event_simulator.emit("test_event", "arg1")
        assert len(event_simulator.get_events()) > 0
        
        event_simulator.clear()
        assert len(event_simulator.get_events()) == 0


@pytest.mark.integration
@pytest.mark.event
class TestGameEvents:
    """游戏事件集成测试"""
    
    def test_player_move_event(self, event_simulator, mock_player):
        """测试玩家移动事件"""
        player = mock_player("L0", Team.LEFT, 5, 5)
        move_events = []
        
        def on_move(direction):
            move_events.append(direction)
        
        event_simulator.register("player_move", on_move)
        
        # 模拟玩家移动
        player.set_direction(Direction.RIGHT)
        event_simulator.emit("player_move", Direction.RIGHT)
        
        assert len(move_events) == 1
        assert move_events[0] == Direction.RIGHT
    
    def test_flag_pickup_event(self, event_simulator, mock_player, mock_flag):
        """测试旗帜拾取事件"""
        player = mock_player()
        flag = mock_flag()
        pickup_events = []
        
        def on_pickup(p, f):
            pickup_events.append((p, f))
        
        event_simulator.register("flag_pickup", on_pickup)
        
        # 模拟拾取旗帜
        player.pick_up_flag()
        flag.pick_up_by(player)
        event_simulator.emit("flag_pickup", player, flag)
        
        assert len(pickup_events) == 1
        assert pickup_events[0][0] == player
        assert pickup_events[0][1] == flag
    
    def test_score_event(self, event_simulator):
        """测试得分事件"""
        score_events = []
        
        def on_score(team, score):
            score_events.append((team, score))
        
        event_simulator.register("score", on_score)
        
        # 模拟得分
        event_simulator.emit("score", Team.LEFT, 1)
        event_simulator.emit("score", Team.RIGHT, 1)
        
        assert len(score_events) == 2
        assert score_events[0] == (Team.LEFT, 1)
        assert score_events[1] == (Team.RIGHT, 1)
    
    def test_game_over_event(self, event_simulator):
        """测试游戏结束事件"""
        game_over_events = []
        
        def on_game_over(winner):
            game_over_events.append(winner)
        
        event_simulator.register("game_over", on_game_over)
        
        # 模拟游戏结束
        event_simulator.emit("game_over", Team.LEFT)
        
        assert len(game_over_events) == 1
        assert game_over_events[0] == Team.LEFT


@pytest.mark.unit
class TestSceneTransitions:
    """场景转换测试"""
    
    def test_scene_activation(self):
        """测试场景激活"""
        scene_manager = Mock()
        scene_manager.screen = Mock()
        scene_manager.clock = Mock()
        
        class TestScene(BaseScene):
            def create(self):
                pass
        
        scene = TestScene("TestScene", scene_manager)
        scene.init(scene_manager.screen, scene_manager.clock)
        
        assert scene._initialized is True
    
    def test_scene_deactivation(self):
        """测试场景停用"""
        scene_manager = Mock()
        
        class TestScene(BaseScene):
            def create(self):
                pass
        
        scene = TestScene("TestScene", scene_manager)
        scene.destroy()
        
        assert scene._initialized is False
    
    def test_scene_manager_switch(self):
        """测试场景管理器切换场景"""
        scene_manager = Mock()
        scene_manager.screen = Mock()
        scene_manager.clock = Mock()
        switch_called = [False]
        
        def start_scene(scene_name, data=None):
            switch_called[0] = True
            assert scene_name == "NextScene"
        
        scene_manager.start_scene = start_scene
        
        class TestScene(BaseScene):
            def create(self):
                pass
            
            def some_action(self):
                self.scene_manager.start_scene("NextScene")
        
        scene = TestScene("TestScene", scene_manager)
        scene.some_action()
        
        assert switch_called[0] is True

