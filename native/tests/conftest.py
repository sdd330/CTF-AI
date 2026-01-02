"""
pytest 配置和共享 fixtures
提供事件模拟、逻辑分离的测试基础设施
"""

import sys
import os
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch
import pytest

# 添加 native 目录的父目录到路径
native_dir = Path(__file__).parent.parent
parent_dir = native_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Mock pygame 在导入任何 native 模块之前
pygame_mock = MagicMock()
pygame_mock.K_w = 119
pygame_mock.K_s = 115
pygame_mock.K_a = 97
pygame_mock.K_d = 100
pygame_mock.K_UP = 273
pygame_mock.K_DOWN = 274
pygame_mock.K_LEFT = 276
pygame_mock.K_RIGHT = 275
pygame_mock.K_SPACE = 32
pygame_mock.KEYDOWN = 2
pygame_mock.KEYUP = 3
pygame_mock.event = MagicMock()
pygame_mock.event.Event = MagicMock

# Mock pygame.sprite
class MockGroup(list):
    """Mock Group 类，继承自 list 以支持迭代"""
    def add(self, sprite):
        if sprite not in self:
            self.append(sprite)
    
    def remove(self, sprite):
        if sprite in self:
            list.remove(self, sprite)
    
    def has(self, sprite):
        return sprite in self

class MockSprite:
    """简单的 Sprite 基类，用于测试"""
    pass

pygame_mock.sprite = MagicMock()
pygame_mock.sprite.Group = MockGroup
pygame_mock.sprite.Sprite = MockSprite
def mock_groupcollide(g1, g2, d1, d2, collided=None):
    """Mock groupcollide 函数"""
    collisions = {}
    if collided:
        for s1 in g1:
            for s2 in g2:
                if collided(s1, s2):
                    if s1 not in collisions:
                        collisions[s1] = []
                    collisions[s1].append(s2)
    return collisions

pygame_mock.sprite.groupcollide = mock_groupcollide

# Mock pygame.Rect
def mock_rect(x, y, width, height):
    rect = MagicMock()
    rect.x = x
    rect.y = y
    rect.width = width
    rect.height = height
    rect.center = (x + width // 2, y + height // 2)
    rect.left = x
    rect.top = y
    rect.right = x + width
    rect.bottom = y + height
    return rect

pygame_mock.Rect = mock_rect

# Mock pygame.Surface
pygame_mock.Surface = MagicMock

# Mock pygame.draw
pygame_mock.draw = MagicMock()
pygame_mock.draw.line = MagicMock()

# Mock pygame.image
pygame_mock.image = MagicMock()
pygame_mock.image.load = MagicMock()

# 将 pygame mock 插入到 sys.modules
sys.modules['pygame'] = pygame_mock


# ========== Fixtures ==========

@pytest.fixture
def mock_pygame():
    """提供 mock 的 pygame 模块"""
    return pygame_mock


@pytest.fixture
def mock_game_map():
    """创建模拟游戏地图"""
    from native.map.map import GameMap
    
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
    return game_map


@pytest.fixture
def game_state():
    """创建游戏状态实例"""
    from native.game.game_state import GameState
    return GameState()


@pytest.fixture
def ctf_game(mock_game_map):
    """创建 CTFGame 实例"""
    from native.game.game import CTFGame
    game = CTFGame(mock_game_map)
    return game


@pytest.fixture
def mock_player():
    """创建模拟玩家"""
    from native.objects.player import Player
    from native.utils import Team
    
    def _create_player(name="L0", team=Team.LEFT, x=2, y=1):
        return Player(name, team, x, y)
    return _create_player


@pytest.fixture
def mock_flag():
    """创建模拟旗帜"""
    from native.objects.flag import Flag
    from native.utils import Team
    
    def _create_flag(flag_id="L0", team=Team.LEFT, x=1, y=1):
        return Flag(flag_id, team, x, y)
    return _create_flag


@pytest.fixture
def event_simulator():
    """事件模拟器 - 用于模拟游戏事件"""
    class EventSimulator:
        def __init__(self):
            self.events = []
            self.callbacks = {}
        
        def register(self, event_type, callback):
            """注册事件回调"""
            if event_type not in self.callbacks:
                self.callbacks[event_type] = []
            self.callbacks[event_type].append(callback)
        
        def emit(self, event_type, *args, **kwargs):
            """触发事件"""
            self.events.append((event_type, args, kwargs))
            if event_type in self.callbacks:
                for callback in self.callbacks[event_type]:
                    callback(*args, **kwargs)
        
        def clear(self):
            """清空事件历史"""
            self.events.clear()
        
        def get_events(self, event_type=None):
            """获取事件历史"""
            if event_type:
                return [e for e in self.events if e[0] == event_type]
            return self.events
    
    return EventSimulator()


@pytest.fixture
def mock_input_manager():
    """创建模拟输入管理器"""
    from native.managers import InputManager, RemoteInputStrategy
    
    # 重置单例
    InputManager._instance = None
    
    strategy = RemoteInputStrategy()
    manager = InputManager(strategy)
    
    yield manager
    
    # 清理
    InputManager._instance = None


@pytest.fixture
def mock_physics_manager(mock_game_map):
    """创建模拟物理管理器"""
    from native.managers import PhysicsManager, CollisionCallbacks
    
    callbacks = CollisionCallbacks()
    manager = PhysicsManager(mock_game_map, callbacks)
    
    # 创建 sprite groups
    left_players = pygame_mock.sprite.Group()
    right_players = pygame_mock.sprite.Group()
    left_flags = pygame_mock.sprite.Group()
    right_flags = pygame_mock.sprite.Group()
    
    manager.set_game_objects(
        left_players,
        right_players,
        left_flags,
        right_flags
    )
    
    # 设置区域
    from native.utils import Team
    left_target_positions = [(pos.x, pos.y) for pos in mock_game_map.get_team_target_positions(Team.LEFT)]
    right_target_positions = [(pos.x, pos.y) for pos in mock_game_map.get_team_target_positions(Team.RIGHT)]
    left_prison_positions = [(pos.x, pos.y) for pos in mock_game_map.get_team_prison_positions(Team.LEFT)]
    right_prison_positions = [(pos.x, pos.y) for pos in mock_game_map.get_team_prison_positions(Team.RIGHT)]
    
    manager.set_zones(
        left_target_positions,
        right_target_positions,
        left_prison_positions,
        right_prison_positions
    )
    
    yield manager
    
    # 清理：清空所有 sprite groups 和状态
    if hasattr(manager, 'left_team_players') and manager.left_team_players:
        manager.left_team_players.clear()
    if hasattr(manager, 'right_team_players') and manager.right_team_players:
        manager.right_team_players.clear()
    if hasattr(manager, 'left_team_flags') and manager.left_team_flags:
        manager.left_team_flags.clear()
    if hasattr(manager, 'right_team_flags') and manager.right_team_flags:
        manager.right_team_flags.clear()
    if hasattr(manager, '_dropped_flags_this_frame'):
        manager._dropped_flags_this_frame.clear()


@pytest.fixture(autouse=True)
def reset_singletons():
    """自动重置单例（每个测试前）"""
    yield
    # 清理单例
    from native.managers import InputManager
    InputManager._instance = None

