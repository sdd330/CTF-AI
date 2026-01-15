"""
Team state generator for game initialization.
"""

import random
from typing import List

from .models import Position, PlayerPosition, GameConfig


class TeamGenerator:
    """Generates team states including flags, players, targets, and prisons."""

    @staticmethod
    def create_3x3_grid(center_x: int, center_y: int) -> List[Position]:
        """Create a 3x3 grid of positions."""
        return [
            Position(x=center_x - 1, y=center_y - 1),
            Position(x=center_x, y=center_y - 1),
            Position(x=center_x + 1, y=center_y - 1),
            Position(x=center_x - 1, y=center_y),
            Position(x=center_x, y=center_y),
            Position(x=center_x + 1, y=center_y),
            Position(x=center_x - 1, y=center_y + 1),
            Position(x=center_x, y=center_y + 1),
            Position(x=center_x + 1, y=center_y + 1),
        ]

    @staticmethod
    def generate_targets_and_prisons(
        map_width: int, map_height: int
    ) -> tuple:
        """
        Generate target areas and prison positions for both teams.

        Returns:
            Tuple of (l_target, l_prison, r_target, r_prison)
        """
        target_y = map_height // 2
        prison_y = map_height - 3

        l_target = TeamGenerator.create_3x3_grid(2, target_y)
        l_prison = TeamGenerator.create_3x3_grid(2, prison_y)
        r_target = TeamGenerator.create_3x3_grid(map_width - 3, target_y)
        r_prison = TeamGenerator.create_3x3_grid(map_width - 3, prison_y)

        return l_target, l_prison, r_target, r_prison

    @staticmethod
    def generate_players(
        map_width: int, config: GameConfig
    ) -> tuple:
        """
        Generate player positions for both teams.

        Returns:
            Tuple of (l_players, r_players)
        """
        num_players = config.num_players
        use_random_flags = config.use_random_flags

        if use_random_flags:
            l_players = [
                PlayerPosition(name=f"L{i}", x=1, y=i + 1)
                for i in range(num_players)
            ]
            r_players = [
                PlayerPosition(name=f"R{i}", x=map_width - 2, y=i + 1)
                for i in range(num_players)
            ]
        else:
            l_players = [
                PlayerPosition(name=f"L{i}", x=2, y=i + 1)
                for i in range(num_players)
            ]
            r_players = [
                PlayerPosition(name=f"R{i}", x=map_width - 3, y=i + 1)
                for i in range(num_players)
            ]

        return l_players, r_players

    @staticmethod
    def generate_flags(
        map_width: int,
        map_height: int,
        config: GameConfig,
        obstacles1: List[Position],
        obstacles2: List[Position]
    ) -> tuple:
        """
        Generate flag positions for both teams.

        Returns:
            Tuple of (l_flags, r_flags)
        """
        num_flags = config.num_flags
        use_random_flags = config.use_random_flags

        middle_line = map_width / 2.0
        l_max_x = int(middle_line - 0.1)
        r_min_x = int(middle_line + 0.5)

        def not_contains(arr: List[Position], x: int, y: int) -> bool:
            return not any(p.x == x and p.y == y for p in arr)

        if use_random_flags:
            l_flags = TeamGenerator._generate_random_flags(
                num_flags, 2, l_max_x, map_height, obstacles1, obstacles2
            )
            r_flags = TeamGenerator._generate_random_flags(
                num_flags, r_min_x, map_width - 2, map_height, obstacles1, obstacles2
            )
        else:
            l_flags = [
                Position(x=min(1, l_max_x), y=i + 1)
                for i in range(num_flags)
            ]
            r_flags = [
                Position(x=max(r_min_x, map_width - 2), y=i + 1)
                for i in range(num_flags)
            ]

        return l_flags, r_flags

    @staticmethod
    def _generate_random_flags(
        num_flags: int,
        min_x: int,
        max_x: int,
        map_height: int,
        obstacles1: List[Position],
        obstacles2: List[Position]
    ) -> List[Position]:
        """Generate random flag positions avoiding obstacles."""
        flags = []
        max_retries = 1000

        def not_contains(arr: List[Position], x: int, y: int) -> bool:
            return not any(p.x == x and p.y == y for p in arr)

        for i in range(num_flags):
            for _ in range(max_retries):
                x = random.randint(min_x, max_x)
                y = random.randint(1, map_height - 3)
                if (not_contains(obstacles1, x, y) and
                    not_contains(obstacles2, x, y - 1) and
                    not_contains(obstacles2, x, y) and
                    not_contains(flags, x, y)):
                    flags.append(Position(x=x, y=y))
                    break
            else:
                flags.append(Position(x=min_x, y=i + 1))

        return flags
