"""
WebSocket游戏服务器模块
处理客户端连接和游戏消息
"""

import asyncio
import websockets
from typing import Callable

from .socket_service import RequestHandler, WebSocketHandler


async def run_game_server(port: int, start_fn: Callable, plan_fn: Callable, end_fn: Callable):
    """
    运行游戏服务器
    
    Args:
        port: 服务器端口
        start_fn: 游戏开始时的回调函数
        plan_fn: 每帧计划动作的回调函数
        end_fn: 游戏结束时的回调函数
    """
    # 创建请求处理器
    request_handler = RequestHandler(start_fn, plan_fn, end_fn)
    
    # 创建 WebSocket 处理器
    ws_handler = WebSocketHandler(request_handler)
    
    # 创建处理函数
    handler = await ws_handler.create_handler(port)
    
    print(f"🚀 [Server] 启动服务器，端口: {port}...")
    async with websockets.serve(handler, "0.0.0.0", port):
        await asyncio.Future()

