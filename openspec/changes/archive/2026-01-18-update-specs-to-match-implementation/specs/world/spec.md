## MODIFIED Requirements

### Requirement: Action Planning
The World SHALL coordinate action planning for all players using a workflow that calls player.plan() and collects results.

#### Scenario: Automatic planning workflow
- **WHEN** `world.plan_actions(req)` is called
- **THEN** `world.update(req)` is called first to synchronize state
- **THEN** all non-prison players from `world.my_players` are iterated
- **THEN** for each player, `player.plan()` is called to get `Optional[Direction]`
- **THEN** directions are collected via `GameInfoCollector.collect_action()`
- **THEN** results are built via `GameInfoCollector.build_result_from_actions()` returning `{"actions": {}, "paths": {}, "timings": {}}`

#### Scenario: Action collection
- **WHEN** planning is complete
- **THEN** actions are returned in format `{"actions": {}, "paths": {}, "timings": {}}`
- **THEN** only actions for `world.my_players` are included (enemy players are filtered out)

### Requirement: Internal Service Architecture
The World SHALL use internal service classes for modular functionality.

#### Scenario: Service initialization
- **WHEN** a World is created
- **THEN** internal services are initialized: `PathFindingService`, `GameInfoCollector`, `GameLogger`, `GameStateUpdater`
- **THEN** services are private and accessed via `self._service_name` pattern

#### Scenario: State update delegation
- **WHEN** `world.update(req)` is called
- **THEN** `GameStateUpdater.update_flags_from_request(req)` is called
- **THEN** `GameStateUpdater.update_players_from_request(req)` is called
- **THEN** `world._check_scoring()` is called to detect and process scoring

#### Scenario: Action collection delegation
- **WHEN** actions need to be collected during planning
- **THEN** `GameInfoCollector.collect_action(player, direction)` is called for each player
- **THEN** `GameInfoCollector.build_result_from_actions(actions)` constructs the final result

### Requirement: Game Map Integration
The World SHALL integrate with the GameMap via direct property access.

**BREAKING CHANGE**: Direct access to map methods and properties is required. Wrapper methods have been removed.

#### Scenario: Map property access
- **WHEN** accessing map functionality
- **THEN** code MUST use `world.map` property directly (e.g., `world.map.is_valid_position(position)`)
- **THEN** code MUST use `world.map.width` and `world.map.height` for dimensions
- **THEN** code MUST use `world.map.walls` for wall positions
- **THEN** code MUST use `world.map.get_team_target_area(team)` and `world.map.get_team_prison_area(team)` for areas

### Requirement: Pathfinding Service
The World SHALL provide pathfinding services through PathFindingService.

#### Scenario: Path calculation with player context
- **WHEN** `world.find_path_to(start, end, player_name=name)` is called
- **THEN** if `player_name` is provided, the player is retrieved from `world.my_players`
- **THEN** if player is in prison, empty path is returned
- **THEN** `PathFindingService.find_path_to()` is called with player context for safe pathfinding
- **THEN** pathfinding timings are collected in `world._path_timings[player_name]`
- **THEN** the calculated path is returned as `List[Position]`
