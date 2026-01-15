"""Game statistics system - tracking game data and stats"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from .enums import Team
from .performance import PerformanceMonitor

# Re-export for backward compatibility
__all__ = ['GameStats', 'PerformanceMonitor']


class GameStats:
    """Game statistics class."""

    def __init__(self):
        """Initialize statistics system."""
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

        # Score stats
        self.left_score = 0
        self.right_score = 0

        # Player stats
        self.player_stats: Dict[str, Dict] = {}

        # Event stats
        self.events: List[Dict] = []

        # Flag stats
        self.flags_captured: Dict[Team, int] = {Team.LEFT: 0, Team.RIGHT: 0}
        self.flags_returned: Dict[Team, int] = {Team.LEFT: 0, Team.RIGHT: 0}

        # Capture stats
        self.captures: Dict[Team, int] = {Team.LEFT: 0, Team.RIGHT: 0}

        # Rescue stats
        self.rescues: Dict[Team, int] = {Team.LEFT: 0, Team.RIGHT: 0}

        # Performance monitor
        self.performance = PerformanceMonitor()

    def start_game(self) -> None:
        """Start game."""
        self.start_time = datetime.now()
        self.performance.start()
        self.events.append({
            "type": "game_start", "time": self.start_time, "message": "Game started"
        })

    def end_game(self, winner: Optional[Team] = None) -> None:
        """End game."""
        self.end_time = datetime.now()
        winner_msg = f"{'L team' if winner == Team.LEFT else 'R team' if winner == Team.RIGHT else 'Draw'} wins"
        self.events.append({
            "type": "game_end", "time": self.end_time,
            "winner": winner.value if winner else None, "message": f"Game over, {winner_msg}"
        })

    def record_score(self, team: Team, points: int = 1) -> None:
        """Record score."""
        if team == Team.LEFT:
            self.left_score += points
        else:
            self.right_score += points

        self.events.append({
            "type": "score", "time": datetime.now(), "team": team.value, "points": points,
            "left_score": self.left_score, "right_score": self.right_score,
            "message": f"{team.value} team scored! Score: {self.left_score}:{self.right_score}"
        })

    def record_flag_captured(self, team: Team, player_name: str) -> None:
        """Record flag captured."""
        self.flags_captured[team] += 1
        self.events.append({
            "type": "flag_captured", "time": datetime.now(),
            "team": team.value, "player": player_name,
            "message": f"{player_name} captured enemy flag"
        })

    def record_flag_returned(self, team: Team, player_name: str) -> None:
        """Record flag returned (scored)."""
        self.flags_returned[team] += 1
        self.events.append({
            "type": "flag_returned", "time": datetime.now(),
            "team": team.value, "player": player_name,
            "message": f"{player_name} returned enemy flag and scored"
        })

    def record_capture(self, team: Team, captor: str, captured: str) -> None:
        """Record player captured."""
        self.captures[team] += 1
        self.events.append({
            "type": "capture", "time": datetime.now(),
            "team": team.value, "captor": captor, "captured": captured,
            "message": f"{captor} captured {captured}"
        })

    def record_rescue(self, team: Team, rescuer: str, rescued: str) -> None:
        """Record player rescued."""
        self.rescues[team] += 1
        self.events.append({
            "type": "rescue", "time": datetime.now(),
            "team": team.value, "rescuer": rescuer, "rescued": rescued,
            "message": f"{rescuer} rescued {rescued}"
        })

    def get_duration(self) -> Optional[timedelta]:
        """Get game duration."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        elif self.start_time:
            return datetime.now() - self.start_time
        return None

    def get_summary(self) -> Dict:
        """Get game statistics summary."""
        duration = self.get_duration()
        return {
            "duration": str(duration) if duration else None,
            "scores": {"left": self.left_score, "right": self.right_score},
            "flags": {"captured": dict(self.flags_captured), "returned": dict(self.flags_returned)},
            "captures": dict(self.captures),
            "rescues": dict(self.rescues),
            "total_events": len(self.events),
            "performance": {
                "fps": round(self.performance.get_fps(), 1),
                "avg_frame_time_ms": round(self.performance.get_average_frame_time(), 2),
                "total_frames": self.performance.get_frame_count(),
                "uptime_seconds": round(self.performance.get_uptime(), 1)
            }
        }

    def reset(self) -> None:
        """Reset statistics."""
        self.start_time = None
        self.end_time = None
        self.left_score = 0
        self.right_score = 0
        self.player_stats.clear()
        self.events.clear()
        self.flags_captured = {Team.LEFT: 0, Team.RIGHT: 0}
        self.flags_returned = {Team.LEFT: 0, Team.RIGHT: 0}
        self.captures = {Team.LEFT: 0, Team.RIGHT: 0}
        self.rescues = {Team.LEFT: 0, Team.RIGHT: 0}
        self.performance.reset()

    def tick(self) -> float:
        """Record a frame for performance monitoring."""
        return self.performance.tick()

    def get_fps(self) -> float:
        """Get current FPS."""
        return self.performance.get_fps()
