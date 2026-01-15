# Frontend Refactoring Design

## Overview
This document outlines the design for refactoring large frontend files into smaller, focused modules following OOP principles.

## Design Principles
1. **Single Responsibility**: Each module handles one aspect of functionality
2. **Composition over Inheritance**: Use manager composition
3. **Encapsulation**: Private methods and properties
4. **Dependency Injection**: Pass dependencies via constructor

## Module Breakdown

### 1. GameStateManager (1030 lines → ~4 modules)

#### 1.1 GameStateDomain (~200 lines)
**Responsibility**: Core game state (started, paused, over, winner)
- `startGame()`
- `pauseGame()`
- `endGame(team)`
- `resetGameState()`
- State: `gameStarted`, `gamePaused`, `gameOver`, `winner`

#### 1.2 TeamStateDomain (~250 lines)
**Responsibility**: Team scores and player/flag states
- `updateLTeamScore(score)`
- `updateRTeamScore(score)`
- `updateLTeamPlayers(players)`
- `updateRTeamPlayers(players)`
- `updateLTeamFlags(flags)`
- `updateRTeamFlags(flags)`
- `setLTeamState(state)`
- `setRTeamState(state)`
- State: `lTeamScore`, `rTeamScore`, `lTeamPlayers`, `rTeamPlayers`, `lTeamFlags`, `rTeamFlags`, `lTeamState`, `rTeamState`

#### 1.3 FlowStateDomain (~200 lines)
**Responsibility**: Game flow state (loading, ready, playing, ended)
- `sendFlowEvent(event)`
- `setFlowState(state)`
- `setFlowSubState(subState)`
- State: `flowState`, `flowSubState`, `currentScene`, `initialized`, `assetsLoaded`, `configLoaded`, `error`

#### 1.4 ConfigStateDomain (~200 lines)
**Responsibility**: Game configuration state
- `loadConfig(path)`
- `getConfig()`
- `setConfig(config)`
- State: `config`, `numPlayers`, `numFlags`, `useRandomFlags`

#### 1.5 GameStateManager (Main) (~180 lines)
**Responsibility**: Orchestration and registry access
- `getState()`
- `updateState(updates)`
- `onStateChange(callback)`
- Composition: All domain managers
- Registry management

### 2. Game Scene (935 lines → ~4 modules)

#### 2.1 GameInitializer (~250 lines)
**Responsibility**: Scene initialization and setup
- `initializeManagers()`
- `initializeGameObjects()`
- `loadGameConfig()`
- `setupEventListeners()`

#### 2.2 GameLoop (~200 lines)
**Responsibility**: Game update loop and tick handling
- `update(time, delta)`
- `handleGameTick()`
- `processServerUpdates()`

#### 2.3 GameObjectManager (~250 lines)
**Responsibility**: Player, flag, and zone object management
- `createPlayers()`
- `createFlags()`
- `createZones()`
- `updateGameObjects()`
- `destroyGameObjects()`

#### 2.4 Game Scene (Main) (~235 lines)
**Responsibility**: Phaser scene lifecycle
- `create()`
- `update()`
- Composition: Initializer, Loop, ObjectManager

### 3. MapManager (719 lines → ~3 modules)

#### 3.1 MapRenderer (~250 lines)
**Responsibility**: Map rendering and display
- `renderMap()`
- `updateMap()`
- `destroyMap()`

#### 3.2 MapLayerManager (~250 lines)
**Responsibility**: Layer management (ground, level, boundary)
- `createLayers()`
- `updateLayers()`
- `getLayer(name)`

#### 3.3 MapParameterManager (~200 lines)
**Responsibility**: Map parameters (position, size, tile size)
- `getMapOffset()`
- `setMapParameters()`
- `calculateMapPosition()`

#### 3.4 MapManager (Main) (~19 lines)
**Responsibility**: Orchestration
- Composition: Renderer, LayerManager, ParameterManager

### 4. SocketManager (435 lines → ~3 modules)

#### 4.1 SocketConnectionManager (~150 lines)
**Responsibility**: Connection establishment and reconnection
- `connect(team, url)`
- `disconnect(team)`
- `reconnect(team)`
- `isConnected(team)`

#### 4.2 SocketMessageHandler (~200 lines)
**Responsibility**: Message parsing and routing
- `handleMessage(team, message)`
- `sendMessage(team, data)`
- `parseMessage(message)`

#### 4.3 TeamSocket (~85 lines, already exists)
**Responsibility**: Per-team socket management
- Already exists, may need minor refactoring

#### 4.4 SocketManager (Main) (~0 lines, becomes thin wrapper)
**Responsibility**: Orchestration
- Composition: ConnectionManager, MessageHandler, TeamSocket

### 5. PhysicsManager (343 lines → ~3 modules)

#### 5.1 CollisionDetector (~150 lines)
**Responsibility**: Collision detection logic
- `detectCollisions()`
- `checkCollision(obj1, obj2)`

#### 5.2 PhysicsUpdater (~100 lines)
**Responsibility**: Physics state updates
- `updatePhysics()`
- `applyForces()`

#### 5.3 CollisionCallbackManager (~93 lines)
**Responsibility**: Collision callback handling
- `registerCallback(type, callback)`
- `triggerCallback(type, data)`

#### 5.4 PhysicsManager (Main) (~0 lines, becomes thin wrapper)
**Responsibility**: Orchestration
- Composition: CollisionDetector, PhysicsUpdater, CallbackManager

### 6. UIManager (321 lines → ~3 modules)

#### 6.1 UIComponentFactory (~120 lines)
**Responsibility**: Component creation and factory pattern
- `createComponent(type, config)`
- `registerComponentType(type, factory)`

#### 6.2 UIComponentManager (~120 lines)
**Responsibility**: Component lifecycle management
- `addComponent(component)`
- `removeComponent(id)`
- `getComponent(id)`

#### 6.3 UIUpdateHandler (~81 lines)
**Responsibility**: UI state updates and rendering
- `updateUI()`
- `showComponent(id)`
- `hideComponent(id)`

#### 6.4 UIManager (Main) (~0 lines, becomes thin wrapper)
**Responsibility**: Orchestration
- Composition: Factory, Manager, UpdateHandler

### 7. Player (361 lines → ~3 modules)

#### 7.1 PlayerMovement (~150 lines)
**Responsibility**: Movement logic and path following
- `move(direction)`
- `followPath(path)`
- `updateMovement()`

#### 7.2 PlayerAnimation (~120 lines)
**Responsibility**: Animation and sprite updates
- `updateAnimation()`
- `setAnimationState(state)`

#### 7.3 PlayerStateManager (~91 lines)
**Responsibility**: State management (prison, flag, etc.)
- `updateState(status)`
- `setInPrison(inPrison)`
- `setHasFlag(hasFlag)`

#### 7.4 Player (Main) (~0 lines, becomes thin wrapper)
**Responsibility**: Phaser sprite extension
- Extends `Phaser.Physics.Arcade.Sprite`
- Composition: Movement, Animation, StateManager

## Implementation Strategy

### Phase 1: Design and Planning
1. Create design document (this file)
2. Review with team
3. Update tasks.md

### Phase 2: Start with Smallest Files
1. UIManager (321 lines) - simplest
2. PhysicsManager (343 lines)
3. Player (361 lines)
4. SocketManager (435 lines)
5. MapManager (719 lines)
6. Game Scene (935 lines)
7. GameStateManager (1030 lines) - most complex

### Phase 3: Implementation Steps (per file)
1. Create new module files
2. Extract methods to modules
3. Update main class to use composition
4. Update imports in dependent files
5. Run tests
6. Verify file sizes ≤ 200 lines

### Phase 4: Testing
1. Update unit tests
2. Run E2E tests
3. Manual testing

### Phase 5: Documentation
1. Update frontend spec
2. Update code comments
3. Update README if needed

## File Structure

```
frontend/src/game/
├── managers/
│   ├── GameStateManager.ts (main, ~180 lines)
│   ├── game-state/
│   │   ├── GameStateDomain.ts (~200 lines)
│   │   ├── TeamStateDomain.ts (~250 lines)
│   │   ├── FlowStateDomain.ts (~200 lines)
│   │   └── ConfigStateDomain.ts (~200 lines)
│   ├── MapManager.ts (main, ~19 lines)
│   ├── map/
│   │   ├── MapRenderer.ts (~250 lines)
│   │   ├── MapLayerManager.ts (~250 lines)
│   │   └── MapParameterManager.ts (~200 lines)
│   ├── SocketManager.ts (main, thin wrapper)
│   ├── socket/
│   │   ├── SocketConnectionManager.ts (~150 lines)
│   │   └── SocketMessageHandler.ts (~200 lines)
│   ├── PhysicsManager.ts (main, thin wrapper)
│   ├── physics/
│   │   ├── CollisionDetector.ts (~150 lines)
│   │   ├── PhysicsUpdater.ts (~100 lines)
│   │   └── CollisionCallbackManager.ts (~93 lines)
│   └── UIManager.ts (main, thin wrapper)
│       └── ui/
│           ├── UIComponentFactory.ts (~120 lines)
│           ├── UIComponentManager.ts (~120 lines)
│           └── UIUpdateHandler.ts (~81 lines)
├── scenes/
│   ├── Game.ts (main, ~235 lines)
│   └── game/
│       ├── GameInitializer.ts (~250 lines)
│       ├── GameLoop.ts (~200 lines)
│       └── GameObjectManager.ts (~250 lines)
└── objects/
    ├── Player.ts (main, thin wrapper)
    └── player/
        ├── PlayerMovement.ts (~150 lines)
        ├── PlayerAnimation.ts (~120 lines)
        └── PlayerStateManager.ts (~91 lines)
```

## Migration Notes

1. **Backward Compatibility**: All public APIs must be preserved
2. **Gradual Migration**: Can be done incrementally, one file at a time
3. **Testing**: Each refactored module should have tests
4. **Documentation**: Update JSDoc comments for new structure
