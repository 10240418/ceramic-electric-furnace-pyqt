# ============================================================
# 文件说明: cooling_water_calculator.py - 冷却水累计流量计算服务
# ============================================================
# 功能:
#   1. 维护炉盖/炉皮流速缓存队列 (60个点, 30秒历史)
#   2. 每15秒计算一次累计流量
#   3. 实时计算前置过滤器压差
#   4. 按批次重置累计流量
# ============================================================
# 【数据库写入说明 - 冷却水累计数据】
# ============================================================
# Measurement: sensor_data
# Tags:
#   - device_type: electric_furnace
#   - module_type: cooling_water_total
#   - device_id: furnace_1
#   - batch_code: 批次号 (动态)
# Fields (共2个数据点):
# ============================================================
#   - furnace_shell_water_total: 炉皮累计流量 (m³)
#   - furnace_cover_water_total: 炉盖累计流量 (m³)
# ============================================================
# 写入逻辑:
#   - 轮询间隔: 0.5秒 (与DB32同步)
#   - 计算间隔: 15秒 (30次轮询)
#   - 流量计算: 平均流速(m³/h) × 时间(h) = 流量增量(m³)
#   - 压差计算: 炉皮水压 - 炉盖水压 = 前置过滤器压差 (kPa)
#   - 批次重置: 新批次开始时从数据库恢复累计值或从0开始
# ============================================================
# 注意: 此模块仅计算累计流量，实时流量和压差在 DB32 传感器数据中写入
# ============================================================

import threading
import statistics
from collections import deque
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from loguru import logger


class CoolingWaterCalculator:
    """冷却水累计流量计算器 - 单例模式"""
    
    _instance: Optional['CoolingWaterCalculator'] = None
    _lock = threading.Lock()
    
    # 队列大小: 60个点 (0.5s × 60 = 30秒)
    QUEUE_SIZE = 60
    # 计算窗口: 30个点 (0.5s × 30 = 15秒)
    CALC_WINDOW = 30
    # 计算间隔: 15秒
    CALC_INTERVAL_SEC = 15
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._data_lock = threading.Lock()
        
        # ============================================================
        # 流速缓存队列 (单位: m³/h)
        # ============================================================
        self._furnace_cover_flow_queue: deque = deque(maxlen=self.QUEUE_SIZE)  # 炉盖
        self._furnace_shell_flow_queue: deque = deque(maxlen=self.QUEUE_SIZE)  # 炉皮
        
        # ============================================================
        # 水压缓存 (单位: kPa) - 用于计算压差
        # ============================================================
        self._furnace_cover_pressure: float = 0.0  # 炉盖水压
        self._furnace_shell_pressure: float = 0.0  # 炉皮水压
        self._pressure_diff: float = 0.0           # 前置过滤器压差
        
        # ============================================================
        # 累计流量 (单位: m³) - 按批次重置
        # 【修复】恢复内存缓存，用于实时显示
        # ============================================================
        self._furnace_cover_total: float = 0.0  # 炉盖累计流量 (m³)
        self._furnace_shell_total: float = 0.0  # 炉皮累计流量 (m³)
        
        # ============================================================
        # 批次信息
        # ============================================================
        self._current_batch_code: Optional[str] = None
        
        # ============================================================
        # 计数器 (用于15秒触发计算)
        # ============================================================
        self._poll_count = 0
        
        logger.info("冷却水计算器已初始化")
    
    # ============================================================
    # 1: 批次管理模块
    # ============================================================
    def reset_for_new_batch(self, batch_code: str):
        """重置累计流量 (新批次开始时调用)
        
        【修复】从数据库恢复累计值到内存
        """
        with self._data_lock:
            # 清空队列和计数器
            self._furnace_cover_flow_queue.clear()
            self._furnace_shell_flow_queue.clear()
            self._poll_count = 0
            self._current_batch_code = batch_code
            
            # 从数据库恢复累计值到内存
            latest_cover, latest_shell = self._get_latest_from_database(batch_code)
            self._furnace_cover_total = latest_cover
            self._furnace_shell_total = latest_shell
            
            logger.info(f"冷却水计算器已重置 (批次: {batch_code}, 恢复: 炉盖={latest_cover:.3f}m³, 炉皮={latest_shell:.3f}m³)")
    
    def _get_latest_from_database(self, batch_code: str) -> tuple[float, float]:
        """从 InfluxDB 查询该批次的最新累计值
        
        【修改】使用 max() 而不是 last()，因为累计值是递增的
        
        Returns:
            (furnace_cover_total, furnace_shell_total)
        """
        try:
            from backend.core.influxdb import get_influxdb_client
            from backend.config import get_settings
            
            settings = get_settings()
            influx = get_influxdb_client()
            
            # 【修改】使用 max() 获取最大累计值（最新值）
            query = f'''
                from(bucket: "{settings.influx_bucket}")
                    |> range(start: -7d)
                    |> filter(fn: (r) => r["_measurement"] == "sensor_data")
                    |> filter(fn: (r) => r["batch_code"] == "{batch_code}")
                    |> filter(fn: (r) => r["module_type"] == "cooling_water_total")
                    |> filter(fn: (r) => 
                        r["_field"] == "furnace_cover_water_total" or 
                        r["_field"] == "furnace_shell_water_total"
                    )
                    |> max()
            '''
            
            result = influx.query_api().query(query)
            
            cover_total = 0.0
            shell_total = 0.0
            
            for table in result:
                for record in table.records:
                    field = record.get_field()
                    value = record.get_value()
                    if field == "furnace_cover_water_total":
                        cover_total = float(value) if value else 0.0
                    elif field == "furnace_shell_water_total":
                        shell_total = float(value) if value else 0.0
            
            return cover_total, shell_total
            
        except Exception as e:
            logger.error(f"从数据库恢复冷却水累计失败: {e}")
            return 0.0, 0.0
    
    # ============================================================
    # 2: 数据添加模块
    # ============================================================
    def add_measurement(
        self,
        furnace_cover_flow: float,  # 炉盖流速 m³/h
        furnace_shell_flow: float,  # 炉皮流速 m³/h
        furnace_cover_pressure: float,  # 炉盖水压 kPa
        furnace_shell_pressure: float,  # 炉皮水压 kPa
    ) -> Dict[str, Any]:
        """添加一次测量数据
        
        Args:
            furnace_cover_flow: 炉盖冷却水流速 (m³/h)
            furnace_shell_flow: 炉皮冷却水流速 (m³/h)
            furnace_cover_pressure: 炉盖冷却水压力 (kPa)
            furnace_shell_pressure: 炉皮冷却水压力 (kPa)
            
        Returns:
            {
                'pressure_diff': float,  # 前置过滤器压差 (kPa)
                'furnace_cover_flow': float,
                'furnace_shell_flow': float,
                'furnace_cover_pressure': float,
                'furnace_shell_pressure': float,
                'should_calc_volume': bool,  # 是否触发累计计算
            }
        """
        with self._data_lock:
            # 1. 添加到队列
            self._furnace_cover_flow_queue.append(furnace_cover_flow)
            self._furnace_shell_flow_queue.append(furnace_shell_flow)
            
            # 2. 更新水压缓存
            self._furnace_cover_pressure = furnace_cover_pressure
            self._furnace_shell_pressure = furnace_shell_pressure
            
            # 3. 计算前置过滤器压差 (炉皮 - 炉盖)
            self._pressure_diff = furnace_shell_pressure - furnace_cover_pressure
            
            # 4. 计数器递增
            self._poll_count += 1
            
            # 5. 检查是否需要计算累计流量 (每30次 = 15秒)
            should_calc = self._poll_count >= self.CALC_WINDOW
            
            return {
                'pressure_diff': self._pressure_diff,
                'furnace_cover_flow': furnace_cover_flow,
                'furnace_shell_flow': furnace_shell_flow,
                'furnace_cover_pressure': furnace_cover_pressure,
                'furnace_shell_pressure': furnace_shell_pressure,
                'should_calc_volume': should_calc,
            }
    
    # ============================================================
    # 3: 累计流量计算模块
    # ============================================================
    def calculate_volume_increment(self) -> Dict[str, Any]:
        """计算15秒内的流量增量并累加
        
        【修复】使用内存累计值，不再每次查询数据库
        
        Returns:
            {
                'furnace_cover_delta': float,  # 炉盖本次增量 (m³)
                'furnace_shell_delta': float,  # 炉皮本次增量 (m³)
                'furnace_cover_total': float,  # 炉盖累计 (m³)
                'furnace_shell_total': float,  # 炉皮累计 (m³)
                'timestamp': str,
            }
        """
        with self._data_lock:
            # 重置计数器
            self._poll_count = 0
            
            # 计算炉盖流量增量
            cover_delta = 0.0
            if len(self._furnace_cover_flow_queue) >= self.CALC_WINDOW:
                # 取最近30个点的平均值
                recent_flows = list(self._furnace_cover_flow_queue)[-self.CALC_WINDOW:]
                avg_flow = statistics.mean(recent_flows)
                # 流量 = 平均流速(m³/h) × 时间(h)
                # 15秒 = 15/3600 小时
                cover_delta = avg_flow * (self.CALC_INTERVAL_SEC / 3600)
            
            # 计算炉皮流量增量
            shell_delta = 0.0
            if len(self._furnace_shell_flow_queue) >= self.CALC_WINDOW:
                recent_flows = list(self._furnace_shell_flow_queue)[-self.CALC_WINDOW:]
                avg_flow = statistics.mean(recent_flows)
                shell_delta = avg_flow * (self.CALC_INTERVAL_SEC / 3600)
            
            # 【修复】使用内存累计值
            self._furnace_cover_total += cover_delta
            self._furnace_shell_total += shell_delta
            
            result = {
                'furnace_cover_delta': cover_delta,
                'furnace_shell_delta': shell_delta,
                'furnace_cover_total': self._furnace_cover_total,
                'furnace_shell_total': self._furnace_shell_total,
                'batch_code': self._current_batch_code,
                'timestamp': datetime.now(timezone.utc).isoformat(),
            }
            
            if cover_delta > 0 or shell_delta > 0:
                logger.info(f"冷却水累计: 炉盖+{cover_delta:.4f}m³ (累计={self._furnace_cover_total:.3f}m³), "
                      f"炉皮+{shell_delta:.4f}m³ (累计={self._furnace_shell_total:.3f}m³)")
            
            return result
    
    # ============================================================
    # 4: 数据获取模块
    # ============================================================
    def get_realtime_data(self) -> Dict[str, Any]:
        """获取实时数据 (供API调用)
        
        【修复】直接返回内存中的累计值
        """
        with self._data_lock:
            return {
                'furnace_cover_flow': self._furnace_cover_flow_queue[-1] if self._furnace_cover_flow_queue else 0.0,
                'furnace_shell_flow': self._furnace_shell_flow_queue[-1] if self._furnace_shell_flow_queue else 0.0,
                'furnace_cover_pressure': self._furnace_cover_pressure,
                'furnace_shell_pressure': self._furnace_shell_pressure,
                'pressure_diff': self._pressure_diff,
                'furnace_cover_total_volume': self._furnace_cover_total,
                'furnace_shell_total_volume': self._furnace_shell_total,
                'batch_code': self._current_batch_code,
                'queue_size': {
                    'cover': len(self._furnace_cover_flow_queue),
                    'shell': len(self._furnace_shell_flow_queue),
                },
            }
    
    def get_pressure_diff(self) -> float:
        """获取前置过滤器压差 (kPa)"""
        with self._data_lock:
            return self._pressure_diff
    
    def _write_to_database(self, batch_code: str, cover_total: float, shell_total: float):
        """写入累计流量到 InfluxDB
        
        【已废弃】改为由 process_modbus_data 统一批量写入
        
        Args:
            batch_code: 批次号
            cover_total: 炉盖累计流量 (m³)
            shell_total: 炉皮累计流量 (m³)
        """
        pass  # 不再使用立即写入，改为批量写入
    
    def get_total_volumes(self) -> Dict[str, float]:
        """获取累计流量
        
        【修复】直接返回内存中的累计值
        """
        with self._data_lock:
            return {
                'furnace_cover': self._furnace_cover_total,
                'furnace_shell': self._furnace_shell_total,
            }


# ============================================================
# 全局单例获取函数
# ============================================================

_cooling_calculator: Optional[CoolingWaterCalculator] = None

def get_cooling_water_calculator() -> CoolingWaterCalculator:
    """获取冷却水计算器单例"""
    global _cooling_calculator
    if _cooling_calculator is None:
        _cooling_calculator = CoolingWaterCalculator()
    return _cooling_calculator
