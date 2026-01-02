"""
场景基类
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import pygame


class BaseScene(ABC):
    """
    场景基类
    
    每个场景都有以下生命周期方法：
    - preload(): 预加载资源（可选）
    - create(): 创建场景对象
    - update(): 更新场景（每帧调用）
    - destroy(): 销毁场景（清理资源）
    """
    
    def __init__(self, scene_key: str, scene_manager: 'SceneManager'):
        """
        初始化场景
        
        Args:
            scene_key: 场景唯一标识符
            scene_manager: 场景管理器
        """
        self.scene_key = scene_key
        self.scene_manager = scene_manager
        self.screen: Optional[pygame.Surface] = None
        self.clock: Optional[pygame.time.Clock] = None
        self._initialized = False
    
    def init(self, screen: pygame.Surface, clock: pygame.time.Clock):
        """
        初始化场景（由场景管理器调用）
        
        Args:
            screen: pygame Surface对象
            clock: pygame Clock对象
        """
        self.screen = screen
        self.clock = clock
        if not self._initialized:
            self.preload()
            self.create()
            self._initialized = True
    
    def preload(self):
        """
        预加载资源
        子类可以重写此方法来加载资源
        """
        pass
    
    @abstractmethod
    def create(self):
        """
        创建场景对象
        子类必须实现此方法
        """
        pass
    
    def update(self, delta_time: int):
        """
        更新场景
        
        Args:
            delta_time: 时间增量（毫秒）
        """
        pass
    
    def handle_event(self, event: pygame.event.Event):
        """
        处理事件
        
        Args:
            event: pygame事件
        """
        pass
    
    def render(self):
        """
        渲染场景
        子类可以重写此方法来自定义渲染
        """
        pass
    
    def destroy(self):
        """
        销毁场景
        子类可以重写此方法来清理资源
        """
        self._initialized = False
    
    def start_scene(self, scene_key: str, data: Optional[Dict[str, Any]] = None):
        """
        启动另一个场景
        
        Args:
            scene_key: 要启动的场景标识符
            data: 传递给场景的数据
        """
        self.scene_manager.start_scene(scene_key, data)
    
    def stop(self):
        """停止当前场景"""
        self.scene_manager.stop_scene(self.scene_key)
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(key={self.scene_key})"


class SceneManager:
    """
    场景管理器
    统一管理所有游戏场景的注册、切换和生命周期
    
    设计特点：
    - 单例模式：全局唯一的场景管理器
    - 统一注册：所有场景通过管理器注册
    - 生命周期管理：自动处理场景的创建、更新、渲染和销毁
    - 场景切换：支持场景间的数据传递
    """
    
    _instance: Optional['SceneManager'] = None
    
    def __new__(cls, screen: Optional[pygame.Surface] = None, clock: Optional[pygame.time.Clock] = None):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, screen: Optional[pygame.Surface] = None, clock: Optional[pygame.time.Clock] = None):
        """
        初始化场景管理器
        
        Args:
            screen: pygame Surface对象
            clock: pygame Clock对象
        """
        # 避免重复初始化
        if hasattr(self, '_initialized'):
            return
        
        self.screen = screen
        self.clock = clock
        self.scenes: Dict[str, BaseScene] = {}
        self.current_scene: Optional[BaseScene] = None
        self.current_scene_key: Optional[str] = None
        self.scene_history: list[str] = []  # 场景切换历史
        self._initialized = True
    
    def set_screen_and_clock(self, screen: pygame.Surface, clock: pygame.time.Clock):
        """
        设置屏幕和时钟（用于延迟初始化）
        
        Args:
            screen: pygame Surface对象
            clock: pygame Clock对象
        """
        self.screen = screen
        self.clock = clock
    
    def register_scene(self, scene: BaseScene):
        """
        注册场景
        
        Args:
            scene: 场景实例
        
        Raises:
            ValueError: 如果场景键已存在
        """
        if scene.scene_key in self.scenes:
            raise ValueError(f"场景 '{scene.scene_key}' 已注册")
        
        self.scenes[scene.scene_key] = scene
        print(f"[SceneManager] 注册场景: {scene.scene_key}")
    
    def register_scenes(self, scenes: list[BaseScene]):
        """
        批量注册场景
        
        Args:
            scenes: 场景实例列表
        """
        for scene in scenes:
            self.register_scene(scene)
    
    def get_scene(self, scene_key: str) -> Optional[BaseScene]:
        """
        获取场景实例
        
        Args:
            scene_key: 场景标识符
        
        Returns:
            场景实例，如果不存在返回None
        """
        return self.scenes.get(scene_key)
    
    def has_scene(self, scene_key: str) -> bool:
        """
        检查场景是否已注册
        
        Args:
            scene_key: 场景标识符
        
        Returns:
            如果场景已注册返回True
        """
        return scene_key in self.scenes
    
    def get_current_scene(self) -> Optional[BaseScene]:
        """
        获取当前场景
        
        Returns:
            当前场景实例
        """
        return self.current_scene
    
    def get_current_scene_key(self) -> Optional[str]:
        """
        获取当前场景键
        
        Returns:
            当前场景键
        """
        return self.current_scene_key
    
    def start_scene(self, scene_key: str, data: Optional[Dict[str, Any]] = None):
        """
        启动场景
        
        Args:
            scene_key: 场景标识符
            data: 传递给场景的数据
        
        Raises:
            ValueError: 如果场景未注册
        """
        if scene_key not in self.scenes:
            raise ValueError(f"场景 '{scene_key}' 未注册。可用场景: {list(self.scenes.keys())}")
        
        if not self.screen or not self.clock:
            raise RuntimeError("SceneManager 未初始化 screen 和 clock")
        
        old_scene_key = self.current_scene_key
        
        # 停止当前场景
        if self.current_scene:
            print(f"[SceneManager] 停止场景: {old_scene_key}")
            self.current_scene.destroy()
        
        # 启动新场景
        self.current_scene = self.scenes[scene_key]
        self.current_scene_key = scene_key
        
        # 记录场景历史
        if old_scene_key:
            self.scene_history.append(old_scene_key)
            # 限制历史记录长度
            if len(self.scene_history) > 10:
                self.scene_history.pop(0)
        
        print(f"[SceneManager] 启动场景: {scene_key}")
        self.current_scene.init(self.screen, self.clock)
        
        # 如果有数据，传递给场景
        if data and hasattr(self.current_scene, 'set_data'):
            self.current_scene.set_data(data)
    
    def stop_scene(self, scene_key: str):
        """
        停止场景
        
        Args:
            scene_key: 场景标识符
        """
        if self.current_scene_key == scene_key and self.current_scene:
            print(f"[SceneManager] 停止场景: {scene_key}")
            self.current_scene.destroy()
            self.current_scene = None
            self.current_scene_key = None
    
    def restart_current_scene(self, data: Optional[Dict[str, Any]] = None):
        """
        重启当前场景
        
        Args:
            data: 传递给场景的数据
        """
        if self.current_scene_key:
            self.start_scene(self.current_scene_key, data)
    
    def go_back(self):
        """
        返回到上一个场景
        """
        if self.scene_history:
            previous_scene = self.scene_history.pop()
            self.start_scene(previous_scene)
        else:
            print("[SceneManager] 没有可返回的场景")
    
    def update(self, delta_time: int):
        """
        更新当前场景
        
        Args:
            delta_time: 时间增量（毫秒）
        """
        if self.current_scene:
            self.current_scene.update(delta_time)
    
    def handle_event(self, event: pygame.event.Event):
        """
        处理事件
        
        Args:
            event: pygame事件
        """
        if self.current_scene:
            self.current_scene.handle_event(event)
    
    def render(self):
        """渲染当前场景"""
        if self.current_scene:
            self.current_scene.render()
        else:
            # 如果没有场景，清空屏幕
            if self.screen:
                self.screen.fill((0, 0, 0))
    
    def get_all_scene_keys(self) -> list[str]:
        """
        获取所有已注册的场景键
        
        Returns:
            场景键列表
        """
        return list(self.scenes.keys())
    
    def clear_all_scenes(self):
        """清除所有场景（用于清理）"""
        if self.current_scene:
            self.current_scene.destroy()
        
        for scene in self.scenes.values():
            scene.destroy()
        
        self.scenes.clear()
        self.current_scene = None
        self.current_scene_key = None
        self.scene_history.clear()
        print("[SceneManager] 已清除所有场景")
    
    def __repr__(self) -> str:
        return f"SceneManager(current={self.current_scene_key}, registered={list(self.scenes.keys())})"

