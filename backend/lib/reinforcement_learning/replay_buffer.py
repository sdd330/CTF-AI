"""
经验回放缓冲区
支持标准经验回放和优先经验回放（Prioritized Experience Replay, PER）
"""

import random
import torch
import numpy as np
from collections import deque, namedtuple
from typing import Tuple, Optional

# 经验元组
Experience = namedtuple('Experience', ['state', 'action', 'reward', 'next_state', 'done'])


class ReplayBuffer:
    """标准经验回放缓冲区"""
    
    def __init__(self, capacity=10000):
        self.buffer = deque(maxlen=capacity)
    
    def push(self, state, action, reward, next_state, done):
        """添加经验"""
        experience = Experience(state, action, reward, next_state, done)
        self.buffer.append(experience)
    
    def sample(self, batch_size):
        """采样批次"""
        batch = random.sample(self.buffer, min(batch_size, len(self.buffer)))
        
        # 先转换为numpy数组，再转换为tensor，避免性能警告
        states = torch.FloatTensor(np.array([e.state for e in batch]))
        actions = torch.LongTensor(np.array([e.action for e in batch]))
        rewards = torch.FloatTensor(np.array([e.reward for e in batch]))
        next_states = torch.FloatTensor(np.array([e.next_state for e in batch]))
        dones = torch.BoolTensor(np.array([e.done for e in batch]))
        
        return states, actions, rewards, next_states, dones
    
    def __len__(self):
        return len(self.buffer)


class PrioritizedReplayBuffer:
    """
    优先经验回放缓冲区（Prioritized Experience Replay）
    根据TD误差的绝对值来优先采样重要的经验
    """
    
    def __init__(self, capacity=10000, alpha=0.6, beta=0.4, beta_increment=1e-6):
        """
        初始化优先经验回放缓冲区
        
        Args:
            capacity: 缓冲区容量
            alpha: 优先级指数（0=均匀采样，1=完全按优先级）
            beta: 重要性采样指数（用于偏差校正，从beta开始逐渐增加到1.0）
            beta_increment: beta的增量
        """
        self.capacity = capacity
        self.alpha = alpha
        self.beta = beta
        self.beta_increment = beta_increment
        self.max_beta = 1.0
        
        # 使用numpy数组存储经验，提高效率
        self.buffer = []
        self.priorities = np.zeros((capacity,), dtype=np.float32)
        self.position = 0
        self.size = 0
    
    def push(self, state, action, reward, next_state, done, td_error: Optional[float] = None):
        """
        添加经验
        
        Args:
            state: 状态
            action: 动作
            reward: 奖励
            next_state: 下一状态
            done: 是否结束
            td_error: TD误差（如果为None，则使用最大优先级）
        """
        experience = Experience(state, action, reward, next_state, done)
        
        # 计算优先级（使用TD误差的绝对值）
        if td_error is None:
            priority = 1.0  # 新经验的初始优先级
        else:
            priority = (abs(td_error) + 1e-6) ** self.alpha
        
        if self.size < self.capacity:
            self.buffer.append(experience)
            self.size += 1
        else:
            self.buffer[self.position] = experience
        
        self.priorities[self.position] = priority
        self.position = (self.position + 1) % self.capacity
    
    def sample(self, batch_size) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, 
                                          torch.Tensor, torch.Tensor, torch.Tensor, np.ndarray]:
        """
        采样批次（带重要性采样权重）
        
        Returns:
            states, actions, rewards, next_states, dones, weights, indices
        """
        if self.size < batch_size:
            batch_size = self.size
        
        # 计算采样概率
        priorities = self.priorities[:self.size]
        probabilities = priorities / priorities.sum()
        
        # 根据概率采样
        indices = np.random.choice(self.size, batch_size, p=probabilities)
        
        # 计算重要性采样权重
        weights = (self.size * probabilities[indices]) ** (-self.beta)
        weights = weights / weights.max()  # 归一化
        
        # 更新beta
        self.beta = min(self.beta + self.beta_increment, self.max_beta)
        
        # 提取批次
        batch = [self.buffer[idx] for idx in indices]
        
        # 转换为tensor
        states = torch.FloatTensor(np.array([e.state for e in batch]))
        actions = torch.LongTensor(np.array([e.action for e in batch]))
        rewards = torch.FloatTensor(np.array([e.reward for e in batch]))
        next_states = torch.FloatTensor(np.array([e.next_state for e in batch]))
        dones = torch.BoolTensor(np.array([e.done for e in batch]))
        weights = torch.FloatTensor(weights)
        
        return states, actions, rewards, next_states, dones, weights, indices
    
    def update_priorities(self, indices: np.ndarray, td_errors: np.ndarray):
        """
        更新经验的优先级
        
        Args:
            indices: 经验索引
            td_errors: TD误差
        """
        priorities = (np.abs(td_errors) + 1e-6) ** self.alpha
        for idx, priority in zip(indices, priorities):
            self.priorities[idx] = priority
    
    def __len__(self):
        return self.size
