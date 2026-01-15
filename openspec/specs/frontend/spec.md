# Frontend Specification

## Purpose
Vue 3 and Phaser-based frontend for game visualization and WebSocket communication.
## Requirements
### Requirement: Manager Architecture
The frontend SHALL use a manager pattern with modular composition for separation of concerns.

**MODIFICATION**: Removed backward compatibility exports. All internal modules are private and not exported unless part of the public API.

#### Scenario: GameStateManager modular structure
- **WHEN** game state management is needed
- **THEN** GameStateManager uses composition with domain-specific state managers:
  - `GameStateDomain`: Core game state (started, paused, over, winner)
  - `TeamStateDomain`: Team scores and player/flag states
  - `FlowStateDomain`: Game flow state (loading, ready, playing, ended)
  - `ConfigStateDomain`: Game configuration state
- **THEN** each domain manager is ≤ 200 lines and handles one aspect of state

#### Scenario: Game scene modular structure
- **WHEN** game scene functionality is needed
- **THEN** Game scene uses composition with specialized modules:
  - `GameInitializer`: Scene initialization and setup
  - `GameLoop`: Game update loop and tick handling
  - `GameObjectManager`: Player, flag, and zone object management
- **THEN** each module is ≤ 200 lines and handles one aspect of scene functionality

#### Scenario: MapManager modular structure
- **WHEN** map rendering is required
- **THEN** MapManager uses composition with specialized modules:
  - `MapRenderer`: Map rendering and display
  - `MapLayerManager`: Layer management (ground, level, boundary)
  - `MapParameterManager`: Map parameters (position, size, tile size)
- **THEN** each module is ≤ 200 lines and handles one aspect of map functionality

#### Scenario: SocketManager modular structure
- **WHEN** WebSocket communication is needed
- **THEN** SocketManager uses composition with specialized modules:
  - `SocketConnectionManager`: Connection establishment and reconnection
  - `SocketMessageHandler`: Message parsing and routing
  - `TeamSocket`: Per-team socket management
- **THEN** each module is ≤ 200 lines and handles one aspect of socket functionality

#### Scenario: PhysicsManager modular structure
- **WHEN** physics simulation is needed
- **THEN** PhysicsManager uses composition with specialized modules:
  - `CollisionDetector`: Collision detection logic
  - `PhysicsUpdater`: Physics state updates
  - `CollisionCallbackManager`: Collision callback handling
- **THEN** each module is ≤ 200 lines and handles one aspect of physics functionality

#### Scenario: UIManager modular structure
- **WHEN** UI management is needed
- **THEN** UIManager uses composition with specialized modules:
  - `UIComponentFactory`: Component creation and factory pattern
  - `UIComponentManager`: Component lifecycle management
  - `UIUpdateHandler`: UI state updates and rendering
- **THEN** each module is ≤ 200 lines and handles one aspect of UI functionality

#### Scenario: Player class modular structure
- **WHEN** player functionality is needed
- **THEN** Player class uses composition with specialized modules:
  - `PlayerMovement`: Movement logic and path following
  - `PlayerAnimation`: Animation and sprite updates
  - `PlayerStateManager`: State management (prison, flag, etc.)
- **THEN** each module is ≤ 200 lines and handles one aspect of player functionality

#### Scenario: Minimal public interface
- **WHEN** using manager classes
- **THEN** only public methods defined in the manager class are accessible
- **THEN** internal modules (domain managers, sub-modules) are private and not exported
- **THEN** type exports are limited to types that are part of the public API

#### Scenario: Encapsulation
- **WHEN** accessing manager functionality
- **THEN** internal managers are private and accessed only through public methods
- **THEN** no direct access to internal implementation details

### Requirement: WebSocket Communication
The frontend SHALL maintain real-time communication with backend servers.

#### Scenario: Connection establishment
- **WHEN** the game starts
- **THEN** WebSocket connections are established to configured server ports

#### Scenario: Message handling
- **WHEN** a WebSocket message is received
- **THEN** the message is parsed and game state is updated

#### Scenario: Connection configuration
- **WHEN** reading `game_config.json`
- **THEN** team server mappings and WebSocket URLs are loaded

### Requirement: Game Object Rendering
The frontend SHALL render game objects using Phaser scenes.

#### Scenario: Player rendering
- **WHEN** player state changes
- **THEN** Player game objects are updated visually

#### Scenario: Flag rendering
- **WHEN** flag state changes
- **THEN** Flag game objects reflect current status

### Requirement: Scene Management
The frontend SHALL manage game flow through Phaser scenes.

#### Scenario: Boot scene
- **WHEN** the application starts
- **THEN** Boot scene initializes core resources

#### Scenario: Preloader scene
- **WHEN** assets need loading
- **THEN** Preloader scene loads all game assets

#### Scenario: Game scene
- **WHEN** gameplay is active
- **THEN** Game scene handles all gameplay rendering and logic

#### Scenario: GameOver scene
- **WHEN** the game ends
- **THEN** GameOver scene displays results

### Requirement: Configuration System
The frontend SHALL be configurable via `game_config.json`.

#### Scenario: Game setup
- **WHEN** configuration is loaded
- **THEN** numPlayers, numFlags, mapWidth, mapHeight are applied

#### Scenario: Server configuration
- **WHEN** connecting to backends
- **THEN** ports 34712 (Team L) and 34713 (Team R) are used as configured

### Requirement: Module Import System
The frontend SHALL use ES6 module imports exclusively.

#### Scenario: Importing modules
- **WHEN** importing modules in TypeScript code
- **THEN** MUST use ES6 `import` statements
- **THEN** MUST NOT use CommonJS `require()` statements

#### Scenario: Dynamic imports
- **WHEN** dynamic module loading is needed
- **THEN** use ES6 dynamic `import()` syntax
- **THEN** MUST NOT use `require()` for dynamic loading

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

### Requirement: OOP Design Principles
Frontend code SHALL follow OOP design principles.

#### Scenario: Single Responsibility
- **WHEN** a class requires "AND" to describe its purpose
- **THEN** the class MUST be split into multiple focused classes

#### Scenario: Composition over Inheritance
- **WHEN** sharing behavior between classes
- **THEN** use composition with manager classes rather than deep inheritance
- **THEN** managers are private and accessed via properties

#### Scenario: Encapsulation
- **WHEN** internal implementation details exist
- **THEN** use private methods and properties (TypeScript `private` keyword)
- **THEN** public interface exposes only necessary methods

#### Scenario: Dependency Injection
- **WHEN** a class requires external dependencies
- **THEN** pass dependencies via constructor parameters
- **THEN** avoid global state and singleton patterns where possible

### Requirement: Package Manager
The frontend SHALL use pnpm as the exclusive package manager for all dependency management.

#### Scenario: pnpm installation and usage
- **WHEN** setting up the frontend development environment
- **THEN** pnpm MUST be installed and used for all package operations
- **THEN** MUST NOT use npm or yarn commands for package management

#### Scenario: package.json configuration
- **WHEN** configuring package.json
- **THEN** the file MUST include a `packageManager` field specifying the pnpm version
- **THEN** the format SHALL be `"packageManager": "pnpm@<version>"`

#### Scenario: lock file management
- **WHEN** installing or updating dependencies
- **THEN** pnpm-lock.yaml MUST be generated and committed to version control
- **THEN** MUST NOT commit package-lock.json or yarn.lock files

#### Scenario: CI/CD integration
- **WHEN** running automated builds or tests
- **THEN** CI/CD pipelines MUST use pnpm for dependency installation
- **THEN** use `pnpm install --frozen-lockfile` for reproducible builds

#### Scenario: developer workflow
- **WHEN** adding or updating dependencies
- **THEN** use `pnpm add <package>` instead of `npm install <package>`
- **WHEN** running scripts
- **THEN** use `pnpm run <script>` or `pnpm <script>` instead of `npm run <script>`

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

