"""
Audio constants and enums

Defines sound types and resource paths for the audio system.
"""

from pathlib import Path
from enum import Enum


class SoundType(Enum):
    """Sound type enumeration"""
    SFX = 'sfx'       # Sound effects
    MUSIC = 'music'   # Background music


# Resource directory
AUDIO_DIR = Path(__file__).parent.parent.parent / "assets" / "audio"

# Predefined sound paths
SOUND_PATHS = {
    # Game sound effects
    'flag_pickup': 'flag_pickup.wav',
    'flag_score': 'flag_score.wav',
    'player_tagged': 'player_tagged.wav',
    'player_rescued': 'player_rescued.wav',
    'game_start': 'game_start.wav',
    'game_over': 'game_over.wav',
    # Background music
    'bgm_menu': 'bgm_menu.mp3',
    'bgm_game': 'bgm_game.mp3',
}
