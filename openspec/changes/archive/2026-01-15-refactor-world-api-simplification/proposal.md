# Change: World API Simplification and Code Cleanup

## Why
The `World` class had accumulated many redundant wrapper methods that simply forwarded calls to underlying objects (especially `GameMap`). These methods added no value, increased code complexity, and violated the DRY principle. Additionally, verbose comments and inconsistent naming (`game_map` vs `map`) made the codebase harder to maintain.

## What Changes
- **REMOVED** redundant wrapper methods from `World` class:
  - `get_team_target_positions()`, `get_team_prison_positions()`, `get_team_target_area()`, `get_team_prison_area()`
  - `is_valid_position()`, `is_wall()`
  - `is_in_team_territory()`, `is_in_enemy_territory()`
  - `width`, `height`, `walls` properties
- **REMOVED** redundant helper methods:
  - `_initialize_map()` - directly call `initialize_map()` instead
  - `_plan_player_action()` - directly call `player.plan()` instead
  - `_process_player_data()` - inlined into `_update_team_players()`
- **RENAMED** `self.game_map` to `self.map` throughout codebase for consistency
- **REMOVED** verbose/redundant code comments that explained obvious code
- **UPDATED** all call sites to use direct `world.map.*` access instead of wrapper methods

**BREAKING**: External code using `world.get_team_target_positions()` etc. must now use `world.map.get_team_target_positions()` directly.

## Impact
- **Affected specs**: `world/spec.md` - API surface simplified
- **Affected code**: 
  - `backend/lib/game_service/game.py` - Main refactoring target
  - `backend/lib/data_models/player/*.py` - Updated to use `world.map.*`
  - `backend/lib/utils/*.py` - Updated to use `world.map.*`
  - `backend/lib/pathfinding_service/*.py` - Updated to use `world.map.*`
  - `backend/lib/reinforcement_learning/*.py` - Updated to use `world.map.*`
  - `backend/tests/*.py` - Updated test code
- **Benefits**: 
  - Reduced code complexity (~100+ lines removed)
  - Improved maintainability (fewer layers of indirection)
  - Consistent naming convention
  - Cleaner, more readable code
