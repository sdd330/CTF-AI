# Capture the Flag

A multiplayer Capture the Flag world project based on Python and WebSocket, supporting AI agent control and reinforcement learning training.

## 📖 Project Overview

Capture the Flag is a classic team-based competitive game. Two teams (Team L and Team R) compete on a rectangular map, with the goal of collecting flags from the opponent's territory and bringing them back to their own target area. Players can tag opponent players within their own territory, and tagged players are sent to prison, requiring teammates to rescue them.

### Core Architecture Concept

**`World` is the collection of all game states, `Player` is self-driven, plans the next `Action` based on `World`, and influences `World`'s state through `Action`!**

This is a cyclic state update mechanism:
- **World** (current state) → **Player.plan()** (self-driven decision) → **Action** (execution) → **World** (new state)

**Key Characteristics**:
- `Player` is **self-driven**: Actively observes `World` state and makes decisions
- `Action` is the **influence mechanism**: Changes `World`'s state through execution
- `World` is the **state container**: Maintains all game states and responds to `Action` modifications

### Core Features

- 🎮 **Real-time Multiplayer Game**: Real-time communication based on WebSocket
- 🤖 **AI Agent Control**: Supports both rule-based and reinforcement learning AI strategies
- 🗺️ **Dynamic Map System**: Supports obstacles, random flag positions, etc.
- 📊 **Training Visualization**: Provides training process visualization and data analysis tools
- 🔧 **Easy to Extend**: Clear code structure for adding new strategies

## 🎯 Game Rules

Capture the Flag is a popular outdoor game where two teams compete in an open field. Each team has a territory and a set of flags located within the territory. Each team's goal is to collect flags of the opponent team and bring them back to the target area.

### Basic Rules

- **Two Teams**: **Team L** (left side) and **Team R** (right side)
- **Map Layout**: The field is a rectangle area, where the left half is Team L's territory and the right half is Team R's territory
- **Map Elements**: The map contains obstacles and walls that players cannot pass through

### Team Resources

Each team has the following resources:
- **Territory**: Half of the map area (Team L on the left, Team R on the right)
- **Target Area**: Located within the team's territory, used for scoring
- **Prison**: Located within the team's territory, used to hold tagged opponent players
- **Flags**: Located within the team's territory, initially positioned near the target area

### Game Objective

**Main Goal**: Collect flags of the opponent team and bring them back to your own target area to score.

### Core Mechanics

1. **Pickup Flag**
   - Players can only pick up flags of the **opponent team**
   - Players **cannot** pick up or move their own team's flags
   - Players must be at the same position as the flag to pick it up

2. **Tag Enemy**
   - Players can tag opponent players **within their own territory**
   - Tagged opponent players are sent to the **tagger's prison**
   - Tagging requires the player and opponent to be at the same position
   - Only free players can tag or be tagged

3. **Prison**
   - Tagged players are sent to the tagger's prison
   - Players stay in prison for a period of time (default 20000 game ticks)
   - Players in prison cannot move or perform other actions

4. **Rescue Teammate**
   - Teammates can go to the **opponent's prison** to rescue captured teammates
   - Rescue requires the rescuer and rescued player to be at the same position
   - After successful rescue, the rescued player immediately regains freedom

5. **Score Flag**
   - Player must be holding an opponent's flag
   - Player must be within their **own target area**
   - After scoring, the flag resets to its original position and the player regains freedom

![Capture The Flag Map](./fixed_map_example.png)

## 🚀 Quick Start

### Requirements

- **Python 3.10+**
- Virtual environment recommended (.venv)
- Modern browser (WebSocket support)

### Dependencies

Project dependencies (`backend/requirements.txt`):

- `torch>=2.0.0` - PyTorch deep learning framework (for reinforcement learning training)
- `numpy>=1.20.0` - Numerical computing library
- `matplotlib>=3.5.0` - Data visualization library
- `websockets>=10.0` - WebSocket communication support
- `ipython>=8.0.0` - IPython support (optional, for Jupyter notebook)

### Installation Steps

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd CTF-AI
```

#### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv .venv
```

#### 3. Activate Virtual Environment

**macOS/Linux:**
```bash
source .venv/bin/activate
```

**Windows:**
```bash
.venv\Scripts\activate
```

After activation, you should see `(.venv)` prefix in your command prompt.

#### 4. Install pnpm

The frontend project uses pnpm as the package manager:

```bash
# Install pnpm (if not already installed)
npm install -g pnpm
```

#### 5. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**Note**: If you encounter "externally-managed-environment" error (common on macOS), use one of the following methods:

**Method 1: Use Virtual Environment (Recommended)**
```bash
# Make sure virtual environment is activated
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows

# Then install in virtual environment
pip install -r requirements.txt
```

**Method 2: Use System Package Manager Flag**
```bash
pip install --break-system-packages -r requirements.txt
```

If you need to install training-related dependencies (PyTorch, etc.), run:

```bash
./install_dependencies.sh
```

#### 5. Verify Installation

```bash
python3 -c "import torch; print(f'✓ PyTorch {torch.__version__}')"
python3 -c "import numpy; print(f'✓ NumPy {numpy.__version__}')"
python3 -c "import matplotlib; print(f'✓ Matplotlib {matplotlib.__version__}')"
python3 -c "import websockets; print(f'✓ WebSockets {websockets.__version__}')"
```

**Note**: IPython is optional, and the code handles compatibility if it's not installed.

### Starting the Game

#### 1. Install Frontend Dependencies

```bash
cd frontend
pnpm install
```

**Note**: If pnpm is not installed, use `npm install -g pnpm` to install it.

#### 2. Install Frontend Dependencies

```bash
cd frontend
pnpm install
```

#### 3. Start Frontend Development Server

```bash
pnpm dev
```

The frontend server will start at `http://localhost:8000` (Vite default port).

#### 4. Start Backend Server (Team L)

```bash
cd backend
python3 server.py 34712
```

#### 5. Start Backend Server (Team R)

```bash
cd backend
python3 server.py 34713
```

#### 6. Access the Game

Open in browser: `http://localhost:8000`

#### 7. Keyboard Control (Optional)

The game supports manual keyboard control for debugging and testing:
- **Team L (left side)**: Use `WASD` keys to control (W=up, A=left, S=down, D=right)
- **Team R (right side)**: Use arrow keys to control (↑↓←→)
- **Space key**: Start/pause the game
- **Priority**: Keyboard input takes priority over AI remote control (convenient for manual debugging)

Note: In AI training mode, keyboard input is disabled and the game is fully controlled by AI.

### Configuration

The frontend server connects to backend servers through `frontend/game_config.json`:

```json
{
  "teams": [
    { "name": "L", "who": "user48-1"},
    { "name": "R", "who": "user48-2"}
  ],
  "setup": {
    "numPlayers": 9,
    "numFlags": 20,
    "useRandomFlags": true,
    "mapWidth": 20,
    "mapHeight": 20
  },
  "servers": {
    "user48-1": "ws://0.0.0.0:34712",
    "user48-2": "ws://0.0.0.0:34713"
  }
}
```

- `teams` field specifies the server ID for each team
- `setup` field configures world settings (takes effect after server restart)
- `servers` field configures WebSocket URL for each server ID
- Ensure backend ports match the configuration

## 💻 Development Guide

### Project Structure

```
CTF-AI/
├── backend/              # Backend server (AI logic)
│   ├── server.py        # Main server file (AI implementation)
│   ├── lib/             # Game engine library (modular design)
│   │   ├── game_engine.py   # Unified entry, exports all modules
│   │   ├── models.py        # Core data models (Team, Player, Flag, etc.)
│   │   ├── algorithms/      # Common algorithms (BFS, A*, Dijkstra)
│   │   ├── pathfinding_service/  # Pathfinding service and strategies
│   │   ├── map.py           # Map management (GameMap)
│   │   ├── world.py          # Game logic (World)
│   │   ├── server.py        # WebSocket server
│   │   ├── RL.py            # Reinforcement learning module (DQN)
│   │   ├── data_structures.py  # Data structure validation and normalization
│   │   └── constants.py      # Constant definitions
│   ├── training/        # Training scripts
│   │   ├── train_gym.py      # Training script (Gymnasium-based)
│   │   └── visualize_training.py  # Training visualization
│   ├── teleop.py       # Manual control script
│   └── requirements.txt
├── frontend/            # Modern frontend (Vue 3 + TypeScript + Vite + Phaser 3)
│   ├── src/            # TypeScript source code
│   │   ├── world/       # Game core code
│   │   │   ├── managers/  # Manager modules (InputManager, SocketManager, etc.)
│   │   │   ├── objects/   # Game objects (Player, Flag)
│   │   │   └── scenes/    # Phaser scenes (Boot, Preloader, Game, GameOver)
│   │   └── components/  # Vue components
│   └── public/         # Static resources
│       ├── game_config.json  # Game configuration
│       └── assets/     # Game resources (images, maps, etc.)
└── README.md           # This file
```

### Code Architecture

The project uses a modular, object-oriented design:

- **`data_models/`**: Defines core data models (Team, PlayerState, Position, Player, Flag, TargetArea, PrisonArea)
- **`algorithms/`**: Common algorithm module providing reusable pathfinding algorithms (BFS, A*, Dijkstra)
- **`pathfinding_service/`**: Pathfinding service and strategies, supports safe pathfinding (avoiding enemy influence zones) and weighted pathfinding
  - All path finders (`PathFindingService`, `WeightedPathFinder`, `CorePathFinder`) now only receive `world` object
  - Players are accessed via `world.players` instead of passing a separate `players` dictionary
  - This simplifies the API and ensures consistent access to game state
- **`map_service/`**: Manages map physical structure (obstacles, target areas, prisons, etc.)
- **`game_service/`**: Implements world logic and rules (tagging, rescue, pickup, scoring, etc.)
- **`utils/`**: Utility functions module, contains player/flag queries, rule checking, distance calculation, etc.

#### Data Structure Standards

All player and flag data use standard key names:
- **Player Dictionary**: `name`, `posX`, `posY`, `team`, `hasFlag`, `inPrison`
- **Flag Dictionary**: `posX`, `posY`, `team`, `canPickup`, `pickedUp`

### Modifying Backend AI

The core AI logic is in `backend/server.py`. You need to implement three functions:

1. **`start_game(req)`** - Game initialization (called once at game start)
2. **`plan_next_actions(req)`** - Decision function (called every game tick, returns player actions)
3. **`game_over(req)`** - Game end (called once when game ends)

**For detailed API documentation and code examples, see [AGENTS.md](AGENTS.md)**

### Reinforcement Learning Training

The project supports DQN (Deep Q-Network) reinforcement learning training.

#### Quick Start

**⚠️ Important: Activate virtual environment before training!**

```bash
# 1. Activate virtual environment
cd backend
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# 2. Online training (with game server)
python3 -m lib.reinforcement_learning.training.train_gym 8080 --algorithm CustomDQN

# 3. Offline training (without server)
python3 -m lib.reinforcement_learning.training.train_gym 8080 --algorithm CustomDQN --train-offline
```

#### Training Scripts

- **`train_gym.py`**: Training script (Gymnasium-based)
  - Supports online training (with game server) and offline training (simulated environment)
  - Supports multiple algorithms: DQN, PPO, A2C, CustomDQN
  - Fully based on Gymnasium standard, compatible with stable-baselines3

#### Training Visualization

Use visualization script to view training progress in real-time:

```bash
cd backend
python3 training/visualize_training.py lib/models/training_stats.json 5
```

Visualization includes:
- Episode reward trends
- Training loss trends
- Win rate trends
- Statistics panel (with training recommendations)

#### Training Recommendations

- **Can stop training**: Win rate ≥ 80%, or win rate ≥ 60% and stable, or rewards converged and loss stable
- **Need to continue training**: Win rate < 50%, large reward variance (std > 50), loss > 1.0

### Modifying Frontend

The frontend is developed using **Vue 3.5 + TypeScript + Vite + Phaser 3**, with modular, object-oriented design:

```
frontend/
├── src/
│   ├── world/          # Game core code
│   │   ├── managers/  # Manager modules
│   │   │   ├── GameStateManager.ts  # Game state management (Singleton+Registry)
│   │   │   ├── SocketManager.ts     # WebSocket communication (Singleton+EventEmitter)
│   │   │   ├── InputManager.ts      # Input management (Observer+Strategy)
│   │   │   ├── MapManager.ts        # Map management
│   │   │   ├── PhysicsManager.ts    # Physics system management
│   │   │   └── UIManager.ts         # UI management
│   │   ├── objects/   # Game objects
│   │   │   ├── Player.ts  # Player object
│   │   │   └── Flag.ts    # Flag object
│   │   └── scenes/    # Phaser scenes
│   │       ├── Boot.ts      # Boot scene
│   │       ├── Preloader.ts # Preloader scene
│   │       ├── Game.ts      # Main world scene
│   │       └── GameOver.ts  # Game over scene
│   └── components/    # Vue components
│       └── GameContainer.tsx  # Game container component
├── public/
│   ├── game_config.json    # Game configuration (server connections, etc.)
│   └── assets/        # Game resources (images, maps, etc.)
└── package.json       # Dependencies configuration
```

**Tech Stack**:
- Vue 3.5 - Progressive JavaScript framework
- TypeScript - Type-safe JavaScript superset
- Vite - Next-generation frontend build tool
- Phaser 3.85+ - HTML5 world framework

**Development Commands**:
```bash
cd frontend
pnpm install         # Install dependencies
pnpm dev             # Development mode
pnpm build           # Build production version
pnpm test            # Run unit tests (Vitest)
pnpm test:ui         # Run unit tests (UI mode)
pnpm test:e2e        # Run E2E tests (Playwright)
pnpm test:e2e:ui     # Run E2E tests (UI mode)
pnpm test:e2e:headed # Run E2E tests (headed mode)
```

**Frontend Optimizations**:
- Movement synchronization: Frontend players wait for backend instructions after each step
- Pre-computation logic: If next two steps in path have same direction, players can move continuously
- Path visualization: Frontend displays paths calculated by backend for debugging and observation
- Detailed logging: Frontend logs detailed path information (start, current, next, end) and timing data

#### Modifying Game Configuration

Edit `frontend/game_config.json`:

- **Modify Team Configuration**:
```json
{
  "teams": [
    { "name": "L", "who": "user48-1"},
    { "name": "R", "who": "user48-2"}
  ]
}
```

- **Modify Server Connections**:
```json
{
  "servers": {
    "user48-1": "ws://0.0.0.0:34712",
    "user48-2": "ws://0.0.0.0:34713"
  }
}
```

- **Modify Game Settings**:
```json
{
  "setup": {
    "numPlayers": 3,      // Players per team
    "numFlags": 9,        // Flags per team
    "useRandomFlags": true // Whether to randomly generate flag positions
  }
}
```

#### Debugging Frontend

- Open browser developer tools (F12 or Cmd+Option+I)
- Check Console tab for logs
- Check Network tab for WebSocket connections
- Ensure cache is disabled (Disable cache) to load latest code

## 🎮 Manual Control

The project provides a manual control script `backend/teleop.py` for keyboard control:

```bash
cd backend
python3 teleop.py <port>
```

Control keys:
- **L0**: `j`(left) `i`(up) `k`(down) `l`(right)
- **L1**: `t`(left) `f`(up) `g`(down) `h`(right)
- **L2**: `w`(up) `s`(down) `a`(left) `d`(right) or arrow keys

Press `q` to exit manual control.

## 🧪 Testing

The project includes a complete test suite:

### Backend Tests

```bash
cd backend
python3 -m pytest tests/ -v
```

Test coverage:
- Player action tests (tag, rescue, pickup, score)
- Pathfinding stability tests
- Player strategy generation tests
- Game state update tests

### Frontend Tests

**Unit Tests (Vitest)**:
```bash
cd frontend
pnpm test              # Run all unit tests
pnpm test:ui           # Run tests (UI mode)
pnpm test:coverage     # Generate test coverage report
```

**E2E Tests (Playwright)**:
```bash
cd frontend
pnpm test:e2e          # Run E2E tests (Chromium)
pnpm test:e2e:ui       # Run E2E tests (UI mode)
pnpm test:e2e:headed   # Run E2E tests (headed mode, visible browser)
```

Test coverage:
- Game scene initialization tests
- Player movement and pathfinding tests
- Game loop tests (grab flag and return)
- Strategy tests (offensive routes, defensive routes)

## ❓ Troubleshooting

### 1. Module Import Error

**Issue**: `ModuleNotFoundError: No module named 'xxx'`

**Solution**:
- Ensure virtual environment is activated
- Check if all dependencies are installed: `pip install -r requirements.txt`
- Verify Python interpreter path is correct

### 2. IPython Import Error

**Issue**: `ModuleNotFoundError: No module named 'IPython'`

**Solution**:
- IPython is optional, code handles compatibility
- To install: `pip install ipython`
- If still error, check import logic in `backend/lib/game_engine.py`

### 3. WebSocket Connection Failed

**Issue**: Frontend cannot connect to backend server

**Solution**:
- Check if backend server is started
- Verify port number matches configuration in `frontend/game_config.json`
- Check firewall settings
- Ensure WebSocket URL format is correct: `ws://localhost:port`

### 4. Indentation Error

**Issue**: `IndentationError: expected an indented block`

**Solution**:
- Ensure consistent indentation (recommend 4 spaces)
- Check if code blocks after `if/else/for` statements are correctly indented
- Use code formatting tools (like `black` or `autopep8`)

### 5. Port Already in Use

**Issue**: `Address already in use`

**Solution**:
- Find process using the port: `lsof -i :port` (macOS/Linux) or `netstat -ano | findstr :port` (Windows)
- Terminate the process or use another port
- Modify port configuration in `frontend/game_config.json`

### 6. Virtual Environment Issues

**Issue**: Cannot import packages after installing in virtual environment

**Solution**:
- Confirm virtual environment is activated (should see `(.venv)` prefix)
- Check if IDE is configured to use project virtual environment
- Recreate virtual environment: `rm -rf .venv && python3 -m venv .venv`

## 📄 License

See [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Issues and Pull Requests are welcome!

## 📚 Related Documentation

- [AGENTS.md](AGENTS.md) - AI agent development guide (detailed API documentation and code examples)
- [backend/lib/reinforcement_learning/README.md](backend/lib/reinforcement_learning/README.md) - Reinforcement learning training documentation

