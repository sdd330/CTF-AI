"""
游戏状态更新器
处理玩家和旗帜的状态更新
"""

from typing import Dict, TYPE_CHECKING
from ..data_models import Position, Team, Player, Flag

if TYPE_CHECKING:
    from .game import World


class GameStateUpdater:
    """游戏状态更新器 - 处理玩家和旗帜的状态更新"""

    def __init__(self, world: 'World'):
        self.world = world

    def update_flags_from_request(self, req: Dict) -> None:
        """更新旗帜状态"""
        self._recreate_my_flags(req, "myteamFlag")
        self._update_enemy_flags(req, "opponentFlag")

    def update_players_from_request(self, req: Dict) -> None:
        """更新玩家状态"""
        self._update_my_players(req, "myteamPlayer")
        self._recreate_enemy_players(req, "opponentPlayer")

    def _recreate_my_flags(self, req: Dict, flag_key: str) -> None:
        """根据前端数组重新创建己方旗帜"""
        flag_data_list = req.get(flag_key, [])
        my_team = self.world._get_my_team()
        self.world.my_flags.clear()

        for index, f_data in enumerate(flag_data_list):
            flag_id = f"FLAG_{my_team.value}_{index}"
            flag_pos = Position(f_data["posX"], f_data["posY"])
            flag = Flag(flag_id, my_team, flag_pos)
            flag.update_from_dict(f_data)
            self.world.my_flags[flag_id] = flag

    def _update_enemy_flags(self, req: Dict, flag_key: str) -> None:
        """更新敌方旗帜状态"""
        flag_data_list = req.get(flag_key, [])
        enemy_team = self.world._get_my_team().get_enemy()

        for index, f_data in enumerate(flag_data_list):
            flag_id = f"FLAG_{enemy_team.value}_{index}"
            flag = self.world.enemy_flags.get(flag_id)
            if flag:
                flag.update_from_dict(f_data)

    def _update_my_players(self, req: Dict, player_key: str) -> None:
        """更新我方玩家状态"""
        my_team = self.world._get_my_team()
        for p_data in req.get(player_key, []):
            p_data["team"] = my_team.value
            player = self.world.my_players.get(p_data["name"])
            if player:
                player.update_from_dict(p_data, self.world.enemy_flags)

    def _recreate_enemy_players(self, req: Dict, player_key: str) -> None:
        """根据前端数组重新创建敌方玩家"""
        enemy_team = self.world._get_my_team().get_enemy()
        enemy_base_area = self.world.map.get_team_target_area(enemy_team)
        self.world.enemy_players.clear()

        for p_data in req.get(player_key, []):
            p_data["team"] = enemy_team.value
            player_name = p_data["name"]
            player_pos = Position(p_data["posX"], p_data["posY"])
            player = Player(player_name, enemy_team, player_pos, self.world)

            if enemy_base_area:
                player.set_base_area(enemy_base_area)

            player.update_from_dict(p_data, self.world.my_flags)
            self.world.enemy_players[player_name] = player
