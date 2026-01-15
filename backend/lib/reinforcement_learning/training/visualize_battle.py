#!/usr/bin/env python3
"""
可视化RL模型对抗脚本
启动两个服务器：一个使用训练好的RL模型，一个使用规则策略
"""

import time
import os
import sys

from .server_launcher import ensure_port_free, start_server, check_port

PORT_RL = 34712
PORT_RULE = 34713

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(SCRIPT_DIR)))
MODEL_PATH = os.path.join(BACKEND_DIR, "lib", "models", "dqn_model_latest.pth")


def main():
    print("=" * 60)
    print("RL模型对抗可视化")
    print("=" * 60)

    if not os.path.exists(MODEL_PATH):
        print(f"❌ 错误：模型文件不存在: {MODEL_PATH}")
        print("   请先训练模型或检查模型路径")
        sys.exit(1)

    print(f"✅ 模型文件: {MODEL_PATH}")

    if not ensure_port_free(PORT_RL) or not ensure_port_free(PORT_RULE):
        sys.exit(1)

    os.makedirs(os.path.join(BACKEND_DIR, "lib", "models"), exist_ok=True)

    print(f"\n启动服务器...")
    print(f"  L队 (RL模型): 端口 {PORT_RL}")
    print(f"  R队 (规则策略): 端口 {PORT_RULE}")
    print(f"\n前端配置:")
    print(f"  L队: ws://localhost:{PORT_RL}")
    print(f"  R队: ws://0.0.0.0:{PORT_RULE}")
    print("\n" + "=" * 60)

    server_path = os.path.join(BACKEND_DIR, "server.py")

    print(f"\n[1/2] 启动L队 - RL模型服务器 (端口 {PORT_RL})...")
    rl_server = start_server(server_path, PORT_RL, "L队")
    time.sleep(3)

    if rl_server.poll() is not None:
        print(f"❌ L队服务器启动失败 (退出码: {rl_server.returncode})")
        sys.exit(1)

    if check_port(PORT_RL):
        print(f"  ✅ L队已启动（使用RL模型: {MODEL_PATH}）")
    else:
        print(f"⚠️  警告：端口 {PORT_RL} 似乎未在监听，但进程仍在运行")

    print(f"\n[2/2] 启动R队 - 规则策略服务器 (端口 {PORT_RULE})...")
    rule_server = start_server(server_path, PORT_RULE, "R队")
    time.sleep(3)

    if rule_server.poll() is not None:
        print(f"❌ R队服务器启动失败 (退出码: {rule_server.returncode})")
        rl_server.terminate()
        sys.exit(1)

    if check_port(PORT_RULE):
        print(f"  ✅ R队已启动（使用规则策略，RL已禁用）")
    else:
        print(f"⚠️  警告：端口 {PORT_RULE} 似乎未在监听，但进程仍在运行")

    _print_server_info(rl_server, rule_server)
    _run_loop(rl_server, rule_server)


def _print_server_info(rl_server, rule_server):
    """打印服务器信息"""
    frontend_dir = os.path.join(BACKEND_DIR, "..", "frontend")
    print("\n" + "=" * 60)
    print("两个服务器已启动")
    print("=" * 60)
    print(f"L队 (RL模型) PID: {rl_server.pid}")
    print(f"R队 (规则策略) PID: {rule_server.pid}")
    print("\n前端访问:")
    print(f"  1. 启动前端服务器:")
    print(f"     cd {frontend_dir} && python3 -m http.server 8000")
    print(f"  2. 在浏览器打开:")
    print(f"     http://localhost:8000/index.html")
    print("\n按 Ctrl+C 停止服务器")
    print("=" * 60)


def _run_loop(rl_server, rule_server):
    """运行主循环"""
    def cleanup():
        print("\n\n正在停止服务器...")
        rl_server.terminate()
        rule_server.terminate()
        try:
            rl_server.wait(timeout=5)
            rule_server.wait(timeout=5)
        except Exception:
            rl_server.kill()
            rule_server.kill()
        print("服务器已停止")

    try:
        while True:
            time.sleep(1)
            if rl_server.poll() is not None:
                print(f"\n⚠️  L队服务器已停止 (退出码: {rl_server.returncode})")
                break
            if rule_server.poll() is not None:
                print(f"\n⚠️  R队服务器已停止 (退出码: {rule_server.returncode})")
                break
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()


if __name__ == "__main__":
    main()
