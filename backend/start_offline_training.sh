#!/bin/bash

# 离线训练启动脚本
# 同时启动训练和监控

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "CTF-AI 离线训练启动脚本"
echo "=========================================="
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 python3"
    exit 1
fi

# 检查必要的依赖
echo "检查依赖..."
python3 -c "import gymnasium" 2>/dev/null || {
    echo "错误: gymnasium 未安装，请运行: pip install gymnasium"
    exit 1
}

# 创建必要的目录
mkdir -p lib/models/gym_best
mkdir -p lib/models/gym_checkpoints
mkdir -p /tmp/ctf-ai

# 设置端口（默认34712）
PORT=${1:-34712}
ALGORITHM=${2:-CustomDQN}

echo "配置:"
echo "  端口: $PORT"
echo "  算法: $ALGORITHM"
echo "  模式: 离线训练"
echo ""

# 启动训练（后台运行）
echo "启动离线训练..."
python3 lib/reinforcement_learning/training/train_gym.py "$PORT" \
    --algorithm "$ALGORITHM" \
    --train-offline \
    --save-interval 10 \
    > /tmp/ctf-ai/training_output.log 2>&1 &
TRAIN_PID=$!

echo "训练进程 PID: $TRAIN_PID"
echo "训练日志: /tmp/ctf-ai/training_output.log"
echo ""

# 等待一下，让训练开始
sleep 3

# 启动监控（在另一个终端或后台）
echo "启动训练监控..."
echo "提示: 监控工具将在新窗口中打开，或按 Ctrl+C 停止训练"
echo ""

# 尝试启动可视化监控（如果matplotlib可用）
if python3 -c "import matplotlib" 2>/dev/null; then
    python3 lib/reinforcement_learning/training/visualize_training.py \
        /tmp/ctf-ai/training_stats.json \
        5 &
    MONITOR_PID=$!
    echo "监控进程 PID: $MONITOR_PID"
    echo ""
else
    echo "警告: matplotlib 未安装，无法启动可视化监控"
    echo "可以手动运行: python3 lib/reinforcement_learning/training/visualize_training.py"
    echo ""
fi

# 显示训练状态
echo "=========================================="
echo "训练已启动"
echo "=========================================="
echo "查看训练日志: tail -f /tmp/ctf-ai/training_output.log"
echo "查看统计文件: cat /tmp/ctf-ai/training_stats.json"
echo "停止训练: kill $TRAIN_PID"
echo ""
echo "按 Ctrl+C 停止训练和监控"
echo "=========================================="

# 等待用户中断
trap "echo ''; echo '正在停止训练...'; kill $TRAIN_PID 2>/dev/null; kill $MONITOR_PID 2>/dev/null; exit 0" INT TERM

# 等待训练进程
wait $TRAIN_PID
