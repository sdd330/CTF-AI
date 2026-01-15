"""Performance monitoring utilities"""

import time
from typing import Deque
from collections import deque


class PerformanceMonitor:
    """Performance monitor for tracking frame times and FPS."""

    def __init__(self, sample_size: int = 60):
        """
        Initialize performance monitor.

        Args:
            sample_size: Number of samples for averaging
        """
        self.sample_size = sample_size
        self._frame_times: Deque[float] = deque(maxlen=sample_size)
        self._last_frame_time: float = 0.0
        self._frame_count: int = 0
        self._start_time: float = 0.0

    def start(self) -> None:
        """Start monitoring."""
        self._start_time = time.time()
        self._last_frame_time = self._start_time

    def tick(self) -> float:
        """
        Record a frame.

        Returns:
            Delta time for this frame (seconds)
        """
        current_time = time.time()
        delta = current_time - self._last_frame_time
        self._last_frame_time = current_time
        self._frame_times.append(delta)
        self._frame_count += 1
        return delta

    def get_fps(self) -> float:
        """Get current FPS."""
        if not self._frame_times:
            return 0.0
        avg_frame_time = sum(self._frame_times) / len(self._frame_times)
        if avg_frame_time > 0:
            return 1.0 / avg_frame_time
        return 0.0

    def get_average_frame_time(self) -> float:
        """Get average frame time (milliseconds)."""
        if not self._frame_times:
            return 0.0
        return (sum(self._frame_times) / len(self._frame_times)) * 1000

    def get_frame_count(self) -> int:
        """Get total frame count."""
        return self._frame_count

    def get_uptime(self) -> float:
        """Get uptime (seconds)."""
        if self._start_time == 0:
            return 0.0
        return time.time() - self._start_time

    def reset(self) -> None:
        """Reset monitor."""
        self._frame_times.clear()
        self._last_frame_time = 0.0
        self._frame_count = 0
        self._start_time = 0.0
