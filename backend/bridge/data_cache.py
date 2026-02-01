"""
内存缓存管理器
"""
from typing import Dict, Any, List, Optional
from collections import deque
from threading import RLock
import time
import logging

logger = logging.getLogger(__name__)


class DataCache:
    
    _instance: Optional['DataCache'] = None
    _lock = RLock()  # 使用 RLock（可重入锁）
    
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
        
        # 读写锁（使用 RLock 可重入锁，提高并发性能和安全性）
        self._arc_lock = RLock()
        self._sensor_lock = RLock()
        self._batch_lock = RLock()
        
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
    
    # 11. 获取前端实时显示数据（高频调用 0.5s）- 线程安全且数据一致
    def get_realtime_display_data(self) -> Dict[str, Any]:
        """获取前端实时显示所需的所有数据（线程安全）
        
        此方法专为前端高频调用（0.5s）设计，返回：
        - 三相弧流弧压（U/V/W）
        - 三相设定值
        - 死区百分比
        - 总功率
        - 总能耗
        - 电极深度
        
        线程安全保证：
        1. 使用 RLock 可重入锁，避免死锁
        2. 同时锁住 arc_lock 和 sensor_lock，确保数据一致性
        3. 使用 .copy() 创建数据副本，避免引用问题
        4. 即使后台正在更新，也能读取到完整的数据快照
        
        Returns:
            Dict: 包含所有实时显示数据的字典
        """
        # 同时获取两个锁，确保读取的数据是一致的快照
        with self._arc_lock, self._sensor_lock:
            # 深拷贝数据，避免引用问题
            arc_data = self._latest_arc_data.copy() if self._latest_arc_data else {}
            sensor_data = self._latest_sensor_data.copy() if self._latest_sensor_data else {}
            
            # 提取电极深度
            electrode_depths = sensor_data.get('electrode_depths', {})
            
            # 构建返回数据（所有数据来自同一时刻的快照）
            return {
                # 弧流数据（A）
                'arc_current': arc_data.get('arc_current', {
                    'U': 0.0, 'V': 0.0, 'W': 0.0
                }),
                # 弧压数据（V）
                'arc_voltage': arc_data.get('arc_voltage', {
                    'U': 0.0, 'V': 0.0, 'W': 0.0
                }),
                # 设定值（A）
                'setpoints': arc_data.get('setpoints', {
                    'U': 0.0, 'V': 0.0, 'W': 0.0
                }),
                # 死区百分比（%）
                'manual_deadzone_percent': arc_data.get('manual_deadzone_percent', 0.0),
                # 总功率（kW）
                'power_total': arc_data.get('power_total', 0.0),
                # 总能耗（kWh）- 从传感器数据中获取
                'energy_total': sensor_data.get('energy_total', 0.0),
                # 电极深度（mm）
                'electrode_depths': {
                    'U': electrode_depths.get('LENTH1', {}).get('distance_mm', 0.0),
                    'V': electrode_depths.get('LENTH2', {}).get('distance_mm', 0.0),
                    'W': electrode_depths.get('LENTH3', {}).get('distance_mm', 0.0),
                },
                # 时间戳（使用弧流数据的时间戳）
                'timestamp': arc_data.get('timestamp', 0.0)
            }
    
    # 11.1 获取料仓上限值（从 DB18 读取）
    def get_hopper_upper_limit(self) -> float:
        """获取料仓上限值（从 DB18 读取）
        
        Returns:
            料仓上限值 (kg)，默认 4900.0
        """
        from backend.services.polling_data_processor import get_hopper_upper_limit
        return get_hopper_upper_limit()
    
    # 12. 获取缓存统计信息
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

