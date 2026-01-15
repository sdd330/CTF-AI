"""
模型持久化模块
处理DQN模型的保存和加载
"""

import torch


def save_model(agent, path: str) -> None:
    """
    保存模型到文件

    Args:
        agent: DQNAgent实例
        path: 保存路径
    """
    checkpoint = {
        'q_network': agent.q_network.state_dict(),
        'target_network': agent.target_network.state_dict(),
        'optimizer': agent.optimizer.state_dict(),
        'epsilon': agent.epsilon,
        'training_step': agent.training_step,
        'use_double_dqn': agent.use_double_dqn,
        'use_per': agent.use_per,
        'use_huber_loss': agent.use_huber_loss,
    }

    if agent.lr_scheduler is not None:
        checkpoint['lr_scheduler'] = agent.lr_scheduler.state_dict()

    torch.save(checkpoint, path)


def load_model(agent, path: str) -> None:
    """
    从文件加载模型

    Args:
        agent: DQNAgent实例
        path: 加载路径
    """
    checkpoint = torch.load(path, map_location=agent.device)
    agent.q_network.load_state_dict(checkpoint['q_network'])
    agent.target_network.load_state_dict(checkpoint['target_network'])

    agent.q_network = agent.q_network.to(agent.device)
    agent.target_network = agent.target_network.to(agent.device)

    agent.optimizer.load_state_dict(checkpoint['optimizer'])
    agent.epsilon = checkpoint.get('epsilon', agent.epsilon_end)
    agent.training_step = checkpoint.get('training_step', 0)

    if 'use_double_dqn' in checkpoint:
        agent.use_double_dqn = checkpoint['use_double_dqn']
    if 'use_per' in checkpoint:
        agent.use_per = checkpoint['use_per']
    if 'use_huber_loss' in checkpoint:
        agent.use_huber_loss = checkpoint['use_huber_loss']
    if 'lr_scheduler' in checkpoint and agent.lr_scheduler is not None:
        agent.lr_scheduler.load_state_dict(checkpoint['lr_scheduler'])

    agent.target_network.eval()
