"""
玩家状态管理类
负责管理玩家的状态和属性
"""

from typing import Optional, TYPE_CHECKING
from ..enums import Team, PlayerState
from ..position import Position
from ..areas import TargetArea

if TYPE_CHECKING:
    from .player import Player


class PlayerStateManager:
    """玩家状态管理器 - 负责管理玩家的状态和属性"""
    
    def __init__(self, player: 'Player'):
        self.player = player
    
    @property
    def is_free(self) -> bool:
        """是否自由（不在监狱中）"""
        return self.player.state != PlayerState.IN_PRISON
    
    @property
    def is_in_prison(self) -> bool:
        """是否在监狱"""
        return self.player.state == PlayerState.IN_PRISON
    
    @property
    def has_flag(self) -> bool:
        """是否持有旗帜（单一数据源：carried_flag）"""
        return self.player.carried_flag is not None
    
    def set_prison_state(self, prison_position: Position) -> None:
        """设置监狱状态"""
        self.player.state = PlayerState.IN_PRISON
        self.player.position = prison_position
        self.player.prison_time_left = self.player.prison_duration
    
    def set_free_state(self) -> None:
        """设置自由状态"""
        self.player.state = PlayerState.FREE
        self.player.prison_time_left = 0
    
    def set_carrying_flag_state(self) -> None:
        """设置携带旗帜状态"""
        self.player.state = PlayerState.CARRYING_FLAG
    
    def update_prison_time(self, delta_time: int) -> None:
        """更新监狱时间"""
        if self.is_in_prison:
            self.player.prison_time_left = max(0, self.player.prison_time_left - delta_time)
            if self.player.prison_time_left == 0:
                self.set_free_state()
    
    def set_base_area(self, base_area: TargetArea) -> None:
        """设置己方基地区域"""
        if base_area and not base_area.belongs_to_team(self.player.team):
            raise ValueError(
                f"玩家 {self.player.name} ({self.player.team.value}队) "
                f"不能设置 {base_area.belongs_to.value}队的基地"
            )
        self.player.base_area = base_area
    
    def is_in_base(self) -> bool:
        """检查玩家是否在己方基地内"""
        if not self.player.base_area:
            return False
        return self.player.base_area.contains(self.player.position)
