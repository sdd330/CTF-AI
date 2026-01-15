"""
碰撞回调接口
"""

from typing import Optional, Callable
from ...utils import Team
from ...objects.flag import Flag


class CollisionCallbacks:
    """碰撞回调接口"""

    def __init__(self):
        self.on_score_update: Optional[Callable[[Team], None]] = None
        self.on_create_flag: Optional[Callable[[int, int, Team, bool], Flag]] = None
