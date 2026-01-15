---
name: backend-dev
description: Python backend development for CTF-AI. Use when working on game engine, player logic, pathfinding, WebSocket server, or any backend Python code.
allowed-tools: Read, Write, Edit, Bash(python:*), Bash(pip:*), Glob, Grep
---

# Backend Development Skill

You are an expert Python developer working on the CTF-AI game backend.

## Project Architecture

```
backend/
├── server.py                    # Entry point
└── lib/
    ├── game_engine.py           # Unified exports
    ├── data_models/             # Core models
    │   ├── enums.py             # Team, Direction, PlayerState, Action, Strategy
    │   ├── position.py          # Position class
    │   ├── areas.py             # TargetArea, PrisonArea
    │   ├── flag.py              # Flag class
    │   └── player/              # Modular Player (13 components)
    ├── game_service/            # World class
    ├── map_service/             # GameMap
    ├── pathfinding_service/     # A*, BFS, Dijkstra, weighted paths
    ├── socket_service/          # WebSocket handling
    ├── utils/                   # Helpers
    └── reinforcement_learning/  # DQN implementation
```

## Core Design Pattern

```
World (state) → Player.plan() (decision) → Action (execution) → World (new state)
```

## Key Imports

```python
from lib.game_engine import GameMap, World, Team, Player, Flag, Position, Direction, Action
from lib.data_models import Strategy
from lib.utils import list_players, list_flags, can_tag_enemy, can_rescue_teammate, can_pickup_flag, can_score_flag
from lib.utils.distance_calculator import DistanceCalculator
```

## Server Entry Points

Implement these in `server.py`:

```python
def start_game(req):
    """Initialize game state (called once)"""
    world.init(req)

def plan_next_actions(req):
    """Return player actions each tick"""
    world.update(req)  # ALWAYS call first!
    return {"actions": {}, "paths": {}, "timings": {}}

def game_over(req):
    """Cleanup (called once)"""
    pass
```

## Player Core Interfaces

```python
# 1. plan() - Self-driven decision making (returns Optional[Direction])
direction = player.plan()  # Auto-generates strategy from world state
direction = player.plan(suggested_strategy=Strategy.SCORING)  # With suggested strategy (for RL training)

# 2. move() - Execute movement (returns bool)
success = player.move(Direction.RIGHT)

# 3. check() - Evaluate conditions (returns bool)
is_free = player.check("state", state="is_free")
is_enemy = player.check("relation", relation="is_enemy_of", other_player=other)
has_flag_nearby = player.check("position", position="find_closest_flag", flags=flags)

# 4. action() - Execute planned action (returns bool)
player.action(Action.PICKUP_FLAG, flag=flag)
player.action(Action.TAG_ENEMY, target=enemy)
player.action(Action.SCORE_FLAG)
```

## Common Patterns

### Pathfinding
```python
# Safe path avoiding enemies
path = world.find_path_to(start, end, player_name=name)

# Direction from position
direction = position.direction_to(target)
```

### Player Queries
```python
# Get free teammates
teammates = list_players(world, team=my_team, state=PlayerState.FREE)

# Get available enemy flags
enemy_flags = list_flags(world, team=enemy_team, available=True)

# Find closest flag
closest = DistanceCalculator.find_closest_flag(player.position, enemy_flags)
```

## Development Commands

```bash
cd backend
source .venv/bin/activate

# Run server (Team L)
python3 server.py 34712

# Run server (Team R)
python3 server.py 34713

# Run tests
python3 -m pytest tests/ -v
```

## Code Style

- Follow PEP 8
- Use type hints
- Keep functions focused and small
- Use descriptive names
