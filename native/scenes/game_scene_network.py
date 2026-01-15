"""Game scene network controller - WebSocket communication"""

from typing import Dict, Any, List, TYPE_CHECKING
from queue import Queue
from ..utils import Team, Direction, get_config
from ..managers import SocketManager, SocketEvent, GameStateManager

if TYPE_CHECKING:
    from .game_scene import GameScene


class GameSceneNetworkController:
    """Handles WebSocket communication for the game scene."""

    def __init__(self, scene: 'GameScene'):
        self.scene = scene
        self.socket_manager: SocketManager = None
        self.game_state_manager: GameStateManager = None
        self._pending_actions: Queue[Dict[str, Any]] = Queue()
        self._elapsed_time_ms: int = 0

    def setup_socket_manager(self, map_width: int, map_height: int, walls,
                             left_target, right_target, left_prison, right_prison):
        """Setup SocketManager and send init message to Backend."""
        config = get_config()
        l_url = config.get_team_server_url("L")
        r_url = config.get_team_server_url("R")

        if not l_url and not r_url:
            print("[Game] No WebSocket server configured, skipping SocketManager init")
            return

        print(f"[Game] WebSocket servers: L={l_url}, R={r_url}")
        self.socket_manager = SocketManager()
        self.game_state_manager = GameStateManager.get_instance()

        self.socket_manager.on(SocketEvent.CONNECT, self._on_connect)
        self.socket_manager.on(SocketEvent.DISCONNECT, self._on_disconnect)
        self.socket_manager.on(SocketEvent.ERROR, self._on_error)
        self.socket_manager.on(SocketEvent.ACTIONS_RECEIVED, self._on_actions_received)

        if l_url:
            self.socket_manager.connect_team(Team.LEFT, l_url)
        if r_url:
            self.socket_manager.connect_team(Team.RIGHT, r_url)

        self._send_init_message(map_width, map_height, walls, left_target,
                                right_target, left_prison, right_prison)

    def _on_connect(self, team: Team):
        print(f"[Game] {team.value} team WebSocket connected")
        if team == Team.LEFT:
            self.game_state_manager.set_l_team_connection(True)
        else:
            self.game_state_manager.set_r_team_connection(True)

    def _on_disconnect(self, team: Team):
        print(f"[Game] {team.value} team WebSocket disconnected")
        if team == Team.LEFT:
            self.game_state_manager.set_l_team_connection(False)
        else:
            self.game_state_manager.set_r_team_connection(False)

    def _on_error(self, team: Team, error: Any):
        print(f"[Game] {team.value} team WebSocket error: {error}")
        self.game_state_manager.set_error(str(error))

    def _on_actions_received(self, team: Team, actions: Dict[str, Any]):
        self._pending_actions.put({"team": team, "actions": actions})

    def _send_init_message(self, map_width, map_height, walls, left_target,
                           right_target, left_prison, right_prison):
        """Build and send init message payload."""
        config = get_config()
        map_manager = self.scene.map_manager
        obstacles_data = map_manager.get_obstacles() if map_manager else {}

        params = {
            "map_width": map_width, "map_height": map_height,
            "walls": walls,
            "obstacles1": obstacles_data.get("obstacles1", []),
            "obstacles2": obstacles_data.get("obstacles2", []),
            "lteam_prison": left_prison, "lteam_target": left_target,
            "rteam_prison": right_prison, "rteam_target": right_target,
            "num_players": config.num_players, "num_flags": config.num_flags,
        }
        self.socket_manager.send_game_init(params)

    def apply_backend_actions(self):
        """Apply player actions returned from Backend."""
        game = self.scene.game
        if not game:
            while not self._pending_actions.empty():
                self._pending_actions.get()
            return

        players_by_name = {
            p.name: p for p in game.state.left_team_players + game.state.right_team_players
        }

        while not self._pending_actions.empty():
            item = self._pending_actions.get()
            actions = item.get("actions", {})
            players_obj = actions.get("players", {}) if isinstance(actions, dict) else {}

            for player_name, direction_str in players_obj.items():
                player = players_by_name.get(player_name)
                if not player:
                    continue
                direction = self._parse_direction(direction_str)
                if direction != Direction.STAY:
                    game.set_player_action(player_name, direction)

    def _parse_direction(self, direction_str: str) -> Direction:
        mapping = {"up": Direction.UP, "down": Direction.DOWN,
                   "left": Direction.LEFT, "right": Direction.RIGHT}
        return mapping.get(direction_str, Direction.STAY)

    def send_game_status(self):
        """Build and send current game status to Backend."""
        game = self.scene.game
        if not game or not self.socket_manager:
            return

        def build_player_status(team: Team) -> List[Dict[str, Any]]:
            players = game.state.left_team_players if team == Team.LEFT else game.state.right_team_players
            return [{"name": p.name, "posX": int(p.grid_x), "posY": int(p.grid_y),
                     "inPrison": bool(p.in_prison), "hasFlag": bool(p.has_flag)} for p in players]

        def build_flag_status(team: Team) -> List[Dict[str, Any]]:
            flags = game.state.left_team_flags if team == Team.LEFT else game.state.right_team_flags
            return [{"posX": int(f.grid_x), "posY": int(f.grid_y),
                     "canPickup": bool(f.can_pickup), "pickedUp": bool(f.is_picked_up)} for f in flags]

        params = {
            "time": int(self._elapsed_time_ms),
            "lteam_player_status": build_player_status(Team.LEFT),
            "lteam_flag_status": build_flag_status(Team.LEFT),
            "rteam_player_status": build_player_status(Team.RIGHT),
            "rteam_flag_status": build_flag_status(Team.RIGHT),
            "lteam_score": int(game.state.left_team_score),
            "rteam_score": int(game.state.right_team_score),
        }
        self.socket_manager.send_game_status(params)

    def send_game_finished(self, left_score: int, right_score: int):
        if self.socket_manager:
            self.socket_manager.send_game_finished(left_score, right_score)

    def is_any_team_connected(self) -> bool:
        if not self.socket_manager:
            return False
        return self.socket_manager.is_connected(Team.LEFT) or self.socket_manager.is_connected(Team.RIGHT)

    def update_elapsed_time(self, delta_time: int):
        self._elapsed_time_ms += delta_time

    def reset_elapsed_time(self):
        self._elapsed_time_ms = 0

    def destroy(self):
        if self.socket_manager:
            self.socket_manager.disconnect_all()
        self.socket_manager = None
