# Neural Network Specification

## Purpose
Deep Q-Network architecture implementing a multi-layer perceptron with batch normalization, LeakyReLU activation, and dropout for Q-value approximation.

## Requirements

### Requirement: Network Architecture
The DQN network SHALL implement a configurable multi-layer perceptron.

#### Scenario: Default architecture
- **WHEN** DQN is created with defaults
- **THEN** hidden layers are [256, 128, 64] with input 19 and output 3

#### Scenario: Custom architecture
- **WHEN** hidden_dims parameter is provided
- **THEN** network uses specified layer dimensions

#### Scenario: Layer construction
- **WHEN** network is built
- **THEN** Linear layers connect input → hidden → output

### Requirement: Batch Normalization
The network SHALL optionally apply batch normalization after each hidden layer.

#### Scenario: BatchNorm enabled
- **WHEN** use_batch_norm=True
- **THEN** BatchNorm1d is applied after each hidden Linear layer

#### Scenario: BatchNorm disabled
- **WHEN** use_batch_norm=False
- **THEN** no batch normalization is applied

#### Scenario: Single sample handling
- **WHEN** batch_size=1 during training with BatchNorm
- **THEN** network temporarily switches to eval mode to avoid NaN

### Requirement: Activation Function
The network SHALL use LeakyReLU activation with negative slope.

#### Scenario: LeakyReLU application
- **WHEN** forward pass executes
- **THEN** LeakyReLU(0.01) is applied after each hidden layer

#### Scenario: Negative input handling
- **WHEN** input is negative
- **THEN** output is 0.01 * input (prevents dead neurons)

### Requirement: Dropout Regularization
The network SHALL apply dropout for regularization during training.

#### Scenario: Dropout enabled
- **WHEN** dropout_rate > 0
- **THEN** Dropout is applied after each hidden layer except the last

#### Scenario: Default dropout
- **WHEN** using default configuration
- **THEN** dropout_rate=0.1 is applied

#### Scenario: Training vs inference
- **WHEN** network is in eval mode
- **THEN** dropout is disabled

### Requirement: Weight Initialization
The network SHALL use Xavier uniform initialization.

#### Scenario: Linear weight init
- **WHEN** network is created
- **THEN** Linear layer weights use Xavier uniform initialization

#### Scenario: Bias init
- **WHEN** network is created
- **THEN** Linear layer biases are initialized to zero

### Requirement: Forward Pass
The network SHALL compute Q-values for all actions given a state.

#### Scenario: State input
- **WHEN** state tensor of shape (batch, 19) is passed
- **THEN** output tensor of shape (batch, 3) is returned

#### Scenario: Q-value interpretation
- **WHEN** output is computed
- **THEN** output[i] represents Q-value for action i (DEFENCE=0, SCORING=1, SAVING=2)

### Requirement: GPU Compatibility
The network SHALL support both CPU and CUDA execution.

#### Scenario: Device placement
- **WHEN** network.to(device) is called
- **THEN** all parameters are moved to specified device

#### Scenario: Mixed precision
- **WHEN** using CUDA
- **THEN** Float32 precision is used for stability

### Requirement: Parameter Count
The network SHALL be lightweight for fast inference.

#### Scenario: Default parameter count
- **WHEN** using default architecture [256, 128, 64]
- **THEN** total parameters are approximately 42,000

#### Scenario: Inference speed
- **WHEN** running forward pass
- **THEN** batch of 32 states processes in < 1ms on CPU
