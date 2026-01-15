"""
Gymnasium环境包装器
将CTF游戏环境包装成Gymnasium标准接口
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Dict, Optional, Tuple

from ..data_models import Position, Team, Strategy, Action
from ..game_engine import GameMap, World
from ..utils import can_pickup_flag, can_score_flag
from .state_extractor import extract_state_features
from .reward_calculator import calculate_reward


class CTFGymEnv(gym.Env):
    """CTF游戏的Gymnasium环境包装器（单智能体）"""

    metadata = {'render_modes': ['human', 'rgb_array', 'ansi'], 'render_fps': 10}

    def __init__(self, world: Optional[World] = None, player_name: Optional[str] = None,
                 max_steps: int = 1000, render_mode: Optional[str] = None):
        super().__init__()
        self.world = world or World(GameMap())
        self.player_name = player_name
        self.max_steps = max_steps
        self.render_mode = render_mode
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(19,), dtype=np.float32)
        self.action_space = spaces.Discrete(3)
        self.current_step = 0
        self.current_player = None
        self.prev_state_dict = None
        self.episode_reward = 0.0
        self._pending_state_update = None

    def reset(self, seed: Optional[int] = None, options: Optional[Dict] = None) -> Tuple[np.ndarray, Dict]:
        """重置环境"""
        super().reset(seed=seed)
        self.current_step = 0
        self.episode_reward = 0.0
        self.prev_state_dict = None

        if options and 'init_data' in options:
            init_data = options['init_data']
            if 'map' in init_data:
                self.world.init(init_data)
            else:
                self.world.update(init_data)
        elif self._pending_state_update:
            self.world.update(self._pending_state_update)
            self._pending_state_update = None

        self._setup_current_player()
        observation = extract_state_features(self.current_player, self.world)
        self.prev_state_dict = self._create_state_dict()
        return observation.astype(np.float32), {"player_name": self.player_name, "step": self.current_step}

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        """执行一步动作"""
        if self.current_player is None:
            raise RuntimeError("Environment not reset. Call reset() first.")

        if self._pending_state_update:
            self.world.update(self._pending_state_update)
            self._pending_state_update = None
            self.current_player = self.world.my_players.get(self.player_name) or self.world.enemy_players.get(self.player_name)
            if self.current_player is None:
                return np.zeros(19, dtype=np.float32), 0.0, True, False, {"error": "Player not found"}

        direction = self._gym_action_to_direction(action)
        if direction:
            self._execute_player_move(direction)
        self.current_step += 1

        self.current_player = self.world.players.get(self.player_name)
        if self.current_player is None:
            return np.zeros(19, dtype=np.float32), 0.0, True, False, {"error": "Player not found after move"}

        reward = calculate_reward(self.current_player, self.world, self.prev_state_dict, current_action=action)
        self.episode_reward += reward
        observation = extract_state_features(self.current_player, self.world)
        self.prev_state_dict = self._create_state_dict()

        return observation.astype(np.float32), reward, False, self.current_step >= self.max_steps, {
            "player_name": self.player_name, "step": self.current_step, "episode_reward": self.episode_reward,
            "action": action, "direction": direction, "has_flag": self.current_player.has_flag,
            "in_prison": self.current_player.is_in_prison
        }

    def update_world_state(self, state_update: Dict):
        """更新世界状态"""
        self._pending_state_update = state_update

    def render(self):
        """渲染环境"""
        if self.render_mode == 'human' and self.current_player:
            print(f"Step: {self.current_step}, Player: {self.player_name}, Reward: {self.episode_reward:.2f}")
        elif self.render_mode == 'ansi':
            return self._render_text()
        elif self.render_mode == 'rgb_array':
            return np.zeros((100, 100, 3), dtype=np.uint8)

    def close(self):
        pass

    def _setup_current_player(self):
        """设置当前玩家"""
        if self.player_name:
            self.current_player = self.world.my_players.get(self.player_name) or self.world.enemy_players.get(self.player_name)
        else:
            my_players = [p for p in self.world.my_players.values() if not p.is_in_prison]
            if my_players:
                self.current_player = my_players[0]
                self.player_name = self.current_player.name
            else:
                raise ValueError("No available players found")
        if self.current_player is None:
            raise ValueError(f"Player {self.player_name} not found")

    def _create_state_dict(self) -> Dict:
        """创建状态字典"""
        my_team = Team.LEFT if self.world.my_team_name == "L" else Team.RIGHT
        return {
            "hasFlag": self.current_player.has_flag, "inPrison": self.current_player.is_in_prison,
            "posX": self.current_player.position.x, "posY": self.current_player.position.y,
            "team_score": self.world.left_team_score if my_team == Team.LEFT else self.world.right_team_score
        }

    def _gym_action_to_direction(self, gym_action: int) -> Optional[str]:
        """将Gymnasium动作转换为游戏方向"""
        if self.current_player is None:
            return None
        my_team = Team.LEFT if self.world.my_team_name == "L" else Team.RIGHT
        opponent_team = my_team.get_enemy()

        if gym_action == Strategy.DEFENCE.value:
            opponents = [p for p in self.world.enemy_players.values() if not p.is_in_prison]
            if opponents:
                best = min(opponents, key=lambda o: self.current_player.position.manhattan_distance(o.position))
                path = self.world.find_path_to(self.current_player.position, best.position, player_name=self.current_player.name)
                if len(path) > 1:
                    return self.current_player.position.direction_to(path[1]).value

        elif gym_action == Strategy.SCORING.value:
            if self.current_player.has_flag:
                targets = list(self.world.map.get_team_target_positions(my_team))
                if targets:
                    path = self.world.find_path_to(self.current_player.position, targets[0], player_name=self.current_player.name)
                    if len(path) > 1:
                        return self.current_player.position.direction_to(path[1]).value
            else:
                flags = [f for f in self.world.enemy_flags.values() if f.can_pickup]
                if flags:
                    best = min(flags, key=lambda f: self.current_player.position.manhattan_distance(f.position))
                    path = self.world.find_path_to(self.current_player.position, best.position, player_name=self.current_player.name)
                    if len(path) > 1:
                        return self.current_player.position.direction_to(path[1]).value

        elif gym_action == Strategy.SAVING.value:
            in_prison = [p for p in self.world.my_players.values() if p.is_in_prison]
            if in_prison:
                prisons = list(self.world.map.get_team_prison_positions(opponent_team))
                if prisons:
                    path = self.world.find_path_to(self.current_player.position, prisons[0], player_name=self.current_player.name)
                    if len(path) > 1:
                        return self.current_player.position.direction_to(path[1]).value
        return None

    def _execute_player_move(self, direction: str):
        """执行玩家移动"""
        if self.current_player is None or direction is None:
            return
        dx, dy = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}.get(direction, (0, 0))
        new_pos = Position(self.current_player.position.x + dx, self.current_player.position.y + dy)

        if not self.world.map.is_valid_position(new_pos) or self.world.map.is_wall(new_pos):
            return
        self.current_player.position = new_pos

        my_team = Team.LEFT if self.world.my_team_name == "L" else Team.RIGHT
        for flag in [f for f in self.world.enemy_flags.values() if f.can_pickup]:
            if flag.position == new_pos and not self.current_player.has_flag and can_pickup_flag(self.current_player, flag):
                self.current_player.action(Action.PICKUP_FLAG, flag=flag)
                break

        if self.current_player.has_flag and self.current_player.is_in_base() and can_score_flag(self.current_player):
            self.current_player.action(Action.SCORE_FLAG)
            for flag in list(self.world.my_flags.values()) + list(self.world.enemy_flags.values()):
                if flag.team == my_team.get_enemy() and flag.is_picked_up:
                    flag.drop_at(flag.original_position)
                    break

    def _render_text(self) -> str:
        if not self.current_player:
            return "Environment not initialized"
        return (f"CTF Gym Environment\nPlayer: {self.player_name}\nStep: {self.current_step}/{self.max_steps}\n"
                f"Reward: {self.episode_reward:.2f}\nPosition: ({self.current_player.position.x}, {self.current_player.position.y})\n"
                f"Has Flag: {self.current_player.has_flag}\nIn Prison: {self.current_player.is_in_prison}")
