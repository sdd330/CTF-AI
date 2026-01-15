# Change: Fix Flag Update Bugs and Reduce Logging

## Why
Several critical bugs were discovered during gameplay:
1. L team players were incorrectly targeting L team flags (own team flags) instead of R team flags (enemy flags)
2. Frontend was creating new flags when players were caught, causing flag count mismatches with backend
3. Excessive logging from safe_pathfinding and state updates was cluttering output

## What Changes
- **Fixed flag targeting bug**: Added debug checks to detect when enemy flag lists incorrectly contain own team flags
- **Fixed frontend flag creation**: Removed logic that created new flags when players are caught; backend now handles flag position updates through player state
- **Reduced logging**: Removed excessive logs from safe_pathfinding errors, state update requests, player action successes, and flag position updates
- **Restored correct backend logic**: Reverted to proper index-based flag matching in `_update_team_flags` method

## Impact
- Affected specs: `world`, `game-objects`
- Affected code:
  - `backend/lib/game_service/game.py` - Flag update logic
  - `backend/lib/data_models/player/player_strategy_executor.py` - Debug checks
  - `backend/lib/pathfinding_service/weighted_path_finder.py` - Logging reduction
  - `backend/lib/socket_service/request_handler.py` - Logging reduction
  - `backend/lib/data_models/player/player_actions.py` - Logging reduction
  - `backend/lib/data_models/flag.py` - Logging reduction
  - `frontend/src/game/managers/PhysicsManager.ts` - Removed flag creation on player catch
