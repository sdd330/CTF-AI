# Reward Function Specification

## Purpose
Reward calculation module computing learning signals based on game events, player actions, and strategic objectives to guide DQN training.

## Requirements

### Requirement: Reward Calculation Interface
The reward calculator SHALL compute rewards from game state transitions.

#### Scenario: Reward computation
- **WHEN** `calculate_reward(player, world, prev_state, action)` is called
- **THEN** scalar reward value is returned

#### Scenario: Reward clipping
- **WHEN** raw reward is computed
- **THEN** result is clipped to [-50, 200] range

### Requirement: Step Penalty
A small penalty SHALL discourage inefficient exploration.

#### Scenario: Step cost
- **WHEN** each step is taken
- **THEN** reward of -0.02 is applied

### Requirement: Flag Pickup Reward
Picking up an enemy flag SHALL give positive reward.

#### Scenario: Flag acquisition
- **WHEN** player picks up flag (has_flag and not prev_has_flag)
- **THEN** reward of +10.0 is added

### Requirement: Flag Loss Penalty
Losing a carried flag SHALL give negative reward.

#### Scenario: Flag drop
- **WHEN** player loses flag (not has_flag and prev_has_flag)
- **THEN** reward of -40.0 is applied

#### Scenario: Loss ratio
- **WHEN** comparing pickup to loss
- **THEN** 4:1 penalty ratio discourages careless flag handling

### Requirement: Capture Penalty
Being captured SHALL give negative reward.

#### Scenario: Prison entry
- **WHEN** player enters prison (in_prison and not prev_in_prison)
- **THEN** reward of -25.0 is applied

### Requirement: Scoring Reward
Scoring a flag SHALL give large positive reward.

#### Scenario: Flag score
- **WHEN** team score increases
- **THEN** reward of +150.0 is added

#### Scenario: Scoring dominance
- **WHEN** comparing rewards
- **THEN** scoring reward is highest to prioritize the objective

### Requirement: Base Entry Reward
Entering base with flag SHALL give intermediate reward.

#### Scenario: Base arrival
- **WHEN** player with flag enters target area
- **THEN** reward of +40.0 is added

### Requirement: Distance-Based Rewards
Approaching objectives SHALL give graduated rewards.

#### Scenario: Approach flag reward
- **WHEN** action=SCORING, no flag, and distance to flag <= 5
- **THEN** graduated reward (+0.7 to +2.0) based on proximity

#### Scenario: Approach base reward
- **WHEN** action=SCORING, has flag, and distance to base <= 5
- **THEN** graduated reward (+3.0 to +25.0) based on proximity

#### Scenario: Smooth distance reward
- **WHEN** player has flag
- **THEN** continuous reward +0.5 * (1/(1+dist)) encourages movement

### Requirement: Proximity Graduation
Distance rewards SHALL increase as player approaches target.

#### Scenario: Very close
- **WHEN** distance <= 1
- **THEN** maximum proximity bonus is applied (+25.0 or +2.0)

#### Scenario: Close
- **WHEN** distance <= 2
- **THEN** high proximity bonus is applied (+18.0 or +1.5)

#### Scenario: Medium
- **WHEN** distance <= 3
- **THEN** medium proximity bonus is applied (+10.0 or +0.7)

#### Scenario: Far
- **WHEN** distance <= 5
- **THEN** small proximity bonus is applied (+3.0 or +0.3)

### Requirement: Defense Rewards
Defending against enemies SHALL give positive reward.

#### Scenario: Defense positioning
- **WHEN** action=DEFENCE and enemy is in own territory
- **THEN** reward of +3.0 to +10.0 is added

#### Scenario: Flag carrier defense
- **WHEN** defending against enemy with flag
- **THEN** bonus +10.0 is added

### Requirement: Rescue Rewards
Attempting to rescue teammates SHALL give positive reward.

#### Scenario: Rescue action
- **WHEN** action=SAVING and teammates are in prison
- **THEN** reward of +1.0 to +6.0 based on active players

#### Scenario: Near prison bonus
- **WHEN** player is near enemy prison during rescue
- **THEN** additional +1.0 is added

### Requirement: Reward Balance
Rewards SHALL be balanced to encourage winning behavior.

#### Scenario: Offensive priority
- **WHEN** comparing strategy rewards
- **THEN** scoring rewards > defense rewards

#### Scenario: Risk-reward tradeoff
- **WHEN** player carries flag in enemy territory
- **THEN** high potential reward but high capture risk

#### Scenario: Team coordination
- **WHEN** multiple strategies are needed
- **THEN** rewards support role diversity

### Requirement: Previous State Tracking
The reward function SHALL compare current state to previous state.

#### Scenario: State persistence
- **WHEN** calculating reward
- **THEN** prev_state_dict contains has_flag, in_prison, position, team_score

#### Scenario: Delta detection
- **WHEN** state changes
- **THEN** appropriate rewards are triggered based on transitions
