#!/usr/bin/env python3
"""
清理训练日志脚本
清理系统临时目录 /tmp/ctf-ai/ 下的所有日志文件
"""

import os
import sys
import glob
from pathlib import Path

LOG_DIR = "/tmp/ctf-ai"


def clear_logs():
    """清理训练日志文件"""
    print("=" * 60)
    print("清理训练日志")
    print("=" * 60)
    print(f"日志目录: {LOG_DIR}")
    print("=" * 60)
    print()
    
    # 检查目录是否存在
    if not os.path.exists(LOG_DIR):
        print(f"ℹ️  日志目录不存在: {LOG_DIR}")
        print("无需清理")
        return
    
    # 统计文件数量
    log_files = list(Path(LOG_DIR).glob("*.log"))
    json_files = list(Path(LOG_DIR).glob("*.json"))
    csv_files = list(Path(LOG_DIR).glob("*.csv"))
    
    log_count = len(log_files)
    json_count = len(json_files)
    csv_count = len(csv_files)
    total_count = log_count + json_count + csv_count
    
    if total_count == 0:
        print("ℹ️  没有找到日志文件")
        return
    
    print("找到以下文件:")
    print(f"  - 日志文件 (.log): {log_count} 个")
    print(f"  - 统计文件 (.json): {json_count} 个")
    print(f"  - CSV文件 (.csv): {csv_count} 个")
    print(f"  - 总计: {total_count} 个")
    print()
    
    # 显示文件列表（最多显示10个）
    print("文件列表（最多显示10个）:")
    all_files = log_files + json_files + csv_files
    for i, file_path in enumerate(all_files[:10], 1):
        try:
            size = file_path.stat().st_size
            size_str = f"{size / 1024:.1f}KB" if size < 1024 * 1024 else f"{size / (1024 * 1024):.1f}MB"
            print(f"  - {file_path.name} ({size_str})")
        except Exception:
            print(f"  - {file_path.name}")
    
    if total_count > 10:
        print(f"  ... 还有 {total_count - 10} 个文件")
    print()
    
    # 确认删除
    if len(sys.argv) > 1 and sys.argv[1] == "--yes":
        confirm = "yes"
    else:
        confirm = input("确认删除所有日志文件？(yes/no): ").strip().lower()
    
    if confirm not in ['yes', 'y']:
        print("操作已取消")
        return
    
    # 删除文件
    print()
    print("正在清理...")
    deleted = 0
    errors = 0
    
    for file_path in all_files:
        try:
            file_path.unlink()
            deleted += 1
        except Exception as e:
            errors += 1
            print(f"  ⚠️  删除失败 {file_path.name}: {e}")
    
    # 尝试删除空目录
    try:
        gym_training_dir = Path(LOG_DIR) / "gym_training"
        if gym_training_dir.exists() and not any(gym_training_dir.iterdir()):
            gym_training_dir.rmdir()
    except Exception:
        pass
    
    try:
        gym_eval_dir = Path(LOG_DIR) / "gym_eval"
        if gym_eval_dir.exists() and not any(gym_eval_dir.iterdir()):
            gym_eval_dir.rmdir()
    except Exception:
        pass
    
    try:
        log_dir_path = Path(LOG_DIR)
        if log_dir_path.exists() and not any(log_dir_path.iterdir()):
            log_dir_path.rmdir()
    except Exception:
        pass
    
    print()
    print("=" * 60)
    if errors == 0:
        print(f"✅ 清理完成！已删除 {deleted} 个文件")
    else:
        print(f"⚠️  清理完成，但有 {errors} 个文件删除失败")
        print(f"   已删除 {deleted} 个文件")
    print("=" * 60)


if __name__ == "__main__":
    clear_logs()
