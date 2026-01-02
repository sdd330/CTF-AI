"""
玩家旗帜管理类
负责管理玩家与旗帜的交互
"""

from typing import Optional, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from .player import Player
    from ..flag import Flag


class PlayerFlagManager:
    """玩家旗帜管理器 - 负责管理玩家与旗帜的交互"""
    
    def __init__(self, player: 'Player'):
        self.player = player
    
    def pick_up_flag(self, flag: 'Flag') -> None:
        """拾取旗帜"""
        if self.player._state_manager.is_free and not self.player._state_manager.has_flag:
            self.player.carried_flag = flag
            self.player._state_manager.set_carrying_flag_state()
            flag.pick_up_by(self.player)
            print(f"✅ [Player.{self.player.name}] 已拾取旗帜 {flag.flag_id}", flush=True)
    
    def drop_flag(self, drop_position: Optional['Position'] = None) -> Optional['Flag']:
        """放下旗帜"""
        if self.player._state_manager.has_flag:
            flag = self.player.carried_flag
            self.player.carried_flag = None
            self.player._state_manager.set_free_state()
            if flag:
                from ..position import Position
                drop_pos = drop_position if drop_position is not None else self.player.position
                flag.drop_at(drop_pos)
            return flag
        return None
    
    def associate_flag_from_dict(self, flags: Dict[str, 'Flag']) -> bool:
        """从旗帜字典关联旗帜对象"""
        if self.player.carried_flag:
            return True
        
        for flag in flags.values():
            if flag.is_enemy_flag_for(self.player.team) and (not flag.can_pickup or flag.is_picked_up):
                self.player.carried_flag = flag
                self.player._state_manager.set_carrying_flag_state()
                print(
                    f"✅ [Player.{self.player.name}] 关联旗帜 {flag.flag_id} "
                    f"(归属: {flag.belongs_to.value}队)",
                    flush=True
                )
                return True
        
        return False
