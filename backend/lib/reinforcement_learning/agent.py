"""
DQN智能体模块
实现深度Q网络智能体的核心功能

支持梯度裁剪、Huber Loss、学习率调度、优先经验回放（PER）
完全基于Gymnasium标准接口，可与stable-baselines3算法配合使用
"""

import torch
import torch.nn as nn
import torch.optim as optim
import random
from typing import Dict, List, Optional

from .network import DQN
from .replay_buffer import ReplayBuffer, PrioritizedReplayBuffer
from .reward_calculator import calculate_reward
from .scheduler import predict_schedule
from .model_persistence import save_model, load_model


class DQNAgent:
    """DQN智能体"""

    def __init__(self, state_dim, action_dim, lr=0.0005, gamma=0.99,
                 epsilon_start=1.0, epsilon_end=0.01, epsilon_decay=0.998,
                 target_update_freq=50, device='cpu', use_double_dqn=True,
                 use_per=False, use_huber_loss=True, grad_clip=10.0,
                 lr_scheduler=None, network_config=None):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.gamma = gamma
        self.epsilon = epsilon_start
        self.epsilon_end = epsilon_end
        self.epsilon_decay = epsilon_decay
        self.target_update_freq = target_update_freq
        self.device = device
        self.use_double_dqn = use_double_dqn
        self.use_per = use_per
        self.use_huber_loss = use_huber_loss
        self.grad_clip = grad_clip

        network_config = network_config or {}
        self.q_network = DQN(state_dim, action_dim, **network_config).to(device)
        self.target_network = DQN(state_dim, action_dim, **network_config).to(device)
        self.target_network.load_state_dict(self.q_network.state_dict())
        self.target_network.eval()

        self.optimizer = optim.Adam(self.q_network.parameters(), lr=lr)
        self.lr_scheduler = self._create_scheduler(lr_scheduler)
        self.loss_fn = nn.SmoothL1Loss(reduction='none') if use_huber_loss else nn.MSELoss(reduction='none')
        self.replay_buffer = PrioritizedReplayBuffer() if use_per else ReplayBuffer()
        self.training_step = 0
        self.prev_states = {}

    def _create_scheduler(self, scheduler_type):
        """创建学习率调度器"""
        if scheduler_type == 'step':
            return optim.lr_scheduler.StepLR(self.optimizer, step_size=1000, gamma=0.9)
        elif scheduler_type == 'cosine':
            return optim.lr_scheduler.CosineAnnealingLR(self.optimizer, T_max=10000)
        return None

    def select_action(self, state, training=True):
        """选择动作（epsilon-greedy）"""
        if training and random.random() < self.epsilon:
            return random.randint(0, self.action_dim - 1)

        was_training = self.q_network.training
        self.q_network.eval()

        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            action = self.q_network(state_tensor).argmax().item()

        if was_training:
            self.q_network.train()
        return action

    def update_epsilon(self):
        """更新epsilon"""
        if self.epsilon > self.epsilon_end:
            self.epsilon *= self.epsilon_decay

    def train_step(self, batch_size=32):
        """训练一步"""
        if len(self.replay_buffer) < batch_size:
            return None

        if self.use_per:
            states, actions, rewards, next_states, dones, weights, indices = self.replay_buffer.sample(batch_size)
            weights = weights.to(self.device)
        else:
            states, actions, rewards, next_states, dones = self.replay_buffer.sample(batch_size)
            weights = torch.ones(batch_size).to(self.device)
            indices = None

        states = states.to(self.device)
        actions = actions.to(self.device)
        rewards = rewards.to(self.device)
        next_states = next_states.to(self.device)
        dones = dones.to(self.device)

        q_values = self.q_network(states).gather(1, actions.unsqueeze(1)).squeeze(1)

        with torch.no_grad():
            if self.use_double_dqn:
                next_actions = self.q_network(next_states).argmax(1)
                next_q_values = self.target_network(next_states).gather(1, next_actions.unsqueeze(1)).squeeze(1)
            else:
                next_q_values = self.target_network(next_states).max(1)[0]
            target_q_values = rewards + (self.gamma * next_q_values * ~dones)

        td_errors = q_values - target_q_values
        loss = (weights * self.loss_fn(q_values, target_q_values)).mean()

        self.optimizer.zero_grad()
        loss.backward()

        if self.grad_clip is not None:
            torch.nn.utils.clip_grad_norm_(self.q_network.parameters(), self.grad_clip)

        self.optimizer.step()

        if self.use_per and indices is not None:
            self.replay_buffer.update_priorities(indices, td_errors.detach().cpu().numpy())

        if self.lr_scheduler is not None:
            self.lr_scheduler.step()

        self.training_step += 1
        if self.training_step % self.target_update_freq == 0:
            self.target_network.load_state_dict(self.q_network.state_dict())

        return loss.item()

    def save_model(self, path):
        """保存模型"""
        save_model(self, path)

    def load_model(self, path):
        """加载模型"""
        load_model(self, path)

    def calculate_reward(self, player, world, prev_state_dict: Optional[dict] = None,
                         current_action: Optional[int] = None) -> float:
        """计算奖励"""
        return calculate_reward(player, world, prev_state_dict, current_action)

    def predict_schedule(self, players: List, world, training: bool = False) -> Dict:
        """预测决策表"""
        return predict_schedule(self.q_network, self.device, players, world, training)
