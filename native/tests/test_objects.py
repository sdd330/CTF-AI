"""
游戏对象测试
测试 Player 和 Flag 对象的行为
使用事件模拟和逻辑分离
"""

import pytest
from native.objects.player import Player
from native.objects.flag import Flag
from native.utils import Team, Direction, PlayerState, TILE_SIZE


@pytest.mark.unit
class TestPlayer:
    """Player 对象测试"""
    
    def test_initialization(self, mock_player):
        """测试玩家初始化"""
        player = mock_player("L0", Team.LEFT, 2, 1)
        
        assert player.name == "L0"
        assert player.team == Team.LEFT
        assert player.grid_x == 2
        assert player.grid_y == 1
        assert player.state == PlayerState.FREE
        assert player.has_flag is False
        assert player.in_prison is False
    
    def test_pick_up_flag(self, mock_player):
        """测试拾取旗帜"""
        player = mock_player()
        
        player.pick_up_flag()
        
        assert player.has_flag is True
        assert player.state == PlayerState.CARRYING_FLAG
    
    def test_pick_up_flag_in_prison(self, mock_player):
        """测试监狱中的玩家不能拾取旗帜"""
        player = mock_player()
        player.in_prison = True
        
        player.pick_up_flag()
        
        assert player.has_flag is False
    
    def test_drop_flag(self, mock_player):
        """测试放下旗帜"""
        player = mock_player()
        player.has_flag = True
        player.state = PlayerState.CARRYING_FLAG
        
        player.drop_flag()
        
        assert player.has_flag is False
        assert player.state == PlayerState.FREE
    
    def test_set_direction(self, mock_player):
        """测试设置移动方向"""
        player = mock_player("L0", Team.LEFT, 5, 5)
        initial_x = player.grid_x
        
        player.set_direction(Direction.RIGHT)
        
        assert player.target_grid_x == initial_x + 1
        assert player.target_grid_y == 5
    
    def test_set_direction_in_prison(self, mock_player):
        """测试监狱中的玩家不能移动"""
        player = mock_player()
        player.in_prison = True
        initial_target_x = player.target_grid_x
        
        player.set_direction(Direction.RIGHT)
        
        assert player.target_grid_x == initial_target_x
    
    def test_send_to_prison(self, mock_player):
        """测试送入监狱"""
        player = mock_player("L0", Team.LEFT, 10, 10)
        prison_x, prison_y = 1, 10
        
        player.send_to_prison(prison_x, prison_y)
        
        assert player.in_prison is True
        assert player.grid_x == prison_x
        assert player.grid_y == prison_y
        assert player.state == PlayerState.IN_PRISON
        assert player.prison_time_left > 0
    
    def test_prison_timeout(self, mock_player):
        """测试监狱时间到期"""
        player = mock_player()
        player.in_prison = True
        player.prison_time_left = 100
        player.state = PlayerState.IN_PRISON
        
        player.update(150)  # 超过监狱时间
        
        assert player.in_prison is False
        assert player.prison_time_left == 0
        assert player.state == PlayerState.FREE
    
    def test_update_movement(self, mock_player):
        """测试移动更新"""
        player = mock_player("L0", Team.LEFT, 5, 5)
        player.target_grid_x = 6
        player.target_grid_y = 5
        player.target_pixel_x = 6 * TILE_SIZE + TILE_SIZE // 2
        player.target_pixel_y = 5 * TILE_SIZE + TILE_SIZE // 2
        initial_pixel_x = player.pixel_x
        
        player.update(100)  # 100ms
        
        # 玩家应该向目标移动
        assert player.pixel_x != initial_pixel_x
    
    def test_is_at_target(self, mock_player):
        """测试到达目标位置检测"""
        player = mock_player("L0", Team.LEFT, 5, 5)
        player.target_pixel_x = player.pixel_x
        player.target_pixel_y = player.pixel_y
        
        assert player.is_at_target() is True
        
        player.target_pixel_x = player.pixel_x + 100
        
        assert player.is_at_target() is False
    
    def test_get_position(self, mock_player):
        """测试获取位置"""
        player = mock_player("L0", Team.LEFT, 5, 10)
        
        grid_pos = player.get_position()
        pixel_pos = player.get_pixel_position()
        
        assert grid_pos == (5, 10)
        assert pixel_pos[0] == 5 * TILE_SIZE + TILE_SIZE // 2
        assert pixel_pos[1] == 10 * TILE_SIZE + TILE_SIZE // 2


@pytest.mark.unit
class TestFlag:
    """Flag 对象测试"""
    
    def test_initialization(self, mock_flag):
        """测试旗帜初始化"""
        flag = mock_flag("L0", Team.LEFT, 1, 1)
        
        assert flag.flag_id == "L0"
        assert flag.team == Team.LEFT
        assert flag.grid_x == 1
        assert flag.grid_y == 1
        assert flag.is_picked_up is False
        assert flag.is_scored is False
        assert flag.carried_by is None
    
    def test_belongs_to_team(self, mock_flag):
        """测试旗帜归属"""
        flag = mock_flag("L0", Team.LEFT)
        
        assert flag.belongs_to_team(Team.LEFT) is True
        assert flag.belongs_to_team(Team.RIGHT) is False
    
    def test_is_enemy_flag_for(self, mock_flag):
        """测试是否为敌方旗帜"""
        flag = mock_flag("L0", Team.LEFT)
        
        assert flag.is_enemy_flag_for(Team.RIGHT) is True
        assert flag.is_enemy_flag_for(Team.LEFT) is False
    
    def test_can_pickup(self, mock_flag):
        """测试是否可以拾取"""
        flag = mock_flag()
        
        assert flag.can_pickup is True
        
        flag.is_picked_up = True
        assert flag.can_pickup is False
        
        flag.is_picked_up = False
        flag.is_scored = True
        assert flag.can_pickup is False
    
    def test_pick_up_by(self, mock_flag, mock_player):
        """测试被玩家拾取"""
        flag = mock_flag()
        player = mock_player()
        
        flag.pick_up_by(player)
        
        assert flag.is_picked_up is True
        assert flag.carried_by == player
    
    def test_pick_up_by_when_not_pickupable(self, mock_flag, mock_player):
        """测试不可拾取时不能拾取"""
        flag = mock_flag()
        flag.is_scored = True
        player = mock_player()
        
        flag.pick_up_by(player)
        
        assert flag.is_picked_up is False
        assert flag.carried_by is None
    
    def test_drop_at(self, mock_flag, mock_player):
        """测试在指定位置放下旗帜"""
        flag = mock_flag()
        player = mock_player()
        flag.is_picked_up = True
        flag.carried_by = player
        
        flag.drop_at(10, 15)
        
        assert flag.is_picked_up is False
        assert flag.carried_by is None
        assert flag.grid_x == 10
        assert flag.grid_y == 15
    
    def test_score(self, mock_flag, mock_player):
        """测试得分"""
        flag = mock_flag("L0", Team.LEFT, 1, 1)
        player = mock_player()
        flag.is_picked_up = True
        flag.carried_by = player
        flag.grid_x = 10
        flag.grid_y = 10
        
        flag.score()
        
        assert flag.is_scored is True
        assert flag.is_picked_up is False
        assert flag.carried_by is None
        assert flag.grid_x == 1  # 回到原始位置
        assert flag.grid_y == 1
    
    def test_reset(self, mock_flag, mock_player):
        """测试重置旗帜"""
        flag = mock_flag("L0", Team.LEFT, 1, 1)
        player = mock_player()
        flag.is_picked_up = True
        flag.is_scored = True
        flag.carried_by = player
        flag.grid_x = 10
        flag.grid_y = 10
        
        flag.reset()
        
        assert flag.is_picked_up is False
        assert flag.is_scored is False
        assert flag.carried_by is None
        assert flag.grid_x == 1
        assert flag.grid_y == 1
    
    def test_update_position_when_carried(self, mock_flag, mock_player):
        """测试携带时更新位置"""
        flag = mock_flag()
        player = mock_player()
        flag.pick_up_by(player)
        player.pixel_x = 200.0
        player.pixel_y = 300.0
        
        flag.update_position(player.pixel_x, player.pixel_y)
        
        assert flag.pixel_x == 200.0
        assert flag.pixel_y == 300.0
    
    def test_update_position_when_not_carried(self, mock_flag):
        """测试未携带时不更新位置"""
        flag = mock_flag()
        initial_x = flag.pixel_x
        initial_y = flag.pixel_y
        
        flag.update_position(200.0, 300.0)
        
        assert flag.pixel_x == initial_x
        assert flag.pixel_y == initial_y
    
    def test_get_position(self, mock_flag):
        """测试获取位置"""
        flag = mock_flag("L0", Team.LEFT, 5, 10)
        
        grid_pos = flag.get_position()
        pixel_pos = flag.get_pixel_position()
        
        assert grid_pos == (5, 10)
        assert pixel_pos[0] == 5 * TILE_SIZE + TILE_SIZE // 2
        assert pixel_pos[1] == 10 * TILE_SIZE + TILE_SIZE // 2


@pytest.mark.integration
class TestPlayerFlagInteraction:
    """玩家和旗帜交互测试"""
    
    def test_player_pickup_flag(self, mock_player, mock_flag):
        """测试玩家拾取旗帜"""
        player = mock_player("L0", Team.LEFT, 15, 10)
        flag = mock_flag("R0", Team.RIGHT, 15, 10)
        
        player.pick_up_flag()
        flag.pick_up_by(player)
        
        assert player.has_flag is True
        assert flag.is_picked_up is True
        assert flag.carried_by == player
    
    def test_player_drop_flag(self, mock_player, mock_flag):
        """测试玩家放下旗帜"""
        player = mock_player()
        flag = mock_flag()
        player.pick_up_flag()
        flag.pick_up_by(player)
        
        player.drop_flag()
        flag.drop_at(10, 10)
        
        assert player.has_flag is False
        assert flag.is_picked_up is False
        assert flag.carried_by is None
    
    def test_flag_follows_player(self, mock_player, mock_flag):
        """测试旗帜跟随玩家移动"""
        player = mock_player("L0", Team.LEFT, 5, 5)
        flag = mock_flag("R0", Team.RIGHT, 5, 5)
        flag.pick_up_by(player)
        
        # 玩家移动
        player.pixel_x = 200.0
        player.pixel_y = 300.0
        
        # 旗帜位置更新
        flag.update_position(player.pixel_x, player.pixel_y)
        
        assert flag.pixel_x == 200.0
        assert flag.pixel_y == 300.0

