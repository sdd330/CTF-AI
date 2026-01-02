"""
Gymnasium环境与游戏服务器的桥接
将Gymnasium环境与WebSocket游戏服务器连接，实现实时训练

完全基于Gymnasium标准接口，支持stable-baselines3和自定义DQN智能体。
"""

from typing import Dict, Optional, Any

from ..game_engine import World
from ..data_models import Team, Position, Strategy
from ..utils import list_players, list_flags
from .gym_env import CTFGymEnv


class GymServerBridge:
    """
    Gymnasium环境与游戏服务器的桥接类
    
    这个类将Gymnasium环境与游戏服务器连接，使得：
    1. 游戏服务器状态更新可以同步到Gymnasium环境
    2. Gymnasium环境的动作可以转换为游戏服务器的动作
    3. 支持实时训练和评估
    4. 支持stable-baselines3和自定义DQN智能体
    """
    
    def __init__(
        self,
        env: CTFGymEnv,
        agent,
        world: Optional[World] = None
    ):
        """
        初始化桥接
        
        Args:
            env: Gymnasium环境实例（CTFGymEnv）
            agent: RL智能体（可以是DQNAgent或stable-baselines3模型）
            world: World对象（如果为None，会从env获取）
        """
        self.env = env
        self.agent = agent
        self.world = world or env.world
        
        # 状态管理
        self.current_obs = None
        self.prev_obs = None
        self.current_info = None
        self.episode_reward = 0.0
        self.episode_step = 0
        self._last_action = 0  # 保存上一帧动作
        
        # 统计信息
        self.stats = {
            'episode': 0,
            'total_reward': 0.0,
            'episode_rewards': [],
            'episode_lengths': []
        }
    
    def start_game(self, req: Dict) -> None:
        """游戏开始时调用"""
        # 检查请求是否包含map字段（init请求的特征）
        if "map" not in req:
            print(f"[Gym Training] Warning: start_game called without 'map' field, skipping init")
            return
        
        # 初始化world
        try:
            self.world.init(req)
        except Exception as e:
            print(f"[Gym Training] world.init() failed: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # 检查玩家是否存在，如果不存在则延迟reset
        my_team = Team.LEFT if self.world.my_team_name == "L" else Team.RIGHT
        my_players = list_players(self.world.players, my_team, in_prison=False, has_flag=None)
        
        if not my_players:
            # 如果玩家不存在，先不reset，等待第一次状态更新
            print(f"[Gym Training] No players found yet, will reset after first status update")
            self.current_obs = None
            self.current_info = None
            self.prev_obs = None
        else:
            # 重置Gymnasium环境
            options = {'init_data': req}
            try:
                self.current_obs, self.current_info = self.env.reset(options=options)
                self.prev_obs = None  # 第一帧没有prev_obs
            except ValueError as e:
                # 如果reset失败（玩家不存在），延迟到第一次状态更新
                print(f"[Gym Training] Reset failed: {e}, will retry after first status update")
                self.current_obs = None
                self.current_info = None
                self.prev_obs = None
        
        self.episode_reward = 0.0
        self.episode_step = 0
        
        print(f"[Gym Training] Episode {self.stats['episode'] + 1} started")
    
    def plan_next_actions(self, req: Dict) -> Dict:
        """
        计划下一步动作（与游戏服务器集成）
        
        Args:
            req: 游戏状态请求
        
        Returns:
            动作字典 {player_name: direction}
        """
        # 减少日志输出，只在需要时打印
        # print(f"[Gym Training] plan_next_actions called, req keys: {list(req.keys())}")
        
        # 在更新world状态之前，保存上一帧的分数（用于检测得分）
        my_team = Team.LEFT if self.world.my_team_name == "L" else Team.RIGHT
        prev_score = self.world.left_team_score if my_team == Team.LEFT else self.world.right_team_score
        
        # 更新world状态
        if not self.world.update(req):
            print(f"[Gym Training] world.update() returned False")
            return {"actions": {}, "paths": {}, "timings": {}}
        
        # 更新Gymnasium环境的状态
        self.env.update_world_state(req)
        
        # 检测得分（在world.update()之后，分数可能已经更新）
        current_score = self.world.left_team_score if my_team == Team.LEFT else self.world.right_team_score
        if current_score > prev_score:
            print(f"[Gym Training] 🎉 得分检测！{my_team.value}队得分: {prev_score} -> {current_score}")
            # 如果env有prev_state_dict，更新其中的分数（用于奖励计算）
            if hasattr(self.env, 'prev_state_dict') and self.env.prev_state_dict:
                self.env.prev_state_dict['team_score'] = prev_score  # 保存更新前的分数
        
        # 获取当前玩家
        my_team = Team.LEFT if self.world.my_team_name == "L" else Team.RIGHT
        my_players = list_players(self.world.players, my_team, in_prison=False, has_flag=None)
        
        if not my_players:
            print(f"[Gym Training] No players found for team {my_team.value}")
            return {"actions": {}, "paths": {}, "timings": {}}
        
        # 减少日志输出
        # print(f"[Gym Training] Found {len(my_players)} players: {[p.name for p in my_players]}")
        
        # 如果环境还没有初始化（第一次状态更新），现在尝试reset
        # 注意：如果req中没有map字段，说明是status请求，不能用于reset
        if self.current_obs is None:
            # 检查是否有map字段，如果没有，说明world还没有初始化，先尝试从当前req初始化观察
            if 'map' not in req:
                # 如果没有map字段，说明world可能还没有初始化，先提取观察
                try:
                    from .state_extractor import extract_state_features
                    if my_players:
                        player = my_players[0]
                        self.current_obs = extract_state_features(player, self.world)
                        self.prev_obs = None
                        print(f"[Gym Training] Extracted observation without reset")
                except Exception as e:
                    print(f"[Gym Training] Failed to extract observation: {e}")
                    return {"actions": {}, "paths": {}, "timings": {}}
            else:
                # 如果有map字段，可以安全地reset
                try:
                    options = {'init_data': req}
                    self.current_obs, self.current_info = self.env.reset(options=options)
                    self.prev_obs = None
                    print(f"[Gym Training] Environment reset successful after first status update")
                except Exception as e:
                    print(f"[Gym Training] Reset failed: {e}")
                    import traceback
                    traceback.print_exc()
                    return {"actions": {}, "paths": {}, "timings": {}}
        
        actions: Dict[str, str] = {}
        
        # 清空上一帧的路径（由 World 统一管理收集）
        self.world._current_paths.clear()
        
        # 为每个玩家选择动作
        for player in my_players:
            if player.is_in_prison:
                continue
            
            player_name = player.name
            
            # 如果环境是为这个玩家创建的，使用Gymnasium接口
            if self.env.player_name == player_name:
                # 确保当前观察已初始化
                if self.current_obs is None:
                    from .state_extractor import extract_state_features
                    self.current_obs = extract_state_features(player, self.world)
                    self.prev_obs = None  # 第一帧
                
                # 如果有上一帧的观察，先执行step收集经验
                if self.prev_obs is not None and self.current_obs is not None:
                    # 使用上一帧的动作（如果有）
                    prev_action = getattr(self, '_last_action', 0)
                    # 执行step以更新状态和计算奖励
                    obs, reward, terminated, truncated, info = self.env.step(prev_action)
                    self.episode_reward += reward
                    
                    # 如果是自定义DQN，存储经验
                    if hasattr(self.agent, 'replay_buffer'):
                        self.agent.replay_buffer.push(
                            self.prev_obs,
                            prev_action,
                            reward,
                            obs,
                            terminated or truncated
                        )
                    
                    # 更新观察
                    self.prev_obs = self.current_obs
                    self.current_obs = obs
                
                # 使用Gymnasium环境选择动作
                action = self._select_action_from_gym()
                self._last_action = action  # 保存动作供下一帧使用
                
                # 将Gymnasium动作转换为策略，然后让 Player 自己执行
                # Player 是自驱动的，智能体只提供策略建议
                # Strategy枚举的值：DEFENCE=0, SCORING=1, SAVING=2
                try:
                    # 从值获取Strategy枚举
                    strategy = Strategy(action)
                except (ValueError, TypeError):
                    # 如果action不在Strategy枚举中，使用默认策略
                    print(f"[Gym Training] Invalid action {action}, using SCORING strategy")
                    strategy = Strategy.SCORING
                
                direction = player.plan(suggested_strategy=strategy)
                if direction:
                    actions[player_name] = direction.value
                    # 减少日志输出，只在需要时打印
                    # print(f"[Gym Training] {player_name}: action={action}, strategy={strategy.name}, direction={direction.value}")
                else:
                    # 如果player.plan()返回None，让Player自己规划（不使用策略建议）
                    # 减少日志输出
                    # print(f"[Gym Training] {player_name}: plan() returned None with strategy {strategy.name}, trying without strategy")
                    direction = player.plan()
                    if direction:
                        actions[player_name] = direction.value
                        # 减少日志输出
                        # print(f"[Gym Training] {player_name}: plan() without strategy returned {direction.value}")
                    else:
                        # 如果还是None，使用随机方向作为fallback
                        import random
                        from ..data_models import Direction
                        fallback_directions = [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]
                        fallback_direction = random.choice(fallback_directions)
                        actions[player_name] = fallback_direction.value
                        # 减少日志输出
                        # print(f"[Gym Training] {player_name}: Using fallback direction {fallback_direction.value}")
            else:
                # 对于其他玩家，使用智能体的predict_schedule或让Player自己规划
                direction = None
                if hasattr(self.agent, 'predict_schedule'):
                    # 使用DQNAgent的predict_schedule
                    try:
                        schedule = self.agent.predict_schedule([player], self.world, training=True)
                        schedule_key = f"{player_name}schedule"
                        if schedule_key in schedule:
                            strategy, player_dict, target = schedule[schedule_key]
                            # 让 Player 自己根据策略执行（自驱动）
                            direction = player.plan(suggested_strategy=strategy)
                            if direction:
                                actions[player_name] = direction.value
                                # 减少日志输出
                                # print(f"[Gym Training] {player_name}: predict_schedule strategy={strategy.name}, direction={direction.value}")
                    except Exception as e:
                        print(f"[Gym Training] {player_name}: predict_schedule failed: {e}")
                
                # 如果predict_schedule没有返回结果或失败，让Player自己规划
                if not direction:
                    direction = player.plan()
                    if direction:
                        actions[player_name] = direction.value
                        # 减少日志输出
                        # print(f"[Gym Training] {player_name}: plan() returned {direction.value}")
                    else:
                        # 如果还是None，使用随机方向作为fallback
                        import random
                        from ..data_models import Direction
                        fallback_directions = [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]
                        fallback_direction = random.choice(fallback_directions)
                        actions[player_name] = fallback_direction.value
                        # 减少日志输出
                        # print(f"[Gym Training] {player_name}: Using fallback direction {fallback_direction.value}")
        
        # 更新episode步数
        self.episode_step += 1
        
        # 减少日志输出，只在没有动作时警告
        if not actions:
            print(f"[Gym Training] Warning: No actions generated for {len(my_players)} players!")
        
        # 交给 World 统一构造返回结果（动作 / 路径 / 耗时，只包含己方）
        return self.world.build_result_from_actions(actions)
    
    def _select_action_from_gym(self) -> int:
        """从Gymnasium环境选择动作"""
        if self.current_obs is None:
            # 如果观察为None，返回随机动作而不是默认动作0
            return self.env.action_space.sample() if hasattr(self.env, 'action_space') else 0
        
        # 根据智能体类型选择动作
        try:
            if hasattr(self.agent, 'predict'):
                # stable-baselines3模型
                action, _ = self.agent.predict(self.current_obs, deterministic=False)
                return int(action)
            elif hasattr(self.agent, 'select_action'):
                # DQNAgent
                return self.agent.select_action(self.current_obs, training=True)
            else:
                # 随机动作
                return self.env.action_space.sample() if hasattr(self.env, 'action_space') else 0
        except Exception as e:
            # 如果动作选择失败，返回随机动作
            print(f"[Gym Training] Action selection failed: {e}, using random action")
            import traceback
            traceback.print_exc()
            return self.env.action_space.sample() if hasattr(self.env, 'action_space') else 0
    
    # Player 是自驱动的，直接调用 player.plan(suggested_strategy=...) 即可
    # Player 会根据 world 状态自己执行策略
    
    def game_over(self, req: Dict) -> None:
        """游戏结束时调用"""
        # 更新统计信息
        self.stats['episode'] += 1
        self.stats['episode_rewards'].append(self.episode_reward)
        self.stats['episode_lengths'].append(self.episode_step)
        
        # 打印统计
        avg_reward = sum(self.stats['episode_rewards'][-10:]) / min(10, len(self.stats['episode_rewards']))
        print(f"[Gym Training] Episode {self.stats['episode']} finished")
        print(f"  Total Reward: {self.episode_reward:.2f}")
        print(f"  Episode Length: {self.episode_step}")
        print(f"  Avg Reward (last 10): {avg_reward:.2f}")
        
        # 训练一步（如果是自定义DQN）
        if hasattr(self.agent, 'train_step'):
            if len(self.agent.replay_buffer) >= 32:
                loss = self.agent.train_step(batch_size=32)
                if loss is not None:
                    print(f"  Training Loss: {loss:.4f}")
        
        # 更新epsilon（如果是DQNAgent）
        if hasattr(self.agent, 'update_epsilon'):
            self.agent.update_epsilon()


def create_gym_server_callbacks(bridge: GymServerBridge):
    """
    创建游戏服务器回调函数
    
    Args:
        bridge: GymServerBridge实例
    
    Returns:
        (start_fn, plan_fn, end_fn) 元组
    """
    def start_fn(req: Dict) -> None:
        bridge.start_game(req)
    
    def plan_fn(req: Dict) -> Dict:
        return bridge.plan_next_actions(req)
    
    def end_fn(req: Dict) -> None:
        bridge.game_over(req)
    
    return start_fn, plan_fn, end_fn
