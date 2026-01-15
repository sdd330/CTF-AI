# Gymnasium Environment Specification

## Purpose
Gymnasium-compatible environment wrapper for CTF gameplay supporting both single-agent and multi-agent training with standard RL interfaces.

## Requirements

### Requirement: Gymnasium Interface
The CTFGymEnv SHALL implement the standard Gymnasium API.

#### Scenario: Reset method
- **WHEN** `reset(seed, options)` is called
- **THEN** (observation, info) tuple is returned with initial state

#### Scenario: Step method
- **WHEN** `step(action)` is called
- **THEN** (observation, reward, terminated, truncated, info) tuple is returned

#### Scenario: Render method
- **WHEN** `render()` is called
- **THEN** environment state is rendered according to render_mode

#### Scenario: Close method
- **WHEN** `close()` is called
- **THEN** environment resources are cleaned up

### Requirement: Observation Space
The environment SHALL define a 19-dimensional continuous observation space.

#### Scenario: Space definition
- **WHEN** accessing observation_space
- **THEN** Box(shape=(19,), dtype=float32) is returned

#### Scenario: Observation range
- **WHEN** extracting observations
- **THEN** all values are normalized to [0, 1]

### Requirement: Action Space
The environment SHALL define a discrete action space with 3 actions.

#### Scenario: Space definition
- **WHEN** accessing action_space
- **THEN** Discrete(3) is returned

#### Scenario: Action mapping
- **WHEN** action is 0, 1, or 2
- **THEN** it maps to DEFENCE, SCORING, or SAVING respectively

### Requirement: Environment Reset
The reset method SHALL initialize game state from provided data.

#### Scenario: Init data reset
- **WHEN** `reset(options={'init_data': init_request})` is called
- **THEN** world is initialized from init_data

#### Scenario: Default reset
- **WHEN** `reset()` is called without options
- **THEN** previous or default configuration is used

#### Scenario: Step counter reset
- **WHEN** reset is called
- **THEN** step count is reset to 0

### Requirement: Step Execution
The step method SHALL execute game actions and return results.

#### Scenario: State persistence
- **WHEN** step begins
- **THEN** previous state (flag, prison, position, score) is saved

#### Scenario: Action conversion
- **WHEN** strategy action is received
- **THEN** it is converted to movement direction via pathfinding

#### Scenario: Move execution
- **WHEN** direction is determined
- **THEN** player position is updated and interactions processed

### Requirement: Action to Direction Conversion
The environment SHALL convert high-level strategies to movement.

#### Scenario: Defence action
- **WHEN** action=DEFENCE
- **THEN** pathfind toward nearest opponent in own territory

#### Scenario: Scoring action with flag
- **WHEN** action=SCORING and player has flag
- **THEN** pathfind toward own target area

#### Scenario: Scoring action without flag
- **WHEN** action=SCORING and player has no flag
- **THEN** pathfind toward nearest enemy flag

#### Scenario: Saving action
- **WHEN** action=SAVING
- **THEN** pathfind toward opponent prison area

### Requirement: Episode Termination
The environment SHALL handle episode termination conditions.

#### Scenario: Max steps truncation
- **WHEN** step count reaches max_steps (default 1000)
- **THEN** truncated=True is returned

#### Scenario: No early termination
- **WHEN** game events occur
- **THEN** terminated=False (episodes run to max_steps)

### Requirement: Multi-Agent Environment
The CTFMultiAgentGymEnv SHALL support simultaneous multi-agent training.

#### Scenario: Multi-agent observation space
- **WHEN** accessing observation_space
- **THEN** Dict({player_name: Box(19,)}) is returned

#### Scenario: Multi-agent action space
- **WHEN** accessing action_space
- **THEN** Dict({player_name: Discrete(3)}) is returned

#### Scenario: Joint step
- **WHEN** `step(action_dict)` is called
- **THEN** (obs_dict, reward_dict, terminated_dict, truncated_dict, info_dict) is returned

### Requirement: Player Management
The environment SHALL manage the controlled player.

#### Scenario: Player assignment
- **WHEN** environment is created with player_name
- **THEN** that player is controlled by the agent

#### Scenario: Player lookup
- **WHEN** executing actions
- **THEN** correct player object is retrieved from world

### Requirement: Info Dictionary
The environment SHALL return useful info in step results.

#### Scenario: Step info
- **WHEN** step completes
- **THEN** info contains current step count and player state

#### Scenario: Debug info
- **WHEN** debug mode is enabled
- **THEN** additional state information is included
