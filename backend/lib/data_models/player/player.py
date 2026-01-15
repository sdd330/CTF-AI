from typing import Optional, Dict, List, TYPE_CHECKING
from ..enums import Team, PlayerState, Direction, Action, Strategy
from ..position import Position
from ..areas import TargetArea
from ..status import PlayerStatus
from .player_actions import PlayerActions
from .player_flag_manager import PlayerFlagManager
from .player_prison_manager import PlayerPrisonManager
from .player_team_relations import PlayerTeamRelations
from .player_checker import PlayerChecker
from .player_behavior import PlayerBehavior
from .player_state import PlayerStateManager
from .player_serializer import PlayerSerializer

if TYPE_CHECKING:
    from ...game_engine import World
    from ..flag import Flag


class Player:
    def __init__(self, name: str, team: Team, position: Position, world: 'World'):
        if not name:
            raise ValueError("Player name cannot be empty")
        if not isinstance(position, Position):
            raise TypeError(f"Position must be Position object, got {type(position)}")
        if not isinstance(team, Team) or team not in (Team.LEFT, Team.RIGHT):
            raise ValueError(f"Player team must be Team.LEFT or Team.RIGHT, got {team}")
        if world is None:
            raise ValueError("world is required and cannot be None")

        self.name = name
        self.team = team
        self.position = position
        self.world: 'World' = world
        self.state = PlayerState.FREE
        self._has_flag: bool = False
        self._in_prison: bool = False
        self.prison_time_left: int = 0
        self.prison_duration: int = 20000
        self.base_area: Optional[TargetArea] = None

        # Manager instances (lazy initialized)
        self.__behavior: Optional[PlayerBehavior] = None
        self.__state_manager: Optional[PlayerStateManager] = None
        self.__actions: Optional[PlayerActions] = None
        self.__flag_manager: Optional[PlayerFlagManager] = None
        self.__prison_manager: Optional[PlayerPrisonManager] = None
        self.__team_relations: Optional[PlayerTeamRelations] = None
        self.__checker: Optional[PlayerChecker] = None
        self.__serializer: Optional[PlayerSerializer] = None

    @property
    def _behavior(self) -> PlayerBehavior:
        if self.__behavior is None:
            self.__behavior = PlayerBehavior(self)
        return self.__behavior

    @property
    def _state_manager(self) -> PlayerStateManager:
        if self.__state_manager is None:
            self.__state_manager = PlayerStateManager(self)
        return self.__state_manager

    @property
    def _actions(self) -> PlayerActions:
        if self.__actions is None:
            self.__actions = PlayerActions(self)
        return self.__actions

    @property
    def _flag_manager(self) -> PlayerFlagManager:
        if self.__flag_manager is None:
            self.__flag_manager = PlayerFlagManager(self)
        return self.__flag_manager

    @property
    def _prison_manager(self) -> PlayerPrisonManager:
        if self.__prison_manager is None:
            self.__prison_manager = PlayerPrisonManager(self)
        return self.__prison_manager

    @property
    def _team_relations(self) -> PlayerTeamRelations:
        if self.__team_relations is None:
            self.__team_relations = PlayerTeamRelations(self)
        return self.__team_relations

    @property
    def _checker(self) -> PlayerChecker:
        if self.__checker is None:
            self.__checker = PlayerChecker(self)
        return self.__checker

    @property
    def _serializer(self) -> PlayerSerializer:
        if self.__serializer is None:
            self.__serializer = PlayerSerializer(self)
        return self.__serializer

    def plan(self, suggested_strategy: Optional[Strategy] = None) -> Optional[Direction]:
        return self._behavior.plan(suggested_strategy)

    def move(self, direction: Direction) -> bool:
        if self._state_manager.is_in_prison or direction == Direction.STAY:
            return direction == Direction.STAY
        delta = {Direction.UP: (0, -1), Direction.DOWN: (0, 1),
                 Direction.LEFT: (-1, 0), Direction.RIGHT: (1, 0)}.get(direction)
        if not delta:
            return False
        new_pos = Position(self.position.x + delta[0], self.position.y + delta[1])
        if self.world and not self.world.map.is_valid_position(new_pos):
            return False
        self.position = new_pos
        self._behavior.stats.record_movement(direction, 1.0)
        return True

    def check(self, check_type: str, **kwargs) -> bool:
        return self._checker.check(check_type, **kwargs)

    def action(self, action_type: Action, **kwargs) -> bool:
        actions_map = {
            Action.PICKUP_FLAG: lambda: self._actions.execute_pickup_flag(kwargs.get('flag')),
            Action.DROP_FLAG: lambda: self._actions.execute_drop_flag(kwargs.get('drop_position')),
            Action.SCORE_FLAG: self._actions.execute_score_flag,
            Action.TAG_ENEMY: lambda: self._actions.execute_tag_enemy(kwargs.get('target')),
            Action.RESCUE_TEAMMATE: lambda: self._actions.execute_rescue_teammate(kwargs.get('teammate')),
        }
        handler = actions_map.get(action_type)
        if handler:
            return handler()
        print(f"⚠️  [Player.{self.name}] 不支持的动作类型: {action_type}", flush=True)
        return False

    @property
    def is_free(self) -> bool:
        return self.check("state", state="is_free")

    @property
    def is_in_prison(self) -> bool:
        return self.check("state", state="is_in_prison")

    @property
    def has_flag(self) -> bool:
        return self.check("state", state="has_flag")

    def is_in_base(self) -> bool:
        return self.check("state", state="is_in_base")

    def belongs_to_team(self, team: Team) -> bool:
        return self.check("relation", relation="belongs_to_team", team=team)

    def is_enemy_of(self, other_player: 'Player') -> bool:
        return self.check("relation", relation="is_enemy_of", other_player=other_player)

    def is_teammate_of(self, other_player: 'Player') -> bool:
        return self.check("relation", relation="is_teammate_of", other_player=other_player)

    def is_enemy_team(self, team: Team) -> bool:
        return self.check("relation", relation="is_enemy_team", team=team)

    def is_my_team(self, team: Team) -> bool:
        return self.check("relation", relation="is_my_team", team=team)

    def find_closest_opponent(self, opponents: List['Player']) -> Optional['Player']:
        return self._team_relations.find_closest_opponent(opponents)

    def find_closest_flag(self, flags: List['Flag']) -> Optional['Flag']:
        return self._team_relations.find_closest_flag(flags)

    def set_base_area(self, base_area: TargetArea) -> None:
        self._state_manager.set_base_area(base_area)

    def update_from_dict(self, p_data: Dict, flags: Dict[str, 'Flag']) -> None:
        self._serializer.update_from_dict(p_data, flags)

    def send_to_prison(self, prison_position: Position) -> None:
        self._prison_manager.send_to_prison(prison_position)

    def _rescue(self) -> None:
        self._prison_manager.rescue()

    def get_status(self) -> PlayerStatus:
        return self._serializer.get_status()

    def to_dict(self) -> Dict:
        return self._serializer.to_dict()

    def __repr__(self) -> str:
        return (f"Player(name={self.name}, team={self.team.value}, "
                f"position={self.position}, state={self.state.value}, has_flag={self.has_flag})")
