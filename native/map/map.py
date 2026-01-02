"""
游戏地图类
"""

from typing import List, Tuple
from ..utils import Team, TILE_SIZE


class Position:
    """位置类（简化版）"""
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
    
    def __eq__(self, other):
        if not isinstance(other, Position):
            return False
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def __repr__(self):
        return f"Position({self.x}, {self.y})"


class GameMap:
    """游戏地图类"""
    
    def __init__(self, width: int, height: int):
        """
        初始化地图
        
        Args:
            width: 地图宽度（格子数）
            height: 地图高度（格子数）
        """
        self.width = width
        self.height = height
        self.middle_line = width / 2.0
        self.walls: set[Position] = set()
        
        # 目标区域和监狱
        # 使用有序列表保持 create_3x3_grid 的顺序（用于渲染）
        # 同时使用集合用于快速查找（用于碰撞检测等）
        self.left_team_target_list: List[Position] = []  # 有序列表，保持顺序
        self.left_team_target_set: set[Position] = set()  # 无序集合，快速查找
        self.right_team_target_list: List[Position] = []
        self.right_team_target_set: set[Position] = set()
        self.left_team_prison_list: List[Position] = []
        self.left_team_prison_set: set[Position] = set()
        self.right_team_prison_list: List[Position] = []
        self.right_team_prison_set: set[Position] = set()
    
    def initialize(self, map_data: dict, 
                   left_target: List[Tuple[int, int]],
                   right_target: List[Tuple[int, int]],
                   left_prison: List[Tuple[int, int]],
                   right_prison: List[Tuple[int, int]]):
        """
        初始化地图数据
        
        Args:
            map_data: 地图数据字典（包含walls）
            left_target: L队目标区域列表
            right_target: R队目标区域列表
            left_prison: L队监狱列表
            right_prison: R队监狱列表
        """
        # 初始化墙壁
        walls = map_data.get("walls", [])
        obstacles = map_data.get("obstacles", [])
        
        # 处理墙壁（字典格式）
        wall_positions = []
        for w in walls:
            if isinstance(w, dict):
                wall_positions.append(Position(w["x"], w["y"]))
            elif isinstance(w, (tuple, list)) and len(w) >= 2:
                wall_positions.append(Position(w[0], w[1]))
        
        # 处理障碍物（可能是元组或字典格式）
        obstacle_positions = []
        for obs in obstacles:
            if isinstance(obs, dict):
                obstacle_positions.append(Position(obs["x"], obs["y"]))
            elif isinstance(obs, (tuple, list)) and len(obs) >= 2:
                obstacle_positions.append(Position(obs[0], obs[1]))
        
        self.walls = set(wall_positions + obstacle_positions)
        
        # 初始化目标区域（保持顺序！）
        # 使用列表保持 create_3x3_grid 的顺序，同时创建集合用于快速查找
        self.left_team_target_list = [Position(x, y) for x, y in left_target]
        self.left_team_target_set = set(self.left_team_target_list)
        self.right_team_target_list = [Position(x, y) for x, y in right_target]
        self.right_team_target_set = set(self.right_team_target_list)
        
        # 初始化监狱（保持顺序！）
        self.left_team_prison_list = [Position(x, y) for x, y in left_prison]
        self.left_team_prison_set = set(self.left_team_prison_list)
        self.right_team_prison_list = [Position(x, y) for x, y in right_prison]
        self.right_team_prison_set = set(self.right_team_prison_list)
    
    def is_on_left(self, x: int, y: int) -> bool:
        """检查位置是否在左侧"""
        return x < self.middle_line
    
    def is_in_team_territory(self, x: int, y: int, team: Team) -> bool:
        """检查位置是否在队伍领地内"""
        is_left = self.is_on_left(x, y)
        return (team == Team.LEFT and is_left) or (team == Team.RIGHT and not is_left)
    
    def is_in_enemy_territory(self, x: int, y: int, team: Team) -> bool:
        """检查位置是否在敌方领地内"""
        return not self.is_in_team_territory(x, y, team)
    
    def is_wall(self, x: int, y: int) -> bool:
        """检查是否是墙"""
        return Position(x, y) in self.walls
    
    def is_valid_position(self, x: int, y: int) -> bool:
        """检查位置是否有效"""
        return (0 <= x < self.width and 
                0 <= y < self.height and
                not self.is_wall(x, y))
    
    def is_in_team_target(self, x: int, y: int, team: Team) -> bool:
        """检查是否在队伍目标区域内（使用集合快速查找）"""
        pos = Position(x, y)
        if team == Team.LEFT:
            return pos in self.left_team_target_set
        else:
            return pos in self.right_team_target_set
    
    def is_in_team_prison(self, x: int, y: int, team: Team) -> bool:
        """检查是否在队伍监狱内（使用集合快速查找）"""
        pos = Position(x, y)
        if team == Team.LEFT:
            return pos in self.left_team_prison_set
        else:
            return pos in self.right_team_prison_set
    
    def get_team_target_positions(self, team: Team) -> List[Position]:
        """
        获取队伍目标位置列表（有序，保持 create_3x3_grid 的顺序）
        
        注意：返回的是有序列表，顺序与 create_3x3_grid 一致
        用于渲染时确保瓦片ID和位置的对应关系正确
        """
        if team == Team.LEFT:
            return self.left_team_target_list
        else:
            return self.right_team_target_list
    
    def get_team_prison_positions(self, team: Team) -> List[Position]:
        """
        获取队伍监狱位置列表（有序，保持 create_3x3_grid 的顺序）
        
        注意：返回的是有序列表，顺序与 create_3x3_grid 一致
        用于渲染时确保瓦片ID和位置的对应关系正确
        """
        if team == Team.LEFT:
            return self.left_team_prison_list
        else:
            return self.right_team_prison_list

