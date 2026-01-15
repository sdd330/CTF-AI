"""
强化学习模块
提供DQN（Deep Q-Network）实现用于CTF游戏
"""

from .agent import DQNAgent
from .network import DQN
from .replay_buffer import ReplayBuffer, PrioritizedReplayBuffer
from .state_extractor import extract_state_features
from .reward_calculator import calculate_reward
from .scheduler import predict_schedule
from .training_monitor import TrainingMonitor

# Gymnasium环境包装器（必需依赖）
from .gym_env import CTFGymEnv
from .gym_env_multiagent import CTFMultiAgentGymEnv


# 常量
DEFAULT_STATE_DIM = 19  # 5(玩家) + 6(目标) + 4(对手) + 4(全局) = 19
DEFAULT_ACTION_DIM = 3  # defence, scoring, saving


__all__ = [
    'DQNAgent',
    'DQN',
    'ReplayBuffer',
    'PrioritizedReplayBuffer',
    'TrainingMonitor',
    'CTFGymEnv',
    'CTFMultiAgentGymEnv',
    'extract_state_features',
    'calculate_reward',
    'predict_schedule',
    'DEFAULT_STATE_DIM',
    'DEFAULT_ACTION_DIM',
]
