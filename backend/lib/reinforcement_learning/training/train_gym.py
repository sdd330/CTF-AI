"""
基于Gymnasium的RL训练脚本
使用Gymnasium标准接口和stable-baselines3进行训练

这是唯一的训练脚本，完全基于Gymnasium标准接口。
支持多种RL算法：DQN, PPO, A2C, CustomDQN
支持在线训练（连接游戏服务器）和离线训练（模拟环境）
"""

import sys
import os

# 添加路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SCRIPT_DIR)  # lib/reinforcement_learning
GRANDPARENT_DIR = os.path.dirname(PARENT_DIR)  # lib
BACKEND_DIR = os.path.dirname(GRANDPARENT_DIR)  # backend
# 将 backend 目录添加到路径，这样可以直接导入 lib
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import asyncio
import numpy as np
from typing import Optional

try:
    from stable_baselines3 import DQN, PPO, A2C
    from stable_baselines3.common.callbacks import EvalCallback, CheckpointCallback
    from stable_baselines3.common.monitor import Monitor
    STABLE_BASELINES3_AVAILABLE = True
except ImportError:
    STABLE_BASELINES3_AVAILABLE = False
    print("Warning: stable-baselines3 not installed. Install with: pip install stable-baselines3")

from lib.game_engine import GameMap, World, run_game_server
from lib.reinforcement_learning import DQNAgent
from lib.reinforcement_learning.gym_env import CTFGymEnv
from lib.reinforcement_learning.gym_server_bridge import GymServerBridge, create_gym_server_callbacks
from lib.reinforcement_learning.training_monitor import TrainingMonitor


# 全局变量
training_agent = None
training_bridge = None
training_monitor = None
world = None
env = None


def create_training_agent(algorithm: str = "DQN", **kwargs):
    """
    创建训练智能体
    
    Args:
        algorithm: 算法名称 ("DQN", "PPO", "A2C", "CustomDQN")
        **kwargs: 算法特定参数
    
    Returns:
        智能体实例
    """
    global env
    
    if env is None:
        # 创建Gymnasium环境
        world = World(GameMap())
        env = CTFGymEnv(world=world, player_name="L0", max_steps=1000)
        # 包装Monitor（日志保存到系统临时目录）
        if STABLE_BASELINES3_AVAILABLE:
            os.makedirs("/tmp/ctf-ai/gym_training", exist_ok=True)
            env = Monitor(env, "/tmp/ctf-ai/gym_training/")
    
    if algorithm == "CustomDQN":
        # 使用自定义DQNAgent
        agent = DQNAgent(
            state_dim=19,
            action_dim=3,
            device='cpu',
            **kwargs
        )
        return agent
    elif STABLE_BASELINES3_AVAILABLE:
        if algorithm == "DQN":
            return DQN(
                "MlpPolicy",
                env,
                learning_rate=kwargs.get('learning_rate', 0.0005),
                buffer_size=kwargs.get('buffer_size', 10000),
                learning_starts=kwargs.get('learning_starts', 1000),
                target_update_interval=kwargs.get('target_update_interval', 50),
                verbose=1
            )
        elif algorithm == "PPO":
            return PPO(
                "MlpPolicy",
                env,
                learning_rate=kwargs.get('learning_rate', 0.0003),
                n_steps=kwargs.get('n_steps', 2048),
                batch_size=kwargs.get('batch_size', 64),
                verbose=1
            )
        elif algorithm == "A2C":
            return A2C(
                "MlpPolicy",
                env,
                learning_rate=kwargs.get('learning_rate', 0.0007),
                verbose=1
            )
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
    else:
        # 如果没有stable-baselines3，只能使用自定义DQN
        print("Warning: stable-baselines3 not available, using custom DQN")
        print("For better performance, install stable-baselines3: pip install stable-baselines3")
        return DQNAgent(state_dim=19, action_dim=3, device='cpu', **kwargs)


async def main():
    """主函数"""
    global training_agent, training_bridge, training_monitor, world, env
    
    import argparse
    
    parser = argparse.ArgumentParser(description='Gym-based RL Training')
    parser.add_argument('port', type=int, help='Server port')
    parser.add_argument('--algorithm', type=str, default='DQN',
                       choices=['DQN', 'PPO', 'A2C', 'CustomDQN'],
                       help='RL algorithm to use')
    parser.add_argument('--model-path', type=str, default=None,
                       help='Path to load existing model')
    parser.add_argument('--save-interval', type=int, default=10,
                       help='Save model every N episodes')
    parser.add_argument('--max-episodes', type=int, default=10000,
                       help='Maximum number of episodes to train (default: 10000)')
    parser.add_argument('--train-offline', action='store_true',
                       help='Train offline without game server')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Gymnasium-based RL Training")
    print("=" * 60)
    print(f"Algorithm: {args.algorithm}")
    print(f"Port: {args.port}")
    print(f"Max Episodes: {args.max_episodes}")
    print(f"Offline Training: {args.train_offline}")
    print("=" * 60)
    
    # 创建环境
    world = World(GameMap())
    env = CTFGymEnv(world=world, player_name="L0", max_steps=1000)
    
    # 创建智能体
    training_agent = create_training_agent(algorithm=args.algorithm)
    
    # 加载已有模型
    if args.model_path and os.path.exists(args.model_path):
        if hasattr(training_agent, 'load'):
            # stable-baselines3模型
            training_agent = training_agent.load(args.model_path, env=env)
            print(f"Loaded model from {args.model_path}")
        elif hasattr(training_agent, 'load_model'):
            # 自定义DQNAgent
            training_agent.load_model(args.model_path)
            print(f"Loaded model from {args.model_path}")
    
    # 创建训练监控器（日志保存到系统临时目录）
    os.makedirs("/tmp/ctf-ai", exist_ok=True)
    training_monitor = TrainingMonitor(log_dir="/tmp/ctf-ai")
    
    if args.train_offline:
        # 离线训练（不连接游戏服务器）
        print("\n[Offline Training] Starting offline training...")
        print("Note: This mode trains without game server interaction")
        print("For server-based training, remove --train-offline flag\n")
        
        # 使用stable-baselines3的训练循环
        if STABLE_BASELINES3_AVAILABLE and args.algorithm != "CustomDQN":
            # 创建评估回调（日志保存到系统临时目录）
            os.makedirs("/tmp/ctf-ai/gym_eval", exist_ok=True)
            eval_callback = EvalCallback(
                env,
                best_model_save_path="lib/models/gym_best/",
                log_path="/tmp/ctf-ai/gym_eval/",
                eval_freq=1000,
                deterministic=True,
                render=False
            )
            
            # 创建检查点回调
            checkpoint_callback = CheckpointCallback(
                save_freq=10000,
                save_path="lib/models/gym_checkpoints/",
                name_prefix="gym_model"
            )
            
            # 训练
            training_agent.learn(
                total_timesteps=100000,
                callback=[eval_callback, checkpoint_callback],
                log_interval=10
            )
            
            # 保存最终模型
            final_path = "lib/models/gym_model_final.zip"
            training_agent.save(final_path)
            print(f"\n[Offline Training] Final model saved to {final_path}")
        else:
            # 使用自定义训练循环
            print("Using custom training loop...")
            
            # 创建模拟初始化数据（用于离线训练）
            def create_mock_init_data():
                """创建模拟的游戏初始化数据（旗帜在己方半场随机摆放）"""
                import random
                
                map_width = 20
                map_height = 20
                num_players = 3  # 每队3个玩家
                num_flags = 9  # 每队9面旗帜（与前后端默认配置保持一致）
                
                # 计算中间线（与前端保持一致：middle_line = width / 2.0）
                # L队领地：x < middle_line
                # R队领地：x >= middle_line
                import math
                middle_line = map_width / 2.0
                l_max_x = int(middle_line - 0.1)  # L队最大x坐标（确保 < middle_line）
                r_min_x = math.ceil(middle_line)  # R队最小x坐标（确保 >= middle_line）
                
                # 生成L队旗帜位置（在左半场随机）
                l_flags = []
                for i in range(num_flags):
                    # 随机生成位置，确保在左半场
                    x = random.randint(2, l_max_x)
                    y = random.randint(1, map_height - 3)
                    l_flags.append({"posX": x, "posY": y, "canPickup": False, "pickedUp": False})
                
                # 生成R队旗帜位置（在右半场随机）
                r_flags = []
                for i in range(num_flags):
                    # 随机生成位置，确保在右半场
                    x = random.randint(r_min_x, map_width - 2)
                    y = random.randint(1, map_height - 3)
                    r_flags.append({"posX": x, "posY": y, "canPickup": True, "pickedUp": False})
                
                return {
                    "myteamName": "L",
                    "map": {
                        "width": map_width,
                        "height": map_height,
                        "walls": [
                            {"x": 5, "y": 5}, {"x": 5, "y": 6}, {"x": 6, "y": 5},
                            {"x": 15, "y": 15}, {"x": 15, "y": 14}, {"x": 14, "y": 15}
                        ]
                    },
                    "myteamTarget": [
                        {"x": 0, "y": 0}, {"x": 0, "y": 1}, {"x": 1, "y": 0}, {"x": 1, "y": 1}
                    ],
                    "opponentTarget": [
                        {"x": 18, "y": 18}, {"x": 18, "y": 19}, {"x": 19, "y": 18}, {"x": 19, "y": 19}
                    ],
                    "myteamPrison": [
                        {"x": 18, "y": 0}, {"x": 18, "y": 1}, {"x": 19, "y": 0}, {"x": 19, "y": 1}
                    ],
                    "opponentPrison": [
                        {"x": 0, "y": 18}, {"x": 0, "y": 19}, {"x": 1, "y": 18}, {"x": 1, "y": 19}
                    ],
                    "myteamPlayer": [
                        {"name": f"L{i}", "posX": 2, "posY": 2 + i, "hasFlag": False, "inPrison": False}
                        for i in range(num_players)
                    ],
                    "opponentPlayer": [
                        {"name": f"R{i}", "posX": 17, "posY": 17 - i, "hasFlag": False, "inPrison": False}
                        for i in range(num_players)
                    ],
                    "myteamFlag": l_flags,
                    "opponentFlag": r_flags,
                    "team": {
                        "name": "L",
                        "numPlayers": num_players,
                        "numFlags": num_flags
                    }
                }
            
            for episode in range(args.max_episodes):
                # 为每个episode提供初始化数据
                init_data = create_mock_init_data()
                obs, info = env.reset(options={'init_data': init_data})
                episode_reward = 0
                episode_length = 0
                
                for step in range(1000):
                    # 保存当前状态（用于存储到 replay buffer）
                    prev_obs = obs.copy() if isinstance(obs, np.ndarray) else obs
                    
                    # 选择动作
                    if hasattr(training_agent, 'predict'):
                        action, _ = training_agent.predict(obs, deterministic=False)
                    else:
                        action = training_agent.select_action(obs, training=True)
                    
                    # 执行动作
                    next_obs, reward, terminated, truncated, info = env.step(int(action))
                    
                    episode_reward += reward
                    episode_length += 1
                    
                    # 存储经验到 replay buffer（如果是自定义DQN）
                    if hasattr(training_agent, 'replay_buffer'):
                        done = terminated or truncated
                        training_agent.replay_buffer.push(prev_obs, action, reward, next_obs, done)
                    
                    # 训练（如果是自定义DQN）
                    loss = None
                    if hasattr(training_agent, 'train_step'):
                        loss = training_agent.train_step(batch_size=32)
                    
                    # 记录每一步（更新 episode_reward 和 episode_length）
                    # 注意：training_monitor.log_step() 会累积 reward 和 length
                    training_monitor.log_step(reward, loss)
                    
                    # 更新观察
                    obs = next_obs
                    
                    if terminated or truncated:
                        break
                
                # 更新 epsilon（每个 episode 结束后）
                if hasattr(training_agent, 'update_epsilon'):
                    training_agent.update_epsilon()
                
                # 记录episode（使用 training_monitor 内部累积的值）
                training_monitor.log_episode(episode, 
                                          training_agent.epsilon if hasattr(training_agent, 'epsilon') else 0.0)
                
                if episode % 10 == 0:
                    training_monitor.print_statistics(episode)
                    # 定期保存统计信息（用于监控工具读取）
                    training_monitor.save_statistics("training_stats.json")
                    training_monitor.save_csv("training_log.csv")
                
                if episode % args.save_interval == 0:
                    if hasattr(training_agent, 'save'):
                        training_agent.save(f"lib/models/gym_model_ep{episode}.zip")
                    elif hasattr(training_agent, 'save_model'):
                        training_agent.save_model(f"lib/models/gym_model_ep{episode}.pth")
            
            # 训练结束后保存最终统计
            training_monitor.save_statistics("training_stats.json")
            training_monitor.save_csv("training_log.csv")
            print("\n[Offline Training] Training completed!")
            print(f"[Offline Training] Statistics saved to /tmp/ctf-ai/training_stats.json")
    else:
        # 在线训练（连接游戏服务器）
        print("\n[Online Training] Starting online training with game server...")
        print("Connecting to game server on port", args.port)
        
        # 创建桥接
        training_bridge = GymServerBridge(env, training_agent, world)
        
        # 创建服务器回调
        start_fn, plan_fn, end_fn = create_gym_server_callbacks(training_bridge)
        
        # 启动服务器
        try:
            await run_game_server(args.port, start_fn, plan_fn, end_fn)
        except KeyboardInterrupt:
            print("\n[Training] Training interrupted by user")
            
            # 保存模型
            if training_agent is not None:
                model_dir = "lib/models"
                os.makedirs(model_dir, exist_ok=True)
                
                if hasattr(training_agent, 'save'):
                    final_path = os.path.join(model_dir, "gym_model_final.zip")
                    training_agent.save(final_path)
                elif hasattr(training_agent, 'save_model'):
                    final_path = os.path.join(model_dir, "gym_model_final.pth")
                    training_agent.save_model(final_path)
                
                print(f"[Training] Final model saved to {final_path}")
            
            # 保存统计
            if training_monitor:
                training_monitor.save_statistics("gym_training_stats.json")
                training_monitor.save_csv("gym_training_log.csv")
        except Exception as e:
            print(f"[Training] Server Stopped: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
