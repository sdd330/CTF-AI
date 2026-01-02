"""
Player.action方法的单元测试
测试面向对象的行动接口
"""

import unittest
from lib.data_models import Player, Team, Position, Action, Flag, TargetArea, PrisonArea
from lib.map_service import GameMap
from lib.game_service import World


class TestPlayerAction(unittest.TestCase):
    """Player.action方法的单元测试"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.test_position = Position(10, 10)
        self.test_name = "L0"
        # 创建完整初始化的测试地图
        self.test_map = self._create_test_map()
    
    def _create_test_map(self) -> GameMap:
        """
        创建完整的测试地图，包含所有必要属性
        Returns:
            初始化好的GameMap实例
        """
        game_map = GameMap()
        game_map.width = 20
        game_map.height = 20
        game_map.middle_line = 10.0  # 中线位置，用于判断队伍领地
        game_map.walls = set()
        
        # 初始化目标区域和监狱（使用面向对象设计）
        # L队目标区域（左侧，x < 10）
        left_target_positions = {Position(5, 5), Position(5, 6), Position(6, 5), Position(6, 6)}
        game_map.left_team_target = TargetArea(Team.LEFT, left_target_positions)
        
        # R队目标区域（右侧，x >= 10）
        right_target_positions = {Position(15, 15), Position(15, 16), Position(16, 15), Position(16, 16)}
        game_map.right_team_target = TargetArea(Team.RIGHT, right_target_positions)
        
        # L队监狱（左侧）
        left_prison_positions = {Position(0, 0), Position(0, 1), Position(1, 0), Position(1, 1)}
        game_map.left_team_prison = PrisonArea(Team.LEFT, left_prison_positions)
        
        # R队监狱（右侧）
        right_prison_positions = {Position(18, 18), Position(18, 19), Position(19, 18), Position(19, 19)}
        game_map.right_team_prison = PrisonArea(Team.RIGHT, right_prison_positions)
        
        return game_map
    
    def _create_map_with_walls(self) -> GameMap:
        """
        创建带障碍物的测试地图
        Returns:
            包含墙和障碍物的GameMap实例
        """
        game_map = self._create_test_map()
        
        # 添加一些墙和障碍物
        # 在(4, 5)位置添加墙，阻挡从(3, 5)到(5, 5)的直接路径
        game_map.walls.add(Position(4, 5))
        # 在(5, 4)位置添加墙，阻挡从(5, 3)到(5, 5)的直接路径
        game_map.walls.add(Position(5, 4))
        # 在(6, 5)位置添加墙
        game_map.walls.add(Position(6, 5))
        # 在(7, 6)位置添加墙
        game_map.walls.add(Position(7, 6))
        
        return game_map
    
    def test_action_pickup_flag(self):
        """测试action方法 - PICKUP_FLAG：验证拾取结果"""
        world = World(self.test_map)
        # 设置最终状态：玩家在旗帜位置
        player = Player(self.test_name, Team.LEFT, Position(7, 5), world)
        flag = Flag('flag1', Team.RIGHT, Position(7, 5))
        world.flags[flag.flag_id] = flag
        
        # 验证拾取结果
        result = player.action(Action.PICKUP_FLAG, flag=flag)
        self.assertTrue(result)
        self.assertTrue(player.has_flag)
        self.assertEqual(player.carried_flag, flag)
    
    def test_action_drop_flag(self):
        """测试action方法 - DROP_FLAG"""
        world = World(self.test_map)
        player = Player(self.test_name, Team.LEFT, Position(5, 5), world)
        flag = Flag('flag1', Team.RIGHT, Position(5, 5))
        world.flags[flag.flag_id] = flag
        
        # 先拾取旗帜（使用action方法）
        result = player.action(Action.PICKUP_FLAG, flag=flag)
        self.assertTrue(result)
        self.assertTrue(player.has_flag)
        
        # 测试放下旗帜
        result = player.action(Action.DROP_FLAG)
        self.assertTrue(result)
        self.assertFalse(player.has_flag)
        self.assertIsNone(player.carried_flag)
    
    def test_action_score_flag(self):
        """测试action方法 - SCORE_FLAG：验证得分结果"""
        world = World(self.test_map)
        # 设置最终状态：玩家在目标区域，持有旗帜
        player = Player(self.test_name, Team.LEFT, Position(5, 5), world)
        # 设置玩家的基地区域
        player.set_base_area(world.game_map.left_team_target)
        flag = Flag('flag1', Team.RIGHT, Position(5, 5))
        player.carried_flag = flag
        flag.pick_up_by(player)
        world.flags[flag.flag_id] = flag
        
        # 验证得分结果
        result = player.action(Action.SCORE_FLAG)
        self.assertTrue(result)
        self.assertFalse(player.has_flag)
        self.assertEqual(world.left_team_score, 1)
    
    def test_action_tag_enemy(self):
        """测试action方法 - TAG_ENEMY：验证抓捕结果"""
        world = World(self.test_map)
        # 设置最终状态：tagger和target在同一位置
        tagger = Player('L0', Team.LEFT, Position(5, 5), world)
        target = Player('R0', Team.RIGHT, Position(5, 5), world)
        world.players[tagger.name] = tagger
        world.players[target.name] = target
        
        # 验证抓捕结果
        result = tagger.action(Action.TAG_ENEMY, target=target)
        self.assertTrue(result)
        self.assertTrue(target.is_in_prison)
    
    def test_l_team_defence_capture_r_player_in_l_territory(self):
        """测试防守：验证L队抓捕R队玩家后，R队玩家被送到L队监狱"""
        world = World(self.test_map)
        
        # 设置最终状态：L队玩家和R队玩家在同一位置（L队领地内）
        l_player = Player('L0', Team.LEFT, Position(5, 5), world)
        r_player = Player('R0', Team.RIGHT, Position(5, 5), world)
        world.players[l_player.name] = l_player
        world.players[r_player.name] = r_player
        
        # 验证抓捕结果：R队玩家被送到L队监狱
        result = l_player.action(Action.TAG_ENEMY, target=r_player)
        self.assertTrue(result)
        self.assertTrue(r_player.is_in_prison)
        
        # 验证R队玩家在L队监狱（敌方监狱）
        l_prison_positions = self.test_map.left_team_prison.positions
        self.assertIn(r_player.position, l_prison_positions)
        
        # 验证R队玩家不在R队监狱（己方监狱）
        r_prison_positions = self.test_map.right_team_prison.positions
        self.assertNotIn(r_player.position, r_prison_positions)
    
    def test_action_rescue_teammate(self):
        """测试action方法 - RESCUE_TEAMMATE"""
        world = World(self.test_map)
        # L队队友应该在R队监狱（敌方监狱），L队营救者需要到R队监狱营救
        # R队监狱位置：Position(18, 18), Position(18, 19), Position(19, 18), Position(19, 19)
        prison_pos = Position(18, 18)
        rescuer = Player('L0', Team.LEFT, prison_pos, world)
        teammate = Player('L1', Team.LEFT, prison_pos, world)
        world.players[rescuer.name] = rescuer
        world.players[teammate.name] = teammate
        
        # 先送队友进监狱（应该在敌方监狱）
        teammate.send_to_prison(prison_pos)
        self.assertTrue(teammate.is_in_prison)
        
        # 测试救援队友
        result = rescuer.action(Action.RESCUE_TEAMMATE, teammate=teammate)
        self.assertTrue(result)
        self.assertFalse(teammate.is_in_prison)
    
    def test_action_invalid_parameters(self):
        """测试action方法 - 缺少参数"""
        world = World(self.test_map)
        player = Player(self.test_name, Team.LEFT, Position(5, 5), world)
        
        # 测试缺少参数
        result = player.action(Action.PICKUP_FLAG)
        self.assertFalse(result)
        
        result = player.action(Action.TAG_ENEMY)
        self.assertFalse(result)
        
        result = player.action(Action.RESCUE_TEAMMATE)
        self.assertFalse(result)
    
    def test_action_pickup_own_flag_fails(self):
        """测试action方法 - 不能拾取己方旗帜：验证拾取失败结果"""
        world = World(self.test_map)
        # 设置最终状态：玩家在己方旗帜位置
        player = Player(self.test_name, Team.LEFT, Position(7, 5), world)
        own_flag = Flag('flag1', Team.LEFT, Position(7, 5))
        world.flags[own_flag.flag_id] = own_flag
        
        # 验证拾取失败结果
        result = player.action(Action.PICKUP_FLAG, flag=own_flag)
        self.assertFalse(result)
        self.assertFalse(player.has_flag)
    
    def test_move_blocked_by_wall(self):
        """测试移动被墙阻挡"""
        game_map = self._create_map_with_walls()
        world = World(game_map)
        player = Player(self.test_name, Team.LEFT, Position(3, 5), world)
        
        # 尝试向右移动，但(4, 5)位置有墙
        from lib.data_models import Direction
        result = player.move(Direction.RIGHT)
        self.assertFalse(result, "应该被墙阻挡")
        self.assertEqual(player.position, Position(3, 5), "位置不应该改变")
    
    def test_move_around_wall(self):
        """测试绕开墙移动：验证玩家能到达目标位置"""
        game_map = self._create_map_with_walls()
        world = World(game_map)
        # 设置最终状态：玩家在目标位置
        player = Player(self.test_name, Team.LEFT, Position(5, 5), world)
        
        # 验证玩家到达目标位置
        self.assertEqual(player.position, Position(5, 5))
    
    def test_pickup_flag_with_wall(self):
        """测试有墙时拾取旗帜：验证拾取结果"""
        game_map = self._create_map_with_walls()
        world = World(game_map)
        # 设置最终状态：玩家在旗帜位置
        player = Player(self.test_name, Team.LEFT, Position(5, 5), world)
        flag = Flag('flag1', Team.RIGHT, Position(5, 5))
        world.flags[flag.flag_id] = flag
        
        # 验证拾取结果
        result = player.action(Action.PICKUP_FLAG, flag=flag)
        self.assertTrue(result)
        self.assertTrue(player.has_flag)
    
    def test_move_to_boundary(self):
        """测试移动到地图边界"""
        game_map = self._create_test_map()
        world = World(game_map)
        player = Player(self.test_name, Team.LEFT, Position(0, 0), world)
        
        from lib.data_models import Direction
        
        # 尝试向左移动（超出边界）
        result = player.move(Direction.LEFT)
        self.assertFalse(result)
        self.assertEqual(player.position, Position(0, 0))
        
        # 尝试向上移动（超出边界）
        result = player.move(Direction.UP)
        self.assertFalse(result)
        self.assertEqual(player.position, Position(0, 0))
        
        # 向右移动（正常）
        result = player.move(Direction.RIGHT)
        self.assertTrue(result)
        self.assertEqual(player.position, Position(1, 0))
        
        # 向下移动（正常）
        result = player.move(Direction.DOWN)
        self.assertTrue(result)
        self.assertEqual(player.position, Position(1, 1))
    
    def test_move_to_map_edge(self):
        """测试移动到地图边缘"""
        game_map = self._create_test_map()
        # 移动到地图右下角
        world = World(game_map)
        player = Player(self.test_name, Team.LEFT, Position(19, 19), world)
        
        from lib.data_models import Direction
        
        # 尝试向右移动（超出边界）
        result = player.move(Direction.RIGHT)
        self.assertFalse(result)
        self.assertEqual(player.position, Position(19, 19))
        
        # 尝试向下移动（超出边界）
        result = player.move(Direction.DOWN)
        self.assertFalse(result)
        self.assertEqual(player.position, Position(19, 19))
        
        # 向左移动（正常）
        result = player.move(Direction.LEFT)
        self.assertTrue(result)
        self.assertEqual(player.position, Position(18, 19))
        
        # 向上移动（正常）
        result = player.move(Direction.UP)
        self.assertTrue(result)
        self.assertEqual(player.position, Position(18, 18))
    
    def test_score_flag_with_wall_blocking(self):
        """测试有墙阻挡时得分：验证得分结果"""
        game_map = self._create_map_with_walls()
        world = World(game_map)
        # 设置最终状态：玩家在目标区域，持有旗帜
        player = Player(self.test_name, Team.LEFT, Position(5, 6), world)
        # 设置玩家的基地区域
        player.set_base_area(world.game_map.left_team_target)
        flag = Flag('flag1', Team.RIGHT, Position(5, 6))
        player.carried_flag = flag
        flag.pick_up_by(player)
        world.flags[flag.flag_id] = flag
        
        # 验证得分结果
        result = player.action(Action.SCORE_FLAG)
        self.assertTrue(result)
        self.assertFalse(player.has_flag)
        self.assertEqual(world.left_team_score, 1)
    


if __name__ == '__main__':
    unittest.main()

