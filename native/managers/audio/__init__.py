"""
Audio module - sound and music management
"""

from .constants import (
    SOUNDS_DIR,
    MUSIC_DIR,
    SOUND_EFFECTS,
    MUSIC_TRACKS,
)
from .sound_player import SoundPlayer
from .music_player import MusicPlayer
from .manager import AudioManager

__all__ = [
    'SOUNDS_DIR',
    'MUSIC_DIR',
    'SOUND_EFFECTS',
    'MUSIC_TRACKS',
    'SoundPlayer',
    'MusicPlayer',
    'AudioManager',
]
