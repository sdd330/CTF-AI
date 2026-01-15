"""
服务器启动器
用于启动和管理游戏服务器进程
"""

import subprocess
import threading
import os
import sys
import signal
import time
import socket


def check_port(port: int) -> bool:
    """检查端口是否被占用"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result == 0


def kill_port(port: int) -> None:
    """终止占用端口的进程"""
    try:
        if os.name == 'nt':
            _kill_port_windows(port)
        else:
            _kill_port_unix(port)
    except FileNotFoundError:
        print(f"  警告：无法找到 lsof 命令，请手动终止占用端口 {port} 的进程")
    except Exception as e:
        print(f"  警告：清理端口 {port} 时出错: {e}")


def _kill_port_windows(port: int) -> None:
    """Windows平台终止端口占用"""
    result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
    for line in result.stdout.split('\n'):
        if f':{port}' in line and 'LISTENING' in line:
            parts = line.split()
            if len(parts) >= 5:
                try:
                    subprocess.run(['taskkill', '/F', '/PID', parts[-1]], capture_output=True)
                    print(f"  已终止进程 {parts[-1]} (端口 {port})")
                except Exception:
                    pass


def _kill_port_unix(port: int) -> None:
    """Unix平台终止端口占用"""
    result = subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True, text=True)
    if result.stdout.strip():
        for pid in result.stdout.strip().split('\n'):
            try:
                os.kill(int(pid), signal.SIGTERM)
                print(f"  已终止进程 {pid} (端口 {port})")
                time.sleep(0.5)
            except ProcessLookupError:
                pass
            except Exception as e:
                print(f"  警告：无法终止进程 {pid}: {e}")


def print_output(pipe, prefix: str) -> None:
    """实时打印进程输出"""
    try:
        for line in iter(pipe.readline, ''):
            if line:
                print(f"[{prefix}] {line.rstrip()}")
        pipe.close()
    except Exception as e:
        print(f"[{prefix}] 输出读取错误: {e}")


def start_server(server_path: str, port: int, prefix: str):
    """启动服务器并返回进程对象"""
    server = subprocess.Popen(
        [sys.executable, server_path, str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    print(f"  PID: {server.pid}")

    output_thread = threading.Thread(
        target=print_output,
        args=(server.stdout, prefix),
        daemon=True
    )
    output_thread.start()

    return server


def ensure_port_free(port: int) -> bool:
    """确保端口空闲"""
    if check_port(port):
        print(f"⚠️  端口 {port} 已被占用，正在清理...")
        kill_port(port)
        time.sleep(2)
        if check_port(port):
            print(f"❌ 错误：端口 {port} 仍被占用，请手动终止相关进程")
            return False
    return True
