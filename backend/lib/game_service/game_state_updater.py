"""
游戏状态更新器
负责更新游戏状态（玩家、旗帜等）
"""

from typing import Dict, Optional, Tuple
from ..data_models import Team, Position, Player, Flag


class GameStateUpdater:
    """游戏状态更新器：更新游戏状态"""
    
    def __init__(self, world):
        self.world = world
    
    def _find_or_create_flag(self, team: Team, f_data: Dict) -> Flag:
        """
        查找或创建旗帜 - 严格确保旗帜归属正确
        
        Args:
            f_data: 旗帜数据字典
            team: 旗帜归属队伍（myteamFlag -> my_team, opponentFlag -> enemy_team）
        """
        flag_pos = Position(f_data["posX"], f_data["posY"])
        
        # 首先尝试通过位置和归属精确匹配现有旗帜
        for existing_flag in self.world.flags.values():
            # 必须同时满足：归属正确 AND 位置匹配
            if existing_flag.belongs_to_team(team):
                # 位置匹配：当前位置或原始位置（如果旗帜未被拾取）
                position_matches = (
                    existing_flag.position == flag_pos or 
                    (not existing_flag.is_picked_up and existing_flag.original_position == flag_pos)
                )
                if position_matches:
                    # 更新旗帜状态（不改变归属）
                    existing_flag.update_from_dict(f_data)
                    print(f"✅ [World] 更新旗帜: {existing_flag.flag_id}, 归属: {existing_flag.belongs_to.value}队, 位置: {flag_pos}", flush=True)
                    return existing_flag
        
        # 如果找不到匹配的旗帜，创建新旗帜
        flag_id_counter = len(self.world.flags)
        new_flag = Flag(f"flag_{team.value}_{flag_id_counter}", team, flag_pos)
        new_flag.update_from_dict(f_data)
        self.world.flags[new_flag.flag_id] = new_flag
        print(f"🚩 [World] 创建新旗帜: {new_flag.flag_id}, 归属: {new_flag.belongs_to.value}队, 位置: {flag_pos}", flush=True)
        return new_flag
    
    def _update_flags_from_request(self, req: Dict) -> None:
        """更新旗帜状态（入口方法）"""
        # 分别处理己方和敌方旗帜，内部通过 my_team_name 计算队伍归属
        self._update_myteam_flags(req)
        self._update_opponent_flags(req)
    
    def _update_myteam_flags(self, req: Dict) -> None:
        """
        更新己方旗帜状态
        
        Args:
            req: 请求字典
        """
        my_team = Team.from_name(self.world.my_team_name)
        
        myteam_flags_data = req.get("myteamFlag", [])
        
        if not myteam_flags_data:
            print(f"ℹ️  [World] 请求中没有己方旗帜数据", flush=True)
            return
        
        for f_data in myteam_flags_data:
            # 确保旗帜归属正确（myteamFlag 必须属于 my_team）
            self._find_or_create_flag(my_team, f_data)
    
    def _update_opponent_flags(self, req: Dict) -> None:
        """
        更新敌方旗帜状态
        
        Args:
            req: 请求字典
        """
        my_team = Team.from_name(self.world.my_team_name)
        enemy_team = my_team.get_enemy()
        
        opponent_flags_data = req.get("opponentFlag", [])
        
        if not opponent_flags_data:
            print(f"ℹ️  [World] 请求中没有敌方旗帜数据", flush=True)
            return
        
        for f_data in opponent_flags_data:
            # 确保旗帜归属正确（opponentFlag 必须属于 enemy_team）
            self._find_or_create_flag(enemy_team, f_data)
    
    def _create_player_from_dict(self, team: Team, p_data: Dict) -> Player:
        """从字典创建玩家对象"""
        name = p_data.get("name")
        
        pos = Position(p_data["posX"], p_data["posY"])
        player = Player(name, team, pos, self.world)
        
        # 设置基地区域
        base_area = self.world.get_team_target_area(team)
        if base_area:
            player.set_base_area(base_area)
        
        player.update_from_dict(p_data, self.world.flags)
        return player
    
    def _update_players_from_request(self, req: Dict) -> bool:
        """更新玩家状态（入口方法）"""
        # 分别处理己方和敌方玩家，内部通过 my_team_name 计算队伍归属
        myteam_success = self._update_myteam_players(req)
        opponent_success = self._update_opponent_players(req)
        return myteam_success and opponent_success
    
    def _update_myteam_players(self, req: Dict) -> bool:
        """
        更新己方玩家状态
        
        Args:
            req: 请求字典
        """
        my_team = Team.from_name(self.world.my_team_name)
        myteam_players_data = req.get("myteamPlayer", [])
        
        if not myteam_players_data:
            print(f"ℹ️  [World] 请求中没有己方玩家数据", flush=True)
            return True
        
        for p_data in myteam_players_data:
            # 直接根据 my_team_name 强制设置 team，避免混淆
            p_data["team"] = my_team.value
            
            if not self._process_player_data(my_team, p_data):
                continue
        
        # 这里不再做额外验证，上层 world 逻辑和物理规则已经保证一致性
        return True
    
    def _update_opponent_players(self, req: Dict) -> bool:
        """
        更新敌方玩家状态
        
        Args:
            req: 请求字典
        """
        my_team = Team.from_name(self.world.my_team_name)
        enemy_team = my_team.get_enemy()
        
        opponent_players_data = req.get("opponentPlayer", [])
        
        if not opponent_players_data:
            print(f"ℹ️  [World] 请求中没有敌方玩家数据", flush=True)
            return True
        
        for p_data in opponent_players_data:
            # 直接根据 my_team_name 推导敌方队伍并强制设置 team
            p_data["team"] = enemy_team.value
            
            if not self._process_player_data(enemy_team, p_data):
                continue
        
        # 这里不再做额外验证，上层 world 逻辑和物理规则已经保证一致性
        return True
    
    def _process_player_data(self, team: Team, p_data: Dict) -> bool:
        """
        处理单个玩家数据
        
        Args:
            team:   调用方传入的队伍（己方或敌方），用于逻辑上的归属判断
            p_data: 玩家数据字典（team 字段已被调用方强制设置正确）
        """
        name = p_data.get("name")
        if not name:
            print(f"⚠️  [World] 玩家数据缺少 name 字段，跳过: {p_data}", flush=True)
            return False
        
        # 如果玩家不存在，直接基于传入的 team 创建
        if name not in self.world.players:
            self.world.players[name] = self._create_player_from_dict(team, p_data)
            return True
        
        # 玩家已存在，直接按传入的 team 更新
        player = self.world.players[name]
        
        # 确保玩家有基地信息
        if not player.base_area:
            base_area = self.world.get_team_target_area(team)
            if base_area:
                player.set_base_area(base_area)
        
        # 更新玩家状态
        player.update_from_dict(p_data, self.world.flags)
        
        return True
    
    def _get_teams(self) -> Tuple[Optional[Team], Optional[Team]]:
        """
        获取己方和敌方队伍
        
        要求：
        - my_team_name 必须是有效的队伍标识（L 或 R）
        - 如果无法解析，直接抛出异常（这是严重配置错误）
        """
        my_team = Team.from_name(self.world.my_team_name)
        enemy_team = my_team.get_enemy()
        return my_team, enemy_team

