"""
玩家检查器类
负责处理玩家的各种检查逻辑
"""

from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from .player import Player


class PlayerChecker:
    """玩家检查器 - 负责处理玩家的各种检查逻辑"""
    
    def __init__(self, player: 'Player'):
        self.player = player
    
    def check(self, check_type: str, **kwargs) -> bool:
        """
        统一的检查接口
        
        Args:
            check_type: 检查类型 ("state" | "relation" | "position")
            **kwargs: 检查参数
        
        Returns:
            检查结果（bool）
        """
        handlers = {
            "state": self._check_state,
            "relation": self._check_relation,
            "position": self._check_position,
        }
        
        handler = handlers.get(check_type)
        if not handler:
            raise ValueError(
                f"未知的检查类型: {check_type}，"
                f"支持的类型: {', '.join(handlers.keys())}"
            )
        
        return handler(**kwargs)
    
    def _check_state(self, **kwargs) -> bool:
        """检查状态"""
        state_name = kwargs.get("state", "")
        state_map = {
            "is_free": lambda: self.player._state_manager.is_free,
            "is_in_prison": lambda: self.player._state_manager.is_in_prison,
            "has_flag": lambda: self.player._state_manager.has_flag,
            "is_in_base": lambda: self.player._state_manager.is_in_base(),
        }
        
        checker = state_map.get(state_name)
        if not checker:
            raise ValueError(f"未知的状态检查类型: {state_name}")
        return checker()
    
    def _check_relation(self, **kwargs) -> bool:
        """检查关系"""
        relation_name = kwargs.get("relation", "")
        relation_map = {
            "is_enemy_of": lambda: self.player._team_relations.is_enemy_of(
                self._require_param(kwargs, "other_player", "is_enemy_of")
            ),
            "is_teammate_of": lambda: self.player._team_relations.is_teammate_of(
                self._require_param(kwargs, "other_player", "is_teammate_of")
            ),
            "belongs_to_team": lambda: self.player._team_relations.belongs_to_team(
                self._require_param(kwargs, "team", "belongs_to_team")
            ),
            "is_enemy_team": lambda: self.player._team_relations.is_enemy_team(
                self._require_param(kwargs, "team", "is_enemy_team")
            ),
            "is_my_team": lambda: self.player._team_relations.is_my_team(
                self._require_param(kwargs, "team", "is_my_team")
            ),
        }
        
        checker = relation_map.get(relation_name)
        if not checker:
            raise ValueError(f"未知的关系检查类型: {relation_name}")
        return checker()
    
    def _check_position(self, **kwargs) -> bool:
        """检查位置"""
        position_name = kwargs.get("position", "")
        position_map = {
            "find_closest_opponent": lambda: self.player._team_relations.find_closest_opponent(
                kwargs.get("opponents", [])
            ) is not None,
            "find_closest_flag": lambda: self.player._team_relations.find_closest_flag(
                kwargs.get("flags", [])
            ) is not None,
        }
        
        checker = position_map.get(position_name)
        if not checker:
            raise ValueError(f"未知的位置检查类型: {position_name}")
        return checker()
    
    def _require_param(self, kwargs: Dict, param_name: str, check_name: str):
        """要求参数存在"""
        value = kwargs.get(param_name)
        if not value:
            raise ValueError(f"{check_name} 需要 {param_name} 参数")
        return value
