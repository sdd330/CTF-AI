# CTF-AI Native (Pygame 版本)

基于 Python/pygame 实现的 Capture the Flag 游戏，采用面向对象设计，代码结构清晰。

## 快速开始

### 安装和运行

```bash
# 安装依赖
pip3 install -r requirements.txt

# 运行游戏
python3 main.py
```

### 游戏控制

- **WASD** - 控制 L0 玩家（左队）
- **方向键** - 控制 R0 玩家（右队）
- **SPACE** - 开始/暂停游戏
- **ESC** - 退出游戏

## 项目结构

```
native/
├── main.py              # 主程序入口
├── game/                # 游戏逻辑（CTFGame, GameState）
├── objects/             # 游戏对象（Player, Flag）
├── map/                 # 地图模块
├── renderer/            # 渲染模块
├── scenes/              # 场景系统（Boot, Preloader, Game, GameOver）
├── managers/            # 管理器模块
│   ├── input_manager.py    # 输入管理（策略+观察者模式）
│   ├── physics_manager.py  # 物理系统（碰撞检测）
│   ├── socket_manager.py   # 网络通信（WebSocket）
│   └── map_manager.py      # 地图管理
├── utils/               # 工具模块（配置、日志、统计）
├── tests/               # 测试（基于 pytest）
└── game_config.json     # 配置文件
```

## 核心系统

- **场景系统**: Boot → Preloader → Game → GameOver，生命周期管理
- **输入管理**: 支持键盘、远程控制、混合策略，观察者模式
- **物理系统**: 基于 Pygame Sprite/Group 的碰撞检测
- **网络通信**: WebSocket 连接，发布订阅模式
- **地图管理**: 基于 pytmx 加载 TMX 地图文件

## 配置

配置文件 `game_config.json` 优先查找 `native/game_config.json`，不存在则使用 `frontend/public/game_config.json`。

```json
{
  "teams": [
    { "name": "L", "who": "user48-1"},
    { "name": "R", "who": "user48-2"}
  ],
  "setup": {
    "numPlayers": 1,
    "numFlags": 1,
    "mapWidth": 20,
    "mapHeight": 20
  },
  "servers": {
    "user48-1": "ws://0.0.0.0:34712",
    "user48-2": "ws://0.0.0.0:34713"
  },
  "native": {
    "fps": 60,
    "tile_size": 32,
    "screen": { "width": 1200, "height": 800 }
  }
}
```

## 测试

基于 pytest 的测试框架，采用事件模拟和逻辑分离设计。

```bash
# 安装依赖（包含测试工具）
pip3 install -r requirements.txt

# 运行所有测试
pytest

# 运行特定类型测试
pytest -m unit              # 单元测试
pytest -m integration       # 集成测试
pytest -m game_logic        # 游戏逻辑测试
pytest -m physics           # 物理系统测试
pytest -m event             # 事件模拟测试

# 生成覆盖率报告
pytest --cov=. --cov-report=html
```

### 测试文件

- `tests/conftest.py` - pytest 配置和共享 fixtures
- `tests/test_game_logic.py` - 游戏逻辑测试
- `tests/test_objects.py` - 游戏对象测试
- `tests/test_scenes.py` - 场景系统测试
- `tests/test_physics_events.py` - 物理系统事件测试

详细测试文档请参考 `tests/README.md`

## 游戏规则

1. **目标**: 将敌方旗帜带回己方目标区域得分
2. **抓捕**: 在己方领地内与敌方玩家在同一位置可以抓捕对方
3. **监狱**: 被抓捕的玩家会被送到敌方监狱，需要队友营救
4. **营救**: 在敌方监狱内与队友在同一位置可以营救队友
5. **得分**: 携带敌方旗帜回到己方目标区域即可得分
6. **胜利**: 先达到设定分数的队伍获胜（默认 5 分）

## 使用示例

### 配置

```python
from native.utils import get_config

config = get_config()
num_players = config.num_players
map_width = config.map_width
```

### 输入管理

```python
from native.managers import InputManager, KeyboardInputStrategy, RemoteInputStrategy

keyboard = KeyboardInputStrategy()
remote = RemoteInputStrategy()
input_manager = InputManager(HybridInputStrategy(keyboard, remote))
input_manager.subscribe(observer)
```

### 网络连接

```python
from native.managers import SocketManager
from native.utils import Team, get_config

config = get_config()
socket_manager = SocketManager()
socket_manager.connect_team(Team.LEFT, config.get_team_server_url("L"))
```

## 注意事项

- 游戏使用格子坐标系统（32x32 像素/格子）
- 玩家移动是平滑的，但逻辑判断基于格子坐标
- 所有玩家必须到达目标位置后才能进行下一步移动（同步机制）
- 资源文件位于 `native/assets/`，如果不存在会使用默认渲染

## 与前端对应关系

- `frontend/src/game/objects/Player.ts` → `native/objects/player.py`
- `frontend/src/game/objects/Flag.ts` → `native/objects/flag.py`
- `frontend/src/game/scenes/Game.ts` → `native/game/game.py`
- `frontend/src/game/managers/GameStateManager.ts` → `native/game/game_state.py`
