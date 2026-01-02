# 离线训练使用指南

## 快速开始

### 方法1: 使用启动脚本（推荐）

```bash
cd backend
./start_offline_training.sh [端口] [算法]
```

示例：
```bash
./start_offline_training.sh 34712 CustomDQN
```

### 方法2: 手动启动

#### 1. 启动离线训练

```bash
cd backend
python3 lib/reinforcement_learning/training/train_gym.py 34712 \
    --algorithm CustomDQN \
    --train-offline \
    --save-interval 10
```

#### 2. 启动监控工具（另一个终端）

```bash
cd backend
# 可视化监控（需要matplotlib）
python3 lib/reinforcement_learning/training/visualize_training.py \
    /tmp/ctf-ai/training_stats.json 5

# 或使用文本监控脚本
./monitor_training.sh [更新间隔秒数]
```

## 支持的算法

- **CustomDQN**: 项目自定义DQN实现（推荐，无需额外依赖）
- **DQN**: stable-baselines3的DQN（需要安装stable-baselines3）
- **PPO**: stable-baselines3的PPO（需要安装stable-baselines3）
- **A2C**: stable-baselines3的A2C（需要安装stable-baselines3）

## 训练参数

- `--algorithm`: 算法选择（默认: CustomDQN）
- `--train-offline`: 离线训练模式（不连接游戏服务器）
- `--save-interval`: 每N个episode保存一次模型（默认: 10）
- `--model-path`: 加载已有模型继续训练

## 训练输出

### 模型保存位置

- 检查点模型: `lib/models/gym_model_ep{N}.pth` 或 `.zip`
- 最终模型: `lib/models/gym_model_final.pth` 或 `.zip`

### 日志文件位置

所有日志保存在 `/tmp/ctf-ai/`:

- 训练日志: `/tmp/ctf-ai/training_output.log`
- 统计文件: `/tmp/ctf-ai/training_stats.json`
- CSV日志: `/tmp/ctf-ai/training_log.csv`
- 可视化图表: `lib/models/training_plot.png`（如果使用可视化监控）

## 监控训练

### 实时查看训练日志

```bash
tail -f /tmp/ctf-ai/training_output.log
```

### 查看统计信息

```bash
cat /tmp/ctf-ai/training_stats.json | python3 -m json.tool
```

### 使用可视化监控

可视化监控会显示：
- Episode奖励趋势图
- 训练损失趋势图
- 胜率趋势图（如果有对局数据）
- 实时统计信息面板
- 训练建议

### 检查训练进程

```bash
ps aux | grep train_gym.py
```

## 停止训练

### 方法1: 使用进程ID

```bash
# 查找训练进程
ps aux | grep train_gym.py | grep -v grep

# 停止训练（替换PID为实际进程ID）
kill <PID>
```

### 方法2: 使用pkill

```bash
pkill -f train_gym.py
```

### 方法3: 在训练终端按 Ctrl+C

如果训练在前台运行，直接按 `Ctrl+C` 即可停止。

## 训练统计说明

### 关键指标

- **total_episodes**: 总训练episode数
- **avg_reward**: 平均奖励
- **avg_reward_recent**: 最近10局平均奖励
- **best_reward**: 最佳奖励
- **avg_loss_recent**: 最近平均损失
- **current_epsilon**: 当前探索率（ε-greedy策略）
- **training_time**: 训练时间

### 训练建议

监控工具会根据以下条件提供建议：

- **胜率 ≥ 80%**: 模型表现优秀，可以考虑停止训练
- **胜率 ≥ 60%**: 模型表现良好，可以继续训练
- **胜率 < 50%**: 模型需要更多训练
- **奖励波动大**: 训练不稳定，可能需要调整超参数
- **损失较高**: 可能需要调整学习率

## 常见问题

### Q: 训练很慢怎么办？

A: 
- 离线训练使用模拟环境，速度取决于CPU性能
- 可以调整 `max_steps` 参数减少每个episode的步数
- 考虑使用GPU加速（如果支持）

### Q: 如何继续训练已有模型？

A: 使用 `--model-path` 参数：

```bash
python3 lib/reinforcement_learning/training/train_gym.py 34712 \
    --algorithm CustomDQN \
    --train-offline \
    --model-path lib/models/gym_model_final.pth
```

### Q: 如何清理训练日志？

A: 使用清理脚本：

```bash
python3 lib/reinforcement_learning/training/clear_logs.py --yes
```

### Q: 可视化监控无法显示中文？

A: 系统会自动检测并使用可用的中文字体。如果仍有问题，可以安装中文字体或修改 `visualize_training.py` 中的字体设置。

## 当前训练状态

训练进程和监控工具已启动：

- **训练进程**: 正在运行（PID可通过 `ps aux | grep train_gym.py` 查看）
- **监控工具**: 已启动（如果matplotlib可用，会显示图形界面）
- **统计文件**: `/tmp/ctf-ai/training_stats.json`
- **训练日志**: `/tmp/ctf-ai/training_output.log`

查看实时状态：
```bash
tail -f /tmp/ctf-ai/training_output.log
```
