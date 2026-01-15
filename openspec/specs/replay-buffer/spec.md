# Replay Buffer Specification

## Purpose
Experience replay implementations including standard uniform sampling and Prioritized Experience Replay (PER) for stable and efficient DQN training.

## Requirements

### Requirement: Standard Replay Buffer
The ReplayBuffer SHALL store and sample experiences uniformly.

#### Scenario: Buffer creation
- **WHEN** ReplayBuffer(capacity=10000) is created
- **THEN** a fixed-size circular buffer is initialized

#### Scenario: Experience storage
- **WHEN** `push(state, action, reward, next_state, done)` is called
- **THEN** experience tuple is added to buffer

#### Scenario: FIFO eviction
- **WHEN** buffer reaches capacity
- **THEN** oldest experiences are removed first

#### Scenario: Uniform sampling
- **WHEN** `sample(batch_size)` is called
- **THEN** batch_size random experiences are returned

### Requirement: Experience Format
Experiences SHALL be stored in a consistent tensor format.

#### Scenario: State format
- **WHEN** storing state
- **THEN** 19-dimensional float32 tensor is used

#### Scenario: Action format
- **WHEN** storing action
- **THEN** scalar int64 tensor (0, 1, or 2) is used

#### Scenario: Reward format
- **WHEN** storing reward
- **THEN** scalar float32 tensor is used

#### Scenario: Done format
- **WHEN** storing done flag
- **THEN** boolean tensor is used

### Requirement: Batch Retrieval
The buffer SHALL return properly formatted tensors for training.

#### Scenario: Batch structure
- **WHEN** `sample(batch_size)` returns
- **THEN** tuple of (states, actions, rewards, next_states, dones) is returned

#### Scenario: Tensor shapes
- **WHEN** sampling batch of 32
- **THEN** states shape is (32, 19), actions shape is (32,)

### Requirement: Prioritized Replay Buffer
The PrioritizedReplayBuffer SHALL sample based on TD-error priorities.

#### Scenario: PER creation
- **WHEN** PrioritizedReplayBuffer(capacity, alpha, beta) is created
- **THEN** priority array and sum tree are initialized

#### Scenario: Initial priority
- **WHEN** new experience is added
- **THEN** priority is set to maximum current priority (default 1.0)

### Requirement: Priority Calculation
Priorities SHALL be computed from TD-errors with configurable exponent.

#### Scenario: Priority formula
- **WHEN** computing priority from TD-error
- **THEN** priority = (|TD_error| + epsilon)^alpha where epsilon=1e-6

#### Scenario: Alpha parameter
- **WHEN** alpha=0
- **THEN** sampling is uniform (ignores priorities)

#### Scenario: Full prioritization
- **WHEN** alpha=1.0
- **THEN** sampling is fully proportional to TD-error

### Requirement: Importance Sampling
PER SHALL correct sampling bias with importance weights.

#### Scenario: Weight calculation
- **WHEN** sampling with PER
- **THEN** weight[i] = (N * P[i])^(-beta) normalized by max weight

#### Scenario: Beta annealing
- **WHEN** sampling progresses
- **THEN** beta increases by beta_increment toward 1.0

#### Scenario: Bias correction
- **WHEN** beta=1.0
- **THEN** importance sampling fully corrects priority bias

### Requirement: Priority Updates
Priorities SHALL be updated after training with new TD-errors.

#### Scenario: Batch update
- **WHEN** `update_priorities(indices, td_errors)` is called
- **THEN** priorities at indices are recomputed from new TD-errors

#### Scenario: Sum tree update
- **WHEN** priorities change
- **THEN** sum tree is updated for O(log n) sampling

### Requirement: Segment Sampling
PER SHALL use segment-based sampling for diversity.

#### Scenario: Segment division
- **WHEN** sampling batch of size k
- **THEN** priority range is divided into k segments

#### Scenario: Segment sampling
- **WHEN** sampling from segment
- **THEN** one experience is sampled uniformly within each segment

### Requirement: Buffer Statistics
The buffer SHALL provide size and capacity information.

#### Scenario: Length query
- **WHEN** `len(buffer)` is called
- **THEN** current number of experiences is returned

#### Scenario: Capacity check
- **WHEN** checking if buffer is full
- **THEN** len(buffer) == capacity indicates full buffer

### Requirement: Memory Efficiency
The buffer SHALL be memory-efficient for large replay sizes.

#### Scenario: Deque implementation
- **WHEN** using standard buffer
- **THEN** collections.deque with maxlen is used

#### Scenario: Numpy arrays
- **WHEN** using PER buffer
- **THEN** numpy arrays store priorities for efficiency
