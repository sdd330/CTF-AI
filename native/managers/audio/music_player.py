"""
Background music player

Handles loading and playing background music tracks.
"""

import pygame
from typing import Optional

from .constants import AUDIO_DIR, SOUND_PATHS


class MusicPlayer:
    """
    Background music player component

    Manages background music playback, volume, and state.
    """

    def __init__(self, mixer_available: bool):
        """
        Initialize music player

        Args:
            mixer_available: Whether pygame mixer is available
        """
        self._mixer_available = mixer_available
        self._volume: float = 0.5
        self._muted: bool = False
        self._current_music: Optional[str] = None

    def play(self, key: str, loops: int = -1, fade_ms: int = 0) -> bool:
        """
        Play background music

        Args:
            key: Music key name
            loops: Loop count (-1 = infinite loop)
            fade_ms: Fade-in time (milliseconds)

        Returns:
            Whether playback succeeded
        """
        if not self._mixer_available:
            return False

        # Get path
        if key in SOUND_PATHS:
            music_path = AUDIO_DIR / SOUND_PATHS[key]
        else:
            music_path = AUDIO_DIR / key

        try:
            if not music_path.exists():
                return False

            # Stop current music
            pygame.mixer.music.stop()

            # Load and play new music
            pygame.mixer.music.load(str(music_path))
            pygame.mixer.music.set_volume(0 if self._muted else self._volume)

            if fade_ms > 0:
                pygame.mixer.music.play(loops=loops, fade_ms=fade_ms)
            else:
                pygame.mixer.music.play(loops=loops)

            self._current_music = key
            return True

        except Exception as e:
            print(f"[MusicPlayer] Failed to play music {key}: {e}")
            return False

    def stop(self, fade_ms: int = 0) -> None:
        """
        Stop background music

        Args:
            fade_ms: Fade-out time (milliseconds)
        """
        if not self._mixer_available:
            return

        try:
            if fade_ms > 0:
                pygame.mixer.music.fadeout(fade_ms)
            else:
                pygame.mixer.music.stop()
            self._current_music = None
        except Exception:
            pass

    def pause(self) -> None:
        """Pause background music"""
        if self._mixer_available:
            pygame.mixer.music.pause()

    def resume(self) -> None:
        """Resume background music"""
        if self._mixer_available:
            pygame.mixer.music.unpause()

    def is_playing(self) -> bool:
        """Check if background music is playing"""
        if not self._mixer_available:
            return False
        return pygame.mixer.music.get_busy()

    def get_current(self) -> Optional[str]:
        """Get current music key name"""
        return self._current_music

    # Volume and mute control
    def set_volume(self, volume: float) -> None:
        """Set music volume (0.0 - 1.0)"""
        self._volume = max(0.0, min(1.0, volume))
        if self._mixer_available and not self._muted:
            pygame.mixer.music.set_volume(self._volume)

    def get_volume(self) -> float:
        """Get music volume"""
        return self._volume

    def set_muted(self, muted: bool) -> None:
        """Set mute state"""
        self._muted = muted
        if self._mixer_available:
            pygame.mixer.music.set_volume(0 if muted else self._volume)

    def is_muted(self) -> bool:
        """Check if muted"""
        return self._muted

    def toggle_mute(self) -> bool:
        """Toggle mute state, returns new state"""
        self.set_muted(not self._muted)
        return self._muted
