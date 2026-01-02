"""
游戏统计工具类
提供游戏统计信息计算功能
"""

from typing import Dict, Tuple, TYPE_CHECKING
from ..data_models import Team
from .player_utils import list_players, list_flags

if TYPE_CHECKING:
    from ..game_service import World
    from ..map_service import GameMap
else:
    World = None
    GameMap = None


class GameStatistics:
    """游戏统计工具类 - 单一职责：计算游戏统计信息"""
    
    @staticmethod
    def calculate_scores(world: World, my_team: Team, game_map: GameMap) -> Tuple[int, int]:
        """
        计算双方得分
        
        Args:
            world: World对象
            my_team: 己方队伍
            game_map: 地图实例
        Returns:
            (己方得分, 敌方得分)
        """
        enemy_team = my_team.get_enemy()
        enemy_flags = list_flags(world.flags, my_team, is_enemy=True, can_pickup=None)
        my_flags = list_flags(world.flags, my_team, is_enemy=False, can_pickup=None)
        
        my_targets_set = game_map.get_team_target_positions(my_team)
        enemy_targets_set = game_map.get_team_target_positions(enemy_team)
        
        # 己方得分 = 己方目标区域内的敌方旗帜数量
        my_score = sum(1 for flag in enemy_flags if flag.position in my_targets_set)
        # 敌方得分 = 敌方目标区域内的己方旗帜数量
        enemy_score = sum(1 for flag in my_flags if flag.position in enemy_targets_set)
        
        return my_score, enemy_score
    
    @staticmethod
    def get_players_statistics(world: World, my_team: Team) -> Dict[str, int]:
        """
        获取玩家统计信息
        
        Args:
            world: World对象
            my_team: 己方队伍
        Returns:
            统计信息字典
        """
        enemy_team = my_team.get_enemy()
        
        return {
            "my_free": len(list_players(world.players, my_team, in_prison=False, has_flag=False)),
            "my_with_flag": len(list_players(world.players, my_team, in_prison=False, has_flag=True)),
            "my_in_prison": len(list_players(world.players, my_team, in_prison=True, has_flag=None)),
            "enemies": len(list_players(world.players, enemy_team, in_prison=False, has_flag=None)),
            "enemy_flags": len(list_flags(world.flags, my_team, is_enemy=True, can_pickup=True)),
        }
    
    @staticmethod
    def get_team_status(world: World, team: Team) -> Dict[str, int]:
        """
        获取队伍状态统计
        
        Args:
            world: World对象
            team: 队伍
        Returns:
            队伍状态字典
        """
        return {
            "total_players": len(list_players(world.players, team, in_prison=None, has_flag=None)),
            "free_players": len(list_players(world.players, team, in_prison=False, has_flag=False)),
            "players_with_flag": len(list_players(world.players, team, in_prison=False, has_flag=True)),
            "players_in_prison": len(list_players(world.players, team, in_prison=True, has_flag=None)),
            "flags_count": len(list_flags(world.flags, team, is_enemy=False, can_pickup=None)),
            "enemy_flags_count": len(list_flags(world.flags, team, is_enemy=True, can_pickup=None)),
        }

