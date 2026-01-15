# Python Object-Oriented Programming Best Practices

## Purpose
Guidelines and requirements for writing clean, maintainable, and Pythonic object-oriented code in the CTF-AI project.

## Requirements

### Requirement: Single Responsibility Principle
Each class SHALL have a single, well-defined responsibility.

#### Scenario: Class with focused purpose
- **WHEN** creating a new class
- **THEN** it MUST handle exactly one aspect of functionality

#### Scenario: Class doing too much
- **WHEN** a class requires "AND" to describe its purpose
- **THEN** the class MUST be split into multiple classes

### Requirement: Composition Over Inheritance
Code SHALL prefer composition over inheritance for code reuse.

#### Scenario: Choosing between inheritance and composition
- **WHEN** deciding how to share behavior between classes
- **THEN** use inheritance only for true "is-a" relationships
- **AND** use composition for "has-a" relationships

#### Scenario: Avoiding deep inheritance hierarchies
- **WHEN** inheritance depth exceeds 2 levels
- **THEN** refactor to use composition or mixins

### Requirement: Explicit Interfaces with Abstract Base Classes
Abstract base classes SHALL define clear interfaces when multiple implementations exist.

#### Scenario: Defining an interface
- **WHEN** multiple classes share a common interface
- **THEN** define an ABC with `@abstractmethod` decorators

#### Scenario: Interface implementation
- **WHEN** implementing an abstract base class
- **THEN** implement ALL abstract methods

```python
from abc import ABC, abstractmethod

class Strategy(ABC):
    @abstractmethod
    def execute(self, world: World) -> Action:
        pass
```

### Requirement: Encapsulation and Access Control
Classes SHALL use appropriate access control conventions.

#### Scenario: Internal implementation details
- **WHEN** a method or attribute is internal to the class
- **THEN** prefix with single underscore `_internal_method`

#### Scenario: Name mangling for subclass protection
- **WHEN** an attribute must not be overridden by subclasses
- **THEN** prefix with double underscore `__protected_attr`

#### Scenario: Public interface
- **WHEN** a method is part of the public API
- **THEN** use no prefix and document with docstrings

### Requirement: Properties for Attribute Access
Classes SHALL use properties for computed attributes and controlled access.

#### Scenario: Computed attribute
- **WHEN** an attribute requires computation
- **THEN** use `@property` decorator

#### Scenario: Validated attribute assignment
- **WHEN** an attribute requires validation on set
- **THEN** use `@property` with `@attr.setter`

```python
class Player:
    @property
    def is_alive(self) -> bool:
        return self._status != Status.DEAD

    @property
    def position(self) -> Position:
        return self._position

    @position.setter
    def position(self, value: Position) -> None:
        if not self._world.is_valid_position(value):
            raise ValueError("Invalid position")
        self._position = value
```

### Requirement: Dataclasses for Data Containers
Simple data-holding classes SHALL use `@dataclass` decorator.

#### Scenario: Pure data container
- **WHEN** a class primarily holds data with minimal behavior
- **THEN** use `@dataclass` with appropriate options

#### Scenario: Immutable data
- **WHEN** data should not change after creation
- **THEN** use `@dataclass(frozen=True)`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Position:
    x: int
    y: int

@dataclass
class GameState:
    tick: int
    players: list[Player]
    flags: list[Flag]
```

### Requirement: Type Hints for Class Members
All class attributes, methods, and return types SHALL have type annotations.

#### Scenario: Method signatures
- **WHEN** defining a method
- **THEN** annotate all parameters and return type

#### Scenario: Instance attributes
- **WHEN** defining instance attributes
- **THEN** annotate in `__init__` or use class-level annotations

```python
class World:
    tick: int
    _players: dict[str, Player]

    def __init__(self, config: GameConfig) -> None:
        self.tick = 0
        self._players = {}

    def get_player(self, name: str) -> Player | None:
        return self._players.get(name)
```

### Requirement: Proper Use of Magic Methods
Classes SHALL implement appropriate magic methods for Pythonic behavior.

#### Scenario: String representation
- **WHEN** a class needs string representation
- **THEN** implement `__repr__` for debugging and optionally `__str__` for users

#### Scenario: Equality comparison
- **WHEN** objects need to be compared for equality
- **THEN** implement `__eq__` and `__hash__` together

#### Scenario: Container behavior
- **WHEN** a class acts as a container
- **THEN** implement `__len__`, `__iter__`, `__getitem__` as appropriate

```python
class Position:
    def __repr__(self) -> str:
        return f"Position(x={self.x}, y={self.y})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Position):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __hash__(self) -> int:
        return hash((self.x, self.y))
```

### Requirement: Dependency Injection
Classes SHALL receive dependencies through constructor injection.

#### Scenario: External dependencies
- **WHEN** a class requires external services or objects
- **THEN** pass them via `__init__` parameters

#### Scenario: Avoiding global state
- **WHEN** accessing shared state
- **THEN** inject the state container rather than using globals

```python
# Good: Dependencies injected
class PlayerController:
    def __init__(self, world: World, pathfinder: Pathfinder) -> None:
        self._world = world
        self._pathfinder = pathfinder

# Bad: Hidden dependencies
class PlayerController:
    def __init__(self) -> None:
        self._world = get_global_world()  # Hidden dependency
```

### Requirement: Factory Methods for Complex Construction
Classes with complex construction logic SHALL use class methods or factory functions.

#### Scenario: Multiple construction patterns
- **WHEN** a class can be created in multiple ways
- **THEN** use `@classmethod` factory methods

#### Scenario: Construction with validation
- **WHEN** construction requires validation or computation
- **THEN** encapsulate in a factory method

```python
class GameMap:
    @classmethod
    def from_file(cls, path: Path) -> "GameMap":
        data = json.loads(path.read_text())
        return cls(width=data["width"], height=data["height"])

    @classmethod
    def from_config(cls, config: MapConfig) -> "GameMap":
        return cls(width=config.width, height=config.height)
```

### Requirement: Mixins for Cross-Cutting Concerns
Reusable behavior across unrelated classes SHALL use mixins.

#### Scenario: Shared utility behavior
- **WHEN** multiple unrelated classes need the same utility methods
- **THEN** create a mixin class with the shared behavior

#### Scenario: Mixin naming convention
- **WHEN** creating a mixin class
- **THEN** suffix the class name with `Mixin`

```python
class LoggingMixin:
    def log_action(self, action: str) -> None:
        logger.info(f"{self.__class__.__name__}: {action}")

class Player(LoggingMixin):
    def move(self, direction: Direction) -> None:
        self.log_action(f"Moving {direction}")
        # ... movement logic
```

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

## Anti-Patterns to Avoid

### God Classes
Classes that do everything violate single responsibility. Split into focused classes.

### Circular Dependencies
Avoid classes that import each other. Use dependency injection or interfaces.

### Inheritance for Code Reuse Only
Don't inherit just to reuse code. Use composition instead.

### Mutable Default Arguments
Never use mutable objects as default arguments.

```python
# Bad
def __init__(self, items: list = []):
    self.items = items

# Good
def __init__(self, items: list | None = None):
    self.items = items if items is not None else []
```
