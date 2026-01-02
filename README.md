# Capture the Flag

A multiplayer Capture the Flag game project with AI agent control and reinforcement learning support.

## 📖 Documentation

- **[中文文档 (Chinese)](README_zh.md)** - 完整的中文开发文档
- **[English Documentation](README_en.md)** - Complete English development guide  
- **[AI Agents Guide](AGENTS.md)** - API reference and code examples for AI development

## 🚀 Quick Start

### Setup Python Virtual Environment

**Create virtual environment:**
```bash
python3 -m venv .venv
```

**Activate virtual environment:**

**macOS/Linux:**
```bash
source .venv/bin/activate
```

**Windows:**
```bash
.venv\Scripts\activate
```

After activation, you should see `(.venv)` prefix in your command prompt.

### Install Dependencies

```bash
# 1. Install dependencies
cd backend && pip install -r requirements.txt

# For training (optional, requires PyTorch):
./install_dependencies.sh
```

### Start the Game

```bash
# 2. Start frontend server (Vite dev server)
cd ../frontend && pnpm dev

# 3. Start backend servers (in separate terminals)
cd ../backend
python3 server.py 34712  # Team L
python3 server.py 34713  # Team R

# 4. Open browser: http://localhost:8000
```

**Note**: Make sure virtual environment is activated before running commands.

## 🎯 Features

- 🎮 Real-time multiplayer game via WebSocket
- 🤖 AI agent control (rule-based & reinforcement learning)
- 🗺️ Dynamic map system with obstacles
- 📊 Training visualization and analysis
- 🔧 Modular, object-oriented code architecture
- 🎯 Minimal interface design - Player class with 4 core methods (plan, move, check, action)
- 🧩 Highly modular - Player class decomposed into specialized manager classes
- ✅ Comprehensive testing - 85+ unit tests covering all core interfaces

## 📚 Project Structure

```
CTF-AI/
├── backend/                    # Backend server (AI logic)
│   ├── server.py              # Main server file - implement AI here
│   ├── lib/                    # Core game engine library
│   │   ├── data_models/        # Data models (Player, Flag, etc.)
│   │   │   └── player/         # Modularized Player class
│   │   │       ├── player.py   # Main Player class (4 core interfaces)
│   │   │       ├── player_state.py, player_actions.py, etc.  # Manager classes
│   │   ├── game_service/       # Game logic (World class)
│   │   ├── map_service/        # Map management
│   │   ├── pathfinding_service/ # Pathfinding algorithms
│   │   ├── utils/              # Utility functions
│   │   └── reinforcement_learning/  # RL implementation
│   └── tests/                  # Unit tests (85+ tests)
├── frontend/                    # Modern frontend (Vue 3 + TypeScript + Vite + Phaser 3)
│   ├── src/                    # TypeScript source code
│   │   ├── game/               # Game core (managers, objects, scenes)
│   │   └── components/         # Vue components
│   └── public/                 # Static assets
└── README_*.md, AGENTS.md      # Documentation files
```

For detailed information, see [README_zh.md](README_zh.md) or [README_en.md](README_en.md).

