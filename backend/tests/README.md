# 单元测试说明

所有测试已迁移到 pytest。

## 测试文件

- `test_game_initializer.py` - World 初始化功能测试
- `test_game_update_scenarios.py` - 游戏状态更新场景测试
- `test_player_action.py` - Player.action 方法测试
- `test_team_methods.py` - Team 类方法测试
- `test_weighted_path_finder.py` - WeightedPathFinder 功能测试

## 运行测试

### 运行所有测试

```bash
cd backend
python3 -m pytest tests/ -v
```

### 运行特定测试文件

```bash
cd backend
python3 -m pytest tests/test_game_initializer.py -v
python3 -m pytest tests/test_game_update_scenarios.py -v
python3 -m pytest tests/test_player_action.py -v
python3 -m pytest tests/test_team_methods.py -v
python3 -m pytest tests/test_weighted_path_finder.py -v
```

### 运行特定测试函数

```bash
cd backend
python3 -m pytest tests/test_game_initializer.py::test_init_creates_players_from_num_players -v
```

## 测试覆盖

### World 初始化测试 (test_game_initializer.py)

- ✅ 初始化设置 my_team_name
- ✅ 根据 numPlayers 创建玩家
- ✅ 根据 numFlags 创建旗帜
- ✅ 玩家和旗帜使用临时位置 (0, 0)
- ✅ 初始化重置游戏状态
- ✅ 初始化路径查找服务
- ✅ 支持 L 队和 R 队初始化

### 游戏状态更新测试 (test_game_update_scenarios.py)

- ✅ 旗帜更新
- ✅ 玩家位置更新
- ✅ 玩家拾取/放下旗帜
- ✅ 玩家被抓进监狱
- ✅ 玩家被营救
- ✅ 时间验证
- ✅ 得分检测

### Player.action 测试 (test_player_action.py)

- ✅ PICKUP_FLAG - 拾取旗帜
- ✅ DROP_FLAG - 放下旗帜
- ✅ SCORE_FLAG - 得分
- ✅ TAG_ENEMY - 标记敌人
- ✅ RESCUE_TEAMMATE - 营救队友
- ✅ 移动被墙阻挡
- ✅ 移动到地图边界

### Team 方法测试 (test_team_methods.py)

- ✅ get_enemy() 方法
- ✅ from_name() 方法
- ✅ 枚举值验证

### WeightedPathFinder 测试 (test_weighted_path_finder.py)

- ✅ 权重地图初始化
- ✅ 地图位置验证
- ✅ 获取敌方玩家
- ✅ 权重应用（min/max 模式）
- ✅ 障碍物保护
- ✅ 构建安全权重地图

## 共享 Fixtures

所有测试文件共享 `conftest.py` 中定义的 fixtures：

- `test_map` - 标准测试地图
- `world` - 已初始化的 World 实例
- `test_map_with_walls` - 带障碍物的测试地图
