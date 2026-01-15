"""
Game configuration system
Supports loading game parameters from configuration files
"""

from pathlib import Path
from typing import Dict, Any, Optional

from .constants import (
    TILE_SIZE, FPS, PLAYER_SPEED, DEFAULT_PRISON_DURATION
)
from .config_loader import (
    find_config_path, load_config_file, get_default_config,
    save_config_file, get_nested_value, set_nested_value
)


class GameConfig:
    """Game configuration class"""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize configuration.

        Args:
            config_path: Config file path, or None to use default discovery
        """
        self.config_path = find_config_path(config_path)
        self._config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self):
        """Load configuration file"""
        loaded = load_config_file(self.config_path)
        self._config = loaded if loaded is not None else get_default_config()

    def get(self, key_path: str, default: Any = None) -> Any:
        """Get config value using dot-separated path"""
        return get_nested_value(self._config, key_path, default)

    def set(self, key_path: str, value: Any):
        """Set config value using dot-separated path"""
        set_nested_value(self._config, key_path, value)

    def save(self, path: Optional[Path] = None):
        """Save configuration to file"""
        save_config_file(self._config, path or self.config_path)

    # Basic game properties
    @property
    def fps(self) -> int:
        return self.get("game.fps", FPS)

    @property
    def tile_size(self) -> int:
        return self.get("game.tile_size", TILE_SIZE)

    @property
    def player_speed(self) -> int:
        return self.get("game.player_speed", PLAYER_SPEED)

    @property
    def prison_duration(self) -> int:
        return self.get("game.prison_duration", DEFAULT_PRISON_DURATION)

    @property
    def win_score(self) -> int:
        return self.get("native.win_score", 5)

    # Frontend-format config properties
    @property
    def teams(self) -> list:
        return self.get("teams", [{"name": "L", "who": "user48-1"}, {"name": "R", "who": "user48-2"}])

    @property
    def num_players(self) -> int:
        return self.get("setup.numPlayers", 1)

    @property
    def num_flags(self) -> int:
        return self.get("setup.numFlags", 1)

    @property
    def use_random_flags(self) -> bool:
        return self.get("setup.useRandomFlags", False)

    @property
    def map_width(self) -> int:
        return self.get("setup.mapWidth", 20)

    @property
    def map_height(self) -> int:
        return self.get("setup.mapHeight", 20)

    @property
    def servers(self) -> Dict[str, str]:
        return self.get("servers", {})

    def get_server_url(self, who: str) -> Optional[str]:
        """Get server URL for specified user identifier"""
        return self.servers.get(who)

    def get_team_server_url(self, team_name: str) -> Optional[str]:
        """Get server URL for specified team name ('L' or 'R')"""
        for team in self.teams:
            if team.get("name") == team_name:
                who = team.get("who")
                if who:
                    return self.get_server_url(who)
        return None

    # Native-specific config properties
    @property
    def screen_width(self) -> int:
        return self.get("native.screen.width", 1200)

    @property
    def screen_height(self) -> int:
        return self.get("native.screen.height", 800)

    @property
    def fullscreen(self) -> bool:
        return self.get("native.screen.fullscreen", False)

    @property
    def show_fps(self) -> bool:
        return self.get("native.debug.show_fps", False)

    @property
    def show_grid(self) -> bool:
        return self.get("native.debug.show_grid", False)

    @property
    def show_debug_info(self) -> bool:
        return self.get("native.debug.show_debug_info", False)


# Global config instance
_config_instance: Optional[GameConfig] = None


def get_config(config_path: Optional[Path] = None) -> GameConfig:
    """
    Get global config instance (singleton pattern).

    Args:
        config_path: Config file path

    Returns:
        Config instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = GameConfig(config_path)
    return _config_instance
