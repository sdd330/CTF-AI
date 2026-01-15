# Game Objects Specification

## Purpose
Phaser game object implementations for Player and Flag entities with physics, animations, and state management.
## Requirements
### Requirement: Player Game Object
The Player class SHALL extend Phaser.Physics.Arcade.Sprite with game-specific functionality.

#### Scenario: Player creation
- **WHEN** a Player is created
- **THEN** sprite, physics body, and state are initialized

#### Scenario: Player properties
- **WHEN** accessing Player properties
- **THEN** name, team, position, inPrison, hasFlag, and spriteChoice are available

### Requirement: Player Movement
The Player SHALL support both local and remote-controlled movement.

#### Scenario: Local movement
- **WHEN** keyboard input is received
- **THEN** player moves in the specified direction

#### Scenario: Remote control
- **WHEN** `setRemoteControl(direction, target)` is called
- **THEN** AI-directed movement is executed

#### Scenario: Movement prediction
- **WHEN** network latency exists
- **THEN** movement prediction smooths visual updates

### Requirement: Player Path Planning
The Player SHALL support planned path visualization and execution.

#### Scenario: Path setting
- **WHEN** `setPlannedPath(path)` is called
- **THEN** the path is stored for prediction

#### Scenario: Path following
- **WHEN** following a planned path
- **THEN** player moves along waypoints

### Requirement: Player Flag Interactions
The Player SHALL handle flag collection and carrying.

#### Scenario: Flag collection
- **WHEN** `collectFlag(flag)` is called
- **THEN** flag is attached to player and hasFlag is true

#### Scenario: Flag drop
- **WHEN** `dropFlag()` is called
- **THEN** carried flag is released

#### Scenario: Player caught with flag
- **WHEN** a player carrying a flag is caught and sent to prison
- **THEN** the player's hasFlag state is cleared
- **THEN** no new flag objects are created in the frontend
- **THEN** the backend updates the existing flag's position based on the player's caught position

#### Scenario: Visual indicator
- **WHEN** player carries a flag
- **THEN** visual feedback indicates flag possession

### Requirement: Player Prison Mechanics
The Player SHALL handle prison state and rescue.

#### Scenario: Prison entry
- **WHEN** `toPrison()` is called
- **THEN** player enters prison state with duration

#### Scenario: Prison state
- **WHEN** player is in prison
- **THEN** inPrison is true and movement is restricted

#### Scenario: Prison release
- **WHEN** player is rescued
- **THEN** player exits prison state

### Requirement: Player Animations
The Player SHALL display appropriate animations for states.

#### Scenario: Idle animation
- **WHEN** player is stationary
- **THEN** idle animation plays

#### Scenario: Movement animation
- **WHEN** player is moving
- **THEN** directional movement animation plays

#### Scenario: Prison animation
- **WHEN** player is in prison
- **THEN** prison state animation plays

### Requirement: Player Status Export
The Player SHALL export status for synchronization.

#### Scenario: Status retrieval
- **WHEN** `getStatus()` is called
- **THEN** PlayerStatus object with all current state is returned

### Requirement: Flag Game Object
The Flag class SHALL extend Phaser.Physics.Arcade.Sprite with flag functionality.

#### Scenario: Flag creation
- **WHEN** a Flag is created
- **THEN** sprite, physics body, and team are initialized

#### Scenario: Flag properties
- **WHEN** accessing Flag properties
- **THEN** team, position, and canPickup are available

### Requirement: Flag Collection Handling
The Flag SHALL respond to collection events.

#### Scenario: Collection event
- **WHEN** `collect(player)` is called
- **THEN** flag state changes and visual feedback is provided

#### Scenario: Pickup eligibility
- **WHEN** checking canPickup
- **THEN** true only if flag is available for pickup

### Requirement: Flag Status Export
The Flag SHALL export status for synchronization.

#### Scenario: Status retrieval
- **WHEN** `getStatus()` is called
- **THEN** FlagStatus object with current state is returned

