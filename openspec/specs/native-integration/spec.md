# Native Desktop Application Specification

## Purpose
Specifications for the native Pygame desktop application that mirrors the web frontend functionality. The native app provides a standalone desktop experience for the CTF-AI game.

## Requirements

### Requirement: File Size Limit
All source files (`.py`) in the native directory SHALL NOT exceed 200 lines, including test files.


#### Scenario: Source file within limit
- **WHEN** a source file has 200 lines or fewer
- **THEN** the file complies with the size limit

#### Scenario: Source file exceeds limit
- **WHEN** a source file exceeds 200 lines
- **THEN** the file MUST be refactored into smaller, focused modules

#### Scenario: Test file within limit
- **WHEN** a test file has 200 lines or fewer
- **THEN** the file complies with the size limit

#### Scenario: Test file exceeds limit
- **WHEN** a test file exceeds 200 lines
- **THEN** the file MUST be split into multiple test files by logical grouping

### Requirement: Status Dataclasses
Game objects SHALL provide status through frozen dataclasses matching frontend interfaces.

#### Scenario: Player status retrieval
- **WHEN** calling `player.get_status()`
- **THEN** returns a `PlayerStatus` dataclass with fields: name, team, posX, posY, hasFlag, inPrison, inPrisonTimeLeft, inPrisonDuration

#### Scenario: Flag status retrieval
- **WHEN** calling `flag.get_status()`
- **THEN** returns a `FlagStatus` dataclass with fields: canPickup, posX, posY

#### Scenario: Status serialization
- **WHEN** calling `status.to_dict()`
- **THEN** returns a dictionary matching the frontend TypeScript interface

### Requirement: Scene Management
The application SHALL use a scene-based architecture for game states.

#### Scenario: Boot scene
- **WHEN** application starts
- **THEN** BootScene initializes core systems

#### Scenario: Preloader scene
- **WHEN** BootScene completes
- **THEN** PreloaderScene loads game assets

#### Scenario: Game scene
- **WHEN** PreloaderScene completes
- **THEN** GameScene runs the main game loop

#### Scenario: Game over scene
- **WHEN** game ends
- **THEN** GameOverScene displays results

### Requirement: Manager Pattern
The application SHALL use singleton managers for cross-cutting concerns.

#### Scenario: Input management
- **WHEN** handling player input
- **THEN** InputManager processes keyboard and remote control

#### Scenario: Map management
- **WHEN** rendering game map
- **THEN** MapManager handles tile rendering and collision

#### Scenario: Physics management
- **WHEN** detecting collisions
- **THEN** PhysicsManager handles player-flag and player-player interactions

#### Scenario: Socket management
- **WHEN** communicating with backend
- **THEN** SocketManager handles WebSocket connections

### Requirement: WebSocket Communication
The native app SHALL communicate with backend servers via WebSocket.

#### Scenario: Team connection
- **WHEN** connecting to a team server
- **THEN** WebSocket connection is established on configured port

#### Scenario: Game initialization
- **WHEN** receiving init payload
- **THEN** game state is initialized with map and player data

#### Scenario: Status updates
- **WHEN** receiving status payload
- **THEN** player and flag positions are updated

#### Scenario: Action sending
- **WHEN** player makes move
- **THEN** action is sent to backend server

### Requirement: Sprite Rendering
The application SHALL render game objects using Pygame sprites.

#### Scenario: Player rendering
- **WHEN** rendering player
- **THEN** correct sprite sheet and animation frame are used

#### Scenario: Flag rendering
- **WHEN** rendering flag
- **THEN** team-colored flag sprite is displayed

#### Scenario: Map rendering
- **WHEN** rendering map
- **THEN** tiles, walls, targets, and prisons are drawn

### Requirement: Input Handling
The application SHALL support multiple input methods.

#### Scenario: Keyboard input
- **WHEN** WASD or arrow keys pressed
- **THEN** corresponding direction is captured

#### Scenario: Remote control
- **WHEN** backend sends direction
- **THEN** player moves according to AI decision

#### Scenario: Hybrid input
- **WHEN** both keyboard and remote available
- **THEN** keyboard takes priority

### Requirement: Game Object Consistency
Native game objects SHALL match backend and frontend implementations.

#### Scenario: Player properties
- **WHEN** creating Player object
- **THEN** includes name, team, position, state, has_flag, prison status

#### Scenario: Flag properties
- **WHEN** creating Flag object
- **THEN** includes flag_id, team, position, can_pickup, is_picked_up

#### Scenario: Position tracking
- **WHEN** objects move
- **THEN** both grid and pixel positions are maintained

## Architecture

### Directory Structure
```
native/
├── main.py              # Entry point
├── game/                # Core game logic
│   ├── game.py          # CTFGame class
│   └── game_state.py    # GameState class
├── managers/            # Singleton managers
│   ├── input_manager.py
│   ├── map_manager.py
│   ├── physics_manager.py
│   ├── socket_manager.py
│   └── ...
├── objects/             # Game objects
│   ├── player.py        # Player class with get_status()
│   └── flag.py          # Flag class with get_status()
├── scenes/              # Scene classes
│   ├── base_scene.py
│   ├── boot_scene.py
│   ├── preloader_scene.py
│   ├── game_scene.py
│   └── game_over_scene.py
├── utils/               # Utilities
│   ├── enums.py         # Team, Direction, PlayerState
│   ├── status.py        # PlayerStatus, FlagStatus dataclasses
│   ├── constants.py
│   └── ...
└── tests/               # Test files (also 200 line limit)
```

### Key Patterns

1. **Status Pattern**: Use `get_status()` methods returning frozen dataclasses
2. **Manager Singletons**: One instance per manager type
3. **Scene Transitions**: Clean activation/deactivation lifecycle
4. **Event-Driven**: Observer pattern for input and game events
