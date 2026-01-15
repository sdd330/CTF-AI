"""
训练监控模块
用于记录和可视化DQN训练过程
"""

import json
import os
from typing import Dict, List, Optional
from collections import deque
from datetime import datetime


class TrainingMonitor:
    """训练监控器"""
    
    def __init__(self, log_dir: str = "/tmp/ctf-ai", max_history: int = 20000):
        """
        初始化训练监控器
        
        Args:
            log_dir: 日志目录（默认：/tmp/ctf-ai）
            max_history: 最大历史记录数（默认：20000，支持10000+ Episode训练）
        """
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # 训练统计
        self.episode_rewards = deque(maxlen=max_history)
        self.episode_losses = deque(maxlen=max_history)
        self.episode_lengths = deque(maxlen=max_history)
        self.epsilon_history = deque(maxlen=max_history)
        self.q_value_history = deque(maxlen=max_history)
        
        # 当前episode统计
        self.current_episode_reward = 0.0
        self.current_episode_length = 0
        self.current_episode_losses = []
        
        # 最佳性能记录
        self.best_episode_reward = float('-inf')
        self.best_episode = 0
        
        # 训练开始时间
        self.start_time = datetime.now()
    
    def log_step(self, reward: float, loss: Optional[float] = None, q_value: Optional[float] = None):
        """
        记录一步训练
        
        Args:
            reward: 奖励
            loss: 损失值（可选）
            q_value: Q值（可选）
        """
        self.current_episode_reward += reward
        self.current_episode_length += 1
        
        if loss is not None:
            self.current_episode_losses.append(loss)
        
        if q_value is not None:
            self.q_value_history.append(q_value)
    
    def log_episode(self, episode: int, epsilon: float):
        """
        记录一个episode结束
        
        Args:
            episode: episode编号
            epsilon: 当前epsilon值
        """
        # 记录episode统计
        self.episode_rewards.append(self.current_episode_reward)
        self.episode_lengths.append(self.current_episode_length)
        self.epsilon_history.append(epsilon)
        
        # 计算平均损失
        avg_loss = sum(self.current_episode_losses) / len(self.current_episode_losses) if self.current_episode_losses else 0.0
        self.episode_losses.append(avg_loss)
        
        # 更新最佳记录
        if self.current_episode_reward > self.best_episode_reward:
            self.best_episode_reward = self.current_episode_reward
            self.best_episode = episode
        
        # 重置当前episode统计
        self.current_episode_reward = 0.0
        self.current_episode_length = 0
        self.current_episode_losses = []
    
    def get_statistics(self, window: int = 10) -> Dict:
        """
        获取训练统计信息
        
        Args:
            window: 滑动窗口大小（用于计算平均值）
        
        Returns:
            统计信息字典
        """
        if len(self.episode_rewards) == 0:
            return {}
        
        recent_rewards = list(self.episode_rewards)[-window:]
        recent_losses = list(self.episode_losses)[-window:]
        
        stats = {
            'total_episodes': len(self.episode_rewards),
            'avg_reward': sum(self.episode_rewards) / len(self.episode_rewards),
            'avg_reward_recent': sum(recent_rewards) / len(recent_rewards) if recent_rewards else 0.0,
            'max_reward': max(self.episode_rewards) if self.episode_rewards else 0.0,
            'min_reward': min(self.episode_rewards) if self.episode_rewards else 0.0,
            'avg_loss': sum(self.episode_losses) / len(self.episode_losses) if self.episode_losses else 0.0,
            'avg_loss_recent': sum(recent_losses) / len(recent_losses) if recent_losses else 0.0,
            'avg_episode_length': sum(self.episode_lengths) / len(self.episode_lengths) if self.episode_lengths else 0.0,
            'current_epsilon': self.epsilon_history[-1] if self.epsilon_history else 0.0,
            'best_episode': self.best_episode,
            'best_reward': self.best_episode_reward,
            'training_time': str(datetime.now() - self.start_time)
        }
        
        return stats
    
    def print_statistics(self, episode: int, window: int = 10):
        """打印训练统计信息"""
        stats = self.get_statistics(window)
        if not stats:
            return
        
        print(f"\n{'='*60}")
        print(f"Episode {episode} Statistics")
        print(f"{'='*60}")
        print(f"Total Episodes: {stats['total_episodes']}")
        print(f"Average Reward (all): {stats['avg_reward']:.2f}")
        print(f"Average Reward (last {window}): {stats['avg_reward_recent']:.2f}")
        print(f"Best Reward: {stats['best_reward']:.2f} (Episode {stats['best_episode']})")
        print(f"Average Loss (last {window}): {stats['avg_loss_recent']:.4f}")
        print(f"Average Episode Length: {stats['avg_episode_length']:.1f}")
        print(f"Current Epsilon: {stats['current_epsilon']:.4f}")
        print(f"Training Time: {stats['training_time']}")
        print(f"{'='*60}\n")
    
    def save_statistics(self, filename: str = "training_stats.json"):
        """
        保存训练统计到文件
        
        Args:
            filename: 文件名
        """
        stats = self.get_statistics()
        stats['episode_rewards'] = list(self.episode_rewards)
        stats['episode_losses'] = list(self.episode_losses)
        stats['episode_lengths'] = list(self.episode_lengths)
        stats['epsilon_history'] = list(self.epsilon_history)
        stats['episode'] = stats.get('total_episodes', 0)
        stats['losses'] = list(self.episode_losses)
        
        filepath = os.path.join(self.log_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"Training statistics saved to {filepath}")
    
    def save_csv(self, filename: str = "training_log.csv"):
        """
        保存训练日志为CSV格式
        
        Args:
            filename: 文件名
        """
        import csv
        
        filepath = os.path.join(self.log_dir, filename)
        
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Episode', 'Reward', 'Loss', 'Length', 'Epsilon'])
            
            for i in range(len(self.episode_rewards)):
                writer.writerow([
                    i + 1,
                    self.episode_rewards[i] if i < len(self.episode_rewards) else 0.0,
                    self.episode_losses[i] if i < len(self.episode_losses) else 0.0,
                    self.episode_lengths[i] if i < len(self.episode_lengths) else 0,
                    self.epsilon_history[i] if i < len(self.epsilon_history) else 0.0
                ])
        
        print(f"Training log saved to {filepath}")
