#!/bin/bash
# 清理训练日志脚本
# 清理系统临时目录 /tmp/ctf-ai/ 下的所有日志文件

LOG_DIR="/tmp/ctf-ai"

echo "=========================================="
echo "清理训练日志"
echo "=========================================="
echo "日志目录: $LOG_DIR"
echo "=========================================="
echo ""

# 检查目录是否存在
if [ ! -d "$LOG_DIR" ]; then
    echo "ℹ️  日志目录不存在: $LOG_DIR"
    echo "无需清理"
    exit 0
fi

# 统计文件数量
LOG_COUNT=$(find "$LOG_DIR" -name "*.log" -type f 2>/dev/null | wc -l | tr -d ' ')
JSON_COUNT=$(find "$LOG_DIR" -name "*.json" -type f 2>/dev/null | wc -l | tr -d ' ')
CSV_COUNT=$(find "$LOG_DIR" -name "*.csv" -type f 2>/dev/null | wc -l | tr -d ' ')
TOTAL_COUNT=$((LOG_COUNT + JSON_COUNT + CSV_COUNT))

if [ "$TOTAL_COUNT" -eq 0 ]; then
    echo "ℹ️  没有找到日志文件"
    exit 0
fi

echo "找到以下文件:"
echo "  - 日志文件 (.log): $LOG_COUNT 个"
echo "  - 统计文件 (.json): $JSON_COUNT 个"
echo "  - CSV文件 (.csv): $CSV_COUNT 个"
echo "  - 总计: $TOTAL_COUNT 个"
echo ""

# 显示文件列表（最多显示10个）
echo "文件列表（最多显示10个）:"
find "$LOG_DIR" -type f \( -name "*.log" -o -name "*.json" -o -name "*.csv" \) 2>/dev/null | head -10 | while read -r file; do
    size=$(du -h "$file" 2>/dev/null | cut -f1)
    echo "  - $(basename "$file") ($size)"
done
if [ "$TOTAL_COUNT" -gt 10 ]; then
    echo "  ... 还有 $((TOTAL_COUNT - 10)) 个文件"
fi
echo ""

# 确认删除
read -p "确认删除所有日志文件？(yes/no): " confirm
if [ "$confirm" != "yes" ] && [ "$confirm" != "y" ]; then
    echo "操作已取消"
    exit 0
fi

# 删除文件
echo ""
echo "正在清理..."
DELETED=0
ERRORS=0

# 删除日志文件
if [ "$LOG_COUNT" -gt 0 ]; then
    find "$LOG_DIR" -name "*.log" -type f 2>/dev/null | while read -r file; do
        if rm -f "$file" 2>/dev/null; then
            DELETED=$((DELETED + 1))
        else
            ERRORS=$((ERRORS + 1))
            echo "  ⚠️  删除失败: $file"
        fi
    done
fi

# 删除JSON文件
if [ "$JSON_COUNT" -gt 0 ]; then
    find "$LOG_DIR" -name "*.json" -type f 2>/dev/null | while read -r file; do
        if rm -f "$file" 2>/dev/null; then
            DELETED=$((DELETED + 1))
        else
            ERRORS=$((ERRORS + 1))
            echo "  ⚠️  删除失败: $file"
        fi
    done
fi

# 删除CSV文件
if [ "$CSV_COUNT" -gt 0 ]; then
    find "$LOG_DIR" -name "*.csv" -type f 2>/dev/null | while read -r file; do
        if rm -f "$file" 2>/dev/null; then
            DELETED=$((DELETED + 1))
        else
            ERRORS=$((ERRORS + 1))
            echo "  ⚠️  删除失败: $file"
        fi
    done
fi

# 尝试删除空目录
if [ -d "$LOG_DIR/gym_training" ]; then
    rmdir "$LOG_DIR/gym_training" 2>/dev/null
fi
if [ -d "$LOG_DIR/gym_eval" ]; then
    rmdir "$LOG_DIR/gym_eval" 2>/dev/null
fi
rmdir "$LOG_DIR" 2>/dev/null

echo ""
echo "=========================================="
if [ "$ERRORS" -eq 0 ]; then
    echo "✅ 清理完成！已删除 $DELETED 个文件"
else
    echo "⚠️  清理完成，但有 $ERRORS 个文件删除失败"
    echo "   已删除 $DELETED 个文件"
fi
echo "=========================================="
