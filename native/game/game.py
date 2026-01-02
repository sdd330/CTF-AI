"""
游戏主类
"""

from typing import List, Optional
from ..utils import Team, Direction
from ..objects import Player, Flag
from ..map.map import GameMap
from .game_state import GameState


class CTFGame:
    """Capture the Flag 游戏主类"""
    
    def __init__(self, game_map: GameMap):
        """
        初始化游戏
        
        Args:
            game_map: 游戏地图
        """
        self.game_map = game_map
        self.state = GameState()
        self.tick_count = 0
    
    def initialize(self, num_players: int = 3, num_flags: int = 9):
        """
        初始化游戏
        
        Args:
            num_players: 每队玩家数量
            num_flags: 每队旗帜数量
        """
        self.state.num_players = num_players
        self.state.num_flags = num_flags
        
        # 创建玩家
        self._create_players()
        
        # 创建旗帜
        self._create_flags()
        
        # 注意：game_started 应该保持为 False，直到用户按空格键开始游戏
        # 参考 frontend，游戏初始化时 game_started 为 False
        self.state.game_started = False
    
    def _create_players(self):
        """
        创建玩家
        参考 frontend: generatePlayers
        - L队：x=2, y=i+1 (i从0开始)
        - R队：x=mapWidth-3, y=i+1
        """
        # L队玩家（左侧，x=2）
        for i in range(self.state.num_players):
            x = 2
            y = i + 1
            player = Player(f"L{i}", Team.LEFT, x, y)
            self.state.left_team_players.append(player)
        
        # R队玩家（右侧，x=mapWidth-3）
        for i in range(self.state.num_players):
            x = self.game_map.width - 3
            y = i + 1
            player = Player(f"R{i}", Team.RIGHT, x, y)
            self.state.right_team_players.append(player)
    
    def _create_flags(self):
        """
        创建旗帜
        参考 frontend: generateFlags (非随机模式)
        - L队旗帜：x=1, y=i+1 (放在L队领地)
        - R队旗帜：x=mapWidth-2, y=i+1 (放在R队领地)
        """
        # L队旗帜（放在L队领地，x=1）
        for i in range(self.state.num_flags):
            x = 1
            y = i + 1
            flag = Flag(f"L{i}", Team.LEFT, x, y)
            self.state.left_team_flags.append(flag)
        
        # R队旗帜（放在R队领地，x=mapWidth-2）
        for i in range(self.state.num_flags):
            x = self.game_map.width - 2
            y = i + 1
            flag = Flag(f"R{i}", Team.RIGHT, x, y)
            self.state.right_team_flags.append(flag)
    
    def update(self, delta_time: int):
        """
        更新游戏状态
        
        Args:
            delta_time: 时间增量（毫秒）
        """
        if not self.state.game_started or self.state.game_paused or self.state.game_over:
            return
        
        self.tick_count += 1
        
        # 更新旗帜位置（如果被携带）
        for flag in self.state.get_all_flags():
            if flag.is_picked_up and flag.carried_by:
                flag.update_position(
                    flag.carried_by.pixel_x,
                    flag.carried_by.pixel_y
                )
        
        # 检查游戏结束
        self.state.check_game_over()
    
    def set_player_action(self, player_name: str, direction: Direction):
        """
        设置玩家动作
        
        Args:
            player_name: 玩家名称
            direction: 移动方向
        """
        for player in self.state.get_all_players():
            if player.name == player_name:
                # 检查目标位置是否有效
                dx, dy = direction.to_vector()
                new_x = player.grid_x + dx
                new_y = player.grid_y + dy
                
                if self.game_map.is_valid_position(new_x, new_y):
                    player.set_direction(direction)
                break

