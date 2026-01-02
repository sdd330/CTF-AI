# Native 测试文档

基于 pytest 的测试框架，采用事件模拟和逻辑分离设计。

## 快速开始

```bash
# 安装依赖
pip3 install -r requirements.txt

# 运行所有测试
pytest

# 运行特定类型测试
pytest -m unit          # 单元测试
pytest -m integration   # 集成测试
pytest -m game_logic    # 游戏逻辑测试
pytest -m physics       # 物理系统测试
pytest -m event         # 事件模拟测试

# 生成覆盖率报告
pytest --cov=. --cov-report=html
```

## 测试结构

```
tests/
├── conftest.py              # pytest 配置和共享 fixtures
├── test_game_logic.py       # 游戏逻辑测试（CTFGame, GameState）
├── test_objects.py          # 游戏对象测试（Player, Flag）
├── test_scenes.py           # 场景系统测试
└── test_physics_events.py   # 物理系统事件测试
```

## 测试标记

- `@pytest.mark.unit` - 单元测试
- `@pytest.mark.integration` - 集成测试
- `@pytest.mark.game_logic` - 游戏逻辑测试
- `@pytest.mark.physics` - 物理系统测试
- `@pytest.mark.event` - 事件模拟测试

## 设计原则

### 事件模拟

使用 `event_simulator` fixture 模拟游戏事件：

```python
def test_event(event_simulator):
    events = []
    event_simulator.register("test", lambda: events.append(1))
    event_simulator.emit("test")
    assert len(events) == 1
```

### 逻辑分离

测试按功能模块分离：
- `test_game_logic.py` - 游戏核心逻辑
- `test_objects.py` - 游戏对象行为
- `test_scenes.py` - 场景系统
- `test_physics_events.py` - 物理事件

### Fixtures 复用

使用 `conftest.py` 中的 fixtures：
- `mock_game_map` - 模拟游戏地图
- `game_state` - 游戏状态实例
- `ctf_game` - CTFGame 实例
- `mock_player` - 创建玩家
- `mock_flag` - 创建旗帜
- `event_simulator` - 事件模拟器

## 示例

### 游戏逻辑测试

```python
@pytest.mark.unit
@pytest.mark.game_logic
class TestCTFGame:
    def test_initialization(self, ctf_game):
        assert ctf_game.game_map is not None
```

### 事件模拟测试

```python
@pytest.mark.unit
@pytest.mark.event
def test_player_move(event_simulator, mock_player):
    player = mock_player("L0", Team.LEFT, 5, 5)
    events = []
    event_simulator.register("move", lambda d: events.append(d))
    event_simulator.emit("move", Direction.RIGHT)
    assert len(events) == 1
```

## 注意事项

1. 所有测试使用 mock 的 pygame，不需要实际初始化
2. 测试会自动重置单例（通过 `reset_singletons` fixture）
3. 使用 `event_simulator` fixture 进行事件模拟
4. 每个测试文件专注于特定功能模块
