"""
网络通信管理器
设计模式：单例模式 + 发布订阅（EventEmitter）
"""

import json
import asyncio
import websocket
import threading
import time
from enum import Enum
from typing import Optional, Dict, Set, Callable, Any, List
from ..utils import Team


class SocketEvent(Enum):
    """Socket 事件类型"""
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    MESSAGE = "message"
    ERROR = "error"
    ACTIONS_RECEIVED = "actions_received"


# 事件监听器类型
EventListener = Callable[..., None]


class EventEmitter:
    """
    事件发射器（发布订阅模式）
    实现事件订阅和发布功能
    """
    
    def __init__(self):
        """初始化事件发射器"""
        self.events: Dict[SocketEvent, Set[EventListener]] = {}
    
    def on(self, event: SocketEvent, listener: EventListener):
        """
        订阅事件
        
        Args:
            event: 事件类型
            listener: 事件监听器函数
        """
        if event not in self.events:
            self.events[event] = set()
        self.events[event].add(listener)
    
    def off(self, event: SocketEvent, listener: EventListener):
        """
        取消订阅事件
        
        Args:
            event: 事件类型
            listener: 事件监听器函数
        """
        if event in self.events:
            self.events[event].discard(listener)
    
    def emit(self, event: SocketEvent, *args, **kwargs):
        """
        发布事件
        
        Args:
            event: 事件类型
            *args: 位置参数
            **kwargs: 关键字参数
        """
        if event in self.events:
            for listener in list(self.events[event]):  # 复制列表避免迭代时修改
                try:
                    listener(*args, **kwargs)
                except Exception as error:
                    print(f"Error in event listener for {event.value}: {error}")
    
    def remove_all_listeners(self, event: Optional[SocketEvent] = None):
        """
        清除所有监听器
        
        Args:
            event: 如果指定，只清除该事件的监听器；否则清除所有
        """
        if event:
            self.events.pop(event, None)
        else:
            self.events.clear()


class TeamSocket:
    """
    WebSocket 连接包装类
    管理单个队伍的 WebSocket 连接（使用 websocket-client，同步）
    """
    
    def __init__(self, url: str, team: Team, emitter: EventEmitter):
        """
        初始化队伍 Socket
        
        Args:
            url: WebSocket 服务器地址
            team: 队伍
            emitter: 事件发射器
        """
        self.url = url
        self.team = team
        self.emitter = emitter
        self.websocket: Optional[websocket.WebSocketApp] = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 1.0  # 秒
        self._running = False
        self._thread: Optional[threading.Thread] = None
    
    def connect(self):
        """
        连接 WebSocket 服务器（同步）
        """
        try:
            self._running = True
            self.websocket = websocket.WebSocketApp(
                self.url,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            
            # 在单独线程中运行 WebSocket
            self._thread = threading.Thread(target=self._run_forever, daemon=True)
            self._thread.start()
        except Exception as error:
            print(f"[SocketManager] {self.team.value} 队连接失败: {error}")
            self.emitter.emit(SocketEvent.ERROR, self.team, error)
            self._attempt_reconnect()
    
    def _run_forever(self):
        """运行 WebSocket（在单独线程中）"""
        try:
            self.websocket.run_forever()
        except Exception as error:
            print(f"[SocketManager] {self.team.value} 队 WebSocket 运行错误: {error}")
            self.emitter.emit(SocketEvent.ERROR, self.team, error)
    
    def _on_open(self, ws):
        """连接打开回调"""
        self.reconnect_attempts = 0
        self.emitter.emit(SocketEvent.CONNECT, self.team)
        print(f"[SocketManager] {self.team.value} 队已连接")
    
    def _on_message(self, ws, message: str):
        """
        消息接收回调
        
        Args:
            ws: WebSocket 连接
            message: 消息内容（JSON 字符串）
        """
        self._handle_message(message)
    
    def _handle_message(self, message: str):
        """
        处理接收到的消息
        
        Args:
            message: 消息内容（JSON 字符串）
        """
        try:
            data = json.loads(message)
            self.emitter.emit(SocketEvent.MESSAGE, self.team, data)
            
            # 优先处理错误消息：{"error": "..."}
            if isinstance(data, dict) and "error" in data:
                self.emitter.emit(SocketEvent.ERROR, self.team, data.get("error"))
                return
            
            # 处理玩家动作消息
            # 服务器返回格式: { "players": { "L0": "up", ... }, "paths": { "L0": [{x, y}, ...], ... } }
            if isinstance(data, dict) and "players" in data:
                players_obj = data.get("players", {})
                paths_obj = data.get("paths", {})
                
                if isinstance(players_obj, dict) and not isinstance(players_obj, list):
                    if len(players_obj) > 0:
                        # 有玩家动作时，发送事件
                        player_actions = {
                            "players": players_obj,
                            "paths": paths_obj
                        }
                        self.emitter.emit(SocketEvent.ACTIONS_RECEIVED, self.team, player_actions)
        except json.JSONDecodeError as error:
            print(f"[SocketManager] {self.team.value} 队消息解析失败: {error}")
            self.emitter.emit(SocketEvent.ERROR, self.team, error)
        except Exception as error:
            print(f"[SocketManager] {self.team.value} 队处理消息错误: {error}")
            self.emitter.emit(SocketEvent.ERROR, self.team, error)
    
    def _on_error(self, ws, error):
        """错误回调"""
        print(f"[SocketManager] {self.team.value} 队 WebSocket 错误: {error}")
        self.emitter.emit(SocketEvent.ERROR, self.team, error)
    
    def _on_close(self, ws, close_status_code, close_msg):
        """连接关闭回调"""
        print(f"[SocketManager] {self.team.value} 队连接已关闭")
        self.emitter.emit(SocketEvent.DISCONNECT, self.team)
        if self._running:
            self._attempt_reconnect()
    
    def _attempt_reconnect(self):
        """尝试重连（在单独线程中）"""
        if self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_attempts += 1
            delay = self.reconnect_delay * self.reconnect_attempts
            print(f"[SocketManager] {self.team.value} 队将在 {delay} 秒后尝试重连 ({self.reconnect_attempts}/{self.max_reconnect_attempts})")
            
            def reconnect():
                time.sleep(delay)
                if self._running:
                    self.connect()
            
            thread = threading.Thread(target=reconnect, daemon=True)
            thread.start()
    
    def send(self, data: str | dict) -> bool:
        """
        发送消息（同步）
        
        Args:
            data: 要发送的数据（字符串或字典）
        
        Returns:
            是否发送成功
        """
        if not self.websocket:
            return False
        
        try:
            if isinstance(data, dict):
                payload = json.dumps(data)
            else:
                payload = data
            
            self.websocket.send(payload)
            return True
        except Exception as error:
            print(f"[SocketManager] {self.team.value} 队发送消息失败: {error}")
            self.emitter.emit(SocketEvent.ERROR, self.team, error)
            return False
    
    def disconnect(self):
        """断开连接"""
        self._running = False
        if self.websocket:
            self.websocket.close()
            self.websocket = None
    
    def is_connected(self) -> bool:
        """
        检查是否已连接
        
        Returns:
            如果已连接返回True
        """
        if not self.websocket or not self._running:
            return False
        try:
            # 检查 WebSocket 连接状态
            return self.websocket.sock is not None and self.websocket.sock.connected
        except:
            return False


class SocketManager:
    """
    Socket 管理器（单例模式）
    统一管理所有 WebSocket 连接
    """
    
    _instance: Optional['SocketManager'] = None
    
    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化 Socket 管理器"""
        # 避免重复初始化
        if hasattr(self, '_initialized'):
            return
        
        self.sockets: Dict[Team, TeamSocket] = {}
        self.emitter = EventEmitter()
        self._initialized = True
    
    def connect_team(self, team: Team, url: str):
        """
        连接队伍（同步）
        
        Args:
            team: 队伍
            url: WebSocket 服务器地址
        """
        if team in self.sockets:
            self.disconnect_team(team)
        
        socket = TeamSocket(url, team, self.emitter)
        self.sockets[team] = socket
        socket.connect()
    
    def disconnect_team(self, team: Team):
        """
        断开队伍连接（同步）
        
        Args:
            team: 队伍
        """
        socket = self.sockets.get(team)
        if socket:
            socket.disconnect()
            self.sockets.pop(team, None)
    
    def send_game_init(self, params: Dict[str, Any]):
        """
        发送游戏初始化消息
        
        Args:
            params: 初始化参数
                - map_width: 地图宽度
                - map_height: 地图高度
                - walls: 墙壁列表
                - obstacles1: 障碍物1列表
                - obstacles2: 障碍物2列表
                - lteam_prison: L队监狱位置列表
                - lteam_target: L队目标位置列表
                - rteam_prison: R队监狱位置列表
                - rteam_target: R队目标位置列表
                - num_players: 玩家数量
                - num_flags: 旗帜数量
        """
        # 构建地图 payload
        map_payload = {
            "width": params["map_width"],
            "height": params["map_height"],
            "walls": [{"x": w["x"], "y": w["y"]} for w in params["walls"]],
            "obstacles": (
                [{"x": w["x"], "y": w["y"]} for w in params["obstacles1"]] +
                [{"x": w["x"], "y": w["y"]} for w in params["obstacles2"]]
            )
        }
        
        # 发送给 L 队
        if self.is_connected(Team.LEFT):
            payload = {
                "action": "init",
                "map": map_payload,
                "numPlayers": params["num_players"],
                "numFlags": params["num_flags"],
                "myteamName": "L",
                "myteamPrison": params["lteam_prison"],
                "myteamTarget": params["lteam_target"],
                "opponentPrison": params["rteam_prison"],
                "opponentTarget": params["rteam_target"]
            }
            self._send_init(Team.LEFT, payload)
        
        # 发送给 R 队
        if self.is_connected(Team.RIGHT):
            payload = {
                "action": "init",
                "map": map_payload,
                "numPlayers": params["num_players"],
                "numFlags": params["num_flags"],
                "myteamName": "R",
                "myteamPrison": params["rteam_prison"],
                "myteamTarget": params["rteam_target"],
                "opponentPrison": params["lteam_prison"],
                "opponentTarget": params["lteam_target"]
            }
            self._send_init(Team.RIGHT, payload)
    
    def _send_init(self, team: Team, payload: Dict[str, Any]) -> bool:
        """
        发送初始化消息（内部使用）
        
        Args:
            team: 队伍
            payload: 消息内容
        
        Returns:
            是否发送成功
        """
        socket = self.sockets.get(team)
        return socket.send(payload) if socket else False
    
    def send_game_status(self, params: Dict[str, Any]):
        """
        发送游戏状态更新
        
        Args:
            params: 状态参数
                - time: 游戏时间
                - lteam_player_status: L队玩家状态列表
                - lteam_flag_status: L队旗帜状态列表
                - rteam_player_status: R队玩家状态列表
                - rteam_flag_status: R队旗帜状态列表
                - lteam_score: L队分数
                - rteam_score: R队分数
        """
        # 发送给 L 队
        if self.is_connected(Team.LEFT):
            payload = {
                "action": "status",
                "time": params["time"],
                "myteamName": "L",
                "myteamPlayer": params["lteam_player_status"],
                "myteamFlag": params["lteam_flag_status"],
                "myteamScore": params["lteam_score"],
                "opponentPlayer": params["rteam_player_status"],
                "opponentFlag": params["rteam_flag_status"],
                "opponentScore": params["rteam_score"]
            }
            self._send_status(Team.LEFT, payload)
        
        # 发送给 R 队
        if self.is_connected(Team.RIGHT):
            payload = {
                "action": "status",
                "time": params["time"],
                "myteamName": "R",
                "myteamPlayer": params["rteam_player_status"],
                "myteamFlag": params["rteam_flag_status"],
                "myteamScore": params["rteam_score"],
                "opponentPlayer": params["lteam_player_status"],
                "opponentFlag": params["lteam_flag_status"],
                "opponentScore": params["lteam_score"]
            }
            self._send_status(Team.RIGHT, payload)
    
    def _send_status(self, team: Team, payload: Dict[str, Any]) -> bool:
        """
        发送状态更新（内部使用）
        
        Args:
            team: 队伍
            payload: 消息内容
        
        Returns:
            是否发送成功
        """
        socket = self.sockets.get(team)
        return socket.send(payload) if socket else False
    
    def send_game_finished(self, lteam_score: int, rteam_score: int):
        """
        发送游戏结束消息
        
        Args:
            lteam_score: L队分数
            rteam_score: R队分数
        """
        # 发送给 L 队
        if self.is_connected(Team.LEFT):
            payload = {
                "action": "finished",
                "myteamScore": lteam_score,
                "opponentScore": rteam_score
            }
            self._send_finished(Team.LEFT, payload)
        
        # 发送给 R 队
        if self.is_connected(Team.RIGHT):
            payload = {
                "action": "finished",
                "myteamScore": rteam_score,
                "opponentScore": lteam_score
            }
            self._send_finished(Team.RIGHT, payload)
    
    def _send_finished(self, team: Team, payload: Dict[str, Any]) -> bool:
        """
        发送游戏结束消息（内部使用）
        
        Args:
            team: 队伍
            payload: 消息内容
        
        Returns:
            是否发送成功
        """
        socket = self.sockets.get(team)
        return socket.send(payload) if socket else False
    
    def is_connected(self, team: Team) -> bool:
        """
        检查连接状态
        
        Args:
            team: 队伍
        
        Returns:
            如果已连接返回True
        """
        socket = self.sockets.get(team)
        return socket.is_connected() if socket else False
    
    def on(self, event: SocketEvent, listener: EventListener):
        """
        订阅事件
        
        Args:
            event: 事件类型
            listener: 事件监听器函数
        """
        self.emitter.on(event, listener)
    
    def off(self, event: SocketEvent, listener: EventListener):
        """
        取消订阅事件
        
        Args:
            event: 事件类型
            listener: 事件监听器函数
        """
        self.emitter.off(event, listener)
    
    def emit(self, event: SocketEvent, *args, **kwargs):
        """
        发布事件
        
        Args:
            event: 事件类型
            *args: 位置参数
            **kwargs: 关键字参数
        """
        self.emitter.emit(event, *args, **kwargs)
    
    def disconnect_all(self):
        """断开所有连接（同步）"""
        for socket in list(self.sockets.values()):
            socket.disconnect()
        self.sockets.clear()
        self.emitter.remove_all_listeners()
    
    def get_connection_status(self) -> Dict[Team, bool]:
        """
        获取连接状态
        
        Returns:
            各队伍的连接状态字典
        """
        return {
            Team.LEFT: self.is_connected(Team.LEFT),
            Team.RIGHT: self.is_connected(Team.RIGHT)
        }

