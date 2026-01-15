## MODIFIED Requirements

### Requirement: Player Flag Interactions
The Player SHALL handle flag collection and carrying.

#### Scenario: Flag collection
- **WHEN** `collectFlag(flag)` is called
- **THEN** flag is attached to player and hasFlag is true

#### Scenario: Flag drop
- **WHEN** `dropFlag()` is called
- **THEN** carried flag is released

#### Scenario: Player caught with flag
- **WHEN** a player carrying a flag is caught and sent to prison
- **THEN** the player's hasFlag state is cleared
- **THEN** no new flag objects are created in the frontend
- **THEN** the backend updates the existing flag's position based on the player's caught position

#### Scenario: Visual indicator
- **WHEN** player carries a flag
- **THEN** visual feedback indicates flag possession
