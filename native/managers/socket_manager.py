"""
网络通信管理器
设计模式：单例模式 + 发布订阅（EventEmitter）

此模块已重构为多个小文件，位于 managers/socket/ 目录下。
此文件保留用于向后兼容。
"""

from .socket import (
    SocketManager,
    SocketEvent,
    EventEmitter,
    EventListener,
    TeamSocket,
)

__all__ = [
    'SocketManager',
    'SocketEvent',
    'EventEmitter',
    'EventListener',
    'TeamSocket',
]
