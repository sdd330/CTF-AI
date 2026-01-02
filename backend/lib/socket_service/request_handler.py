"""
请求处理器
负责处理不同类型的游戏请求
"""

import json
from typing import Dict, Callable, Optional


class RequestHandler:
    """请求处理器 - 单一职责：处理游戏请求"""
    
    def __init__(self, start_fn: Callable, plan_fn: Callable, end_fn: Callable):
        """
        初始化请求处理器
        
        Args:
            start_fn: 游戏开始时的回调函数
            plan_fn: 每帧计划动作的回调函数
            end_fn: 游戏结束时的回调函数
        """
        self.start_fn = start_fn
        self.plan_fn = plan_fn
        self.end_fn = end_fn
    
    def parse_message(self, message: str) -> Optional[Dict]:
        """
        解析 WebSocket 消息
        
        Args:
            message: WebSocket 消息字符串
            
        Returns:
            解析后的请求字典，如果解析失败返回 None
        """
        try:
            return json.loads(message)
        except json.JSONDecodeError as e:
            print(f"❌ [RequestHandler] JSON 解析失败: {e}")
            return None
    
    def handle_init_request(self, req: Dict) -> None:
        """
        处理游戏初始化请求
        
        Args:
            req: 初始化请求字典
        """
        team_name = req.get("myteamName", "未知")
        team_prefix = f"{team_name}队"
        print(f"🎮 [{team_prefix}] [RequestHandler] 处理游戏初始化请求...")
        try:
            self.start_fn(req)
            print(f"✅ [{team_prefix}] [RequestHandler] 游戏初始化完成")
        except Exception as e:
            print(f"❌ [{team_prefix}] [RequestHandler] 游戏初始化失败: {e}")
            raise
    
    def handle_status_request(self, req: Dict) -> Optional[Dict]:
        """
        处理游戏状态更新请求
        
        Args:
            req: 状态请求字典
            
        Returns:
            响应字典，包含 actions 和 paths，如果处理失败返回 None
        """
        team_name = req.get("myteamName", "未知")
        team_prefix = f"{team_name}队"
        print(f"⚙️  [{team_prefix}] [RequestHandler] 处理游戏状态更新请求...")
        try:
            result = self.plan_fn(req)
            moves = result.get("actions", {})
            paths = result.get("paths", {})
            timings = result.get("timings", {})
            return {"players": moves, "paths": paths, "timings": timings}
        except Exception as e:
            print(f"❌ [{team_prefix}] [RequestHandler] 处理状态请求失败: {e}")
            return None
    
    def handle_finished_request(self, req: Dict) -> None:
        """
        处理游戏结束请求
        
        Args:
            req: 结束请求字典
        """
        team_name = req.get("myteamName", "未知")
        team_prefix = f"{team_name}队"
        print(f"🏁 [{team_prefix}] [RequestHandler] 处理游戏结束请求...")
        try:
            self.end_fn(req)
            print(f"✅ [{team_prefix}] [RequestHandler] 游戏结束处理完成")
        except Exception as e:
            print(f"❌ [{team_prefix}] [RequestHandler] 游戏结束处理失败: {e}")
            raise
    
    def handle_request(self, req: Dict) -> Optional[Dict]:
        """
        根据请求类型分发处理
        
        Args:
            req: 请求字典
            
        Returns:
            响应字典（仅 status 请求返回），其他返回 None
        """
        action = req.get("action")
        print(f"📨 [RequestHandler] 收到请求，action: {action}")
        
        if action == "init":
            self.handle_init_request(req)
            return None
        elif action == "status":
            return self.handle_status_request(req)
        elif action == "finished":
            self.handle_finished_request(req)
            return None
        else:
            print(f"⚠️  [RequestHandler] 未知的 action: {action}")
            return None

