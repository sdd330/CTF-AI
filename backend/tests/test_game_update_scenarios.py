"""
World.update 场景测试
测试各种更新场景的覆盖
"""

import unittest
from lib.data_models import Player, Team, Position, Flag, Action
from lib.map_service import GameMap
from lib.game_service import World


class TestGameUpdateScenarios(unittest.TestCase):
    """游戏更新场景测试"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.test_map = self._create_test_map()
        self.world = World(self.test_map)
        self.world.my_team_name = "L"
    
    def _create_test_map(self) -> GameMap:
        """创建测试地图"""
        game_map = GameMap()
        game_map.width = 20
        game_map.height = 20
        game_map.middle_line = 10.0
        game_map.walls = set()
        
        from lib.data_models import TargetArea, PrisonArea
        
        left_target_positions = {Position(2, 2), Position(2, 3)}
        game_map.left_team_target = TargetArea(Team.LEFT, left_target_positions)
        
        right_target_positions = {Position(17, 17), Position(17, 18)}
        game_map.right_team_target = TargetArea(Team.RIGHT, right_target_positions)
        
        left_prison_positions = {Position(0, 0), Position(0, 1)}
        game_map.left_team_prison = PrisonArea(Team.LEFT, left_prison_positions)
        
        right_prison_positions = {Position(18, 18), Position(18, 19)}
        game_map.right_team_prison = PrisonArea(Team.RIGHT, right_prison_positions)
        
        return game_map
    
    def test_update_flags_from_request(self):
        """测试旗帜更新场景"""
        req = {
            "time": 1.0,
            "myteamFlag": [
                {"posX": 5, "posY": 5, "canPickup": True}
            ],
            "opponentFlag": [
                {"posX": 15, "posY": 15, "canPickup": True}
            ],
            "myteamPlayer": [],
            "opponentPlayer": []
        }
        
        result = self.world.update(req)
        self.assertTrue(result)
        self.assertEqual(len(self.world.flags), 2)
    
    def test_update_players_from_request_new_player(self):
        """测试新玩家创建场景"""
        req = {
            "time": 1.0,
            "myteamPlayer": [
                {
                    "name": "L0",
                    "team": "L",
                    "posX": 5,
                    "posY": 5,
                    "hasFlag": False,
                    "inPrison": False
                }
            ],
            "opponentPlayer": [],
            "myteamFlag": [],
            "opponentFlag": []
        }
        
        result = self.world.update(req)
        self.assertTrue(result)
        self.assertIn("L0", self.world.players)
        self.assertEqual(self.world.players["L0"].team, Team.LEFT)
    
    def test_update_players_from_request_existing_player(self):
        """测试现有玩家更新场景"""
        # 先创建玩家
        player = Player("L0", Team.LEFT, Position(5, 5), self.world)
        self.world.players["L0"] = player
        
        req = {
            "time": 1.0,
            "myteamPlayer": [
                {
                    "name": "L0",
                    "team": "L",
                    "posX": 6,
                    "posY": 6,
                    "hasFlag": False,
                    "inPrison": False
                }
            ],
            "opponentPlayer": [],
            "myteamFlag": [],
            "opponentFlag": []
        }
        
        result = self.world.update(req)
        self.assertTrue(result)
        self.assertEqual(self.world.players["L0"].position, Position(6, 6))
    
    def test_update_player_pickup_flag(self):
        """测试玩家拾取旗帜场景"""
        # 创建旗帜
        flag = Flag("enemy_flag_1", Team.RIGHT, Position(15, 15))
        self.world.flags[flag.flag_id] = flag
        
        # 创建玩家
        player = Player("L0", Team.LEFT, Position(15, 15), self.world)
        self.world.players["L0"] = player
        
        req = {
            "time": 1.0,
            "myteamPlayer": [
                {
                    "name": "L0",
                    "team": "L",
                    "posX": 15,
                    "posY": 15,
                    "hasFlag": True,
                    "inPrison": False
                }
            ],
            "opponentPlayer": [],
            "myteamFlag": [],
            "opponentFlag": [
                {"posX": 15, "posY": 15, "canPickup": False}
            ]
        }
        
        result = self.world.update(req)
        self.assertTrue(result)
        self.assertTrue(self.world.players["L0"].has_flag)
    
    def test_update_player_drop_flag(self):
        """测试玩家放下旗帜场景"""
        # 创建旗帜
        flag = Flag("enemy_flag_1", Team.RIGHT, Position(15, 15))
        self.world.flags[flag.flag_id] = flag
        
        # 创建玩家并持有旗帜
        player = Player("L0", Team.LEFT, Position(15, 15), self.world)
        player.action(Action.PICKUP_FLAG, flag=flag)
        self.world.players["L0"] = player
        
        req = {
            "time": 1.0,
            "myteamPlayer": [
                {
                    "name": "L0",
                    "team": "L",
                    "posX": 15,
                    "posY": 15,
                    "hasFlag": False,
                    "inPrison": False
                }
            ],
            "opponentPlayer": [],
            "myteamFlag": [],
            "opponentFlag": [
                {"posX": 15, "posY": 15, "canPickup": True}
            ]
        }
        
        result = self.world.update(req)
        self.assertTrue(result)
        self.assertFalse(self.world.players["L0"].has_flag)
    
    def test_update_player_sent_to_prison(self):
        """测试玩家被抓进监狱场景"""
        player = Player("L0", Team.LEFT, Position(5, 5), self.world)
        self.world.players["L0"] = player
        
        req = {
            "time": 1.0,
            "myteamPlayer": [
                {
                    "name": "L0",
                    "team": "L",
                    "posX": 0,
                    "posY": 0,
                    "hasFlag": False,
                    "inPrison": True
                }
            ],
            "opponentPlayer": [],
            "myteamFlag": [],
            "opponentFlag": []
        }
        
        result = self.world.update(req)
        self.assertTrue(result)
        self.assertTrue(self.world.players["L0"].is_in_prison)
        # 验证玩家在敌方监狱（R队监狱）
        r_prison = self.test_map.right_team_prison.positions
        self.assertIn(self.world.players["L0"].position, r_prison)
    
    def test_update_player_rescued_from_prison(self):
        """测试玩家被营救场景"""
        # 创建玩家并在监狱中
        player = Player("L0", Team.LEFT, Position(0, 0), self.world)
        player.send_to_prison(Position(18, 18))
        self.world.players["L0"] = player
        
        req = {
            "time": 1.0,
            "myteamPlayer": [
                {
                    "name": "L0",
                    "team": "L",
                    "posX": 5,
                    "posY": 5,
                    "hasFlag": False,
                    "inPrison": False
                }
            ],
            "opponentPlayer": [],
            "myteamFlag": [],
            "opponentFlag": []
        }
        
        result = self.world.update(req)
        self.assertTrue(result)
        self.assertFalse(self.world.players["L0"].is_in_prison)
    
    def test_update_time_validation(self):
        """测试时间验证场景"""
        req = {
            "time": 0.5,
            "myteamPlayer": [],
            "opponentPlayer": [],
            "myteamFlag": [],
            "opponentFlag": []
        }
        
        # 第一次更新
        result1 = self.world.update(req)
        self.assertTrue(result1)
        self.assertEqual(self.world.current_time, 0.5)
        
        # 第二次更新（时间倒退，应该失败）
        req["time"] = 0.3
        result2 = self.world.update(req)
        self.assertFalse(result2)
        self.assertEqual(self.world.current_time, 0.5)  # 时间不应该更新
    
    def test_update_scoring_detection(self):
        """测试得分检测场景"""
        # 创建旗帜
        flag = Flag("enemy_flag_1", Team.RIGHT, Position(2, 2))
        self.world.flags[flag.flag_id] = flag
        
        # 创建玩家并持有旗帜，在己方基地内
        player = Player("L0", Team.LEFT, Position(2, 2), self.world)
        player.action(Action.PICKUP_FLAG, flag=flag)
        self.world.players["L0"] = player
        
        req = {
            "time": 1.0,
            "myteamPlayer": [
                {
                    "name": "L0",
                    "team": "L",
                    "posX": 2,
                    "posY": 2,
                    "hasFlag": True,
                    "inPrison": False
                }
            ],
            "opponentPlayer": [],
            "myteamFlag": [],
            "opponentFlag": [
                {"posX": 2, "posY": 2, "canPickup": False}
            ]
        }
        
        initial_score = self.world.left_team_score
        result = self.world.update(req)
        self.assertTrue(result)
        # 应该检测到得分
        self.assertGreaterEqual(self.world.left_team_score, initial_score)


if __name__ == '__main__':
    unittest.main()

