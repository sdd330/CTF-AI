"""
游戏配置系统
支持从配置文件加载游戏参数
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from .constants import (
    TILE_SIZE, FPS, PLAYER_SPEED, DEFAULT_PRISON_DURATION,
    COLOR_LEFT_TEAM, COLOR_RIGHT_TEAM
)


class GameConfig:
    """游戏配置类"""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        初始化配置
        
        Args:
            config_path: 配置文件路径，如果为 None 则使用默认配置
                        默认路径：native/game_config.json（参照 frontend/public/game_config.json）
        """
        if config_path is None:
            # 优先尝试 native/game_config.json
            native_config = Path(__file__).parent.parent / "game_config.json"
            # 如果不存在，尝试 frontend/public/game_config.json
            frontend_config = Path(__file__).parent.parent.parent / "frontend" / "public" / "game_config.json"
            if native_config.exists():
                self.config_path = native_config
            elif frontend_config.exists():
                self.config_path = frontend_config
            else:
                self.config_path = native_config  # 使用默认路径，即使不存在
        else:
            self.config_path = config_path
        self._config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
                print(f"[Config] 已加载配置文件: {self.config_path}")
            except Exception as e:
                print(f"[Config] 加载配置文件失败: {e}，使用默认配置")
                self._set_defaults()
        else:
            print(f"[Config] 配置文件不存在: {self.config_path}，使用默认配置")
            self._set_defaults()
    
    def _set_defaults(self):
        """设置默认配置（参照 frontend/public/game_config.json 格式）"""
        self._config = {
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
            # Native 特有的配置项
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
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        获取配置值（支持点号分隔的路径）
        
        Args:
            key_path: 配置路径，如 "game.fps"
            default: 默认值
        
        Returns:
            配置值
        """
        keys = key_path.split('.')
        value = self._config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def set(self, key_path: str, value: Any):
        """
        设置配置值（支持点号分隔的路径）
        
        Args:
            key_path: 配置路径，如 "game.fps"
            value: 配置值
        """
        keys = key_path.split('.')
        config = self._config
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        config[keys[-1]] = value
    
    def save(self, path: Optional[Path] = None):
        """
        保存配置到文件
        
        Args:
            path: 保存路径，如果为 None 则使用初始化时的路径
        """
        save_path = path or self.config_path
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            print(f"[Config] 配置已保存到: {save_path}")
        except Exception as e:
            print(f"[Config] 保存配置失败: {e}")
    
    @property
    def fps(self) -> int:
        """获取帧率"""
        return self.get("game.fps", FPS)
    
    @property
    def tile_size(self) -> int:
        """获取格子大小"""
        return self.get("game.tile_size", TILE_SIZE)
    
    @property
    def player_speed(self) -> int:
        """获取玩家速度"""
        return self.get("game.player_speed", PLAYER_SPEED)
    
    @property
    def prison_duration(self) -> int:
        """获取监狱持续时间"""
        return self.get("game.prison_duration", DEFAULT_PRISON_DURATION)
    
    @property
    def win_score(self) -> int:
        """获取胜利分数"""
        return self.get("native.win_score", 5)
    
    # Frontend 格式的配置属性
    @property
    def teams(self) -> list:
        """获取队伍配置"""
        return self.get("teams", [{"name": "L", "who": "user48-1"}, {"name": "R", "who": "user48-2"}])
    
    @property
    def num_players(self) -> int:
        """获取每队玩家数量（从 setup.numPlayers）"""
        return self.get("setup.numPlayers", 1)
    
    @property
    def num_flags(self) -> int:
        """获取每队旗帜数量（从 setup.numFlags）"""
        return self.get("setup.numFlags", 1)
    
    @property
    def use_random_flags(self) -> bool:
        """获取是否使用随机旗帜"""
        return self.get("setup.useRandomFlags", False)
    
    @property
    def map_width(self) -> int:
        """获取地图宽度（从 setup.mapWidth）"""
        return self.get("setup.mapWidth", 20)
    
    @property
    def map_height(self) -> int:
        """获取地图高度（从 setup.mapHeight）"""
        return self.get("setup.mapHeight", 20)
    
    @property
    def servers(self) -> Dict[str, str]:
        """获取服务器配置"""
        return self.get("servers", {})
    
    def get_server_url(self, who: str) -> Optional[str]:
        """
        获取指定用户的服务器 URL
        
        Args:
            who: 用户标识（如 "user48-1"）
        
        Returns:
            服务器 URL，如果不存在则返回 None
        """
        servers = self.servers
        return servers.get(who)
    
    def get_team_server_url(self, team_name: str) -> Optional[str]:
        """
        获取指定队伍的服务器 URL
        
        Args:
            team_name: 队伍名称（"L" 或 "R"）
        
        Returns:
            服务器 URL，如果不存在则返回 None
        """
        teams = self.teams
        for team in teams:
            if team.get("name") == team_name:
                who = team.get("who")
                if who:
                    return self.get_server_url(who)
        return None
    
    # Native 特有的配置属性
    @property
    def screen_width(self) -> int:
        """获取屏幕宽度"""
        return self.get("native.screen.width", 1200)
    
    @property
    def screen_height(self) -> int:
        """获取屏幕高度"""
        return self.get("native.screen.height", 800)
    
    @property
    def fullscreen(self) -> bool:
        """获取是否全屏"""
        return self.get("native.screen.fullscreen", False)
    
    @property
    def show_fps(self) -> bool:
        """获取是否显示 FPS"""
        return self.get("native.debug.show_fps", False)
    
    @property
    def show_grid(self) -> bool:
        """获取是否显示网格"""
        return self.get("native.debug.show_grid", False)
    
    @property
    def show_debug_info(self) -> bool:
        """获取是否显示调试信息"""
        return self.get("native.debug.show_debug_info", False)


# 全局配置实例
_config_instance: Optional[GameConfig] = None


def get_config(config_path: Optional[Path] = None) -> GameConfig:
    """
    获取全局配置实例（单例模式）
    
    Args:
        config_path: 配置文件路径
    
    Returns:
        配置实例
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = GameConfig(config_path)
    return _config_instance

