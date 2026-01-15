# State Extraction Specification

## Purpose
Feature extraction module converting game state into a 19-dimensional normalized vector suitable for neural network input.

## Requirements

### Requirement: Feature Vector Structure
The state extractor SHALL produce a 19-dimensional feature vector.

#### Scenario: Feature extraction
- **WHEN** `extract_state_features(player, world)` is called
- **THEN** numpy array of shape (19,) with dtype float32 is returned

#### Scenario: Feature composition
- **WHEN** extracting features
- **THEN** vector contains player(5) + target(6) + enemy(4) + global(4) features

### Requirement: Player State Features
The extractor SHALL include 5 features describing player state.

#### Scenario: Position features
- **WHEN** extracting player position
- **THEN** pos_x_norm and pos_y_norm are computed in [0, 1]

#### Scenario: Flag possession
- **WHEN** player has flag
- **THEN** has_flag feature is 1.0, else 0.0

#### Scenario: Prison state
- **WHEN** player is in prison
- **THEN** in_prison feature is 1.0, else 0.0

#### Scenario: Territory position
- **WHEN** player is in enemy territory
- **THEN** in_enemy_territory feature is 1.0, else 0.0

### Requirement: Target Information Features
The extractor SHALL include 6 features describing objectives.

#### Scenario: Nearest flag distance
- **WHEN** enemy flags exist
- **THEN** nearest_flag_dist is normalized Manhattan distance

#### Scenario: Flag direction encoding
- **WHEN** computing flag direction
- **THEN** one-hot encoding [right, down, left, up] indicates primary direction

#### Scenario: Target distance with flag
- **WHEN** player has flag
- **THEN** target_dist_if_has_flag is distance to own base

#### Scenario: No flag case
- **WHEN** player has no flag
- **THEN** target_dist_if_has_flag is 1.0 (maximum)

### Requirement: Enemy Information Features
The extractor SHALL include 4 features describing threats.

#### Scenario: Nearest enemy distance
- **WHEN** enemies exist
- **THEN** nearest_enemy_dist is normalized Manhattan distance

#### Scenario: Enemy danger weighting
- **WHEN** computing danger
- **THEN** enemy_danger_weighted considers distance and territory

#### Scenario: Enemy has flag
- **WHEN** any enemy has a flag
- **THEN** enemy_has_flag feature is 1.0

#### Scenario: Enemy in prison
- **WHEN** any enemy is in prison
- **THEN** enemy_in_prison feature is 1.0

### Requirement: Global Information Features
The extractor SHALL include 4 features describing game state.

#### Scenario: Flag counts
- **WHEN** extracting flag counts
- **THEN** my_flags_count_norm and enemy_flags_count_norm are in [0, 1]

#### Scenario: Score tracking
- **WHEN** extracting scores
- **THEN** my_score_norm and enemy_score_norm are in [0, 1]

### Requirement: Position Normalization
All positions SHALL be normalized to [0, 1] range.

#### Scenario: X coordinate normalization
- **WHEN** normalizing x position
- **THEN** x_norm = (x + 0.5) / (width + 1)

#### Scenario: Y coordinate normalization
- **WHEN** normalizing y position
- **THEN** y_norm = (y + 0.5) / (height + 1)

#### Scenario: Clamping
- **WHEN** normalized value exceeds bounds
- **THEN** value is clamped to [0, 1]

### Requirement: Distance Normalization
All distances SHALL be normalized relative to map size.

#### Scenario: Manhattan distance normalization
- **WHEN** normalizing distance
- **THEN** dist_norm = min(manhattan_distance / (width + height), 1.0)

### Requirement: Danger Calculation
Enemy danger SHALL be weighted by proximity and territory.

#### Scenario: Base danger
- **WHEN** computing danger for enemy
- **THEN** danger_base = 1.0 / (min_dist_to_my_flag + 1.0)

#### Scenario: Territory multiplier
- **WHEN** enemy is in my territory
- **THEN** danger is multiplied by 2.0

#### Scenario: Danger normalization
- **WHEN** finalizing danger
- **THEN** danger_weighted = min(danger_base * territory_mult / 2.0, 1.0)

### Requirement: Direction Encoding
Flag direction SHALL use one-hot encoding.

#### Scenario: Direction calculation
- **WHEN** computing direction to flag
- **THEN** dx = flag_x - player_x, dy = flag_y - player_y

#### Scenario: Horizontal priority
- **WHEN** |dx| >= |dy|
- **THEN** right (dx > 0) or left (dx < 0) is set to 1.0

#### Scenario: Vertical priority
- **WHEN** |dy| > |dx|
- **THEN** down (dy > 0) or up (dy < 0) is set to 1.0

### Requirement: Edge Case Handling
The extractor SHALL handle edge cases gracefully.

#### Scenario: No enemies
- **WHEN** no enemies exist
- **THEN** enemy features use default safe values

#### Scenario: No flags
- **WHEN** no enemy flags exist
- **THEN** flag features use maximum distance values

#### Scenario: Player in prison
- **WHEN** player is in prison
- **THEN** appropriate features reflect imprisoned state
