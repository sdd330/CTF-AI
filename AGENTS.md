# CTF-AI Project Guide for AI Agents

This document provides structured information about the CTF-AI project for AI agents to understand and work with the codebase effectively.

## Project Overview

**Project Name**: CTF-AI (Capture the Flag AI)  
**Language**: Python 3.10+  
**Type**: Multiplayer game with AI agent control  
**Architecture**: Client-Server (WebSocket), Frontend-Backend separation

### Core Architecture Concept

**`World` 是所有状态的集合，`Player` 是自驱动的，根据 `World` 规划下一步的 `Action`，通过 `Action` 影响 `World` 的状态！**

这是一个循环的状态更新机制：
- **World** (当前状态) → **Player.plan()** (自驱动决策) → **Action** (执行) → **World** (新状态)

**关键特性**：
- `Player` 是**自驱动的**：主动观察 `World` 状态并做出决策，根据 world 状态生成策略（Strategy.DEFENCE/SCORING/SAVING）
- `Action` 是**影响机制**：通过执行 `Action` 来改变 `World` 的状态
- `World` 是**状态容器**：维护所有游戏状态，响应 `Action` 的修改

## Project Structure

```
CTF-AI/
├── backend/                    # Backend server and AI logic
│   ├── server.py              # Main server file - implement AI here
│   ├── lib/                    # Core game engine library
│   │   ├── game_engine.py     # GameMap class, pathfinding, game state
│   │   ├── reinforcement_learning/  # Reinforcement learning (DQN) implementation
│   │   └── __init__.py         # Library exports
│   │   └── training/           # RL training scripts
│   │       ├── train_gym.py        # 训练脚本（基于Gymnasium）
│   │       └── visualize_training.py
│   └── requirements.txt        # Python dependencies
├── frontend/                    # Modern frontend (Vue 3 + TypeScript + Vite + Phaser 3)
│   ├── src/                   # TypeScript source code
│   │   ├── game/             # Game core code
│   │   │   ├── managers/    # Manager modules (GameStateManager, SocketManager, etc.)
│   │   │   ├── objects/      # Game objects (Player, Flag)
│   │   │   └── scenes/       # Phaser scenes (Boot, Preloader, Game, GameOver)
│   │   └── components/       # Vue components
│   └── public/               # Static resources
│       ├── game_config.json  # Server connection config
│       └── assets/           # Game resources
└── README.md                  # Main documentation
```

## Core API Reference

### Entry Point: `backend/server.py`

The main server file contains three critical functions that must be implemented:

#### 1. `start_game(req: dict) -> None`

**Purpose**: Initialize game state when game starts  
**Called**: Once at game start  
**Parameters**:
- `req`: Dictionary containing game initialization data
  - `req["map"]`: Map configuration (width, height, obstacles)
  - `req["team"]`: Team information (name, player count, flag count)

**Example**:
```python
from lib.game_engine import GameMap, World

game_map = GameMap()
world = World(game_map)

def start_game(req):
    world.init(req)
    print(f"Map initialized: {world.width}x{world.height}")
```

#### 2. `plan_next_actions(req: dict) -> dict`

**Purpose**: Generate actions for all players each game tick  
**Called**: Every game tick (multiple times per second)  
**Parameters**:
- `req`: Dictionary containing current game state
  - `req["players"]`: List of all players with positions, states
  - `req["flags"]`: List of all flags with positions, pickup status
  - `req["map"]`: Current map state

**Returns**: Dictionary with `actions`, `paths`, and `timings` keys
- `actions`: Dictionary mapping player names to movement directions
  - Format: `{"playerName": "direction"}`
  - Directions: `"up"`, `"down"`, `"left"`, `"right"`, `""` (stay still)
- `paths`: Dictionary mapping player names to path arrays (for visualization)
  - Format: `{"playerName": [{"x": int, "y": int}, ...]}`
- `timings`: Dictionary mapping player names to pathfinding timing data
  - Format: `{"playerName": {"algorithm": str, "total": float, ...}}`

**Example**:
```python
from lib.game_engine import GameMap, World, Team
from lib.utils import list_players

game_map = GameMap()
world = World(game_map)

def plan_next_actions(req):
    # Use world.plan_actions which handles everything
    result = world.plan_actions(req)
    
    # Return the result (contains actions, paths, and timings)
    return result
```

**Note**: The modern approach is to use `world.plan_actions(req)` which handles strategy generation, pathfinding, and action generation automatically. For custom AI logic, you can still access the game state directly:

```python
def plan_next_actions(req):
    world.update(req)
    actions = {}
    
    # Get available players using utility function
    my_team = Team.LEFT if req.get("myteamName") == "L" else Team.RIGHT
    my_players = list_players(world.players, my_team, in_prison=False, has_flag=False)
    
    # Generate actions for each player
    for player in my_players:
        actions[player.name] = "right"  # Example: move right
    
    return {"actions": actions, "paths": {}, "timings": {}}
```

#### 3. `game_over(req: dict) -> None`

**Purpose**: Clean up when game ends  
**Called**: Once when game finishes  
**Parameters**:
- `req`: Dictionary containing final game state and results

**Example**:
```python
def game_over(req):
    print("Game Over!")
```

### Core Classes: `World` and `GameMap`

**Location**: `backend/lib/game_service/game.py` and `backend/lib/map_service/map.py`  
**Purpose**: Manage game state and provide utility methods

#### World Class

**`World(game_map: GameMap)`**
- Main game class that manages game state and rules

**Key Methods**:

**`world.init(req: dict) -> None`**
- Initialize game from request data
- Must be called in `start_game()`

**`world.update(req: dict) -> bool`**
- Update game state from request data
- Must be called at start of `plan_next_actions()`
- Returns: `True` if update successful

**`world.plan_actions(req: dict) -> Dict[str, Dict]`**
- Plan actions for all players
- Returns: Dictionary with `actions`, `paths`, and `timings` keys
  - `actions`: `{player_name: direction}` mapping
  - `paths`: `{player_name: [Position, ...]}` for visualization
  - `timings`: `{player_name: {algorithm, total, ...}}` pathfinding performance data

**`world.find_path_to(start: Position, end: Position, extra_obstacles: Optional[Set[Position]], player_name: Optional[str]) -> List[Position]`**
- Find path using pathfinding algorithm (supports safe pathfinding when `player_name` is provided)
- Returns: List of Position objects forming path

**Key Properties**:
- `world.width`: int - Map width
- `world.height`: int - Map height
- `world.players`: Dict[str, Player] - All players
- `world.flags`: Dict[str, Flag] - All flags
- `world.left_team_score`, `world.right_team_score`: int - Scores

**Key Methods** (encapsulating game_map access):
- `world.is_in_team_territory(position: Position, team: Team) -> bool`
- `world.is_in_enemy_territory(position: Position, team: Team) -> bool`
- `world.get_team_target_positions(team: Team) -> List[Position]`
- `world.get_team_prison_positions(team: Team) -> List[Position]`
- `world.get_team_target_area(team: Team) -> Optional[TargetArea]`
- `world.get_team_prison_area(team: Team) -> Optional[PrisonArea]`
- `world.is_valid_position(position: Position) -> bool`
- `world.is_wall(position: Position) -> bool`

#### GameMap Class

**Note**: `GameMap` is now an internal class. Use `World` methods instead of accessing `world.game_map` directly.

**Key Properties** (internal, use `world` methods instead):
- `game_map.width`: int - Map width (use `world.width`)
- `game_map.height`: int - Map height (use `world.height`)
- `game_map.walls`: Set[Position] - Set of obstacle positions (use `world.is_wall()`)

### Utility Functions

**Location**: `backend/lib/utils/`

All utility functions are now centralized in the `utils` module for better modularity and reusability.

#### Player and Flag Query Functions

```python
from lib.utils import (
    list_players,
    list_flags
)

# Get players by team with filters
my_players = list_players(world.players, my_team, in_prison=False, has_flag=False)

# Get enemy flags
enemy_flags = list_flags(world.flags, my_team, is_enemy=True, can_pickup=True)

# Get team flags
my_flags = list_flags(world.flags, my_team, is_enemy=False, can_pickup=None)
```

#### Game Rule Checking Functions

```python
from lib.utils import (
    can_tag_enemy,
    can_rescue_teammate,
    can_pickup_flag,
    can_score_flag
)

# Check if player can tag enemy
if can_tag_enemy(player, enemy, world):
    player.action(Action.TAG_ENEMY, target=enemy)

# Check if player can rescue teammate
if can_rescue_teammate(player, teammate, world):
    player.action(Action.RESCUE_TEAMMATE, teammate=teammate)

# Check if player can pickup flag
if can_pickup_flag(player, flag):
    player.action(Action.PICKUP_FLAG, flag=flag)

# Check if player can score flag
if can_score_flag(player):
    player.action(Action.SCORE_FLAG)
```

## Common Tasks

### Task 1: Implement Basic Movement

**Goal**: Make all players move in a specific direction

**Steps**:
1. In `plan_next_actions()`, get all own team players
2. For each player, assign a direction
3. Return actions dictionary

**Code Template**:
```python
from lib.game_engine import GameMap, World, Team
from lib.utils import list_players

game_map = GameMap()
world = World(game_map)

def plan_next_actions(req):
    world.update(req)
    actions = {}
    
    my_team = Team.LEFT if req.get("myteamName") == "L" else Team.RIGHT
    my_players = list_players(world.players, my_team, in_prison=None, has_flag=None)
    for player in my_players:
        if not player.is_in_prison:
            actions[player.name] = "right"  # Move right
    
    return {"actions": actions, "paths": {}, "timings": {}}
```

### Task 2: Move to Nearest Flag

**Goal**: Make players move toward the nearest pickupable flag

**Steps**:
1. Get all free own team players
2. Get all pickupable opponent flags
3. For each player, find nearest flag
4. Calculate path to flag
5. Get next direction from path
6. Assign direction to player

**Code Template**:
```python
from lib.game_engine import GameMap, World, Team
from lib.utils import list_players, list_flags
from lib.utils.distance_calculator import DistanceCalculator

game_map = GameMap()
world = World(game_map)

def plan_next_actions(req):
    world.update(req)
    actions = {}
    paths = {}
    
    my_team = Team.LEFT if req.get("myteamName") == "L" else Team.RIGHT
    my_players = list_players(world.players, my_team, in_prison=False, has_flag=False)
    enemy_flags = list_flags(world.flags, my_team, is_enemy=True, can_pickup=True)
    
    for player in my_players:
        player_pos = player.position
        
        # Find nearest flag
        nearest_flag = DistanceCalculator.find_closest_flag(player_pos, enemy_flags)
        
        # Move toward nearest flag
        if nearest_flag:
            path = world.find_path_to(player_pos, nearest_flag.position, player_name=player.name)
            if len(path) > 1:
                direction = player.position.direction_to(path[1])
                actions[player.name] = direction.value
                paths[player.name] = [{"x": p.x, "y": p.y} for p in path]
    
    return {"actions": actions, "paths": paths, "timings": {}}
```

### Task 3: Return Flag to Target

**Goal**: Make players holding flags return to target area

**Steps**:
1. Get all own team players holding flags
2. For each player, find nearest target position
3. Calculate path to target
4. Get direction and assign

**Code Template**:
```python
from lib.game_engine import GameMap, World, Team
from lib.utils import list_players
from lib.utils.distance_calculator import DistanceCalculator

game_map = GameMap()
world = World(game_map)

def plan_next_actions(req):
    world.update(req)
    actions = {}
    paths = {}
    
    my_team = Team.LEFT if req.get("myteamName") == "L" else Team.RIGHT
    my_players_with_flag = list_players(world.players, my_team, in_prison=False, has_flag=True)
    
    for player in my_players_with_flag:
        if not player.base_area or not player.base_area.positions:
            continue
        
        player_pos = player.position
        base_positions = list(player.base_area.positions)
        
        # Find nearest target position
        nearest_target = DistanceCalculator.find_closest_position(player_pos, base_positions)
        
        # Move toward target
        if nearest_target:
            path = world.find_path_to(player_pos, nearest_target, player_name=player.name)
            if len(path) > 1:
                direction = player.position.direction_to(path[1])
                actions[player.name] = direction.value
                paths[player.name] = [{"x": p.x, "y": p.y} for p in path]
    
    return {"actions": actions, "paths": paths, "timings": {}}
```

### Task 4: Defend Territory

**Goal**: Intercept enemy players in own territory

**Steps**:
1. Get all free own team players
2. Get all free opponent players
3. Filter opponents in own territory
4. Assign defenders to intercept enemies
5. Calculate paths and directions

**Code Template**:
```python
from lib.game_engine import GameMap, World, Team
from lib.utils import list_players

game_map = GameMap()
world = World(game_map)

def plan_next_actions(req):
    world.update(req)
    actions = {}
    paths = {}
    
    my_team = Team.LEFT if req.get("myteamName") == "L" else Team.RIGHT
    my_players = list_players(world.players, my_team, in_prison=False, has_flag=False)
    enemy_team = my_team.get_enemy()
    enemies = list_players(world.players, enemy_team, in_prison=False, has_flag=None)
    
    # Filter enemies in own territory
    enemies_in_territory = []
    for enemy in enemies:
        if world.is_in_team_territory(enemy.position, my_team):
            enemies_in_territory.append(enemy)
    
    # Assign defenders
    for i, player in enumerate(my_players):
        if i < len(enemies_in_territory):
            enemy = enemies_in_territory[i]
            path = world.find_path_to(player.position, enemy.position, player_name=player.name)
            if len(path) > 1:
                direction = player.position.direction_to(path[1])
                actions[player.name] = direction.value
                paths[player.name] = [{"x": p.x, "y": p.y} for p in path]
    
    return {"actions": actions, "paths": paths, "timings": {}}
```

### Task 5: Rescue Teammates

**Goal**: Free teammates from prison

**Steps**:
1. Get all own team players in prison
2. Get all free own team players
3. Assign rescuers to prison positions
4. Calculate paths and directions

**Code Template**:
```python
from lib.game_engine import GameMap, World, Team
from lib.utils import list_players

game_map = GameMap()
world = World(game_map)

def plan_next_actions(req):
    world.update(req)
    actions = {}
    paths = {}
    
    my_team = Team.LEFT if req.get("myteamName") == "L" else Team.RIGHT
    my_players_in_prison = list_players(world.players, my_team, in_prison=True, has_flag=None)
    my_free_players = list_players(world.players, my_team, in_prison=False, has_flag=False)
    
    # Get enemy prison area
    enemy_team = my_team.get_enemy()
    enemy_prison_area = world.get_team_prison_area(enemy_team)
    
    # Assign rescuers
    for i, player in enumerate(my_free_players):
        if i < len(my_players_in_prison) and enemy_prison_area:
            # Find teammate in prison
            teammate = my_players_in_prison[i]
            prison_pos = teammate.position
            path = world.find_path_to(player.position, prison_pos, player_name=player.name)
            if len(path) > 1:
                direction = player.position.direction_to(path[1])
                actions[player.name] = direction.value
                paths[player.name] = [{"x": p.x, "y": p.y} for p in path]
    
    return {"actions": actions, "paths": paths, "timings": {}}
```

## Data Structures

### Player Dictionary (Standard Format)

**Note**: All player data now uses standard key names (`posX`, `posY`). Player objects are used directly, no conversion needed.

```python
{
    "name": str,        # Player identifier (e.g., "L0", "R1")
    "team": str,        # Team name ("L" or "R")
    "posX": int,        # X coordinate (standard key name)
    "posY": int,        # Y coordinate (standard key name)
    "inPrison": bool,   # Whether player is in prison
    "hasFlag": bool     # Whether player is holding a flag
}
```

### Flag Dictionary (Standard Format)

```python
{
    "posX": int,        # X coordinate (standard key name)
    "posY": int,        # Y coordinate (standard key name)
    "team": str,        # Team name ("L" or "R")
    "canPickup": bool,  # Whether flag can be picked up
    "pickedUp": bool    # Whether flag is picked up
}
```

### Player and Flag Objects

The new API uses `Player` and `Flag` objects with a clean, minimal interface:

```python
from lib.data_models import Player, Flag, Position, Team, Direction, Action

# Player object - Four Core Interfaces
player = Player("L0", Team.LEFT, Position(10, 10), world)

# 1. plan() - Plan next action (self-driven)
direction = player.plan()  # Returns Direction or None
direction = player.plan(suggested_strategy=Strategy.SCORING)  # With suggested strategy

# 2. move() - Move player
success = player.move(Direction.RIGHT)  # Returns bool

# 3. check() - Check state, relations, conditions
is_free = player.check("state", state="is_free")
is_enemy = player.check("relation", relation="is_enemy_of", other_player=other_player)
has_opponent = player.check("position", position="find_closest_opponent", opponents=opponents)

# 4. action() - Execute actions
player.action(Action.PICKUP_FLAG, flag=flag)
player.action(Action.TAG_ENEMY, target=enemy)
player.action(Action.SCORE_FLAG)

# Compatibility properties (backward compatible)
player.name          # str
player.team          # Team enum
player.position      # Position object
player.has_flag      # bool property (uses check() internally)
player.is_in_prison  # bool property (uses check() internally)
player.is_free       # bool property (uses check() internally)

# Flag object
flag.position        # Position object
flag.team            # Team enum
flag.can_pickup      # bool property
```

### Request Dictionary (`req`)

```python
{
    "action": str,           # "init", "status", or "finished"
    "players": [Player],     # List of player dictionaries
    "flags": [Flag],         # List of flag dictionaries
    "map": {
        "width": int,
        "height": int,
        "walls": [[x, y], ...],
        "targets": {
            "L": [[x, y], ...],
            "R": [[x, y], ...]
        },
        "prisons": {
            "L": [[x, y], ...],
            "R": [[x, y], ...]
        }
    },
    "team": {
        "name": str,
        "numPlayers": int,
        "numFlags": int
    }
}
```

## Running the Server

**Command**:
```bash
cd backend
python3 server.py <port>
```

**Example**:
```bash
python3 server.py 34712
```

**Requirements**:
- Python 3.10+
- All dependencies installed (`pip install -r requirements.txt`)
- Virtual environment activated (recommended)

## Testing Your Implementation

1. **Install Frontend Dependencies**:
   ```bash
   cd frontend
   pnpm install
   ```

2. **Start Frontend Development Server**:
   ```bash
   cd frontend
   pnpm dev
   ```

3. **Start Backend Server**:
   ```bash
   cd backend
   python3 server.py 34712
   ```

4. **Open Browser**: `http://localhost:8000`

5. **Check Console**: Backend server console shows game state and debug output

## Common Patterns

### Pattern 1: Strategy Assignment

Player 是自驱动的，会根据 world 状态自动生成策略。使用策略评估器（StrategyEvaluator）进行智能的策略选择，考虑多个因素：距离、威胁度、团队协作、比分差距等。

如果需要自定义策略分配，可以为 Player 提供策略建议（用于 RL 训练）：

```python
from lib.data_models import Strategy

# Player 自己根据 world 状态生成策略（自驱动，使用策略评估器）
direction = player.plan()

# 或者，为 Player 提供策略建议（用于 RL 训练）
direction = player.plan(suggested_strategy=Strategy.DEFENCE)
```

### Pattern 2: State Machine

Use state machines to manage player behavior.

```python
player_states = {}  # {player_name: "defence" | "scoring" | "returning" | "saving"}

for player in my_players:
    state = player_states.get(player["name"], "scoring")
    
    if state == "defence":
        # Defence behavior
        pass
    elif state == "scoring":
        # Scoring behavior
        pass
    # ... etc
```

### Pattern 3: Dynamic Strategy

Adjust strategy based on game conditions.

```python
from lib.utils import list_players

score_diff = my_score - enemy_score
enemy_team = my_team.get_enemy()
enemy_prison_count = len(list_players(world.players, enemy_team, in_prison=True, has_flag=None))

# 根据比分动态调整策略
if score_diff < 0:
    # 落后：更激进的进攻
    # 默认所有玩家都去抢旗
    pass
elif score_diff == 0:
    # 平局：保持默认策略
    pass
else:
    # 领先：可以考虑防守
    # Player 会自动根据 world 状态生成防守策略（如果有敌人在己方领地）
    pass
```

## Error Handling

### Common Errors and Solutions

1. **`IndentationError`**: Ensure consistent indentation (4 spaces)
2. **`KeyError`**: Check dictionary keys exist before access
3. **`AttributeError`**: Ensure `world.init()` called before using `world`
4. **Empty Path**: `world.find_path_to()` may return empty list if no path exists
5. **IndexError**: Check list length before accessing indices

## Best Practices

1. **Always call `world.update(req)`** at start of `plan_next_actions()`
2. **Use utility functions** from `lib.utils` for player/flag queries and rule checking
3. **Check player states** before assigning actions (is_in_prison, has_flag)
4. **Use pathfinding with player_name** to enable safe pathfinding (avoids enemy influence zones)
5. **Path finders are simplified** - they only receive `world` object, players are accessed via `world.players`
6. **Return proper format** - always return `{"actions": {}, "paths": {}, "timings": {}}`
7. **Use Position objects** - all positions are `Position` objects, not tuples
8. **Check base_area** - players have `base_area` (TargetArea) for scoring checks
9. **Debug with print()** - all logs are prefixed with team name (e.g., `[L队]`, `[R队]`)
10. **Test incrementally** - start with simple movement, then add complexity
11. **Frontend synchronization** - frontend waits for backend instructions after each step

## Reinforcement Learning Integration

The project includes DQN (Deep Q-Network) implementation in `backend/lib/reinforcement_learning/`.

**Key Classes**:
- `DQNAgent`: Main RL agent
- `DQN`: Neural network model
- `ReplayBuffer`: Experience replay buffer

**Training**:
```bash
# 1. 激活虚拟环境
cd backend
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate  # Windows

# 2. 启动训练
cd lib/reinforcement_learning/training
python3 train_gym.py <port> --algorithm CustomDQN
```

See `backend/lib/reinforcement_learning/README.md` for detailed RL documentation.

## Player Class Architecture

### Core Design Philosophy

The `Player` class follows a **minimal interface design** with four core methods, hiding all internal complexity:

1. **`plan()`** - Self-driven decision making
2. **`move()`** - Movement execution
3. **`check()`** - State and condition checking
4. **`action()`** - Action execution

### Modular Architecture

The `Player` class is modularized into specialized manager classes (all private):

```
backend/lib/data_models/player/
├── player.py                    # Main Player class (4 core interfaces)
├── player_state.py              # PlayerStateManager - state management
├── player_actions.py             # PlayerActions - action execution
├── player_flag_manager.py        # PlayerFlagManager - flag interactions
├── player_prison_manager.py      # PlayerPrisonManager - prison logic
├── player_data_updater.py        # PlayerDataUpdater - data updates
├── player_team_relations.py      # PlayerTeamRelations - team relations
├── player_checker.py             # PlayerChecker - unified checking
├── player_behavior.py            # PlayerBehavior - behavior orchestration
├── player_behavior_stats.py      # PlayerBehaviorStats - statistics tracking
├── player_strategy_planner.py    # PlayerStrategyPlanner - strategy generation
└── player_strategy_executor.py   # PlayerStrategyExecutor - strategy execution
```

**Key Design Principles**:
- **Encapsulation**: All managers are private (`__` prefix), not accessible externally
- **Single Responsibility**: Each manager handles one specific concern
- **Lazy Initialization**: Managers are created on-demand to avoid circular imports
- **Minimal Interface**: External code only uses the four core methods

### Using Player Core Interfaces

```python
from lib.data_models import Player, Team, Position, Direction, Action, Strategy
from lib.game_service import World

# Create player
player = Player("L0", Team.LEFT, Position(10, 10), world)

# 1. Plan next action (self-driven)
direction = player.plan()
# Or with suggested strategy (for RL training)
direction = player.plan(suggested_strategy=Strategy.SCORING)

# 2. Move player
if direction:
    success = player.move(direction)

# 3. Check various conditions
# State checks
is_free = player.check("state", state="is_free")
has_flag = player.check("state", state="has_flag")
is_in_base = player.check("state", state="is_in_base")

# Relation checks
is_enemy = player.check("relation", relation="is_enemy_of", other_player=other)
belongs = player.check("relation", relation="belongs_to_team", team=Team.LEFT)

# Position checks
has_opponent = player.check("position", position="find_closest_opponent", opponents=opponents)
has_flag_nearby = player.check("position", position="find_closest_flag", flags=flags)

# 4. Execute actions
player.action(Action.PICKUP_FLAG, flag=flag)
player.action(Action.DROP_FLAG)
player.action(Action.SCORE_FLAG)
player.action(Action.TAG_ENEMY, target=enemy)
player.action(Action.RESCUE_TEAMMATE, teammate=teammate)
```

### Player State Management

Players automatically handle state transitions:
- **Free** → **In Prison**: When tagged by enemy
- **Free** → **Carrying Flag**: When picking up flag
- **Carrying Flag** → **Free**: When scoring or dropping flag
- **In Prison** → **Free**: When rescued by teammate

**Important**: Players in prison cannot:
- Move (`move()` returns `False`)
- Plan paths (`plan()` returns `None` or `Direction.STAY`)
- Execute most actions (blocked by internal checks)

## File Locations Summary

- **Main AI Logic**: `backend/server.py`
- **Game Engine**: `backend/lib/game_engine.py` (exports all modules)
- **Game Service**: `backend/lib/game_service/game.py` (World class)
- **Player Module**: `backend/lib/data_models/player/` (modularized Player class)
  - **Core Class**: `player.py` (4 core interfaces: plan, move, check, action)
  - **Managers**: `player_state.py`, `player_actions.py`, `player_flag_manager.py`, etc.
  - **Behavior**: `player_behavior.py`, `player_strategy_planner.py`, `player_strategy_executor.py`
  - **Utilities**: `player_checker.py`, `player_team_relations.py`, `player_data_updater.py`
- **Utility Functions**: `backend/lib/utils/` (player queries, rule checking, etc.)
- **Pathfinding Service**: `backend/lib/pathfinding_service/` (safe pathfinding, weighted pathfinding)
  - All path finders (`PathFindingService`, `WeightedPathFinder`, `CorePathFinder`) now only receive `world` object
  - Players are accessed via `world.players` instead of passing a separate `players` dictionary
  - This simplifies the API and ensures consistent access to game state
- **Data Models**: `backend/lib/data_models/` (Player, Flag, Position, Team, etc.)
- **Map Service**: `backend/lib/map_service/` (GameMap, TargetArea, PrisonArea)
- **RL Module**: `backend/lib/reinforcement_learning/` (DQN implementation)
- **Frontend Config**: `frontend/public/game_config.json`
- **Frontend Source**: `frontend/src/game/`
- **Backend Dependencies**: `backend/requirements.txt`
- **Frontend Dependencies**: `frontend/package.json` (use `pnpm install`)
- **Training Scripts**: `backend/lib/reinforcement_learning/training/`
- **Tests**: `backend/tests/` (unit tests, 85+ tests covering all core interfaces), `frontend/e2e/` (E2E tests)

## Quick Reference

**Get Players**:
```python
from lib.utils import list_players

my_team = Team.LEFT if req.get("myteamName") == "L" else Team.RIGHT
# Own team free
my_players = list_players(world.players, my_team, in_prison=False, has_flag=False)
# Own team with flag
players_with_flag = list_players(world.players, my_team, in_prison=False, has_flag=True)
# Own team in prison
players_in_prison = list_players(world.players, my_team, in_prison=True, has_flag=None)
# Enemies
enemy_team = my_team.get_enemy()
enemies = list_players(world.players, enemy_team, in_prison=False, has_flag=None)
```

**Get Flags**:
```python
from lib.utils import list_flags

# Pickupable enemy flags
enemy_flags = list_flags(world.flags, my_team, is_enemy=True, can_pickup=True)
# Own flags
my_flags = list_flags(world.flags, my_team, is_enemy=False, can_pickup=None)
```

**Get Positions**:
```python
# Own target area (TargetArea object)
my_target_area = world.get_team_target_area(my_team)
my_target_positions = list(my_target_area.positions) if my_target_area else []

# Own prison area (PrisonArea object)
my_prison_area = world.get_team_prison_area(my_team)
my_prison_positions = list(my_prison_area.positions) if my_prison_area else []
```

**Pathfinding**:
```python
# Find path (with safe pathfinding when player_name is provided)
path = world.find_path_to(start_position, end_position, player_name=player.name)

# Get direction from Position object
if len(path) > 1:
    direction = player.position.direction_to(path[1])
    direction_str = direction.value  # "up", "down", "left", "right", "stay"
```

**Player Base Area**:
```python
# Each player has a base_area (TargetArea object)
if player.base_area:
    # Using check() interface
    is_in_base = player.check("state", state="is_in_base")
    # Or using compatibility method
    is_in_base = player.is_in_base()
    base_positions = list(player.base_area.positions)  # Get base positions
```

**Using Player Core Interfaces**:
```python
# Complete workflow example
def plan_next_actions(req):
    world.update(req)
    actions = {}
    paths = {}
    
    my_team = Team.LEFT if req.get("myteamName") == "L" else Team.RIGHT
    my_players = list_players(world.players, my_team, in_prison=False, has_flag=False)
    
    for player in my_players:
        # 1. Check state
        if not player.check("state", state="is_free"):
            continue
        
        # 2. Plan action (self-driven)
        direction = player.plan()
        
        # 3. Move if direction is valid
        if direction and direction != Direction.STAY:
            if player.move(direction):
                actions[player.name] = direction.value
        
        # 4. Check and execute actions
        if player.check("state", state="has_flag"):
            # Check if in base to score
            if player.check("state", state="is_in_base"):
                player.action(Action.SCORE_FLAG)
        else:
            # Check for nearby flags
            enemy_flags = list_flags(world.flags, my_team, is_enemy=True, can_pickup=True)
            if player.check("position", position="find_closest_flag", flags=enemy_flags):
                # Find and pickup nearest flag
                nearest_flag = player._team_relations.find_closest_flag(enemy_flags)
                if nearest_flag and player.position == nearest_flag.position:
                    player.action(Action.PICKUP_FLAG, flag=nearest_flag)
    
    return {"actions": actions, "paths": paths, "timings": {}}
```
