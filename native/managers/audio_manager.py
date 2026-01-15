"""
音频管理器 - 重导出模块
为保持向后兼容性，从 audio 子模块重导出
"""

from .audio import (
    SOUNDS_DIR,
    MUSIC_DIR,
    SOUND_EFFECTS,
    MUSIC_TRACKS,
    SoundPlayer,
    MusicPlayer,
    AudioManager,
)

__all__ = [
    'SOUNDS_DIR',
    'MUSIC_DIR',
    'SOUND_EFFECTS',
    'MUSIC_TRACKS',
    'SoundPlayer',
    'MusicPlayer',
    'AudioManager',
]
