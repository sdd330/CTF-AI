"""
游戏地图模块
管理地图的物理结构：尺寸、障碍物、目标区域、监狱等
"""

from typing import Set, Optional

from ..data_models import Position, Team, TargetArea, PrisonArea


class GameMap:
    """游戏地图类"""

    def __init__(self):
        self.width = 0
        self.height = 0
        self.middle_line = 0.0
        self.walls: Set[Position] = set()
        self.left_team_target: Optional[TargetArea] = None
        self.right_team_target: Optional[TargetArea] = None
        self.left_team_prison: Optional[PrisonArea] = None
        self.right_team_prison: Optional[PrisonArea] = None

    def initialize(self, map_data: dict, my_team_name: str,
                   my_team_target: list, opponent_target: list,
                   my_team_prison: list, opponent_prison: list):
        """初始化地图"""
        self._init_dimensions(map_data)
        self._init_walls(map_data)
        self._init_areas(my_team_name, my_team_target, opponent_target,
                         my_team_prison, opponent_prison)
        self._validate_areas()

    def _init_dimensions(self, map_data: dict):
        """初始化地图尺寸"""
        if "width" not in map_data or "height" not in map_data:
            raise ValueError(f"❌ [GameMap] 地图数据缺少必需字段！")
        self.width = map_data.get("width", 0)
        self.height = map_data.get("height", 0)
        if self.width <= 0 or self.height <= 0:
            raise ValueError(f"❌ [GameMap] 地图尺寸无效！width={self.width}, height={self.height}")
        self.middle_line = self.width / 2.0
        print(f"🗺️  [GameMap] 设置地图: {self.width}x{self.height}, 中线: {self.middle_line}", flush=True)

    def _init_walls(self, map_data: dict):
        """初始化墙壁"""
        self.walls = {
            Position(w["x"], w["y"])
            for w in (map_data.get("walls", []) + map_data.get("obstacles", []))
        }

    def _init_areas(self, my_team_name: str, my_target: list, opp_target: list,
                    my_prison: list, opp_prison: list):
        """初始化目标区域和监狱"""
        my_target_pos = {Position(t["x"], t["y"]) for t in my_target}
        opp_target_pos = {Position(t["x"], t["y"]) for t in opp_target}
        my_prison_pos = {Position(p["x"], p["y"]) for p in my_prison}
        opp_prison_pos = {Position(p["x"], p["y"]) for p in opp_prison}

        if my_team_name == "L":
            self.left_team_target = TargetArea(Team.LEFT, my_target_pos)
            self.right_team_target = TargetArea(Team.RIGHT, opp_target_pos)
            self.left_team_prison = PrisonArea(Team.LEFT, my_prison_pos)
            self.right_team_prison = PrisonArea(Team.RIGHT, opp_prison_pos)
        else:
            self.right_team_target = TargetArea(Team.RIGHT, my_target_pos)
            self.left_team_target = TargetArea(Team.LEFT, opp_target_pos)
            self.right_team_prison = PrisonArea(Team.RIGHT, my_prison_pos)
            self.left_team_prison = PrisonArea(Team.LEFT, opp_prison_pos)

    def _validate_areas(self):
        """验证区域归属"""
        checks = [
            (self.left_team_target, Team.LEFT, "L队基地"),
            (self.right_team_target, Team.RIGHT, "R队基地"),
            (self.left_team_prison, Team.LEFT, "L队监狱"),
            (self.right_team_prison, Team.RIGHT, "R队监狱"),
        ]
        for area, team, name in checks:
            if area and not area.belongs_to_team(team):
                raise ValueError(f"{name}归属错误！belongs_to={area.belongs_to.value}")

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

    def _get_area(self, team: Team, is_target: bool):
        """获取指定队伍的区域"""
        if is_target:
            return self.left_team_target if team == Team.LEFT else self.right_team_target
        return self.left_team_prison if team == Team.LEFT else self.right_team_prison

    def get_team_target_positions(self, team: Team) -> Set[Position]:
        """获取队伍目标位置集合"""
        area = self._get_area(team, is_target=True)
        return area.positions if area else set()

    def get_team_target_area(self, team: Team) -> Optional[TargetArea]:
        """获取队伍基地对象"""
        return self._get_area(team, is_target=True)

    def get_team_prison_positions(self, team: Team) -> Set[Position]:
        """获取队伍监狱位置集合"""
        area = self._get_area(team, is_target=False)
        return area.positions if area else set()

    def get_team_prison_area(self, team: Team) -> Optional[PrisonArea]:
        """获取队伍监狱对象"""
        return self._get_area(team, is_target=False)

    def is_in_team_prison(self, position: Position, team: Team) -> bool:
        """检查位置是否在队伍监狱内"""
        area = self.get_team_prison_area(team)
        return area.contains(position) if area else False
