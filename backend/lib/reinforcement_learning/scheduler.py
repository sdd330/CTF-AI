"""
策略调度模块
用于根据RL决策生成策略分配表
"""

import torch
import numpy as np
from typing import Dict, List, TYPE_CHECKING
from ..data_models import Position, Team, Strategy
from ..utils import (
    list_players, 
    list_flags
)
from .state_extractor import extract_state_features

if TYPE_CHECKING:
    from ..data_models.player import Player
    from ..game_engine import World


def predict_schedule(
    q_network,
    device,
    players: List['Player'],
    world: 'World',
    training: bool = False
) -> Dict:
    """
    预测决策表（快速推理，<0.1秒）
    
    Args:
        q_network: Q网络模型
        device: 设备（'cpu' 或 'cuda'）
        players: 己方玩家对象列表
        world: World对象
        training: 是否处于训练模式
    
    Returns:
        dict: 策略表 {player_name + "schedule": (strategy, player_dict, target)}
    """
    schedule = {}
    
    # 获取所有相关信息
    my_team = Team.LEFT if world.my_team_name == "L" else Team.RIGHT
    opponent_team = Team.RIGHT if my_team == Team.LEFT else Team.LEFT
    opponents = list_players(world.players, opponent_team, in_prison=False, has_flag=None)
    enemy_flags = list_flags(world.flags, my_team, is_enemy=True, can_pickup=True)
    my_players_in_prison = list_players(world.players, my_team, in_prison=True, has_flag=None)
    
    # 批量提取状态特征
    states = []
    valid_players = []
    
    for player in players:
        if player.is_in_prison:
            continue  # 跳过在prison中的玩家
        
        state = extract_state_features(player, world)
        # 验证状态维度
        if len(state) != 19:
            print(f"⚠️  警告：玩家 {player.name} 的状态维度错误: {len(state)} (期望19)")
            continue  # 跳过维度不正确的状态
        
        states.append(state)
        valid_players.append(player)
    
    if not states:
        return schedule
    
    # 批量推理（加速）
    # 在推理时确保网络处于eval模式（避免BatchNorm在batch size=1时出错）
    was_training = q_network.training
    q_network.eval()
    
    with torch.no_grad():
        states_tensor = torch.FloatTensor(np.array(states)).to(device)
        q_values = q_network(states_tensor)
        actions = q_values.argmax(dim=1).cpu().numpy()
    
    # 恢复训练模式（如果之前是训练模式）
    if was_training:
        q_network.train()
    
    # 检查是否有敌人在己方领地（需要至少一个玩家防御）
    enemies_in_my_territory = []
    for opp in opponents:
        if world.is_in_team_territory(opp.position, my_team):
            enemies_in_my_territory.append(opp)
    
    # 为每个玩家分配策略
    assigned_enemies = set()
    assigned_flags = set()
    has_defender = False  # 记录是否已有玩家选择防御
    
    for i, player in enumerate(valid_players):
        action = actions[i]
        player_name = player.name
        
        if action == Strategy.DEFENCE.value:  # defence
            # 找到最近的敌人（优先选择己方领地内的敌人）
            best_opponent = None
            min_dist = float('inf')
            
            for opp in opponents:
                if opp.name in assigned_enemies:
                    continue
                dist = player.position.manhattan_distance(opp.position)
                
                # 如果敌人在己方领地，优先选择
                if world.is_in_team_territory(opp.position, my_team) and (best_opponent is None or dist < min_dist):
                    min_dist = dist
                    best_opponent = opp
            
            # 如果没有找到己方领地的敌人，选择最近的敌人
            if best_opponent is None:
                for opp in opponents:
                    if opp.name in assigned_enemies:
                        continue
                    dist = player.position.manhattan_distance(opp.position)
                    if dist < min_dist:
                        min_dist = dist
                        best_opponent = opp
            
            if best_opponent:
                schedule[f"{player_name}schedule"] = (Strategy.DEFENCE, player.to_dict(), best_opponent.to_dict())
                assigned_enemies.add(best_opponent.name)
                has_defender = True
            else:
                # 所有敌方都在prison，无法防御，转换为scoring策略
                if player.has_flag:
                    # 有flag，返回目标区域
                    my_targets_list = world.get_team_target_positions(my_team)
                    if my_targets_list:
                        schedule[f"{player_name}schedule"] = (Strategy.SCORING, player.to_dict(), my_targets_list[0].to_tuple())
                else:
                    # 无flag，找最近的敌方flag
                    best_flag = None
                    min_dist = float('inf')
                    
                    for flag in enemy_flags:
                        flag_pos_tuple = flag.position.to_tuple()
                        if flag_pos_tuple in assigned_flags:
                            continue
                        dist = player.position.manhattan_distance(flag.position)
                        if dist < min_dist:
                            min_dist = dist
                            best_flag = flag
                    
                    if best_flag:
                        schedule[f"{player_name}schedule"] = (Strategy.SCORING, player.to_dict(), best_flag.to_dict())
                        assigned_flags.add(best_flag.position.to_tuple())
                    elif my_players_in_prison:
                        # 如果没有flag可拿，且队友在prison，改为saving
                        schedule[f"{player_name}schedule"] = (Strategy.SAVING, player.to_dict(), None)
        
        # 如果有敌人在己方领地但没有玩家选择防御，强制第一个玩家选择防御
        elif enemies_in_my_territory and not has_defender and i == 0:
            best_opponent = None
            min_dist = float('inf')
            
            for opp_obj in enemies_in_my_territory:
                if opp_obj.name in assigned_enemies:
                    continue
                dist = player.position.manhattan_distance(opp_obj.position)
                if dist < min_dist:
                    min_dist = dist
                    best_opponent = opp_obj
            
            if best_opponent:
                schedule[f"{player_name}schedule"] = (Strategy.DEFENCE, player.to_dict(), best_opponent.to_dict())
                assigned_enemies.add(best_opponent.name)
                has_defender = True
                continue  # 跳过原来的动作分配
        
        elif action == Strategy.SCORING.value:  # scoring
            # 找到最近的flag或目标
            if player.has_flag:
                # 有flag，返回目标区域
                my_targets_list = world.get_team_target_positions(my_team)
                if my_targets_list:
                    schedule[f"{player_name}schedule"] = (Strategy.SCORING, player.to_dict(), my_targets_list[0].to_tuple())
            else:
                # 无flag，找最近的敌方flag
                best_flag = None
                min_dist = float('inf')
                
                for flag in enemy_flags:
                    flag_pos_tuple = flag.position.to_tuple()
                    if flag_pos_tuple in assigned_flags:
                        continue
                    dist = player.position.manhattan_distance(flag.position)
                    if dist < min_dist:
                        min_dist = dist
                        best_flag = flag
                
                if best_flag:
                    schedule[f"{player_name}schedule"] = (Strategy.SCORING, player.to_dict(), best_flag.to_dict())
                    assigned_flags.add(best_flag.position.to_tuple())
        
        elif action == Strategy.SAVING.value:  # saving
            # 营救在prison中的队友
            if my_players_in_prison:
                schedule[f"{player_name}schedule"] = (Strategy.SAVING, player.to_dict(), None)
    
    return schedule
