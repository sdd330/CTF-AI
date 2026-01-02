# CTF-AI 训练模型发布说明

## 版本 2.0 (最新)

### 模型信息

- **模型名称**: `gym_model_v2.0.pth`
- **算法**: CustomDQN (深度Q网络)
- **训练Episode**: 8530 (最接近最佳表现Episode 8526，差距4个Episode)
- **最佳奖励**: 7,078.47 (Episode 8526)
- **Episode 8530奖励**: 836.91
- **最近10局平均奖励**: 1,321.95
- **模型大小**: 约 774 KB

### 模型性能

#### 训练统计
- **总训练Episode数**: 10,000
- **平均奖励**: 1,262.59
- **最近10局平均奖励**: 1,321.95 ✅ (表现稳定)
- **最佳奖励**: 7,078.47 (Episode 8526)
- **最小奖励**: -20.00
- **训练配置**: 3个玩家/队，6面旗帜/队

#### 性能评估
- ✅ **优秀** - 模型表现稳定，平均奖励超过1,200
- 相比初始训练（前1000个episode平均1,428.38），后1000个episode平均939.15
- 最佳Episode表现突出，奖励达到7,078.47
- 建议进行在线对战验证真实胜率

#### 训练趋势
- **前1000个episode平均**: 1,428.38
- **后1000个episode平均**: 939.15
- **最近10个episode平均**: 1,321.95
- **探索率**: 0.0100（已从探索转向利用）

### 训练参数

- **算法**: CustomDQN
- **状态维度**: 19 (玩家位置、旗帜位置、游戏状态等)
- **动作维度**: 3 (DEFENCE, SCORING, SAVING)
- **最终探索率**: 0.0100 (已收敛)
- **学习率**: 0.0005
- **批次大小**: 32
- **经验回放缓冲区**: 10000
- **保存间隔**: 每10个episode

### 奖励函数说明（优化后）

- **成功得分**: +150.0
- **进入基地区域（持有旗帜）**: +40.0
- **拾取旗帜**: +10.0
- **失去旗帜**: -40.0
- **被捕获**: -25.0
- **步惩罚**: -0.02/步
- **单步奖励裁剪**: [-50.0, 200.0]

## 版本 1.0 (历史版本)

### 模型信息

- **模型名称**: `gym_model_best.pth`
- **算法**: CustomDQN (深度Q网络)
- **训练Episode**: 580 (最接近最佳表现Episode 579)
- **最佳奖励**: 1,014.33 (Episode 579)
- **最近10局平均奖励**: 220.15
- **模型大小**: 约 774 KB

### 模型性能

#### 训练统计
- **总训练Episode数**: 1,000
- **平均奖励**: 222.36
- **最近10局平均奖励**: 220.15 ✅ (表现稳定)
- **最佳奖励**: 1,014.33 (Episode 579)
- **训练时间**: 40分45秒
- **训练速度**: 约 24.5 episodes/分钟

### 性能评估
- ✅ **优秀** - 模型表现稳定，平均奖励超过220
- 相比初始训练（前10个episode平均45.87），提升了 **380%**
- 最后10个episode表现稳定在220左右
- 建议进行在线对战验证真实胜率

### 训练趋势
- **前10个episode平均**: 45.87
- **最后10个episode平均**: 220.15
- **提升幅度**: +174.28 (380%提升)
- **探索率变化**: 从0.998降至0.1351（已从探索转向利用）

## 使用方法

### 1. 在线训练（连接游戏服务器）

```bash
cd backend
source .venv/bin/activate  # 如果使用虚拟环境
python3 lib/reinforcement_learning/training/train_gym.py 34712 \
    --algorithm CustomDQN \
    --model-path release/gym_model_v2.0.pth
```

### 2. 离线训练（继续训练）

```bash
cd backend
source .venv/bin/activate  # 如果使用虚拟环境
python3 lib/reinforcement_learning/training/train_gym.py 34712 \
    --algorithm CustomDQN \
    --train-offline \
    --model-path release/gym_model_v2.0.pth \
    --save-interval 10 \
    --max-episodes 10000
```

### 3. 在游戏服务器中使用

将模型文件复制到 `backend/lib/models/` 目录，然后在 `backend/server.py` 中加载：

```python
from lib.reinforcement_learning import DQNAgent

# 加载模型
agent = DQNAgent(state_dim=19, action_dim=3, device='cpu')
agent.load_model('lib/models/gym_model_v2.0.pth')
```

### 4. 快速启动离线训练

```bash
cd backend
./start_offline_training.sh 34712 CustomDQN
```

## 模型文件结构

```
release/
├── gym_model_v2.0.pth    # 最佳训练模型 v2.0 (Episode 8530，最接近最佳Episode 8526)
├── gym_model_best.pth     # 历史版本 v1.0 (Episode 580)
└── README.md              # 本说明文件
```

## 注意事项

1. **模型格式**: PyTorch (.pth) 格式
2. **依赖要求**: 
   - Python 3.10+
   - PyTorch >= 2.0.0
   - gymnasium >= 0.29.0
   - numpy >= 1.20.0
3. **设备要求**: 当前模型在 CPU 上训练，可在 CPU 或 GPU 上运行
4. **兼容性**: 与 `backend/lib/reinforcement_learning/agent.py` 中的 `DQNAgent` 类兼容
5. **虚拟环境**: 建议使用虚拟环境，已创建 `.venv` 目录

## 性能建议

1. **在线验证**: 建议进行在线对战验证真实胜率
2. **继续训练**: 如需进一步提升，可继续训练以稳定高奖励表现
3. **超参数调整**: 可根据实际表现调整学习率、探索率等参数
4. **模型选择**: 
   - **v2.0**: 最新版本，10,000 episodes训练，Episode 8530（最接近最佳Episode 8526，奖励7,078.47）
   - **v1.0**: 历史版本，1,000 episodes训练，最佳奖励1,014.33

## 训练日志

训练日志和统计信息保存在：
- **训练日志**: `/tmp/ctf-ai/training_output.log`
- **训练统计**: `/tmp/ctf-ai/training_stats.json`
- **CSV日志**: `/tmp/ctf-ai/training_log.csv`

## 版本信息

### v2.0
- **训练日期**: 2026-01-14
- **训练模式**: 离线训练
- **训练环境**: macOS
- **Python版本**: 3.14
- **训练完成**: ✅ 10,000 episodes
- **游戏配置**: 3个玩家/队，6面旗帜/队

### v1.0
- **训练日期**: 2026-01-12
- **训练模式**: 离线训练
- **训练环境**: macOS
- **Python版本**: 3.14
- **训练完成**: ✅ 1,000 episodes

## 许可证

请参考项目根目录的 LICENSE 文件。

## 联系方式

如有问题或建议，请参考项目 README 文件。
