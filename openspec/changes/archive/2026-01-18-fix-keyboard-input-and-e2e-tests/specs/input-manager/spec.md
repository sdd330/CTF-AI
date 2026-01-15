## ADDED Requirements

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
