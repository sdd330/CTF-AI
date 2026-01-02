"""
游戏统计系统
追踪游戏数据和统计信息
"""

import time
from typing import Dict, List, Optional, Deque
from datetime import datetime, timedelta
from collections import deque
from .enums import Team


class PerformanceMonitor:
    """性能监控器"""

    def __init__(self, sample_size: int = 60):
        """
        初始化性能监控器

        Args:
            sample_size: 采样数量（用于计算平均值）
        """
        self.sample_size = sample_size
        self._frame_times: Deque[float] = deque(maxlen=sample_size)
        self._last_frame_time: float = 0.0
        self._frame_count: int = 0
        self._start_time: float = 0.0

    def start(self) -> None:
        """开始监控"""
        self._start_time = time.time()
        self._last_frame_time = self._start_time

    def tick(self) -> float:
        """
        记录一帧

        Returns:
            该帧的增量时间（秒）
        """
        current_time = time.time()
        delta = current_time - self._last_frame_time
        self._last_frame_time = current_time
        self._frame_times.append(delta)
        self._frame_count += 1
        return delta

    def get_fps(self) -> float:
        """获取当前 FPS"""
        if not self._frame_times:
            return 0.0
        avg_frame_time = sum(self._frame_times) / len(self._frame_times)
        if avg_frame_time > 0:
            return 1.0 / avg_frame_time
        return 0.0

    def get_average_frame_time(self) -> float:
        """获取平均帧时间（毫秒）"""
        if not self._frame_times:
            return 0.0
        return (sum(self._frame_times) / len(self._frame_times)) * 1000

    def get_frame_count(self) -> int:
        """获取总帧数"""
        return self._frame_count

    def get_uptime(self) -> float:
        """获取运行时间（秒）"""
        if self._start_time == 0:
            return 0.0
        return time.time() - self._start_time

    def reset(self) -> None:
        """重置监控器"""
        self._frame_times.clear()
        self._last_frame_time = 0.0
        self._frame_count = 0
        self._start_time = 0.0


class GameStats:
    """游戏统计类"""

    def __init__(self):
        """初始化统计系统"""
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None

        # 得分统计
        self.left_score = 0
        self.right_score = 0

        # 玩家统计
        self.player_stats: Dict[str, Dict] = {}

        # 事件统计
        self.events: List[Dict] = []

        # 旗帜统计
        self.flags_captured: Dict[Team, int] = {Team.LEFT: 0, Team.RIGHT: 0}
        self.flags_returned: Dict[Team, int] = {Team.LEFT: 0, Team.RIGHT: 0}

        # 抓捕统计
        self.captures: Dict[Team, int] = {Team.LEFT: 0, Team.RIGHT: 0}

        # 营救统计
        self.rescues: Dict[Team, int] = {Team.LEFT: 0, Team.RIGHT: 0}

        # 性能监控
        self.performance = PerformanceMonitor()
    
    def start_game(self):
        """开始游戏"""
        self.start_time = datetime.now()
        self.performance.start()
        self.events.append({
            "type": "game_start",
            "time": self.start_time,
            "message": "游戏开始"
        })
    
    def end_game(self, winner: Optional[Team] = None):
        """结束游戏"""
        self.end_time = datetime.now()
        self.events.append({
            "type": "game_end",
            "time": self.end_time,
            "winner": winner.value if winner else None,
            "message": f"游戏结束，{'L队' if winner == Team.LEFT else 'R队' if winner == Team.RIGHT else '平局'}获胜"
        })
    
    def record_score(self, team: Team, points: int = 1):
        """
        记录得分
        
        Args:
            team: 得分队伍
            points: 得分数量
        """
        if team == Team.LEFT:
            self.left_score += points
        else:
            self.right_score += points
        
        self.events.append({
            "type": "score",
            "time": datetime.now(),
            "team": team.value,
            "points": points,
            "left_score": self.left_score,
            "right_score": self.right_score,
            "message": f"{team.value}队得分！当前比分 {self.left_score}:{self.right_score}"
        })
    
    def record_flag_captured(self, team: Team, player_name: str):
        """
        记录旗帜被拾取
        
        Args:
            team: 拾取旗帜的队伍
            player_name: 玩家名称
        """
        self.flags_captured[team] += 1
        self.events.append({
            "type": "flag_captured",
            "time": datetime.now(),
            "team": team.value,
            "player": player_name,
            "message": f"{player_name} 拾取了敌方旗帜"
        })
    
    def record_flag_returned(self, team: Team, player_name: str):
        """
        记录旗帜被归还（得分）
        
        Args:
            team: 归还旗帜的队伍
            player_name: 玩家名称
        """
        self.flags_returned[team] += 1
        self.events.append({
            "type": "flag_returned",
            "time": datetime.now(),
            "team": team.value,
            "player": player_name,
            "message": f"{player_name} 归还了敌方旗帜并得分"
        })
    
    def record_capture(self, team: Team, captor: str, captured: str):
        """
        记录玩家被抓捕
        
        Args:
            team: 抓捕方的队伍
            captor: 抓捕者名称
            captured: 被抓捕者名称
        """
        self.captures[team] += 1
        self.events.append({
            "type": "capture",
            "time": datetime.now(),
            "team": team.value,
            "captor": captor,
            "captured": captured,
            "message": f"{captor} 抓捕了 {captured}"
        })
    
    def record_rescue(self, team: Team, rescuer: str, rescued: str):
        """
        记录玩家被营救
        
        Args:
            team: 营救方的队伍
            rescuer: 营救者名称
            rescued: 被营救者名称
        """
        self.rescues[team] += 1
        self.events.append({
            "type": "rescue",
            "time": datetime.now(),
            "team": team.value,
            "rescuer": rescuer,
            "rescued": rescued,
            "message": f"{rescuer} 营救了 {rescued}"
        })
    
    def get_duration(self) -> Optional[timedelta]:
        """
        获取游戏持续时间
        
        Returns:
            游戏持续时间，如果游戏未开始或未结束则返回 None
        """
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        elif self.start_time:
            return datetime.now() - self.start_time
        return None
    
    def get_summary(self) -> Dict:
        """
        获取游戏统计摘要

        Returns:
            统计摘要字典
        """
        duration = self.get_duration()
        return {
            "duration": str(duration) if duration else None,
            "scores": {
                "left": self.left_score,
                "right": self.right_score
            },
            "flags": {
                "captured": dict(self.flags_captured),
                "returned": dict(self.flags_returned)
            },
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
    
    def reset(self):
        """重置统计"""
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
        """
        记录一帧，用于性能监控

        Returns:
            该帧的增量时间（秒）
        """
        return self.performance.tick()

    def get_fps(self) -> float:
        """获取当前 FPS"""
        return self.performance.get_fps()

