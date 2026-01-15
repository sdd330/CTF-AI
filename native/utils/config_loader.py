"""
Configuration loading and validation utilities
Handles config file discovery, loading, and default values
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

from .constants import (
    TILE_SIZE, FPS, PLAYER_SPEED, DEFAULT_PRISON_DURATION
)


def find_config_path(config_path: Optional[Path] = None) -> Path:
    """
    Find configuration file path.

    Args:
        config_path: Explicit config path, or None for auto-discovery

    Returns:
        Path to configuration file
    """
    if config_path is not None:
        return config_path

    # Priority: native/game_config.json > frontend/public/game_config.json
    native_config = Path(__file__).parent.parent / "game_config.json"
    frontend_config = (
        Path(__file__).parent.parent.parent / "frontend" / "public" / "game_config.json"
    )

    if native_config.exists():
        return native_config
    elif frontend_config.exists():
        return frontend_config
    else:
        return native_config  # Default path even if not exists


def load_config_file(config_path: Path) -> Optional[Dict[str, Any]]:
    """
    Load configuration from JSON file.

    Args:
        config_path: Path to configuration file

    Returns:
        Configuration dict, or None if loading failed
    """
    if not config_path.exists():
        print(f"[Config] Config file not found: {config_path}, using defaults")
        return None

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"[Config] Loaded config file: {config_path}")
        return config
    except Exception as e:
        print(f"[Config] Failed to load config file: {e}, using defaults")
        return None


def get_default_config() -> Dict[str, Any]:
    """
    Get default configuration (matches frontend/public/game_config.json format).

    Returns:
        Default configuration dict
    """
    return {
        "teams": [
            {"name": "L", "who": "user48-1"},
            {"name": "R", "who": "user48-2"}
        ],
        "setup": {
            "numPlayers": 1,
            "numFlags": 1,
            "useRandomFlags": False,
            "mapWidth": 20,
            "mapHeight": 20
        },
        "servers": {
            "user48-1": "ws://0.0.0.0:34712",
            "user48-2": "ws://0.0.0.0:34713"
        },
        "native": {
            "fps": FPS,
            "tile_size": TILE_SIZE,
            "player_speed": PLAYER_SPEED,
            "prison_duration": DEFAULT_PRISON_DURATION,
            "win_score": 5,
            "screen": {
                "width": 1200,
                "height": 800,
                "fullscreen": False
            },
            "debug": {
                "show_fps": False,
                "show_grid": False,
                "show_debug_info": False
            }
        }
    }


def save_config_file(config: Dict[str, Any], path: Path) -> bool:
    """
    Save configuration to JSON file.

    Args:
        config: Configuration dict to save
        path: Path to save to

    Returns:
        True if successful, False otherwise
    """
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"[Config] Config saved to: {path}")
        return True
    except Exception as e:
        print(f"[Config] Failed to save config: {e}")
        return False


def get_nested_value(config: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """
    Get value from nested config using dot-separated path.

    Args:
        config: Configuration dict
        key_path: Dot-separated path (e.g., "game.fps")
        default: Default value if path not found

    Returns:
        Configuration value or default
    """
    keys = key_path.split('.')
    value = config
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    return value


def set_nested_value(config: Dict[str, Any], key_path: str, value: Any) -> None:
    """
    Set value in nested config using dot-separated path.

    Args:
        config: Configuration dict (modified in-place)
        key_path: Dot-separated path (e.g., "game.fps")
        value: Value to set
    """
    keys = key_path.split('.')
    current = config
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    current[keys[-1]] = value
