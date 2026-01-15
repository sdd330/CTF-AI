## MODIFIED Requirements

### Requirement: State Updates
The World SHALL update its state based on incoming game data.

#### Scenario: Update from request
- **WHEN** `world.update(req)` is called at the start of `plan_next_actions()`
- **THEN** the World synchronizes with the latest game state

#### Scenario: Flag state update
- **WHEN** flag data is received from frontend
- **THEN** flags are updated using index-based matching to ensure correct flag-to-data correspondence
- **THEN** flag positions and pickup states are synchronized without creating new flag objects

#### Scenario: Player list access
- **WHEN** `world.players` is accessed
- **THEN** the current list of all players is returned
