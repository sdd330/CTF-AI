"""SocketManager - singleton for WebSocket connections"""

from typing import Optional, Dict, Any
from .event_emitter import EventEmitter, SocketEvent, EventListener
from .team_socket import TeamSocket
from ...utils import Team


class SocketManager:
    """Socket manager (singleton)"""
    _instance: Optional['SocketManager'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        self.sockets: Dict[Team, TeamSocket] = {}
        self.emitter = EventEmitter()
        self._initialized = True

    def connect_team(self, team: Team, url: str):
        if team in self.sockets:
            self.disconnect_team(team)
        socket = TeamSocket(url, team, self.emitter)
        self.sockets[team] = socket
        socket.connect()

    def disconnect_team(self, team: Team):
        socket = self.sockets.get(team)
        if socket:
            socket.disconnect()
            self.sockets.pop(team, None)

    def send_game_init(self, params: Dict[str, Any]):
        map_payload = self._build_map_payload(params)
        if self.is_connected(Team.LEFT):
            self._send_to_team(Team.LEFT, self._build_init_payload("L", map_payload, params, True))
        if self.is_connected(Team.RIGHT):
            self._send_to_team(Team.RIGHT, self._build_init_payload("R", map_payload, params, False))

    def _build_map_payload(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {"width": params["map_width"], "height": params["map_height"],
                "walls": [{"x": w["x"], "y": w["y"]} for w in params["walls"]],
                "obstacles": [{"x": w["x"], "y": w["y"]} for w in params["obstacles1"]] +
                             [{"x": w["x"], "y": w["y"]} for w in params["obstacles2"]]}

    def _build_init_payload(self, team_name: str, map_payload: Dict, params: Dict, is_left: bool) -> Dict:
        my, opp = ("lteam", "rteam") if is_left else ("rteam", "lteam")
        return {"action": "init", "map": map_payload, "numPlayers": params["num_players"],
                "numFlags": params["num_flags"], "myteamName": team_name,
                "myteamPrison": params[f"{my}_prison"], "myteamTarget": params[f"{my}_target"],
                "opponentPrison": params[f"{opp}_prison"], "opponentTarget": params[f"{opp}_target"]}

    def send_game_status(self, params: Dict[str, Any]):
        if self.is_connected(Team.LEFT):
            self._send_to_team(Team.LEFT, self._build_status_payload(params, True))
        if self.is_connected(Team.RIGHT):
            self._send_to_team(Team.RIGHT, self._build_status_payload(params, False))

    def _build_status_payload(self, params: Dict[str, Any], is_left: bool) -> Dict:
        my, opp = ("lteam", "rteam") if is_left else ("rteam", "lteam")
        return {"action": "status", "time": params["time"], "myteamName": "L" if is_left else "R",
                "myteamPlayer": params[f"{my}_player_status"], "myteamFlag": params[f"{my}_flag_status"],
                "myteamScore": params[f"{my}_score"], "opponentPlayer": params[f"{opp}_player_status"],
                "opponentFlag": params[f"{opp}_flag_status"], "opponentScore": params[f"{opp}_score"]}

    def send_game_finished(self, lteam_score: int, rteam_score: int):
        if self.is_connected(Team.LEFT):
            self._send_to_team(Team.LEFT, {"action": "finished", "myteamScore": lteam_score, "opponentScore": rteam_score})
        if self.is_connected(Team.RIGHT):
            self._send_to_team(Team.RIGHT, {"action": "finished", "myteamScore": rteam_score, "opponentScore": lteam_score})

    def _send_to_team(self, team: Team, payload: Dict[str, Any]) -> bool:
        socket = self.sockets.get(team)
        return socket.send(payload) if socket else False

    def is_connected(self, team: Team) -> bool:
        socket = self.sockets.get(team)
        return socket.is_connected() if socket else False

    def on(self, event: SocketEvent, listener: EventListener):
        self.emitter.on(event, listener)

    def off(self, event: SocketEvent, listener: EventListener):
        self.emitter.off(event, listener)

    def emit(self, event: SocketEvent, *args, **kwargs):
        self.emitter.emit(event, *args, **kwargs)

    def disconnect_all(self):
        for socket in list(self.sockets.values()):
            socket.disconnect()
        self.sockets.clear()
        self.emitter.remove_all_listeners()

    def get_connection_status(self) -> Dict[Team, bool]:
        return {Team.LEFT: self.is_connected(Team.LEFT), Team.RIGHT: self.is_connected(Team.RIGHT)}
