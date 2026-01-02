"""
DQN神经网络模型
支持Batch Normalization、LeakyReLU激活函数、可配置网络深度
"""

import torch
import torch.nn as nn


class DQN(nn.Module):
    """DQN神经网络模型"""
    
    def __init__(self, state_dim, action_dim, hidden_dims=[256, 128, 64], 
                 use_batch_norm=True, dropout_rate=0.1):
        """
        初始化DQN网络
        
        Args:
            state_dim: 状态维度
            action_dim: 动作维度
            hidden_dims: 隐藏层维度列表，默认[256, 128, 64]
            use_batch_norm: 是否使用Batch Normalization
            dropout_rate: Dropout比率（0表示不使用）
        """
        super(DQN, self).__init__()
        self.use_batch_norm = use_batch_norm
        self.dropout_rate = dropout_rate
        
        # 构建网络层
        layers = []
        input_dim = state_dim
        
        for i, hidden_dim in enumerate(hidden_dims):
            layers.append(nn.Linear(input_dim, hidden_dim))
            
            if use_batch_norm:
                layers.append(nn.BatchNorm1d(hidden_dim))
            
            # 使用LeakyReLU替代ReLU，避免死亡ReLU问题
            layers.append(nn.LeakyReLU(negative_slope=0.01))
            
            if dropout_rate > 0 and i < len(hidden_dims) - 1:  # 最后一层不使用dropout
                layers.append(nn.Dropout(dropout_rate))
            
            input_dim = hidden_dim
        
        # 输出层（不使用激活函数，因为输出Q值）
        layers.append(nn.Linear(input_dim, action_dim))
        
        self.network = nn.Sequential(*layers)
        
        # 权重初始化（Xavier初始化）
        self._initialize_weights()
    
    def _initialize_weights(self):
        """初始化网络权重"""
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
    
    def forward(self, x):
        """
        前向传播
        
        注意：BatchNorm在batch size=1时会失败，所以我们在训练时
        如果batch size=1，需要临时将BatchNorm层切换到eval模式
        """
        # 如果batch size=1且网络处于训练模式，临时切换BatchNorm层到eval模式
        if self.training and x.size(0) == 1 and self.use_batch_norm:
            # 找到所有BatchNorm层并临时切换到eval模式
            batch_norm_layers = []
            for module in self.network.modules():
                if isinstance(module, nn.BatchNorm1d):
                    batch_norm_layers.append(module)
                    module.eval()
            
            result = self.network(x)
            
            # 恢复BatchNorm层的训练模式
            for module in batch_norm_layers:
                module.train()
            
            return result
        else:
            return self.network(x)
