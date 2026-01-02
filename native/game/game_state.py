"""
游戏状态管理
"""

from typing import List, Dict, TYPE_CHECKING
from ..utils import Team

if TYPE_CHECKING:
    from ..objects import Player, Flag


class GameState:
    """游戏状态类"""
    
    def __init__(self):
        self.left_team_score = 0
        self.right_team_score = 0
        self.game_started = False
        self.game_paused = False
        self.game_over = False
        self.winner: Team | None = None
        
        # 玩家和旗帜
        self.left_team_players: List['Player'] = []
        self.right_team_players: List['Player'] = []
        self.left_team_flags: List['Flag'] = []
        self.right_team_flags: List['Flag'] = []
        
        # 游戏配置
        self.num_players = 3
        self.num_flags = 9
        self.max_score = 5  # 达到此分数游戏结束
    
    def get_team_players(self, team: Team) -> List['Player']:
        """获取队伍玩家列表"""
        if team == Team.LEFT:
            return self.left_team_players
        else:
            return self.right_team_players
    
    def get_team_flags(self, team: Team) -> List['Flag']:
        """获取队伍旗帜列表"""
        if team == Team.LEFT:
            return self.left_team_flags
        else:
            return self.right_team_flags
    
    def get_all_players(self) -> List['Player']:
        """获取所有玩家"""
        return self.left_team_players + self.right_team_players
    
    def get_all_flags(self) -> List['Flag']:
        """获取所有旗帜"""
        return self.left_team_flags + self.right_team_flags
    
    def check_game_over(self) -> bool:
        """检查游戏是否结束"""
        if self.left_team_score >= self.max_score:
            self.game_over = True
            self.winner = Team.LEFT
            return True
        elif self.right_team_score >= self.max_score:
            self.game_over = True
            self.winner = Team.RIGHT
            return True
        return False

