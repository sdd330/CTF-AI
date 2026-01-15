# Game Engine Specification

## Purpose
Core game engine managing the Capture the Flag game mechanics, including teams, territories, flags, and game rules.

## Requirements

### Requirement: Team Management
The system SHALL support two competing teams (L and R) with distinct territories.

#### Scenario: Team initialization
- **WHEN** a game starts
- **THEN** two teams (L and R) are created with assigned territories

#### Scenario: Enemy team lookup
- **WHEN** `team.get_enemy()` is called
- **THEN** the opposing team is returned

### Requirement: Territory System
The system SHALL define territories including base areas (TargetArea) and prison areas (PrisonArea) for each team.

#### Scenario: Base area scoring
- **WHEN** a player carries a flag to their base area
- **THEN** the system recognizes a valid scoring position

#### Scenario: Prison containment
- **WHEN** a player is tagged in enemy territory
- **THEN** the player is sent to the enemy's prison area

### Requirement: Flag Management
The system SHALL manage flag entities that can be picked up, carried, and scored.

#### Scenario: Flag pickup
- **WHEN** a player is adjacent to an unclaimed flag and `can_pickup_flag()` returns true
- **THEN** the player can pick up the flag

#### Scenario: Flag scoring
- **WHEN** a player with a flag reaches their base area and `can_score_flag()` returns true
- **THEN** the flag is scored and points are awarded

### Requirement: Tagging System
The system SHALL allow players to tag enemies within their own territory.

#### Scenario: Valid tag
- **WHEN** a player attempts to tag an enemy and `can_tag_enemy()` returns true
- **THEN** the enemy is tagged and sent to prison

#### Scenario: Invalid tag in enemy territory
- **WHEN** a player attempts to tag while in enemy territory
- **THEN** the tag fails

### Requirement: Rescue System
The system SHALL allow players to rescue teammates from prison.

#### Scenario: Teammate rescue
- **WHEN** a player reaches a teammate in prison and `can_rescue_teammate()` returns true
- **THEN** the teammate is freed from prison

### Requirement: Action System
The system SHALL process discrete actions that modify game state.

#### Scenario: Move action
- **WHEN** a move action is executed with a valid direction
- **THEN** the player's position is updated

#### Scenario: Action validation
- **WHEN** an invalid action is attempted
- **THEN** the action is rejected and state remains unchanged

### Requirement: Position and Direction
The system SHALL use Position objects for all coordinates and Direction for movement.

#### Scenario: Direction calculation
- **WHEN** `position.direction_to(other)` is called
- **THEN** the direction from current position to target is returned

#### Scenario: Grid-based movement
- **WHEN** a player moves in a direction
- **THEN** the position changes by one grid cell in that direction
