"""
输入管理器 - 统一管理键盘输入和远程控制
使用策略模式和观察者模式，单例实现
"""

import pygame
from typing import Optional, Set, Callable
from ...utils import Direction
from .input_strategy import InputStrategy, InputObserver
from .keyboard_handler import KeyboardInputStrategy
from .remote_handler import RemoteInputStrategy
from .hybrid_strategy import HybridInputStrategy


class InputManager:
    """输入管理器（单例模式）"""

    _instance = None

    def __new__(cls, strategy: Optional[InputStrategy] = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize(strategy)
        elif strategy is not None:
            cls._instance.strategy = strategy
        return cls._instance

    def _initialize(self, strategy: Optional[InputStrategy]):
        """初始化输入管理器"""
        self.strategy = strategy
        self.observers: Set[InputObserver] = set()
        self.current_direction: Direction = Direction.STAY
        self.game_start_callback: Optional[Callable[[], None]] = None
        self.game_pause_callback: Optional[Callable[[], None]] = None

    def set_game_start_callback(self, callback: Callable[[], None]):
        """设置游戏开始回调"""
        self.game_start_callback = callback

    def set_game_pause_callback(self, callback: Callable[[], None]):
        """设置游戏暂停/继续回调"""
        self.game_pause_callback = callback

    def subscribe(self, observer: InputObserver):
        """注册观察者"""
        self.observers.add(observer)

    def unsubscribe(self, observer: InputObserver):
        """取消注册观察者"""
        self.observers.discard(observer)

    def _notify_observers(self, direction: Direction):
        """通知所有观察者"""
        for observer in self.observers:
            observer.on_input_change(direction)

    def handle_event(self, event: pygame.event.Event):
        """处理 pygame 事件"""
        if event.type == pygame.KEYDOWN:
            self._handle_keydown(event.key)
        elif event.type == pygame.KEYUP:
            self._handle_keyup(event.key)

    def _handle_keydown(self, key: int):
        """处理按键按下事件"""
        if key == pygame.K_SPACE:
            self._handle_game_control()
        elif key == pygame.K_p:
            self._handle_pause_toggle()

        if isinstance(self.strategy, KeyboardInputStrategy):
            self.strategy.handle_key_down(key)
        elif isinstance(self.strategy, HybridInputStrategy):
            self.strategy.keyboard_strategy.handle_key_down(key)

    def _handle_keyup(self, key: int):
        """处理按键释放事件"""
        if isinstance(self.strategy, KeyboardInputStrategy):
            self.strategy.handle_key_up(key)
        elif isinstance(self.strategy, HybridInputStrategy):
            self.strategy.keyboard_strategy.handle_key_up(key)

    def _handle_game_control(self):
        """处理游戏控制（空格键）"""
        if self.game_start_callback:
            self.game_start_callback()

    def _handle_pause_toggle(self):
        """处理暂停切换（P键）"""
        if self.game_pause_callback:
            self.game_pause_callback()

    def update(self, delta_time: int):
        """更新输入状态"""
        self.strategy.update(delta_time)
        new_direction = self.strategy.get_direction()

        if new_direction != self.current_direction:
            self.current_direction = new_direction
            self._notify_observers(new_direction)

    def get_current_direction(self) -> Direction:
        """获取当前输入方向"""
        return self.current_direction

    def set_strategy(self, strategy: InputStrategy):
        """切换输入策略"""
        self.strategy = strategy

    def set_remote_control(self, direction: Optional[Direction]):
        """设置远程控制方向"""
        if not self.strategy:
            return

        if isinstance(self.strategy, HybridInputStrategy):
            if self.strategy.remote_strategy:
                self.strategy.remote_strategy.set_remote_control(direction)
        elif isinstance(self.strategy, RemoteInputStrategy):
            self.strategy.set_remote_control(direction)

    def get_keyboard_strategy(self) -> Optional[KeyboardInputStrategy]:
        """获取键盘输入策略"""
        if isinstance(self.strategy, KeyboardInputStrategy):
            return self.strategy
        elif isinstance(self.strategy, HybridInputStrategy):
            return self.strategy.keyboard_strategy
        return None

    def get_remote_strategy(self) -> Optional[RemoteInputStrategy]:
        """获取远程控制策略"""
        if isinstance(self.strategy, RemoteInputStrategy):
            return self.strategy
        elif isinstance(self.strategy, HybridInputStrategy):
            return self.strategy.remote_strategy
        return None
