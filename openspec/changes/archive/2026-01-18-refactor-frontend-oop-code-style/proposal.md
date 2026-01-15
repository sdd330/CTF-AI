# Change: Refactor Frontend Code to Comply with OOP Design and Code Style

## Why
Frontend code has multiple files exceeding 200 lines, violating code style guidelines:
- `GameStateManager.ts`: 1030 lines (5x limit)
- `Game.ts`: 935 lines (4.7x limit)
- `MapManager.ts`: 719 lines (3.6x limit)
- `SocketManager.ts`: 435 lines (2.2x limit)
- `PhysicsManager.ts`: 343 lines (1.7x limit)
- `UIManager.ts`: 321 lines (1.6x limit)
- `Player.ts`: 361 lines (1.8x limit)

While the code-style spec allows exceptions for framework requirements, these files violate single responsibility principle and should be refactored into smaller, focused modules following OOP design patterns.

## What Changes
- Refactor large frontend files into smaller modules:
  - **GameStateManager.ts** (1030 lines): Split into state domains (game state, team state, flow state, config state)
  - **Game.ts** (935 lines): Extract scene initialization, game loop, and object management into separate modules
  - **MapManager.ts** (719 lines): Split map rendering, layer management, and map parameter management
  - **SocketManager.ts** (435 lines): Extract connection management, message handling, and team socket logic
  - **PhysicsManager.ts** (343 lines): Split collision detection, physics updates, and collision callbacks
  - **UIManager.ts** (321 lines): Extract component factory, component management, and UI updates
  - **Player.ts** (361 lines): Extract movement logic, animation, and state management

- Apply OOP design principles:
  - Single Responsibility: Each class handles one aspect
  - Composition over Inheritance: Use manager composition
  - Encapsulation: Private methods and properties
  - Dependency Injection: Pass dependencies via constructor

- Update frontend spec to document refactored architecture

## Impact
- Affected specs: `frontend/spec.md` (update architecture documentation)
- Affected code: Multiple frontend TypeScript files (refactoring)
- Breaking changes: None (internal refactoring, public APIs preserved)
