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
import numpy as np
from typing import Dict, List, Optional

from .network import DQN
from .replay_buffer import ReplayBuffer, PrioritizedReplayBuffer
from .reward_calculator import calculate_reward
from .scheduler import predict_schedule


class DQNAgent:
    """DQN智能体"""
    
    def __init__(self, state_dim, action_dim, lr=0.0005, gamma=0.99, 
                 epsilon_start=1.0, epsilon_end=0.01, epsilon_decay=0.998,
                 target_update_freq=50, device='cpu', use_double_dqn=True,
                 use_per=False, use_huber_loss=True, grad_clip=10.0,
                 lr_scheduler=None, network_config=None):
        """
        初始化DQN智能体
        
        Args:
            state_dim: 状态维度
            action_dim: 动作维度
            lr: 学习率
            gamma: 折扣因子
            epsilon_start: 初始探索率
            epsilon_end: 最终探索率
            epsilon_decay: 探索率衰减率
            target_update_freq: Target网络更新频率
            device: 设备（'cpu' 或 'cuda'）
            use_double_dqn: 是否使用Double DQN
            use_per: 是否使用优先经验回放
            use_huber_loss: 是否使用Huber Loss（否则使用MSE Loss）
            grad_clip: 梯度裁剪阈值（None表示不裁剪）
            lr_scheduler: 学习率调度器类型（'step', 'cosine', None）
            network_config: 网络配置字典
        """
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
        
        # 网络配置
        if network_config is None:
            network_config = {}
        
        # 创建网络
        self.q_network = DQN(state_dim, action_dim, **network_config).to(device)
        self.target_network = DQN(state_dim, action_dim, **network_config).to(device)
        self.target_network.load_state_dict(self.q_network.state_dict())
        self.target_network.eval()
        
        # 优化器
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=lr)
        
        # 学习率调度器
        self.lr_scheduler = None
        if lr_scheduler == 'step':
            self.lr_scheduler = optim.lr_scheduler.StepLR(self.optimizer, step_size=1000, gamma=0.9)
        elif lr_scheduler == 'cosine':
            self.lr_scheduler = optim.lr_scheduler.CosineAnnealingLR(self.optimizer, T_max=10000)
        
        # 损失函数（使用reduction='none'以便应用重要性采样权重）
        if use_huber_loss:
            self.loss_fn = nn.SmoothL1Loss(reduction='none')  # Huber Loss
        else:
            self.loss_fn = nn.MSELoss(reduction='none')
        
        # 经验回放
        if use_per:
            self.replay_buffer = PrioritizedReplayBuffer()
        else:
            self.replay_buffer = ReplayBuffer()
        
        # 训练步数（使用training_step避免与方法名冲突）
        self.training_step = 0
        
        # 上一帧状态（用于奖励计算）
        self.prev_states = {}  # {player_name: state_dict}
    
    def select_action(self, state, training=True):
        """选择动作（epsilon-greedy）"""
        if training and random.random() < self.epsilon:
            return random.randint(0, self.action_dim - 1)
        
        # 在推理时确保网络处于eval模式（避免BatchNorm在batch size=1时出错）
        was_training = self.q_network.training
        self.q_network.eval()
        
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            q_values = self.q_network(state_tensor)
            action = q_values.argmax().item()
        
        # 恢复训练模式（如果之前是训练模式）
        if was_training:
            self.q_network.train()
        
        return action
    
    def update_epsilon(self):
        """更新epsilon"""
        if self.epsilon > self.epsilon_end:
            self.epsilon *= self.epsilon_decay
    
    def train_step(self, batch_size=32):
        """
        训练一步（支持PER、梯度裁剪、学习率调度）
        
        Returns:
            loss值，如果缓冲区不足则返回None
        """
        if len(self.replay_buffer) < batch_size:
            return None
        
        # 采样批次
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
        
        # 当前Q值
        q_values = self.q_network(states).gather(1, actions.unsqueeze(1)).squeeze(1)
        
        # 目标Q值 - 使用Double DQN
        with torch.no_grad():
            if self.use_double_dqn:
                # Double DQN: 使用主网络选择动作，target network评估Q值
                next_actions = self.q_network(next_states).argmax(1)
                next_q_values = self.target_network(next_states).gather(1, next_actions.unsqueeze(1)).squeeze(1)
            else:
                # 标准DQN: 使用target network选择动作和评估Q值
                next_q_values = self.target_network(next_states).max(1)[0]
            
            target_q_values = rewards + (self.gamma * next_q_values * ~dones)
        
        # 计算损失（带重要性采样权重）
        td_errors = q_values - target_q_values
        loss = (weights * self.loss_fn(q_values, target_q_values)).mean()
        
        # 反向传播
        self.optimizer.zero_grad()
        loss.backward()
        
        # 梯度裁剪
        if self.grad_clip is not None:
            torch.nn.utils.clip_grad_norm_(self.q_network.parameters(), self.grad_clip)
        
        self.optimizer.step()
        
        # 更新PER优先级
        if self.use_per and indices is not None:
            td_errors_np = td_errors.detach().cpu().numpy()
            self.replay_buffer.update_priorities(indices, td_errors_np)
        
        # 更新学习率
        if self.lr_scheduler is not None:
            self.lr_scheduler.step()
        
        # 更新target network
        self.training_step += 1
        if self.training_step % self.target_update_freq == 0:
            self.target_network.load_state_dict(self.q_network.state_dict())
        
        return loss.item()
    
    def save_model(self, path):
        """保存模型"""
        checkpoint = {
            'q_network': self.q_network.state_dict(),
            'target_network': self.target_network.state_dict(),
            'optimizer': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'training_step': self.training_step,
            'use_double_dqn': self.use_double_dqn,
            'use_per': self.use_per,
            'use_huber_loss': self.use_huber_loss,
        }
        
        # 保存学习率调度器状态
        if self.lr_scheduler is not None:
            checkpoint['lr_scheduler'] = self.lr_scheduler.state_dict()
        
        torch.save(checkpoint, path)
    
    def load_model(self, path):
        """加载模型"""
        # 使用map_location确保模型加载到正确的设备
        checkpoint = torch.load(path, map_location=self.device)
        self.q_network.load_state_dict(checkpoint['q_network'])
        self.target_network.load_state_dict(checkpoint['target_network'])
        # 确保网络在正确的设备上
        self.q_network = self.q_network.to(self.device)
        self.target_network = self.target_network.to(self.device)
        self.optimizer.load_state_dict(checkpoint['optimizer'])
        self.epsilon = checkpoint.get('epsilon', self.epsilon_end)
        self.training_step = checkpoint.get('training_step', 0)
        if 'use_double_dqn' in checkpoint:
            self.use_double_dqn = checkpoint['use_double_dqn']
        if 'use_per' in checkpoint:
            self.use_per = checkpoint['use_per']
        if 'use_huber_loss' in checkpoint:
            self.use_huber_loss = checkpoint['use_huber_loss']
        if 'lr_scheduler' in checkpoint and self.lr_scheduler is not None:
            self.lr_scheduler.load_state_dict(checkpoint['lr_scheduler'])
        self.target_network.eval()
    
    def calculate_reward(self, player, world, prev_state_dict: Optional[dict] = None, current_action: Optional[int] = None) -> float:
        """
        计算奖励（委托给reward_calculator模块）
        
        Args:
            player: 当前玩家字典对象
            world: World对象
            prev_state_dict: 上一帧的状态字典
            current_action: 当前选择的动作
        
        Returns:
            float: 奖励值
        """
        return calculate_reward(player, world, prev_state_dict, current_action)
    
    def predict_schedule(self, players: List, world, training: bool = False) -> Dict:
        """
        预测决策表（委托给scheduler模块）
        
        Args:
            players: 己方玩家字典列表
            world: World对象
            training: 是否处于训练模式
        
        Returns:
            dict: 决策表
        """
        return predict_schedule(self.q_network, self.device, players, world, training)
