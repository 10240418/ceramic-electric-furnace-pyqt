"""
内存缓存管理器
"""
from typing import Dict, Any, List, Optional
from collections import deque
from threading import Lock
import time
import logging

logger = logging.getLogger(__name__)


class DataCache:
    
    _instance: Optional['DataCache'] = None
    _lock = Lock()
    
    # 1. 单例模式：确保全局只有一个实例
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    # 2. 初始化缓存管理器
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        
        # 最新数据（单条）
        self._latest_arc_data: Dict[str, Any] = {}
        self._latest_sensor_data: Dict[str, Any] = {}
        self._latest_batch_status: Dict[str, Any] = {}
        
        # 历史数据（用于图表，保留最近 1000 条）
        self._arc_history: deque = deque(maxlen=1000)
        self._sensor_history: deque = deque(maxlen=1000)
        
        # 读写锁（细粒度锁，提高并发性能）
        self._arc_lock = Lock()
        self._sensor_lock = Lock()
        self._batch_lock = Lock()
        
        logger.info("数据缓存管理器已初始化")
        logger.info(f"   - 弧流历史缓存: {self._arc_history.maxlen} 条")
        logger.info(f"   - 传感器历史缓存: {self._sensor_history.maxlen} 条")
    
    # 3. 存储弧流数据（线程安全）
    def set_arc_data(self, data: Dict[str, Any]):
        with self._arc_lock:
            self._latest_arc_data = data.copy()
            self._arc_history.append({
                'data': data.copy(),
                'timestamp': time.time()
            })
    
    # 4. 获取最新弧流数据（线程安全）
    def get_arc_data(self) -> Dict[str, Any]:
        with self._arc_lock:
            return self._latest_arc_data.copy()
    
    # 5. 获取弧流历史数据（线程安全）
    def get_arc_history(self, count: int = 100) -> List[Dict[str, Any]]:
        with self._arc_lock:
            return list(self._arc_history)[-count:]
    
    # 6. 存储传感器数据（线程安全）
    def set_sensor_data(self, data: Dict[str, Any]):
        with self._sensor_lock:
            self._latest_sensor_data = data.copy()
            self._sensor_history.append({
                'data': data.copy(),
                'timestamp': time.time()
            })
    
    # 7. 获取最新传感器数据（线程安全）
    def get_sensor_data(self) -> Dict[str, Any]:
        with self._sensor_lock:
            return self._latest_sensor_data.copy()
    
    # 8. 获取传感器历史数据（线程安全）
    def get_sensor_history(self, count: int = 100) -> List[Dict[str, Any]]:
        with self._sensor_lock:
            return list(self._sensor_history)[-count:]
    
    # 9. 存储批次状态（线程安全）
    def set_batch_status(self, status: Dict[str, Any]):
        with self._batch_lock:
            self._latest_batch_status = status.copy()
    
    # 10. 获取批次状态（线程安全）
    def get_batch_status(self) -> Dict[str, Any]:
        with self._batch_lock:
            return self._latest_batch_status.copy()
    
    # 11. 获取缓存统计信息
    def get_stats(self) -> Dict[str, Any]:
        return {
            'arc_history_count': len(self._arc_history),
            'sensor_history_count': len(self._sensor_history),
            'has_arc_data': bool(self._latest_arc_data),
            'has_sensor_data': bool(self._latest_sensor_data),
            'has_batch_status': bool(self._latest_batch_status),
            'arc_history_maxlen': self._arc_history.maxlen,
            'sensor_history_maxlen': self._sensor_history.maxlen
        }
    
    # 12. 清空所有缓存（线程安全）
    def clear(self):
        with self._arc_lock, self._sensor_lock, self._batch_lock:
            self._latest_arc_data.clear()
            self._latest_sensor_data.clear()
            self._latest_batch_status.clear()
            self._arc_history.clear()
            self._sensor_history.clear()
        logger.info("缓存已清空")


_data_cache_instance: Optional[DataCache] = None

# 13. 获取数据缓存管理器单例
def get_data_cache() -> DataCache:
    global _data_cache_instance
    if _data_cache_instance is None:
        _data_cache_instance = DataCache()
    return _data_cache_instance

