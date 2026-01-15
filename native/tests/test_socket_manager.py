"""
SocketManager 单元测试
测试网络通信管理器的所有功能
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
import json
from native.managers import SocketManager, SocketEvent, EventEmitter
from native.utils import Team


@pytest.mark.unit
@pytest.mark.network
class TestEventEmitter:
    """EventEmitter 测试"""
    
    def test_on(self):
        """测试订阅事件"""
        emitter = EventEmitter()
        called = [False]
        
        def listener():
            called[0] = True
        
        emitter.on(SocketEvent.CONNECT, listener)
        assert listener in emitter.events[SocketEvent.CONNECT]
    
    def test_off(self):
        """测试取消订阅事件"""
        emitter = EventEmitter()
        called = [False]
        
        def listener():
            called[0] = True
        
        emitter.on(SocketEvent.CONNECT, listener)
        emitter.off(SocketEvent.CONNECT, listener)
        assert listener not in emitter.events.get(SocketEvent.CONNECT, set())
    
    def test_emit(self):
        """测试发布事件"""
        emitter = EventEmitter()
        called = [False]
        args = None
        
        def listener(*args, **kwargs):
            called[0] = True
            args = (args, kwargs)
        
        emitter.on(SocketEvent.CONNECT, listener)
        emitter.emit(SocketEvent.CONNECT, Team.LEFT)
        
        assert called[0] is True
    
    def test_emit_multiple_listeners(self):
        """测试多个监听器"""
        emitter = EventEmitter()
        listener1 = Mock()
        listener2 = Mock()
        
        emitter.on(SocketEvent.CONNECT, listener1)
        emitter.on(SocketEvent.CONNECT, listener2)
        emitter.emit(SocketEvent.CONNECT, Team.LEFT)
        
        listener1.assert_called_once_with(Team.LEFT)
        listener2.assert_called_once_with(Team.LEFT)
    
    def test_emit_error_handling(self):
        """测试错误处理"""
        emitter = EventEmitter()
        
        def error_listener():
            raise ValueError("Test error")
        
        emitter.on(SocketEvent.CONNECT, error_listener)
        # 不应该抛出异常
        emitter.emit(SocketEvent.CONNECT)
    
    def test_remove_all_listeners(self):
        """测试清除所有监听器"""
        emitter = EventEmitter()
        called = [False]
        
        def listener():
            called[0] = True
        
        emitter.on(SocketEvent.CONNECT, listener)
        emitter.on(SocketEvent.DISCONNECT, listener)
        
        emitter.remove_all_listeners()
        assert len(emitter.events) == 0
    
    def test_remove_all_listeners_specific_event(self):
        """测试清除特定事件的监听器"""
        emitter = EventEmitter()
        called = [False]
        
        def listener():
            called[0] = True
        
        emitter.on(SocketEvent.CONNECT, listener)
        emitter.on(SocketEvent.DISCONNECT, listener)
        
        emitter.remove_all_listeners(SocketEvent.CONNECT)
        assert SocketEvent.CONNECT not in emitter.events
        assert SocketEvent.DISCONNECT in emitter.events


@pytest.mark.unit
@pytest.mark.network
class TestSocketManager:
    """SocketManager 测试"""
    
    def test_singleton_pattern(self):
        """测试单例模式"""
        SocketManager._instance = None
        manager1 = SocketManager()
        manager2 = SocketManager()
        
        # 应该是同一个实例
        assert manager1 is manager2
        
        # 清理
        SocketManager._instance = None
    
    def test_on_off(self):
        """测试事件订阅和取消订阅"""
        SocketManager._instance = None
        manager = SocketManager()
        listener = Mock()
        
        manager.on(SocketEvent.CONNECT, listener)
        manager.emit(SocketEvent.CONNECT, Team.LEFT)
        
        listener.assert_called_once_with(Team.LEFT)
        
        listener.reset_mock()
        manager.off(SocketEvent.CONNECT, listener)
        manager.emit(SocketEvent.CONNECT, Team.LEFT)
        
        listener.assert_not_called()
        
        # 清理
        SocketManager._instance = None
    
    def test_is_connected(self):
        """测试检查连接状态"""
        SocketManager._instance = None
        manager = SocketManager()
        
        # 未连接时应该返回 False
        assert manager.is_connected(Team.LEFT) is False
        assert manager.is_connected(Team.RIGHT) is False
        
        # 清理
        SocketManager._instance = None
    
    def test_get_connection_status(self):
        """测试获取连接状态"""
        SocketManager._instance = None
        manager = SocketManager()
        
        status = manager.get_connection_status()
        
        assert Team.LEFT in status
        assert Team.RIGHT in status
        assert status[Team.LEFT] is False
        assert status[Team.RIGHT] is False
        
        # 清理
        SocketManager._instance = None
    
    @patch('native.managers.socket.team_socket.websocket')
    def test_connect_team(self, mock_websocket):
        """测试连接队伍"""
        SocketManager._instance = None
        manager = SocketManager()
        
        # Mock WebSocketApp
        mock_ws = MagicMock()
        mock_websocket.WebSocketApp = MagicMock(return_value=mock_ws)
        
        # 连接队伍
        manager.connect_team(Team.LEFT, "ws://localhost:34712")
        
        # 验证 WebSocketApp 被创建
        mock_websocket.WebSocketApp.assert_called_once()
        
        # 验证 socket 被添加到字典
        assert Team.LEFT in manager.sockets
        
        # 清理
        SocketManager._instance = None
    
    @patch('native.managers.socket.team_socket.websocket')
    def test_disconnect_team(self, mock_websocket):
        """测试断开队伍连接"""
        SocketManager._instance = None
        manager = SocketManager()
        
        # 先连接
        mock_ws = MagicMock()
        mock_websocket.WebSocketApp = MagicMock(return_value=mock_ws)
        
        manager.connect_team(Team.LEFT, "ws://localhost:34712")
        
        # 断开连接
        manager.disconnect_team(Team.LEFT)
        
        # 验证 close 被调用
        mock_ws.close.assert_called_once()
        
        # 验证 socket 被移除
        assert Team.LEFT not in manager.sockets
        
        # 清理
        SocketManager._instance = None
    
    @patch('native.managers.socket.team_socket.websocket')
    def test_send_game_init(self, mock_websocket):
        """测试发送游戏初始化消息"""
        SocketManager._instance = None
        manager = SocketManager()
        
        mock_ws = MagicMock()
        mock_ws.sock = MagicMock()
        mock_ws.sock.connected = True
        mock_websocket.WebSocketApp = MagicMock(return_value=mock_ws)
        
        # 连接队伍
        manager.connect_team(Team.LEFT, "ws://localhost:34712")
        manager.connect_team(Team.RIGHT, "ws://localhost:34713")
        
        # 发送初始化消息
        params = {
            "map_width": 20,
            "map_height": 20,
            "walls": [{"x": 0, "y": 0}],
            "obstacles1": [],
            "obstacles2": [],
            "lteam_prison": [(1, 10)],
            "lteam_target": [(2, 10)],
            "rteam_prison": [(19, 10)],
            "rteam_target": [(18, 10)],
            "num_players": 3,
            "num_flags": 3
        }
        
        manager.send_game_init(params)
        
        # 验证 send 被调用（每个队伍一次）
        assert mock_ws.send.call_count == 2
        
        # 清理
        SocketManager._instance = None
    
    @patch('native.managers.socket.team_socket.websocket')
    def test_send_game_status(self, mock_websocket):
        """测试发送游戏状态"""
        SocketManager._instance = None
        manager = SocketManager()
        
        mock_ws = MagicMock()
        mock_ws.sock = MagicMock()
        mock_ws.sock.connected = True
        mock_websocket.WebSocketApp = MagicMock(return_value=mock_ws)
        
        # 连接队伍
        manager.connect_team(Team.LEFT, "ws://localhost:34712")
        manager.connect_team(Team.RIGHT, "ws://localhost:34713")
        
        # 发送状态更新
        params = {
            "time": 1000,
            "lteam_player_status": [],
            "lteam_flag_status": [],
            "rteam_player_status": [],
            "rteam_flag_status": [],
            "lteam_score": 0,
            "rteam_score": 0
        }
        
        manager.send_game_status(params)
        
        # 验证 send 被调用（每个队伍一次）
        assert mock_ws.send.call_count == 2
        
        # 清理
        SocketManager._instance = None
    
    @patch('native.managers.socket.team_socket.websocket')
    def test_send_game_finished(self, mock_websocket):
        """测试发送游戏结束消息"""
        SocketManager._instance = None
        manager = SocketManager()
        
        mock_ws = MagicMock()
        mock_ws.sock = MagicMock()
        mock_ws.sock.connected = True
        mock_websocket.WebSocketApp = MagicMock(return_value=mock_ws)
        
        # 连接队伍
        manager.connect_team(Team.LEFT, "ws://localhost:34712")
        manager.connect_team(Team.RIGHT, "ws://localhost:34713")
        
        # 发送游戏结束消息
        manager.send_game_finished(5, 3)
        
        # 验证 send 被调用（每个队伍一次）
        assert mock_ws.send.call_count == 2
        
        # 验证消息内容
        calls = mock_ws.send.call_args_list
        for call_args in calls:
            payload = json.loads(call_args[0][0])
            assert payload["action"] == "finished"
            assert "myteamScore" in payload
            assert "opponentScore" in payload
        
        # 清理
        SocketManager._instance = None
    
    @patch('native.managers.socket.team_socket.websocket')
    def test_disconnect_all(self, mock_websocket):
        """测试断开所有连接"""
        SocketManager._instance = None
        manager = SocketManager()
        
        mock_ws = MagicMock()
        mock_websocket.WebSocketApp = MagicMock(return_value=mock_ws)
        
        # 连接多个队伍
        manager.connect_team(Team.LEFT, "ws://localhost:34712")
        manager.connect_team(Team.RIGHT, "ws://localhost:34713")
        
        # 断开所有连接
        manager.disconnect_all()
        
        # 验证所有 socket 都被断开
        assert mock_ws.close.call_count == 2
        
        # 验证 sockets 字典被清空
        assert len(manager.sockets) == 0
        
        # 清理
        SocketManager._instance = None
