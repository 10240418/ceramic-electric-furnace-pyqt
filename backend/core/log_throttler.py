"""
日志限流器 - 防止重复错误日志刷屏
"""
import threading
from datetime import datetime, timedelta
from typing import Dict, Optional
from loguru import logger


class ErrorLogThrottler:
    """错误日志限流器 - 单例模式
    
    功能：
    1. 同一类型的错误，只在首次发生时记录
    2. 之后每隔指定时间（默认60秒）才记录一次
    3. 避免连接失败等错误日志刷屏
    """
    
    _instance: Optional['ErrorLogThrottler'] = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, throttle_seconds: int = 60):
        """
        初始化日志限流器
        
        Args:
            throttle_seconds: 限流时间间隔（秒），默认60秒
        """
        if self._initialized:
            return
        
        self._initialized = True
        self._throttle_seconds = throttle_seconds
        self._last_log_time: Dict[str, datetime] = {}
        self._error_count: Dict[str, int] = {}
        self._data_lock = threading.Lock()
    
    def should_log(self, error_key: str) -> bool:
        """判断是否应该记录日志
        
        Args:
            error_key: 错误类型标识（如 "plc_connect_failed", "influxdb_write_failed"）
            
        Returns:
            True: 应该记录日志, False: 跳过日志
        """
        with self._data_lock:
            now = datetime.now()
            
            # 首次出现，记录日志
            if error_key not in self._last_log_time:
                self._last_log_time[error_key] = now
                self._error_count[error_key] = 1
                return True
            
            # 检查是否超过限流时间
            last_time = self._last_log_time[error_key]
            elapsed = (now - last_time).total_seconds()
            
            # 累计错误次数
            self._error_count[error_key] += 1
            
            if elapsed >= self._throttle_seconds:
                # 超过限流时间，记录日志并重置计时
                self._last_log_time[error_key] = now
                return True
            
            # 未超过限流时间，跳过日志
            return False
    
    def log_error(self, error_key: str, message: str, exc_info: bool = False):
        """记录错误日志（带限流）
        
        Args:
            error_key: 错误类型标识
            message: 错误消息
            exc_info: 是否包含异常堆栈
        """
        if self.should_log(error_key):
            # 获取累计错误次数
            count = self._error_count.get(error_key, 1)
            
            if count > 1:
                # 不是首次错误，附加累计次数信息
                message = f"{message} (累计 {count} 次)"
            
            logger.error(message, exc_info=exc_info)
    
    def reset(self, error_key: Optional[str] = None):
        """重置限流状态
        
        Args:
            error_key: 错误类型标识，None 表示重置所有
        """
        with self._data_lock:
            if error_key is None:
                self._last_log_time.clear()
                self._error_count.clear()
            else:
                self._last_log_time.pop(error_key, None)
                self._error_count.pop(error_key, None)
    
    def get_error_count(self, error_key: str) -> int:
        """获取错误累计次数
        
        Args:
            error_key: 错误类型标识
            
        Returns:
            累计错误次数
        """
        with self._data_lock:
            return self._error_count.get(error_key, 0)


# ============================================================
# 全局单例获取函数
# ============================================================

_error_log_throttler: Optional[ErrorLogThrottler] = None

def get_error_log_throttler() -> ErrorLogThrottler:
    """获取错误日志限流器单例"""
    global _error_log_throttler
    if _error_log_throttler is None:
        _error_log_throttler = ErrorLogThrottler(throttle_seconds=60)
    return _error_log_throttler

