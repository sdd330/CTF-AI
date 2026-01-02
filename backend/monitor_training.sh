#!/bin/bash

# 训练监控脚本
# 实时显示训练进度和统计信息

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

STATS_FILE="/tmp/ctf-ai/training_stats.json"
UPDATE_INTERVAL=${1:-5}

echo "=========================================="
echo "CTF-AI 训练监控工具"
echo "=========================================="
echo "统计文件: $STATS_FILE"
echo "更新间隔: ${UPDATE_INTERVAL}秒"
echo "按 Ctrl+C 停止监控"
echo "=========================================="
echo ""

# 检查训练进程
TRAIN_PID=$(ps aux | grep "train_gym.py" | grep -v grep | awk '{print $2}' | head -1)
if [ -z "$TRAIN_PID" ]; then
    echo "警告: 未找到训练进程"
    echo "请先启动训练: python3 lib/reinforcement_learning/training/train_gym.py 34712 --algorithm CustomDQN --train-offline"
    exit 1
else
    echo "训练进程 PID: $TRAIN_PID"
    echo ""
fi

# 启动可视化监控
if python3 -c "import matplotlib" 2>/dev/null; then
    echo "启动可视化监控（图形界面）..."
    python3 lib/reinforcement_learning/training/visualize_training.py "$STATS_FILE" "$UPDATE_INTERVAL"
else
    echo "matplotlib 未安装，使用文本监控模式"
    echo ""
    
    # 文本监控模式
    while true; do
        if [ -f "$STATS_FILE" ]; then
            echo "=========================================="
            echo "$(date '+%Y-%m-%d %H:%M:%S')"
            echo "=========================================="
            
            # 使用python读取并显示统计信息
            python3 << EOF
import json
import os

stats_file = "$STATS_FILE"
if os.path.exists(stats_file):
    with open(stats_file, 'r') as f:
        stats = json.load(f)
    
    print(f"总Episode数: {stats.get('total_episodes', 0)}")
    print(f"平均奖励: {stats.get('avg_reward', 0):.2f}")
    print(f"最近10局平均奖励: {stats.get('avg_reward_recent', 0):.2f}")
    print(f"最佳奖励: {stats.get('best_reward', 0):.2f} (Episode {stats.get('best_episode', 0)})")
    print(f"平均损失: {stats.get('avg_loss_recent', 0):.4f}")
    print(f"当前探索率 (ε): {stats.get('current_epsilon', 0):.4f}")
    print(f"训练时间: {stats.get('training_time', 'N/A')}")
else:
    print("等待训练数据...")
EOF
        else
            echo "等待训练数据..."
        fi
        
        sleep "$UPDATE_INTERVAL"
    done
fi
