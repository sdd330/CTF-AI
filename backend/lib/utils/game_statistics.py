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
        # 直接从字典获取
        enemy_flags = list(world.enemy_flags.values())
        my_flags = list(world.my_flags.values())
        
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
        # 直接从我方和敌方玩家字典获取
        my_players = world.my_players.values()
        enemy_players = world.enemy_players.values()
        enemy_flags_count = len([f for f in world.enemy_flags.values() if f.can_pickup])
        return {
            "my_free": len([p for p in my_players if not p.is_in_prison and not p.has_flag]),
            "my_with_flag": len([p for p in my_players if not p.is_in_prison and p.has_flag]),
            "my_in_prison": len([p for p in my_players if p.is_in_prison]),
            "enemies": len([p for p in enemy_players if not p.is_in_prison]),
            "enemy_flags": enemy_flags_count,
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
        # 根据队伍直接获取玩家和旗帜
        if team == Team.from_name(world.my_team_name):
            players = world.my_players.values()
            flags_count = len(world.my_flags)
            enemy_flags_count = len(world.enemy_flags)
        else:
            players = world.enemy_players.values()
            flags_count = len(world.enemy_flags)
            enemy_flags_count = len(world.my_flags)
        
        return {
            "total_players": len(list(players)),
            "free_players": len([p for p in players if not p.is_in_prison and not p.has_flag]),
            "players_with_flag": len([p for p in players if not p.is_in_prison and p.has_flag]),
            "players_in_prison": len([p for p in players if p.is_in_prison]),
            "flags_count": flags_count,
            "enemy_flags_count": enemy_flags_count,
        }

