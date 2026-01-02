"""
WebSocket 处理器
负责 WebSocket 连接和消息处理
"""

import asyncio
import json
import threading
import websockets
from typing import Callable, Optional

from .request_handler import RequestHandler


class WebSocketHandler:
    """WebSocket 处理器 - 单一职责：处理 WebSocket 连接和消息"""
    
    def __init__(self, request_handler: RequestHandler):
        """
        初始化 WebSocket 处理器
        
        Args:
            request_handler: 请求处理器实例
        """
        self.request_handler = request_handler
        self.lock = threading.Lock()
    
    async def handle_connection(self, websocket, port: int):
        """
        处理单个 WebSocket 连接
        
        Args:
            websocket: WebSocket 连接对象
            port: 服务器端口（用于日志）
        """
        print(f"✅ [WebSocketHandler] 客户端已连接，端口: {port}")
        
        async for message in websocket:
            try:
                # 解析消息
                req = self.request_handler.parse_message(message)
                if req is None:
                    continue
                
                # 处理请求（需要加锁保护）
                with self.lock:
                    response = self.request_handler.handle_request(req)
                
                # 发送响应（仅 status 请求需要响应）
                if response is not None:
                    await websocket.send(json.dumps(response))
                    
            except Exception as e:
                print(f"❌ [WebSocketHandler] 处理消息时出错: {e}")
                import traceback
                traceback.print_exc()
    
    async def create_handler(self, port: int):
        """
        创建 WebSocket 消息处理函数
        
        Args:
            port: 服务器端口
            
        Returns:
            WebSocket 处理函数
        """
        async def handler(websocket):
            await self.handle_connection(websocket, port)
        
        return handler

