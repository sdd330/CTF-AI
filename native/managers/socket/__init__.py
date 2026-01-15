"""
Socket module for WebSocket communication management.
Exports SocketManager, EventEmitter, SocketEvent, TeamSocket.
"""

from .event_emitter import EventEmitter, SocketEvent, EventListener
from .team_socket import TeamSocket
from .socket_manager import SocketManager

__all__ = [
    'SocketManager',
    'SocketEvent',
    'EventEmitter',
    'EventListener',
    'TeamSocket',
]
