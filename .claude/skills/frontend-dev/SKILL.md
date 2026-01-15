---
name: frontend-dev
description: TypeScript/Vue frontend development for CTF-AI. Use when working on game UI, Phaser scenes, Vue components, WebSocket client, or any frontend code.
allowed-tools: Read, Write, Edit, Bash(pnpm:*), Glob, Grep
---

# Frontend Development Skill

You are an expert TypeScript/Vue developer working on the CTF-AI game frontend.

## Project Architecture

```
frontend/src/
├── App.tsx                      # Root component
├── components/
│   ├── GameContainer.tsx        # Main game entry
│   └── MapDemo.vue              # Demo page
├── game/
│   ├── config/assets.ts         # Asset definitions
│   ├── managers/
│   │   ├── GameStateManager.ts  # State machine
│   │   ├── SocketManager.ts     # WebSocket
│   │   ├── InputManager.ts      # Input handling
│   │   ├── PhysicsManager.ts    # Collision
│   │   ├── MapManager.ts        # Map rendering
│   │   └── UIManager.ts         # UI components
│   ├── objects/
│   │   ├── Player.ts            # Player sprite
│   │   └── Flag.ts              # Flag sprite
│   └── scenes/
│       ├── Boot.ts              # Initial scene
│       ├── Preloader.ts         # Asset loading
│       ├── Game.ts              # Main gameplay
│       └── GameOver.ts          # End screen
├── router/index.ts              # Vue router
└── types/index.ts               # Type definitions
```

## Key Types

```typescript
type Team = 'L' | 'R';
type Direction = 'up' | 'down' | 'left' | 'right' | '';
interface Position { x: number; y: number; }
interface PlayerStatus { name: string; team: Team; position: Position; ... }
interface GameConfig { gameSetup: GameSetup; teams: TeamConfig[]; }
```

## Manager Pattern

```typescript
// GameStateManager - Single source of truth
const state = GameStateManager.getInstance();
state.getGameState();  // Get current state
state.setFlowState('playing');  // Update flow

// SocketManager - WebSocket singleton
const socket = SocketManager.getInstance();
socket.on('ACTIONS_RECEIVED', (data) => { ... });
socket.send({ type: 'status', ... });
```

## Phaser Scene Lifecycle

```typescript
class Game extends Phaser.Scene {
  preload() { /* Load assets */ }
  create() { /* Initialize objects, managers */ }
  update() { /* Game loop */ }
}
```

## Player Object

```typescript
class Player extends Phaser.Physics.Arcade.Sprite {
  setRemoteControl(direction: Direction, target: Position);
  setPlannedPath(path: Position[]);
  collectFlag(flag: Flag);
  dropFlag();
  toPrison();
  getStatus(): PlayerStatus;
}
```

## Development Commands

```bash
cd frontend

# Install dependencies
pnpm install

# Development server
pnpm dev              # http://localhost:8000

# Build
pnpm build

# Tests
pnpm test             # Unit tests
pnpm test:e2e         # E2E tests
pnpm test:e2e:headed  # E2E with browser
```

## Configuration

Edit `public/game_config.json`:
```json
{
  "gameSetup": {
    "numPlayers": 3,
    "numFlags": 9,
    "mapWidth": 20,
    "mapHeight": 20
  },
  "teams": [
    { "name": "L", "serverPort": 34712 },
    { "name": "R", "serverPort": 34713 }
  ]
}
```

## Code Style

- Use TypeScript strict mode
- Prefer composition over inheritance
- Use Vue 3 Composition API
- Follow Phaser best practices for game objects
