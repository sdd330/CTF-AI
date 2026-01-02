#!/bin/bash
# 运行 native 项目的 pytest 测试

set -e

echo "安装测试依赖..."
pip3 install -r requirements.txt

echo ""
echo "运行 pytest 测试..."
pytest "$@"

