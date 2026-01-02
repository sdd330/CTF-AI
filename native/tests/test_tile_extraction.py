"""
测试 tile 提取逻辑
验证 native 的 tile 提取计算是否正确
"""

import pytest
from typing import Tuple


def calculate_tile_position(tile_index: int, tiles_per_row: int = 12, tile_size: int = 32) -> Tuple[int, int, int, int]:
    """
    计算 tile 在 spritesheet 中的位置
    
    Args:
        tile_index: tile 索引（1-based，与 Phaser 的 firstgid=1 对应）
        tiles_per_row: 每行 tile 数量
        tile_size: tile 大小（像素）
    
    Returns:
        (row, col, pixel_x, pixel_y)
    """
    # tile_index 从 1 开始，转换为 0-based
    index = tile_index - 1
    
    # 计算瓦片在 spritesheet 中的位置
    row = index // tiles_per_row
    col = index % tiles_per_row
    
    # 计算像素坐标
    pixel_x = col * tile_size
    pixel_y = row * tile_size
    
    return (row, col, pixel_x, pixel_y)


@pytest.mark.unit
class TestTileExtraction:
    """测试 tile 提取逻辑"""
    
    def test_target_tiles_extraction(self):
        """
        测试目标区域 tile 的提取位置
        target_tiles: [13, 14, 15, 25, 26, 27, 37, 38, 39]
        """
        target_tiles = [13, 14, 15, 25, 26, 27, 37, 38, 39]
        tiles_per_row = 12
        
        expected_positions = [
            # tile 13: row=1, col=0 (第2行第1列)
            (1, 0, 0, 32),
            # tile 14: row=1, col=1 (第2行第2列)
            (1, 1, 32, 32),
            # tile 15: row=1, col=2 (第2行第3列)
            (1, 2, 64, 32),
            # tile 25: row=2, col=0 (第3行第1列)
            (2, 0, 0, 64),
            # tile 26: row=2, col=1 (第3行第2列)
            (2, 1, 32, 64),
            # tile 27: row=2, col=2 (第3行第3列)
            (2, 2, 64, 64),
            # tile 37: row=3, col=0 (第4行第1列)
            (3, 0, 0, 96),
            # tile 38: row=3, col=1 (第4行第2列)
            (3, 1, 32, 96),
            # tile 39: row=3, col=2 (第4行第3列)
            (3, 2, 64, 96),
        ]
        
        for i, tile_index in enumerate(target_tiles):
            row, col, pixel_x, pixel_y = calculate_tile_position(tile_index, tiles_per_row)
            expected_row, expected_col, expected_x, expected_y = expected_positions[i]
            
            assert (row, col, pixel_x, pixel_y) == (expected_row, expected_col, expected_x, expected_y), \
                f"Tile {tile_index} 位置计算错误: 期望 ({expected_row}, {expected_col}, {expected_x}, {expected_y}), " \
                f"实际 ({row}, {col}, {pixel_x}, {pixel_y})"
    
    def test_prison_tiles_extraction(self):
        """
        测试监狱区域 tile 的提取位置
        prison_tiles: [97, 98, 99, 109, 110, 111, 121, 122, 123]
        """
        prison_tiles = [97, 98, 99, 109, 110, 111, 121, 122, 123]
        tiles_per_row = 12
        
        expected_positions = [
            # tile 97: row=8, col=0 (第9行第1列)
            (8, 0, 0, 256),
            # tile 98: row=8, col=1 (第9行第2列)
            (8, 1, 32, 256),
            # tile 99: row=8, col=2 (第9行第3列)
            (8, 2, 64, 256),
            # tile 109: row=9, col=0 (第10行第1列)
            (9, 0, 0, 288),
            # tile 110: row=9, col=1 (第10行第2列)
            (9, 1, 32, 288),
            # tile 111: row=9, col=2 (第10行第3列)
            (9, 2, 64, 288),
            # tile 121: row=10, col=0 (第11行第1列)
            (10, 0, 0, 320),
            # tile 122: row=10, col=1 (第11行第2列)
            (10, 1, 32, 320),
            # tile 123: row=10, col=2 (第11行第3列)
            (10, 2, 64, 320),
        ]
        
        for i, tile_index in enumerate(prison_tiles):
            row, col, pixel_x, pixel_y = calculate_tile_position(tile_index, tiles_per_row)
            expected_row, expected_col, expected_x, expected_y = expected_positions[i]
            
            assert (row, col, pixel_x, pixel_y) == (expected_row, expected_col, expected_x, expected_y), \
                f"Tile {tile_index} 位置计算错误: 期望 ({expected_row}, {expected_col}, {expected_x}, {expected_y}), " \
                f"实际 ({row}, {col}, {pixel_x}, {pixel_y})"
    
    def test_tile_index_calculation(self):
        """
        验证 tile 索引计算逻辑
        """
        test_cases = [
            (1, 0, 0, 0, 0),      # 第1个 tile: row=0, col=0
            (12, 0, 11, 352, 0),  # 第12个 tile: row=0, col=11
            (13, 1, 0, 0, 32),    # 第13个 tile: row=1, col=0
            (25, 2, 0, 0, 64),    # 第25个 tile: row=2, col=0
            (37, 3, 0, 0, 96),    # 第37个 tile: row=3, col=0
            (97, 8, 0, 0, 256),   # 第97个 tile: row=8, col=0
            (109, 9, 0, 0, 288),  # 第109个 tile: row=9, col=0
            (121, 10, 0, 0, 320), # 第121个 tile: row=10, col=0
        ]
        
        for tile_index, expected_row, expected_col, expected_x, expected_y in test_cases:
            row, col, pixel_x, pixel_y = calculate_tile_position(tile_index)
            
            assert row == expected_row, \
                f"Tile {tile_index} row 计算错误: 期望 {expected_row}, 实际 {row}"
            assert col == expected_col, \
                f"Tile {tile_index} col 计算错误: 期望 {expected_col}, 实际 {col}"
            assert pixel_x == expected_x, \
                f"Tile {tile_index} pixel_x 计算错误: 期望 {expected_x}, 实际 {pixel_x}"
            assert pixel_y == expected_y, \
                f"Tile {tile_index} pixel_y 计算错误: 期望 {expected_y}, 实际 {pixel_y}"
    
    def test_tiles_per_row_boundary(self):
        """
        测试 tiles_per_row 边界情况
        """
        # 验证每行的 tile 范围
        for row in range(11):  # 11 行（0-10）
            # 每行的第一个 tile: row * 12 + 1
            first_tile = row * 12 + 1
            row_first, col_first, _, _ = calculate_tile_position(first_tile)
            assert row_first == row, f"第 {row+1} 行的第一个 tile {first_tile} row 计算错误"
            assert col_first == 0, f"第 {row+1} 行的第一个 tile {first_tile} col 应该是 0"
            
            # 每行的最后一个 tile: row * 12 + 12 (col=11，即第12列，索引为11)
            if row < 10:  # 最后一行不需要检查
                last_tile = row * 12 + 12
                row_last, col_last, _, _ = calculate_tile_position(last_tile)
                # 最后一个 tile 的 col 应该是 11（第12列），row 应该是当前行
                assert row_last == row, f"第 {row+1} 行的最后一个 tile {last_tile} row 应该是 {row}"
                assert col_last == 11, f"第 {row+1} 行的最后一个 tile {last_tile} col 应该是 11"
                
                # 验证下一行的第一个 tile
                next_first_tile = (row + 1) * 12 + 1
                row_next, col_next, _, _ = calculate_tile_position(next_first_tile)
                assert row_next == row + 1, f"第 {row+2} 行的第一个 tile {next_first_tile} row 应该是 {row+1}"
                assert col_next == 0, f"第 {row+2} 行的第一个 tile {next_first_tile} col 应该是 0"
