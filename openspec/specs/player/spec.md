# Player Specification

## Purpose
Self-driven player entity with planning capabilities, implementing the core decision-making loop for AI agents.
## Requirements
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

### Requirement: Strategy Planning
The Player SHALL select appropriate strategies based on game state analysis.

#### Scenario: Strategy selection
- **WHEN** a player plans its next action
- **THEN** a Strategy is suggested based on current conditions (flags, enemies, teammates)

#### Scenario: Closest flag targeting
- **WHEN** planning to capture a flag
- **THEN** `DistanceCalculator.find_closest_flag()` is used to identify the nearest target

### Requirement: Pathfinding Integration
The Player SHALL use safe pathfinding to navigate while avoiding enemy zones.

#### Scenario: Safe path calculation
- **WHEN** `world.find_path_to(start, end, player_name=name)` is called
- **THEN** a path avoiding enemy zones is returned

#### Scenario: Weighted pathfinding
- **WHEN** navigating through contested areas
- **THEN** weighted pathfinding considers risk factors

### Requirement: State Awareness
The Player SHALL maintain awareness of its own state and surroundings.

#### Scenario: Base area knowledge
- **WHEN** `player.base_area` is accessed
- **THEN** the player's TargetArea for scoring is returned

#### Scenario: Team identification
- **WHEN** checking player allegiance
- **THEN** the player's team (L or R) is correctly identified

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

### Requirement: Prison State Handling
The Player SHALL handle being in prison and awaiting rescue.

#### Scenario: Prison detection
- **WHEN** a player is tagged
- **THEN** the player enters prison state and awaits rescue

#### Scenario: Post-rescue behavior
- **WHEN** a player is rescued
- **THEN** the player resumes normal planning

