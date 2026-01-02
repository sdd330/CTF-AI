"""
玩家动作执行类
负责执行玩家的各种动作
"""

from typing import Optional, TYPE_CHECKING
from ..enums import Action, Team
from ..position import Position
from ...utils import can_tag_enemy, can_rescue_teammate, can_pickup_flag, can_score_flag

if TYPE_CHECKING:
    from .player import Player
    from .flag import Flag


class PlayerActions:
    """玩家动作执行器 - 负责执行玩家的各种动作"""
    
    def __init__(self, player: 'Player'):
        self.player = player
    
    def execute_pickup_flag(self, flag: 'Flag') -> bool:
        """执行拾取旗帜动作"""
        if not flag:
            print(f"❌ [Player.{self.player.name}] PICKUP_FLAG动作缺少flag参数", flush=True)
            return False
        if not can_pickup_flag(self.player, flag):
            return False
        
        if self.player._state_manager.is_free and not self.player._state_manager.has_flag:
            self.player.carried_flag = flag
            self.player._state_manager.set_carrying_flag_state()
            flag.pick_up_by(self.player)
            print(f"✅ [Player.{self.player.name}] 成功拾取旗帜 {flag.flag_id}", flush=True)
            return True
        return False
    
    def execute_drop_flag(self, drop_position: Optional[Position] = None) -> bool:
        """执行放下旗帜动作"""
        if not self.player._state_manager.has_flag:
            return False
        
        flag = self.player.carried_flag
        self.player.carried_flag = None
        self.player._state_manager.set_free_state()
        
        if flag:
            drop_pos = drop_position if drop_position is not None else self.player.position
            flag.drop_at(drop_pos)
            print(f"✅ [Player.{self.player.name}] 成功放下旗帜 {flag.flag_id}", flush=True)
            return True
        return False
    
    def execute_score_flag(self) -> bool:
        """执行得分动作"""
        if not can_score_flag(self.player):
            return False
        if not self.player.carried_flag:
            print(f"❌ [Player.{self.player.name}] SCORE_FLAG动作失败：未持有旗帜", flush=True)
            return False
        
        flag = self.player.carried_flag
        flag.score()
        self.player.carried_flag = None
        self.player._state_manager.set_free_state()
        
        # 更新游戏得分
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
        """执行标记敌人动作"""
        if not target:
            print(f"❌ [Player.{self.player.name}] TAG_ENEMY动作缺少target参数", flush=True)
            return False
        if not can_tag_enemy(self.player, target, self.player.world):
            return False
        
        # 计算监狱位置：被抓捕的敌方玩家应该被送到抓捕方的监狱
        tagger_team = self.player.team
        tagger_prison_area = self.player.world.get_team_prison_area(tagger_team)
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
        """执行营救队友动作"""
        if not teammate:
            print(f"❌ [Player.{self.player.name}] RESCUE_TEAMMATE动作缺少teammate参数", flush=True)
            return False
        if not can_rescue_teammate(self.player, teammate, self.player.world):
            return False
        
        teammate._prison_manager.rescue()
        print(f"✅ [Player.{self.player.name}] 成功营救队友 {teammate.name}", flush=True)
        return True
