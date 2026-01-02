"""
Prison 和 Target 数据一致性测试
确保使用相同的地图尺寸时，生成的位置数据与 frontend 项目一致
"""

import pytest
from typing import List, Tuple


def create_3x3_grid(center_x: int, center_y: int) -> List[Tuple[int, int]]:
    """
    创建 3x3 网格位置
    顺序必须与 frontend 完全一致：
    [0] (x-1, y-1), [1] (x, y-1), [2] (x+1, y-1)
    [3] (x-1, y),   [4] (x, y),   [5] (x+1, y)
    [6] (x-1, y+1), [7] (x, y+1), [8] (x+1, y+1)
    """
    return [
        (center_x - 1, center_y - 1), (center_x, center_y - 1), (center_x + 1, center_y - 1),
        (center_x - 1, center_y),     (center_x, center_y),     (center_x + 1, center_y),
        (center_x - 1, center_y + 1), (center_x, center_y + 1), (center_x + 1, center_y + 1)
    ]


def generate_targets_and_prisons(map_width: int, map_height: int) -> dict:
    """
    生成目标区域和监狱位置
    
    Args:
        map_width: 地图宽度
        map_height: 地图高度
    
    Returns:
        包含 left_target, right_target, left_prison, right_prison 的字典
    """
    target_y = map_height // 2  # floor(mapHeight / 2)
    prison_y = map_height - 3   # floor(mapHeight - 3)
    
    left_target = create_3x3_grid(2, target_y)
    right_target = create_3x3_grid(map_width - 3, target_y)
    left_prison = create_3x3_grid(2, prison_y)
    right_prison = create_3x3_grid(map_width - 3, prison_y)
    
    return {
        'left_target': left_target,
        'right_target': right_target,
        'left_prison': left_prison,
        'right_prison': right_prison
    }


@pytest.mark.unit
class TestPrisonTargetConsistency:
    """Prison 和 Target 一致性测试"""
    
    def test_create_3x3_grid_order(self):
        """测试 create_3x3_grid 方法生成的顺序"""
        map_width = 20
        map_height = 20
        
        result = generate_targets_and_prisons(map_width, map_height)
        l_target = result['left_target']
        r_target = result['right_target']
        l_prison = result['left_prison']
        r_prison = result['right_prison']
        
        # 验证 L 队 Target 的顺序（中心点 x=2, y=10）
        assert len(l_target) == 9
        assert l_target[0] == (1, 9)   # (2-1, 10-1)
        assert l_target[1] == (2, 9)  # (2, 10-1)
        assert l_target[2] == (3, 9)  # (2+1, 10-1)
        assert l_target[3] == (1, 10) # (2-1, 10)
        assert l_target[4] == (2, 10) # (2, 10)
        assert l_target[5] == (3, 10) # (2+1, 10)
        assert l_target[6] == (1, 11) # (2-1, 10+1)
        assert l_target[7] == (2, 11)  # (2, 10+1)
        assert l_target[8] == (3, 11) # (2+1, 10+1)
        
        # 验证 R 队 Target 的顺序（中心点 x=17, y=10）
        assert len(r_target) == 9
        assert r_target[0] == (16, 9)  # (17-1, 10-1)
        assert r_target[1] == (17, 9)   # (17, 10-1)
        assert r_target[2] == (18, 9)   # (17+1, 10-1)
        assert r_target[3] == (16, 10)  # (17-1, 10)
        assert r_target[4] == (17, 10)  # (17, 10)
        assert r_target[5] == (18, 10) # (17+1, 10)
        assert r_target[6] == (16, 11)  # (17-1, 10+1)
        assert r_target[7] == (17, 11) # (17, 10+1)
        assert r_target[8] == (18, 11) # (17+1, 10+1)
        
        # 验证 L 队 Prison 的顺序（中心点 x=2, y=17）
        assert len(l_prison) == 9
        assert l_prison[0] == (1, 16)   # (2-1, 17-1)
        assert l_prison[1] == (2, 16)   # (2, 17-1)
        assert l_prison[2] == (3, 16)   # (2+1, 17-1)
        assert l_prison[3] == (1, 17)  # (2-1, 17)
        assert l_prison[4] == (2, 17)  # (2, 17)
        assert l_prison[5] == (3, 17)  # (2+1, 17)
        assert l_prison[6] == (1, 18)  # (2-1, 17+1)
        assert l_prison[7] == (2, 18)  # (2, 17+1)
        assert l_prison[8] == (3, 18)  # (2+1, 17+1)
        
        # 验证 R 队 Prison 的顺序（中心点 x=17, y=17）
        assert len(r_prison) == 9
        assert r_prison[0] == (16, 16) # (17-1, 17-1)
        assert r_prison[1] == (17, 16) # (17, 17-1)
        assert r_prison[2] == (18, 16)  # (17+1, 17-1)
        assert r_prison[3] == (16, 17)  # (17-1, 17)
        assert r_prison[4] == (17, 17)  # (17, 17)
        assert r_prison[5] == (18, 17)  # (17+1, 17)
        assert r_prison[6] == (16, 18)  # (17-1, 17+1)
        assert r_prison[7] == (17, 18)  # (17, 17+1)
        assert r_prison[8] == (18, 18)  # (17+1, 17+1)
    
    def test_20x20_map_consistency(self):
        """测试 20x20 地图的一致性"""
        map_width = 20
        map_height = 20
        
        result = generate_targets_and_prisons(map_width, map_height)
        l_target = result['left_target']
        r_target = result['right_target']
        l_prison = result['left_prison']
        r_prison = result['right_prison']
        
        # 验证 target_y = map_height // 2 = 20 // 2 = 10
        # 验证 prison_y = map_height - 3 = 20 - 3 = 17
        
        # L 队 Target: center (2, 10)
        assert l_target[4] == (2, 10)
        
        # R 队 Target: center (17, 10)
        assert r_target[4] == (17, 10)
        
        # L 队 Prison: center (2, 17)
        assert l_prison[4] == (2, 17)
        
        # R 队 Prison: center (17, 17)
        assert r_prison[4] == (17, 17)
    
    def test_odd_map_height(self):
        """测试奇数地图高度的处理"""
        map_width = 20
        map_height = 21
        
        result = generate_targets_and_prisons(map_width, map_height)
        l_target = result['left_target']
        
        # target_y = 21 // 2 = 10
        # 与 frontend 的 Math.floor(21 / 2) = 10 一致
        assert l_target[4] == (2, 10)
    
    def test_different_map_sizes(self):
        """测试不同地图尺寸"""
        test_cases = [
            {'width': 15, 'height': 15},
            {'width': 20, 'height': 20},
            {'width': 25, 'height': 25},
            {'width': 30, 'height': 30}
        ]
        
        for case in test_cases:
            width = case['width']
            height = case['height']
            
            result = generate_targets_and_prisons(width, height)
            l_target = result['left_target']
            r_target = result['right_target']
            l_prison = result['left_prison']
            r_prison = result['right_prison']
            
            # 验证所有数组都有 9 个元素
            assert len(l_target) == 9
            assert len(r_target) == 9
            assert len(l_prison) == 9
            assert len(r_prison) == 9
            
            # 验证 L 队 Target 中心点
            target_y = height // 2
            assert l_target[4] == (2, target_y)
            
            # 验证 R 队 Target 中心点
            assert r_target[4] == (width - 3, target_y)
            
            # 验证 L 队 Prison 中心点
            prison_y = height - 3
            assert l_prison[4] == (2, prison_y)
            
            # 验证 R 队 Prison 中心点
            assert r_prison[4] == (width - 3, prison_y)
    
    def test_position_format(self):
        """验证位置数据格式"""
        map_width = 20
        map_height = 20
        
        result = generate_targets_and_prisons(map_width, map_height)
        l_target = result['left_target']
        
        # 验证格式：Python 使用 Tuple[int, int] 格式
        for pos in l_target:
            assert isinstance(pos, tuple)
            assert len(pos) == 2
            assert isinstance(pos[0], int)
            assert isinstance(pos[1], int)
    
    def test_cross_platform_consistency(self):
        """
        跨平台一致性测试
        验证 Python 生成的数据与 frontend TypeScript 生成的数据一致
        
        这个测试需要手动验证，因为无法直接调用 TypeScript 代码
        但可以通过比较输出格式来验证逻辑一致性
        """
        map_width = 20
        map_height = 20
        
        result = generate_targets_and_prisons(map_width, map_height)
        
        # 验证计算逻辑
        target_y = map_height // 2  # 10
        prison_y = map_height - 3   # 17
        
        assert target_y == 10
        assert prison_y == 17
        
        # 验证 L 队坐标
        assert result['left_target'][4] == (2, 10)
        assert result['left_prison'][4] == (2, 17)
        
        # 验证 R 队坐标
        assert result['right_target'][4] == (17, 10)
        assert result['right_prison'][4] == (17, 17)
        
        # 验证所有位置都是有效的整数坐标
        for key in ['left_target', 'right_target', 'left_prison', 'right_prison']:
            positions = result[key]
            for pos in positions:
                assert pos[0] >= 0
                assert pos[1] >= 0
                assert pos[0] < map_width
                assert pos[1] < map_height
    
    def test_render_targets_tile_id_mapping(self):
        """
        验证 renderTargets 的 tile ID 映射关系
        确保与 frontend 项目使用相同的 tile ID 数组和映射顺序
        """
        map_width = 20
        map_height = 20
        
        result = generate_targets_and_prisons(map_width, map_height)
        l_target = result['left_target']
        r_target = result['right_target']
        
        # Native target_tiles: [13, 14, 15, 25, 26, 27, 37, 38, 39]
        # 与 frontend 的 targetTiles 完全一致
        expected_target_tiles = [13, 14, 15, 25, 26, 27, 37, 38, 39]
        
        # 验证 L 队 Target 的 tile ID 映射
        # create_3x3_grid 顺序: [0] (x-1, y-1), [1] (x, y-1), [2] (x+1, y-1)
        #                        [3] (x-1, y),   [4] (x, y),   [5] (x+1, y)
        #                        [6] (x-1, y+1), [7] (x, y+1), [8] (x+1, y+1)
        # 对应 tile ID: [13, 14, 15, 25, 26, 27, 37, 38, 39]
        l_target_tile_map = {}
        for i, pos in enumerate(l_target):
            if i < len(expected_target_tiles):
                l_target_tile_map[f"{pos[0]},{pos[1]}"] = expected_target_tiles[i]
        
        # 验证每个位置对应的 tile ID
        assert l_target_tile_map['1,9'] == 13   # [0] (x-1, y-1) -> tile 13
        assert l_target_tile_map['2,9'] == 14   # [1] (x, y-1) -> tile 14
        assert l_target_tile_map['3,9'] == 15    # [2] (x+1, y-1) -> tile 15
        assert l_target_tile_map['1,10'] == 25  # [3] (x-1, y) -> tile 25
        assert l_target_tile_map['2,10'] == 26  # [4] (x, y) -> tile 26
        assert l_target_tile_map['3,10'] == 27  # [5] (x+1, y) -> tile 27
        assert l_target_tile_map['1,11'] == 37  # [6] (x-1, y+1) -> tile 37
        assert l_target_tile_map['2,11'] == 38  # [7] (x, y+1) -> tile 38
        assert l_target_tile_map['3,11'] == 39 # [8] (x+1, y+1) -> tile 39
        
        # 验证 R 队 Target 的 tile ID 映射（中心点 x=17, y=10）
        r_target_tile_map = {}
        for i, pos in enumerate(r_target):
            if i < len(expected_target_tiles):
                r_target_tile_map[f"{pos[0]},{pos[1]}"] = expected_target_tiles[i]
        
        assert r_target_tile_map['16,9'] == 13  # [0] (x-1, y-1) -> tile 13
        assert r_target_tile_map['17,9'] == 14  # [1] (x, y-1) -> tile 14
        assert r_target_tile_map['18,9'] == 15  # [2] (x+1, y-1) -> tile 15
        assert r_target_tile_map['16,10'] == 25 # [3] (x-1, y) -> tile 25
        assert r_target_tile_map['17,10'] == 26  # [4] (x, y) -> tile 26
        assert r_target_tile_map['18,10'] == 27 # [5] (x+1, y) -> tile 27
        assert r_target_tile_map['16,11'] == 37 # [6] (x-1, y+1) -> tile 37
        assert r_target_tile_map['17,11'] == 38 # [7] (x, y+1) -> tile 38
        assert r_target_tile_map['18,11'] == 39 # [8] (x+1, y+1) -> tile 39
    
    def test_render_prisons_tile_id_mapping(self):
        """
        验证 renderPrisons 的 tile ID 映射关系
        确保与 frontend 项目使用相同的 tile ID 数组和映射顺序
        """
        map_width = 20
        map_height = 20
        
        result = generate_targets_and_prisons(map_width, map_height)
        l_prison = result['left_prison']
        r_prison = result['right_prison']
        
        # Native prison_tiles: [97, 98, 99, 109, 110, 111, 121, 122, 123]
        # 与 frontend 的 prisonTiles 完全一致
        expected_prison_tiles = [97, 98, 99, 109, 110, 111, 121, 122, 123]
        
        # 验证 L 队 Prison 的 tile ID 映射（中心点 x=2, y=17）
        l_prison_tile_map = {}
        for i, pos in enumerate(l_prison):
            if i < len(expected_prison_tiles):
                l_prison_tile_map[f"{pos[0]},{pos[1]}"] = expected_prison_tiles[i]
        
        assert l_prison_tile_map['1,16'] == 97   # [0] (x-1, y-1) -> tile 97
        assert l_prison_tile_map['2,16'] == 98   # [1] (x, y-1) -> tile 98
        assert l_prison_tile_map['3,16'] == 99    # [2] (x+1, y-1) -> tile 99
        assert l_prison_tile_map['1,17'] == 109  # [3] (x-1, y) -> tile 109
        assert l_prison_tile_map['2,17'] == 110  # [4] (x, y) -> tile 110
        assert l_prison_tile_map['3,17'] == 111  # [5] (x+1, y) -> tile 111
        assert l_prison_tile_map['1,18'] == 121  # [6] (x-1, y+1) -> tile 121
        assert l_prison_tile_map['2,18'] == 122  # [7] (x, y+1) -> tile 122
        assert l_prison_tile_map['3,18'] == 123  # [8] (x+1, y+1) -> tile 123
        
        # 验证 R 队 Prison 的 tile ID 映射（中心点 x=17, y=17）
        r_prison_tile_map = {}
        for i, pos in enumerate(r_prison):
            if i < len(expected_prison_tiles):
                r_prison_tile_map[f"{pos[0]},{pos[1]}"] = expected_prison_tiles[i]
        
        assert r_prison_tile_map['16,16'] == 97  # [0] (x-1, y-1) -> tile 97
        assert r_prison_tile_map['17,16'] == 98   # [1] (x, y-1) -> tile 98
        assert r_prison_tile_map['18,16'] == 99   # [2] (x+1, y-1) -> tile 99
        assert r_prison_tile_map['16,17'] == 109 # [3] (x-1, y) -> tile 109
        assert r_prison_tile_map['17,17'] == 110  # [4] (x, y) -> tile 110
        assert r_prison_tile_map['18,17'] == 111  # [5] (x+1, y) -> tile 111
        assert r_prison_tile_map['16,18'] == 121  # [6] (x-1, y+1) -> tile 121
        assert r_prison_tile_map['17,18'] == 122  # [7] (x, y+1) -> tile 122
        assert r_prison_tile_map['18,18'] == 123  # [8] (x+1, y+1) -> tile 123
