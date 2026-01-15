"""
重构后的服务器主文件
使用面向对象的设计，代码更整洁、一致和可读
"""

import importlib
import lib.game_engine

# Force the reload manually
importlib.reload(lib.game_engine)

# Re-import the specific classes/functions
from lib.game_engine import (
    GameMap,
    World,
    run_game_server,
)

# Initialize game objects
game_map = GameMap()
world = World(game_map)


def start_game(req: dict) -> None:
    """
    游戏开始时调用
    Args:
        req: 游戏初始化请求
    """
    world.init(req)
    print(f"Map initialized: {game_map.width}x{game_map.height}")


def plan_next_actions(req: dict) -> dict:
    """
    每帧调用，计划下一步动作
    Args:
        req: 游戏状态请求
    Returns:
        包含 actions 和 paths 的字典
    """
    # 获取队伍名称
    team_name = world.my_team_name or "未知"
    team_prefix = f"{team_name}队"
    
    # 直接使用 world.plan_actions
    result = world.plan_actions(req)
    
    # 确保返回正确的格式
    if not isinstance(result, dict):
        print(f"⚠️  [{team_prefix}] [server] plan_actions 返回了非字典类型: {type(result)}", flush=True)
        return {"actions": {}, "paths": {}}
    
    actions = result.get("actions", {})
    paths = result.get("paths", {})
    timings = result.get("timings", {})
    
    if not actions:
        print(f"⚠️  [{team_prefix}] [server] plan_actions 返回空动作字典", flush=True)
    else:
        print(f"✅ [{team_prefix}] [server] 返回 {len(actions)} 个动作: {list(actions.keys())[:5]}...", flush=True)
    
    # 静默处理耗时信息，减少日志输出（只在总耗时超过阈值时输出）
    # 如果需要调试，可以取消注释下面的代码
    # if timings:
    #     for player_name, player_timings in timings.items():
    #         if isinstance(player_timings, dict):
    #             total = player_timings.get('total', 0)
    #             # 只在总耗时超过 50ms 时输出（性能问题）
    #             if total > 50:
    #                 algorithm = player_timings.get('algorithm', 'unknown')
    #                 details = []
    #                 if 'influence_zone' in player_timings:
    #                     details.append(f"影响区域: {player_timings['influence_zone']:.2f}ms")
    #                 if 'weight_map' in player_timings:
    #                     details.append(f"权重地图: {player_timings['weight_map']:.2f}ms")
    #                 if 'pathfinding' in player_timings:
    #                     details.append(f"路径查找: {player_timings['pathfinding']:.2f}ms")
    #                 if 'obstacle_filter' in player_timings:
    #                     details.append(f"障碍过滤: {player_timings['obstacle_filter']:.2f}ms")
    #                 
    #                 detail_str = ', '.join(details) if details else '无详情'
    #                 print(f"⏱️  [{team_prefix}] [server] {player_name} ({algorithm}): 总耗时 {total:.2f}ms ({detail_str})", flush=True)
    #         else:
    #             if player_timings > 50:
    #                 print(f"⏱️  [{team_prefix}] [server] {player_name}: {player_timings:.2f}ms", flush=True)
    
    return {"actions": actions, "paths": paths, "timings": timings}


def game_over(req: dict) -> None:
    """
    游戏结束时调用
    Args:
        req: 游戏结束请求
    """
    print("Game Over!")


async def main():
    """主函数"""
    import sys
    import asyncio
    
    if len(sys.argv) != 2:
        print(f"Usage: python3 {sys.argv[0]} <port>")
        print(f"Example: python3 {sys.argv[0]} 8080")
        sys.exit(1)
    
    port = int(sys.argv[1])
    print(f"AI backend running on port {port} ...", flush=True)
    print(f"Log file: /tmp/backend_l.log", flush=True)
    
    try:
        await run_game_server(port, start_game, plan_next_actions, game_over)
    except Exception as e:
        print(f"Server Stopped: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
