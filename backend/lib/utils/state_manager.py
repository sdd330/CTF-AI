"""
状态管理模块
管理游戏状态、玩家分配、目标追踪等
"""

from typing import Dict, Set, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..data_models import Player, Flag, Position


class StateManager:
    """状态管理器"""
    
    def __init__(self):
        """初始化状态管理器"""
        self.player_to_enemy_assignments: Dict[str, str] = {}
        from ..data_models import Position
        self.player_to_flag_assignments: Dict[str, Position] = {}
        self.player_to_rescue_assignments: Dict[str, Position] = {}
        self.player_defence_targets: Dict[str, str] = {}  # {player_name: enemy_name}
        self.player_flag_targets: Dict[str, Position] = {}  # {player_name: (flag_posX, flag_posY)}
        self.assigned_enemies: Set[str] = set()
        self.assigned_flags: Set[Position] = set()
        self.player_last_positions: Dict[str, List[Position]] = {}  # {player_name: [last_pos1, last_pos2, ...]}
        self.player_stuck_count: Dict[str, int] = {}  # {player_name: stuck_count}
    
    def reset(self):
        """重置所有状态"""
        self.player_to_enemy_assignments.clear()
        self.player_to_flag_assignments.clear()
        self.player_to_rescue_assignments.clear()
        self.player_defence_targets.clear()
        self.player_flag_targets.clear()
        self.assigned_enemies.clear()
        self.assigned_flags.clear()
        self.player_last_positions.clear()
        self.player_stuck_count.clear()
    
    def set_defence_target(self, player_name: str, enemy_name: str):
        """设置玩家的防御目标"""
        self.player_defence_targets[player_name] = enemy_name
    
    def get_defence_target(self, player_name: str) -> Optional[str]:
        """获取玩家的防御目标"""
        return self.player_defence_targets.get(player_name)
    
    def clear_defence_target(self, player_name: str):
        """清除玩家的防御目标"""
        if player_name in self.player_defence_targets:
            del self.player_defence_targets[player_name]
    
    def set_flag_target(self, player_name: str, flag_position: 'Position'):
        """设置玩家的旗子目标"""
        self.player_flag_targets[player_name] = flag_position
    
    def get_flag_target(self, player_name: str) -> Optional['Position']:
        """获取玩家的旗子目标"""
        return self.player_flag_targets.get(player_name)
    
    def clear_flag_target(self, player_name: str):
        """清除玩家的旗子目标"""
        if player_name in self.player_flag_targets:
            del self.player_flag_targets[player_name]
    
    def mark_enemy_assigned(self, enemy_name: str):
        """标记敌人已被分配"""
        self.assigned_enemies.add(enemy_name)
    
    def is_enemy_assigned(self, enemy_name: str) -> bool:
        """检查敌人是否已被分配"""
        return enemy_name in self.assigned_enemies
    
    def mark_flag_assigned(self, flag_position: 'Position'):
        """标记旗子已被分配"""
        self.assigned_flags.add(flag_position)
    
    def is_flag_assigned(self, flag_position: 'Position') -> bool:
        """检查旗子是否已被分配"""
        return flag_position in self.assigned_flags
    
    def clear_assignments(self):
        """清除所有分配标记"""
        self.assigned_enemies.clear()
        self.assigned_flags.clear()
    
    def get_unassigned_enemies(self, enemies: list) -> list:
        """获取未分配的敌人列表"""
        return [e for e in enemies if not self.is_enemy_assigned(e.name)]
    
    def get_unassigned_flags(self, flags: list) -> list:
        """获取未分配的旗子列表"""
        return [f for f in flags if not self.is_flag_assigned(f.position)]
    
    def update_player_position(self, player_name: str, position: 'Position'):
        """更新玩家位置，用于检测是否卡住"""
        if player_name not in self.player_last_positions:
            self.player_last_positions[player_name] = []
        
        # 保留最近3个位置
        self.player_last_positions[player_name].append(position)
        if len(self.player_last_positions[player_name]) > 3:
            self.player_last_positions[player_name].pop(0)
    
    def is_player_stuck(self, player_name: str, current_position: 'Position') -> bool:
        """检查玩家是否卡住（在相同或相邻位置来回移动）"""
        if player_name not in self.player_last_positions:
            return False
        
        last_positions = self.player_last_positions[player_name]
        if len(last_positions) < 4:  # 需要至少4个位置才能判断
            return False
        
        # 检查是否在相同位置停留超过3次
        if current_position == last_positions[-1] == last_positions[-2] == last_positions[-3]:
            self.player_stuck_count[player_name] = self.player_stuck_count.get(player_name, 0) + 1
            return self.player_stuck_count[player_name] >= 3
        
        # 检查是否在两个位置之间来回移动（至少3次来回）
        if len(last_positions) >= 4:
            # 检查模式：A -> B -> A -> B
            if (current_position == last_positions[-3] and 
                last_positions[-1] == last_positions[-2] and
                current_position != last_positions[-1]):
                self.player_stuck_count[player_name] = self.player_stuck_count.get(player_name, 0) + 1
                return self.player_stuck_count[player_name] >= 3
        
        # 如果位置有变化，重置卡住计数
        self.player_stuck_count[player_name] = 0
        return False
    
    def clear_stuck_status(self, player_name: str):
        """清除玩家的卡住状态"""
        if player_name in self.player_stuck_count:
            self.player_stuck_count[player_name] = 0
        if player_name in self.player_last_positions:
            self.player_last_positions[player_name].clear()

