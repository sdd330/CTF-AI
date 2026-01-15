"""
游戏信息收集器
负责收集和整理游戏信息（动作、路径、耗时等）用于前端可视化
"""

from typing import Dict, List, Optional, TYPE_CHECKING
from ..data_models import Player, Direction, Position

if TYPE_CHECKING:
    from .game import World
    from .game_logger import GameLogger


class GameInfoCollector:
    """游戏信息收集器 - 负责收集动作、路径、耗时等信息"""
    
    def __init__(self, world: 'World'):
        """
        初始化信息收集器
        
        Args:
            world: World 对象，用于访问游戏状态
        """
        self.world = world
    
    def collect_action(self, player: Player, direction: Optional[Direction]) -> None:
        """收集玩家的动作（只收集己方队伍）"""
        # 只收集我方玩家的动作
        if player.name in self.world.my_players:
            self.world._actions[player.name] = (direction or Direction.STAY).value
        else:
            team_prefix = f"{self.world.my_team_name}队"
            self.world._logger.log_skip_collect_action(team_prefix, player.name, player.team)
    
    def collect_paths_for_visualization(self) -> None:
        """收集路径数据用于前端可视化（只收集己方队伍）"""
        # 直接遍历我方玩家，只收集我方玩家的路径
        for player_name, player in self.world.my_players.items():
            if player_name not in self.world._current_paths:
                continue
            
            path = self.world._current_paths[player_name]
            if path and len(path) > 0:
                self.world._paths[player_name] = [
                    {"x": pos.x, "y": pos.y} 
                    for pos in path
                ]
                # 收集耗时信息（如果存在）
                if player_name in self.world._path_timings:
                    # 将耗时信息添加到路径数据中（作为元数据）
                    pass  # 耗时信息将在返回的 timings 字段中单独传递
    
    def build_result_from_actions(self, actions: Dict[str, str]) -> Dict[str, Dict]:
        """
        基于传入的动作字典和当前帧收集到的路径/耗时，构造返回给前端的结果。
        
        - 只返回己方队伍玩家的数据
        - 路径来源于 self.world._current_paths / self.world._paths
        - 耗时信息来源于 self.world._path_timings
        
        方便在不同的决策入口（普通对战 / Gym 训练桥接）之间复用。
        """
        # 基于当前帧的 _current_paths 收集可视化路径
        self.world._paths.clear()
        self.collect_paths_for_visualization()
        
        filtered_actions: Dict[str, str] = {}
        filtered_paths: Dict[str, List[Dict[str, int]]] = {}
        filtered_timings: Dict[str, Dict[str, float]] = {}
        
        # 过滤动作：仅保留我方玩家（直接从我方玩家字典检查）
        for player_name, direction in actions.items():
            if player_name in self.world.my_players:
                filtered_actions[player_name] = direction
        
        # 过滤路径：collect_paths_for_visualization 已经只收集我方玩家，这里直接使用
        for player_name, path in self.world._paths.items():
            if player_name in self.world.my_players:
                filtered_paths[player_name] = path
        
        # 过滤耗时信息：仅保留我方玩家（直接从我方玩家字典检查）
        for player_name, timings in self.world._path_timings.items():
            if player_name in self.world.my_players:
                filtered_timings[player_name] = timings
        
        return {
            "actions": filtered_actions,
            "paths": filtered_paths,
            "timings": filtered_timings,
        }
