# 强化学习模块（基于Gymnasium）

本模块提供基于Gymnasium标准的强化学习实现，用于CTF游戏的训练和推理。
完全使用Gymnasium标准接口，支持多种RL算法（DQN, PPO, A2C等）。

## 概述

本项目完全基于**Gymnasium**标准接口，将CTF游戏环境包装成标准的Gymnasium环境，从而：

- ✅ 使用成熟的RL算法库（stable-baselines3, Ray RLlib等）
- ✅ 使用标准化的评估和监控工具
- ✅ 与其他Gymnasium环境进行比较
- ✅ 利用Gymnasium生态系统中的工具和资源

## 安装

**重要：训练前请先激活虚拟环境！**

### 必需依赖

```bash
pip install gymnasium
```

### 完整安装

```bash
# 1. 创建并激活虚拟环境（如果还没有）
cd backend
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows

# 2. 安装基础依赖
pip install gymnasium

# 3. stable-baselines3（包含多种RL算法）
pip install stable-baselines3[extra]

# 或仅安装DQN
pip install stable-baselines3

# 或使用Ray RLlib（多智能体）
pip install ray[rllib]
```

## 快速开始

**⚠️ 重要：训练前必须先激活虚拟环境！**

### 基础训练

```bash
# 1. 激活虚拟环境
cd backend
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows

# 2. 在线训练（连接游戏服务器）
python3 lib/reinforcement_learning/training/train_gym.py 34712 --algorithm DQN

# 3. 离线训练（不连接服务器）
python3 lib/reinforcement_learning/training/train_gym.py 34712 --algorithm DQN --train-offline

# 4. 使用PPO算法
python3 lib/reinforcement_learning/training/train_gym.py 34712 --algorithm PPO
```

### 使用离线训练的模型进行在线训练

**三步快速开始**：

#### 步骤1：找到你的模型文件

```bash
# 查看可用的模型文件
ls -lh lib/models/*.pth
ls -lh lib/models/gym_best/
```

#### 步骤2：启动在线训练

**方法A：使用便捷脚本（推荐）**
```bash
cd backend
source .venv/bin/activate
bash lib/reinforcement_learning/training/start_online_training.sh \
    lib/models/gym_model_ep200.pth \
    34712
```

**方法B：直接使用训练脚本**
```bash
cd backend
source .venv/bin/activate
python3 lib/reinforcement_learning/training/train_gym.py 34712 \
    --algorithm CustomDQN \
    --model-path lib/models/gym_model_ep200.pth
```

#### 步骤3：监控训练（可选）

在另一个终端：
```bash
bash lib/reinforcement_learning/training/monitor_training_live.sh
```

**完整示例**：
```bash
# 1. 进入backend目录
cd backend

# 2. 激活虚拟环境
source .venv/bin/activate

# 3. 查看可用模型
ls -lh lib/models/*.pth | tail -5

# 4. 启动在线训练（使用最新模型）
bash lib/reinforcement_learning/training/start_online_training.sh \
    lib/models/gym_model_ep200.pth \
    34712 \
    CustomDQN

# 5. 在另一个终端监控训练
bash lib/reinforcement_learning/training/monitor_training_live.sh
```

**参数说明**：
- **模型路径**：`.pth` 文件（CustomDQN）或 `.zip` 文件（stable-baselines3）
- **端口**：游戏服务器端口（默认：34712）
- **算法**：可选，默认 CustomDQN

**注意事项**：
1. **确保前端已启动**（如果需要可视化）：`cd frontend && pnpm dev`
2. **算法匹配**：CustomDQN → `.pth` 文件，DQN/PPO/A2C → `.zip` 文件
3. **端口冲突**：脚本会自动检测并提示

详细代码示例请参考 `gym_example.py` 和 `training/train_gym.py`。

## 环境接口

### CTFGymEnv（单智能体）

**观察空间**：

- 类型：`Box(19,)`
- 19维特征向量：
  - 玩家自身信息（5维）：位置(x,y)、持旗、在监狱、在敌方领地
  - 目标信息（6维）：最近敌方flag距离、方向(4维one-hot)、到目标区域距离
  - 对手信息（4维）：最近敌人距离、危险度、敌人持旗、敌人在监狱
  - 全局信息（4维）：己方flag数、敌方flag数、己方得分、敌方得分

**动作空间**：

- 类型：`Discrete(3)`
- Strategy.DEFENCE.value (0): defence（防御）
- Strategy.SCORING.value (1): scoring（得分）
- Strategy.SAVING.value (2): saving（救援）

**奖励**：

- 基于游戏事件和动作的奖励信号
- 范围：约 -50 到 +100

### CTFMultiAgentGymEnv（多智能体）

**观察空间**：

- 类型：`Dict[str, Box(19,)]`
- 每个玩家一个19维观察向量

**动作空间**：

- 类型：`Dict[str, Discrete(3)]`
- 每个玩家一个离散动作

## 核心模块

### agent.py

- `DQNAgent`: DQN智能体类
  - `select_action()`: 选择动作（epsilon-greedy）
  - `train_step()`: 训练一步（支持PER、梯度裁剪、学习率调度）
  - `save_model()` / `load_model()`: 模型保存/加载
  - 支持参数：`use_per`, `use_huber_loss`, `grad_clip`, `lr_scheduler`, `network_config`

### network.py

- `DQN`: 深度Q网络模型
  - Batch Normalization
  - LeakyReLU激活函数
  - Dropout正则化（可选）
  - Xavier权重初始化

### replay_buffer.py

- `ReplayBuffer`: 标准经验回放缓冲区
- `PrioritizedReplayBuffer`: 优先经验回放缓冲区（PER）

### gym_env.py

- `CTFGymEnv`: 单智能体Gymnasium环境包装器
- `CTFMultiAgentGymEnv`: 多智能体Gymnasium环境包装器

### gym_server_bridge.py

- `GymServerBridge`: 连接Gymnasium环境与游戏服务器
- `create_gym_server_callbacks`: 创建服务器回调函数

### 其他模块

- `state_extractor.py`: 状态特征提取
- `reward_calculator.py`: 奖励计算
- `scheduler.py`: 策略调度（决策表生成）
- `training_monitor.py`: 训练监控器

## 主要特性

### 1. 网络结构

- Batch Normalization，提高训练稳定性
- LeakyReLU激活函数，避免死亡ReLU问题
- 支持可配置的网络深度和宽度
- Xavier权重初始化
- 可选的Dropout正则化

### 2. 经验回放

- 标准经验回放（ReplayBuffer）
- 优先经验回放（PrioritizedReplayBuffer, PER）
  - 根据TD误差优先级采样
  - 重要性采样权重校正

### 3. 训练特性

- Huber Loss（SmoothL1Loss），对异常值更鲁棒
- 梯度裁剪，防止梯度爆炸
- 学习率调度（StepLR、CosineAnnealingLR）
- Double DQN支持

### 4. 状态特征

- 位置归一化方法
- 使用曼哈顿距离归一化
- 边界值保护

### 5. 奖励函数

- 渐进式距离奖励（平滑的奖励曲线）
- 细粒度的动作奖励（根据具体情况动态调整）
- 团队协作奖励（救人、防御等）

## 训练

### 支持的算法

- **DQN**: Deep Q-Network（stable-baselines3）
- **PPO**: Proximal Policy Optimization（stable-baselines3）
- **A2C**: Advantage Actor-Critic（stable-baselines3）
- **CustomDQN**: 项目自定义DQN实现

### 算法对比

| 算法 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **DQN** | 稳定、成熟 | 样本效率较低 | 离散动作空间 |
| **PPO** | 样本效率高、稳定 | 需要调参 | 连续/离散动作 |
| **A2C** | 简单、快速 | 稳定性较差 | 快速原型 |
| **CustomDQN** | 完全控制 | 需要自己实现 | 特殊需求 |

### 训练模式

- **在线训练**: 连接游戏服务器，实时训练（默认）
- **离线训练**: 使用模拟环境，不连接服务器（`--train-offline`）

### 训练脚本

训练脚本：`training/train_gym.py`

**⚠️ 重要：训练前必须先激活虚拟环境！**

```bash
# 1. 激活虚拟环境
cd backend
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows
```

#### 在线训练（连接游戏服务器）

**基础在线训练**：
```bash
# 使用DQN算法
python3 lib/reinforcement_learning/training/train_gym.py 34712 --algorithm DQN

# 使用PPO算法
python3 lib/reinforcement_learning/training/train_gym.py 34712 --algorithm PPO

# 使用自定义DQN（项目自己的实现）
python3 lib/reinforcement_learning/training/train_gym.py 34712 --algorithm CustomDQN
```

**使用离线训练的模型继续在线训练**：

```bash
# 方法1：使用便捷脚本（推荐）
bash lib/reinforcement_learning/training/start_online_training.sh \
    lib/models/gym_model_ep200.pth \
    34712

# 方法2：直接使用训练脚本
python3 lib/reinforcement_learning/training/train_gym.py 34712 \
    --algorithm CustomDQN \
    --model-path lib/models/gym_model_ep200.pth

# 使用stable-baselines3的模型
python3 lib/reinforcement_learning/training/train_gym.py 34712 \
    --algorithm DQN \
    --model-path lib/models/gym_model_final.zip
```

**模型文件位置**：
- 定期保存的模型：`lib/models/gym_model_ep*.pth`（按episode保存的检查点）
- 最佳模型：`lib/models/gym_best/best_model.pth`（训练过程中表现最好的模型）
- 最终模型：`lib/models/gym_model_final.pth`（训练结束时保存的最终模型）

#### 离线训练（不连接服务器）

```bash
# 离线训练（使用模拟环境）
python3 lib/reinforcement_learning/training/train_gym.py 34712 --algorithm DQN --train-offline

# 离线训练PPO
python3 lib/reinforcement_learning/training/train_gym.py 34712 --algorithm PPO --train-offline
```

#### 参数说明

- `port`: 服务器端口（必需）
- `--algorithm`: 算法选择（DQN, PPO, A2C, CustomDQN），默认DQN
- `--model-path`: 加载已有模型路径
- `--save-interval`: 每N个episode保存一次模型，默认10
- `--train-offline`: 离线训练模式（不连接游戏服务器）

### 训练输出

#### 模型保存位置

- 在线训练：`lib/models/gym_model_final.pth` 或 `.zip`
- 离线训练：`lib/models/gym_best/`（最佳模型）
- 检查点：`lib/models/gym_checkpoints/`（定期保存）

#### 日志位置

所有日志文件保存在系统临时目录 `/tmp/ctf-ai/`：

- 训练日志：`/tmp/ctf-ai/training_*.log`
- Gym训练日志：`/tmp/ctf-ai/gym_training/`
- Gym评估日志：`/tmp/ctf-ai/gym_eval/`
- 统计文件：`/tmp/ctf-ai/training_stats.json`、`/tmp/ctf-ai/gym_training_stats.json`
- CSV日志：`/tmp/ctf-ai/training_log.csv`、`/tmp/ctf-ai/gym_training_log.csv`

### 完整训练流程

```bash
# 1. 激活虚拟环境
cd backend
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows

# 2. 启动游戏前端（另一个终端）
cd frontend && pnpm dev

# 3. 启动训练（使用Gym）
cd backend
python3 lib/reinforcement_learning/training/train_gym.py 34712 --algorithm DQN

# 4. 训练过程中会自动保存模型
# 5. 按Ctrl+C停止训练，模型会自动保存
```

## 使用示例

详细代码示例请参考：
- `gym_example.py`: 完整使用示例代码
- `training/train_gym.py`: 训练脚本源码

## 常见问题

### Q: 如何选择算法？

A: 
- **初学者**：使用DQN（稳定）
- **需要快速训练**：使用PPO（样本效率高）
- **特殊需求**：使用CustomDQN（完全控制）

### Q: 在线训练和离线训练的区别？

A:

| 特性 | 离线训练 | 在线训练 |
|------|---------|---------|
| **连接服务器** | ❌ 不连接 | ✅ 连接 |
| **环境真实性** | 模拟环境 | 真实游戏环境 |
| **训练速度** | 快 | 较慢（受网络延迟影响） |
| **适用场景** | 快速迭代、大量episode | 真实场景、与人类对战 |
| **启动参数** | `--train-offline` | 默认（无此参数） |

**训练模式选择建议**：
- **初期训练**：使用离线训练快速迭代
- **精细调优**：使用在线训练在真实环境中继续训练
- **最终测试**：使用在线训练与人类或其他AI对战

### Q: 如何继续训练已有模型？

A: 有两种方法：

**方法1：使用便捷脚本（推荐）**
```bash
bash lib/reinforcement_learning/training/start_online_training.sh \
    lib/models/gym_model_ep200.pth \
    34712
```

**方法2：直接使用训练脚本**
```bash
python3 lib/reinforcement_learning/training/train_gym.py 34712 \
    --algorithm CustomDQN \
    --model-path lib/models/gym_model_ep200.pth
```

**模型文件说明**：
- CustomDQN使用`.pth`文件，stable-baselines3使用`.zip`文件
- 模型保存在`lib/models/`目录下
- 查看可用模型：`ls -lh lib/models/*.pth`

**详细说明**：所有在线训练相关内容已整合到本文档中，请查看下方的"使用离线模型进行在线训练"章节。

### Q: 训练数据保存在哪里？

A: 
- 模型：`lib/models/`（模型文件、检查点、最佳模型）
- 日志：`/tmp/ctf-ai/`（所有训练日志、统计文件、CSV日志）

### Q: 如何清理训练日志？

A: 使用日志清理脚本：
```bash
# 使用Python脚本（推荐）
python3 lib/reinforcement_learning/training/clear_logs.py

# 或使用Shell脚本
bash lib/reinforcement_learning/training/clear_logs.sh

# 自动确认（无需交互）
python3 lib/reinforcement_learning/training/clear_logs.py --yes
```

### Q: Gymnasium环境如何与游戏服务器同步？

A: 使用`update_world_state()`方法从服务器更新状态。

### Q: 可以使用向量化环境吗？

A: 可以！使用stable-baselines3的`VecEnv`包装器。

### Q: 如何监控训练过程？

A: 有多种方法：

**实时监控训练日志**：
```bash
bash lib/reinforcement_learning/training/monitor_training_live.sh
```

**查看训练统计**：
```bash
# 查看训练统计JSON
cat /tmp/ctf-ai/gym_training_stats.json

# 查看训练日志CSV
cat /tmp/ctf-ai/gym_training_log.csv
```

也可以使用Gymnasium的Monitor或stable-baselines3的监控工具。

## 目录结构

```
reinforcement_learning/
├── __init__.py              # 模块导出
├── agent.py                 # DQNAgent智能体（核心类）
├── network.py               # DQN神经网络模型
├── replay_buffer.py         # 经验回放缓冲区
├── state_extractor.py       # 状态特征提取
├── reward_calculator.py     # 奖励计算
├── scheduler.py             # 任务调度（决策表生成）
├── training_monitor.py      # 训练监控器
├── gym_env.py              # Gymnasium环境包装器
├── gym_server_bridge.py    # 服务器桥接
├── gym_example.py          # 使用示例
└── training/                # 训练脚本和工具
    ├── train_gym.py          # 训练脚本（基于Gymnasium）
    ├── start_online_training.sh  # 在线训练便捷启动脚本
    ├── start_single_agent_training.sh  # 单智能体训练启动脚本
    ├── start_self_play_training.sh  # 自对抗训练启动脚本
    ├── monitor_training_live.sh  # 实时监控训练过程
    ├── monitor_training.sh   # 训练监控脚本
    ├── clear_logs.py         # 清理训练日志（Python）
    ├── clear_logs.sh         # 清理训练日志（Shell）
    ├── clear_training_data.py  # 清理训练数据
    ├── visualize_training.py  # 训练可视化
    ├── visualize_battle.py   # 战斗可视化
    └── test_training.py      # 训练系统测试
```

## 系统特性

| 特性 | 说明 |
|------|------|
| 接口 | Gymnasium标准接口 |
| 算法 | DQN, PPO, A2C, CustomDQN |
| 工具支持 | 丰富（监控、评估、可视化等） |
| 离线训练 | ✅ 支持 |
| 在线训练 | ✅ 支持（连接游戏服务器） |
| 向量化 | ✅ 支持（可扩展） |
| 社区支持 | 广泛（stable-baselines3生态） |

## 参考文档

详细代码示例和高级用法请参考：
- `gym_example.py`: 完整使用示例代码
- `training/train_gym.py`: 训练脚本源码
- `training/start_online_training.sh`: 在线训练便捷启动脚本

**注意**：所有在线训练相关文档已整合到本文档中，包括快速开始、详细步骤、模型文件说明、使用场景和常见问题等。

## 使用离线模型进行在线训练

> **提示**：本节详细说明如何使用离线训练的模型进行在线训练。如果你已经熟悉基本操作，可以直接查看上方的"快速开始"章节。

### 模型文件说明

**模型文件格式**：
- **`.pth` 文件**：PyTorch模型文件（CustomDQN使用）
  - 包含：Q网络、目标网络、优化器状态、epsilon值等
  - 可以完全恢复训练状态
- **`.zip` 文件**：stable-baselines3模型文件（DQN/PPO/A2C使用）
  - 包含：模型参数、训练配置等

**模型文件位置**：
- 定期保存的模型：`lib/models/gym_model_ep*.pth`（按episode保存的检查点）
- 最佳模型：`lib/models/gym_best/best_model.pth`（训练过程中表现最好的模型）
- 最终模型：`lib/models/gym_model_final.pth`（训练结束时保存的最终模型）
- 检查点：`lib/models/gym_checkpoints/`（定期保存）

### 使用场景

**场景1：继续训练已有模型**
```bash
# 从episode 200的检查点继续训练
python3 lib/reinforcement_learning/training/train_gym.py 34712 \
    --algorithm CustomDQN \
    --model-path lib/models/gym_model_ep200.pth \
    --save-interval 10
```

**场景2：从最佳模型开始训练**
```bash
# 从最佳模型开始继续训练
python3 lib/reinforcement_learning/training/train_gym.py 34712 \
    --algorithm CustomDQN \
    --model-path lib/models/gym_best/best_model.pth
```

**场景3：使用不同算法加载模型**
```bash
# 注意：不同算法的模型文件格式不同，不能混用
# CustomDQN只能加载.pth文件
python3 lib/reinforcement_learning/training/train_gym.py 34712 \
    --algorithm CustomDQN \
    --model-path lib/models/gym_model_ep200.pth

# stable-baselines3的DQN只能加载.zip文件
python3 lib/reinforcement_learning/training/train_gym.py 34712 \
    --algorithm DQN \
    --model-path lib/models/gym_model_final.zip
```

### 常见问题

**Q: 如何知道模型训练到哪个episode了？**

A: 查看模型文件名，例如 `gym_model_ep200.pth` 表示训练到episode 200。或者查看训练日志：
```bash
cat /tmp/ctf-ai/training_offline_*.log | grep "Episode"
```

**Q: 在线训练时模型会自动保存吗？**

A: 是的，在线训练时：
- 每N个episode保存一次（由`--save-interval`控制，默认10）
- 按Ctrl+C停止时会自动保存最终模型到 `lib/models/gym_model_final.pth`

**Q: 加载模型后epsilon会重置吗？**

A: 不会，模型文件保存了当前的epsilon值，加载后会继续使用。如果你想重置epsilon，需要修改代码或使用新的模型。

**Q: 如何只使用模型进行推理（不训练）？**

A: 目前训练脚本会继续训练。如果只想推理，可以：
1. 设置很小的学习率
2. 或者修改代码，在加载模型后设置 `training_agent.epsilon = 0.0`（完全贪婪）

### 最佳实践

1. **定期保存**：使用 `--save-interval` 定期保存检查点
2. **保留最佳模型**：不要删除 `gym_best/` 目录中的最佳模型
3. **监控训练**：使用监控脚本实时查看训练进度
4. **备份模型**：重要模型要备份到其他位置
5. **记录训练参数**：在模型文件名中包含关键参数信息
6. **算法匹配**：确保 `--algorithm` 参数与模型文件匹配
   - CustomDQN → `.pth` 文件
   - DQN/PPO/A2C → `.zip` 文件