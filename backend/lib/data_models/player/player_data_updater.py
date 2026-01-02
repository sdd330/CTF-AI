"""
玩家数据更新类
负责从字典更新玩家状态
"""

from typing import Dict, TYPE_CHECKING
from ..enums import Team
from ..position import Position

if TYPE_CHECKING:
    from .player import Player
    from ..flag import Flag


class PlayerDataUpdater:
    """玩家数据更新器 - 负责从字典更新玩家状态"""
    
    def __init__(self, player: 'Player'):
        self.player = player
    
    def update_from_dict(self, p_data: Dict, flags: Dict[str, 'Flag']) -> None:
        """
        从字典更新玩家状态
        
        Args:
            p_data: 玩家数据字典（包含 posX, posY, hasFlag, inPrison 等）
            flags: 旗帜字典（用于关联旗帜）
        """
        # 首先正确设置 team（必须在最开始就设置，避免后续判断逻辑出错）
        self._validate_and_set_team(p_data)
        
        # 然后确保基地信息被正确设置（必须在最开始就设置，确保后续逻辑都能使用）
        self._ensure_base_area()
        
        # 更新位置
        self._update_position(p_data)
        
        # 更新监狱状态
        self._update_prison_state(p_data)
        
        # 更新旗帜状态
        self._update_flag_state(p_data, flags)
    
    def _validate_and_set_team(self, p_data: Dict) -> None:
        """
        验证并设置 team - 严格确保团队归属正确
        
        注意：如果 team 不匹配，这是严重错误，不应该静默修改，应该抛出异常
        """
        if "team" not in p_data:
            raise ValueError(f"玩家数据字典缺少必需的 'team' 字段: {p_data}")
        
        team_str = p_data.get("team", "")
        if not team_str:
            raise ValueError(f"玩家数据字典中 'team' 字段为空: {p_data}")
        
        expected_team = Team.from_name(team_str)
        if not expected_team:
            raise ValueError(f"无效的队伍名称: {team_str}, 玩家数据: {p_data}")
        
        # 🚨 严格验证：如果当前 team 与期望的 team 不匹配，这是严重错误
        if self.player.team != expected_team:
            raise ValueError(
                f"玩家 {self.player.name} 团队归属不匹配！"
                f"当前团队: {self.player.team.value}, 期望团队: {expected_team.value}. "
                f"这不应该在 update_from_dict 中发生，应该在更新前就处理！"
            )
        
        # 如果匹配，确保一致性（即使相同也设置，确保一致性）
        self.player.team = expected_team
    
    def _ensure_base_area(self) -> None:
        """
        确保基地信息被正确设置 - 基于当前 team
        
        注意：必须在 _validate_and_set_team 之后调用，确保 team 正确
        """
        base_area = self.player.world.get_team_target_area(self.player.team)
        if base_area:
            # 验证 base_area 是否属于当前 team（防御性检查）
            if not base_area.belongs_to_team(self.player.team):
                raise ValueError(
                    f"玩家 {self.player.name} ({self.player.team.value}队) "
                    f"的基地区域属于 {base_area.belongs_to.value}队，不匹配！"
                )
            self.player._state_manager.set_base_area(base_area)
    
    def _update_position(self, p_data: Dict) -> None:
        """更新位置"""
        if "posX" in p_data and "posY" in p_data:
            self.player.position = Position(p_data["posX"], p_data["posY"])
    
    def _update_prison_state(self, p_data: Dict) -> None:
        """更新监狱状态"""
        if p_data.get("inPrison", False):
            # 如果玩家在监狱，确保状态正确
            if not self.player._state_manager.is_in_prison:
                # 确定监狱位置（敌方监狱）
                enemy_team = self.player.team.get_enemy()
                prison_area = self.player.world.get_team_prison_area(enemy_team)
                if prison_area and prison_area.positions:
                    # 如果当前位置不在监狱，移动到监狱
                    if self.player.position not in prison_area.positions:
                        self.player.position = next(iter(prison_area.positions))
                    self.player._prison_manager.send_to_prison(self.player.position)
        else:
            # 如果不在监狱，确保状态正确
            if self.player._state_manager.is_in_prison:
                self.player._prison_manager.rescue()
    
    def _update_flag_state(self, p_data: Dict, flags: Dict[str, 'Flag']) -> None:
        """更新旗帜状态"""
        if p_data.get("hasFlag", False):
            # 如果有旗帜，尝试关联旗帜
            if not self.player._state_manager.has_flag:
                self.player._flag_manager.associate_flag_from_dict(flags)
        else:
            # 如果没有旗帜，确保放下旗帜
            if self.player._state_manager.has_flag:
                self.player._flag_manager.drop_flag()
