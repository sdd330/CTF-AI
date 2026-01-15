"""
混合输入策略
组合键盘和远程输入，键盘优先
"""

from ...utils import Direction
from .input_strategy import InputStrategy
from .keyboard_handler import KeyboardInputStrategy
from .remote_handler import RemoteInputStrategy


class HybridInputStrategy(InputStrategy):
    """混合输入策略（键盘优先）"""

    def __init__(
        self,
        keyboard_strategy: KeyboardInputStrategy,
        remote_strategy: RemoteInputStrategy,
    ):
        """
        初始化混合输入策略

        Args:
            keyboard_strategy: 键盘输入策略
            remote_strategy: 远程控制策略
        """
        self.keyboard_strategy = keyboard_strategy
        self.remote_strategy = remote_strategy

    def get_direction(self) -> Direction:
        """获取输入方向（键盘输入优先）"""
        # 键盘输入优先
        keyboard_dir = self.keyboard_strategy.get_direction()
        if keyboard_dir != Direction.STAY:
            return keyboard_dir

        # 如果没有键盘输入，使用远程控制
        return self.remote_strategy.get_direction()

    def update(self, delta_time: int):
        """更新输入状态"""
        self.keyboard_strategy.update(delta_time)
        self.remote_strategy.update(delta_time)
