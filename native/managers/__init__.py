"""
管理器模块
"""

# 使用延迟导入，避免在导入时触发所有模块的加载
__all__ = [
    'InputManager',
    'InputStrategy',
    'KeyboardInputStrategy',
    'RemoteInputStrategy',
    'HybridInputStrategy',
    'InputObserver',
    'PhysicsManager',
    'CollisionCallbacks',
    'SocketManager',
    'SocketEvent',
    'EventEmitter',
    'MapManager',
    'MapLayer',
    'TileData',
    'UIManager',
    'UIComponent',
    'UIComponentType',
    'UIComponentFactory',
    'GameStateManager',
    'GameFlowState',
    'GameFlowSubState',
    'StateSnapshot',
    'GameConfig',
    'TeamState',
    'AssetManager',
    'AssetType',
    'AudioManager',
    'SoundType',
]

# 延迟导入
# 当需要使用某个类时，才会导入对应的模块
def __getattr__(name):
    if name in __all__:
        if name in [
            'InputManager',
            'InputStrategy',
            'KeyboardInputStrategy',
            'RemoteInputStrategy',
            'HybridInputStrategy',
            'InputObserver',
        ]:
            from .input_manager import (
                InputManager,
                InputStrategy,
                KeyboardInputStrategy,
                RemoteInputStrategy,
                HybridInputStrategy,
                InputObserver,
            )
            return locals()[name]
        elif name in ['PhysicsManager', 'CollisionCallbacks']:
            from .physics_manager import PhysicsManager, CollisionCallbacks
            return locals()[name]
        elif name in ['SocketManager', 'SocketEvent', 'EventEmitter']:
            from .socket_manager import SocketManager, SocketEvent, EventEmitter
            return locals()[name]
        elif name in ['MapManager', 'MapLayer', 'TileData']:
            from .map_manager import MapManager, MapLayer, TileData
            return locals()[name]
        elif name in ['UIManager', 'UIComponent', 'UIComponentType', 'UIComponentFactory']:
            from .ui_manager import UIManager, UIComponent, UIComponentType, UIComponentFactory
            return locals()[name]
        elif name in ['GameStateManager', 'GameFlowState', 'GameFlowSubState', 'StateSnapshot', 'GameConfig', 'TeamState']:
            from .game_state_manager import GameStateManager, GameFlowState, GameFlowSubState, StateSnapshot, GameConfig, TeamState
            return locals()[name]
        elif name in ['AssetManager', 'AssetType']:
            from .asset_manager import AssetManager, AssetType
            return locals()[name]
        elif name in ['AudioManager', 'SoundType']:
            from .audio_manager import AudioManager, SoundType
            return locals()[name]
    raise AttributeError(f"module {__name__} has no attribute {name}")

