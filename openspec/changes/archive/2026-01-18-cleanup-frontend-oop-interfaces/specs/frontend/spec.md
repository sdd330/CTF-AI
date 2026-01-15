## MODIFIED Requirements

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
