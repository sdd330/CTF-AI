# Data Models Specification

## Purpose
Core data models representing game entities including teams, positions, directions, player states, actions, and strategies.

## Requirements

### Requirement: Team Enum
The Team enum SHALL represent the two competing teams with utility methods.

#### Scenario: Team values
- **WHEN** accessing Team enum
- **THEN** LEFT and RIGHT values are available

#### Scenario: Enemy lookup
- **WHEN** `team.get_enemy()` is called
- **THEN** the opposing team is returned

#### Scenario: Name parsing
- **WHEN** `Team.from_name("L")` or `Team.from_name("R")` is called
- **THEN** the corresponding Team enum is returned

### Requirement: Direction Enum
The Direction enum SHALL represent movement directions including stationary.

#### Scenario: Direction values
- **WHEN** accessing Direction enum
- **THEN** UP, DOWN, LEFT, RIGHT, and STAY are available

### Requirement: PlayerState Enum
The PlayerState enum SHALL represent possible player states.

#### Scenario: State values
- **WHEN** accessing PlayerState enum
- **THEN** FREE, IN_PRISON, and CARRYING_FLAG are available

### Requirement: Action Enum
The Action enum SHALL represent discrete player actions.

#### Scenario: Action values
- **WHEN** accessing Action enum
- **THEN** PICKUP_FLAG, DROP_FLAG, RESCUE_TEAMMATE, TAG_ENEMY, and SCORE_FLAG are available

### Requirement: Strategy Enum
The Strategy enum SHALL represent high-level player strategies.

#### Scenario: Strategy values
- **WHEN** accessing Strategy enum
- **THEN** DEFENCE, SCORING, and SAVING are available

### Requirement: Position Model
The Position class SHALL represent grid coordinates with utility methods.

#### Scenario: Position creation
- **WHEN** `Position(x, y)` is created
- **THEN** x and y coordinates are stored

#### Scenario: Direction calculation
- **WHEN** `position.direction_to(other)` is called
- **THEN** the Direction toward the other position is returned

#### Scenario: Manhattan distance
- **WHEN** `position.manhattan_distance(other)` is called
- **THEN** the Manhattan distance between positions is returned

### Requirement: TargetArea Model
The TargetArea class SHALL represent team base zones for scoring.

#### Scenario: Area creation
- **WHEN** a TargetArea is created
- **THEN** it has bounds and team association

#### Scenario: Contains check
- **WHEN** `target_area.contains(position)` is called
- **THEN** true is returned if position is within the area

#### Scenario: Team ownership
- **WHEN** `target_area.belongs_to_team(team)` is called
- **THEN** true is returned if the area belongs to that team

### Requirement: PrisonArea Model
The PrisonArea class SHALL represent team prison zones for captured players.

#### Scenario: Prison creation
- **WHEN** a PrisonArea is created
- **THEN** it has bounds and team association

#### Scenario: Position management
- **WHEN** players are sent to prison
- **THEN** the prison area manages their positions

### Requirement: Flag Model
The Flag class SHALL represent capturable flag entities.

#### Scenario: Flag creation
- **WHEN** a Flag is created
- **THEN** it has team, position, and state properties

#### Scenario: Flag pickup
- **WHEN** `flag.pick_up_by(player)` is called
- **THEN** the flag's picked_up state changes and carrier is set

#### Scenario: Flag drop
- **WHEN** `flag.drop(position)` is called
- **THEN** the flag is placed at the specified position

#### Scenario: Flag scoring
- **WHEN** `flag.score()` is called
- **THEN** the flag's scored state is set

#### Scenario: Flag reset
- **WHEN** `flag.reset()` is called
- **THEN** the flag returns to its original position and state

#### Scenario: Pickup eligibility
- **WHEN** checking `flag.can_pickup`
- **THEN** true is returned only if flag is not picked up and not scored

#### Scenario: Enemy flag check
- **WHEN** `flag.is_enemy_flag_for(team)` is called
- **THEN** true is returned if the flag belongs to the opposing team
