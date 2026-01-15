# Project Context

## Purpose
CTF-AI is a multiplayer Capture the Flag game with AI agent control and reinforcement learning support. The game enables autonomous AI players to compete in strategic capture-the-flag matches using pathfinding, decision-making, and learned behaviors.

## Tech Stack
- **Backend**: Python 3.x with WebSocket server
- **Frontend**: TypeScript, Vue 3, Phaser (game engine)
- **Package Manager**: pnpm (frontend)
- **Testing**: pytest (backend), Vitest (frontend unit), Playwright (E2E)
- **AI/ML**: Custom DQN implementation for reinforcement learning

## Project Conventions

### Code Style
- Python: Follow PEP 8 conventions
- TypeScript: Standard TypeScript conventions with strict mode
- Use descriptive variable and function names
- Prefer explicit type annotations in TypeScript
- **Maximum 200 lines per file** (including test files) - for AI readability and maintainability
- Split large files into focused modules with single responsibility

### Architecture Patterns
- **Core Pattern**: `World` (state container) → `Player.plan()` (decision) → `Action` (execution) → `World` (new state)
- Client-server model with WebSocket communication
- Modular player class with 4 core interfaces: `plan()`, `move()`, `check()`, `action()`
- Managers pattern in frontend: GameStateManager, SocketManager, InputManager, MapManager

### Testing Strategy
- Backend: pytest with verbose output (`python3 -m pytest tests/ -v`)
- Frontend: Vitest for unit tests, Playwright for E2E
- Test files mirror source structure

### Git Workflow
- Main branch: `main`
- Feature branches for new development
- Descriptive commit messages

## Domain Context

### Game Mechanics
- Two teams (L and R) compete to capture flags
- Players can tag enemies in their territory
- Tagged players go to prison and can be rescued by teammates
- Flags must be brought to base area to score
- Game runs on tick-based loop with WebSocket updates

### Key Entities
- **World**: Central state container managing all game state
- **Player**: Self-driven entity with planning capabilities
- **Flag**: Capturable objective
- **Team**: L or R team with territory and prison areas
- **Action**: Discrete actions (move, tag, pickup, etc.)
- **Position/Direction**: Grid-based movement system

### Server Entry Points
Three functions to implement in `server.py`:
1. `start_game(req)` - Initialize game state
2. `plan_next_actions(req)` - Return player actions each tick
3. `game_over(req)` - Cleanup

## Important Constraints
- Two server instances required (one per team, ports 34712 and 34713)
- All positions are `Position` objects, use `position.direction_to(other)` for calculations
- Always call `world.update(req)` at start of `plan_next_actions()`
- Pathfinding must avoid enemy zones for safety

## External Dependencies
- WebSocket for real-time communication
- Frontend connects via configured ports in `game_config.json`
- No external APIs required for core gameplay
