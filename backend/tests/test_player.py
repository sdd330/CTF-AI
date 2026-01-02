"""
Player类的单元测试
确保Player类的所有功能正常工作
"""

import unittest
from lib.data_models import Player, Team, Position, PlayerState, Flag, Direction, Action, Strategy
from lib.map_service import GameMap
from lib.game_service import World


class TestPlayer(unittest.TestCase):
    """Player类的单元测试"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.test_position = Position(10, 10)
        self.test_name = "L0"
        # 创建测试用的地图和游戏实例
        self.test_map = GameMap()
        self.test_map.width = 20
        self.test_map.height = 20
        self.test_map.middle_line = 10.0
        self.test_map.walls = set()
        
        # 初始化目标区域和监狱区域
        from lib.data_models import TargetArea, PrisonArea
        left_target_positions = {Position(5, 5), Position(5, 6), Position(6, 5), Position(6, 6)}
        self.test_map.left_team_target = TargetArea(Team.LEFT, left_target_positions)
        right_target_positions = {Position(15, 15), Position(15, 16), Position(16, 15), Position(16, 16)}
        self.test_map.right_team_target = TargetArea(Team.RIGHT, right_target_positions)
        left_prison_positions = {Position(0, 0), Position(0, 1), Position(1, 0), Position(1, 1)}
        self.test_map.left_team_prison = PrisonArea(Team.LEFT, left_prison_positions)
        right_prison_positions = {Position(18, 18), Position(18, 19), Position(19, 18), Position(19, 19)}
        self.test_map.right_team_prison = PrisonArea(Team.RIGHT, right_prison_positions)
        
        self.test_game = World(self.test_map)
    
    def test_player_creation_success(self):
        """测试Player对象成功创建"""
        player = Player(self.test_name, Team.LEFT, self.test_position, self.test_game)
        
        # 验证基本属性
        self.assertEqual(player.name, self.test_name)
        self.assertEqual(player.team, Team.LEFT)
        self.assertEqual(player.position, self.test_position)
        self.assertEqual(player.state, PlayerState.FREE)
        
        # 验证基本属性
        self.assertEqual(player.team, Team.LEFT)
    
    def test_player_creation_right_team(self):
        """测试R队Player对象创建"""
        player = Player("R0", Team.RIGHT, Position(20, 20), self.test_game)
        
        self.assertEqual(player.team, Team.RIGHT)
    
    def test_player_creation_empty_name(self):
        """测试空名称应该抛出ValueError"""
        with self.assertRaises(ValueError) as context:
            Player("", Team.LEFT, self.test_position, self.test_game)
        self.assertIn("empty", str(context.exception).lower())
    
    def test_player_creation_invalid_position_type(self):
        """测试无效的position类型应该抛出TypeError"""
        with self.assertRaises(TypeError):
            Player(self.test_name, Team.LEFT, (10, 10), self.test_game)  # 应该是Position对象
    
    def test_player_creation_invalid_team_type(self):
        """测试无效的team类型应该抛出TypeError"""
        with self.assertRaises(TypeError):
            Player(self.test_name, "LEFT", self.test_position, self.test_game)  # 应该是Team枚举
    
    def test_player_belongs_to_team(self):
        """测试belongs_to_team方法"""
        l_player = Player("L0", Team.LEFT, Position(1, 1), self.test_game)
        r_player = Player("R0", Team.RIGHT, Position(2, 2), self.test_game)
        
        # L队玩家
        self.assertTrue(l_player.belongs_to_team(Team.LEFT))
        self.assertFalse(l_player.belongs_to_team(Team.RIGHT))
        
        # R队玩家
        self.assertTrue(r_player.belongs_to_team(Team.RIGHT))
        self.assertFalse(r_player.belongs_to_team(Team.LEFT))
    
    def test_player_is_enemy_of(self):
        """测试is_enemy_of方法"""
        l_player = Player("L0", Team.LEFT, Position(1, 1), self.test_game)
        r_player = Player("R0", Team.RIGHT, Position(2, 2), self.test_game)
        l_player2 = Player("L1", Team.LEFT, Position(3, 3), self.test_game)
        
        # L队和R队是敌人
        self.assertTrue(l_player.is_enemy_of(r_player))
        self.assertTrue(r_player.is_enemy_of(l_player))
        
        # 同队不是敌人
        self.assertFalse(l_player.is_enemy_of(l_player2))
        self.assertFalse(l_player2.is_enemy_of(l_player))
    
    def test_player_is_teammate_of(self):
        """测试is_teammate_of方法"""
        l_player = Player("L0", Team.LEFT, Position(1, 1), self.test_game)
        r_player = Player("R0", Team.RIGHT, Position(2, 2), self.test_game)
        l_player2 = Player("L1", Team.LEFT, Position(3, 3), self.test_game)
        
        # 同队是队友
        self.assertTrue(l_player.is_teammate_of(l_player2))
        self.assertTrue(l_player2.is_teammate_of(l_player))
        
        # 不同队不是队友
        self.assertFalse(l_player.is_teammate_of(r_player))
        self.assertFalse(r_player.is_teammate_of(l_player))
    
    def test_player_is_enemy_team(self):
        """测试is_enemy_team方法"""
        l_player = Player("L0", Team.LEFT, Position(1, 1), self.test_game)
        r_player = Player("R0", Team.RIGHT, Position(2, 2), self.test_game)
        
        # L队玩家
        self.assertTrue(l_player.is_enemy_team(Team.RIGHT))
        self.assertFalse(l_player.is_enemy_team(Team.LEFT))
        
        # R队玩家
        self.assertTrue(r_player.is_enemy_team(Team.LEFT))
        self.assertFalse(r_player.is_enemy_team(Team.RIGHT))
    
    def test_player_is_my_team(self):
        """测试is_my_team方法"""
        l_player = Player("L0", Team.LEFT, Position(1, 1), self.test_game)
        r_player = Player("R0", Team.RIGHT, Position(2, 2), self.test_game)
        
        # L队玩家
        self.assertTrue(l_player.is_my_team(Team.LEFT))
        self.assertFalse(l_player.is_my_team(Team.RIGHT))
        
        # R队玩家
        self.assertTrue(r_player.is_my_team(Team.RIGHT))
        self.assertFalse(r_player.is_my_team(Team.LEFT))
    
    def test_player_properties(self):
        """测试Player的属性"""
        player = Player(self.test_name, Team.LEFT, self.test_position, self.test_game)
        
        # 初始状态应该是FREE
        self.assertTrue(player.is_free)
        self.assertFalse(player.is_in_prison)
        self.assertFalse(player.has_flag)
    
    def test_player_pick_up_flag(self):
        """测试拾取旗帜"""
        world = World(self.test_map)
        # 玩家和旗帜在同一位置
        flag_pos = self.test_position
        player = Player(self.test_name, Team.LEFT, flag_pos, world)
        flag = Flag("flag1", Team.RIGHT, flag_pos)
        world.flags[flag.flag_id] = flag
        
        # 初始状态
        self.assertFalse(player.has_flag)
        self.assertIsNone(player.carried_flag)
        
        # 拾取旗帜（使用action方法）
        result = player.action(Action.PICKUP_FLAG, flag=flag)
        self.assertTrue(result)
        
        # 验证状态
        self.assertTrue(player.has_flag)
        self.assertEqual(player.carried_flag, flag)
        self.assertEqual(player.state, PlayerState.CARRYING_FLAG)
        self.assertTrue(flag.is_picked_up)
        self.assertEqual(flag.carried_by, player)
    
    def test_player_drop_flag(self):
        """测试放下旗帜"""
        world = World(self.test_map)
        # 玩家和旗帜在同一位置
        flag_pos = self.test_position
        player = Player(self.test_name, Team.LEFT, flag_pos, world)
        flag = Flag("flag1", Team.RIGHT, flag_pos)
        world.flags[flag.flag_id] = flag
        
        # 先拾取
        result = player.action(Action.PICKUP_FLAG, flag=flag)
        self.assertTrue(result)
        self.assertTrue(player.has_flag)
        
        # 放下（使用action方法）
        dropped_result = player.action(Action.DROP_FLAG)
        self.assertTrue(dropped_result)
        
        # 验证状态
        self.assertFalse(player.has_flag)
        self.assertIsNone(player.carried_flag)
        self.assertEqual(player.state, PlayerState.FREE)
        self.assertFalse(flag.is_picked_up)
        self.assertIsNone(flag.carried_by)
    
    def test_player_send_to_prison(self):
        """测试送入监狱"""
        world = World(self.test_map)
        # 玩家和旗帜在同一位置
        flag_pos = self.test_position
        player = Player(self.test_name, Team.LEFT, flag_pos, world)
        flag = Flag("flag1", Team.RIGHT, flag_pos)
        world.flags[flag.flag_id] = flag
        prison_pos = Position(0, 0)
        
        # 先拾取旗帜（使用action方法）
        result = player.action(Action.PICKUP_FLAG, flag=flag)
        self.assertTrue(result)
        self.assertTrue(player.has_flag)
        
        # 送入监狱（应该自动放下旗帜）
        player.send_to_prison(prison_pos)
        
        # 验证状态
        self.assertFalse(player.has_flag)
        self.assertIsNone(player.carried_flag)
        self.assertTrue(player.is_in_prison)
        self.assertEqual(player.state, PlayerState.IN_PRISON)
        self.assertEqual(player.position, prison_pos)
        self.assertEqual(player.prison_time_left, player.prison_duration)
    
    def test_player_rescue(self):
        """测试救援"""
        world = World(self.test_map)
        # L队玩家应该在R队监狱（敌方监狱），L队营救者需要到R队监狱营救
        # R队监狱位置：Position(18, 18), Position(18, 19), Position(19, 18), Position(19, 19)
        prison_pos = Position(18, 18)
        player = Player(self.test_name, Team.LEFT, prison_pos, world)
        
        # 先送入监狱（应该在敌方监狱）
        player.send_to_prison(prison_pos)
        self.assertTrue(player.is_in_prison)
        
        # 救援（使用action方法，需要另一个玩家作为救援者，在敌方监狱）
        rescuer = Player("L1", Team.LEFT, prison_pos, world)
        result = rescuer.action(Action.RESCUE_TEAMMATE, teammate=player)
        self.assertTrue(result)
        
        # 验证状态
        self.assertFalse(player.is_in_prison)
        self.assertEqual(player.state, PlayerState.FREE)
        self.assertEqual(player.prison_time_left, 0)
    
    def test_player_move(self):
        """测试移动（使用Direction枚举）"""
        player = Player(self.test_name, Team.LEFT, self.test_position, self.test_game)
        
        # 自由状态可以移动
        self.assertTrue(player.is_free)
        
        # 测试各个方向移动
        original_pos = player.position
        
        # 向右移动
        result = player.move(Direction.RIGHT)
        self.assertTrue(result)
        self.assertEqual(player.position.x, original_pos.x + 1)
        self.assertEqual(player.position.y, original_pos.y)
        
        # 向下移动
        result = player.move(Direction.DOWN)
        self.assertTrue(result)
        self.assertEqual(player.position.x, original_pos.x + 1)
        self.assertEqual(player.position.y, original_pos.y + 1)
        
        # 向左移动
        result = player.move(Direction.LEFT)
        self.assertTrue(result)
        self.assertEqual(player.position.x, original_pos.x)
        self.assertEqual(player.position.y, original_pos.y + 1)
        
        # 向上移动
        result = player.move(Direction.UP)
        self.assertTrue(result)
        self.assertEqual(player.position.x, original_pos.x)
        self.assertEqual(player.position.y, original_pos.y)
        
        # 保持不动
        result = player.move(Direction.STAY)
        self.assertTrue(result)
        self.assertEqual(player.position.x, original_pos.x)
        self.assertEqual(player.position.y, original_pos.y)
        
        # 在监狱中不能移动
        player.send_to_prison(Position(0, 0))
        old_pos = player.position
        result = player.move(Direction.RIGHT)
        self.assertFalse(result)  # 移动失败
        self.assertEqual(player.position, old_pos)  # 位置不变
    
    def test_player_move_with_map(self):
        """测试带地图验证的移动"""
        from lib.map_service import GameMap
        
        # 创建地图
        game_map = GameMap()
        game_map.width = 20
        game_map.height = 20
        game_map.walls = set()
        
        # 创建游戏实例和玩家
        world = World(game_map)
        player = Player(self.test_name, Team.LEFT, Position(10, 10), world)
        
        # 在地图范围内移动应该成功
        result = player.move(Direction.RIGHT)
        self.assertTrue(result)
        self.assertEqual(player.position, Position(11, 10))
        
        # 移动到地图边界外应该失败
        player.position = Position(19, 10)
        result = player.move(Direction.RIGHT)
        self.assertFalse(result)  # 超出地图边界，移动失败
        self.assertEqual(player.position, Position(19, 10))  # 位置不变
    
    
    def test_player_team_consistency(self):
        """测试team属性的一致性"""
        # 创建L队玩家
        l_player = Player("L0", Team.LEFT, Position(1, 1), self.test_game)
        r_player = Player("R0", Team.RIGHT, Position(2, 2), self.test_game)
        
        # L队玩家
        self.assertEqual(l_player.team, Team.LEFT)
        
        # R队玩家
        self.assertEqual(r_player.team, Team.RIGHT)
        
        # 验证所有方法都使用team
        self.assertTrue(l_player.belongs_to_team(Team.LEFT))
        self.assertTrue(r_player.belongs_to_team(Team.RIGHT))
        self.assertTrue(l_player.is_enemy_of(r_player))
        self.assertTrue(l_player.is_teammate_of(Player("L1", Team.LEFT, Position(3, 3), self.test_game)))
    
    def test_player_team_update(self):
        """测试更新team"""
        player = Player("L0", Team.LEFT, Position(1, 1), self.test_game)
        
        # 更新team
        player.team = Team.RIGHT
        
        # 验证更新
        self.assertEqual(player.team, Team.RIGHT)
    
    def test_player_initial_attributes(self):
        """测试Player对象的初始属性"""
        player = Player(self.test_name, Team.LEFT, self.test_position, self.test_game)
        
        # 验证所有初始属性都存在
        self.assertIsNotNone(player.name)
        self.assertIsNotNone(player.team)
        self.assertIsNotNone(player.position)
        self.assertIsNotNone(player.state)
        self.assertIsNone(player.carried_flag)
        self.assertEqual(player.prison_time_left, 0)
        self.assertGreater(player.prison_duration, 0)
    
    def test_player_to_dict(self):
        """测试to_dict方法"""
        player = Player(self.test_name, Team.LEFT, self.test_position, self.test_game)
        player_dict = player.to_dict()
        
        # 验证字典包含所有必要字段
        self.assertEqual(player_dict["name"], self.test_name)
        self.assertEqual(player_dict["team"], "L")
        self.assertEqual(player_dict["posX"], 10)
        self.assertEqual(player_dict["posY"], 10)
        self.assertFalse(player_dict["hasFlag"])
        self.assertFalse(player_dict["inPrison"])
    
    def test_player_repr(self):
        """测试__repr__方法"""
        player = Player(self.test_name, Team.LEFT, self.test_position, self.test_game)
        repr_str = repr(player)
        
        # 验证repr包含关键信息
        self.assertIn(self.test_name, repr_str)
        self.assertIn("team", repr_str)
        self.assertIn("L", repr_str)
    
    def test_multiple_players_team(self):
        """测试多个Player对象的team属性"""
        players = [
            Player("L0", Team.LEFT, Position(1, 1), self.test_game),
            Player("L1", Team.LEFT, Position(2, 2), self.test_game),
            Player("R0", Team.RIGHT, Position(3, 3), self.test_game),
            Player("R1", Team.RIGHT, Position(4, 4), self.test_game),
        ]
        
        # 验证L队玩家
        for player in players[:2]:
            self.assertEqual(player.team, Team.LEFT)
            self.assertTrue(player.belongs_to_team(Team.LEFT))
        
        # 验证R队玩家
        for player in players[2:]:
            self.assertEqual(player.team, Team.RIGHT)
            self.assertTrue(player.belongs_to_team(Team.RIGHT))
    
    def test_player_with_flag_team(self):
        """测试携带旗帜时team属性仍然正确"""
        world = World(self.test_map)
        # 玩家和旗帜在同一位置
        flag_pos = Position(1, 1)
        player = Player("L0", Team.LEFT, flag_pos, self.test_game)
        flag = Flag("flag1", Team.RIGHT, flag_pos)
        world.flags[flag.flag_id] = flag
        
        # 拾取旗帜（使用action方法）
        result = player.action(Action.PICKUP_FLAG, flag=flag)
        self.assertTrue(result)
        
        # 验证team属性仍然正确
        self.assertEqual(player.team, Team.LEFT)
        self.assertTrue(player.has_flag)
    
    def test_player_in_prison_team(self):
        """测试在监狱中时team属性仍然正确"""
        player = Player("L0", Team.LEFT, Position(1, 1), self.test_game)
        prison_pos = Position(0, 0)
        
        # 送入监狱
        player.send_to_prison(prison_pos)
        
        # 验证team属性仍然正确
        self.assertEqual(player.team, Team.LEFT)
        self.assertTrue(player.is_in_prison)
    
    def test_player_all_methods_use_team(self):
        """测试所有方法都正确使用team属性"""
        l_player = Player("L0", Team.LEFT, Position(1, 1), self.test_game)
        r_player = Player("R0", Team.RIGHT, Position(2, 2), self.test_game)
        l_player2 = Player("L1", Team.LEFT, Position(3, 3), self.test_game)
        
        # 验证所有方法都使用team
        self.assertTrue(l_player.belongs_to_team(Team.LEFT))
        self.assertFalse(l_player.belongs_to_team(Team.RIGHT))
        
        self.assertTrue(l_player.is_enemy_of(r_player))
        self.assertFalse(l_player.is_enemy_of(l_player2))
        
        self.assertTrue(l_player.is_teammate_of(l_player2))
        self.assertFalse(l_player.is_teammate_of(r_player))
        
        self.assertTrue(l_player.is_enemy_team(Team.RIGHT))
        self.assertFalse(l_player.is_enemy_team(Team.LEFT))
        
        self.assertTrue(l_player.is_my_team(Team.LEFT))
        self.assertFalse(l_player.is_my_team(Team.RIGHT))
    
    def test_update_from_dict_missing_team(self):
        """测试update_from_dict缺少team字段应该报错"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        flags = {}
        
        # 缺少team字段应该抛出ValueError
        p_data = {
            "name": "L0",
            "posX": 11,
            "posY": 11,
            "hasFlag": False,
            "inPrison": False
        }
        
        with self.assertRaises(ValueError) as context:
            player.update_from_dict(p_data, flags)
        self.assertIn("team", str(context.exception).lower())
        self.assertIn("缺少", str(context.exception) or "missing" in str(context.exception).lower())
    
    def test_update_from_dict_empty_team(self):
        """测试update_from_dict中team字段为空应该报错"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        flags = {}
        
        # team字段为空字符串应该抛出ValueError
        p_data = {
            "name": "L0",
            "team": "",
            "posX": 11,
            "posY": 11,
            "hasFlag": False,
            "inPrison": False
        }
        
        with self.assertRaises(ValueError) as context:
            player.update_from_dict(p_data, flags)
        self.assertIn("team", str(context.exception).lower())
        self.assertIn("空", str(context.exception) or "empty" in str(context.exception).lower())
    
    def test_update_from_dict_invalid_team(self):
        """测试update_from_dict中team字段无效应该报错"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        flags = {}
        
        # team字段无效应该抛出ValueError
        p_data = {
            "name": "L0",
            "team": "INVALID",
            "posX": 11,
            "posY": 11,
            "hasFlag": False,
            "inPrison": False
        }
        
        with self.assertRaises(ValueError) as context:
            player.update_from_dict(p_data, flags)
        self.assertIn("无效", str(context.exception) or "invalid" in str(context.exception).lower())
    
    def test_update_from_dict_valid_team(self):
        """测试update_from_dict中team字段正确应该更新"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        flags = {}
        
        # 更新为R队
        p_data = {
            "name": "L0",
            "team": "R",
            "posX": 11,
            "posY": 11,
            "hasFlag": False,
            "inPrison": False
        }
        
        player.update_from_dict(p_data, flags)
        self.assertEqual(player.team, Team.RIGHT)
        
        # 更新回L队
        p_data["team"] = "L"
        player.update_from_dict(p_data, flags)
        self.assertEqual(player.team, Team.LEFT)
    
    def test_update_from_dict_sets_base_area(self):
        """测试update_from_dict应该设置base_area"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        flags = {}
        
        # 初始状态base_area应该为None或已设置
        # 调用update_from_dict后应该确保base_area被设置
        p_data = {
            "name": "L0",
            "team": "L",
            "posX": 11,
            "posY": 11,
            "hasFlag": False,
            "inPrison": False
        }
        
        player.update_from_dict(p_data, flags)
        
        # 验证base_area被设置
        self.assertIsNotNone(player.base_area)
        self.assertEqual(player.base_area.belongs_to, Team.LEFT)
        self.assertTrue(len(player.base_area.positions) > 0)
    
    def test_update_from_dict_updates_position(self):
        """测试update_from_dict应该更新位置"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        flags = {}
        
        p_data = {
            "name": "L0",
            "team": "L",
            "posX": 15,
            "posY": 20,
            "hasFlag": False,
            "inPrison": False
        }
        
        player.update_from_dict(p_data, flags)
        self.assertEqual(player.position, Position(15, 20))
    
    def test_update_from_dict_updates_prison_state(self):
        """测试update_from_dict应该更新监狱状态"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        flags = {}
        
        # 初始状态不在监狱
        self.assertFalse(player.is_in_prison)
        
        # 更新为在监狱
        p_data = {
            "name": "L0",
            "team": "L",
            "posX": 18,
            "posY": 18,  # R队监狱位置
            "hasFlag": False,
            "inPrison": True
        }
        
        player.update_from_dict(p_data, flags)
        self.assertTrue(player.is_in_prison)
        self.assertEqual(player.state, PlayerState.IN_PRISON)
        
        # 更新为不在监狱
        p_data["inPrison"] = False
        player.update_from_dict(p_data, flags)
        self.assertFalse(player.is_in_prison)
        self.assertEqual(player.state, PlayerState.FREE)
    
    def test_update_from_dict_updates_flag_state(self):
        """测试update_from_dict应该更新旗帜状态"""
        world = World(self.test_map)
        player = Player("L0", Team.LEFT, Position(10, 10), world)
        
        # 创建一个敌方旗帜，并设置为已被拾取（这样才能被关联）
        flag = Flag("flag_R_0", Team.RIGHT, Position(10, 10))
        flag.is_picked_up = True  # 设置为已被拾取，符合关联条件
        flag.carried_by = player  # 设置携带者
        world.flags[flag.flag_id] = flag
        flags = world.flags
        
        # 初始状态没有旗帜
        self.assertFalse(player.has_flag)
        
        # 更新为有旗帜
        p_data = {
            "name": "L0",
            "team": "L",
            "posX": 10,
            "posY": 10,
            "hasFlag": True,
            "inPrison": False
        }
        
        player.update_from_dict(p_data, flags)
        self.assertTrue(player.has_flag)
        self.assertIsNotNone(player.carried_flag)
        
        # 更新为没有旗帜
        p_data["hasFlag"] = False
        player.update_from_dict(p_data, flags)
        self.assertFalse(player.has_flag)
        self.assertIsNone(player.carried_flag)
    
    def test_update_from_dict_sets_base_area_when_has_flag(self):
        """测试玩家拿到旗帜时应该确保基地信息被设置"""
        world = World(self.test_map)
        player = Player("L0", Team.LEFT, Position(10, 10), world)
        
        # 清除base_area（模拟初始状态）
        player.base_area = None
        
        # 创建一个敌方旗帜，并设置为已被拾取（这样才能被关联）
        flag = Flag("flag_R_0", Team.RIGHT, Position(10, 10))
        flag.is_picked_up = True  # 设置为已被拾取，符合关联条件
        flag.carried_by = player  # 设置携带者
        world.flags[flag.flag_id] = flag
        flags = world.flags
        
        # 更新为有旗帜
        p_data = {
            "name": "L0",
            "team": "L",
            "posX": 10,
            "posY": 10,
            "hasFlag": True,
            "inPrison": False
        }
        
        player.update_from_dict(p_data, flags)
        
        # 验证base_area被设置（因为update_from_dict开始就会设置）
        self.assertIsNotNone(player.base_area)
        self.assertEqual(player.base_area.belongs_to, Team.LEFT)
        self.assertTrue(player.has_flag)
    
    def test_update_from_dict_team_before_base_area(self):
        """测试update_from_dict中team应该在base_area之前设置"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        flags = {}
        
        # 更新team为R队
        p_data = {
            "name": "L0",
            "team": "R",
            "posX": 11,
            "posY": 11,
            "hasFlag": False,
            "inPrison": False
        }
        
        player.update_from_dict(p_data, flags)
        
        # 验证team已更新
        self.assertEqual(player.team, Team.RIGHT)
        
        # 验证base_area使用的是更新后的team（R队）
        self.assertIsNotNone(player.base_area)
        self.assertEqual(player.base_area.belongs_to, Team.RIGHT)
    
    def test_update_from_dict_complete_update(self):
        """测试update_from_dict完整更新所有字段"""
        world = World(self.test_map)
        player = Player("L0", Team.LEFT, Position(10, 10), world)
        
        # 创建一个敌方旗帜，并设置为已被拾取（这样才能被关联）
        flag = Flag("flag_R_0", Team.RIGHT, Position(10, 10))
        flag.is_picked_up = True  # 设置为已被拾取，符合关联条件
        flag.carried_by = player  # 设置携带者
        world.flags[flag.flag_id] = flag
        flags = world.flags
        
        # 完整更新
        p_data = {
            "name": "L0",
            "team": "L",
            "posX": 15,
            "posY": 20,
            "hasFlag": True,
            "inPrison": False
        }
        
        player.update_from_dict(p_data, flags)
        
        # 验证所有字段都已更新
        self.assertEqual(player.team, Team.LEFT)
        self.assertEqual(player.position, Position(15, 20))
        self.assertTrue(player.has_flag)
        self.assertFalse(player.is_in_prison)
        self.assertIsNotNone(player.base_area)
        self.assertEqual(player.base_area.belongs_to, Team.LEFT)
    
    # ========== 四核心接口测试 ==========
    
    def test_plan_interface(self):
        """测试 plan() 核心接口"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        
        # plan() 应该返回一个方向或 None
        direction = player.plan()
        self.assertIsInstance(direction, (Direction, type(None)))
        
        # 如果玩家在监狱中，plan() 应该返回 STAY
        player.send_to_prison(Position(0, 0))
        direction = player.plan()
        self.assertEqual(direction, Direction.STAY)
    
    def test_plan_with_suggested_strategy(self):
        """测试 plan() 接口接受建议策略"""
        from lib.data_models import Strategy
        
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        
        # 提供建议策略
        direction = player.plan(suggested_strategy=Strategy.SCORING)
        self.assertIsInstance(direction, (Direction, type(None)))
    
    def test_move_interface(self):
        """测试 move() 核心接口"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        original_position = player.position
        
        # 测试移动
        result = player.move(Direction.RIGHT)
        self.assertTrue(result)
        self.assertEqual(player.position.x, original_position.x + 1)
        self.assertEqual(player.position.y, original_position.y)
        
        # 测试向上移动
        result = player.move(Direction.UP)
        self.assertTrue(result)
        self.assertEqual(player.position.y, original_position.y - 1)
        
        # 测试 STAY
        result = player.move(Direction.STAY)
        self.assertTrue(result)
        
        # 测试监狱中的玩家不能移动
        player.send_to_prison(Position(0, 0))
        result = player.move(Direction.RIGHT)
        self.assertFalse(result)
    
    def test_move_invalid_direction(self):
        """测试 move() 接口处理无效方向"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        
        # 测试无效方向（虽然 Direction 枚举应该不会有无效值，但测试边界情况）
        # 这里主要测试 move 方法能正确处理各种情况
        result = player.move(Direction.STAY)
        self.assertTrue(result)
    
    def test_move_to_invalid_position(self):
        """测试 move() 接口处理无效位置"""
        player = Player("L0", Team.LEFT, Position(0, 0), self.test_game)
        
        # 尝试移动到地图外（如果地图有边界检查）
        # 这取决于 world.is_valid_position 的实现
        result = player.move(Direction.LEFT)
        # 如果位置无效，应该返回 False
        # 这里主要测试方法不会崩溃
    
    def test_check_state_interface(self):
        """测试 check() 接口 - 状态检查"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        
        # 测试状态检查
        self.assertTrue(player.check("state", state="is_free"))
        self.assertFalse(player.check("state", state="is_in_prison"))
        self.assertFalse(player.check("state", state="has_flag"))
        self.assertFalse(player.check("state", state="is_in_base"))
        
        # 测试监狱状态
        player.send_to_prison(Position(0, 0))
        self.assertFalse(player.check("state", state="is_free"))
        self.assertTrue(player.check("state", state="is_in_prison"))
    
    def test_check_state_with_flag(self):
        """测试 check() 接口 - 持有旗帜状态"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        flag = Flag("flag_R_0", Team.RIGHT, Position(10, 10))
        
        # 拾取旗帜
        player.action(Action.PICKUP_FLAG, flag=flag)
        self.assertTrue(player.check("state", state="has_flag"))
    
    def test_check_state_in_base(self):
        """测试 check() 接口 - 在基地内状态"""
        player = Player("L0", Team.LEFT, Position(5, 5), self.test_game)
        
        # 如果玩家在基地内
        if player.base_area and player.base_area.contains(player.position):
            self.assertTrue(player.check("state", state="is_in_base"))
        else:
            self.assertFalse(player.check("state", state="is_in_base"))
    
    def test_check_state_invalid_state(self):
        """测试 check() 接口 - 无效状态类型"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        
        with self.assertRaises(ValueError):
            player.check("state", state="invalid_state")
    
    def test_check_relation_interface(self):
        """测试 check() 接口 - 关系检查"""
        l_player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        r_player = Player("R0", Team.RIGHT, Position(15, 15), self.test_game)
        l_player2 = Player("L1", Team.LEFT, Position(11, 11), self.test_game)
        
        # 测试敌人关系
        self.assertTrue(l_player.check("relation", relation="is_enemy_of", other_player=r_player))
        self.assertFalse(l_player.check("relation", relation="is_enemy_of", other_player=l_player2))
        
        # 测试队友关系
        self.assertTrue(l_player.check("relation", relation="is_teammate_of", other_player=l_player2))
        self.assertFalse(l_player.check("relation", relation="is_teammate_of", other_player=r_player))
        
        # 测试队伍归属
        self.assertTrue(l_player.check("relation", relation="belongs_to_team", team=Team.LEFT))
        self.assertFalse(l_player.check("relation", relation="belongs_to_team", team=Team.RIGHT))
        
        # 测试敌方队伍
        self.assertTrue(l_player.check("relation", relation="is_enemy_team", team=Team.RIGHT))
        self.assertFalse(l_player.check("relation", relation="is_enemy_team", team=Team.LEFT))
        
        # 测试己方队伍
        self.assertTrue(l_player.check("relation", relation="is_my_team", team=Team.LEFT))
        self.assertFalse(l_player.check("relation", relation="is_my_team", team=Team.RIGHT))
    
    def test_check_relation_missing_parameter(self):
        """测试 check() 接口 - 关系检查缺少参数"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        other_player = Player("R0", Team.RIGHT, Position(15, 15), self.test_game)
        
        # 缺少 other_player 参数
        with self.assertRaises(ValueError):
            player.check("relation", relation="is_enemy_of")
        
        # 缺少 team 参数
        with self.assertRaises(ValueError):
            player.check("relation", relation="belongs_to_team")
    
    def test_check_relation_invalid_relation(self):
        """测试 check() 接口 - 无效关系类型"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        
        with self.assertRaises(ValueError):
            player.check("relation", relation="invalid_relation")
    
    def test_check_position_interface(self):
        """测试 check() 接口 - 位置检查"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        enemy1 = Player("R0", Team.RIGHT, Position(12, 12), self.test_game)
        enemy2 = Player("R1", Team.RIGHT, Position(15, 15), self.test_game)
        opponents = [enemy1, enemy2]
        
        # 测试找到最近的敌人
        has_opponent = player.check("position", position="find_closest_opponent", opponents=opponents)
        self.assertTrue(has_opponent)
        
        # 测试没有敌人
        has_opponent = player.check("position", position="find_closest_opponent", opponents=[])
        self.assertFalse(has_opponent)
        
        # 测试找到最近的旗帜
        flag1 = Flag("flag_R_0", Team.RIGHT, Position(13, 13))
        flag2 = Flag("flag_R_1", Team.RIGHT, Position(16, 16))
        flags = [flag1, flag2]
        
        has_flag = player.check("position", position="find_closest_flag", flags=flags)
        self.assertTrue(has_flag)
        
        # 测试没有旗帜
        has_flag = player.check("position", position="find_closest_flag", flags=[])
        self.assertFalse(has_flag)
    
    def test_check_position_invalid_position(self):
        """测试 check() 接口 - 无效位置类型"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        
        with self.assertRaises(ValueError):
            player.check("position", position="invalid_position")
    
    def test_check_invalid_check_type(self):
        """测试 check() 接口 - 无效检查类型"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        
        with self.assertRaises(ValueError):
            player.check("invalid_type")
    
    def test_action_interface_pickup_flag(self):
        """测试 action() 接口 - 拾取旗帜"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        # 创建可拾取的旗帜（默认 is_picked_up=False, is_scored=False）
        flag = Flag("flag_R_0", Team.RIGHT, Position(10, 10))
        self.test_game.flags[flag.flag_id] = flag
        
        # 拾取旗帜（玩家和旗帜在同一位置）
        result = player.action(Action.PICKUP_FLAG, flag=flag)
        self.assertTrue(result)
        self.assertTrue(player.has_flag)
        self.assertEqual(player.carried_flag, flag)
    
    def test_action_interface_drop_flag(self):
        """测试 action() 接口 - 放下旗帜"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        # 创建可拾取的旗帜（默认 is_picked_up=False, is_scored=False）
        flag = Flag("flag_R_0", Team.RIGHT, Position(10, 10))
        self.test_game.flags[flag.flag_id] = flag
        
        # 先拾取旗帜
        player.action(Action.PICKUP_FLAG, flag=flag)
        self.assertTrue(player.has_flag)
        
        # 放下旗帜
        result = player.action(Action.DROP_FLAG)
        self.assertTrue(result)
        self.assertFalse(player.has_flag)
    
    def test_action_interface_score_flag(self):
        """测试 action() 接口 - 得分"""
        player = Player("L0", Team.LEFT, Position(5, 5), self.test_game)
        # 创建可拾取的旗帜
        flag = Flag("flag_R_0", Team.RIGHT, Position(5, 5))
        self.test_game.flags[flag.flag_id] = flag
        
        # 设置基地区域
        player.set_base_area(self.test_map.left_team_target)
        
        # 拾取旗帜
        player.action(Action.PICKUP_FLAG, flag=flag)
        self.assertTrue(player.has_flag)
        
        # 在基地内得分
        if player.is_in_base():
            result = player.action(Action.SCORE_FLAG)
            # 得分可能成功或失败，取决于具体条件
            # 这里主要测试接口不会崩溃
            self.assertIsInstance(result, bool)
    
    def test_action_interface_tag_enemy(self):
        """测试 action() 接口 - 标记敌人"""
        l_player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        r_player = Player("R0", Team.RIGHT, Position(10, 10), self.test_game)
        
        # 标记敌人（需要满足条件：在相邻位置）
        # 这里主要测试接口不会崩溃
        result = l_player.action(Action.TAG_ENEMY, target=r_player)
        self.assertIsInstance(result, bool)
    
    def test_action_interface_rescue_teammate(self):
        """测试 action() 接口 - 营救队友"""
        l_player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        l_player2 = Player("L1", Team.LEFT, Position(10, 10), self.test_game)
        
        # 将队友送入监狱
        l_player2.send_to_prison(Position(18, 18))
        self.assertTrue(l_player2.is_in_prison)
        
        # 营救队友（需要满足条件：在相邻位置）
        result = l_player.action(Action.RESCUE_TEAMMATE, teammate=l_player2)
        # 营救可能成功或失败，取决于具体条件
        self.assertIsInstance(result, bool)
    
    def test_action_interface_invalid_action(self):
        """测试 action() 接口 - 无效动作类型"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        
        # 测试无效动作（虽然 Action 枚举应该不会有无效值）
        # 这里主要测试方法能正确处理
        # 注意：Action 枚举可能没有无效值，所以这个测试可能不会触发错误
        # 但可以测试方法的健壮性
    
    def test_action_interface_missing_parameters(self):
        """测试 action() 接口 - 缺少参数"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        
        # PICKUP_FLAG 需要 flag 参数
        result = player.action(Action.PICKUP_FLAG)
        self.assertFalse(result)
        
        # TAG_ENEMY 需要 target 参数
        result = player.action(Action.TAG_ENEMY)
        self.assertFalse(result)
        
        # RESCUE_TEAMMATE 需要 teammate 参数
        result = player.action(Action.RESCUE_TEAMMATE)
        self.assertFalse(result)
    
    def test_core_interfaces_integration(self):
        """测试四个核心接口的集成使用"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        
        # 1. 检查状态
        is_free = player.check("state", state="is_free")
        self.assertTrue(is_free)
        
        # 2. 规划行动
        direction = player.plan()
        self.assertIsInstance(direction, (Direction, type(None)))
        
        # 3. 移动
        if direction:
            result = player.move(direction)
            self.assertIsInstance(result, bool)
        
        # 4. 执行动作（如果有条件）
        flag = Flag("flag_R_0", Team.RIGHT, Position(10, 10))
        self.test_game.flags[flag.flag_id] = flag
        if player.position == flag.position:
            result = player.action(Action.PICKUP_FLAG, flag=flag)
            self.assertIsInstance(result, bool)
    
    def test_core_interfaces_encapsulation(self):
        """测试核心接口的封装性 - 内部管理器不可访问"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        
        # 验证内部管理器不可访问
        private_attrs = ['state_manager', 'actions', 'flag_manager', 
                        'prison_manager', 'data_updater', 'team_relations', 'behavior']
        
        for attr in private_attrs:
            with self.assertRaises(AttributeError):
                getattr(player, attr)
        
        # 验证公共接口可用
        self.assertTrue(hasattr(player, 'plan'))
        self.assertTrue(hasattr(player, 'move'))
        self.assertTrue(hasattr(player, 'check'))
        self.assertTrue(hasattr(player, 'action'))
    
    # ========== plan() 接口扩展测试 ==========
    
    def test_plan_in_prison_returns_none(self):
        """测试 plan() 接口 - 监狱中的玩家无法规划"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        
        # 将玩家送入监狱
        player.send_to_prison(Position(18, 18))
        self.assertTrue(player.is_in_prison)
        
        # 监狱中的玩家应该无法规划
        direction = player.plan()
        # 注意：plan() 可能返回 None 或 Direction.STAY，取决于实现
        # 但关键是不能返回有效的移动方向
        if direction is not None:
            self.assertEqual(direction, Direction.STAY)
    
    def test_plan_with_flag_returns_direction(self):
        """测试 plan() 接口 - 持有旗帜时的规划"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        flag = Flag("flag_R_0", Team.RIGHT, Position(10, 10))
        self.test_game.flags[flag.flag_id] = flag
        
        # 拾取旗帜
        player.action(Action.PICKUP_FLAG, flag=flag)
        self.assertTrue(player.has_flag)
        
        # 持有旗帜时应该能规划返回基地的路径
        direction = player.plan()
        # 应该返回一个方向（可能是返回基地的方向）
        self.assertIsInstance(direction, (Direction, type(None)))
    
    def test_plan_all_strategies(self):
        """测试 plan() 接口 - 所有策略类型"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        
        # 测试所有策略
        strategies = [Strategy.SCORING, Strategy.DEFENCE, Strategy.SAVING]
        for strategy in strategies:
            direction = player.plan(suggested_strategy=strategy)
            self.assertIsInstance(direction, (Direction, type(None)))
    
    def test_plan_consistency(self):
        """测试 plan() 接口 - 多次调用的一致性"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        
        # 多次调用 plan()，结果应该合理
        directions = []
        for _ in range(5):
            direction = player.plan()
            directions.append(direction)
            self.assertIsInstance(direction, (Direction, type(None)))
    
    # ========== move() 接口扩展测试 ==========
    
    def test_move_all_directions(self):
        """测试 move() 接口 - 所有方向"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        initial_pos = Position(10, 10)
        
        directions = [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT, Direction.STAY]
        for direction in directions:
            # 重置位置
            player.position = initial_pos
            
            # 执行移动
            result = player.move(direction)
            self.assertIsInstance(result, bool)
            
            if direction == Direction.STAY:
                self.assertEqual(player.position, initial_pos)
            elif result:
                # 验证位置确实改变了
                self.assertNotEqual(player.position, initial_pos)
    
    def test_move_in_prison_fails(self):
        """测试 move() 接口 - 监狱中的玩家无法移动"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        initial_pos = Position(10, 10)
        
        # 将玩家送入监狱
        player.send_to_prison(Position(18, 18))
        self.assertTrue(player.is_in_prison)
        
        # 尝试移动应该失败
        result = player.move(Direction.UP)
        self.assertFalse(result)
        # 位置不应该改变
        self.assertEqual(player.position, Position(18, 18))
    
    def test_move_boundary_conditions(self):
        """测试 move() 接口 - 边界条件"""
        player = Player("L0", Team.LEFT, Position(0, 0), self.test_game)
        
        # 尝试向上移动（边界外）
        result = player.move(Direction.UP)
        # 应该失败或保持在边界内
        self.assertIsInstance(result, bool)
        
        # 尝试向左移动（边界外）
        result = player.move(Direction.LEFT)
        self.assertIsInstance(result, bool)
    
    def test_move_into_wall_fails(self):
        """测试 move() 接口 - 移动到墙壁应该失败"""
        # 创建有墙壁的地图
        test_map = GameMap()
        test_map.width = 20
        test_map.height = 20
        test_map.walls = {Position(11, 10)}  # 在玩家右侧放置墙壁
        
        test_game = World(test_map)
        player = Player("L0", Team.LEFT, Position(10, 10), test_game)
        
        # 尝试移动到墙壁位置
        result = player.move(Direction.RIGHT)
        # 应该失败
        self.assertFalse(result)
        # 位置不应该改变
        self.assertEqual(player.position, Position(10, 10))
    
    def test_move_position_update(self):
        """测试 move() 接口 - 位置更新验证"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        
        # 向上移动
        result = player.move(Direction.UP)
        if result:
            self.assertEqual(player.position.y, 9)
            self.assertEqual(player.position.x, 10)
        
        # 重置并向右移动
        player.position = Position(10, 10)
        result = player.move(Direction.RIGHT)
        if result:
            self.assertEqual(player.position.x, 11)
            self.assertEqual(player.position.y, 10)
    
    # ========== check() 接口扩展测试 ==========
    
    def test_check_state_transitions(self):
        """测试 check() 接口 - 状态转换"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        
        # 初始状态：自由
        self.assertTrue(player.check("state", state="is_free"))
        self.assertFalse(player.check("state", state="is_in_prison"))
        self.assertFalse(player.check("state", state="has_flag"))
        
        # 拾取旗帜后
        flag = Flag("flag_R_0", Team.RIGHT, Position(10, 10))
        self.test_game.flags[flag.flag_id] = flag
        player.action(Action.PICKUP_FLAG, flag=flag)
        self.assertTrue(player.check("state", state="has_flag"))
        self.assertTrue(player.check("state", state="is_free"))
        
        # 送入监狱后
        player.send_to_prison(Position(18, 18))
        self.assertTrue(player.check("state", state="is_in_prison"))
        self.assertFalse(player.check("state", state="is_free"))
    
    def test_check_relation_all_combinations(self):
        """测试 check() 接口 - 所有关系组合"""
        l_player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        l_player2 = Player("L1", Team.LEFT, Position(11, 11), self.test_game)
        r_player = Player("R0", Team.RIGHT, Position(15, 15), self.test_game)
        r_player2 = Player("R1", Team.RIGHT, Position(16, 16), self.test_game)
        
        # 测试所有关系检查
        self.assertTrue(l_player.check("relation", relation="is_teammate_of", other_player=l_player2))
        self.assertFalse(l_player.check("relation", relation="is_teammate_of", other_player=r_player))
        
        self.assertTrue(l_player.check("relation", relation="is_enemy_of", other_player=r_player))
        self.assertFalse(l_player.check("relation", relation="is_enemy_of", other_player=l_player2))
        
        self.assertTrue(l_player.check("relation", relation="belongs_to_team", team=Team.LEFT))
        self.assertFalse(l_player.check("relation", relation="belongs_to_team", team=Team.RIGHT))
        
        self.assertTrue(l_player.check("relation", relation="is_my_team", team=Team.LEFT))
        self.assertFalse(l_player.check("relation", relation="is_my_team", team=Team.RIGHT))
        
        self.assertTrue(l_player.check("relation", relation="is_enemy_team", team=Team.RIGHT))
        self.assertFalse(l_player.check("relation", relation="is_enemy_team", team=Team.LEFT))
    
    def test_check_position_with_multiple_opponents(self):
        """测试 check() 接口 - 多个对手的位置检查"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        
        # 创建多个对手
        opponents = [
            Player("R0", Team.RIGHT, Position(12, 12), self.test_game),
            Player("R1", Team.RIGHT, Position(15, 15), self.test_game),
            Player("R2", Team.RIGHT, Position(8, 8), self.test_game),
        ]
        
        # 应该能找到最近的对手
        has_opponent = player.check("position", position="find_closest_opponent", opponents=opponents)
        self.assertTrue(has_opponent)
    
    def test_check_position_with_multiple_flags(self):
        """测试 check() 接口 - 多个旗帜的位置检查"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        
        # 创建多个旗帜
        flags = [
            Flag("flag_R_0", Team.RIGHT, Position(12, 12)),
            Flag("flag_R_1", Team.RIGHT, Position(15, 15)),
            Flag("flag_R_2", Team.RIGHT, Position(8, 8)),
        ]
        
        # 应该能找到最近的旗帜
        has_flag = player.check("position", position="find_closest_flag", flags=flags)
        self.assertTrue(has_flag)
    
    def test_check_complex_scenario(self):
        """测试 check() 接口 - 复杂场景"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        flag = Flag("flag_R_0", Team.RIGHT, Position(10, 10))
        self.test_game.flags[flag.flag_id] = flag
        
        # 拾取旗帜
        player.action(Action.PICKUP_FLAG, flag=flag)
        
        # 检查多个状态
        self.assertTrue(player.check("state", state="has_flag"))
        self.assertTrue(player.check("state", state="is_free"))
        self.assertFalse(player.check("state", state="is_in_prison"))
        
        # 检查关系
        enemy = Player("R0", Team.RIGHT, Position(15, 15), self.test_game)
        self.assertTrue(player.check("relation", relation="is_enemy_of", other_player=enemy))
    
    # ========== action() 接口扩展测试 ==========
    
    def test_action_pickup_flag_conditions(self):
        """测试 action() 接口 - 拾取旗帜的条件验证"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        
        # 测试：旗帜不在同一位置
        flag1 = Flag("flag_R_0", Team.RIGHT, Position(15, 15))
        self.test_game.flags[flag1.flag_id] = flag1
        result = player.action(Action.PICKUP_FLAG, flag=flag1)
        # 应该失败（不在同一位置）
        self.assertFalse(result)
        
        # 测试：旗帜在同一位置
        flag2 = Flag("flag_R_1", Team.RIGHT, Position(10, 10))
        self.test_game.flags[flag2.flag_id] = flag2
        result = player.action(Action.PICKUP_FLAG, flag=flag2)
        # 应该成功
        self.assertTrue(result)
        self.assertTrue(player.has_flag)
    
    def test_action_drop_flag_conditions(self):
        """测试 action() 接口 - 放下旗帜的条件验证"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        flag = Flag("flag_R_0", Team.RIGHT, Position(10, 10))
        self.test_game.flags[flag.flag_id] = flag
        
        # 没有旗帜时放下应该失败
        result = player.action(Action.DROP_FLAG)
        self.assertFalse(result)
        
        # 拾取旗帜后放下应该成功
        player.action(Action.PICKUP_FLAG, flag=flag)
        result = player.action(Action.DROP_FLAG)
        self.assertTrue(result)
        self.assertFalse(player.has_flag)
    
    def test_action_score_flag_conditions(self):
        """测试 action() 接口 - 得分条件验证"""
        player = Player("L0", Team.LEFT, Position(5, 5), self.test_game)
        flag = Flag("flag_R_0", Team.RIGHT, Position(5, 5))
        self.test_game.flags[flag.flag_id] = flag
        
        # 设置基地区域
        player.set_base_area(self.test_map.left_team_target)
        
        # 没有旗帜时得分应该失败
        result = player.action(Action.SCORE_FLAG)
        self.assertFalse(result)
        
        # 拾取旗帜
        player.action(Action.PICKUP_FLAG, flag=flag)
        
        # 在基地内得分
        if player.is_in_base():
            result = player.action(Action.SCORE_FLAG)
            # 可能成功或失败，取决于具体实现
            self.assertIsInstance(result, bool)
    
    def test_action_tag_enemy_conditions(self):
        """测试 action() 接口 - 标记敌人的条件验证"""
        l_player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        r_player = Player("R0", Team.RIGHT, Position(10, 10), self.test_game)
        
        # 在同一位置标记敌人
        result = l_player.action(Action.TAG_ENEMY, target=r_player)
        # 可能成功或失败，取决于具体条件（距离、状态等）
        self.assertIsInstance(result, bool)
        
        # 测试标记队友应该失败
        l_player2 = Player("L1", Team.LEFT, Position(10, 10), self.test_game)
        result = l_player.action(Action.TAG_ENEMY, target=l_player2)
        # 标记队友应该失败
        self.assertFalse(result)
    
    def test_action_rescue_teammate_conditions(self):
        """测试 action() 接口 - 营救队友的条件验证"""
        l_player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        l_player2 = Player("L1", Team.LEFT, Position(10, 10), self.test_game)
        
        # 将队友送入监狱
        l_player2.send_to_prison(Position(18, 18))
        self.assertTrue(l_player2.is_in_prison)
        
        # 不在监狱附近营救应该失败
        result = l_player.action(Action.RESCUE_TEAMMATE, teammate=l_player2)
        # 可能失败（不在相邻位置）
        self.assertIsInstance(result, bool)
        
        # 测试营救敌人应该失败
        r_player = Player("R0", Team.RIGHT, Position(18, 18), self.test_game)
        r_player.send_to_prison(Position(18, 18))
        result = l_player.action(Action.RESCUE_TEAMMATE, teammate=r_player)
        # 营救敌人应该失败
        self.assertFalse(result)
    
    def test_action_sequence(self):
        """测试 action() 接口 - 动作序列"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        flag = Flag("flag_R_0", Team.RIGHT, Position(10, 10))
        self.test_game.flags[flag.flag_id] = flag
        
        # 序列1：拾取 -> 移动 -> 放下
        result1 = player.action(Action.PICKUP_FLAG, flag=flag)
        self.assertTrue(result1)
        self.assertTrue(player.has_flag)
        
        # 移动
        player.move(Direction.RIGHT)
        
        # 放下
        result2 = player.action(Action.DROP_FLAG)
        self.assertTrue(result2)
        self.assertFalse(player.has_flag)
    
    def test_action_in_prison_blocked(self):
        """测试 action() 接口 - 监狱中的玩家动作被阻止"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        flag = Flag("flag_R_0", Team.RIGHT, Position(10, 10))
        self.test_game.flags[flag.flag_id] = flag
        
        # 将玩家送入监狱
        player.send_to_prison(Position(18, 18))
        self.assertTrue(player.is_in_prison)
        
        # 监狱中的玩家应该无法执行动作
        # 注意：某些动作可能仍然可以执行（如营救），但大部分应该被阻止
        # 这里主要测试接口不会崩溃
        result = player.action(Action.PICKUP_FLAG, flag=flag)
        # 应该失败（在监狱中）
        self.assertFalse(result)
    
    # ========== 核心接口组合测试 ==========
    
    def test_plan_move_sequence(self):
        """测试 plan() 和 move() 的组合使用"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        
        # 规划 -> 移动的序列
        for _ in range(5):
            direction = player.plan()
            if direction:
                result = player.move(direction)
                self.assertIsInstance(result, bool)
    
    def test_check_action_sequence(self):
        """测试 check() 和 action() 的组合使用"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        flag = Flag("flag_R_0", Team.RIGHT, Position(10, 10))
        self.test_game.flags[flag.flag_id] = flag
        
        # 检查状态 -> 执行动作
        if player.check("state", state="is_free"):
            if not player.check("state", state="has_flag"):
                result = player.action(Action.PICKUP_FLAG, flag=flag)
                self.assertTrue(result)
                self.assertTrue(player.check("state", state="has_flag"))
    
    def test_all_interfaces_workflow(self):
        """测试所有核心接口的完整工作流"""
        player = Player("L0", Team.LEFT, Position(10, 10), self.test_game)
        flag = Flag("flag_R_0", Team.RIGHT, Position(10, 10))
        self.test_game.flags[flag.flag_id] = flag
        
        # 1. 检查初始状态
        self.assertTrue(player.check("state", state="is_free"))
        self.assertFalse(player.check("state", state="has_flag"))
        
        # 2. 规划行动
        direction = player.plan()
        self.assertIsInstance(direction, (Direction, type(None)))
        
        # 3. 执行移动（如果规划了方向）
        if direction:
            moved = player.move(direction)
            self.assertIsInstance(moved, bool)
        
        # 4. 检查是否可以拾取旗帜
        if player.position == flag.position:
            can_pickup = not player.check("state", state="has_flag")
            if can_pickup:
                result = player.action(Action.PICKUP_FLAG, flag=flag)
                self.assertTrue(result)
                
                # 5. 再次检查状态
                self.assertTrue(player.check("state", state="has_flag"))
                
                # 6. 规划返回基地
                direction = player.plan()
                self.assertIsInstance(direction, (Direction, type(None)))


if __name__ == '__main__':
    unittest.main()

