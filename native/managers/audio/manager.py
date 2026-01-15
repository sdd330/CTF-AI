"""
Audio manager

Main facade class that coordinates sound and music playback.
Implements singleton pattern for global access.
"""

import pygame
from typing import Optional

from .sound_player import SoundPlayer
from .music_player import MusicPlayer


class AudioManager:
    """
    Audio manager

    Uses singleton pattern to ensure global unique instance.
    Coordinates SoundPlayer and MusicPlayer components.
    """

    _instance: Optional['AudioManager'] = None

    def __new__(cls) -> 'AudioManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # Check if pygame.mixer is available
        self._mixer_available = False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self._mixer_available = True
        except Exception as e:
            print(f"[AudioManager] Audio system initialization failed: {e}")

        # Initialize components
        self._sound_player = SoundPlayer(self._mixer_available)
        self._music_player = MusicPlayer(self._mixer_available)

        self._initialized = True

    @classmethod
    def get_instance(cls) -> 'AudioManager':
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset singleton instance (for testing)"""
        if cls._instance is not None:
            cls._instance.stop_all()
        cls._instance = None

    def is_available(self) -> bool:
        """Check if audio system is available"""
        return self._mixer_available

    # ========== Sound Effect Methods ==========

    def load_sound(self, key: str, path: Optional[str] = None):
        """Load a sound effect"""
        return self._sound_player.load_sound(key, path)

    def get_sound(self, key: str):
        """Get a loaded sound effect"""
        return self._sound_player.get_sound(key)

    def play_sound(self, key: str, loops: int = 0, volume: Optional[float] = None) -> bool:
        """Play a sound effect"""
        return self._sound_player.play(key, loops, volume)

    def stop_sound(self, key: str) -> None:
        """Stop a specific sound effect"""
        self._sound_player.stop(key)

    def preload_sounds(self, keys: list = None) -> int:
        """Preload sound effects"""
        return self._sound_player.preload(keys)

    # ========== Music Methods ==========

    def play_music(self, key: str, loops: int = -1, fade_ms: int = 0) -> bool:
        """Play background music"""
        return self._music_player.play(key, loops, fade_ms)

    def stop_music(self, fade_ms: int = 0) -> None:
        """Stop background music"""
        self._music_player.stop(fade_ms)

    def pause_music(self) -> None:
        """Pause background music"""
        self._music_player.pause()

    def resume_music(self) -> None:
        """Resume background music"""
        self._music_player.resume()

    def is_music_playing(self) -> bool:
        """Check if background music is playing"""
        return self._music_player.is_playing()

    def get_current_music(self) -> Optional[str]:
        """Get current music key name"""
        return self._music_player.get_current()

    # ========== Volume Control ==========

    def set_sfx_volume(self, volume: float) -> None:
        """Set sound effect volume (0.0 - 1.0)"""
        self._sound_player.set_volume(volume)

    def get_sfx_volume(self) -> float:
        """Get sound effect volume"""
        return self._sound_player.get_volume()

    def set_music_volume(self, volume: float) -> None:
        """Set music volume (0.0 - 1.0)"""
        self._music_player.set_volume(volume)

    def get_music_volume(self) -> float:
        """Get music volume"""
        return self._music_player.get_volume()

    # ========== Mute Control ==========

    def mute_sfx(self, muted: bool = True) -> None:
        """Mute/unmute sound effects"""
        self._sound_player.set_muted(muted)

    def mute_music(self, muted: bool = True) -> None:
        """Mute/unmute background music"""
        self._music_player.set_muted(muted)

    def is_sfx_muted(self) -> bool:
        """Check if sound effects are muted"""
        return self._sound_player.is_muted()

    def is_music_muted(self) -> bool:
        """Check if music is muted"""
        return self._music_player.is_muted()

    def toggle_sfx_mute(self) -> bool:
        """Toggle sound effect mute state"""
        return self._sound_player.toggle_mute()

    def toggle_music_mute(self) -> bool:
        """Toggle music mute state"""
        return self._music_player.toggle_mute()

    # ========== Resource Management ==========

    def clear_cache(self) -> None:
        """Clear sound cache"""
        self._sound_player.clear_cache()

    def stop_all(self) -> None:
        """Stop all sounds and music"""
        self._sound_player.stop_all()
        self._music_player.stop()

    # ========== Game Event Convenience Methods ==========

    def play_flag_pickup(self) -> bool:
        """Play flag pickup sound"""
        return self.play_sound('flag_pickup')

    def play_flag_score(self) -> bool:
        """Play score sound"""
        return self.play_sound('flag_score')

    def play_player_tagged(self) -> bool:
        """Play player tagged sound"""
        return self.play_sound('player_tagged')

    def play_player_rescued(self) -> bool:
        """Play player rescued sound"""
        return self.play_sound('player_rescued')

    def play_game_start(self) -> bool:
        """Play game start sound"""
        return self.play_sound('game_start')

    def play_game_over(self) -> bool:
        """Play game over sound"""
        return self.play_sound('game_over')
