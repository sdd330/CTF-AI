"""
玩家行为类
负责玩家的决策和行为执行逻辑
封装玩家的：举动、表现、行动、举止、态度
"""

from typing import Optional, TYPE_CHECKING
from ..enums import Strategy, Direction

if TYPE_CHECKING:
    from .player import Player
    from .player_behavior_stats import PlayerBehaviorStats
    from .player_strategy_planner import PlayerStrategyPlanner
    from .player_strategy_executor import PlayerStrategyExecutor


class PlayerBehavior:
    """
    玩家行为类 - 负责玩家的决策和行为执行
    
    封装内容：
    1. 举动（Actions）- 玩家执行的具体动作
    2. 表现（Performance）- 玩家的行为统计数据
    3. 行动（Movements）- 玩家的移动行为
    4. 举止（Conduct）- 玩家的行为模式和风格
    5. 态度（Attitude）- 玩家的行为倾向和偏好
    
    设计原则：
    1. 单一职责：只负责行为逻辑，不管理状态
    2. 依赖注入：通过 Player 对象访问状态和 World
    3. 可测试性：行为逻辑独立，易于单元测试
    """
    
    def __init__(self, player: 'Player'):
        """初始化行为对象"""
        self.player = player
        
        # 初始化各个组件（延迟初始化，避免循环导入）
        self._stats: Optional['PlayerBehaviorStats'] = None
        self._planner: Optional['PlayerStrategyPlanner'] = None
        self._executor: Optional['PlayerStrategyExecutor'] = None
    
    @property
    def stats(self) -> 'PlayerBehaviorStats':
        """获取行为统计器（延迟初始化）"""
        if self._stats is None:
            from .player_behavior_stats import PlayerBehaviorStats
            self._stats = PlayerBehaviorStats(self.player)
        return self._stats
    
    @property
    def planner(self) -> 'PlayerStrategyPlanner':
        """获取策略规划器（延迟初始化）"""
        if self._planner is None:
            from .player_strategy_planner import PlayerStrategyPlanner
            self._planner = PlayerStrategyPlanner(self.player)
        return self._planner
    
    @property
    def executor(self) -> 'PlayerStrategyExecutor':
        """获取策略执行器（延迟初始化）"""
        if self._executor is None:
            from .player_strategy_executor import PlayerStrategyExecutor
            self._executor = PlayerStrategyExecutor(self.player)
        return self._executor
    
    def plan(self, suggested_strategy: Optional[Strategy] = None) -> Optional[Direction]:
        """
        规划玩家下一步行动 - 自驱动决策方法
        
        Args:
            suggested_strategy: 可选的外部建议策略（用于 RL 训练）
            
        Returns:
            方向枚举，如果无法规划则返回None
        """
        # 如果玩家在监狱中，无法行动，不能规划路径，忽略执行任何策略
        if self.player.is_in_prison:
            return Direction.STAY
        
        # 如果玩家持有旗帜，立即返回基地（最高优先级）
        if self.player.has_flag:
            return self.executor.return_to_base()
        
        # 根据 world 状态生成策略（自驱动）
        if suggested_strategy is not None:
            strategy = suggested_strategy
        else:
            strategy = self.planner.generate_strategy()
        
        # 记录策略使用（举止）
        self.stats.record_strategy_usage(strategy)
        
        # 根据策略执行相应的行为
        if strategy == Strategy.SAVING:
            direction = self.executor.execute_saving_strategy()
            # 如果没有队友在监狱，回退到抢旗策略
            if direction is None:
                return self.executor.execute_scoring_strategy()
            return direction
        elif strategy == Strategy.DEFENCE:
            direction = self.executor.execute_defence_strategy()
            # 如果没有敌人在领地，回退到抢旗策略
            if direction is None:
                return self.executor.execute_scoring_strategy()
            return direction
        elif strategy == Strategy.SCORING:
            return self.executor.execute_scoring_strategy()
        else:
            return Direction.STAY
    
    # ========== 行为统计接口（委托给 stats） ==========
    
    def record_action(self, action) -> None:
        """记录玩家的举动"""
        self.stats.record_action(action)
    
    def record_movement(self, direction, distance: float = 1.0) -> None:
        """记录玩家的行动（移动）"""
        self.stats.record_movement(direction, distance)
    
    def record_capture(self) -> None:
        """记录被捕获"""
        self.stats.record_capture()
    
    def get_action_count(self, action) -> int:
        """获取某个动作的执行次数"""
        return self.stats.get_action_count(action)
    
    def get_recent_actions(self, count: int = 10):
        """获取最近的动作历史"""
        return self.stats.get_recent_actions(count)
    
    def get_movement_statistics(self):
        """获取移动统计信息"""
        return self.stats.get_movement_statistics()
    
    def get_recent_movements(self, count: int = 10):
        """获取最近的移动历史"""
        return self.stats.get_recent_movements(count)
    
    def get_movement_pattern(self):
        """分析移动模式"""
        return self.stats.get_movement_pattern()
    
    def get_performance_summary(self):
        """获取表现摘要"""
        return self.stats.get_performance_summary()
    
    def get_attitude(self):
        """获取玩家态度"""
        return self.stats.get_attitude()
    
    def set_attitude(self, **kwargs) -> None:
        """设置玩家态度"""
        self.stats.set_attitude(**kwargs)
    
    def adjust_attitude_by_experience(self) -> None:
        """根据经验调整态度"""
        self.stats.adjust_attitude_by_experience()
    
    def analyze_behavior_pattern(self):
        """分析行为模式（举止）"""
        return self.stats.analyze_behavior_pattern()
    
    def update_behavior_pattern(self, pattern_name: str, value: int = 1) -> None:
        """更新行为模式"""
        self.stats.update_behavior_pattern(pattern_name, value)
    
    def return_to_base(self) -> Direction:
        """玩家持有旗帜时，立即返回基地"""
        return self.executor.return_to_base()
