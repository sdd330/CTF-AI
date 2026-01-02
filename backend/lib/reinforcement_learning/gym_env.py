"""
Gymnasium环境包装器
将CTF游戏环境包装成Gymnasium标准接口，便于使用标准RL算法和工具

注意：必须安装gymnasium: pip install gymnasium
"""

# 要求必须安装gymnasium
import gymnasium as gym
from gymnasium import spaces

import numpy as np
from typing import Dict, Optional, Tuple, Any
import sys
import os

# 添加路径以便导入游戏模块
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SCRIPT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

from ..data_models import Position, Team, Strategy, Action
from ..game_engine import GameMap, World
from ..utils import list_players, list_flags, can_pickup_flag, can_score_flag
from .state_extractor import extract_state_features
from .reward_calculator import calculate_reward


class CTFGymEnv(gym.Env):
    """
    CTF游戏的Gymnasium环境包装器
    
    这个环境将CTF游戏包装成标准的Gymnasium接口，使得：
    1. 可以使用标准的RL算法（如stable-baselines3）
    2. 可以与其他Gymnasium环境进行比较
    3. 可以使用Gymnasium的监控和评估工具
    4. 可以更容易地集成其他RL库
    """
    
    metadata = {
        'render_modes': ['human', 'rgb_array', 'ansi'],
        'render_fps': 10
    }
    
    def __init__(
        self,
        world: Optional[World] = None,
        player_name: Optional[str] = None,
        max_steps: int = 1000,
        render_mode: Optional[str] = None
    ):
        """
        初始化CTF Gymnasium环境
        
        Args:
            world: World对象（如果为None，会创建新的）
            player_name: 要控制的玩家名称（如果为None，会使用第一个玩家）
            max_steps: 最大步数（episode长度限制）
            render_mode: 渲染模式
        """
        super().__init__()
        
        self.world = world or World(GameMap())
        self.player_name = player_name
        self.max_steps = max_steps
        self.render_mode = render_mode
        
        # 状态空间：19维特征向量
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(19,),
            dtype=np.float32
        )
        
        # 动作空间：3个离散动作（defence, scoring, saving）
        self.action_space = spaces.Discrete(3)
        
        # 内部状态
        self.current_step = 0
        self.current_player = None
        self.prev_state_dict = None
        self.episode_reward = 0.0
        
        # 用于存储游戏状态更新
        self._pending_state_update = None
    
    def reset(
        self,
        seed: Optional[int] = None,
        options: Optional[Dict] = None
    ) -> Tuple[np.ndarray, Dict]:
        """
        重置环境
        
        Args:
            seed: 随机种子
            options: 可选参数（可以包含游戏初始化数据）
        
        Returns:
            observation: 初始观察
            info: 信息字典
        """
        super().reset(seed=seed)
        
        self.current_step = 0
        self.episode_reward = 0.0
        self.prev_state_dict = None
        
        # 如果提供了初始化数据，使用它
        if options and 'init_data' in options:
            init_data = options['init_data']
            # 检查是否包含map字段（init请求的特征）
            if 'map' in init_data:
                self.world.init(init_data)
            else:
                # 如果没有map字段，说明是status请求，只更新状态
                self.world.update(init_data)
        elif self._pending_state_update:
            # 使用待处理的状态更新
            self.world.update(self._pending_state_update)
            self._pending_state_update = None
        
        # 确定要控制的玩家
        if self.player_name:
            self.current_player = self.world.players.get(self.player_name)
        else:
            # 使用第一个可用玩家
            my_team = Team.LEFT if self.world.my_team_name == "L" else Team.RIGHT
            my_players = list_players(self.world.players, my_team, in_prison=False, has_flag=None)
            if my_players:
                self.current_player = my_players[0]
                self.player_name = self.current_player.name
            else:
                raise ValueError("No available players found")
        
        if self.current_player is None:
            raise ValueError(f"Player {self.player_name} not found")
        
        # 提取初始观察
        observation = extract_state_features(self.current_player, self.world)
        
        # 保存初始状态
        self.prev_state_dict = {
            "hasFlag": self.current_player.has_flag,
            "inPrison": self.current_player.is_in_prison,
            "posX": self.current_player.position.x,
            "posY": self.current_player.position.y
        }
        
        info = {
            "player_name": self.player_name,
            "step": self.current_step
        }
        
        return observation.astype(np.float32), info
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        """
        执行一步动作
        
        Args:
            action: 动作（Strategy.DEFENCE.value/SCORING.value/SAVING.value）
        
        Returns:
            observation: 新的观察
            reward: 奖励
            terminated: 是否终止（游戏结束）
            truncated: 是否截断（达到最大步数）
            info: 信息字典
        """
        if self.current_player is None:
            raise RuntimeError("Environment not reset. Call reset() first.")
        
        # 更新状态（如果有待处理的状态更新）
        # 在游戏服务器模式下，状态更新在step之前完成
        if self._pending_state_update:
            self.world.update(self._pending_state_update)
            self._pending_state_update = None
            # 重新获取玩家对象（状态可能已更新）
            self.current_player = self.world.players.get(self.player_name)
            if self.current_player is None:
                # 如果玩家不存在，返回终止状态
                observation = np.zeros(19, dtype=np.float32)
                return observation, 0.0, True, False, {"error": "Player not found"}
        
        # 保存执行动作前的状态（包含分数信息）
        my_team = Team.LEFT if self.world.my_team_name == "L" else Team.RIGHT
        prev_score = self.world.left_team_score if my_team == Team.LEFT else self.world.right_team_score
        
        prev_state = {
            "hasFlag": self.current_player.has_flag,
            "inPrison": self.current_player.is_in_prison,
            "posX": self.current_player.position.x,
            "posY": self.current_player.position.y,
            "team_score": prev_score  # 保存当前分数，用于检测得分
        }
        
        # 执行动作：将Gym动作转换为游戏方向并移动玩家
        direction = self._gym_action_to_direction(action)
        if direction:
            self._execute_player_move(direction)
        
        # 更新步数
        self.current_step += 1
        
        # 重新获取玩家对象（位置可能已更新）
        self.current_player = self.world.players.get(self.player_name)
        if self.current_player is None:
            observation = np.zeros(19, dtype=np.float32)
            return observation, 0.0, True, False, {"error": "Player not found after move"}
        
        # 计算奖励（基于状态变化）
        reward = calculate_reward(
            self.current_player,
            self.world,
            self.prev_state_dict,
            current_action=action
        )
        self.episode_reward += reward
        
        # 检查终止条件
        terminated = False
        truncated = False
        
        # 检查是否达到最大步数
        if self.current_step >= self.max_steps:
            truncated = True
        
        # 检查游戏是否结束（可以通过检查分数来判断）
        # 这里简化处理，实际应该检查world的游戏状态
        
        # 提取新观察
        observation = extract_state_features(self.current_player, self.world)
        
        # 更新prev_state_dict（包含分数信息用于奖励计算）
        my_team = Team.LEFT if self.world.my_team_name == "L" else Team.RIGHT
        current_score = self.world.left_team_score if my_team == Team.LEFT else self.world.right_team_score
        
        self.prev_state_dict = {
            "hasFlag": self.current_player.has_flag,
            "inPrison": self.current_player.is_in_prison,
            "posX": self.current_player.position.x,
            "posY": self.current_player.position.y,
            "team_score": current_score  # 保存当前分数，用于下一帧检测得分
        }
        
        info = {
            "player_name": self.player_name,
            "step": self.current_step,
            "episode_reward": self.episode_reward,
            "action": action,
            "direction": direction,
            "has_flag": self.current_player.has_flag,
            "in_prison": self.current_player.is_in_prison
        }
        
        return observation.astype(np.float32), reward, terminated, truncated, info
    
    def _gym_action_to_direction(self, gym_action: int) -> Optional[str]:
        """
        将Gymnasium动作转换为游戏方向
        
        Args:
            gym_action: Gymnasium动作（Strategy.DEFENCE.value/SCORING.value/SAVING.value）
        
        Returns:
            游戏方向字符串（"up", "down", "left", "right"）或None
        """
        if self.current_player is None:
            return None
        
        my_team = Team.LEFT if self.world.my_team_name == "L" else Team.RIGHT
        opponent_team = Team.RIGHT if my_team == Team.LEFT else Team.LEFT
        
        if gym_action == Strategy.DEFENCE.value:  # defence
            # 找到最近的敌人
            opponents = list_players(self.world.players, opponent_team, in_prison=False, has_flag=None)
            if opponents:
                best_opponent = None
                min_dist = float('inf')
                for opp in opponents:
                    dist = self.current_player.position.manhattan_distance(opp.position)
                    if dist < min_dist:
                        min_dist = dist
                        best_opponent = opp
                
                if best_opponent:
                    path = self.world.find_path_to(self.current_player.position, best_opponent.position, player_name=self.current_player.name)
                    if len(path) > 1:
                        return self.current_player.position.direction_to(path[1]).value
        
        elif gym_action == Strategy.SCORING.value:  # scoring
            if self.current_player.has_flag:
                # 返回目标区域
                my_targets = self.world.get_team_target_positions(my_team)
                if my_targets:
                    path = self.world.find_path_to(self.current_player.position, my_targets[0], player_name=self.current_player.name)
                    if len(path) > 1:
                        return self.current_player.position.direction_to(path[1]).value
            else:
                # 找最近的敌方flag
                enemy_flags = list_flags(self.world.flags, my_team, is_enemy=True, can_pickup=True)
                if enemy_flags:
                    best_flag = None
                    min_dist = float('inf')
                    for flag in enemy_flags:
                        dist = self.current_player.position.manhattan_distance(flag.position)
                        if dist < min_dist:
                            min_dist = dist
                            best_flag = flag
                    
                    if best_flag:
                        path = self.world.find_path_to(self.current_player.position, best_flag.position, player_name=self.current_player.name)
                        if len(path) > 1:
                            return self.current_player.position.direction_to(path[1]).value
        
        elif gym_action == Strategy.SAVING.value:  # saving
            # 营救队友
            my_players_in_prison = list_players(self.world.players, my_team, in_prison=True, has_flag=None)
            if my_players_in_prison:
                prison_positions = self.world.get_team_prison_positions(opponent_team)
                if prison_positions:
                    path = self.world.find_path_to(self.current_player.position, prison_positions[0], player_name=self.current_player.name)
                    if len(path) > 1:
                        return self.current_player.position.direction_to(path[1]).value
        
        return None
    
    def _execute_player_move(self, direction: str) -> None:
        """
        执行玩家移动
        
        Args:
            direction: 移动方向（"up", "down", "left", "right"）
        """
        if self.current_player is None or direction is None:
            return
        
        # 计算新位置
        dx, dy = 0, 0
        if direction == "up":
            dy = -1
        elif direction == "down":
            dy = 1
        elif direction == "left":
            dx = -1
        elif direction == "right":
            dx = 1
        
        new_pos = Position(self.current_player.position.x + dx, self.current_player.position.y + dy)
        
        # 检查新位置是否有效
        if not self.world.is_valid_position(new_pos):
            return
        
        if self.world.is_wall(new_pos):
            return
        
        # 移动玩家
        self.current_player.position = new_pos
        
        # 检查是否拾取旗帜
        my_team = Team.LEFT if self.world.my_team_name == "L" else Team.RIGHT
        enemy_flags = list_flags(self.world.flags, my_team, is_enemy=True, can_pickup=True)
        for flag in enemy_flags:
            if flag.position == new_pos and not self.current_player.has_flag:
                # 使用 action 方法拾取旗帜
                if can_pickup_flag(self.current_player, flag):
                    self.current_player.action(Action.PICKUP_FLAG, flag=flag)
                break
        
        # 检查是否得分（在目标区域且有旗帜）
        if self.current_player.has_flag and self.current_player.is_in_base():
            # 使用 action 方法得分
            if can_score_flag(self.current_player):
                self.current_player.action(Action.SCORE_FLAG)
            # 重置旗帜位置（简化处理）
            for flag in self.world.flags.values():
                if flag.team == my_team.get_enemy() and flag.is_picked_up:
                    flag.drop_at(flag.original_position)
                    # 将旗帜放回初始位置（简化处理）
                    break
    
    def update_world_state(self, state_update: Dict):
        """
        更新世界状态（用于与游戏服务器同步）
        
        Args:
            state_update: 游戏状态更新字典
        """
        self._pending_state_update = state_update
    
    def render(self):
        """渲染环境（可选实现）"""
        if self.render_mode == 'human':
            # 简单的文本渲染
            if self.current_player:
                print(f"Step: {self.current_step}, Player: {self.player_name}, "
                      f"Reward: {self.episode_reward:.2f}")
        elif self.render_mode == 'ansi':
            # ANSI文本渲染
            return self._render_text()
        elif self.render_mode == 'rgb_array':
            # RGB数组渲染（用于视频录制）
            return self._render_rgb_array()
    
    def _render_text(self) -> str:
        """文本渲染"""
        if not self.current_player:
            return "Environment not initialized"
        
        lines = [
            f"CTF Gym Environment",
            f"Player: {self.player_name}",
            f"Step: {self.current_step}/{self.max_steps}",
            f"Reward: {self.episode_reward:.2f}",
            f"Position: ({self.current_player.position.x}, {self.current_player.position.y})",
            f"Has Flag: {self.current_player.has_flag}",
            f"In Prison: {self.current_player.is_in_prison}"
        ]
        return "\n".join(lines)
    
    def _render_rgb_array(self) -> np.ndarray:
        """RGB数组渲染（占位符）"""
        # 这里可以实现实际的图像渲染
        # 返回一个numpy数组，形状为(height, width, 3)
        return np.zeros((100, 100, 3), dtype=np.uint8)
    
    def close(self):
        """关闭环境"""
        pass


class CTFMultiAgentGymEnv(gym.Env):
    """
    CTF游戏的多智能体Gymnasium环境
    
    这个环境支持多个玩家同时训练，每个玩家有自己的观察和动作空间
    完全符合Gymnasium标准接口
    """
    
    def __init__(
        self,
        world: Optional[World] = None,
        player_names: Optional[list] = None,
        max_steps: int = 1000,
        render_mode: Optional[str] = None
    ):
        """
        初始化多智能体环境
        
        Args:
            world: World对象
            player_names: 玩家名称列表
            max_steps: 最大步数
            render_mode: 渲染模式
        """
        super().__init__()
        
        self.world = world or World(GameMap())
        self.player_names = player_names or []
        self.max_steps = max_steps
        self.render_mode = render_mode
        
        # 多智能体观察空间（字典空间）
        self.observation_space = spaces.Dict({
            name: spaces.Box(low=-np.inf, high=np.inf, shape=(19,), dtype=np.float32)
            for name in self.player_names
        })
        
        # 多智能体动作空间（字典空间）
        self.action_space = spaces.Dict({
            name: spaces.Discrete(3)
            for name in self.player_names
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
        
        observations = {}
        info = {}
        
        for name in self.player_names:
            player = self.world.players.get(name)
            if player:
                self.players[name] = player
                observations[name] = extract_state_features(player, self.world).astype(np.float32)
                self.prev_states[name] = {
                    "hasFlag": player.has_flag,
                    "inPrison": player.is_in_prison,
                    "posX": player.position.x,
                    "posY": player.position.y
                }
                info[name] = {"step": self.current_step}
        
        return observations, info
    
    def step(self, actions: Dict[str, int]):
        """执行多智能体动作"""
        self.current_step += 1
        
        observations = {}
        rewards = {}
        terminated = {}
        truncated = {}
        infos = {}
        
        all_terminated = True
        all_truncated = True
        
        for name, action in actions.items():
            if name not in self.players:
                continue
            
            player = self.players[name]
            
            # 计算奖励
            reward = calculate_reward(
                player,
                self.world,
                self.prev_states.get(name),
                current_action=action
            )
            rewards[name] = reward
            self.episode_rewards[name] += reward
            
            # 提取观察
            observations[name] = extract_state_features(player, self.world).astype(np.float32)
            
            # 更新状态
            self.prev_states[name] = {
                "hasFlag": player.has_flag,
                "inPrison": player.is_in_prison,
                "posX": player.position.x,
                "posY": player.position.y
            }
            
            terminated[name] = False
            truncated[name] = (self.current_step >= self.max_steps)
            
            if not terminated[name]:
                all_terminated = False
            if not truncated[name]:
                all_truncated = False
            
            infos[name] = {
                "step": self.current_step,
                "episode_reward": self.episode_rewards[name],
                "action": action
            }
        
        return observations, rewards, terminated, truncated, infos
