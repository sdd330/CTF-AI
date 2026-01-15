"""
Gymnasium环境与游戏服务器的桥接
"""

from typing import Dict, Optional
import random

from ..game_engine import World
from ..data_models import Team, Strategy, Direction
from .gym_env import CTFGymEnv


class GymServerBridge:
    """Gymnasium环境与游戏服务器的桥接类"""

    def __init__(self, env: CTFGymEnv, agent, world: Optional[World] = None):
        self.env = env
        self.agent = agent
        self.world = world or env.world
        self.current_obs, self.prev_obs, self.current_info = None, None, None
        self.episode_reward, self.episode_step, self._last_action = 0.0, 0, 0
        self.stats = {'episode': 0, 'total_reward': 0.0, 'episode_rewards': [], 'episode_lengths': []}

    def start_game(self, req: Dict) -> None:
        """游戏开始时调用"""
        if "map" not in req:
            return
        try:
            self.world.init(req)
        except Exception as e:
            print(f"[Gym Training] world.init() failed: {e}")
            return

        my_players = [p for p in self.world.my_players.values() if not p.is_in_prison]
        if my_players:
            try:
                self.current_obs, self.current_info = self.env.reset(options={'init_data': req})
                self.prev_obs = None
            except ValueError:
                self.current_obs, self.current_info, self.prev_obs = None, None, None
        else:
            self.current_obs, self.current_info, self.prev_obs = None, None, None

        self.episode_reward, self.episode_step = 0.0, 0
        print(f"[Gym Training] Episode {self.stats['episode'] + 1} started")

    def plan_next_actions(self, req: Dict) -> Dict:
        """计划下一步动作"""
        my_team = Team.LEFT if self.world.my_team_name == "L" else Team.RIGHT
        prev_score = self.world.left_team_score if my_team == Team.LEFT else self.world.right_team_score

        if not self.world.update(req):
            return {"actions": {}, "paths": {}, "timings": {}}
        self.env.update_world_state(req)

        current_score = self.world.left_team_score if my_team == Team.LEFT else self.world.right_team_score
        if current_score > prev_score and hasattr(self.env, 'prev_state_dict') and self.env.prev_state_dict:
            self.env.prev_state_dict['team_score'] = prev_score

        my_players = [p for p in self.world.my_players.values() if not p.is_in_prison]
        if not my_players:
            return {"actions": {}, "paths": {}, "timings": {}}

        if self.current_obs is None:
            self._try_init_observation(req, my_players)
            if self.current_obs is None:
                return {"actions": {}, "paths": {}, "timings": {}}

        self.world._current_paths.clear()
        actions = {}

        for player in my_players:
            if player.is_in_prison:
                continue
            actions[player.name] = self._plan_player_action(player)

        self.episode_step += 1
        return self.world._info_collector.build_result_from_actions(actions)

    def _try_init_observation(self, req: Dict, my_players):
        """尝试初始化观察"""
        if 'map' not in req:
            try:
                from .state_extractor import extract_state_features
                if my_players:
                    self.current_obs = extract_state_features(my_players[0], self.world)
                    self.prev_obs = None
            except Exception:
                pass
        else:
            try:
                self.current_obs, self.current_info = self.env.reset(options={'init_data': req})
                self.prev_obs = None
            except Exception:
                pass

    def _plan_player_action(self, player) -> str:
        """为单个玩家规划动作"""
        if self.env.player_name == player.name:
            return self._plan_main_player_action(player)
        return self._plan_other_player_action(player)

    def _plan_main_player_action(self, player) -> str:
        """为主玩家规划动作"""
        if self.current_obs is None:
            from .state_extractor import extract_state_features
            self.current_obs = extract_state_features(player, self.world)
            self.prev_obs = None

        if self.prev_obs is not None and self.current_obs is not None:
            obs, reward, terminated, truncated, _ = self.env.step(self._last_action)
            self.episode_reward += reward
            if hasattr(self.agent, 'replay_buffer'):
                self.agent.replay_buffer.push(self.prev_obs, self._last_action, reward, obs, terminated or truncated)
            self.prev_obs, self.current_obs = self.current_obs, obs

        action = self._select_action_from_gym()
        self._last_action = action

        try:
            strategy = Strategy(action)
        except (ValueError, TypeError):
            strategy = Strategy.SCORING

        direction = player.plan(suggested_strategy=strategy) or player.plan()
        if direction:
            return direction.value
        return random.choice([Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]).value

    def _plan_other_player_action(self, player) -> str:
        """为其他玩家规划动作"""
        direction = None
        if hasattr(self.agent, 'predict_schedule'):
            try:
                schedule = self.agent.predict_schedule([player], self.world, training=True)
                schedule_key = f"{player.name}schedule"
                if schedule_key in schedule:
                    strategy, _, _ = schedule[schedule_key]
                    direction = player.plan(suggested_strategy=strategy)
            except Exception:
                pass

        if not direction:
            direction = player.plan()
        if direction:
            return direction.value
        return random.choice([Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]).value

    def _select_action_from_gym(self) -> int:
        """从Gymnasium环境选择动作"""
        if self.current_obs is None:
            return self.env.action_space.sample() if hasattr(self.env, 'action_space') else 0
        try:
            if hasattr(self.agent, 'predict'):
                action, _ = self.agent.predict(self.current_obs, deterministic=False)
                return int(action)
            elif hasattr(self.agent, 'select_action'):
                return self.agent.select_action(self.current_obs, training=True)
        except Exception:
            pass
        return self.env.action_space.sample() if hasattr(self.env, 'action_space') else 0

    def game_over(self, req: Dict) -> None:
        """游戏结束时调用"""
        self.stats['episode'] += 1
        self.stats['episode_rewards'].append(self.episode_reward)
        self.stats['episode_lengths'].append(self.episode_step)

        avg_reward = sum(self.stats['episode_rewards'][-10:]) / min(10, len(self.stats['episode_rewards']))
        print(f"[Gym Training] Episode {self.stats['episode']} finished - Reward: {self.episode_reward:.2f}, Avg(10): {avg_reward:.2f}")

        if hasattr(self.agent, 'train_step') and len(self.agent.replay_buffer) >= 32:
            self.agent.train_step(batch_size=32)
        if hasattr(self.agent, 'update_epsilon'):
            self.agent.update_epsilon()


def create_gym_server_callbacks(bridge: GymServerBridge):
    """创建游戏服务器回调函数"""
    return lambda req: bridge.start_game(req), lambda req: bridge.plan_next_actions(req), lambda req: bridge.game_over(req)
