"""
Gymnasium环境使用示例
演示如何使用Gymnasium接口训练CTF游戏
"""

import sys
import os

# 添加路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SCRIPT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

# 要求必须安装gymnasium
from gym_env import CTFGymEnv, CTFMultiAgentGymEnv
from game_engine import World, GameMap


def example_basic_usage():
    """基础使用示例"""
    print("=" * 60)
    print("基础Gymnasium环境使用示例")
    print("=" * 60)
    
    # 创建环境
    world = World(GameMap())
    env = CTFGymEnv(world=world, player_name="L0", max_steps=100)
    
    # 重置环境
    obs, info = env.reset()
    print(f"初始观察形状: {obs.shape}")
    print(f"动作空间: {env.action_space}")
    print(f"观察空间: {env.observation_space}")
    
    # 运行几个步骤
    total_reward = 0
    for step in range(10):
        action = env.action_space.sample()  # 随机动作
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        
        print(f"Step {step}: action={action}, reward={reward:.2f}, "
              f"terminated={terminated}, truncated={truncated}")
        
        if terminated or truncated:
            print("Episode结束")
            obs, info = env.reset()
            break
    
    print(f"总奖励: {total_reward:.2f}")
    env.close()


def example_with_dqn():
    """使用DQN训练示例（需要stable-baselines3）"""
    try:
        from stable_baselines3 import DQN
        from stable_baselines3.common.evaluation import evaluate_policy
    except ImportError:
        print("stable-baselines3 not installed")
        print("Install with: pip install stable-baselines3")
        return
    
    print("=" * 60)
    print("使用stable-baselines3 DQN训练示例")
    print("=" * 60)
    
    # 创建环境
    world = World(GameMap())
    env = CTFGymEnv(world=world, player_name="L0", max_steps=200)
    
    # 创建DQN模型
    model = DQN(
        "MlpPolicy",
        env,
        learning_rate=0.0005,
        buffer_size=10000,
        learning_starts=1000,
        target_update_interval=50,
        verbose=1
    )
    
    # 训练（这里只训练少量步数作为示例）
    print("开始训练...")
    model.learn(total_timesteps=5000)
    
    # 评估
    print("评估模型...")
    mean_reward, std_reward = evaluate_policy(model, env, n_eval_episodes=10)
    print(f"平均奖励: {mean_reward:.2f} +/- {std_reward:.2f}")
    
    env.close()


def example_multi_agent():
    """多智能体环境示例"""
    print("=" * 60)
    print("多智能体环境示例")
    print("=" * 60)
    
    world = World(GameMap())
    env = CTFMultiAgentGymEnv(
        world=world,
        player_names=["L0", "L1"],
        max_steps=100
    )
    
    # 重置环境
    obs, info = env.reset()
    print(f"观察空间: {list(obs.keys())}")
    print(f"动作空间: {list(env.action_space.keys())}")
    
    # 运行几个步骤
    for step in range(10):
        # 为每个玩家选择动作
        actions = {
            name: env.action_space[name].sample()
            for name in env.player_names
        }
        
        obs, rewards, terminated, truncated, infos = env.step(actions)
        
        print(f"Step {step}:")
        for name in env.player_names:
            print(f"  {name}: action={actions[name]}, reward={rewards[name]:.2f}")
        
        if all(terminated.values()) or all(truncated.values()):
            print("Episode结束")
            break
    
    env.close()


if __name__ == "__main__":
    print("CTF Gymnasium环境使用示例")
    print("\n1. 基础使用示例")
    example_basic_usage()
    
    print("\n2. 多智能体示例")
    example_multi_agent()
    
    print("\n3. 使用stable-baselines3训练（需要安装stable-baselines3）")
    # example_with_dqn()  # 取消注释以运行
