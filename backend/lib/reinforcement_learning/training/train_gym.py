"""
基于Gymnasium的RL训练脚本
支持多种RL算法：DQN, PPO, A2C, CustomDQN
支持在线训练（连接游戏服务器）和离线训练（模拟环境）
"""

import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(SCRIPT_DIR)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import asyncio
import numpy as np

try:
    from stable_baselines3 import DQN, PPO, A2C
    from stable_baselines3.common.callbacks import EvalCallback, CheckpointCallback
    from stable_baselines3.common.monitor import Monitor
    STABLE_BASELINES3_AVAILABLE = True
except ImportError:
    STABLE_BASELINES3_AVAILABLE = False

from lib.game_engine import GameMap, World, run_game_server
from lib.reinforcement_learning import DQNAgent
from lib.reinforcement_learning.gym_env import CTFGymEnv
from lib.reinforcement_learning.gym_server_bridge import GymServerBridge, create_gym_server_callbacks
from lib.reinforcement_learning.training_monitor import TrainingMonitor
from lib.reinforcement_learning.training.mock_data import create_mock_init_data

training_agent, training_bridge, training_monitor, world, env = None, None, None, None, None


def create_training_agent(algorithm: str = "DQN", **kwargs):
    """创建训练智能体"""
    global env
    if env is None:
        env = CTFGymEnv(world=World(GameMap()), player_name="L0", max_steps=1000)
        if STABLE_BASELINES3_AVAILABLE:
            os.makedirs("/tmp/ctf-ai/gym_training", exist_ok=True)
            env = Monitor(env, "/tmp/ctf-ai/gym_training/")

    if algorithm == "CustomDQN":
        return DQNAgent(state_dim=19, action_dim=3, device='cpu', **kwargs)
    elif STABLE_BASELINES3_AVAILABLE:
        if algorithm == "DQN":
            return DQN("MlpPolicy", env, learning_rate=kwargs.get('learning_rate', 0.0005),
                       buffer_size=kwargs.get('buffer_size', 10000), learning_starts=kwargs.get('learning_starts', 1000),
                       target_update_interval=kwargs.get('target_update_interval', 50), verbose=1)
        elif algorithm == "PPO":
            return PPO("MlpPolicy", env, learning_rate=kwargs.get('learning_rate', 0.0003),
                       n_steps=kwargs.get('n_steps', 2048), batch_size=kwargs.get('batch_size', 64), verbose=1)
        elif algorithm == "A2C":
            return A2C("MlpPolicy", env, learning_rate=kwargs.get('learning_rate', 0.0007), verbose=1)
        raise ValueError(f"Unknown algorithm: {algorithm}")
    return DQNAgent(state_dim=19, action_dim=3, device='cpu', **kwargs)


def run_offline_training_sb3(args, env, training_agent):
    """使用stable-baselines3进行离线训练"""
    os.makedirs("/tmp/ctf-ai/gym_eval", exist_ok=True)
    eval_cb = EvalCallback(env, best_model_save_path="lib/models/gym_best/", log_path="/tmp/ctf-ai/gym_eval/",
                           eval_freq=1000, deterministic=True, render=False)
    ckpt_cb = CheckpointCallback(save_freq=10000, save_path="lib/models/gym_checkpoints/", name_prefix="gym_model")
    training_agent.learn(total_timesteps=100000, callback=[eval_cb, ckpt_cb], log_interval=10)
    training_agent.save("lib/models/gym_model_final.zip")
    print("\n[Offline Training] Final model saved to lib/models/gym_model_final.zip")


def run_offline_training_custom(args, env, training_agent, training_monitor):
    """使用自定义DQN进行离线训练"""
    for episode in range(args.max_episodes):
        obs, _ = env.reset(options={'init_data': create_mock_init_data()})
        for step in range(1000):
            prev_obs = obs.copy() if isinstance(obs, np.ndarray) else obs
            action = training_agent.predict(obs, deterministic=False)[0] if hasattr(training_agent, 'predict') else training_agent.select_action(obs, training=True)
            next_obs, reward, terminated, truncated, _ = env.step(int(action))

            if hasattr(training_agent, 'replay_buffer'):
                training_agent.replay_buffer.push(prev_obs, action, reward, next_obs, terminated or truncated)
            loss = training_agent.train_step(batch_size=32) if hasattr(training_agent, 'train_step') else None
            training_monitor.log_step(reward, loss)
            obs = next_obs
            if terminated or truncated:
                break

        if hasattr(training_agent, 'update_epsilon'):
            training_agent.update_epsilon()
        training_monitor.log_episode(episode, getattr(training_agent, 'epsilon', 0.0))

        if episode % 10 == 0:
            training_monitor.print_statistics(episode)
            training_monitor.save_statistics("training_stats.json")
            training_monitor.save_csv("training_log.csv")
        if episode % args.save_interval == 0:
            if hasattr(training_agent, 'save'):
                training_agent.save(f"lib/models/gym_model_ep{episode}.zip")
            elif hasattr(training_agent, 'save_model'):
                training_agent.save_model(f"lib/models/gym_model_ep{episode}.pth")

    training_monitor.save_statistics("training_stats.json")
    training_monitor.save_csv("training_log.csv")
    print("\n[Offline Training] Training completed!")


async def run_online_training(args, env, training_agent, training_monitor, world):
    """在线训练（连接游戏服务器）"""
    print(f"\n[Online Training] Connecting to game server on port {args.port}")
    bridge = GymServerBridge(env, training_agent, world)
    start_fn, plan_fn, end_fn = create_gym_server_callbacks(bridge)

    try:
        await run_game_server(args.port, start_fn, plan_fn, end_fn)
    except KeyboardInterrupt:
        print("\n[Training] Training interrupted by user")
        if training_agent:
            os.makedirs("lib/models", exist_ok=True)
            if hasattr(training_agent, 'save'):
                training_agent.save("lib/models/gym_model_final.zip")
            elif hasattr(training_agent, 'save_model'):
                training_agent.save_model("lib/models/gym_model_final.pth")
        if training_monitor:
            training_monitor.save_statistics("gym_training_stats.json")
            training_monitor.save_csv("gym_training_log.csv")
    except Exception as e:
        print(f"[Training] Server Stopped: {e}")
        sys.exit(1)


async def main():
    global training_agent, training_monitor, world, env
    import argparse
    parser = argparse.ArgumentParser(description='Gym-based RL Training')
    parser.add_argument('port', type=int, help='Server port')
    parser.add_argument('--algorithm', type=str, default='DQN', choices=['DQN', 'PPO', 'A2C', 'CustomDQN'])
    parser.add_argument('--model-path', type=str, default=None)
    parser.add_argument('--save-interval', type=int, default=10)
    parser.add_argument('--max-episodes', type=int, default=10000)
    parser.add_argument('--train-offline', action='store_true')
    args = parser.parse_args()

    print(f"{'='*60}\nGymnasium-based RL Training\n{'='*60}")
    print(f"Algorithm: {args.algorithm}, Port: {args.port}, Max Episodes: {args.max_episodes}, Offline: {args.train_offline}\n{'='*60}")

    world = World(GameMap())
    env = CTFGymEnv(world=world, player_name="L0", max_steps=1000)
    training_agent = create_training_agent(algorithm=args.algorithm)

    if args.model_path and os.path.exists(args.model_path):
        if hasattr(training_agent, 'load'):
            training_agent = training_agent.load(args.model_path, env=env)
        elif hasattr(training_agent, 'load_model'):
            training_agent.load_model(args.model_path)
        print(f"Loaded model from {args.model_path}")

    os.makedirs("/tmp/ctf-ai", exist_ok=True)
    training_monitor = TrainingMonitor(log_dir="/tmp/ctf-ai")

    if args.train_offline:
        print("\n[Offline Training] Starting offline training...")
        if STABLE_BASELINES3_AVAILABLE and args.algorithm != "CustomDQN":
            run_offline_training_sb3(args, env, training_agent)
        else:
            run_offline_training_custom(args, env, training_agent, training_monitor)
    else:
        await run_online_training(args, env, training_agent, training_monitor, world)


if __name__ == "__main__":
    asyncio.run(main())
