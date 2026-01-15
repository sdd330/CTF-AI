## MODIFIED Requirements

### Requirement: Player Query Functions
The system SHALL provide filtering functions for player lists with specific parameter signatures.

#### Scenario: List players with filters
- **WHEN** `list_players(players: Dict[str, Player], team: Team, in_prison: Optional[bool] = None, has_flag: Optional[bool] = None)` is called
- **THEN** all players from the specified team are returned
- **THEN** if `in_prison` is not None, only players matching that prison state are returned
- **THEN** if `has_flag` is not None, only players matching that flag possession state are returned
- **THEN** returns `List[Player]`

#### Scenario: Filter by team only
- **WHEN** `list_players(players, team=Team.LEFT)` is called without in_prison or has_flag
- **THEN** all players from Team LEFT are returned regardless of state

#### Scenario: Filter by state combinations
- **WHEN** `list_players(players, team=Team.LEFT, in_prison=False, has_flag=False)` is called
- **THEN** only free players from Team LEFT without flags are returned

### Requirement: Flag Query Functions
The system SHALL provide filtering functions for flag lists with specific parameter signatures.

#### Scenario: List flags with filters
- **WHEN** `list_flags(flags: Dict[str, Flag], team: Team, is_enemy: Optional[bool] = None, can_pickup: Optional[bool] = None)` is called
- **THEN** if `is_enemy` is None, all flags are returned
- **THEN** if `is_enemy` is True, only flags from the enemy team are returned
- **THEN** if `is_enemy` is False, only flags from the specified team are returned
- **THEN** if `can_pickup` is not None, only flags matching that pickup availability are returned
- **THEN** returns `List[Flag]`

#### Scenario: Filter enemy flags
- **WHEN** `list_flags(flags, team=Team.LEFT, is_enemy=True, can_pickup=True)` is called
- **THEN** only pickupable enemy flags (Team RIGHT flags when team is LEFT) are returned

#### Scenario: Filter team flags
- **WHEN** `list_flags(flags, team=Team.LEFT, is_enemy=False)` is called
- **THEN** only flags belonging to Team LEFT are returned

### Requirement: Rule Checking Functions
The system SHALL provide game rule validation functions with specific signatures.

#### Scenario: Can tag enemy
- **WHEN** `can_tag_enemy(player: Player, enemy: Player, world: World)` is called
- **THEN** true is returned only if: player is in own territory, enemy is in player's territory, and both are free

#### Scenario: Can rescue teammate
- **WHEN** `can_rescue_teammate(player: Player, teammate: Player, world: World)` is called
- **THEN** true is returned only if: teammate is in prison, player is adjacent to teammate, and both are from same team

#### Scenario: Can pickup flag
- **WHEN** `can_pickup_flag(player: Player, flag: Flag)` is called
- **THEN** true is returned only if: player is adjacent to flag, flag can be picked up, and player is free

#### Scenario: Can score flag
- **WHEN** `can_score_flag(player: Player)` is called
- **THEN** true is returned only if: player has flag and player is in base area
