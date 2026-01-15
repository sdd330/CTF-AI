# Training Pipeline Specification

## Purpose
Complete training workflow for DQN agents supporting both online (against live opponents) and offline (self-play with mock data) training modes.

## Requirements

### Requirement: Training Modes
The pipeline SHALL support both online and offline training.

#### Scenario: Online training
- **WHEN** running without --train-offline flag
- **THEN** agent connects to game server via WebSocket

#### Scenario: Offline training
- **WHEN** running with --train-offline flag
- **THEN** agent trains against mock environment

### Requirement: Command Line Interface
The training script SHALL accept configuration via CLI arguments.

#### Scenario: Port specification
- **WHEN** `train_gym.py <port>` is run
- **THEN** agent connects to specified port for online training

#### Scenario: Algorithm selection
- **WHEN** --algorithm {DQN|PPO|A2C|CustomDQN} is specified
- **THEN** corresponding algorithm is used

#### Scenario: Model path
- **WHEN** --model-path is specified
- **THEN** training resumes from saved checkpoint

#### Scenario: Save interval
- **WHEN** --save-interval N is specified
- **THEN** model is saved every N episodes

#### Scenario: Max episodes
- **WHEN** --max-episodes N is specified
- **THEN** training stops after N episodes

### Requirement: Mock Data Generation
Offline training SHALL use realistic mock game data.

#### Scenario: Mock initialization
- **WHEN** creating mock init data
- **THEN** valid map, players, flags, and zones are generated

#### Scenario: Map configuration
- **WHEN** generating mock map
- **THEN** 20x20 grid with walls and zones is created

#### Scenario: Player spawning
- **WHEN** generating mock players
- **THEN** 3 players per team are placed in starting positions

#### Scenario: Flag placement
- **WHEN** generating mock flags
- **THEN** 9 flags per team are placed in respective territories

### Requirement: Episode Loop
Training SHALL execute standard RL episode structure.

#### Scenario: Episode reset
- **WHEN** new episode starts
- **THEN** environment is reset and initial observation extracted

#### Scenario: Step execution
- **WHEN** executing step
- **THEN** action selection, environment step, experience storage occur

#### Scenario: Episode termination
- **WHEN** truncated or terminated is True
- **THEN** episode ends and statistics are logged

### Requirement: Experience Collection
Training SHALL collect experiences for replay buffer.

#### Scenario: Experience storage
- **WHEN** step completes
- **THEN** (state, action, reward, next_state, done) is stored

#### Scenario: Buffer threshold
- **WHEN** buffer size >= batch_size (32)
- **THEN** training can proceed

### Requirement: Training Execution
Training steps SHALL be performed during episodes.

#### Scenario: Batch training
- **WHEN** sufficient experiences exist
- **THEN** agent.train_step(batch_size=32) is called

#### Scenario: Training frequency
- **WHEN** step completes
- **THEN** training step is performed

### Requirement: Model Checkpointing
Models SHALL be saved periodically during training.

#### Scenario: Periodic saving
- **WHEN** episode % save_interval == 0
- **THEN** model is saved to lib/models/gym_model_epN.pth

#### Scenario: Final model
- **WHEN** training completes
- **THEN** final model is saved as gym_model_final.pth

#### Scenario: Format selection
- **WHEN** using stable-baselines3
- **THEN** .zip format is used

### Requirement: Server Bridge Integration
Online training SHALL use GymServerBridge for communication.

#### Scenario: Bridge initialization
- **WHEN** online training starts
- **THEN** GymServerBridge connects to game server

#### Scenario: Game callbacks
- **WHEN** server sends messages
- **THEN** start_game, plan_next_actions, game_over are invoked

### Requirement: Stable-Baselines3 Integration
Training SHALL optionally use stable-baselines3 algorithms.

#### Scenario: DQN algorithm
- **WHEN** --algorithm DQN is specified
- **THEN** stable-baselines3 DQN is used

#### Scenario: PPO algorithm
- **WHEN** --algorithm PPO is specified
- **THEN** stable-baselines3 PPO is used

#### Scenario: Custom fallback
- **WHEN** stable-baselines3 is unavailable
- **THEN** CustomDQN with custom training loop is used

### Requirement: Training Statistics
Training progress SHALL be tracked and logged.

#### Scenario: Episode logging
- **WHEN** episode completes
- **THEN** reward, length, epsilon are logged

#### Scenario: Console output
- **WHEN** episode % 10 == 0
- **THEN** statistics are printed to console

#### Scenario: File persistence
- **WHEN** training completes
- **THEN** statistics are saved to JSON and CSV

### Requirement: Resource Management
Training SHALL properly manage system resources.

#### Scenario: GPU utilization
- **WHEN** CUDA is available
- **THEN** GPU is used for training

#### Scenario: Memory management
- **WHEN** replay buffer is full
- **THEN** old experiences are evicted

#### Scenario: Graceful shutdown
- **WHEN** training is interrupted
- **THEN** current model is saved before exit
