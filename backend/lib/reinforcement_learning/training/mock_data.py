"""
模拟数据生成器
用于离线训练时生成模拟的游戏初始化数据
"""

import random
import math


def create_mock_init_data(map_width=20, map_height=20, num_players=3, num_flags=9):
    """
    创建模拟的游戏初始化数据（旗帜在己方半场随机摆放）

    Args:
        map_width: 地图宽度
        map_height: 地图高度
        num_players: 每队玩家数
        num_flags: 每队旗帜数

    Returns:
        初始化数据字典
    """
    middle_line = map_width / 2.0
    l_max_x = int(middle_line - 0.1)
    r_min_x = math.ceil(middle_line)

    l_flags = [
        {"posX": random.randint(2, l_max_x), "posY": random.randint(1, map_height - 3),
         "canPickup": False, "pickedUp": False}
        for _ in range(num_flags)
    ]
    r_flags = [
        {"posX": random.randint(r_min_x, map_width - 2), "posY": random.randint(1, map_height - 3),
         "canPickup": True, "pickedUp": False}
        for _ in range(num_flags)
    ]

    return {
        "myteamName": "L",
        "map": {
            "width": map_width, "height": map_height,
            "walls": [
                {"x": 5, "y": 5}, {"x": 5, "y": 6}, {"x": 6, "y": 5},
                {"x": 15, "y": 15}, {"x": 15, "y": 14}, {"x": 14, "y": 15}
            ]
        },
        "myteamTarget": [{"x": 0, "y": 0}, {"x": 0, "y": 1}, {"x": 1, "y": 0}, {"x": 1, "y": 1}],
        "opponentTarget": [{"x": 18, "y": 18}, {"x": 18, "y": 19}, {"x": 19, "y": 18}, {"x": 19, "y": 19}],
        "myteamPrison": [{"x": 18, "y": 0}, {"x": 18, "y": 1}, {"x": 19, "y": 0}, {"x": 19, "y": 1}],
        "opponentPrison": [{"x": 0, "y": 18}, {"x": 0, "y": 19}, {"x": 1, "y": 18}, {"x": 1, "y": 19}],
        "myteamPlayer": [
            {"name": f"L{i}", "posX": 2, "posY": 2 + i, "hasFlag": False, "inPrison": False}
            for i in range(num_players)
        ],
        "opponentPlayer": [
            {"name": f"R{i}", "posX": 17, "posY": 17 - i, "hasFlag": False, "inPrison": False}
            for i in range(num_players)
        ],
        "myteamFlag": l_flags,
        "opponentFlag": r_flags,
        "team": {"name": "L", "numPlayers": num_players, "numFlags": num_flags}
    }
