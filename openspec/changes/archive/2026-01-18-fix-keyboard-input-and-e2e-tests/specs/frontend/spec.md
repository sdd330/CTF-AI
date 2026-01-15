## ADDED Requirements

### Requirement: Keyboard Input Control
The frontend SHALL support independent keyboard control for each team using different key sets.

**Previous**: All players shared a single InputManager instance, causing input conflicts.
**Reason**: To restore fejs functionality where L team uses WASD and R team uses Arrow keys.

#### Scenario: L team uses WASD keys
- **WHEN** game is started
- **THEN** L team players SHALL respond to W, A, S, D keys
- **THEN** L team players SHALL NOT respond to Arrow keys

#### Scenario: R team uses Arrow keys
- **WHEN** game is started
- **THEN** R team players SHALL respond to UP, LEFT, DOWN, RIGHT arrow keys
- **THEN** R team players SHALL NOT respond to W, A, S, D keys

#### Scenario: Independent team control
- **WHEN** W key and UP arrow are pressed simultaneously
- **THEN** L team players SHALL move up (responding to W)
- **THEN** R team players SHALL move up (responding to UP arrow)
- **THEN** teams SHALL move independently without interference

#### Scenario: Keyboard input priority
- **WHEN** keyboard key is pressed
- **THEN** keyboard input SHALL override any remote control command
- **THEN** player SHALL move according to keyboard input
- **WHEN** keyboard key is released
- **THEN** player SHALL return to remote control or stop

### Requirement: Team Initialization
The frontend SHALL create independent InputManager instances for each team during initialization.

#### Scenario: L team InputManager creation
- **WHEN** TeamInitializer.initTeams() is called
- **THEN** a new InputManager with WASD bindings SHALL be created for L team
- **THEN** all L team players SHALL receive this InputManager instance
- **THEN** L team InputManager SHALL be updated in game loop

#### Scenario: R team InputManager creation
- **WHEN** TeamInitializer.initTeams() is called
- **THEN** a new InputManager with Arrow key bindings SHALL be created for R team
- **THEN** all R team players SHALL receive this InputManager instance
- **THEN** R team InputManager SHALL be updated in game loop

#### Scenario: AI mode without keyboard
- **WHEN** game is started in AI training mode
- **THEN** InputManager instances MAY not be created
- **THEN** players SHALL respond only to remote control
- **THEN** keyboard input SHALL have no effect
