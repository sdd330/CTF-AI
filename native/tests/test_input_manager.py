"""
InputManager 单元测试
测试输入管理器的所有功能
"""

import pytest
from unittest.mock import Mock, patch
from native.managers import (
    InputManager,
    KeyboardInputStrategy,
    RemoteInputStrategy,
    HybridInputStrategy,
    InputObserver
)
from native.utils import Team, Direction


class MockObserver(InputObserver):
    """模拟观察者"""
    
    def __init__(self):
        self.called = False
        self.last_direction = None
    
    def on_input_change(self, direction: Direction):
        self.called = True
        self.last_direction = direction


@pytest.mark.unit
class TestKeyboardInputStrategy:
    """KeyboardInputStrategy 测试"""
    
    def test_handle_key_down_event(self, mock_pygame):
        """测试处理按键按下事件"""
        strategy = KeyboardInputStrategy()
        pygame = mock_pygame
        
        # 测试 WASD 按键
        strategy.handle_key_down(pygame.K_w)
        assert pygame.K_w in strategy.pressed_keys
        
        strategy.handle_key_down(pygame.K_s)
        assert pygame.K_s in strategy.pressed_keys
        
        strategy.handle_key_down(pygame.K_a)
        assert pygame.K_a in strategy.pressed_keys
        
        strategy.handle_key_down(pygame.K_d)
        assert pygame.K_d in strategy.pressed_keys
        
        # 测试方向键
        strategy.handle_key_down(pygame.K_UP)
        assert pygame.K_UP in strategy.pressed_keys
        
        strategy.handle_key_down(pygame.K_DOWN)
        assert pygame.K_DOWN in strategy.pressed_keys
        
        strategy.handle_key_down(pygame.K_LEFT)
        assert pygame.K_LEFT in strategy.pressed_keys
        
        strategy.handle_key_down(pygame.K_RIGHT)
        assert pygame.K_RIGHT in strategy.pressed_keys
    
    def test_handle_key_up_event(self, mock_pygame):
        """测试处理按键释放事件"""
        strategy = KeyboardInputStrategy()
        pygame = mock_pygame
        
        # 先按下按键
        strategy.handle_key_down(pygame.K_w)
        assert pygame.K_w in strategy.pressed_keys
        
        # 然后释放按键
        strategy.handle_key_up(pygame.K_w)
        assert pygame.K_w not in strategy.pressed_keys
    
    def test_get_direction(self, mock_pygame):
        """测试获取方向"""
        strategy = KeyboardInputStrategy()
        pygame = mock_pygame
        
        # 测试按下W键
        strategy.handle_key_down(pygame.K_w)
        assert strategy.get_direction() == Direction.UP
        
        # 测试按下S键
        strategy.handle_key_down(pygame.K_s)
        # 优先级：左 > 右 > 上 > 下，所以应该返回UP
        assert strategy.get_direction() == Direction.UP
        
        # 测试按下A键
        strategy.handle_key_down(pygame.K_a)
        # 左优先级最高，应该返回LEFT
        assert strategy.get_direction() == Direction.LEFT
        
        # 测试按下D键
        strategy.handle_key_down(pygame.K_d)
        # 右优先级高于上和下，应该返回LEFT
        assert strategy.get_direction() == Direction.LEFT
        
        # 释放所有按键
        strategy.handle_key_up(pygame.K_w)
        strategy.handle_key_up(pygame.K_s)
        strategy.handle_key_up(pygame.K_a)
        strategy.handle_key_up(pygame.K_d)
        # 没有按键按下，应该返回STAY
        assert strategy.get_direction() == Direction.STAY


@pytest.mark.unit
class TestRemoteInputStrategy:
    """RemoteInputStrategy 测试"""
    
    def test_set_remote_control(self):
        """测试设置远程控制"""
        strategy = RemoteInputStrategy()
        strategy.set_remote_control(Direction.UP)
        assert strategy.remote_control == Direction.UP
    
    def test_get_direction(self):
        """测试获取方向"""
        strategy = RemoteInputStrategy()
        strategy.set_remote_control(Direction.RIGHT)
        assert strategy.get_direction() == Direction.RIGHT
    
    def test_get_direction_none(self):
        """测试未设置时返回 STAY"""
        strategy = RemoteInputStrategy()
        # 根据实际实现，未设置时应该返回 Direction.STAY
        assert strategy.get_direction() == Direction.STAY
    
    def test_get_direction_with_value(self):
        """测试设置方向后返回正确值"""
        strategy = RemoteInputStrategy()
        strategy.set_remote_control(Direction.LEFT)
        assert strategy.get_direction() == Direction.LEFT
        
        strategy.set_remote_control(Direction.DOWN)
        assert strategy.get_direction() == Direction.DOWN


@pytest.mark.unit
class TestHybridInputStrategy:
    """HybridInputStrategy 测试"""
    
    def test_keyboard_priority(self, mock_pygame):
        """测试键盘输入优先"""
        keyboard_strategy = KeyboardInputStrategy()
        remote_strategy = RemoteInputStrategy()
        strategy = HybridInputStrategy(keyboard_strategy, remote_strategy)
        pygame = mock_pygame
        
        # 设置远程控制
        remote_strategy.set_remote_control(Direction.UP)
        
        # 模拟键盘按下D键（向右）
        keyboard_strategy.handle_key_down(pygame.K_d)
        
        # 获取方向
        direction = strategy.get_direction()
        
        # 应该返回键盘输入（RIGHT），而不是远程控制（UP）
        assert direction == Direction.RIGHT
    
    def test_remote_fallback(self):
        """测试远程控制作为备选"""
        keyboard_strategy = KeyboardInputStrategy()
        remote_strategy = RemoteInputStrategy()
        strategy = HybridInputStrategy(keyboard_strategy, remote_strategy)
        
        # 设置远程控制
        remote_strategy.set_remote_control(Direction.UP)
        
        # 没有键盘输入（确保没有按键按下）
        direction = strategy.get_direction()
        
        # 应该返回远程控制
        assert direction == Direction.UP


@pytest.mark.unit
class TestInputManager:
    """InputManager 测试"""
    
    def test_singleton_pattern(self):
        """测试单例模式"""
        # 重置单例
        InputManager._instance = None
        
        strategy1 = RemoteInputStrategy()
        manager1 = InputManager(strategy1)
        
        strategy2 = RemoteInputStrategy()
        manager2 = InputManager(strategy2)
        
        # 应该是同一个实例
        assert manager1 is manager2
        
        # 清理
        InputManager._instance = None
    
    def test_subscribe(self):
        """测试订阅观察者"""
        InputManager._instance = None
        strategy = RemoteInputStrategy()
        manager = InputManager(strategy)
        observer = MockObserver()
        
        manager.subscribe(observer)
        assert observer in manager.observers
        
        # 清理
        InputManager._instance = None
    
    def test_unsubscribe(self):
        """测试取消订阅观察者"""
        InputManager._instance = None
        strategy = RemoteInputStrategy()
        manager = InputManager(strategy)
        observer = MockObserver()
        
        manager.subscribe(observer)
        manager.unsubscribe(observer)
        assert observer not in manager.observers
        
        # 清理
        InputManager._instance = None
    
    def test_notify_observers(self):
        """测试通知观察者"""
        InputManager._instance = None
        strategy = RemoteInputStrategy()
        manager = InputManager(strategy)
        observer = MockObserver()
        
        manager.subscribe(observer)
        
        # 模拟输入变化
        manager._notify_observers(Direction.UP)
        
        assert observer.called is True
        assert observer.last_direction == Direction.UP
        
        # 清理
        InputManager._instance = None
    
    def test_set_remote_control(self):
        """测试设置远程控制"""
        InputManager._instance = None
        remote_strategy = RemoteInputStrategy()
        manager = InputManager(remote_strategy)
        
        manager.set_remote_control(Direction.UP)
        assert remote_strategy.remote_control == Direction.UP
        
        # 清理
        InputManager._instance = None
    
    def test_set_remote_control_hybrid(self):
        """测试混合策略的远程控制"""
        InputManager._instance = None
        keyboard_strategy = KeyboardInputStrategy()
        remote_strategy = RemoteInputStrategy()
        hybrid_strategy = HybridInputStrategy(keyboard_strategy, remote_strategy)
        manager = InputManager(hybrid_strategy)
        
        manager.set_remote_control(Direction.UP)
        assert remote_strategy.remote_control == Direction.UP
        
        # 清理
        InputManager._instance = None
    
    def test_update_remote_strategy(self):
        """测试更新远程策略"""
        InputManager._instance = None
        remote_strategy = RemoteInputStrategy()
        manager = InputManager(remote_strategy)
        observer = MockObserver()
        manager.subscribe(observer)
        
        # 设置远程控制
        manager.set_remote_control(Direction.UP)
        
        # 更新
        manager.update(100)
        
        # 应该通知观察者
        assert observer.called is True
        assert observer.last_direction == Direction.UP
        
        # 清理
        InputManager._instance = None
