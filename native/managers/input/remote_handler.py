"""
远程控制输入策略
处理来自远程（如AI代理或网络）的控制输入
"""

from typing import Optional
from ...utils import Direction
from .input_strategy import InputStrategy


class RemoteInputStrategy(InputStrategy):
    """远程控制输入策略"""

    def __init__(self):
        """初始化远程控制输入策略"""
        self.remote_control: Optional[Direction] = None

    def set_remote_control(self, direction: Optional[Direction]):
        """
        设置远程控制方向

        Args:
            direction: 远程控制方向，None表示清除
        """
        self.remote_control = direction

    def get_direction(self) -> Direction:
        """获取远程控制方向"""
        return self.remote_control if self.remote_control else Direction.STAY

    def update(self, delta_time: int):
        """更新输入状态（远程输入不需要特殊更新逻辑）"""
        pass
