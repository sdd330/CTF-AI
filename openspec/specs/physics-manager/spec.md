# Physics Manager Specification

## Purpose
Physics and collision detection system managing player interactions, flag collection, zone triggers, and physics body configuration.

## Requirements

### Requirement: Physics World Management
The PhysicsManager SHALL manage the Phaser physics world configuration.

#### Scenario: World initialization
- **WHEN** PhysicsManager is created
- **THEN** Arcade physics world is configured

#### Scenario: Physics body creation
- **WHEN** game objects are created
- **THEN** physics bodies are attached and configured

### Requirement: Player-to-Player Collision
The system SHALL detect and handle player collisions for tagging.

#### Scenario: Tag detection
- **WHEN** a player collides with an enemy in their territory
- **THEN** tag collision callback is invoked

#### Scenario: Tag validation
- **WHEN** tag collision occurs
- **THEN** territory and team rules are validated before tagging

#### Scenario: Tag execution
- **WHEN** valid tag conditions are met
- **THEN** enemy player is sent to prison

### Requirement: Player-to-Flag Collision
The system SHALL detect and handle player-flag collisions.

#### Scenario: Flag collection detection
- **WHEN** a player overlaps with an enemy flag
- **THEN** flag collection callback is invoked

#### Scenario: Collection validation
- **WHEN** flag overlap occurs
- **THEN** flag availability and team rules are validated

#### Scenario: Flag pickup
- **WHEN** valid pickup conditions are met
- **THEN** flag is attached to player

### Requirement: Player-to-Zone Collision
The system SHALL detect zone entry and exit events.

#### Scenario: Base zone entry
- **WHEN** player with flag enters their base zone
- **THEN** flag scoring callback is invoked

#### Scenario: Prison zone entry
- **WHEN** tagged player enters prison zone
- **THEN** player prison state is activated

#### Scenario: Rescue zone overlap
- **WHEN** free player overlaps with imprisoned teammate
- **THEN** rescue callback is invoked

### Requirement: Collision Callbacks
The PhysicsManager SHALL support configurable collision callbacks.

#### Scenario: Callback registration
- **WHEN** `addCollider(object1, object2, callback)` is called
- **THEN** callback is registered for those objects

#### Scenario: Callback invocation
- **WHEN** registered collision occurs
- **THEN** callback is invoked with collision data

### Requirement: Physics Body Configuration
The system SHALL configure physics bodies appropriately for each object type.

#### Scenario: Player body
- **WHEN** player physics body is created
- **THEN** appropriate size and collision settings are applied

#### Scenario: Flag body
- **WHEN** flag physics body is created
- **THEN** overlap detection is enabled

#### Scenario: Zone body
- **WHEN** zone physics body is created
- **THEN** trigger-style detection is configured
