"""
TeamSocket module for managing individual team WebSocket connections.
Handles connection, reconnection, message sending/receiving for a single team.
"""

import json
import threading
import time
import websocket
from typing import Optional

from .event_emitter import EventEmitter, SocketEvent
from ...utils import Team


class TeamSocket:
    """
    WebSocket connection wrapper class.
    Manages a single team's WebSocket connection (using websocket-client, synchronous).
    """

    def __init__(self, url: str, team: Team, emitter: EventEmitter):
        """
        Initialize team socket.

        Args:
            url: WebSocket server URL
            team: Team identifier
            emitter: Event emitter for publishing events
        """
        self.url = url
        self.team = team
        self.emitter = emitter
        self.websocket: Optional[websocket.WebSocketApp] = None
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 1.0  # seconds
        self._running = False
        self._thread: Optional[threading.Thread] = None

    def connect(self):
        """Connect to WebSocket server (synchronous)"""
        try:
            self._running = True
            self.websocket = websocket.WebSocketApp(
                self.url,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )

            # Run WebSocket in a separate thread
            self._thread = threading.Thread(target=self._run_forever, daemon=True)
            self._thread.start()
        except Exception as error:
            print(f"[SocketManager] {self.team.value} team connection failed: {error}")
            self.emitter.emit(SocketEvent.ERROR, self.team, error)
            self._attempt_reconnect()

    def _run_forever(self):
        """Run WebSocket (in a separate thread)"""
        try:
            self.websocket.run_forever()
        except Exception as error:
            print(f"[SocketManager] {self.team.value} team WebSocket error: {error}")
            self.emitter.emit(SocketEvent.ERROR, self.team, error)

    def _on_open(self, ws):
        """Connection opened callback"""
        self.reconnect_attempts = 0
        self.emitter.emit(SocketEvent.CONNECT, self.team)
        print(f"[SocketManager] {self.team.value} team connected")

    def _on_message(self, ws, message: str):
        """Message received callback"""
        self._handle_message(message)

    def _handle_message(self, message: str):
        """
        Handle received message.

        Args:
            message: Message content (JSON string)
        """
        try:
            data = json.loads(message)
            self.emitter.emit(SocketEvent.MESSAGE, self.team, data)

            # Handle error messages first: {"error": "..."}
            if isinstance(data, dict) and "error" in data:
                self.emitter.emit(SocketEvent.ERROR, self.team, data.get("error"))
                return

            # Handle player action messages
            # Server returns: { "players": { "L0": "up", ... }, "paths": {...} }
            if isinstance(data, dict) and "players" in data:
                players_obj = data.get("players", {})
                paths_obj = data.get("paths", {})

                if isinstance(players_obj, dict) and not isinstance(players_obj, list):
                    if len(players_obj) > 0:
                        player_actions = {
                            "players": players_obj,
                            "paths": paths_obj
                        }
                        self.emitter.emit(
                            SocketEvent.ACTIONS_RECEIVED, self.team, player_actions
                        )
        except json.JSONDecodeError as error:
            print(f"[SocketManager] {self.team.value} team message parse failed: {error}")
            self.emitter.emit(SocketEvent.ERROR, self.team, error)
        except Exception as error:
            print(f"[SocketManager] {self.team.value} team message handling error: {error}")
            self.emitter.emit(SocketEvent.ERROR, self.team, error)

    def _on_error(self, ws, error):
        """Error callback"""
        print(f"[SocketManager] {self.team.value} team WebSocket error: {error}")
        self.emitter.emit(SocketEvent.ERROR, self.team, error)

    def _on_close(self, ws, close_status_code, close_msg):
        """Connection closed callback"""
        print(f"[SocketManager] {self.team.value} team connection closed")
        self.emitter.emit(SocketEvent.DISCONNECT, self.team)
        if self._running:
            self._attempt_reconnect()

    def _attempt_reconnect(self):
        """Attempt reconnection (in a separate thread)"""
        if self.reconnect_attempts < self.max_reconnect_attempts:
            self.reconnect_attempts += 1
            delay = self.reconnect_delay * self.reconnect_attempts
            print(
                f"[SocketManager] {self.team.value} team will reconnect in {delay}s "
                f"({self.reconnect_attempts}/{self.max_reconnect_attempts})"
            )

            def reconnect():
                time.sleep(delay)
                if self._running:
                    self.connect()

            thread = threading.Thread(target=reconnect, daemon=True)
            thread.start()

    def send(self, data: str | dict) -> bool:
        """
        Send message (synchronous).

        Args:
            data: Data to send (string or dict)

        Returns:
            True if successful, False otherwise
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
            print(f"[SocketManager] {self.team.value} team send failed: {error}")
            self.emitter.emit(SocketEvent.ERROR, self.team, error)
            return False

    def disconnect(self):
        """Disconnect from server"""
        self._running = False
        if self.websocket:
            self.websocket.close()
            self.websocket = None

    def is_connected(self) -> bool:
        """
        Check if connected.

        Returns:
            True if connected, False otherwise
        """
        if not self.websocket or not self._running:
            return False
        try:
            return self.websocket.sock is not None and self.websocket.sock.connected
        except Exception:
            return False
