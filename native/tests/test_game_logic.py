"""
游戏逻辑测试
测试 CTFGame 和 GameState 的核心逻辑
使用事件模拟和逻辑分离
"""

import pytest
from native.game.game import CTFGame
from native.game.game_state import GameState
from native.utils import Team, Direction


@pytest.mark.unit
@pytest.mark.game_logic
class TestGameState:
    """GameState 单元测试"""
    
    def test_initialization(self, game_state):
        """测试游戏状态初始化"""
        assert game_state.left_team_score == 0
        assert game_state.right_team_score == 0
        assert game_state.game_started is False
        assert game_state.game_paused is False
        assert game_state.game_over is False
        assert game_state.winner is None
        assert len(game_state.left_team_players) == 0
        assert len(game_state.right_team_players) == 0
    
    def test_get_team_players(self, game_state, mock_player):
        """测试获取队伍玩家"""
        player = mock_player("L0", Team.LEFT)
        game_state.left_team_players.append(player)
        
        left_players = game_state.get_team_players(Team.LEFT)
        assert len(left_players) == 1
        assert left_players[0].name == "L0"
        
        right_players = game_state.get_team_players(Team.RIGHT)
        assert len(right_players) == 0
    
    def test_get_team_flags(self, game_state, mock_flag):
        """测试获取队伍旗帜"""
        flag = mock_flag("L0", Team.LEFT)
        game_state.left_team_flags.append(flag)
        
        left_flags = game_state.get_team_flags(Team.LEFT)
        assert len(left_flags) == 1
        assert left_flags[0].flag_id == "L0"
    
    def test_get_all_players(self, game_state, mock_player):
        """测试获取所有玩家"""
        player1 = mock_player("L0", Team.LEFT)
        player2 = mock_player("R0", Team.RIGHT)
        game_state.left_team_players.append(player1)
        game_state.right_team_players.append(player2)
        
        all_players = game_state.get_all_players()
        assert len(all_players) == 2
        assert player1 in all_players
        assert player2 in all_players
    
    def test_check_game_over_left_wins(self, game_state):
        """测试游戏结束 - 左队获胜"""
        game_state.max_score = 5
        game_state.left_team_score = 5
        
        result = game_state.check_game_over()
        
        assert result is True
        assert game_state.game_over is True
        assert game_state.winner == Team.LEFT
    
    def test_check_game_over_right_wins(self, game_state):
        """测试游戏结束 - 右队获胜"""
        game_state.max_score = 5
        game_state.right_team_score = 5
        
        result = game_state.check_game_over()
        
        assert result is True
        assert game_state.game_over is True
        assert game_state.winner == Team.RIGHT
    
    def test_check_game_over_not_over(self, game_state):
        """测试游戏未结束"""
        game_state.max_score = 5
        game_state.left_team_score = 3
        game_state.right_team_score = 2
        
        result = game_state.check_game_over()
        
        assert result is False
        assert game_state.game_over is False
        assert game_state.winner is None


@pytest.mark.unit
@pytest.mark.game_logic
class TestCTFGame:
    """CTFGame 单元测试"""
    
    def test_initialization(self, ctf_game):
        """测试游戏初始化"""
        assert ctf_game.game_map is not None
        assert ctf_game.state is not None
        assert ctf_game.tick_count == 0
    
    def test_initialize_creates_players(self, ctf_game):
        """测试初始化创建玩家"""
        ctf_game.initialize(num_players=2, num_flags=1)
        
        assert len(ctf_game.state.left_team_players) == 2
        assert len(ctf_game.state.right_team_players) == 2
        assert ctf_game.state.left_team_players[0].name == "L0"
        assert ctf_game.state.left_team_players[1].name == "L1"
        assert ctf_game.state.right_team_players[0].name == "R0"
        assert ctf_game.state.right_team_players[1].name == "R1"
    
    def test_initialize_creates_flags(self, ctf_game):
        """测试初始化创建旗帜"""
        ctf_game.initialize(num_players=1, num_flags=2)
        
        assert len(ctf_game.state.left_team_flags) == 2
        assert len(ctf_game.state.right_team_flags) == 2
        assert ctf_game.state.left_team_flags[0].flag_id == "L0"
        assert ctf_game.state.right_team_flags[0].flag_id == "R0"
    
    def test_initialize_game_not_started(self, ctf_game):
        """测试初始化后游戏未开始"""
        ctf_game.initialize()
        
        assert ctf_game.state.game_started is False
    
    def test_update_when_not_started(self, ctf_game):
        """测试游戏未开始时更新不生效"""
        ctf_game.initialize()
        initial_tick = ctf_game.tick_count
        
        ctf_game.update(100)
        
        assert ctf_game.tick_count == initial_tick
    
    def test_update_when_paused(self, ctf_game):
        """测试游戏暂停时更新不生效"""
        ctf_game.initialize()
        ctf_game.state.game_started = True
        ctf_game.state.game_paused = True
        initial_tick = ctf_game.tick_count
        
        ctf_game.update(100)
        
        assert ctf_game.tick_count == initial_tick
    
    def test_update_when_started(self, ctf_game):
        """测试游戏开始时正常更新"""
        ctf_game.initialize()
        ctf_game.state.game_started = True
        initial_tick = ctf_game.tick_count
        
        ctf_game.update(100)
        
        assert ctf_game.tick_count == initial_tick + 1
    
    def test_set_player_action_valid(self, ctf_game):
        """测试设置玩家动作 - 有效位置"""
        ctf_game.initialize(num_players=1)
        player = ctf_game.state.left_team_players[0]
        initial_x, initial_y = player.grid_x, player.grid_y
        
        ctf_game.set_player_action("L0", Direction.RIGHT)
        
        # 玩家应该设置目标位置
        assert player.target_grid_x == initial_x + 1
        assert player.target_grid_y == initial_y
    
    def test_set_player_action_invalid_position(self, ctf_game):
        """测试设置玩家动作 - 无效位置"""
        ctf_game.initialize(num_players=1)
        player = ctf_game.state.left_team_players[0]
        # 移动到地图边界
        player.grid_x = 0
        player.grid_y = 0
        initial_target_x = player.target_grid_x
        
        ctf_game.set_player_action("L0", Direction.LEFT)
        
        # 不应该移动（因为位置无效，向左会到 -1）
        assert player.target_grid_x == initial_target_x or player.target_grid_x == 0
    
    def test_set_player_action_nonexistent_player(self, ctf_game):
        """测试设置不存在的玩家动作"""
        ctf_game.initialize()
        
        # 不应该抛出异常
        ctf_game.set_player_action("NonExistent", Direction.UP)
    
    def test_flag_position_update_when_carried(self, ctf_game, mock_flag):
        """测试携带旗帜时更新位置"""
        ctf_game.initialize(num_players=1)
        player = ctf_game.state.left_team_players[0]
        flag = mock_flag("R0", Team.RIGHT)
        flag.pick_up_by(player)
        flag.carried_by = player
        player.pixel_x = 100.0
        player.pixel_y = 200.0
        
        ctf_game.state.right_team_flags.append(flag)
        ctf_game.state.game_started = True
        
        ctf_game.update(100)
        
        # 旗帜位置应该更新
        assert flag.pixel_x == 100.0
        assert flag.pixel_y == 200.0


@pytest.mark.integration
@pytest.mark.game_logic
class TestGameFlow:
    """游戏流程集成测试"""
    
    def test_complete_game_flow(self, ctf_game):
        """测试完整游戏流程"""
        # 1. 初始化游戏
        ctf_game.initialize(num_players=1, num_flags=1)
        assert ctf_game.state.game_started is False
        
        # 2. 开始游戏
        ctf_game.state.game_started = True
        assert ctf_game.state.game_started is True
        
        # 3. 更新游戏
        ctf_game.update(100)
        assert ctf_game.tick_count > 0
        
        # 4. 设置玩家动作
        ctf_game.set_player_action("L0", Direction.RIGHT)
        player = ctf_game.state.left_team_players[0]
        assert player.target_grid_x > player.grid_x
        
        # 5. 检查游戏结束条件
        ctf_game.state.left_team_score = 5
        ctf_game.state.max_score = 5
        result = ctf_game.state.check_game_over()
        assert result is True
        assert ctf_game.state.winner == Team.LEFT

