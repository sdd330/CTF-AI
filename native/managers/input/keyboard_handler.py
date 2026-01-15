"""
键盘输入策略
处理键盘按键映射和方向输入
"""

import pygame
from typing import Optional, Set, Dict
from ...utils import Direction
from .input_strategy import InputStrategy


class KeyboardInputStrategy(InputStrategy):
    """键盘输入策略"""

    def __init__(self, key_mapping: Optional[Dict[int, Direction]] = None):
        """
        初始化键盘输入策略

        Args:
            key_mapping: 按键映射，格式为 {pygame.K_xxx: Direction}
                        如果为None，使用默认映射（WASD + 方向键）
        """
        if key_mapping is None:
            # 默认按键映射
            self.key_mapping = {
                pygame.K_w: Direction.UP,
                pygame.K_s: Direction.DOWN,
                pygame.K_a: Direction.LEFT,
                pygame.K_d: Direction.RIGHT,
                pygame.K_UP: Direction.UP,
                pygame.K_DOWN: Direction.DOWN,
                pygame.K_LEFT: Direction.LEFT,
                pygame.K_RIGHT: Direction.RIGHT,
            }
        else:
            self.key_mapping = key_mapping

        self.pressed_keys: Set[int] = set()

    def handle_key_down(self, key: int):
        """
        处理按键按下事件

        Args:
            key: 按键代码
        """
        if key in self.key_mapping:
            self.pressed_keys.add(key)

    def handle_key_up(self, key: int):
        """
        处理按键释放事件

        Args:
            key: 按键代码
        """
        if key in self.key_mapping:
            self.pressed_keys.discard(key)

    def get_direction(self) -> Direction:
        """获取当前输入方向（优先级：左 > 右 > 上 > 下）"""
        # 先检查模拟按键状态（pressed_keys）
        # 按优先级检查方向键
        if pygame.K_LEFT in self.pressed_keys or pygame.K_a in self.pressed_keys:
            return Direction.LEFT
        if pygame.K_RIGHT in self.pressed_keys or pygame.K_d in self.pressed_keys:
            return Direction.RIGHT
        if pygame.K_UP in self.pressed_keys or pygame.K_w in self.pressed_keys:
            return Direction.UP
        if pygame.K_DOWN in self.pressed_keys or pygame.K_s in self.pressed_keys:
            return Direction.DOWN

        return Direction.STAY

    def update(self, delta_time: int):
        """更新输入状态（键盘输入不需要特殊更新逻辑）"""
        pass
