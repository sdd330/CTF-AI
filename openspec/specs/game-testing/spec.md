# Game Testing Specification

## Purpose
Testing infrastructure and requirements for CTF-AI project across frontend, backend, and native platforms.
## Requirements
### Requirement: Test Infrastructure
All test suites SHALL be runnable and pass successfully.

**MODIFICATION**: Added pytest dependency to backend and native, fixed frontend test warnings.

#### Scenario: Backend test execution
- **WHEN** running `python3 -m pytest tests/ -v` in backend directory
- **THEN** pytest is available and tests execute successfully
- **THEN** all backend unit tests pass

#### Scenario: Native test execution
- **WHEN** running `python3 -m pytest tests/ -v` in native directory
- **THEN** pytest is available and tests execute successfully
- **THEN** all native unit tests pass

#### Scenario: Frontend test execution
- **WHEN** running `pnpm test` in frontend directory
- **THEN** tests execute without warnings
- **THEN** all frontend unit tests pass

#### Scenario: Test dependencies
- **WHEN** setting up test environment
- **THEN** backend/requirements.txt includes pytest>=7.0.0
- **THEN** native/requirements.txt includes pytest>=7.0.0
- **THEN** frontend package.json includes vitest and related dependencies

### Requirement: Test File Organization
Test files SHALL follow project structure and naming conventions.

#### Scenario: Backend test structure
- **WHEN** creating backend tests
- **THEN** tests are located in `backend/tests/` directory
- **THEN** test files follow naming pattern `test_*.py`
- **THEN** tests use pytest fixtures from `conftest.py`

#### Scenario: Frontend test structure
- **WHEN** creating frontend tests
- **THEN** tests are located alongside source files in `__tests__` directories
- **THEN** test files follow naming pattern `*.test.ts`
- **THEN** tests use Vitest testing framework

#### Scenario: Native test structure
- **WHEN** creating native tests
- **THEN** tests are located in `native/tests/` directory
- **THEN** test files follow naming pattern `test_*.py`
- **THEN** tests use pytest testing framework

### Requirement: Test Execution
All test suites SHALL execute without errors or warnings.

#### Scenario: Clean test execution
- **WHEN** running test suites
- **THEN** no dependency errors occur
- **THEN** no mock setup warnings appear
- **THEN** all tests complete successfully

#### Scenario: Test failure reporting
- **WHEN** tests fail
- **THEN** clear error messages indicate the failure reason
- **THEN** test output includes relevant context for debugging

### Requirement: Keyboard Input E2E Testing
The game testing suite SHALL include comprehensive E2E tests for keyboard input functionality.

#### Scenario: L team WASD control test
- **WHEN** game is started
- **THEN** test SHALL press W, A, S, D keys in sequence
- **THEN** L team player SHALL move up, left, down, right correspondingly
- **THEN** player position SHALL update correctly after each key press
- **THEN** at least 10 steps of movement SHALL be tested

#### Scenario: R team Arrow keys control test
- **WHEN** game is started
- **THEN** test SHALL press UP, LEFT, DOWN, RIGHT arrow keys in sequence
- **THEN** R team player SHALL move up, left, down, right correspondingly
- **THEN** player position SHALL update correctly after each key press
- **THEN** at least 10 steps of movement SHALL be tested

#### Scenario: Keyboard input priority test
- **WHEN** remote control sends movement command
- **THEN** test SHALL press keyboard key
- **THEN** keyboard input SHALL override remote control
- **THEN** player SHALL move according to keyboard input
- **WHEN** keyboard key is released
- **THEN** player SHALL return to remote control behavior

#### Scenario: Independent team control test
- **WHEN** test presses W key (L team) and UP arrow (R team) simultaneously
- **THEN** L team player SHALL move independently
- **THEN** R team player SHALL move independently
- **THEN** no input conflicts SHALL occur
- **THEN** both players SHALL reach their intended destinations

#### Scenario: Wall collision test
- **WHEN** player attempts to move into wall using keyboard
- **THEN** player SHALL NOT move through wall
- **THEN** player SHALL remain in current position
- **THEN** subsequent valid moves SHALL work correctly

#### Scenario: Game state control test
- **WHEN** game is paused
- **THEN** keyboard input SHALL have no effect
- **WHEN** game is resumed
- **THEN** keyboard input SHALL work again
- **WHEN** game ends
- **THEN** keyboard input SHALL have no effect

### Requirement: Input Integration Testing
The game testing suite SHALL include integration tests for InputManager and Player interaction.

#### Scenario: InputManager with Player integration
- **WHEN** Player is created with InputManager
- **THEN** Player SHALL receive input from InputManager
- **THEN** Player SHALL move according to InputManager direction
- **THEN** Player SHALL update position correctly

#### Scenario: Multiple Players with same InputManager
- **WHEN** multiple Players share one InputManager
- **THEN** all Players SHALL receive same input direction
- **THEN** all Players SHALL attempt to move in same direction
- **THEN** collision detection SHALL still work correctly

#### Scenario: InputManager priority logic
- **WHEN** unit test sets remote control direction
- **WHEN** unit test simulates keyboard key press
- **THEN** InputManager.getCurrentDirection() SHALL return keyboard direction
- **WHEN** unit test releases keyboard key
- **THEN** InputManager.getCurrentDirection() SHALL return remote control direction

### Requirement: E2E Test Coverage
The game testing suite SHALL provide comprehensive E2E coverage including all keyboard input scenarios.

**Previous**: E2E tests only covered basic game start and simple movement.
**Reason**: To ensure keyboard input functionality works correctly in real gameplay.

#### Scenario: Comprehensive keyboard test suite
- **WHEN** E2E test suite is run
- **THEN** tests SHALL cover L team WASD control
- **THEN** tests SHALL cover R team Arrow keys control
- **THEN** tests SHALL cover keyboard input priority
- **THEN** tests SHALL cover independent team control
- **THEN** tests SHALL cover wall collision
- **THEN** tests SHALL cover game state transitions
- **THEN** all tests SHALL pass without manual intervention

#### Scenario: Test execution time
- **WHEN** full E2E test suite is run
- **THEN** execution time SHALL be under 5 minutes
- **THEN** tests SHALL be parallelizable where possible
- **THEN** CI pipeline SHALL run E2E tests on every commit

