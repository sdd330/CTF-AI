from typing import Optional, TYPE_CHECKING
from ..enums import Action, Team
from ..position import Position
from ...utils import can_tag_enemy, can_rescue_teammate, can_pickup_flag, can_score_flag

if TYPE_CHECKING:
    from .player import Player
    from .flag import Flag


class PlayerActions:
    def __init__(self, player: 'Player'):
        self.player = player
    
    def execute_pickup_flag(self, flag: 'Flag') -> bool:
        if not flag:
            print(f"❌ [Player.{self.player.name}] PICKUP_FLAG动作缺少flag参数", flush=True)
            return False
        if not can_pickup_flag(self.player, flag):
            return False
        
        if self.player._state_manager.is_free and not self.player._state_manager.has_flag:
            flag.pick_up_by(self.player)
            return True
        return False
    
    def execute_drop_flag(self, drop_position: Optional[Position] = None) -> bool:
        flag = self.player._flag_manager._get_carried_flag()
        if not flag:
            return False
        
        drop_pos = drop_position if drop_position is not None else self.player.position
        flag.drop_at(drop_pos)
        return True
    
    def execute_score_flag(self) -> bool:
        if not can_score_flag(self.player):
            return False
        
        flag = self.player._flag_manager._get_carried_flag()
        if not flag:
            print(f"❌ [Player.{self.player.name}] SCORE_FLAG动作失败：未持有旗帜", flush=True)
            return False
        
        flag.score()
        
        if self.player.team == Team.LEFT:
            self.player.world.left_team_score += 1
        else:
            self.player.world.right_team_score += 1
        
        print(
            f"🎉 [Player.{self.player.name}] 成功得分！"
            f"当前得分: L={self.player.world.left_team_score}, R={self.player.world.right_team_score}",
            flush=True
        )
        return True
    
    def execute_tag_enemy(self, target: 'Player') -> bool:
        if not target:
            print(f"❌ [Player.{self.player.name}] TAG_ENEMY动作缺少target参数", flush=True)
            return False
        if not can_tag_enemy(self.player, target, self.player.world):
            return False
        
        tagger_team = self.player.team
        tagger_prison_area = self.player.world.map.get_team_prison_area(tagger_team)
        if not tagger_prison_area or not tagger_prison_area.positions:
            print(f"❌ [Player.{self.player.name}] TAG_ENEMY动作失败：找不到己方监狱位置", flush=True)
            return False
        
        prison_pos = next(iter(tagger_prison_area.positions))
        target._prison_manager.send_to_prison(prison_pos)
        print(
            f"✅ [Player.{self.player.name}] 成功标记敌人 {target.name}，"
            f"将其送入{self.player.team.value}队监狱 {prison_pos}",
            flush=True
        )
        return True
    
    def execute_rescue_teammate(self, teammate: 'Player') -> bool:
        if not teammate:
            print(f"❌ [Player.{self.player.name}] RESCUE_TEAMMATE动作缺少teammate参数", flush=True)
            return False
        if not can_rescue_teammate(self.player, teammate, self.player.world):
            return False
        
        teammate._prison_manager.rescue()
        return True
