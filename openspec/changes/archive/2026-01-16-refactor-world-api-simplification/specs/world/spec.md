## MODIFIED Requirements

### Requirement: Game Map Integration
The World SHALL integrate with the GameMap for spatial queries.

**BREAKING CHANGE**: Direct access to map methods and properties is now required. Wrapper methods have been removed.

#### Scenario: Map boundaries
- **WHEN** position validity is checked
- **THEN** code MUST use `world.map.is_valid_position(position)` directly (no wrapper)

#### Scenario: Territory queries
- **WHEN** checking if a position is in a specific territory
- **THEN** code MUST use `world.map.is_in_team_territory(position, team)` directly (no wrapper)

#### Scenario: Map dimensions
- **WHEN** accessing map width or height
- **THEN** code MUST use `world.map.width` and `world.map.height` directly (no wrapper properties)

#### Scenario: Wall positions
- **WHEN** accessing wall positions
- **THEN** code MUST use `world.map.walls` directly (no wrapper property)

#### Scenario: Target and prison areas
- **WHEN** accessing team target or prison positions/areas
- **THEN** code MUST use `world.map.get_team_target_positions(team)`, `world.map.get_team_prison_positions(team)`, `world.map.get_team_target_area(team)`, or `world.map.get_team_prison_area(team)` directly (no wrapper methods)
