# Game State Manager Specification

## Purpose
Central state management for the game, implementing a state machine for game flow and serving as the single source of truth for all game data.

## Requirements

### Requirement: State Container
The GameStateManager SHALL serve as the single source of truth for game state.

#### Scenario: State initialization
- **WHEN** GameStateManager is created
- **THEN** default game state is initialized

#### Scenario: State access
- **WHEN** any component needs game state
- **THEN** consistent, up-to-date state is provided

### Requirement: Game Flow State Machine
The GameStateManager SHALL implement a state machine for game flow.

#### Scenario: Loading state
- **WHEN** game is starting
- **THEN** state is 'loading' with substates for assets and config

#### Scenario: Ready state
- **WHEN** assets and config are loaded
- **THEN** state transitions to 'ready'

#### Scenario: Playing state
- **WHEN** game starts
- **THEN** state transitions to 'playing'

#### Scenario: Ended state
- **WHEN** game finishes
- **THEN** state transitions to 'ended'

### Requirement: State Substates
The system SHALL support substates for detailed flow tracking.

#### Scenario: Loading assets substate
- **WHEN** in 'loading' state loading assets
- **THEN** substate is 'loadingAssets'

#### Scenario: Loading config substate
- **WHEN** in 'loading' state loading config
- **THEN** substate is 'loadingConfig'

#### Scenario: Running substate
- **WHEN** game is actively playing
- **THEN** substate is 'running'

#### Scenario: Paused substate
- **WHEN** game is paused
- **THEN** substate is 'paused'

### Requirement: Score Tracking
The GameStateManager SHALL track team scores.

#### Scenario: Score initialization
- **WHEN** game starts
- **THEN** both team scores are set to 0

#### Scenario: Score update
- **WHEN** a team scores a flag
- **THEN** that team's score is incremented

### Requirement: Map Data Management
The GameStateManager SHALL store map configuration data.

#### Scenario: Wall storage
- **WHEN** map is generated
- **THEN** wall positions are stored in state

#### Scenario: Obstacle storage
- **WHEN** map is generated
- **THEN** obstacle positions are stored in state

### Requirement: Team State Generation
The GameStateManager SHALL generate team-specific state data.

#### Scenario: Team state creation
- **WHEN** `generateTeamState(team)` is called
- **THEN** flags, players, target zone, and prison zone for that team are returned

### Requirement: Config Loading
The GameStateManager SHALL load game configuration from game_config.json.

#### Scenario: Config fetch
- **WHEN** loading configuration
- **THEN** game_config.json is fetched and parsed

#### Scenario: Default fallback
- **WHEN** config loading fails
- **THEN** sensible defaults are applied

### Requirement: Registry Integration
The GameStateManager SHALL use Phaser's registry for cross-scene state sharing.

#### Scenario: Registry storage
- **WHEN** state changes
- **THEN** state is stored in scene registry

#### Scenario: Registry retrieval
- **WHEN** scenes need shared state
- **THEN** state is retrieved from registry
