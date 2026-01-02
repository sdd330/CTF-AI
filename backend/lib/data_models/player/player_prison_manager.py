"""
玩家监狱管理类
负责管理玩家的监狱相关操作
"""

from typing import TYPE_CHECKING
from ..enums import PlayerState
from ..position import Position

if TYPE_CHECKING:
    from .player import Player


class PlayerPrisonManager:
    """玩家监狱管理器 - 负责管理玩家的监狱相关操作"""
    
    def __init__(self, player: 'Player'):
        self.player = player
    
    def send_to_prison(self, prison_position: Position) -> None:
        """送入监狱"""
        if self.player._state_manager.has_flag:
            caught_position = self.player.position
            self.player._flag_manager.drop_flag(drop_position=caught_position)
            print(
                f"🚩 [Player.{self.player.name}] 被抓，"
                f"旗帜保留在被抓位置: {caught_position}",
                flush=True
            )
        
        self.player._state_manager.set_prison_state(prison_position)
        
        # 记录被捕获行为（表现）
        self.player._behavior.record_capture()
    
    def rescue(self) -> None:
        """被救援"""
        if self.player._state_manager.is_in_prison:
            self.player._state_manager.set_free_state()
