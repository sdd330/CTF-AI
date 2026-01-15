"""
输入策略接口和观察者接口
定义输入系统的核心抽象
"""

from abc import ABC, abstractmethod
from ...utils import Direction


class InputObserver(ABC):
    """观察者接口"""

    @abstractmethod
    def on_input_change(self, direction: Direction):
        """
        当输入方向改变时调用

        Args:
            direction: 新的输入方向
        """
        pass


class InputStrategy(ABC):
    """输入策略接口"""

    @abstractmethod
    def get_direction(self) -> Direction:
        """
        获取当前输入方向

        Returns:
            当前方向，如果没有输入返回 Direction.STAY
        """
        pass

    @abstractmethod
    def update(self, delta_time: int):
        """
        更新输入状态

        Args:
            delta_time: 时间增量（毫秒）
        """
        pass
