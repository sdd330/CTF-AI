## ADDED Requirements

### Requirement: Manager Composition Pattern
Classes SHALL use composition with manager classes for complex functionality, using lazy initialization to avoid circular dependencies.

#### Scenario: Manager composition
- **WHEN** a class requires multiple specialized behaviors
- **THEN** use composition with manager classes (e.g., `PlayerBehavior`, `PlayerStateManager`, `PlayerActions`)
- **THEN** managers are private (prefixed with `__` or `_`) and accessed via properties

#### Scenario: Lazy initialization
- **WHEN** managers are created to avoid circular imports
- **THEN** managers are initialized on-demand via `@property` methods
- **THEN** managers are stored as `Optional` attributes and created when first accessed

```python
class Player:
    def __init__(self, ...):
        self.__behavior: Optional[PlayerBehavior] = None
    
    @property
    def _behavior(self) -> PlayerBehavior:
        if self.__behavior is None:
            self.__behavior = PlayerBehavior(self)
        return self.__behavior
```

### Requirement: Service Composition Pattern
Classes SHALL use internal service classes for modular functionality.

#### Scenario: Service initialization
- **WHEN** a class requires multiple services (e.g., `World` class)
- **THEN** services are initialized in `__init__` and stored as private attributes
- **THEN** services follow `self._service_name` naming pattern

```python
class World:
    def __init__(self, game_map: GameMap):
        self._pathfinding_service = PathFindingService(self)
        self._info_collector = GameInfoCollector(self)
        self._logger = GameLogger(self)
        self._state_updater = GameStateUpdater(self)
```

### Requirement: Minimal Public Interface
Classes SHALL expose minimal public interfaces, hiding internal complexity.

#### Scenario: Player class interface
- **WHEN** using the `Player` class
- **THEN** external code only uses four core methods: `plan()`, `move()`, `check()`, `action()`
- **THEN** all internal managers are private and not directly accessible

#### Scenario: World class interface
- **WHEN** using the `World` class
- **THEN** external code uses public methods: `init()`, `update()`, `plan_actions()`, `find_path_to()`
- **THEN** internal services are private and accessed only through public methods
