#!/bin/bash
# Frontend 启动脚本
# 自动安装依赖并启动开发服务器

set -e

echo "=========================================="
echo "CTF-AI Frontend 启动脚本"
echo "=========================================="

# 检查 Node.js 和 pnpm
if ! command -v node &> /dev/null; then
    echo "错误: 未找到 Node.js，请先安装 Node.js"
    exit 1
fi

if ! command -v pnpm &> /dev/null; then
    echo "错误: 未找到 pnpm，请先安装 pnpm"
    echo "安装命令: npm install -g pnpm"
    exit 1
fi

echo "Node.js 版本: $(node --version)"
echo "pnpm 版本: $(pnpm --version)"
echo ""

# 检查并安装依赖
if [ ! -d "node_modules" ]; then
    echo "检测到 node_modules 不存在，开始安装依赖..."
    pnpm install
    echo "依赖安装完成！"
else
    echo "依赖已存在，跳过安装"
fi

echo ""
echo "启动开发服务器..."
echo "访问地址: http://localhost:8000"
echo "按 Ctrl+C 停止服务器"
echo "=========================================="
echo ""

# 启动开发服务器
pnpm dev
