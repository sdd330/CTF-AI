#!/bin/bash
# 使用离线训练的模型启动在线训练
# 用法: bash start_online_training.sh <模型路径> <端口> [算法]

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 检查参数
if [ $# -lt 2 ]; then
    print_error "参数不足"
    echo ""
    echo "用法: bash start_online_training.sh <模型路径> <端口> [算法]"
    echo ""
    echo "参数说明:"
    echo "  模型路径: 离线训练的模型文件路径（.pth 或 .zip）"
    echo "  端口:     游戏服务器端口（例如: 34712）"
    echo "  算法:     可选，RL算法（DQN, PPO, A2C, CustomDQN），默认: CustomDQN"
    echo ""
    echo "示例:"
    echo "  bash start_online_training.sh lib/models/gym_model_ep200.pth 34712"
    echo "  bash start_online_training.sh lib/models/gym_best/best_model.pth 34712 CustomDQN"
    echo ""
    exit 1
fi

MODEL_PATH="$1"
PORT="$2"
ALGORITHM="${3:-CustomDQN}"  # 默认使用CustomDQN

# 切换到脚本所在目录的父目录（backend目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "$SCRIPT_DIR/../../.." && pwd)"
cd "$BACKEND_DIR"

print_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
print_info "🚀 启动在线训练（使用离线模型）"
print_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 检查模型文件是否存在
if [ ! -f "$MODEL_PATH" ]; then
    print_error "模型文件不存在: $MODEL_PATH"
    echo ""
    print_info "可用的模型文件:"
    if [ -d "lib/models" ]; then
        find lib/models -name "*.pth" -o -name "*.zip" | head -10
    else
        print_warning "lib/models 目录不存在"
    fi
    exit 1
fi

print_success "模型文件: $MODEL_PATH"
print_info "端口: $PORT"
print_info "算法: $ALGORITHM"
echo ""

# 检查端口是否被占用
if lsof -i :$PORT > /dev/null 2>&1; then
    print_warning "端口 $PORT 已被占用"
    read -p "是否要停止占用端口的进程？(y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "正在停止占用端口的进程..."
        lsof -ti :$PORT | xargs kill -9 2>/dev/null || true
        sleep 1
        print_success "端口已释放"
    else
        print_error "请先释放端口或使用其他端口"
        exit 1
    fi
fi

# 检查虚拟环境
if [ -d ".venv" ]; then
    PYTHON_CMD=".venv/bin/python3"
    print_success "使用虚拟环境: .venv"
else
    PYTHON_CMD="python3"
    print_warning "未找到虚拟环境，使用系统Python"
fi

# 检查模型文件类型并验证算法匹配
MODEL_EXT="${MODEL_PATH##*.}"
if [ "$MODEL_EXT" = "pth" ] && [ "$ALGORITHM" != "CustomDQN" ]; then
    print_warning ".pth 文件通常用于 CustomDQN，但你选择了 $ALGORITHM"
    print_info "如果模型是 stable-baselines3 格式，请使用 .zip 文件"
elif [ "$MODEL_EXT" = "zip" ] && [ "$ALGORITHM" = "CustomDQN" ]; then
    print_warning ".zip 文件通常用于 stable-baselines3，但你选择了 CustomDQN"
    print_info "CustomDQN 通常使用 .pth 文件"
fi

# 创建日志目录
mkdir -p /tmp/ctf-ai
LOG_FILE="/tmp/ctf-ai/training_online_$(date +%Y%m%d_%H%M%S).log"

print_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
print_info "📋 训练配置"
print_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  模型路径: $MODEL_PATH"
echo "  端口:     $PORT"
echo "  算法:     $ALGORITHM"
echo "  日志文件: $LOG_FILE"
echo ""

# 询问是否继续
read -p "是否开始训练？(Y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    print_info "已取消"
    exit 0
fi

print_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
print_info "🎮 启动在线训练..."
print_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
print_info "提示:"
echo "  - 按 Ctrl+C 停止训练（模型会自动保存）"
echo "  - 在另一个终端运行监控: bash lib/reinforcement_learning/training/monitor_training_live.sh"
echo "  - 确保前端已启动: cd frontend && pnpm dev"
echo ""

# 启动训练
print_success "正在启动训练进程..."
$PYTHON_CMD lib/reinforcement_learning/training/train_gym.py "$PORT" \
    --algorithm "$ALGORITHM" \
    --model-path "$MODEL_PATH" \
    --save-interval 10 \
    2>&1 | tee "$LOG_FILE"

# 如果训练正常退出，保存最终模型
if [ $? -eq 0 ]; then
    print_success "训练完成！"
else
    print_warning "训练被中断或出错"
fi

echo ""
print_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
print_info "📊 训练日志已保存到: $LOG_FILE"
print_info "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
