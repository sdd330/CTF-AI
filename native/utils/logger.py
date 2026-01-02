"""
日志系统
提供统一的日志记录功能
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


class GameLogger:
    """游戏日志类"""
    
    def __init__(self, name: str = "CTFGame", log_file: Optional[Path] = None, level: int = logging.INFO):
        """
        初始化日志系统
        
        Args:
            name: 日志名称
            log_file: 日志文件路径，如果为 None 则只输出到控制台
            level: 日志级别
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # 避免重复添加处理器
        if self.logger.handlers:
            return
        
        # 创建格式化器
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # 文件处理器（如果指定了日志文件）
        if log_file:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str, *args, **kwargs):
        """记录调试信息"""
        self.logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs):
        """记录信息"""
        self.logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs):
        """记录警告"""
        self.logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, **kwargs):
        """记录错误"""
        self.logger.error(message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs):
        """记录异常（包含堆栈跟踪）"""
        self.logger.exception(message, *args, **kwargs)


# 全局日志实例
_logger_instance: Optional[GameLogger] = None


def get_logger(name: str = "CTFGame", log_file: Optional[Path] = None) -> GameLogger:
    """
    获取全局日志实例（单例模式）
    
    Args:
        name: 日志名称
        log_file: 日志文件路径
    
    Returns:
        日志实例
    """
    global _logger_instance
    if _logger_instance is None:
        if log_file is None:
            # 默认日志文件路径
            log_dir = Path(__file__).parent.parent / "logs"
            log_file = log_dir / f"game_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        _logger_instance = GameLogger(name, log_file)
    return _logger_instance

