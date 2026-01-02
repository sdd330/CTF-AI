"""
区域类定义
定义目标区域和监狱区域
"""

from typing import Set, Optional
from .enums import Team
from .position import Position


class TargetArea:
    """基地（目标区域）类 - 面向对象设计"""
    
    def __init__(self, team: Team, positions: Set[Position]):
        """
        初始化基地
        Args:
            team: 所属队伍（必须是 Team.LEFT 或 Team.RIGHT）
            positions: 基地位置集合
        """
        if not isinstance(team, Team):
            raise TypeError(f"Team must be Team enum, got {type(team)}")
        if team not in (Team.LEFT, Team.RIGHT):
            raise ValueError(f"Team must be Team.LEFT or Team.RIGHT, got {team}")
        if not isinstance(positions, set):
            raise TypeError(f"Positions must be a set, got {type(positions)}")
        
        self.team = team  # 所属队伍
        self.belongs_to = team  # 🚨 归属属性：明确标识基地归属哪个队伍
        self.positions: Set[Position] = positions.copy()  # 基地位置集合
        
        # 🚨 验证：确保归属属性正确设置
        if self.team != self.belongs_to:
            raise ValueError(f"基地的 team 和 belongs_to 不一致！team={team.value}, belongs_to={self.belongs_to.value}")
    
    def belongs_to_team(self, team: Team) -> bool:
        """
        检查基地是否属于指定队伍
        Args:
            team: 要检查的队伍
        Returns:
            如果基地属于该队伍返回True
        """
        return self.belongs_to == team
    
    def contains(self, position: Position) -> bool:
        """
        检查位置是否在基地内
        Args:
            position: 要检查的位置
        Returns:
            如果位置在基地内返回True
        """
        return position in self.positions
    
    def add_position(self, position: Position):
        """添加位置到基地"""
        self.positions.add(position)
    
    def remove_position(self, position: Position):
        """从基地移除位置"""
        self.positions.discard(position)
    
    def __len__(self) -> int:
        """返回基地位置数量"""
        return len(self.positions)
    
    def __iter__(self):
        """迭代基地位置"""
        return iter(self.positions)
    
    def __repr__(self) -> str:
        """字符串表示"""
        return f"TargetArea(belongs_to={self.belongs_to.value}, positions={len(self.positions)})"


class PrisonArea:
    """监狱类 - 面向对象设计"""
    
    def __init__(self, team: Team, positions: Set[Position]):
        """
        初始化监狱
        Args:
            team: 所属队伍（必须是 Team.LEFT 或 Team.RIGHT）
            positions: 监狱位置集合
        """
        if not isinstance(team, Team):
            raise TypeError(f"Team must be Team enum, got {type(team)}")
        if team not in (Team.LEFT, Team.RIGHT):
            raise ValueError(f"Team must be Team.LEFT or Team.RIGHT, got {team}")
        if not isinstance(positions, set):
            raise TypeError(f"Positions must be a set, got {type(positions)}")
        
        self.team = team  # 所属队伍
        self.belongs_to = team  # 🚨 归属属性：明确标识监狱归属哪个队伍
        self.positions: Set[Position] = positions.copy()  # 监狱位置集合
        
        # 🚨 验证：确保归属属性正确设置
        if self.team != self.belongs_to:
            raise ValueError(f"监狱的 team 和 belongs_to 不一致！team={team.value}, belongs_to={self.belongs_to.value}")
    
    def belongs_to_team(self, team: Team) -> bool:
        """
        检查监狱是否属于指定队伍
        Args:
            team: 要检查的队伍
        Returns:
            如果监狱属于该队伍返回True
        """
        return self.belongs_to == team
    
    def contains(self, position: Position) -> bool:
        """
        检查位置是否在监狱内
        Args:
            position: 要检查的位置
        Returns:
            如果位置在监狱内返回True
        """
        return position in self.positions
    
    def add_position(self, position: Position):
        """添加位置到监狱"""
        self.positions.add(position)
    
    def remove_position(self, position: Position):
        """从监狱移除位置"""
        self.positions.discard(position)
    
    def get_available_position(self, occupied_positions: Set[Position]) -> Optional[Position]:
        """
        获取可用的监狱位置（未被占用的）
        Args:
            occupied_positions: 已被占用的位置集合
        Returns:
            可用的位置，如果没有则返回None
        """
        for pos in self.positions:
            if pos not in occupied_positions:
                return pos
        return None
    
    def __len__(self) -> int:
        """返回监狱位置数量"""
        return len(self.positions)
    
    def __iter__(self):
        """迭代监狱位置"""
        return iter(self.positions)
    
    def __repr__(self) -> str:
        """字符串表示"""
        return f"PrisonArea(belongs_to={self.belongs_to.value}, positions={len(self.positions)})"

