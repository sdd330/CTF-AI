"""
游戏初始化器
负责游戏初始化相关逻辑
"""

from typing import Dict, Optional
from ..data_models import Team, Position, Flag, Player
from ..map_service import GameMap
from ..pathfinding_service import PathFindingService
from ..utils import list_players, list_flags


class GameInitializer:
    """游戏初始化器：初始化游戏"""
    
    def __init__(self, world):
        self.world = world
    
    def init(self, req: Dict):
        """从请求初始化游戏（每次游戏开始都会调用，包括重新开始）"""
        # myteamName 必须在请求中提供，且一旦设置不可更改
        self.world.my_team_name = req["myteamName"]
        team_prefix = f"{self.world.my_team_name}队"
        
        print(f"🔄 [{team_prefix}] [World] ========== 重新初始化游戏 ==========", flush=True)
        
        self._reset_game_state()
        
        my_team = Team.from_name(self.world.my_team_name)
        enemy_team = my_team.get_enemy()
        
        print(f"🎮 [{team_prefix}] [World] 初始化游戏！队伍: {self.world.my_team_name}, Team对象: {my_team.value}", flush=True)
        self._log_request_data(req)
        
        map_data = self._validate_map_data(req)
        self._initialize_map(req, map_data)
        self._initialize_flags(req, my_team, enemy_team)
        self._initialize_players(req, my_team, enemy_team)
        
        self._log_initialization_complete()
    
    def _log_request_data(self, req: Dict) -> None:
        """记录请求数据"""
        print(f"🔍 [World] 初始化请求数据：", flush=True)
        print(f"   - myteamPlayer数量: {len(req.get('myteamPlayer', []))}", flush=True)
        print(f"   - opponentPlayer数量: {len(req.get('opponentPlayer', []))}", flush=True)
        print(f"   - myteamFlag数量: {len(req.get('myteamFlag', []))}", flush=True)
        print(f"   - opponentFlag数量: {len(req.get('opponentFlag', []))}", flush=True)
        print(f"   - 请求keys: {list(req.keys())}", flush=True)
    
    def _validate_map_data(self, req: Dict) -> Dict:
        """验证地图数据"""
        if "map" not in req:
            raise ValueError("❌ [World] 初始化请求缺少 'map' 字段！")
        
        map_data = req["map"]
        if not isinstance(map_data, dict):
            raise ValueError(f"❌ [World] 'map' 字段必须是字典类型，实际类型: {type(map_data)}")
        
        if "width" not in map_data or "height" not in map_data:
            raise ValueError(f"❌ [World] 地图数据缺少 'width' 或 'height' 字段！map keys: {list(map_data.keys())}")
        
        map_width = map_data.get("width", 0)
        map_height = map_data.get("height", 0)
        
        if map_width <= 0 or map_height <= 0:
            raise ValueError(f"❌ [World] 地图尺寸无效！width={map_width}, height={map_height}")
        
        print(f"🗺️  [World] 地图数据验证通过: {map_width}x{map_height}", flush=True)
        return map_data
    
    def _initialize_map(self, req: Dict, map_data: Dict) -> None:
        """初始化地图"""
        self.world.initialize_map(
            map_data=map_data,
            my_team_name=self.world.my_team_name,
            my_team_target=req.get("myteamTarget", []),
            opponent_target=req.get("opponentTarget", []),
            my_team_prison=req.get("myteamPrison", []),
            opponent_prison=req.get("opponentPrison", [])
        )
        
        map_width = map_data.get("width", 0)
        map_height = map_data.get("height", 0)
        if (self.world.width != map_width or 
            self.world.height != map_height):
            raise ValueError(f"❌ [World] 地图初始化后尺寸不匹配！期望: {map_width}x{map_height}, 实际: {self.world.width}x{self.world.height}")
    
    def _log_initialization_complete(self) -> None:
        """记录初始化完成信息"""
        print(f"✅ [World] ========== 游戏初始化完成 ==========", flush=True)
        print(f"   - 地图: {self.world.width}x{self.world.height}", flush=True)
        print(f"   - 玩家数量: {len(self.world.players)}", flush=True)
        print(f"   - 旗帜数量: {len(self.world.flags)}", flush=True)
        print(f"   - 得分: L={self.world.left_team_score}, R={self.world.right_team_score}", flush=True)
    
    def _reset_game_state(self):
        """完全重置游戏状态（用于游戏重新开始）"""
        print(f"🔄 [World] 重置游戏状态...", flush=True)
        
        # 清空字典而不是创建新字典，保持引用有效
        self.world.players.clear()
        self.world.flags.clear()
        self.world.left_team_score = 0
        self.world.right_team_score = 0
        self.world.current_time = 0.0
        
        # 重新初始化路径查找服务
        self.world._pathfinding_service = PathFindingService(
            self.world,  # 传入 world 对象
            pathfinding_strategy=self.world._pathfinding_strategy
        )
        
        print(f"✅ [World] 游戏状态已重置", flush=True)
    
    def _initialize_flags(self, req: Dict, my_team: Team, enemy_team: Team):
        """初始化旗帜"""
        self.world.flags.clear()
        flag_id = 0
        
        flag_id = self._initialize_team_flags(req.get("myteamFlag", []), my_team, "己方", flag_id)
        flag_id = self._initialize_team_flags(req.get("opponentFlag", []), enemy_team, "敌方", flag_id)
    
    def _initialize_team_flags(self, flags_data: list, team: Team, team_type: str, flag_id: int) -> int:
        """初始化队伍旗帜"""
        for f_data in flags_data:
            flag = Flag(f"{team_type.lower()}_flag_{flag_id}", team, 
                       Position(f_data["posX"], f_data["posY"]))
            flag.is_picked_up = not f_data.get("canPickup", True)
            self.world.flags[flag.flag_id] = flag
            print(f"🚩 [World] 初始化{team_type}旗帜: {flag.flag_id}, 归属: {flag.belongs_to.value}队, 位置: {flag.position}", flush=True)
            flag_id += 1
        return flag_id
    
    def _initialize_players(self, req: Dict, my_team: Team, enemy_team: Team):
        """初始化玩家"""
        self.world.players.clear()
        
        self._initialize_team_players(req.get("myteamPlayer", []), my_team, enemy_team, "己方")
        self._initialize_team_players(req.get("opponentPlayer", []), enemy_team, my_team, "敌方")
    
    def _initialize_team_players(self, players_data: list, team: Team, prison_team: Team, team_type: str):
        """初始化队伍玩家"""
        # 获取队伍的基地位置（每个队伍只有一个基地）
        base_area = self.world.get_team_target_area(team)
        
        for p_data in players_data:
            player = Player(p_data["name"], team, Position(p_data["posX"], p_data["posY"]), self.world)
            
            # 设置基地位置
            if base_area:
                player.set_base_area(base_area)
            
            if p_data.get("inPrison", False):
                prison_area = self.world.get_team_prison_area(prison_team)
                if prison_area and prison_area.positions:
                    player.send_to_prison(next(iter(prison_area.positions)))
            
            if p_data.get("hasFlag", False):
                player._associate_flag_from_dict(self.world.flags)
            
            self.world.players[player.name] = player
            base_info = f"基地位置数: {len(base_area.positions)}" if base_area else "无基地"
            print(f"👤 [World] 初始化{team_type}玩家: {player.name}, 队伍: {player.team.value}队, 位置: {player.position}, {base_info}", flush=True)

