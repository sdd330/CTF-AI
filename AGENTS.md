<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

# CTF-AI Project Guide

## 核心架构

**World** (状态) → **Player.plan()** (决策) → **Action** (执行) → **World** (新状态)

## Server 入口

```python
from lib.game_engine import GameMap, World

game_map = GameMap()
world = World(game_map)

def start_game(req):
    world.init(req)

def plan_next_actions(req):
    return world.plan_actions(req)  # 自动规划（推荐）
    # 或自定义：
    # world.update(req)
    # actions = {}
    # for player in [p for p in world.my_players.values() if not p.is_in_prison]:
    #     actions[player.name] = "right"
    # return {"actions": actions, "paths": {}, "timings": {}}

def game_over(req):
    pass
```

## 核心 API

### World

```python
world.update(req)  # 必须先调用
world.plan_actions(req)  # 自动规划
world.find_path_to(start, end, player_name=name)
world.my_players, world.enemy_players  # Dict[str, Player]
world.my_flags, world.enemy_flags  # Dict[str, Flag]
world.map.width, world.map.height
world.map.is_in_team_territory(pos, team)
world.map.get_team_target_area(team)
```

### Player

```python
player.plan()  # 返回 Optional[Direction]
player.move(Direction.RIGHT)  # 返回 bool
player.check("state", state="is_free")
player.action(Action.PICKUP_FLAG, flag=flag)
player.is_free, player.is_in_prison, player.has_flag
```

## 快速参考

```python
# 获取玩家
my_players = [p for p in world.my_players.values() if not p.is_in_prison and not p.has_flag]
enemies = [p for p in world.enemy_players.values() if not p.is_in_prison]

# 获取旗帜
enemy_flags = [f for f in world.enemy_flags.values() if f.can_pickup]

# 路径查找
path = world.find_path_to(start, end, player_name=player.name)
if len(path) > 1:
    direction = player.position.direction_to(path[1])

# 规则检查
from lib.utils import can_tag_enemy, can_pickup_flag, can_score_flag
if can_pickup_flag(player, flag):
    player.action(Action.PICKUP_FLAG, flag=flag)
```

## 文件位置

- `backend/server.py` - AI 入口
- `backend/lib/game_service/game.py` - World 类
- `backend/lib/data_models/player/player.py` - Player 类
