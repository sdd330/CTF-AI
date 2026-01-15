---
name: rl-training
description: Reinforcement learning training for CTF-AI. Use when training DQN agents, adjusting hyperparameters, debugging training issues, analyzing rewards, or improving AI performance.
allowed-tools: Read, Bash(python:*), Bash(pip:*), Grep, Glob
---

# Reinforcement Learning Training Skill

You are an expert in reinforcement learning, specifically Deep Q-Networks (DQN) for game AI.

## Project Context

This CTF-AI project uses:
- **DQN Agent** with Double DQN, Prioritized Experience Replay, Huber loss
- **19-dimensional state vector**: player(5) + target(6) + enemy(4) + global(4)
- **3 actions**: DEFENCE(0), SCORING(1), SAVING(2)
- **Gymnasium environment** for training interface
- **PyTorch** for neural network

## Key Files

- `backend/lib/reinforcement_learning/agent.py` - DQNAgent class
- `backend/lib/reinforcement_learning/network.py` - Neural network architecture
- `backend/lib/reinforcement_learning/reward_calculator.py` - Reward function
- `backend/lib/reinforcement_learning/state_extractor.py` - Feature extraction
- `backend/lib/reinforcement_learning/training/train_gym.py` - Training script

## When Asked to Train

```bash
# Offline training
python3 -m lib.reinforcement_learning.training.train_gym 8080 --algorithm CustomDQN --train-offline

# Online training (requires game server)
python3 -m lib.reinforcement_learning.training.train_gym 34712 --algorithm CustomDQN
```

## Hyperparameter Guidelines

| Parameter | Default | Tuning Advice |
|-----------|---------|---------------|
| Learning rate | 0.0005 | Lower (0.0001) if unstable, higher (0.001) if slow |
| Epsilon decay | 0.998 | Slower (0.999) for more exploration |
| Gamma | 0.99 | Lower (0.95) for shorter-term focus |
| Batch size | 32 | Larger (64, 128) for more stable gradients |
| Target update | 50 | More frequent (20) for faster learning |

## Debugging Training Issues

1. **Reward not improving**: Check reward_calculator.py, ensure rewards are balanced
2. **Q-values exploding**: Enable gradient clipping, reduce learning rate
3. **Agent stuck in one action**: Increase exploration (epsilon), check state features
4. **Training unstable**: Enable Double DQN, use Huber loss, increase buffer size

## Reward Tuning

Current reward structure:
- Score flag: +150 (primary objective)
- Pick up flag: +10
- Lose flag: -40
- Get captured: -25
- Step penalty: -0.02

Adjust in `reward_calculator.py` if agent behavior is suboptimal.
