"""
Game configuration loader.
"""

import json
from pathlib import Path
from typing import Optional

from .models import GameConfig


class ConfigLoader:
    """Handles loading game configuration from files."""

    @staticmethod
    def load(config_path: str = 'game_config.json') -> Optional[GameConfig]:
        """
        Load game configuration from file.

        Args:
            config_path: Path to the configuration file.

        Returns:
            GameConfig instance or None if loading fails.
        """
        try:
            path = Path(config_path)
            if not path.exists():
                # Try to find in native directory
                native_path = Path(__file__).parent.parent.parent / config_path
                if native_path.exists():
                    path = native_path
                else:
                    raise FileNotFoundError(f"Config file not found: {config_path}")

            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            setup = data.get('setup', {})
            config = GameConfig(
                num_players=setup.get('numPlayers', 3),
                num_flags=setup.get('numFlags', 9),
                use_random_flags=setup.get('useRandomFlags', True),
                map_width=setup.get('mapWidth', 20),
                map_height=setup.get('mapHeight', 20),
                servers=data.get('servers', {}),
                teams=data.get('teams', [])
            )

            print(f"[ConfigLoader] Configuration loaded successfully: {config}")
            return config

        except Exception as e:
            print(f"[ConfigLoader] Failed to load config: {e}")
            return None

    @staticmethod
    def get_default() -> GameConfig:
        """Return default game configuration."""
        return GameConfig()
