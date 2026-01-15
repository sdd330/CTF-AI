"""Base scene class"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, TYPE_CHECKING
import pygame

if TYPE_CHECKING:
    from .scene_manager import SceneManager


class BaseScene(ABC):
    """
    Base scene class.

    Each scene has the following lifecycle methods:
    - preload(): Preload resources (optional)
    - create(): Create scene objects
    - update(): Update scene (called each frame)
    - destroy(): Destroy scene (cleanup resources)
    """

    def __init__(self, scene_key: str, scene_manager: 'SceneManager'):
        """
        Initialize scene.

        Args:
            scene_key: Unique scene identifier
            scene_manager: Scene manager
        """
        self.scene_key = scene_key
        self.scene_manager = scene_manager
        self.screen: Optional[pygame.Surface] = None
        self.clock: Optional[pygame.time.Clock] = None
        self._initialized = False

    def init(self, screen: pygame.Surface, clock: pygame.time.Clock):
        """
        Initialize scene (called by scene manager).

        Args:
            screen: pygame Surface object
            clock: pygame Clock object
        """
        self.screen = screen
        self.clock = clock
        if not self._initialized:
            self.preload()
            self.create()
            self._initialized = True

    def preload(self):
        """Preload resources. Subclasses can override."""
        pass

    @abstractmethod
    def create(self):
        """Create scene objects. Subclasses must implement."""
        pass

    def update(self, delta_time: int):
        """
        Update scene.

        Args:
            delta_time: Time delta (milliseconds)
        """
        pass

    def handle_event(self, event: pygame.event.Event):
        """
        Handle event.

        Args:
            event: pygame event
        """
        pass

    def render(self):
        """Render scene. Subclasses can override."""
        pass

    def destroy(self):
        """Destroy scene. Subclasses can override."""
        self._initialized = False

    def start_scene(self, scene_key: str, data: Optional[Dict[str, Any]] = None):
        """
        Start another scene.

        Args:
            scene_key: Scene identifier to start
            data: Data to pass to scene
        """
        self.scene_manager.start_scene(scene_key, data)

    def stop(self):
        """Stop current scene."""
        self.scene_manager.stop_scene(self.scene_key)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(key={self.scene_key})"


# Re-export SceneManager for backward compatibility
from .scene_manager import SceneManager

__all__ = ['BaseScene', 'SceneManager']
