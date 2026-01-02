"""
旗帜类定义
定义旗帜相关的数据结构和操作
"""

from typing import Optional, Dict, TYPE_CHECKING
from .enums import Team
from .position import Position

if TYPE_CHECKING:
    from .player import Player


class Flag:
    """旗帜类"""
    
    def __init__(self, flag_id: str, team: Team, position: Position):
        """
        初始化旗帜
        Args:
            flag_id: 旗帜ID
            team: 所属队伍（归属队伍）
            position: 初始位置
        """
        if not flag_id:
            raise ValueError("Flag ID cannot be empty")
        if not isinstance(position, Position):
            raise TypeError(f"Position must be Position object, got {type(position)}")
        if not isinstance(team, Team):
            raise TypeError(f"Team must be Team enum, got {type(team)}")
        
        self.flag_id = flag_id
        self.team = team  # 所属队伍
        self.belongs_to = team  # 🚨 归属属性：明确标识旗帜归属哪个队伍（与team保持一致）
        self._original_belongs_to = team  # 🚨 保存原始归属，用于验证（防止更新时被错误修改）
        self.original_position = position
        self.position = position
        self.carried_by: Optional['Player'] = None
        self.is_picked_up = False
        self.is_scored = False
        
        # 🚨 验证：确保归属属性正确设置
        if self.team != self.belongs_to:
            raise ValueError(f"旗帜 {flag_id} 的 team 和 belongs_to 不一致！team={team.value}, belongs_to={self.belongs_to.value}")
    
    def belongs_to_team(self, team: Team) -> bool:
        """
        检查旗帜是否属于指定队伍
        Args:
            team: 要检查的队伍
        Returns:
            如果旗帜属于该队伍返回True
        """
        return self.belongs_to == team
    
    def is_enemy_flag_for(self, team: Team) -> bool:
        """
        检查旗帜是否是指定队伍的敌方旗帜
        Args:
            team: 要检查的队伍
        Returns:
            如果旗帜是敌方旗帜返回True
        """
        return self.belongs_to != team
    
    def is_my_flag_for(self, team: Team) -> bool:
        """
        检查旗帜是否是指定队伍的己方旗帜
        Args:
            team: 要检查的队伍
        Returns:
            如果旗帜是己方旗帜返回True
        """
        return self.belongs_to == team
    
    @property
    def can_pickup(self) -> bool:
        """是否可以拾取"""
        return not self.is_picked_up and not self.is_scored
    
    def pick_up_by(self, player: 'Player'):
        """被玩家拾取"""
        if self.can_pickup:
            self.is_picked_up = True
            self.carried_by = player
    
    def drop(self):
        """被放下（使用携带者的当前位置）"""
        self.is_picked_up = False
        self.carried_by = None
        # 注意：position 保持不变，因为旗帜位置应该跟随携带者位置
    
    def drop_at(self, position: Position):
        """在指定位置放下旗帜"""
        self.is_picked_up = False
        self.carried_by = None
        self.position = position  # 🚨 设置旗帜位置为指定位置
    
    def score(self):
        """得分"""
        self.is_scored = True
        self.is_picked_up = False
        self.carried_by = None
        self.position = self.original_position
    
    def reset(self):
        """重置旗帜"""
        self.is_picked_up = False
        self.is_scored = False
        self.carried_by = None
        self.position = self.original_position
    
    def update_from_dict(self, f_data: Dict) -> None:
        """
        从字典更新旗帜状态 - 面向对象设计，旗帜自己处理状态更新
        
        注意：此方法只更新位置和状态，绝不改变旗帜的归属（belongs_to）！
        
        Args:
            f_data: 旗帜数据字典，包含 posX, posY, canPickup
        """
        from .position import Position
        
        flag_pos = Position(f_data["posX"], f_data["posY"])
        can_pickup = f_data.get("canPickup", True)
        
        # 只更新位置和状态，不改变归属
        old_position = self.position
        self.is_picked_up = not can_pickup
        self.position = flag_pos
        
        # 验证归属没有被意外改变（防御性检查）
        if hasattr(self, '_original_belongs_to'):
            if self.belongs_to != self._original_belongs_to:
                raise ValueError(
                    f"旗帜归属被意外改变！旗帜ID: {self.flag_id}, "
                    f"原始归属: {self._original_belongs_to.value}队, "
                    f"当前归属: {self.belongs_to.value}队"
                )
        
        if old_position != flag_pos:
            print(f"🔄 [Flag.{self.flag_id}] 更新状态: 归属={self.belongs_to.value}队, 位置: {old_position} -> {flag_pos}, 可拾取={can_pickup}", flush=True)
        else:
            print(f"🔄 [Flag.{self.flag_id}] 更新状态: 归属={self.belongs_to.value}队, 位置={flag_pos}, 可拾取={can_pickup}", flush=True)
    
    def to_dict(self) -> Dict:
        """转换为字典（用于API）"""
        return {
            "posX": self.position.x,
            "posY": self.position.y,
            "team": self.team.value,
            "belongsTo": self.belongs_to.value,  # 🚨 归属属性
            "canPickup": self.can_pickup,
            "pickedUp": self.is_picked_up
        }
    
    def __repr__(self) -> str:
        """字符串表示"""
        return f"Flag(id={self.flag_id}, belongs_to={self.belongs_to.value}, position={self.position}, picked_up={self.is_picked_up}, scored={self.is_scored})"

