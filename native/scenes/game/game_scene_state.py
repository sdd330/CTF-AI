"""
Game scene state management mixin.
Handles game state transitions, scoring, and callbacks.
"""

from typing import TYPE_CHECKING

from ...utils import Team

if TYPE_CHECKING:
    from ...objects.flag import Flag


class GameSceneStateMixin:
    """
    Mixin providing game state management functionality.
    Handles score updates, flag creation, game start/pause/end.
    """

    def _on_score_update(self, team: Team):
        """
        Score update callback (reference frontend: updateTeamScore).

        Frontend logic:
        1. Update GameStateManager score
        2. Update UI
        3. Check game end condition (newScore === NUM_FLAGS)
        """
        if not self.game:
            return

        # Update score (reference frontend: gameState.updateLTeamScore(newScore))
        if team == Team.LEFT:
            new_score = self.game.state.left_team_score + 1
            self.game.state.left_team_score = new_score
        else:
            new_score = self.game.state.right_team_score + 1
            self.game.state.right_team_score = new_score

        # Record stats
        if self.game_stats:
            self.game_stats.record_score(team)

        print(f"[Game] {team.value} team scored! Score: "
              f"L={self.game.state.left_team_score}, R={self.game.state.right_team_score}")

        # Check game end condition (reference frontend: if (newScore === this.NUM_FLAGS))
        num_flags = self.game.state.num_flags
        if new_score == num_flags:
            print(f"[Game] {team.value} team wins ({new_score}/{num_flags})! Game over")
            self._end_game(team)

    def _on_create_flag(self, x: int, y: int, team: Team, can_pickup: bool) -> "Flag":
        """
        Create flag callback.

        Args:
            x: X coordinate (grid)
            y: Y coordinate (grid)
            team: Team
            can_pickup: Whether flag can be picked up

        Returns:
            Created flag object
        """
        from ...objects.flag import Flag

        # Generate flag ID
        flag_id = f"{team.value}{len(self.game.state.get_all_flags())}"

        # Create flag
        flag = Flag(flag_id, team, x, y)

        # Set pickup state
        if not can_pickup:
            flag.is_scored = True

        # Add to appropriate flag group
        if team == Team.LEFT:
            self.game.state.left_team_flags.append(flag)
            if self.left_team_flags_group:
                self.left_team_flags_group.add(flag)
        else:
            self.game.state.right_team_flags.append(flag)
            if self.right_team_flags_group:
                self.right_team_flags_group.add(flag)

        return flag

    def _on_game_start(self):
        """Game start callback (reference frontend: startGame)."""
        if self.game and not self.game.state.game_started:
            self.game.state.game_started = True
            if self.game_stats:
                self.game_stats.start_game()
            # Reset elapsed time for status message
            self._elapsed_time_ms = 0
            # Hide tutorial text (reference frontend: this.uiManager.hideComponent('tutorial'))
            if self.ui_manager:
                self.ui_manager.hide_component('tutorial')
            print("[Game] Game started")

    def _on_game_pause(self):
        """Game pause/resume callback."""
        if self.game and self.game.state.game_started:
            self.game.state.game_paused = not self.game.state.game_paused
            status = "paused" if self.game.state.game_paused else "resumed"
            print(f"[Game] Game {status}")

    def _end_game(self, winner: Team):
        """
        End game.

        Note: Only sets game state, does not switch scenes.
        Scene switching is handled in update() to avoid duplicate switching.
        """
        if self.game:
            self.game.state.game_over = True
            self.game.state.winner = winner
            if self.game_stats:
                self.game_stats.end_game(winner)
            print(f"[Game] Game over, {winner.value} team wins!")
