"""
Sound effect player

Handles loading, caching, and playing sound effects.
"""

import pygame
from pathlib import Path
from typing import Optional, Dict, List

from .constants import AUDIO_DIR, SOUND_PATHS


class SoundPlayer:
    """
    Sound effect player component

    Manages sound effect loading, caching, and playback.
    """

    def __init__(self, mixer_available: bool):
        """
        Initialize sound player

        Args:
            mixer_available: Whether pygame mixer is available
        """
        self._mixer_available = mixer_available
        self._sound_cache: Dict[str, pygame.mixer.Sound] = {}
        self._volume: float = 1.0
        self._muted: bool = False

    def load_sound(self, key: str, path: Optional[str] = None) -> Optional[pygame.mixer.Sound]:
        """
        Load a sound effect

        Args:
            key: Sound key name
            path: Custom path (optional)

        Returns:
            pygame.mixer.Sound or None
        """
        if not self._mixer_available:
            return None

        # Check cache
        if key in self._sound_cache:
            return self._sound_cache[key]

        # Get path
        if path:
            sound_path = Path(path)
        elif key in SOUND_PATHS:
            sound_path = AUDIO_DIR / SOUND_PATHS[key]
        else:
            sound_path = AUDIO_DIR / key

        try:
            if not sound_path.exists():
                # Sound file doesn't exist, silently return None
                return None

            sound = pygame.mixer.Sound(str(sound_path))
            self._sound_cache[key] = sound
            return sound

        except Exception as e:
            print(f"[SoundPlayer] Failed to load sound {key}: {e}")
            return None

    def get_sound(self, key: str) -> Optional[pygame.mixer.Sound]:
        """Get a loaded sound effect"""
        return self._sound_cache.get(key)

    def play(self, key: str, loops: int = 0, volume: Optional[float] = None) -> bool:
        """
        Play a sound effect

        Args:
            key: Sound key name
            loops: Loop count (0 = no loop, -1 = infinite loop)
            volume: Volume override (optional)

        Returns:
            Whether playback succeeded
        """
        if not self._mixer_available or self._muted:
            return False

        sound = self.get_sound(key) or self.load_sound(key)
        if not sound:
            return False

        try:
            # Set volume
            actual_volume = volume if volume is not None else self._volume
            sound.set_volume(actual_volume)

            # Play
            sound.play(loops=loops)
            return True

        except Exception as e:
            print(f"[SoundPlayer] Failed to play sound {key}: {e}")
            return False

    def stop(self, key: str) -> None:
        """Stop a specific sound effect"""
        sound = self.get_sound(key)
        if sound:
            sound.stop()

    def stop_all(self) -> None:
        """Stop all sound effects"""
        if self._mixer_available:
            pygame.mixer.stop()

    def preload(self, keys: Optional[List[str]] = None) -> int:
        """
        Preload sound effects

        Args:
            keys: List of sound keys to preload, defaults to all non-music sounds

        Returns:
            Number of successfully loaded sounds
        """
        if keys is None:
            keys = [k for k in SOUND_PATHS.keys() if not k.startswith('bgm_')]

        loaded = 0
        for key in keys:
            if self.load_sound(key):
                loaded += 1
        return loaded

    def clear_cache(self) -> None:
        """Clear sound cache"""
        for sound in self._sound_cache.values():
            sound.stop()
        self._sound_cache.clear()

    # Volume and mute control
    def set_volume(self, volume: float) -> None:
        """Set sound effect volume (0.0 - 1.0)"""
        self._volume = max(0.0, min(1.0, volume))

    def get_volume(self) -> float:
        """Get sound effect volume"""
        return self._volume

    def set_muted(self, muted: bool) -> None:
        """Set mute state"""
        self._muted = muted

    def is_muted(self) -> bool:
        """Check if muted"""
        return self._muted

    def toggle_mute(self) -> bool:
        """Toggle mute state, returns new state"""
        self._muted = not self._muted
        return self._muted
