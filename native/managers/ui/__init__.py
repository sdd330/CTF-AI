"""
UI module - UI components and manager
"""

from .base import UIComponent, UIComponentType, TEXT_OUTLINE_OFFSETS
from .score_text import ScoreTextComponent
from .tutorial_text import TutorialTextComponent
from .game_over_text import GameOverTextComponent
from .team_name_text import TeamNameTextComponent
from .manager import UIManager, UIComponentFactory

__all__ = [
    'UIComponent',
    'UIComponentType',
    'TEXT_OUTLINE_OFFSETS',
    'ScoreTextComponent',
    'TutorialTextComponent',
    'GameOverTextComponent',
    'TeamNameTextComponent',
    'UIManager',
    'UIComponentFactory',
]
