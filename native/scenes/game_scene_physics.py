"""Game scene physics controller - collision and physics handling"""

import pygame
from typing import Optional, TYPE_CHECKING
from ..utils import Team
from ..managers import PhysicsManager, CollisionCallbacks

if TYPE_CHECKING:
    from .game_scene import GameScene


class GameScenePhysicsController:
    """Handles physics and collision for the game scene."""

    def __init__(self, scene: 'GameScene'):
        self.scene = scene
        self.physics_manager: Optional[PhysicsManager] = None
        self.left_team_players_group: Optional[pygame.sprite.Group] = None
        self.right_team_players_group: Optional[pygame.sprite.Group] = None
        self.left_team_flags_group: Optional[pygame.sprite.Group] = None
        self.right_team_flags_group: Optional[pygame.sprite.Group] = None

    def setup(self):
        """Setup physics manager with sprite groups."""
        game = self.scene.game
        if not game:
            return

        # Create sprite groups
        self.left_team_players_group = pygame.sprite.Group()
        self.right_team_players_group = pygame.sprite.Group()
        self.left_team_flags_group = pygame.sprite.Group()
        self.right_team_flags_group = pygame.sprite.Group()

        # Add players and flags to groups
        for player in game.state.left_team_players:
            self.left_team_players_group.add(player)
        for player in game.state.right_team_players:
            self.right_team_players_group.add(player)
        for flag in game.state.left_team_flags:
            self.left_team_flags_group.add(flag)
        for flag in game.state.right_team_flags:
            self.right_team_flags_group.add(flag)

        # Create collision callbacks
        callbacks = CollisionCallbacks()
        callbacks.on_score_update = self._on_score_update
        callbacks.on_create_flag = self._on_create_flag

        # Create physics manager
        self.physics_manager = PhysicsManager(game.game_map, callbacks)
        self.physics_manager.set_game_objects(
            self.left_team_players_group, self.right_team_players_group,
            self.left_team_flags_group, self.right_team_flags_group
        )

        # Setup zones from map
        game_map = game.game_map
        left_target = [(p.x, p.y) for p in game_map.get_team_target_positions(Team.LEFT)]
        right_target = [(p.x, p.y) for p in game_map.get_team_target_positions(Team.RIGHT)]
        left_prison = [(p.x, p.y) for p in game_map.get_team_prison_positions(Team.LEFT)]
        right_prison = [(p.x, p.y) for p in game_map.get_team_prison_positions(Team.RIGHT)]
        self.physics_manager.set_zones(left_target, right_target, left_prison, right_prison)
        print("[Game] Physics manager setup complete")

    def _on_score_update(self, team: Team):
        """Score update callback."""
        game = self.scene.game
        if not game:
            return

        if team == Team.LEFT:
            new_score = game.state.left_team_score + 1
            game.state.left_team_score = new_score
        else:
            new_score = game.state.right_team_score + 1
            game.state.right_team_score = new_score

        if self.scene.game_stats:
            self.scene.game_stats.record_score(team)

        print(f"[Game] {team.value} team scored! Score: L={game.state.left_team_score}, R={game.state.right_team_score}")

        # Check win condition
        if new_score == game.state.num_flags:
            print(f"[Game] {team.value} team wins ({new_score}/{game.state.num_flags})! Game over")
            self.scene._end_game(team)

    def _on_create_flag(self, x: int, y: int, team: Team, can_pickup: bool):
        """Create flag callback."""
        from ..objects.flag import Flag
        game = self.scene.game

        flag_id = f"{team.value}{len(game.state.get_all_flags())}"
        flag = Flag(flag_id, team, x, y)
        if not can_pickup:
            flag.is_scored = True

        if team == Team.LEFT:
            game.state.left_team_flags.append(flag)
            if self.left_team_flags_group:
                self.left_team_flags_group.add(flag)
        else:
            game.state.right_team_flags.append(flag)
            if self.right_team_flags_group:
                self.right_team_flags_group.add(flag)
        return flag

    def update(self):
        """Update physics system."""
        if self.physics_manager:
            self.physics_manager.update()
