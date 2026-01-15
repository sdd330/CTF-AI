## MODIFIED Requirements

### Requirement: Player Core Interfaces
The Player class SHALL implement four core interfaces: `plan()`, `move()`, `check()`, and `action()`.

#### Scenario: Plan interface with optional strategy
- **WHEN** `player.plan(suggested_strategy: Optional[Strategy] = None)` is called
- **THEN** the player analyzes the world state, determines a strategy (or uses suggested_strategy for RL training), and returns `Optional[Direction]`
- **THEN** if player is in prison, returns `Direction.STAY`
- **THEN** if player has flag, immediately plans return to base strategy

#### Scenario: Move interface
- **WHEN** `player.move(direction: Direction)` is called
- **THEN** the player validates the move (checks if in prison, validates new position)
- **THEN** if valid, updates position and records movement statistics
- **THEN** returns `bool` indicating success

#### Scenario: Check interface with type system
- **WHEN** `player.check(check_type: str, **kwargs)` is called
- **THEN** the player evaluates conditions based on check_type:
  - `"state"`: Checks player state (is_free, is_in_prison, has_flag, is_in_base)
  - `"relation"`: Checks team relations (is_enemy_of, is_teammate_of, belongs_to_team, is_enemy_team, is_my_team)
  - `"position"`: Checks position-based conditions (find_closest_opponent, find_closest_flag)
- **THEN** returns `bool` indicating check result

#### Scenario: Action interface
- **WHEN** `player.action(action_type: Action, **kwargs)` is called
- **THEN** the player executes the action (PICKUP_FLAG, DROP_FLAG, SCORE_FLAG, TAG_ENEMY, RESCUE_TEAMMATE)
- **THEN** returns `bool` indicating success

### Requirement: Compatibility Properties
The Player SHALL provide compatibility properties that use the check() interface internally.

#### Scenario: Property access
- **WHEN** `player.is_free`, `player.is_in_prison`, or `player.has_flag` is accessed
- **THEN** the property calls `player.check("state", state="is_free")` (or equivalent) internally
- **THEN** returns the boolean result

#### Scenario: Base area check
- **WHEN** `player.is_in_base()` is called
- **THEN** the method calls `player.check("state", state="is_in_base")` internally
- **THEN** returns the boolean result

### Requirement: Modular Architecture
The Player SHALL use a modular architecture with internal managers (all private, accessed via properties).

#### Scenario: Lazy initialization
- **WHEN** a Player is created
- **THEN** internal managers (PlayerBehavior, PlayerStateManager, PlayerActions, etc.) are not immediately initialized
- **THEN** managers are created on-demand when first accessed via private properties

#### Scenario: Manager encapsulation
- **WHEN** accessing player functionality
- **THEN** all manager instances are private (prefixed with `__` or `_`)
- **THEN** external code only uses the four core interfaces: `plan()`, `move()`, `check()`, `action()`
