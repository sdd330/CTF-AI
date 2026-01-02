"""
玩家类定义
定义玩家相关的数据结构和操作
"""

from typing import Optional, Dict, List, TYPE_CHECKING
from ..enums import Team, PlayerState, Direction, Action, Strategy
from ..position import Position
from ..areas import TargetArea

if TYPE_CHECKING:
    from ...game_engine import World
    from ...map_service import GameMap
    from ..flag import Flag
    from .player_behavior import PlayerBehavior
    from .player_state import PlayerStateManager
    from .player_actions import PlayerActions
    from .player_flag_manager import PlayerFlagManager
    from .player_prison_manager import PlayerPrisonManager
    from .player_data_updater import PlayerDataUpdater
    from .player_team_relations import PlayerTeamRelations
    from .player_checker import PlayerChecker


class Player:
    """
    玩家类 - 四核心接口设计
    
    设计理念：
    - 对外暴露四个核心接口：plan、move、check、action
    - 隐藏内部复杂实现，外部只需调用简单方法
    - 内部使用组合模式，将职责委托给专门的管理器
    
    核心接口（极简）：
    1. plan() - 规划下一步行动
    2. move() - 移动
    3. check() - 检查（状态、关系、条件等）
    4. action() - 执行动作
    
    内部实现（私有）：
    - 使用多个管理器处理不同职责（状态、动作、旗帜、监狱等）
    - 所有管理器都是私有属性，外部不可访问
    - 通过四个核心接口统一对外暴露功能
    """
    
    def __init__(self, name: str, team: Team, position: Position, world: 'World'):
        """
        初始化玩家
        
        Args:
            name: 玩家名称
            team: 所属队伍（必须是 Team.LEFT 或 Team.RIGHT）
            position: 初始位置
            world: World对象（必需，作为上下文）
            
        Raises:
            ValueError: 如果参数无效
            TypeError: 如果参数类型错误
        """
        # 参数验证
        if not name:
            raise ValueError("Player name cannot be empty")
        if not isinstance(position, Position):
            raise TypeError(f"Position must be Position object, got {type(position)}")
        if not isinstance(team, Team):
            raise TypeError(f"Team must be Team enum, got {type(team)}")
        if team not in (Team.LEFT, Team.RIGHT):
            raise ValueError(f"Player team must be Team.LEFT or Team.RIGHT, got {team}")
        if world is None:
            raise ValueError("world is required and cannot be None")
        
        # 直接设置所有属性
        self.name = name
        self.team = team
        self.position = position
        self.world: 'World' = world
        self.state = PlayerState.FREE
        self.carried_flag: Optional['Flag'] = None
        self.prison_time_left: int = 0
        self.prison_duration: int = 20000
        self.base_area: Optional[TargetArea] = None
        
        # 内部管理器（私有，延迟初始化，避免循环导入）
        self.__behavior: Optional['PlayerBehavior'] = None
        self.__state_manager: Optional['PlayerStateManager'] = None
        self.__actions: Optional['PlayerActions'] = None
        self.__flag_manager: Optional['PlayerFlagManager'] = None
        self.__prison_manager: Optional['PlayerPrisonManager'] = None
        self.__data_updater: Optional['PlayerDataUpdater'] = None
        self.__team_relations: Optional['PlayerTeamRelations'] = None
        self.__checker: Optional['PlayerChecker'] = None
    
    # ========== 私有属性访问器（内部使用） ==========
    
    @property
    def _behavior(self) -> 'PlayerBehavior':
        """获取行为对象（延迟初始化，私有）"""
        if self.__behavior is None:
            from .player_behavior import PlayerBehavior
            self.__behavior = PlayerBehavior(self)
        return self.__behavior
    
    @property
    def _state_manager(self) -> 'PlayerStateManager':
        """获取状态管理器（延迟初始化，私有）"""
        if self.__state_manager is None:
            from .player_state import PlayerStateManager
            self.__state_manager = PlayerStateManager(self)
        return self.__state_manager
    
    @property
    def _actions(self) -> 'PlayerActions':
        """获取动作执行器（延迟初始化，私有）"""
        if self.__actions is None:
            from .player_actions import PlayerActions
            self.__actions = PlayerActions(self)
        return self.__actions
    
    @property
    def _flag_manager(self) -> 'PlayerFlagManager':
        """获取旗帜管理器（延迟初始化，私有）"""
        if self.__flag_manager is None:
            from .player_flag_manager import PlayerFlagManager
            self.__flag_manager = PlayerFlagManager(self)
        return self.__flag_manager
    
    @property
    def _prison_manager(self) -> 'PlayerPrisonManager':
        """获取监狱管理器（延迟初始化，私有）"""
        if self.__prison_manager is None:
            from .player_prison_manager import PlayerPrisonManager
            self.__prison_manager = PlayerPrisonManager(self)
        return self.__prison_manager
    
    @property
    def _data_updater(self) -> 'PlayerDataUpdater':
        """获取数据更新器（延迟初始化，私有）"""
        if self.__data_updater is None:
            from .player_data_updater import PlayerDataUpdater
            self.__data_updater = PlayerDataUpdater(self)
        return self.__data_updater
    
    @property
    def _team_relations(self) -> 'PlayerTeamRelations':
        """获取队伍关系管理器（延迟初始化，私有）"""
        if self.__team_relations is None:
            from .player_team_relations import PlayerTeamRelations
            self.__team_relations = PlayerTeamRelations(self)
        return self.__team_relations
    
    @property
    def _checker(self) -> 'PlayerChecker':
        """获取检查器（延迟初始化，私有）"""
        if self.__checker is None:
            from .player_checker import PlayerChecker
            self.__checker = PlayerChecker(self)
        return self.__checker
    
    # ========== 核心接口 1: plan - 规划 ==========
    
    def plan(self, suggested_strategy: Optional[Strategy] = None) -> Optional[Direction]:
        """
        规划玩家下一步行动
        
        这是 Player 的核心接口之一，隐藏了内部复杂的行为决策逻辑。
        
        Args:
            suggested_strategy: 可选的外部建议策略（用于 RL 训练）
            
        Returns:
            方向枚举，如果无法规划则返回None
        """
        return self._behavior.plan(suggested_strategy)
    
    # ========== 核心接口 2: move - 移动 ==========
    
    def move(self, direction: Direction) -> bool:
        """
        移动玩家
        
        Args:
            direction: 移动方向
            
        Returns:
            是否成功移动
        """
        if self._state_manager.is_in_prison:
            return False
        
        if direction == Direction.STAY:
            return True
        
        new_x, new_y = self.position.x, self.position.y
        if direction == Direction.UP:
            new_y -= 1
        elif direction == Direction.DOWN:
            new_y += 1
        elif direction == Direction.LEFT:
            new_x -= 1
        elif direction == Direction.RIGHT:
            new_x += 1
        else:
            return False
        
        new_position = Position(new_x, new_y)
        if self.world:
            if not self.world.is_valid_position(new_position):
                return False
        
        self.position = new_position
        
        # 记录移动行为（行动）
        if direction != Direction.STAY:
            self._behavior.stats.record_movement(direction, 1.0)
        
        return True
    
    # ========== 核心接口 3: check - 检查 ==========
    
    def check(self, check_type: str, **kwargs) -> bool:
        """
        检查玩家状态、关系、条件等
        
        统一的检查接口，支持多种检查类型：
        - "state": 状态检查（is_free, is_in_prison, has_flag, is_in_base）
        - "relation": 关系检查（is_enemy_of, is_teammate_of, belongs_to_team）
        - "position": 位置检查（find_closest_opponent, find_closest_flag）
        
        使用示例：
            player.check("state", state="is_free")
            player.check("relation", relation="is_enemy_of", other_player=other)
            player.check("position", position="find_closest_opponent", opponents=opponents)
        
        Args:
            check_type: 检查类型 ("state" | "relation" | "position")
            **kwargs: 检查参数
        
        Returns:
            检查结果（bool）
        """
        return self._checker.check(check_type, **kwargs)
    
    # ========== 核心接口 4: action - 动作 ==========
    
    def action(self, action_type: Action, **kwargs) -> bool:
        """
        执行玩家动作
        
        Args:
            action_type: 动作类型
            **kwargs: 额外参数
                - flag: Flag对象（用于PICKUP_FLAG）
                - target: Player对象（用于TAG_ENEMY）
                - teammate: Player对象（用于RESCUE_TEAMMATE）
        
        Returns:
            动作是否成功执行
        """
        if action_type == Action.PICKUP_FLAG:
            return self._actions.execute_pickup_flag(kwargs.get('flag'))
        elif action_type == Action.DROP_FLAG:
            return self._actions.execute_drop_flag(kwargs.get('drop_position'))
        elif action_type == Action.SCORE_FLAG:
            return self._actions.execute_score_flag()
        elif action_type == Action.TAG_ENEMY:
            return self._actions.execute_tag_enemy(kwargs.get('target'))
        elif action_type == Action.RESCUE_TEAMMATE:
            return self._actions.execute_rescue_teammate(kwargs.get('teammate'))
        else:
            print(f"⚠️  [Player.{self.name}] 不支持的动作类型: {action_type}", flush=True)
            return False
    
    # ========== 便捷接口（基于 check() 方法的便捷访问） ==========
    
    @property
    def is_free(self) -> bool:
        """是否自由（不在监狱中）"""
        return self.check("state", state="is_free")
    
    @property
    def is_in_prison(self) -> bool:
        """是否在监狱"""
        return self.check("state", state="is_in_prison")
    
    @property
    def has_flag(self) -> bool:
        """是否持有旗帜"""
        return self.check("state", state="has_flag")
    
    def is_in_base(self) -> bool:
        """检查玩家是否在己方基地内"""
        return self.check("state", state="is_in_base")
    
    def belongs_to_team(self, team: Team) -> bool:
        """检查玩家是否属于指定队伍"""
        return self.check("relation", relation="belongs_to_team", team=team)
    
    def is_enemy_of(self, other_player: 'Player') -> bool:
        """检查是否是另一个玩家的敌人"""
        return self.check("relation", relation="is_enemy_of", other_player=other_player)
    
    def is_teammate_of(self, other_player: 'Player') -> bool:
        """检查是否是另一个玩家的队友"""
        return self.check("relation", relation="is_teammate_of", other_player=other_player)
    
    def is_enemy_team(self, team: Team) -> bool:
        """检查是否是指定队伍的敌人"""
        return self.check("relation", relation="is_enemy_team", team=team)
    
    def is_my_team(self, team: Team) -> bool:
        """检查是否是指定队伍的己方"""
        return self.check("relation", relation="is_my_team", team=team)
    
    def find_closest_opponent(self, opponents: List['Player']) -> Optional['Player']:
        """找到最近的敌人"""
        return self._team_relations.find_closest_opponent(opponents)
    
    def find_closest_flag(self, flags: List['Flag']) -> Optional['Flag']:
        """找到最近的旗帜"""
        return self._team_relations.find_closest_flag(flags)
    
    # ========== 内部方法（系统使用） ==========
    
    def set_base_area(self, base_area: TargetArea) -> None:
        """设置己方基地区域（内部方法）"""
        self._state_manager.set_base_area(base_area)
    
    def update_from_dict(self, p_data: Dict, flags: Dict[str, 'Flag']) -> None:
        """从字典更新玩家状态（内部方法）"""
        self._data_updater.update_from_dict(p_data, flags)
    
    def send_to_prison(self, prison_position: Position) -> None:
        """送入监狱（内部方法）"""
        self._prison_manager.send_to_prison(prison_position)
    
    def _rescue(self) -> None:
        """内部方法：被救援"""
        self._prison_manager.rescue()
    
    def update_prison_time(self, delta_time: int) -> None:
        """更新监狱时间（内部方法）"""
        self._state_manager.update_prison_time(delta_time)
    
    # ========== 序列化 ==========
    
    def to_dict(self) -> Dict:
        """转换为字典（用于API）"""
        return {
            "name": self.name,
            "team": self.team.value,
            "posX": self.position.x,
            "posY": self.position.y,
            "hasFlag": self.has_flag,
            "inPrison": self.is_in_prison,
            "inPrisonTimeLeft": self.prison_time_left,
            "inPrisonDuration": self.prison_duration
        }
    
    def __repr__(self) -> str:
        """字符串表示"""
        return (
            f"Player(name={self.name}, team={self.team.value}, "
            f"position={self.position}, state={self.state.value}, "
            f"has_flag={self.has_flag})"
        )
