# Training Monitor Specification

## Purpose
Training metrics collection and visualization system providing real-time statistics, logging, and performance analysis during DQN training.

## Requirements

### Requirement: Metrics Collection
The TrainingMonitor SHALL collect training metrics over time.

#### Scenario: Step logging
- **WHEN** `log_step(reward, loss, q_value)` is called
- **THEN** metrics are accumulated for current episode

#### Scenario: Episode logging
- **WHEN** `log_episode(episode, epsilon)` is called
- **THEN** episode metrics are finalized and stored

### Requirement: History Storage
The monitor SHALL maintain rolling history of metrics.

#### Scenario: Episode rewards
- **WHEN** episodes complete
- **THEN** rewards are stored in episode_rewards deque

#### Scenario: Episode losses
- **WHEN** episodes complete
- **THEN** average losses are stored in episode_losses deque

#### Scenario: Episode lengths
- **WHEN** episodes complete
- **THEN** step counts are stored in episode_lengths deque

#### Scenario: Epsilon history
- **WHEN** episodes complete
- **THEN** exploration rates are stored in epsilon_history deque

#### Scenario: History limit
- **WHEN** history exceeds max_history (default 20000)
- **THEN** oldest entries are removed

### Requirement: Statistics Computation
The monitor SHALL compute summary statistics over windows.

#### Scenario: Average reward
- **WHEN** `get_statistics(window=10)` is called
- **THEN** average over last 'window' episodes is computed

#### Scenario: Max/min tracking
- **WHEN** computing statistics
- **THEN** maximum and minimum values are identified

#### Scenario: Recent vs total
- **WHEN** computing statistics
- **THEN** both recent (window) and total averages are provided

### Requirement: Statistics Dictionary
The monitor SHALL return comprehensive statistics.

#### Scenario: Statistics structure
- **WHEN** `get_statistics()` returns
- **THEN** dict contains total_episodes, avg_reward, avg_loss, avg_episode_length

#### Scenario: Best episode tracking
- **WHEN** computing statistics
- **THEN** best_episode and best_reward are included

#### Scenario: Training time
- **WHEN** computing statistics
- **THEN** training_time string is included

### Requirement: Console Output
The monitor SHALL support formatted console output.

#### Scenario: Print statistics
- **WHEN** `print_statistics(episode, window)` is called
- **THEN** formatted report is printed to console

#### Scenario: Progress indication
- **WHEN** printing statistics
- **THEN** episode number and key metrics are shown

### Requirement: File Persistence
The monitor SHALL save statistics to files.

#### Scenario: JSON export
- **WHEN** `save_statistics(filename)` is called
- **THEN** full history and summary are saved to JSON

#### Scenario: CSV export
- **WHEN** `save_csv(filename)` is called
- **THEN** tabular data is saved for external analysis

### Requirement: Log Directory
The monitor SHALL use configurable log directory.

#### Scenario: Default directory
- **WHEN** monitor is created without log_dir
- **THEN** /tmp/ctf-ai is used

#### Scenario: Custom directory
- **WHEN** log_dir is specified
- **THEN** that directory is used for output

### Requirement: Training Visualization
The visualizer SHALL provide real-time training dashboards.

#### Scenario: Reward plot
- **WHEN** visualizing training
- **THEN** reward trend with moving average is displayed

#### Scenario: Loss plot
- **WHEN** visualizing training
- **THEN** loss trend with moving average is displayed

#### Scenario: Win rate plot
- **WHEN** visualizing training
- **THEN** win percentage with moving average is displayed

#### Scenario: Stats panel
- **WHEN** visualizing training
- **THEN** text summary of recent performance is shown

### Requirement: Training Advice
The visualizer SHALL provide automated training advice.

#### Scenario: Excellent performance
- **WHEN** win rate >= 80%
- **THEN** "Excellent, consider stopping" is suggested

#### Scenario: Good performance
- **WHEN** win rate is 60-80%
- **THEN** "Good, continue training" is suggested

#### Scenario: Poor performance
- **WHEN** win rate < 50%
- **THEN** "Poor, adjust hyperparameters" is suggested

### Requirement: Convergence Detection
The monitor SHALL detect training convergence.

#### Scenario: Reward stability
- **WHEN** reward standard deviation is low
- **THEN** convergence is indicated

#### Scenario: Loss plateau
- **WHEN** loss stops decreasing
- **THEN** potential convergence is noted

### Requirement: Real-Time Updates
The visualizer SHALL update plots in real-time.

#### Scenario: File monitoring
- **WHEN** training_stats.json is updated
- **THEN** visualizer refreshes plots

#### Scenario: Refresh rate
- **WHEN** visualizing
- **THEN** plots update periodically (e.g., every 5 seconds)

### Requirement: Q-Value Tracking
The monitor SHALL track Q-value statistics.

#### Scenario: Q-value storage
- **WHEN** training steps execute
- **THEN** Q-values are sampled and stored

#### Scenario: Q-value analysis
- **WHEN** analyzing training
- **THEN** Q-value trends can indicate learning progress
