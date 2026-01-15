"""
游戏逻辑模块
World 类整合了所有游戏功能
"""

from typing import Dict, List, Optional, Set
from ..data_models import Position, Team, Player, Flag, Direction, Action
from ..map_service import GameMap
from ..pathfinding_service import PathFindingService
from ..utils import can_score_flag
from .game_info_collector import GameInfoCollector
from .game_logger import GameLogger
from .game_state_updater import GameStateUpdater


class World:
    """Capture the Flag 游戏主类 - 整合所有游戏功能"""

    def __init__(self, game_map: GameMap):
        self.map = game_map
        self.my_players: Dict[str, Player] = {}
        self.enemy_players: Dict[str, Player] = {}
        self.my_flags: Dict[str, Flag] = {}
        self.enemy_flags: Dict[str, Flag] = {}
        self.left_team_score = 0
        self.right_team_score = 0
        self.current_time = 0.0
        self.my_team_name = ""

        self._pathfinding_service = PathFindingService(self)
        self._info_collector = GameInfoCollector(self)
        self._logger = GameLogger(self)
        self._state_updater = GameStateUpdater(self)
        self._actions: Dict[str, str] = {}
        self._paths: Dict[str, List[Dict[str, int]]] = {}
        self._path_timings: Dict[str, Dict[str, float]] = {}
        self._current_paths: Dict[str, List[Position]] = {}

    def init(self, req: Dict):
        """从请求初始化游戏"""
        self.my_team_name = req["myteamName"]
        team_prefix = f"{self.my_team_name}队"

        self._logger.log_game_reinit(team_prefix)
        self._reset_game_state()
        self._logger.log_game_init(team_prefix, self.my_team_name)
        self._logger.log_request_data(req)

        self.initialize_map(
            map_data=req["map"],
            my_team_name=self.my_team_name,
            my_team_target=req.get("myteamTarget", []),
            opponent_target=req.get("opponentTarget", []),
            my_team_prison=req.get("myteamPrison", []),
            opponent_prison=req.get("opponentPrison", [])
        )

        self._initialize_players(req.get("numPlayers", 0))
        self._initialize_flags(req.get("numFlags", 0))
        self._logger.log_initialization_complete()

    def update(self, req: Dict) -> bool:
        """从请求更新游戏状态"""
        if req.get("time", 0) < self.current_time:
            return False

        self.current_time = req.get("time", 0)
        self._state_updater.update_flags_from_request(req)
        self._state_updater.update_players_from_request(req)
        self._check_scoring()
        return True

    def plan_actions(self, req: Dict) -> Dict[str, Dict]:
        """计划下一步动作"""
        if not self.update(req):
            return {"actions": {}, "paths": {}}

        my_players = [p for p in self.my_players.values() if not p.is_in_prison]
        self._actions.clear()
        self._paths.clear()
        self._path_timings.clear()
        self._current_paths.clear()
        
        # 🎲 随机打乱玩家规划顺序，让不同玩家有机会先选择目标
        # 每个玩家规划后会将路径存入 _current_paths，后续玩家可以看到
        import random
        random.shuffle(my_players)

        for player in my_players:
            direction_enum = player.plan() or Direction.STAY
            self._info_collector.collect_action(player, direction_enum)

        return self._info_collector.build_result_from_actions(self._actions)

    def _get_my_team(self) -> Team:
        """获取己方队伍"""
        return Team.from_name(self.my_team_name)

    def initialize_map(self, map_data: Dict, my_team_name: str,
                       my_team_target: list, opponent_target: list,
                       my_team_prison: list, opponent_prison: list):
        """初始化地图"""
        self.map.initialize(
            map_data=map_data, my_team_name=my_team_name,
            my_team_target=my_team_target, opponent_target=opponent_target,
            my_team_prison=my_team_prison, opponent_prison=opponent_prison
        )

    def _check_scoring(self) -> None:
        """检测得分"""
        for player in self.my_players.values():
            if player.has_flag and player.is_in_base() and can_score_flag(player):
                if player.action(Action.SCORE_FLAG):
                    team_prefix = f"{player.team.value}队"
                    self._logger.log_scoring(player.name, player.team, team_prefix)

    def find_path_to(self, start: Position, end: Position,
                     extra_obstacles: Optional[Set[Position]] = None,
                     player_name: Optional[str] = None) -> List[Position]:
        """寻找路径"""
        team_prefix = f"{self.my_team_name}队"

        if player_name:
            player = self.my_players.get(player_name)
            if not player or player.is_in_prison:
                return []

        path, timings = self._pathfinding_service.find_path_to(
            start, end, extra_obstacles, player_name, team_prefix)

        if player_name and player_name in self.my_players:
            if player_name not in self._path_timings:
                self._path_timings[player_name] = {}
            for key, value in timings.items():
                # 只累加数字类型的值，跳过字符串（如 'algorithm'）
                if isinstance(value, (int, float)):
                    self._path_timings[player_name][key] = \
                        self._path_timings[player_name].get(key, 0) + value
                else:
                    # 字符串类型直接覆盖（不累加）
                    self._path_timings[player_name][key] = value

        return path

    def get_direction(self, current: Position, next_pos: Position) -> str:
        """获取方向"""
        return self._pathfinding_service.get_direction(current, next_pos)

    def _reset_game_state(self):
        """重置游戏状态"""
        self._logger.log_game_reset()
        self.my_players.clear()
        self.enemy_players.clear()
        self.my_flags.clear()
        self.enemy_flags.clear()
        self.left_team_score = 0
        self.right_team_score = 0
        self.current_time = 0.0
        self._pathfinding_service = PathFindingService(self)
        self._logger.log_game_reset_complete()

    def _initialize_players(self, num_players: int) -> None:
        """初始化玩家对象"""
        my_team = self._get_my_team()
        enemy_team = my_team.get_enemy()
        my_base_area = self.map.get_team_target_area(my_team)
        enemy_base_area = self.map.get_team_target_area(enemy_team)

        for i in range(num_players):
            player_name = f"{my_team.value}{i}"
            player = Player(player_name, my_team, Position(0, 0), self)
            if my_base_area:
                player.set_base_area(my_base_area)
            self.my_players[player_name] = player
            self._logger.log_player_init(player_name, my_team, is_my_team=True)

        for i in range(num_players):
            player_name = f"{enemy_team.value}{i}"
            player = Player(player_name, enemy_team, Position(0, 0), self)
            if enemy_base_area:
                player.set_base_area(enemy_base_area)
            self.enemy_players[player_name] = player
            self._logger.log_player_init(player_name, enemy_team, is_my_team=False)

    def _initialize_flags(self, num_flags: int) -> None:
        """初始化旗帜对象"""
        my_team = self._get_my_team()
        enemy_team = my_team.get_enemy()

        for i in range(num_flags):
            flag_id = f"FLAG_{my_team.value}_{i}"
            self.my_flags[flag_id] = Flag(flag_id, my_team, Position(0, 0))
            self._logger.log_flag_init(flag_id, my_team, is_my_team=True)

        for i in range(num_flags):
            flag_id = f"FLAG_{enemy_team.value}_{i}"
            self.enemy_flags[flag_id] = Flag(flag_id, enemy_team, Position(0, 0))
            self._logger.log_flag_init(flag_id, enemy_team, is_my_team=False)
