"""
Game flow state enums.
"""

from enum import Enum


class GameFlowState(Enum):
    """Game flow states."""
    LOADING = 'loading'
    READY = 'ready'
    PLAYING = 'playing'
    ENDED = 'ended'


class GameFlowSubState(Enum):
    """Game flow sub-states."""
    LOADING_ASSETS = 'loadingAssets'
    LOADING_CONFIG = 'loadingConfig'
    RUNNING = 'running'
    PAUSED = 'paused'
