"""
多智能体Gymnasium环境
支持多个玩家同时训练
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Dict, Optional

from ..game_engine import GameMap, World
from .state_extractor import extract_state_features
from .reward_calculator import calculate_reward


class CTFMultiAgentGymEnv(gym.Env):
    """CTF游戏的多智能体Gymnasium环境"""

    def __init__(
        self,
        world: Optional[World] = None,
        player_names: Optional[list] = None,
        max_steps: int = 1000,
        render_mode: Optional[str] = None
    ):
        super().__init__()
        self.world = world or World(GameMap())
        self.player_names = player_names or []
        self.max_steps = max_steps
        self.render_mode = render_mode

        self.observation_space = spaces.Dict({
            name: spaces.Box(low=-np.inf, high=np.inf, shape=(19,), dtype=np.float32)
            for name in self.player_names
        })
        self.action_space = spaces.Dict({
            name: spaces.Discrete(3) for name in self.player_names
        })

        self.current_step = 0
        self.players = {}
        self.prev_states = {}
        self.episode_rewards = {}

    def reset(self, seed=None, options=None):
        """重置多智能体环境"""
        super().reset(seed=seed)
        self.current_step = 0
        self.episode_rewards = {name: 0.0 for name in self.player_names}
        self.prev_states = {}

        if options and 'init_data' in options:
            self.world.init(options['init_data'])

        observations, info = {}, {}
        for name in self.player_names:
            player = self.world.my_players.get(name) or self.world.enemy_players.get(name)
            if player:
                self.players[name] = player
                observations[name] = extract_state_features(player, self.world).astype(np.float32)
                self.prev_states[name] = {
                    "hasFlag": player.has_flag, "inPrison": player.is_in_prison,
                    "posX": player.position.x, "posY": player.position.y
                }
                info[name] = {"step": self.current_step}
        return observations, info

    def step(self, actions: Dict[str, int]):
        """执行多智能体动作"""
        self.current_step += 1
        observations, rewards, terminated, truncated, infos = {}, {}, {}, {}, {}

        for name, action in actions.items():
            if name not in self.players:
                continue
            player = self.players[name]
            reward = calculate_reward(player, self.world, self.prev_states.get(name), current_action=action)
            rewards[name] = reward
            self.episode_rewards[name] += reward
            observations[name] = extract_state_features(player, self.world).astype(np.float32)
            self.prev_states[name] = {
                "hasFlag": player.has_flag, "inPrison": player.is_in_prison,
                "posX": player.position.x, "posY": player.position.y
            }
            terminated[name] = False
            truncated[name] = self.current_step >= self.max_steps
            infos[name] = {"step": self.current_step, "episode_reward": self.episode_rewards[name], "action": action}

        return observations, rewards, terminated, truncated, infos
