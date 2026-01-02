# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CTF-AI is a multiplayer Capture the Flag game with AI agent control and reinforcement learning support. The architecture follows a client-server model with WebSocket communication.

**Core Architecture**: `World` is the state container, `Player` is self-driven and plans actions based on `World` state, `Action` modifies `World` state.

**Game Loop**: `World` (current state) → `Player.plan()` (self-driven decision) → `Action` (execution) → `World` (new state)

## Common Commands

### Backend (Python)

```bash
# Setup virtual environment
cd backend
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Run backend servers (two terminals, one per team)
python3 server.py 34712  # Team L
python3 server.py 34713  # Team R

# Run tests
python3 -m pytest tests/ -v
python3 -m pytest tests/test_player.py -v        # Single test file
python3 -m pytest tests/test_player.py::TestPlayerPlan -v  # Single test class
python3 -m pytest -k "test_plan" -v              # Tests matching pattern

# RL Training
python3 -m lib.reinforcement_learning.training.train_gym 8080 --algorithm CustomDQN
python3 -m lib.reinforcement_learning.training.train_gym 8080 --algorithm CustomDQN --train-offline
```

### Frontend (TypeScript/Vue)

```bash
cd frontend
pnpm install
pnpm dev              # Development server at http://localhost:8000
pnpm build            # Production build
pnpm test             # Unit tests (Vitest)
pnpm test:e2e         # E2E tests (Playwright)
pnpm test:e2e:headed  # E2E tests with visible browser
```

## Architecture

### Backend Structure (`backend/lib/`)

- **`game_engine.py`** - Unified entry point exporting all modules
- **`data_models/`** - Core data models (Team, Player, Flag, Position, Direction, Action)
  - **`player/`** - Modularized Player class with 4 core interfaces: `plan()`, `move()`, `check()`, `action()`
- **`game_service/`** - World class managing game state and rules
- **`map_service/`** - GameMap, TargetArea, PrisonArea
- **`pathfinding_service/`** - Safe and weighted pathfinding (receives only `world` object, accesses players via `world.players`)
- **`utils/`** - Player/flag queries (`list_players`, `list_flags`), rule checking (`can_tag_enemy`, `can_pickup_flag`, etc.)
- **`reinforcement_learning/`** - DQN implementation

### Frontend Structure (`frontend/src/`)

- **`game/managers/`** - GameStateManager, SocketManager, InputManager, MapManager
- **`game/objects/`** - Player, Flag game objects
- **`game/scenes/`** - Phaser scenes (Boot, Preloader, Game, GameOver)
- **`components/`** - Vue components

### Server Entry Point

`backend/server.py` requires implementing three functions:

1. **`start_game(req)`** - Initialize game state (called once)
2. **`plan_next_actions(req)`** - Return player actions each tick (returns `{"actions": {}, "paths": {}, "timings": {}}`)
3. **`game_over(req)`** - Cleanup (called once)

### Key Imports

```python
from lib.game_engine import GameMap, World, Team, Player, Flag, Position, Direction, Action
from lib.data_models import Strategy  # For suggested_strategy in player.plan()
from lib.utils import list_players, list_flags, can_tag_enemy, can_rescue_teammate, can_pickup_flag, can_score_flag
from lib.utils.distance_calculator import DistanceCalculator  # For find_closest_flag, find_closest_position
```

## Game Configuration

Frontend config at `frontend/public/game_config.json`:
- Team server mappings
- WebSocket URLs (ports must match backend servers)
- Game setup (numPlayers, numFlags, mapWidth, mapHeight)

## Key Patterns

- Always call `world.update(req)` at start of `plan_next_actions()`
- Use `world.plan_actions(req)` for automatic strategy/pathfinding/action generation
- Use `world.find_path_to(start, end, player_name=name)` for safe pathfinding (avoids enemy zones)
- Player `base_area` property holds the TargetArea for scoring checks
- All positions are `Position` objects, use `position.direction_to(other)` for direction calculation
- Player has 4 core interfaces: `plan()`, `move()`, `check()`, `action()`
- Use `DistanceCalculator.find_closest_flag(position, flags)` for nearest target calculation
- Get enemy team with `my_team.get_enemy()`
