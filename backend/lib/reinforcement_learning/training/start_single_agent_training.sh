#!/bin/bash
# 单智能体训练启动脚本
# 启动单个智能体的强化学习训练

PORT=${1:-34712}  # 默认端口 34712
ALGORITHM=${2:-CustomDQN}  # 默认算法 CustomDQN（不需要 stable-baselines3）
MODE=${3:-offline}  # offline 或 online

echo "=========================================="
echo "启动单智能体训练"
echo "=========================================="
echo "端口: $PORT"
echo "算法: $ALGORITHM"
echo "模式: $MODE"
echo "=========================================="

# 切换到backend目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
cd "$BACKEND_DIR"

# 检查虚拟环境
if [ -d ".venv" ]; then
    PYTHON_CMD=".venv/bin/python3"
    echo "使用虚拟环境: .venv"
    source .venv/bin/activate
else
    PYTHON_CMD="python3"
    echo "使用系统Python"
fi

# 检查依赖
echo ""
echo "检查依赖..."
if ! $PYTHON_CMD -c "import torch" 2>/dev/null; then
    echo "❌ 错误: PyTorch 未安装"
    echo "请先安装依赖:"
    echo "  pip install torch numpy matplotlib"
    echo "或安装所有依赖:"
    echo "  pip install -r requirements.txt"
    exit 1
fi

if ! $PYTHON_CMD -c "import gymnasium" 2>/dev/null; then
    echo "⚠️  警告: gymnasium 未安装"
    echo "安装命令: pip install gymnasium"
    echo "继续使用 CustomDQN（不需要 gymnasium）..."
fi

# 创建模型目录和日志目录
mkdir -p lib/models
mkdir -p /tmp/ctf-ai

# 设置 PYTHONPATH
export PYTHONPATH="$BACKEND_DIR:$PYTHONPATH"

# 构建命令
TRAIN_CMD="$PYTHON_CMD lib/reinforcement_learning/training/train_gym.py $PORT --algorithm $ALGORITHM"

if [ "$MODE" = "offline" ]; then
    TRAIN_CMD="$TRAIN_CMD --train-offline"
    echo ""
    echo "[离线训练模式] 不连接游戏服务器，使用模拟环境"
else
    echo ""
    echo "[在线训练模式] 连接游戏服务器，实时训练"
    echo "确保游戏服务器已启动或前端已连接"
fi

echo ""
echo "启动训练..."
echo "命令: $TRAIN_CMD"
echo ""
echo "按 Ctrl+C 停止训练"
echo "=========================================="
echo ""

# 执行训练（将输出保存到日志文件）
mkdir -p /tmp/ctf-ai
LOG_FILE="/tmp/ctf-ai/training_offline_$(date +%Y%m%d_%H%M%S).log"
echo "训练日志将保存到: $LOG_FILE"
echo ""

$TRAIN_CMD 2>&1 | tee "$LOG_FILE"
