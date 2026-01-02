"""
输入管理器
设计模式：观察者模式 + 策略模式
统一处理键盘输入和远程控制
"""

import pygame
from abc import ABC, abstractmethod
from typing import Optional, Set, Callable, Dict
from ..utils import Direction


class InputObserver(ABC):
    """观察者接口"""
    
    @abstractmethod
    def on_input_change(self, direction: Direction):
        """
        当输入方向改变时调用
        
        Args:
            direction: 新的输入方向
        """
        pass


class InputStrategy(ABC):
    """输入策略接口"""
    
    @abstractmethod
    def get_direction(self) -> Direction:
        """
        获取当前输入方向
        
        Returns:
            当前方向，如果没有输入返回 Direction.STAY
        """
        pass
    
    @abstractmethod
    def update(self, delta_time: int):
        """
        更新输入状态
        
        Args:
            delta_time: 时间增量（毫秒）
        """
        pass


class KeyboardInputStrategy(InputStrategy):
    """键盘输入策略"""
    
    def __init__(self, key_mapping: Optional[Dict[int, Direction]] = None):
        """
        初始化键盘输入策略
        
        Args:
            key_mapping: 按键映射，格式为 {pygame.K_xxx: Direction}
                        如果为None，使用默认映射（WASD + 方向键）
        """
        if key_mapping is None:
            # 默认按键映射
            self.key_mapping = {
                pygame.K_w: Direction.UP,
                pygame.K_s: Direction.DOWN,
                pygame.K_a: Direction.LEFT,
                pygame.K_d: Direction.RIGHT,
                pygame.K_UP: Direction.UP,
                pygame.K_DOWN: Direction.DOWN,
                pygame.K_LEFT: Direction.LEFT,
                pygame.K_RIGHT: Direction.RIGHT,
            }
        else:
            self.key_mapping = key_mapping
        
        self.pressed_keys: Set[int] = set()
    
    def handle_key_down(self, key: int):
        """
        处理按键按下事件
        
        Args:
            key: 按键代码
        """
        if key in self.key_mapping:
            self.pressed_keys.add(key)
    
    def handle_key_up(self, key: int):
        """
        处理按键释放事件
        
        Args:
            key: 按键代码
        """
        if key in self.key_mapping:
            self.pressed_keys.discard(key)
    
    def get_direction(self) -> Direction:
        """获取当前输入方向（优先级：左 > 右 > 上 > 下）"""
        # 先检查模拟按键状态（pressed_keys）
        # 按优先级检查方向键
        if pygame.K_LEFT in self.pressed_keys or pygame.K_a in self.pressed_keys:
            return Direction.LEFT
        if pygame.K_RIGHT in self.pressed_keys or pygame.K_d in self.pressed_keys:
            return Direction.RIGHT
        if pygame.K_UP in self.pressed_keys or pygame.K_w in self.pressed_keys:
            return Direction.UP
        if pygame.K_DOWN in self.pressed_keys or pygame.K_s in self.pressed_keys:
            return Direction.DOWN
        
        return Direction.STAY
    
    def update(self, delta_time: int):
        """更新输入状态（键盘输入不需要特殊更新逻辑）"""
        pass


class RemoteInputStrategy(InputStrategy):
    """远程控制输入策略"""
    
    def __init__(self):
        """初始化远程控制输入策略"""
        self.remote_control: Optional[Direction] = None
    
    def set_remote_control(self, direction: Optional[Direction]):
        """
        设置远程控制方向
        
        Args:
            direction: 远程控制方向，None表示清除
        """
        self.remote_control = direction
    
    def get_direction(self) -> Direction:
        """获取远程控制方向"""
        return self.remote_control if self.remote_control else Direction.STAY
    
    def update(self, delta_time: int):
        """更新输入状态（远程输入不需要特殊更新逻辑）"""
        pass


class HybridInputStrategy(InputStrategy):
    """混合输入策略（键盘优先）"""
    
    def __init__(self, keyboard_strategy: KeyboardInputStrategy, 
                 remote_strategy: RemoteInputStrategy):
        """
        初始化混合输入策略
        
        Args:
            keyboard_strategy: 键盘输入策略
            remote_strategy: 远程控制策略
        """
        self.keyboard_strategy = keyboard_strategy
        self.remote_strategy = remote_strategy
    
    def get_direction(self) -> Direction:
        """获取输入方向（键盘输入优先）"""
        # 键盘输入优先
        keyboard_dir = self.keyboard_strategy.get_direction()
        if keyboard_dir != Direction.STAY:
            return keyboard_dir
        
        # 如果没有键盘输入，使用远程控制
        return self.remote_strategy.get_direction()
    
    def update(self, delta_time: int):
        """更新输入状态"""
        self.keyboard_strategy.update(delta_time)
        self.remote_strategy.update(delta_time)


class InputManager:
    """
    输入管理器
    统一管理键盘输入和远程控制
    使用策略模式和观察者模式
    使用单例模式
    """
    
    _instance = None
    
    def __new__(cls, strategy: Optional[InputStrategy] = None):
        """
        单例模式实现
        
        Args:
            strategy: 输入策略（仅在第一次实例化时使用）
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # 初始化仅在第一次创建实例时进行
            cls._instance._initialize(strategy)
        else:
            # 如果已经存在实例，并且提供了新的strategy，更新strategy
            if strategy is not None:
                cls._instance.strategy = strategy
        return cls._instance
    
    def _initialize(self, strategy: Optional[InputStrategy]):
        """
        初始化输入管理器
        
        Args:
            strategy: 输入策略
        """
        self.strategy = strategy
        self.observers: Set[InputObserver] = set()
        self.current_direction: Direction = Direction.STAY
        self.game_start_callback: Optional[Callable[[], None]] = None
        self.game_pause_callback: Optional[Callable[[], None]] = None
    
    def set_game_start_callback(self, callback: Callable[[], None]):
        """
        设置游戏开始回调
        
        Args:
            callback: 回调函数
        """
        self.game_start_callback = callback
    
    def set_game_pause_callback(self, callback: Callable[[], None]):
        """
        设置游戏暂停/继续回调
        
        Args:
            callback: 回调函数
        """
        self.game_pause_callback = callback
    
    def subscribe(self, observer: InputObserver):
        """
        注册观察者
        
        Args:
            observer: 观察者实例
        """
        self.observers.add(observer)
    
    def unsubscribe(self, observer: InputObserver):
        """
        取消注册观察者
        
        Args:
            observer: 观察者实例
        """
        self.observers.discard(observer)
    
    def _notify_observers(self, direction: Direction):
        """
        通知所有观察者
        
        Args:
            direction: 新的输入方向
        """
        for observer in self.observers:
            observer.on_input_change(direction)
    
    def handle_event(self, event: pygame.event.Event):
        """
        处理 pygame 事件
        
        Args:
            event: pygame 事件
        """
        if event.type == pygame.KEYDOWN:
            # 处理游戏控制按键
            if event.key == pygame.K_SPACE:
                self._handle_game_control()
            elif event.key == pygame.K_p:
                self._handle_pause_toggle()
            
            # 处理键盘输入策略的按键事件
            if isinstance(self.strategy, KeyboardInputStrategy):
                self.strategy.handle_key_down(event.key)
            elif isinstance(self.strategy, HybridInputStrategy):
                self.strategy.keyboard_strategy.handle_key_down(event.key)
        
        elif event.type == pygame.KEYUP:
            # 处理键盘输入策略的按键释放事件
            if isinstance(self.strategy, KeyboardInputStrategy):
                self.strategy.handle_key_up(event.key)
            elif isinstance(self.strategy, HybridInputStrategy):
                self.strategy.keyboard_strategy.handle_key_up(event.key)
    
    def _handle_game_control(self):
        """处理游戏控制（空格键：开始/暂停/继续）"""
        if self.game_start_callback:
            self.game_start_callback()
    
    def _handle_pause_toggle(self):
        """处理暂停切换（P键：暂停/继续）"""
        if self.game_pause_callback:
            self.game_pause_callback()
    
    def update(self, delta_time: int):
        """
        更新输入状态
        
        Args:
            delta_time: 时间增量（毫秒）
        """
        self.strategy.update(delta_time)
        new_direction = self.strategy.get_direction()
        
        # 如果方向改变，通知观察者
        if new_direction != self.current_direction:
            self.current_direction = new_direction
            self._notify_observers(new_direction)
    
    def get_current_direction(self) -> Direction:
        """
        获取当前输入方向
        
        Returns:
            当前输入方向
        """
        return self.current_direction
    
    def set_strategy(self, strategy: InputStrategy):
        """
        切换输入策略
        
        Args:
            strategy: 新的输入策略
        """
        self.strategy = strategy
    
    def set_remote_control(self, direction: Optional[Direction]):
        """
        设置远程控制方向
        
        Args:
            direction: 远程控制方向，None表示清除
        """
        # 确保strategy不是None
        if not self.strategy:
            return
            
        if isinstance(self.strategy, HybridInputStrategy):
            if self.strategy.remote_strategy:
                self.strategy.remote_strategy.set_remote_control(direction)
        elif isinstance(self.strategy, RemoteInputStrategy):
            self.strategy.set_remote_control(direction)
    
    def get_keyboard_strategy(self) -> Optional[KeyboardInputStrategy]:
        """
        获取键盘输入策略（如果存在）
        
        Returns:
            键盘输入策略，如果不存在返回None
        """
        if isinstance(self.strategy, KeyboardInputStrategy):
            return self.strategy
        elif isinstance(self.strategy, HybridInputStrategy):
            return self.strategy.keyboard_strategy
        return None
    
    def get_remote_strategy(self) -> Optional[RemoteInputStrategy]:
        """
        获取远程控制策略（如果存在）
        
        Returns:
            远程控制策略，如果不存在返回None
        """
        if isinstance(self.strategy, RemoteInputStrategy):
            return self.strategy
        elif isinstance(self.strategy, HybridInputStrategy):
            return self.strategy.remote_strategy
        return None

