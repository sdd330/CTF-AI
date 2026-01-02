"""
音效管理器
设计模式：单例模式

职责：
- 管理游戏音效和背景音乐
- 提供音量控制
- 支持音效资源管理
"""

import pygame
from pathlib import Path
from typing import Optional, Dict
from enum import Enum


class SoundType(Enum):
    """音效类型"""
    SFX = 'sfx'       # 音效
    MUSIC = 'music'   # 背景音乐


class AudioManager:
    """
    音效管理器
    使用单例模式确保全局唯一实例
    """

    _instance: Optional['AudioManager'] = None

    # 资源目录
    AUDIO_DIR = Path(__file__).parent.parent / "assets" / "audio"

    # 预定义音效
    SOUND_PATHS = {
        # 游戏音效
        'flag_pickup': 'flag_pickup.wav',
        'flag_score': 'flag_score.wav',
        'player_tagged': 'player_tagged.wav',
        'player_rescued': 'player_rescued.wav',
        'game_start': 'game_start.wav',
        'game_over': 'game_over.wav',
        # 背景音乐
        'bgm_menu': 'bgm_menu.mp3',
        'bgm_game': 'bgm_game.mp3',
    }

    def __new__(cls) -> 'AudioManager':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # 检查 pygame.mixer 是否可用
        self._mixer_available = False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self._mixer_available = True
        except Exception as e:
            print(f"[AudioManager] 音频系统初始化失败: {e}")

        # 音效缓存
        self._sound_cache: Dict[str, pygame.mixer.Sound] = {}

        # 音量设置
        self._sfx_volume: float = 1.0
        self._music_volume: float = 0.5

        # 静音状态
        self._sfx_muted: bool = False
        self._music_muted: bool = False

        # 当前播放的背景音乐
        self._current_music: Optional[str] = None

        self._initialized = True

    @classmethod
    def get_instance(cls) -> 'AudioManager':
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """重置单例实例（用于测试）"""
        if cls._instance is not None:
            cls._instance.stop_all()
        cls._instance = None

    def is_available(self) -> bool:
        """检查音频系统是否可用"""
        return self._mixer_available

    # ========== 音效加载 ==========

    def load_sound(self, key: str, path: Optional[str] = None) -> Optional[pygame.mixer.Sound]:
        """
        加载音效

        Args:
            key: 音效键名
            path: 自定义路径（可选）

        Returns:
            pygame.mixer.Sound 或 None
        """
        if not self._mixer_available:
            return None

        # 检查缓存
        if key in self._sound_cache:
            return self._sound_cache[key]

        # 获取路径
        if path:
            sound_path = Path(path)
        elif key in self.SOUND_PATHS:
            sound_path = self.AUDIO_DIR / self.SOUND_PATHS[key]
        else:
            sound_path = self.AUDIO_DIR / key

        try:
            if not sound_path.exists():
                # 音效文件不存在，静默返回 None（不打印警告）
                return None

            sound = pygame.mixer.Sound(str(sound_path))
            self._sound_cache[key] = sound
            return sound

        except Exception as e:
            print(f"[AudioManager] 加载音效失败 {key}: {e}")
            return None

    def get_sound(self, key: str) -> Optional[pygame.mixer.Sound]:
        """获取已加载的音效"""
        return self._sound_cache.get(key)

    # ========== 音效播放 ==========

    def play_sound(self, key: str, loops: int = 0, volume: Optional[float] = None) -> bool:
        """
        播放音效

        Args:
            key: 音效键名
            loops: 循环次数（0 = 不循环，-1 = 无限循环）
            volume: 音量覆盖（可选）

        Returns:
            是否成功播放
        """
        if not self._mixer_available or self._sfx_muted:
            return False

        sound = self.get_sound(key) or self.load_sound(key)
        if not sound:
            return False

        try:
            # 设置音量
            actual_volume = volume if volume is not None else self._sfx_volume
            sound.set_volume(actual_volume)

            # 播放
            sound.play(loops=loops)
            return True

        except Exception as e:
            print(f"[AudioManager] 播放音效失败 {key}: {e}")
            return False

    def stop_sound(self, key: str) -> None:
        """停止指定音效"""
        sound = self.get_sound(key)
        if sound:
            sound.stop()

    # ========== 背景音乐 ==========

    def play_music(self, key: str, loops: int = -1, fade_ms: int = 0) -> bool:
        """
        播放背景音乐

        Args:
            key: 音乐键名
            loops: 循环次数（-1 = 无限循环）
            fade_ms: 淡入时间（毫秒）

        Returns:
            是否成功播放
        """
        if not self._mixer_available:
            return False

        # 获取路径
        if key in self.SOUND_PATHS:
            music_path = self.AUDIO_DIR / self.SOUND_PATHS[key]
        else:
            music_path = self.AUDIO_DIR / key

        try:
            if not music_path.exists():
                return False

            # 停止当前音乐
            pygame.mixer.music.stop()

            # 加载并播放新音乐
            pygame.mixer.music.load(str(music_path))
            pygame.mixer.music.set_volume(0 if self._music_muted else self._music_volume)

            if fade_ms > 0:
                pygame.mixer.music.play(loops=loops, fade_ms=fade_ms)
            else:
                pygame.mixer.music.play(loops=loops)

            self._current_music = key
            return True

        except Exception as e:
            print(f"[AudioManager] 播放音乐失败 {key}: {e}")
            return False

    def stop_music(self, fade_ms: int = 0) -> None:
        """
        停止背景音乐

        Args:
            fade_ms: 淡出时间（毫秒）
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

    def pause_music(self) -> None:
        """暂停背景音乐"""
        if self._mixer_available:
            pygame.mixer.music.pause()

    def resume_music(self) -> None:
        """恢复背景音乐"""
        if self._mixer_available:
            pygame.mixer.music.unpause()

    def is_music_playing(self) -> bool:
        """检查背景音乐是否正在播放"""
        if not self._mixer_available:
            return False
        return pygame.mixer.music.get_busy()

    def get_current_music(self) -> Optional[str]:
        """获取当前播放的背景音乐键名"""
        return self._current_music

    # ========== 音量控制 ==========

    def set_sfx_volume(self, volume: float) -> None:
        """
        设置音效音量

        Args:
            volume: 音量（0.0 - 1.0）
        """
        self._sfx_volume = max(0.0, min(1.0, volume))

    def get_sfx_volume(self) -> float:
        """获取音效音量"""
        return self._sfx_volume

    def set_music_volume(self, volume: float) -> None:
        """
        设置背景音乐音量

        Args:
            volume: 音量（0.0 - 1.0）
        """
        self._music_volume = max(0.0, min(1.0, volume))
        if self._mixer_available and not self._music_muted:
            pygame.mixer.music.set_volume(self._music_volume)

    def get_music_volume(self) -> float:
        """获取背景音乐音量"""
        return self._music_volume

    # ========== 静音控制 ==========

    def mute_sfx(self, muted: bool = True) -> None:
        """静音/取消静音音效"""
        self._sfx_muted = muted

    def mute_music(self, muted: bool = True) -> None:
        """静音/取消静音背景音乐"""
        self._music_muted = muted
        if self._mixer_available:
            pygame.mixer.music.set_volume(0 if muted else self._music_volume)

    def is_sfx_muted(self) -> bool:
        """检查音效是否静音"""
        return self._sfx_muted

    def is_music_muted(self) -> bool:
        """检查背景音乐是否静音"""
        return self._music_muted

    def toggle_sfx_mute(self) -> bool:
        """切换音效静音状态"""
        self._sfx_muted = not self._sfx_muted
        return self._sfx_muted

    def toggle_music_mute(self) -> bool:
        """切换背景音乐静音状态"""
        self.mute_music(not self._music_muted)
        return self._music_muted

    # ========== 资源管理 ==========

    def preload_sounds(self, keys: list = None) -> int:
        """
        预加载音效

        Args:
            keys: 要预加载的音效键名列表，默认加载所有预定义音效

        Returns:
            成功加载的数量
        """
        if keys is None:
            keys = [k for k in self.SOUND_PATHS.keys() if not k.startswith('bgm_')]

        loaded = 0
        for key in keys:
            if self.load_sound(key):
                loaded += 1
        return loaded

    def clear_cache(self) -> None:
        """清除音效缓存"""
        for sound in self._sound_cache.values():
            sound.stop()
        self._sound_cache.clear()

    def stop_all(self) -> None:
        """停止所有音效和音乐"""
        if not self._mixer_available:
            return

        # 停止所有音效
        pygame.mixer.stop()

        # 停止背景音乐
        pygame.mixer.music.stop()
        self._current_music = None

    # ========== 游戏事件音效便捷方法 ==========

    def play_flag_pickup(self) -> bool:
        """播放拾取旗帜音效"""
        return self.play_sound('flag_pickup')

    def play_flag_score(self) -> bool:
        """播放得分音效"""
        return self.play_sound('flag_score')

    def play_player_tagged(self) -> bool:
        """播放玩家被抓音效"""
        return self.play_sound('player_tagged')

    def play_player_rescued(self) -> bool:
        """播放玩家被救音效"""
        return self.play_sound('player_rescued')

    def play_game_start(self) -> bool:
        """播放游戏开始音效"""
        return self.play_sound('game_start')

    def play_game_over(self) -> bool:
        """播放游戏结束音效"""
        return self.play_sound('game_over')
