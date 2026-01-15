# Change: Update Specs to Match Current Implementation

## Why
The current OpenSpec specifications are outdated and do not accurately reflect the actual code implementation. This creates confusion for AI agents and developers working with the codebase. The specs need to be updated to match the current implementation details, including:

- Player class interface details (plan() method signature, check() interface)
- World class implementation details (plan_actions() workflow, internal services)
- Utils function signatures (list_players, list_flags parameters)
- Architecture patterns (modular managers, lazy initialization)

## What Changes
- Update `specs/player/spec.md` to reflect actual Player interface:
  - `plan(suggested_strategy: Optional[Strategy]) -> Optional[Direction]` signature
  - `check(check_type: str, **kwargs)` interface with three types: "state", "relation", "position"
  - Compatibility properties (is_free, is_in_prison, has_flag)
  - Modular internal architecture (managers pattern)
  
- Update `specs/world/spec.md` to reflect actual World implementation:
  - `plan_actions()` workflow: calls `player.plan()` and collects results via GameInfoCollector
  - Direct `map` property access (no wrapper methods)
  - Internal service classes (GameInfoCollector, GameLogger, GameStateUpdater)
  - `find_path_to()` with `player_name` parameter for safe pathfinding
  
- Update `specs/utils/spec.md` to reflect actual function signatures:
  - `list_players(players: Dict[str, Player], team: Team, in_prison: Optional[bool], has_flag: Optional[bool])`
  - `list_flags(flags: Dict[str, Flag], team: Team, is_enemy: Optional[bool], can_pickup: Optional[bool])`
  - Rule check functions signatures

## Impact
- Affected specs: `player/spec.md`, `world/spec.md`, `utils/spec.md`
- Affected code: None (this is a documentation update)
- Breaking changes: None (specs are being updated to match existing code)
