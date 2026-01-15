"""
游戏日志记录器
负责记录游戏相关的日志信息
"""

from typing import Dict, TYPE_CHECKING
from ..data_models import Team

if TYPE_CHECKING:
    from .game import World


class GameLogger:
    """游戏日志记录器 - 负责记录游戏相关的日志信息"""
    
    def __init__(self, world: 'World'):
        """
        初始化日志记录器
        
        Args:
            world: World 对象，用于访问游戏状态
        """
        self.world = world
    
    def log_game_reset(self) -> None:
        """记录游戏重置"""
        print(f"🔄 [World] 重置游戏状态...", flush=True)
    
    def log_game_reset_complete(self) -> None:
        """记录游戏重置完成"""
        print(f"✅ [World] 游戏状态已重置", flush=True)
    
    def log_game_reinit(self, team_prefix: str) -> None:
        """记录游戏重新初始化"""
        print(f"🔄 [{team_prefix}] [World] ========== 重新初始化游戏 ==========", flush=True)
    
    def log_game_init(self, team_prefix: str, my_team_name: str) -> None:
        """记录游戏初始化"""
        print(f"🎮 [{team_prefix}] [World] 初始化游戏！队伍: {my_team_name}", flush=True)
    
    def log_request_data(self, req: Dict) -> None:
        """记录请求数据（基于 GameInitPayload 字段）"""
        print(f"🔍 [World] 初始化请求数据：", flush=True)
        print(f"   - myteamName: {req.get('myteamName', 'N/A')}", flush=True)
        print(f"   - numPlayers: {req.get('numPlayers', 'N/A')}", flush=True)
        print(f"   - numFlags: {req.get('numFlags', 'N/A')}", flush=True)
        print(f"   - myteamTarget数量: {len(req.get('myteamTarget', []))}", flush=True)
        print(f"   - myteamPrison数量: {len(req.get('myteamPrison', []))}", flush=True)
        print(f"   - opponentTarget数量: {len(req.get('opponentTarget', []))}", flush=True)
        print(f"   - opponentPrison数量: {len(req.get('opponentPrison', []))}", flush=True)
        print(f"   - 请求keys: {list(req.keys())}", flush=True)
    
    def log_initialization_complete(self) -> None:
        """记录初始化完成信息"""
        print(f"✅ [World] ========== 游戏初始化完成 ==========", flush=True)
        print(f"   - 地图: {self.world.map.width}x{self.world.map.height}", flush=True)
        print(f"   - 队伍: {self.world.my_team_name}", flush=True)
        print(f"   - 玩家数量: 我方={len(self.world.my_players)}, 敌方={len(self.world.enemy_players)}", flush=True)
        print(f"   - 旗帜数量: 我方={len(self.world.my_flags)}, 敌方={len(self.world.enemy_flags)}", flush=True)
        print(f"   - 得分: L={self.world.left_team_score}, R={self.world.right_team_score}", flush=True)
    
    def log_player_init(self, player_name: str, team: Team, is_my_team: bool) -> None:
        """记录玩家初始化"""
        team_type = "己方" if is_my_team else "敌方"
        print(f"👤 [World] 初始化{team_type}玩家: {player_name}, 队伍: {team.value}队", flush=True)
    
    def log_flag_init(self, flag_id: str, team: Team, is_my_team: bool) -> None:
        """记录旗帜初始化"""
        team_type = "己方" if is_my_team else "敌方"
        print(f"🚩 [World] 初始化{team_type}旗帜: {flag_id}, 归属: {team.value}队", flush=True)
    
    def log_scoring(self, player_name: str, team: Team, team_prefix: str) -> None:
        """记录得分"""
        print(f"🎉 [{team_prefix}] [World] 玩家 {player_name} ({team.value}队) 在己方基地插旗得分！当前得分: L={self.world.left_team_score}, R={self.world.right_team_score}", flush=True)
    
    def log_skip_collect_action(self, team_prefix: str, player_name: str, player_team: Team) -> None:
        """记录跳过收集非己方玩家动作"""
        print(f"⚠️  [{team_prefix}] [GameInfoCollector] 跳过收集非己方玩家动作: {player_name} ({player_team.value}队)", flush=True)
