"""Scene manager - handles scene registration, switching, and lifecycle"""

from typing import Optional, Dict, Any, TYPE_CHECKING
import pygame

if TYPE_CHECKING:
    from .base_scene import BaseScene


class SceneManager:
    """
    Scene manager - manages all game scenes.

    Features:
    - Singleton pattern: single global instance
    - Registration: all scenes registered via manager
    - Lifecycle management: automatic create, update, render, destroy
    - Scene switching: supports data passing between scenes
    """

    _instance: Optional['SceneManager'] = None

    def __new__(cls, screen: Optional[pygame.Surface] = None, clock: Optional[pygame.time.Clock] = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, screen: Optional[pygame.Surface] = None, clock: Optional[pygame.time.Clock] = None):
        if hasattr(self, '_initialized'):
            return
        self.screen = screen
        self.clock = clock
        self.scenes: Dict[str, 'BaseScene'] = {}
        self.current_scene: Optional['BaseScene'] = None
        self.current_scene_key: Optional[str] = None
        self.scene_history: list[str] = []
        self._initialized = True

    def set_screen_and_clock(self, screen: pygame.Surface, clock: pygame.time.Clock):
        """Set screen and clock (for delayed initialization)."""
        self.screen = screen
        self.clock = clock

    def register_scene(self, scene: 'BaseScene'):
        """Register a scene."""
        if scene.scene_key in self.scenes:
            raise ValueError(f"Scene '{scene.scene_key}' already registered")
        self.scenes[scene.scene_key] = scene
        print(f"[SceneManager] Registered scene: {scene.scene_key}")

    def register_scenes(self, scenes: list):
        """Register multiple scenes."""
        for scene in scenes:
            self.register_scene(scene)

    def get_scene(self, scene_key: str) -> Optional['BaseScene']:
        """Get scene instance by key."""
        return self.scenes.get(scene_key)

    def has_scene(self, scene_key: str) -> bool:
        """Check if scene is registered."""
        return scene_key in self.scenes

    def get_current_scene(self) -> Optional['BaseScene']:
        """Get current scene."""
        return self.current_scene

    def get_current_scene_key(self) -> Optional[str]:
        """Get current scene key."""
        return self.current_scene_key

    def start_scene(self, scene_key: str, data: Optional[Dict[str, Any]] = None):
        """Start a scene."""
        if scene_key not in self.scenes:
            raise ValueError(f"Scene '{scene_key}' not registered. Available: {list(self.scenes.keys())}")
        if not self.screen or not self.clock:
            raise RuntimeError("SceneManager not initialized with screen and clock")

        old_scene_key = self.current_scene_key

        # Stop current scene
        if self.current_scene:
            print(f"[SceneManager] Stopping scene: {old_scene_key}")
            self.current_scene.destroy()

        # Start new scene
        self.current_scene = self.scenes[scene_key]
        self.current_scene_key = scene_key

        # Record history
        if old_scene_key:
            self.scene_history.append(old_scene_key)
            if len(self.scene_history) > 10:
                self.scene_history.pop(0)

        print(f"[SceneManager] Starting scene: {scene_key}")
        self.current_scene.init(self.screen, self.clock)

        if data and hasattr(self.current_scene, 'set_data'):
            self.current_scene.set_data(data)

    def stop_scene(self, scene_key: str):
        """Stop a scene."""
        if self.current_scene_key == scene_key and self.current_scene:
            print(f"[SceneManager] Stopping scene: {scene_key}")
            self.current_scene.destroy()
            self.current_scene = None
            self.current_scene_key = None

    def restart_current_scene(self, data: Optional[Dict[str, Any]] = None):
        """Restart current scene."""
        if self.current_scene_key:
            self.start_scene(self.current_scene_key, data)

    def go_back(self):
        """Go back to previous scene."""
        if self.scene_history:
            previous_scene = self.scene_history.pop()
            self.start_scene(previous_scene)
        else:
            print("[SceneManager] No scene to go back to")

    def update(self, delta_time: int):
        """Update current scene."""
        if self.current_scene:
            self.current_scene.update(delta_time)

    def handle_event(self, event: pygame.event.Event):
        """Handle event."""
        if self.current_scene:
            self.current_scene.handle_event(event)

    def render(self):
        """Render current scene."""
        if self.current_scene:
            self.current_scene.render()
        elif self.screen:
            self.screen.fill((0, 0, 0))

    def get_all_scene_keys(self) -> list:
        """Get all registered scene keys."""
        return list(self.scenes.keys())

    def clear_all_scenes(self):
        """Clear all scenes."""
        if self.current_scene:
            self.current_scene.destroy()
        for scene in self.scenes.values():
            scene.destroy()
        self.scenes.clear()
        self.current_scene = None
        self.current_scene_key = None
        self.scene_history.clear()
        print("[SceneManager] Cleared all scenes")

    def __repr__(self) -> str:
        return f"SceneManager(current={self.current_scene_key}, registered={list(self.scenes.keys())})"
