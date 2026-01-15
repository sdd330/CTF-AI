# DQN Agent Specification

## Purpose
Deep Q-Network agent implementation with Double DQN, Prioritized Experience Replay, Huber loss, gradient clipping, and learning rate scheduling for training CTF AI players.

## Requirements

### Requirement: Agent Initialization
The DQNAgent SHALL be configurable with comprehensive hyperparameters.

#### Scenario: Default configuration
- **WHEN** DQNAgent is created with defaults
- **THEN** state_dim=19, action_dim=3, lr=0.0005, gamma=0.99 are applied

#### Scenario: Custom configuration
- **WHEN** DQNAgent is created with custom parameters
- **THEN** epsilon_start, epsilon_end, epsilon_decay, target_update_freq are configurable

#### Scenario: Device selection
- **WHEN** device parameter is specified
- **THEN** agent uses 'cpu' or 'cuda' accordingly

### Requirement: Epsilon-Greedy Action Selection
The agent SHALL use epsilon-greedy policy for exploration-exploitation balance.

#### Scenario: Exploration action
- **WHEN** `select_action(state, training=True)` is called and random < epsilon
- **THEN** a random action (0, 1, or 2) is returned

#### Scenario: Exploitation action
- **WHEN** `select_action(state, training=True)` is called and random >= epsilon
- **THEN** argmax of Q-values is returned

#### Scenario: Inference mode
- **WHEN** `select_action(state, training=False)` is called
- **THEN** always returns argmax of Q-values (no exploration)

### Requirement: Epsilon Decay
The agent SHALL decay exploration rate over training.

#### Scenario: Epsilon update
- **WHEN** `update_epsilon()` is called after each episode
- **THEN** epsilon is multiplied by epsilon_decay

#### Scenario: Epsilon floor
- **WHEN** epsilon falls below epsilon_end
- **THEN** epsilon is clamped to epsilon_end (default 0.01)

#### Scenario: Decay calculation
- **WHEN** using default decay rate 0.998
- **THEN** epsilon reaches ~0.01 after approximately 690 episodes

### Requirement: Double DQN
The agent SHALL support Double DQN to reduce Q-value overestimation.

#### Scenario: Double DQN target calculation
- **WHEN** use_double_dqn=True and computing targets
- **THEN** action is selected by Q-network but evaluated by target network

#### Scenario: Standard DQN fallback
- **WHEN** use_double_dqn=False
- **THEN** max Q-value from target network is used directly

### Requirement: Training Step
The agent SHALL perform TD learning updates from replay buffer samples.

#### Scenario: Batch sampling
- **WHEN** `train_step(batch_size=32)` is called
- **THEN** batch is sampled from replay buffer

#### Scenario: TD target computation
- **WHEN** computing targets
- **THEN** target = reward + gamma * next_q * (1 - done)

#### Scenario: Loss computation
- **WHEN** use_huber_loss=True
- **THEN** SmoothL1Loss (Huber) is used instead of MSELoss

#### Scenario: Gradient update
- **WHEN** loss is computed
- **THEN** gradients are clipped to grad_clip (default 10.0) before optimizer step

### Requirement: Target Network Updates
The agent SHALL periodically sync target network with Q-network.

#### Scenario: Target update frequency
- **WHEN** training_steps reaches target_update_freq (default 50)
- **THEN** target network weights are copied from Q-network

#### Scenario: Hard update
- **WHEN** target network is updated
- **THEN** full weight copy is performed (not soft update)

### Requirement: Prioritized Experience Replay
The agent SHALL optionally use priority-based sampling.

#### Scenario: PER enabled
- **WHEN** use_per=True
- **THEN** PrioritizedReplayBuffer is used with importance sampling weights

#### Scenario: Priority updates
- **WHEN** training step completes with PER
- **THEN** priorities are updated based on TD-errors

#### Scenario: PER disabled
- **WHEN** use_per=False
- **THEN** uniform random sampling from standard ReplayBuffer

### Requirement: Learning Rate Scheduling
The agent SHALL support optional learning rate schedules.

#### Scenario: Step LR schedule
- **WHEN** lr_scheduler='step'
- **THEN** learning rate is multiplied by 0.9 every 1000 steps

#### Scenario: Cosine annealing
- **WHEN** lr_scheduler='cosine'
- **THEN** learning rate follows cosine curve with T_max=10000

#### Scenario: No scheduling
- **WHEN** lr_scheduler=None
- **THEN** constant learning rate is used

### Requirement: Model Persistence
The agent SHALL support saving and loading trained models.

#### Scenario: Model saving
- **WHEN** `save_model(path)` is called
- **THEN** Q-network, target network, optimizer state, and metadata are saved

#### Scenario: Model loading
- **WHEN** `load_model(path)` is called
- **THEN** full agent state including epsilon and training steps is restored

#### Scenario: Checkpoint format
- **WHEN** saving model
- **THEN** PyTorch .pth format is used with state dict

### Requirement: Reward Delegation
The agent SHALL delegate reward calculation to reward module.

#### Scenario: Reward calculation
- **WHEN** `calculate_reward()` is called
- **THEN** reward_calculator.calculate_reward() is invoked

### Requirement: Strategy Scheduling
The agent SHALL delegate strategy assignment to scheduler module.

#### Scenario: Batch prediction
- **WHEN** `predict_schedule()` is called
- **THEN** scheduler.predict_schedule() assigns strategies to all players
