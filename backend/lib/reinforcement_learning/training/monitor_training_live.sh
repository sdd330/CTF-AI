#!/bin/bash
# 实时监控训练过程

cd "$(dirname "$0")/../../.."

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 训练过程实时监控"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 检查训练进程
TRAIN_PID=$(ps aux | grep "train_gym.py" | grep -v grep | awk '{print $2}' | head -1)
if [ -z "$TRAIN_PID" ]; then
    echo "❌ 未检测到训练进程"
    echo "请先启动训练: bash lib/reinforcement_learning/training/start_single_agent_training.sh 34712 CustomDQN offline"
    exit 1
fi

echo "✅ 训练进程运行中 (PID: $TRAIN_PID)"
echo ""

# 查找最新日志文件（在系统临时目录）
mkdir -p /tmp/ctf-ai
LATEST_LOG=$(ls -t /tmp/ctf-ai/training_offline_*.log 2>/dev/null | head -1)
if [ -z "$LATEST_LOG" ]; then
    echo "❌ 未找到训练日志文件（在 /tmp/ctf-ai 目录）"
    exit 1
fi

echo "📊 日志文件: $LATEST_LOG"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "实时训练输出（按 Ctrl+C 退出监控）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 实时跟踪日志
tail -f "$LATEST_LOG" 2>/dev/null | grep -E "Episode|Statistics|Average|Best|Loss|Epsilon|Training|模型保存" --line-buffered
