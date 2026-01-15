# Input Manager Specification

## Purpose
Input handling system supporting multiple input strategies (keyboard, remote AI control, hybrid) with the strategy and observer patterns.
## Requirements
### Requirement: Input Manager Core
The InputManager SHALL handle all input sources and distribute to game objects.

#### Scenario: Input initialization
- **WHEN** InputManager is created with a scene
- **THEN** input strategies are initialized

#### Scenario: Input processing
- **WHEN** game update loop runs
- **THEN** current input state is processed and distributed

### Requirement: Keyboard Input Strategy
The KeyboardInputStrategy SHALL handle local keyboard controls.

#### Scenario: Arrow key movement
- **WHEN** arrow keys are pressed
- **THEN** corresponding direction input is captured

#### Scenario: WASD movement
- **WHEN** WASD keys are pressed
- **THEN** corresponding direction input is captured

#### Scenario: Spacebar control
- **WHEN** spacebar is pressed
- **THEN** game start/pause is triggered

### Requirement: Remote Input Strategy
The RemoteInputStrategy SHALL handle AI-controlled player commands.

#### Scenario: Remote command reception
- **WHEN** AI backend sends player actions
- **THEN** commands are queued for processing

#### Scenario: Command application
- **WHEN** processing remote commands
- **THEN** player positions and actions are updated

### Requirement: Hybrid Input Strategy
The HybridInputStrategy SHALL combine keyboard and remote inputs.

#### Scenario: Input priority
- **WHEN** both keyboard and remote inputs exist
- **THEN** keyboard input takes precedence for human player

#### Scenario: AI player handling
- **WHEN** processing AI-controlled players
- **THEN** remote commands are applied

### Requirement: Strategy Pattern
The InputManager SHALL use interchangeable input strategies.

#### Scenario: Strategy switching
- **WHEN** `setStrategy(strategy)` is called
- **THEN** the active input strategy changes

#### Scenario: Strategy interface
- **WHEN** implementing a new input strategy
- **THEN** the InputStrategy interface is implemented

### Requirement: Observer Pattern
The InputManager SHALL notify observers of input events.

#### Scenario: Input event subscription
- **WHEN** a component subscribes to input events
- **THEN** it receives input notifications

#### Scenario: Input event emission
- **WHEN** input is detected
- **THEN** all subscribers are notified

### Requirement: Key Bindings
The system SHALL support configurable key bindings.

#### Scenario: Default bindings
- **WHEN** no custom bindings are set
- **THEN** arrow keys and WASD are used

#### Scenario: Game control keys
- **WHEN** spacebar is pressed
- **THEN** game start or pause is toggled

### Requirement: Configurable Key Bindings
The InputManager SHALL support configurable key bindings for different keyboard layouts.

#### Scenario: WASD key bindings
- **WHEN** InputManager is created with WASD key bindings
- **THEN** W key SHALL map to up direction
- **THEN** A key SHALL map to left direction
- **THEN** S key SHALL map to down direction
- **THEN** D key SHALL map to right direction

#### Scenario: Arrow key bindings
- **WHEN** InputManager is created with Arrow key bindings
- **THEN** UP arrow SHALL map to up direction
- **THEN** LEFT arrow SHALL map to left direction
- **THEN** DOWN arrow SHALL map to down direction
- **THEN** RIGHT arrow SHALL map to right direction

#### Scenario: Custom key bindings
- **WHEN** InputManager is created with custom key bindings
- **THEN** the specified keys SHALL map to the corresponding directions
- **THEN** other keys SHALL have no effect on direction

### Requirement: Keyboard Input Priority
The InputManager SHALL prioritize keyboard input over remote control when both are present.

**Reason**: To match fejs original behavior and improve debugging experience by allowing manual keyboard control to override AI remote control.

#### Scenario: Keyboard input overrides remote control
- **WHEN** keyboard input is active (key is pressed)
- **THEN** keyboard direction SHALL be used
- **THEN** remote control direction SHALL be ignored

#### Scenario: Remote control used when no keyboard input
- **WHEN** no keyboard keys are pressed
- **THEN** remote control direction SHALL be used
- **THEN** getCurrentDirection() SHALL return remote control direction

#### Scenario: Remote control used when keyboard disabled
- **WHEN** keyboard input is disabled
- **THEN** remote control direction SHALL be used regardless of key presses
- **THEN** keyboard keys SHALL have no effect

### Requirement: Multiple InputManager Instances
The InputManager SHALL support multiple independent instances with different key bindings.

**Reason**: To enable L team and R team to use different keyboard controls (WASD vs Arrow keys) without conflicts.

#### Scenario: Two InputManager instances with different bindings
- **WHEN** two InputManager instances are created with different key bindings
- **THEN** each instance SHALL respond only to its configured keys
- **THEN** one instance's input SHALL NOT affect the other instance

#### Scenario: WASD and Arrow keys simultaneously
- **WHEN** WASD InputManager detects W key press
- **THEN** WASD InputManager SHALL return 'up' direction
- **WHEN** Arrow InputManager detects UP arrow press
- **THEN** Arrow InputManager SHALL return 'up' direction
- **THEN** both instances SHALL work independently without conflict

