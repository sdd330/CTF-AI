"""
游戏地图模块
管理地图的物理结构：尺寸、障碍物、目标区域、监狱等
"""

from typing import Set, Dict, Optional

from ..data_models import Position, Team, TargetArea, PrisonArea


class GameMap:
    """游戏地图类"""
    
    def __init__(self):
        self.width = 0
        self.height = 0
        self.middle_line = 0.0
        self.walls: Set[Position] = set()
        # 🚨 使用面向对象设计：基地和监狱对象
        self.left_team_target: Optional[TargetArea] = None
        self.right_team_target: Optional[TargetArea] = None
        self.left_team_prison: Optional[PrisonArea] = None
        self.right_team_prison: Optional[PrisonArea] = None
    
    def initialize(self, map_data: Dict, my_team_name: str, 
                   my_team_target: list, opponent_target: list,
                   my_team_prison: list, opponent_prison: list):
        """
        初始化地图
        Args:
            map_data: 地图数据字典
            my_team_name: 己方队伍名称 ("L" 或 "R")
            my_team_target: 己方目标区域列表
            opponent_target: 对方目标区域列表
            my_team_prison: 己方监狱列表
            opponent_prison: 对方监狱列表
        """
        # 🚨 验证地图数据
        if "width" not in map_data or "height" not in map_data:
            raise ValueError(f"❌ [GameMap] 地图数据缺少必需字段！map_data keys: {list(map_data.keys())}")
        
        self.width = map_data.get("width", 0)
        self.height = map_data.get("height", 0)
        
        if self.width <= 0 or self.height <= 0:
            raise ValueError(f"❌ [GameMap] 地图尺寸无效！width={self.width}, height={self.height}")
        
        self.middle_line = self.width / 2.0
        
        print(f"🗺️  [GameMap] 设置地图尺寸: {self.width}x{self.height}, 中线: {self.middle_line}", flush=True)
        
        # 初始化墙壁
        self.walls = {
            Position(w["x"], w["y"]) 
            for w in (map_data.get("walls", []) + map_data.get("obstacles", []))
        }
        
        # 🚨 初始化目标区域和监狱 - 使用面向对象设计
        if my_team_name == "L":
            # L 队是己方
            left_target_positions = {Position(t["x"], t["y"]) for t in my_team_target}
            right_target_positions = {Position(t["x"], t["y"]) for t in opponent_target}
            left_prison_positions = {Position(p["x"], p["y"]) for p in my_team_prison}
            right_prison_positions = {Position(p["x"], p["y"]) for p in opponent_prison}
            
            self.left_team_target = TargetArea(Team.LEFT, left_target_positions)
            self.right_team_target = TargetArea(Team.RIGHT, right_target_positions)
            self.left_team_prison = PrisonArea(Team.LEFT, left_prison_positions)
            self.right_team_prison = PrisonArea(Team.RIGHT, right_prison_positions)
            
            print(f"🗺️  [GameMap] 初始化地图 - L队视角:", flush=True)
            print(f"   L队基地: {self.left_team_target}", flush=True)
            print(f"   R队基地: {self.right_team_target}", flush=True)
            print(f"   L队监狱: {self.left_team_prison}", flush=True)
            print(f"   R队监狱: {self.right_team_prison}", flush=True)
        else:  # R
            # R 队是己方
            right_target_positions = {Position(t["x"], t["y"]) for t in my_team_target}
            left_target_positions = {Position(t["x"], t["y"]) for t in opponent_target}
            right_prison_positions = {Position(p["x"], p["y"]) for p in my_team_prison}
            left_prison_positions = {Position(p["x"], p["y"]) for p in opponent_prison}
            
            self.right_team_target = TargetArea(Team.RIGHT, right_target_positions)
            self.left_team_target = TargetArea(Team.LEFT, left_target_positions)
            self.right_team_prison = PrisonArea(Team.RIGHT, right_prison_positions)
            self.left_team_prison = PrisonArea(Team.LEFT, left_prison_positions)
            
            print(f"🗺️  [GameMap] 初始化地图 - R队视角:", flush=True)
            print(f"   R队基地: {self.right_team_target}", flush=True)
            print(f"   L队基地: {self.left_team_target}", flush=True)
            print(f"   R队监狱: {self.right_team_prison}", flush=True)
            print(f"   L队监狱: {self.left_team_prison}", flush=True)
        
        # 🚨 验证：确保基地和监狱的归属正确（使用通用的 belongs_to_team 方法）
        if self.left_team_target and not self.left_team_target.belongs_to_team(Team.LEFT):
            raise ValueError(f"L队基地归属错误！belongs_to={self.left_team_target.belongs_to.value}")
        if self.right_team_target and not self.right_team_target.belongs_to_team(Team.RIGHT):
            raise ValueError(f"R队基地归属错误！belongs_to={self.right_team_target.belongs_to.value}")
        if self.left_team_prison and not self.left_team_prison.belongs_to_team(Team.LEFT):
            raise ValueError(f"L队监狱归属错误！belongs_to={self.left_team_prison.belongs_to.value}")
        if self.right_team_prison and not self.right_team_prison.belongs_to_team(Team.RIGHT):
            raise ValueError(f"R队监狱归属错误！belongs_to={self.right_team_prison.belongs_to.value}")
    
    def is_on_left(self, position: Position) -> bool:
        """检查位置是否在左侧"""
        return position.x < self.middle_line
    
    def is_in_team_territory(self, position: Position, team: Team) -> bool:
        """检查位置是否在队伍领地内"""
        is_left = self.is_on_left(position)
        return (team == Team.LEFT and is_left) or (team == Team.RIGHT and not is_left)
    
    def is_in_enemy_territory(self, position: Position, team: Team) -> bool:
        """检查位置是否在敌方领地内"""
        return not self.is_in_team_territory(position, team)
    
    def is_wall(self, position: Position) -> bool:
        """检查是否是墙"""
        return position in self.walls
    
    def is_valid_position(self, position: Position) -> bool:
        """检查位置是否有效"""
        return (0 <= position.x < self.width and 
                0 <= position.y < self.height and
                not self.is_wall(position))
    
    def _validate_area_ownership(self, area, team: Team, area_type: str) -> None:
        """
        验证区域归属（内部辅助方法）
        
        Args:
            area: 区域对象（TargetArea 或 PrisonArea）
            team: 队伍
            area_type: 区域类型名称（用于错误消息）
        Raises:
            ValueError: 如果归属不匹配
        """
        if area and not area.belongs_to_team(team):
            raise ValueError(f"{area_type}归属错误！请求 {team.value}队，但{area_type}属于 {area.belongs_to.value}队")
    
    def get_team_target_positions(self, team: Team) -> Set[Position]:
        """
        获取队伍目标位置集合 - 使用归属属性验证
        Args:
            team: 队伍
        Returns:
            目标位置集合
        """
        target_area = self.left_team_target if team == Team.LEFT else self.right_team_target
        if target_area:
            self._validate_area_ownership(target_area, team, "基地")
            return target_area.positions
        return set()
    
    def get_team_target_area(self, team: Team) -> Optional[TargetArea]:
        """
        获取队伍基地对象 - 使用归属属性验证
        Args:
            team: 队伍
        Returns:
            基地对象，如果不存在返回None
        """
        target_area = self.left_team_target if team == Team.LEFT else self.right_team_target
        if target_area:
            self._validate_area_ownership(target_area, team, "基地")
        return target_area
    
    def get_team_prison_positions(self, team: Team) -> Set[Position]:
        """
        获取队伍监狱位置集合 - 使用归属属性验证
        Args:
            team: 队伍
        Returns:
            监狱位置集合
        """
        prison_area = self.left_team_prison if team == Team.LEFT else self.right_team_prison
        if prison_area:
            self._validate_area_ownership(prison_area, team, "监狱")
            return prison_area.positions
        return set()
    
    def get_team_prison_area(self, team: Team) -> Optional[PrisonArea]:
        """
        获取队伍监狱对象 - 使用归属属性验证
        Args:
            team: 队伍
        Returns:
            监狱对象，如果不存在返回None
        """
        prison_area = self.left_team_prison if team == Team.LEFT else self.right_team_prison
        if prison_area:
            self._validate_area_ownership(prison_area, team, "监狱")
        return prison_area
    
    def is_in_team_prison(self, position: Position, team: Team) -> bool:
        """
        检查位置是否在队伍监狱内 - 使用归属属性验证
        Args:
            position: 位置
            team: 队伍
        Returns:
            如果位置在监狱内返回True
        """
        prison_area = self.get_team_prison_area(team)
        if prison_area:
            return prison_area.contains(position)
        return False

