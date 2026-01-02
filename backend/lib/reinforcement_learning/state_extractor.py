"""
状态特征提取模块
用于从游戏状态中提取强化学习所需的状态特征向量
"""

import numpy as np
from typing import TYPE_CHECKING

from ..data_models import Position, Team
from ..utils import (
    list_players, 
    list_flags
)

if TYPE_CHECKING:
    from ..data_models.player import Player
    from ..game_engine import World


def extract_state_features(player: 'Player', world: 'World') -> np.ndarray:
    """
    提取玩家的状态特征向量
    
    Args:
        player: Player对象
        world: World对象
    
    Returns:
        numpy array: 状态特征向量（19维）
    """
    features = []
    
    # ========== 玩家自身信息 (5维) ==========
    pos_x = player.position.x
    pos_y = player.position.y
    player_pos_obj = player.position
    
    # 归一化位置 [0,1] - 使用更稳定的归一化方法
    # 使用 (x + 0.5) / (width + 1) 来避免边界问题
    player_pos_x = (pos_x + 0.5) / max(world.width + 1, 1)
    player_pos_y = (pos_y + 0.5) / max(world.height + 1, 1)
    # 确保值在[0,1]范围内
    player_pos_x = max(0.0, min(1.0, player_pos_x))
    player_pos_y = max(0.0, min(1.0, player_pos_y))
    features.extend([player_pos_x, player_pos_y])
    
    # 玩家状态
    player_has_flag = 1.0 if player.has_flag else 0.0
    player_in_prison = 1.0 if player.is_in_prison else 0.0
    is_in_enemy_territory_val = 1.0 if world.is_in_enemy_territory(player.position, player.team) else 0.0
    features.extend([player_has_flag, player_in_prison, is_in_enemy_territory_val])
    
    # ========== 目标信息 (6维: 1距离 + 4方向 + 1flag_dist) ==========
    my_team = Team.LEFT if world.my_team_name == "L" else Team.RIGHT
    enemy_flags = list_flags(world.flags, my_team, is_enemy=True, can_pickup=True)
    my_targets = world.get_team_target_positions(my_team)
    
    if enemy_flags:
        # 找到最近的敌方flag
        min_flag_dist = float('inf')
        nearest_flag = None
        for flag in enemy_flags:
            # Flag对象有position属性
            flag_pos = flag.position.to_tuple()
            dist = player_pos_obj.manhattan_distance(flag.position)
            if dist < min_flag_dist:
                min_flag_dist = dist
                nearest_flag = flag_pos
        
        # 归一化距离（使用更稳定的归一化方法）
        # 使用曼哈顿距离的最大值（width + height）而不是欧几里得距离
        max_manhattan_dist = world.width + world.height
        nearest_flag_dist = min(min_flag_dist / max(max_manhattan_dist, 1), 1.0) if max_manhattan_dist > 0 else 0.0
        
        # 方向编码（4维one-hot）
        if nearest_flag:
            # nearest_flag是元组 (x, y)
            dx = nearest_flag[0] - pos_x
            dy = nearest_flag[1] - pos_y
            
            # 确定主要方向
            if abs(dx) > abs(dy):
                if dx > 0:
                    nearest_flag_dir = [1.0, 0.0, 0.0, 0.0]  # right
                else:
                    nearest_flag_dir = [0.0, 0.0, 1.0, 0.0]  # left
            else:
                if dy > 0:
                    nearest_flag_dir = [0.0, 1.0, 0.0, 0.0]  # down
                else:
                    nearest_flag_dir = [0.0, 0.0, 0.0, 1.0]  # up
        else:
            nearest_flag_dir = [0.0, 0.0, 0.0, 0.0]
    else:
        nearest_flag_dist = 1.0  # 没有flag，距离设为最大
        nearest_flag_dir = [0.0, 0.0, 0.0, 0.0]
    
    features.append(nearest_flag_dist)
    features.extend(nearest_flag_dir)
    
    # flag_dist: 如果玩家有flag，到目标区域的距离
    if player_has_flag and my_targets:
        target = my_targets[0]
        flag_dist = player_pos_obj.manhattan_distance(target)
        max_manhattan_dist = world.width + world.height
        flag_dist = min(flag_dist / max(max_manhattan_dist, 1), 1.0) if max_manhattan_dist > 0 else 0.0
    else:
        flag_dist = 0.0
    features.append(flag_dist)
    
    # ========== 对手信息 (4维) ==========
    opponent_team = Team.RIGHT if my_team == Team.LEFT else Team.LEFT
    opponents = list_players(world.players, opponent_team, in_prison=False, has_flag=None)
    my_flags = list_flags(world.flags, opponent_team, is_enemy=False, can_pickup=None)
    
    if opponents:
        # 找到最近的敌人
        min_enemy_dist = float('inf')
        nearest_enemy = None
        for opp in opponents:
            dist = player_pos_obj.manhattan_distance(opp.position)
            if dist < min_enemy_dist:
                min_enemy_dist = dist
                nearest_enemy = opp
        
        # 归一化距离（使用曼哈顿距离）
        max_manhattan_dist = world.width + world.height
        enemy_dist = min(min_enemy_dist / max(max_manhattan_dist, 1), 1.0) if max_manhattan_dist > 0 else 0.0
        
        # enemy_danger: 根据敌人到最近己方flag的距离和是否在己方区域加权
        enemy_danger = 0.0
        if nearest_enemy and my_flags:
            # 找到敌人到最近己方flag的距离
            min_flag_dist_to_enemy = float('inf')
            for flag in my_flags:
                dist = nearest_enemy.position.manhattan_distance(flag.position)
                if dist < min_flag_dist_to_enemy:
                    min_flag_dist_to_enemy = dist
            
            # 计算危险度：距离越近危险度越高，在己方区域危险度翻倍
            in_my_territory = world.is_in_team_territory(nearest_enemy.position, my_team)
            danger_base = 1.0 / (min_flag_dist_to_enemy + 1.0)
            territory_multiplier = 2.0 if in_my_territory else 1.0
            enemy_danger = danger_base * territory_multiplier
            # 归一化到[0,1]
            enemy_danger = min(enemy_danger / 2.0, 1.0)
        
        # 是否有敌人持旗
        enemy_has_flag = 1.0 if any(opp.has_flag for opp in opponents) else 0.0
    else:
        enemy_dist = 1.0  # 没有敌人，距离设为最大
        enemy_danger = 0.0
        enemy_has_flag = 0.0
    
    # 是否有敌人在prison
    enemies_in_prison = list_players(world.players, opponent_team, in_prison=True, has_flag=None)
    enemy_in_prison = 1.0 if enemies_in_prison else 0.0
    
    features.extend([enemy_dist, enemy_danger, enemy_has_flag, enemy_in_prison])
    
    # ========== 全局信息 (4维) ==========
    my_flags_list = list_flags(world.flags, opponent_team, is_enemy=False, can_pickup=None)
    enemy_flags_list = list_flags(world.flags, my_team, is_enemy=True, can_pickup=None)
    
    # flag数量（归一化，假设最多3个flag）
    my_flags_count = min(len(my_flags_list) / 3.0, 1.0) if my_flags_list else 0.0
    enemy_flags_count = min(len(enemy_flags_list) / 3.0, 1.0) if enemy_flags_list else 0.0
    
    # 得分（需要从flag位置推断：flag在目标区域表示得分）
    my_score = 0.0
    enemy_score = 0.0
    
    my_targets_set = set(world.get_team_target_positions(my_team))
    enemy_targets_set = set(world.get_team_target_positions(opponent_team))
    
    # 检查己方flag是否在目标区域
    for flag in my_flags_list:
        if flag.position in my_targets_set:
            my_score += 1.0
    
    # 检查敌方flag是否在目标区域
    for flag in enemy_flags_list:
        if flag.position in enemy_targets_set:
            enemy_score += 1.0
    
    # 归一化得分（假设最多3分）
    my_score = min(my_score / 3.0, 1.0)
    enemy_score = min(enemy_score / 3.0, 1.0)
    
    features.extend([my_flags_count, enemy_flags_count, my_score, enemy_score])
    
    # 验证特征向量维度
    feature_array = np.array(features, dtype=np.float32)
    expected_dim = 19  # 5(玩家) + 6(目标) + 4(对手) + 4(全局) = 19
    
    if len(feature_array) != expected_dim:
        print(f"⚠️  警告：状态特征向量维度不匹配！")
        print(f"   玩家: {player.name}, 在prison: {player.is_in_prison}")
        print(f"   期望维度: {expected_dim}, 实际维度: {len(feature_array)}")
        print(f"   特征列表: {features}")
        # 如果维度不匹配，尝试修复或抛出错误
        if len(feature_array) < expected_dim:
            # 补零
            feature_array = np.pad(feature_array, (0, expected_dim - len(feature_array)), 'constant')
        elif len(feature_array) > expected_dim:
            # 截断
            feature_array = feature_array[:expected_dim]
        print(f"   已修复为: {len(feature_array)}维")
    
    return feature_array
