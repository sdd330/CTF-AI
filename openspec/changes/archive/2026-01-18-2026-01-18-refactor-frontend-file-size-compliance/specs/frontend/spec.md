## ADDED Requirements

### Requirement: Detailed Module Structure
All frontend managers and scenes SHALL be split into focused sub-modules when exceeding 200 lines.

#### Scenario: Debug utilities modular structure
- **WHEN** debug functionality is needed
- **THEN** debug utilities use separate focused modules:
  - `debug/PerformanceMonitor.ts`: Performance metrics and FPS monitoring
  - `debug/Logger.ts`: Logging system with log levels
  - `debug/DebugTools.ts`: Unified debug tool interface
- **THEN** each debug module is ≤ 200 lines

#### Scenario: InputManager modular structure
- **WHEN** input management is needed
- **THEN** InputManager uses composition with specialized modules:
  - `input/KeyboardInputHandler.ts`: Keyboard input processing
  - `input/RemoteInputHandler.ts`: Remote control handling
  - `input/InputObserverManager.ts`: Observer pattern management
- **THEN** each input module is ≤ 200 lines and handles one aspect of input

#### Scenario: GameInitializer modular structure
- **WHEN** game initialization is needed
- **THEN** GameInitializer uses composition with specialized modules:
  - `game/ManagerFactory.ts`: Manager creation and instantiation
  - `game/EventSetup.ts`: Event listener setup and binding
- **THEN** each initialization module is ≤ 200 lines

#### Scenario: GameStateManager modular structure
- **WHEN** game state API management is needed
- **THEN** GameStateManager uses composition with API layer:
  - `game-state/GameStateAPI.ts`: Public API methods grouped by concern
- **THEN** each state management module is ≤ 200 lines

#### Scenario: Game scene detailed structure
- **WHEN** game scene requires complex management
- **THEN** Game scene uses composition with specialized modules:
  - `game/GameObjectManager.ts`: Game object group management (players, flags, zones)
  - `game/GameFlowController.ts`: Game flow control (start, pause, restart, game over)
  - `game/ScoreManager.ts`: Score and flag management
  - `game/GameInitializer.ts`: Scene initialization
  - `game/GameLoop.ts`: Game update loop
- **THEN** each game scene module is ≤ 200 lines and handles one aspect of scene functionality

## MODIFIED Requirements

### Requirement: File Size Compliance
All frontend TypeScript files SHALL target ≤ 200 lines per file.

**PREVIOUS**: SHOULD target 200 lines, MAY exceed when framework requirements make it impractical  
**REASON**: Enforce strict compliance to improve AI readability and maintainability

#### Scenario: File within limit
- **WHEN** a TypeScript file has 200 lines or fewer
- **THEN** the file complies with the size limit

#### Scenario: File exceeds limit
- **WHEN** a TypeScript file exceeds 200 lines
- **THEN** the file MUST be refactored into smaller modules following single responsibility principle
- **THEN** each resulting module MUST be ≤ 200 lines
- **THEN** use composition pattern with private sub-modules to maintain clean public API
