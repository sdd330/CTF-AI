"""
游戏场景模块
使用 SceneManager 统一管理所有游戏场景

场景系统特点：
- 单例模式：SceneManager 是全局唯一的场景管理器
- 统一注册：所有场景通过 SceneManager 注册
- 生命周期管理：自动处理场景的创建、更新、渲染和销毁
- 场景切换：支持场景间的数据传递和历史记录
"""

from .base_scene import BaseScene, SceneManager
from .boot_scene import BootScene
from .preloader_scene import PreloaderScene
from .game_scene import GameScene
from .game_over_scene import GameOverScene

__all__ = [
    'BaseScene',
    'SceneManager',  # 场景管理器（单例模式）
    'BootScene',
    'PreloaderScene',
    'GameScene',
    'GameOverScene',
]

