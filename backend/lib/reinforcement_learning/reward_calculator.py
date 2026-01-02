"""
奖励计算模块
用于计算强化学习中的奖励信号

奖励设计（聚焦基地插旗得分，兼顾稳定性）：
- 步惩罚: -0.02（稍微加大步惩罚，避免长时间空跑）
- 拾旗奖励: +10.0（鼓励拾取旗帜，但不至于爆炸）
- 得分奖励: +150.0（仍然是最高优先级，但降低爆炸幅度）
- 持有旗帜时接近基地: +3.0~+25.0（渐进式奖励，距离越近奖励越高）
- 进入基地区域（持有旗帜）: +40.0（关键里程碑）
- 失去旗帜惩罚: -40.0（加大惩罚，避免无脑送旗）
- 被捕获惩罚: -25.0（适度惩罚）
- 其他策略奖励降低，聚焦得分目标
- 最终对单步奖励做裁剪：[-50, 200]，避免回报爆炸（稳定训练）
"""

from typing import Optional, TYPE_CHECKING
from ..data_models import Position, Team, Strategy
from ..utils import (
    list_players, 
    list_flags
)

if TYPE_CHECKING:
    from ..data_models.player import Player
    from ..game_engine import World


def calculate_reward(
    player: 'Player',
    world: 'World',
    prev_state_dict: Optional[dict] = None,
    current_action: Optional[int] = None
) -> float:
    """
    计算奖励
    
    Args:
        player: Player对象
        world: World对象
        prev_state_dict: 上一帧的状态字典 {hasFlag, inPrison, posX, posY, ...}（可选）
        current_action: 当前选择的动作 (Strategy.DEFENCE.value/SCORING.value/SAVING.value) 或 None
    
    Returns:
        float: 奖励值
    """
    reward = 0.0
    
    if prev_state_dict is None:
        # 第一帧，只有步惩罚
        reward = -0.02
        return reward
    
    # 步惩罚：略微加大，避免长时间空跑
    reward -= 0.02
    
    # 检测事件
    current_has_flag = player.has_flag
    prev_has_flag = prev_state_dict.get("hasFlag", False)
    current_in_prison = player.is_in_prison
    prev_in_prison = prev_state_dict.get("inPrison", False)
    
    # pick_flag: 玩家刚获得flag（鼓励拾取旗帜）
    if current_has_flag and not prev_has_flag:
        reward += 10.0
    
    # lose_flag: 玩家失去flag（适度惩罚）
    if not current_has_flag and prev_has_flag:
        reward -= 40.0
    
    # get_caught: 玩家被捕获（适度惩罚，不影响得分目标）
    if current_in_prison and not prev_in_prison:
        reward -= 25.0
    
    # score_flag: 检测实际得分事件（通过检查分数变化）
    # 注意：需要在调用此函数前保存上一帧的分数
    my_team = Team.LEFT if world.my_team_name == "L" else Team.RIGHT
    prev_score = prev_state_dict.get("team_score", None) if prev_state_dict else None
    current_score = world.left_team_score if my_team == Team.LEFT else world.right_team_score
    
    # score_flag: 得分事件（最高优先级奖励，聚焦得分目标）
    if prev_score is not None and current_score > prev_score:
        reward += 150.0
        print(f"[Reward] 🎉 得分奖励！{my_team.value}队得分: {prev_score} -> {current_score}, 奖励: +150.0")
    
    # 检测是否进入目标区域（持有旗帜时）- 关键里程碑
    if prev_has_flag and prev_state_dict:
        prev_pos = Position(prev_state_dict["posX"], prev_state_dict["posY"])
        current_pos = player.position
        my_targets = set(world.get_team_target_positions(my_team))
        
        # 如果上一帧不在目标区域，当前帧在目标区域（持有旗帜时）
        prev_in_target = prev_pos in my_targets
        current_in_target = current_pos in my_targets
        
        if current_in_target and not prev_in_target:
            reward += 40.0
            print(f"[Reward] 🏁 进入基地区域（持有旗帜）！奖励: +40.0")
    
    # ========== 基于动作的奖励调整 ==========
    if current_action is not None:
        pos_x = player.position.x
        pos_y = player.position.y
        player_pos_obj = Position(pos_x, pos_y)
        my_team = Team.LEFT if world.my_team_name == "L" else Team.RIGHT
        opponent_team = Team.RIGHT if my_team == Team.LEFT else Team.LEFT
        
        # 1. 防御决策奖励：降低奖励，聚焦得分目标
        if current_action == Strategy.DEFENCE.value:  # defence
            opponents = list_players(world.players, opponent_team, in_prison=False, has_flag=None)
            
            # 检查是否有敌人在己方领地
            enemies_in_my_territory = []
            for opp in opponents:
                if world.is_in_team_territory(opp.position, my_team):
                    enemies_in_my_territory.append(opp)
            
            # 如果有敌人在己方领地，选择防御动作给予小奖励（降低优先级）
            if enemies_in_my_territory:
                reward += 3.0
                
                # 如果敌人持旗，额外奖励拦截（保护得分机会）
                for enemy in enemies_in_my_territory:
                    if enemy.has_flag:
                        reward += 10.0  # 拦截持旗敌人，保护得分机会（仍然重要）
                        break
        
        # 2. 拿旗决策奖励：聚焦得分，大幅提高持有旗帜时接近基地的奖励
        if current_action == Strategy.SCORING.value:  # scoring
            if not current_has_flag:
                # 未持旗时，接近敌方旗帜的奖励（适度）
                enemy_flags = list_flags(world.flags, my_team, is_enemy=True, can_pickup=True)
                if enemy_flags:
                    min_dist = float('inf')
                    for flag in enemy_flags:
                        dist = player_pos_obj.manhattan_distance(flag.position)
                        if dist < min_dist:
                            min_dist = dist
                    
                    # 渐进式距离奖励（适度）
                    if min_dist <= 1:
                        reward += 2.0
                    elif min_dist <= 2:
                        reward += 1.5
                    elif min_dist <= 3:
                        reward += 0.7
                    elif min_dist <= 5:
                        reward += 0.3
                    # 使用平滑的距离奖励函数
                    distance_reward = 1.0 / (1.0 + min_dist)
                    reward += 0.05 * distance_reward
            else:
                # 有旗时，接近目标区域的奖励（大幅提高，聚焦得分）
                my_targets = world.get_team_target_positions(my_team)
                if my_targets:
                    min_target_dist = float('inf')
                    for target in my_targets:
                        dist = player_pos_obj.manhattan_distance(target)
                        if dist < min_target_dist:
                            min_target_dist = dist
                    
                    # 渐进式接近目标奖励（大幅提高）
                    if min_target_dist <= 1:
                        reward += 25.0
                    elif min_target_dist <= 2:
                        reward += 18.0
                    elif min_target_dist <= 3:
                        reward += 10.0
                    elif min_target_dist <= 5:
                        reward += 3.0
                    # 使用平滑的距离奖励函数（额外奖励，降低系数）
                    distance_reward = 1.0 / (1.0 + min_target_dist)
                    reward += 0.8 * distance_reward
        
        # 3. 救人决策奖励：降低奖励，聚焦得分目标
        if current_action == Strategy.SAVING.value:  # saving
            my_players_active = list_players(world.players, my_team, in_prison=False, has_flag=None)
            my_players_in_prison = list_players(world.players, my_team, in_prison=True, has_flag=None)
            
            if len(my_players_in_prison) > 0:
                # 根据场上活跃玩家数量调整奖励（降低优先级）
                if len(my_players_active) == 1:
                    reward += 6.0
                elif len(my_players_active) == 2:
                    reward += 3.0
                else:
                    reward += 1.0
                
                # 如果接近监狱，小奖励
                enemy_prison_area = world.get_team_prison_area(opponent_team)
                if enemy_prison_area:
                    min_prison_dist = float('inf')
                    for prison_pos in enemy_prison_area.positions:
                        dist = player_pos_obj.manhattan_distance(prison_pos)
                        if dist < min_prison_dist:
                            min_prison_dist = dist
                    
                    if min_prison_dist <= 2:
                        reward += 1.0  # 接近监狱，小奖励
    
    # distance_to_flag: 基于距离的连续奖励（仅在未指定动作时使用，降低优先级）
    if current_action is None and not current_has_flag:
        my_team = Team.LEFT if world.my_team_name == "L" else Team.RIGHT
        enemy_flags = list_flags(world.flags, my_team, is_enemy=True, can_pickup=True)
        if enemy_flags:
            min_dist = float('inf')
            for flag in enemy_flags:
                dist = player.position.manhattan_distance(flag.position)
                if dist < min_dist:
                    min_dist = dist
            
            # 使用平滑的距离奖励函数（降低系数，聚焦得分）
            distance_reward = 1.0 / (1.0 + min_dist)
            reward += 0.05 * distance_reward
    
    # 持有旗帜时，持续给予接近基地的奖励（聚焦得分）
    if current_has_flag:
        my_team = Team.LEFT if world.my_team_name == "L" else Team.RIGHT
        my_targets = world.get_team_target_positions(my_team)
        if my_targets:
            min_target_dist = float('inf')
            for target in my_targets:
                dist = player.position.manhattan_distance(target)
                if dist < min_target_dist:
                    min_target_dist = dist
            
            # 持有旗帜时，持续给予接近基地的奖励（聚焦得分）
            if min_target_dist <= 10:  # 扩大范围，持续引导
                # 使用平滑的距离奖励函数（中等系数）
                distance_reward = 1.0 / (1.0 + min_target_dist)
                reward += 0.5 * distance_reward
    
    # 对单步奖励做裁剪，避免极端值导致训练不稳定
    reward = max(min(reward, 200.0), -50.0)
    return reward
