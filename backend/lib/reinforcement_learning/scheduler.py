"""
策略调度模块
用于根据RL决策生成策略分配表
"""

import torch
import numpy as np
from typing import Dict, List, TYPE_CHECKING
from ..data_models import Team, Strategy
from .state_extractor import extract_state_features
from .scheduler_helpers import find_best_opponent, find_best_flag, get_scoring_target

if TYPE_CHECKING:
    from ..data_models.player import Player
    from ..game_engine import World


def predict_schedule(q_network, device, players: List['Player'],
                     world: 'World', training: bool = False) -> Dict:
    """预测决策表（快速推理，<0.1秒）"""
    schedule = {}
    my_team = Team.LEFT if world.my_team_name == "L" else Team.RIGHT

    # 收集游戏状态
    opponents = [p for p in world.enemy_players.values() if not p.is_in_prison]
    enemy_flags = [f for f in world.enemy_flags.values() if f.can_pickup]
    prisoners = [p for p in world.my_players.values() if p.is_in_prison]
    enemies_in_territory = [o for o in opponents if world.map.is_in_team_territory(o.position, my_team)]

    # 批量提取状态特征
    states, valid_players = _extract_batch_states(players, world)
    if not states:
        return schedule

    # 批量推理
    actions = _batch_inference(q_network, device, states)

    # 分配策略
    assigned_enemies, assigned_flags = set(), set()
    has_defender = False

    for i, player in enumerate(valid_players):
        action = actions[i]
        name = player.name

        # 强制防御检查
        if enemies_in_territory and not has_defender and i == 0:
            opp = find_best_opponent(player, enemies_in_territory, assigned_enemies, world, my_team)
            if opp:
                schedule[f"{name}schedule"] = (Strategy.DEFENCE, player.to_dict(), opp.to_dict())
                assigned_enemies.add(opp.name)
                has_defender = True
                continue

        if action == Strategy.DEFENCE.value:
            result = _assign_defence(player, opponents, assigned_enemies, world, my_team,
                                     enemy_flags, assigned_flags, prisoners)
            if result:
                schedule[f"{name}schedule"] = result
                if result[0] == Strategy.DEFENCE:
                    has_defender = True
                    if result[2]:
                        assigned_enemies.add(result[2].get('name', ''))

        elif action == Strategy.SCORING.value:
            result = _assign_scoring(player, world, my_team, enemy_flags, assigned_flags)
            if result:
                schedule[f"{name}schedule"] = result

        elif action == Strategy.SAVING.value:
            if prisoners:
                schedule[f"{name}schedule"] = (Strategy.SAVING, player.to_dict(), None)

    return schedule


def _extract_batch_states(players: List['Player'], world: 'World'):
    """批量提取状态特征"""
    states, valid_players = [], []
    for player in players:
        if player.is_in_prison:
            continue
        state = extract_state_features(player, world)
        if len(state) != 19:
            print(f"⚠️  警告：玩家 {player.name} 的状态维度错误: {len(state)}")
            continue
        states.append(state)
        valid_players.append(player)
    return states, valid_players


def _batch_inference(q_network, device, states) -> np.ndarray:
    """批量推理"""
    was_training = q_network.training
    q_network.eval()
    with torch.no_grad():
        tensor = torch.FloatTensor(np.array(states)).to(device)
        q_values = q_network(tensor)
        actions = q_values.argmax(dim=1).cpu().numpy()
    if was_training:
        q_network.train()
    return actions


def _assign_defence(player: 'Player', opponents, assigned_enemies, world, my_team,
                    enemy_flags, assigned_flags, prisoners):
    """分配防御策略"""
    opp = find_best_opponent(player, opponents, assigned_enemies, world, my_team)
    if opp:
        assigned_enemies.add(opp.name)
        return (Strategy.DEFENCE, player.to_dict(), opp.to_dict())

    # 无敌人可防，转为得分或救援
    if player.has_flag:
        targets = list(world.map.get_team_target_positions(my_team))
        if targets:
            return (Strategy.SCORING, player.to_dict(), targets[0].to_tuple())
    else:
        flag = find_best_flag(player, enemy_flags, assigned_flags)
        if flag:
            assigned_flags.add(flag.position.to_tuple())
            return (Strategy.SCORING, player.to_dict(), flag.to_dict())
        elif prisoners:
            return (Strategy.SAVING, player.to_dict(), None)
    return None


def _assign_scoring(player: 'Player', world, my_team, enemy_flags, assigned_flags):
    """分配得分策略"""
    if player.has_flag:
        targets = list(world.map.get_team_target_positions(my_team))
        if targets:
            return (Strategy.SCORING, player.to_dict(), targets[0].to_tuple())
    else:
        flag = find_best_flag(player, enemy_flags, assigned_flags)
        if flag:
            assigned_flags.add(flag.position.to_tuple())
            return (Strategy.SCORING, player.to_dict(), flag.to_dict())
    return None
