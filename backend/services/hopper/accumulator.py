# ============================================================
# 文件说明: accumulator.py - 基于 PLC 的投料累计服务
# ============================================================
# 功能:
#   1. 每0.5秒轮询读取 DB18 (料仓重量) 和 DB19 (排料标志)
#   2. 当 DB19 的排料标志为 True 时，读取 DB18 的本次排料重量
#   3. 生成投料记录并累加到投料总量
#   4. 批量写入 InfluxDB (投料记录 + 投料累计)
# ============================================================
# 【数据库写入说明】
# ============================================================
# 写入 sensor_data Measurement (统一数据库):
# 
# sensor_data (投料记录，用于所有查询)
#    Tags:
#      - device_type: hopper
#      - device_id: hopper_1
#      - module_type: feeding
#      - batch_code: 批次号
#    Fields:
#      - discharge_weight: 本次排料重量 (kg)
#      - feeding_total: 累计投料量 (kg)
#    Time: 投料时间戳
# 
# 用途:
#   - 历史曲线页面 (投料累计曲线)
#   - 批次对比页面 (累计投料对比)
#   - 料仓详情弹窗 (投料记录表格 + 累计曲线)
# ============================================================

import threading
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from collections import deque
from dataclasses import dataclass

from loguru import logger


@dataclass
class FeedingRecord:
    """投料记录"""
    timestamp: datetime
    discharge_weight: float  # 本次排料重量 (kg)
    batch_code: str


class FeedingPLCAccumulator:
    """基于 PLC 的投料累计器 - 单例模式"""
    
    _instance: Optional['FeedingPLCAccumulator'] = None
    _lock = threading.Lock()
    
    # 批量写入配置
    BATCH_SIZE = 30  # 30次轮询后批量写入 (15秒)
    
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
        # 累计状态
        # ============================================================
        self._feeding_total: float = 0.0       # 累计投料量 (kg)
        self._feeding_count: int = 0           # 投料次数
        self._current_batch_code: Optional[str] = None
        
        # ============================================================
        # 投料记录缓存 (待写入数据库)
        # ============================================================
        self._feeding_records_buffer: deque = deque(maxlen=100)
        self._buffer_count: int = 0
        
        # ============================================================
        # 最新数据缓存 (供前端读取)
        # ============================================================
        self._latest_current_weight: float = 0.0  # 当前料仓重量
        self._latest_upper_limit: float = 4900.0  # 料仓上限值
        
        logger.info("基于 PLC 的投料累计器已初始化")
    
    # ============================================================
    # 1: 批次管理模块
    # ============================================================
    def reset_for_new_batch(self, batch_code: str):
        """重置累计量 (新批次开始时调用)
        
        从数据库恢复累计值到内存
        """
        with self._data_lock:
            # 清空缓存
            self._feeding_records_buffer.clear()
            self._buffer_count = 0
            self._current_batch_code = batch_code
            self._feeding_count = 0
            
            # 从数据库恢复累计值
            latest_total = self._get_latest_from_database(batch_code)
            self._feeding_total = latest_total
            
            logger.info(f"投料累计器已重置 (批次: {batch_code}, 恢复: {latest_total:.1f}kg)")
    
    def _get_latest_from_database(self, batch_code: str) -> float:
        """从 InfluxDB 查询该批次的最新投料累计值
        
        Returns:
            feeding_total (kg)
        """
        try:
            from backend.core.influxdb import get_influx_client
            from backend.config import get_settings
            
            settings = get_settings()
            influx = get_influx_client()
            
            # 使用新标签格式查询: module_type='feeding', device_type='hopper'
            query = f'''
                from(bucket: "{settings.influx_bucket}")
                    |> range(start: -7d)
                    |> filter(fn: (r) => r["_measurement"] == "sensor_data")
                    |> filter(fn: (r) => r["batch_code"] == "{batch_code}")
                    |> filter(fn: (r) => r["module_type"] == "feeding")
                    |> filter(fn: (r) => r["device_type"] == "hopper")
                    |> filter(fn: (r) => r["_field"] == "feeding_total")
                    |> max()
            '''
            
            result = influx.query_api().query(query)
            
            feeding_total = 0.0
            for table in result:
                for record in table.records:
                    value = record.get_value()
                    feeding_total = float(value) if value else 0.0
                    logger.info(f"从数据库恢复投料累计: {feeding_total:.1f}kg (批次: {batch_code})")
                    break
            
            if feeding_total == 0.0:
                logger.warning(f"批次 {batch_code} 没有找到投料累计数据，从0开始")
            
            return feeding_total
            
        except Exception as e:
            logger.error(f"从数据库恢复投料累计失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return 0.0
    
    # ============================================================
    # 2: 数据添加模块
    # ============================================================
    def add_feeding_record(
        self,
        discharge_weight: float,
        batch_code: str,
        current_weight: float = 0.0,
        upper_limit: float = 4900.0
    ) -> Dict[str, Any]:
        """添加一条投料记录
        
        Args:
            discharge_weight: 本次排料重量 (kg)
            batch_code: 批次号
            current_weight: 当前料仓重量 (kg)
            upper_limit: 料仓上限值 (kg)
            
        Returns:
            {
                'feeding_total': float,      # 累计投料量
                'feeding_count': int,        # 投料次数
                'should_flush': bool,        # 是否需要批量写入
            }
        """
        with self._data_lock:
            # 更新最新数据缓存
            self._latest_current_weight = current_weight
            self._latest_upper_limit = upper_limit
            
            # 如果累计值为0，从数据库恢复
            if self._feeding_total == 0.0 and batch_code:
                self._feeding_total = self._get_latest_from_database(batch_code)
            
            # 累加投料量
            self._feeding_total += discharge_weight
            self._feeding_count += 1
            
            # 创建投料记录
            record = FeedingRecord(
                timestamp=datetime.now(timezone.utc),
                discharge_weight=discharge_weight,
                batch_code=batch_code
            )
            
            # 添加到缓存
            self._feeding_records_buffer.append(record)
            self._buffer_count += 1
            
            # 检查是否需要批量写入
            should_flush = self._buffer_count >= self.BATCH_SIZE
            
            logger.info(f"投料记录已添加: {discharge_weight:.1f}kg, 累计: {self._feeding_total:.1f}kg")
            
            return {
                'feeding_total': self._feeding_total,
                'feeding_count': self._feeding_count,
                'should_flush': should_flush,
            }
    
    # ============================================================
    # 3: 批量写入模块
    # ============================================================
    async def flush_feeding_records(self):
        """批量写入投料记录到 InfluxDB (只写入 sensor_data，统一数据库)"""
        with self._data_lock:
            if not self._feeding_records_buffer:
                return
            
            # 复制缓存并清空
            records = list(self._feeding_records_buffer)
            self._feeding_records_buffer.clear()
            self._buffer_count = 0
        
        # 写入数据库
        try:
            from backend.core.influxdb import write_points_batch, build_point
            
            points = []
            current_total = self._feeding_total - sum(r.discharge_weight for r in records)
            
            for record in records:
                current_total += record.discharge_weight
                
                # 写入 sensor_data (统一使用 sensor_data measurement)
                point = build_point(
                    measurement='sensor_data',
                    tags={
                        'device_type': 'hopper',
                        'device_id': 'hopper_1',
                        'module_type': 'feeding',
                        'batch_code': record.batch_code
                    },
                    fields={
                        'discharge_weight': record.discharge_weight,
                        'feeding_total': current_total
                    },
                    timestamp=record.timestamp
                )
                if point:
                    points.append(point)
            
            if points:
                success, err = write_points_batch(points)
                if success:
                    logger.info(f"批量写入投料记录成功: {len(records)} 条记录")
                else:
                    logger.error(f"批量写入投料记录失败: {err}")
        
        except Exception as e:
            logger.error(f"批量写入投料记录异常: {e}")
    
    # ============================================================
    # 4: 强制刷新缓存模块
    # ============================================================
    async def force_flush(self):
        """强制刷新缓存，立即写入数据库（不管是否达到批量阈值）"""
        logger.info("强制刷新投料记录缓存...")
        await self.flush_feeding_records()
        logger.info("投料记录缓存已强制刷新")
    
    # ============================================================
    # 5: 数据获取模块
    # ============================================================
    def get_feeding_total(self) -> float:
        """获取累计投料量 (kg)"""
        with self._data_lock:
            return self._feeding_total
    
    def get_realtime_data(self) -> Dict[str, Any]:
        """获取实时数据 (供API调用)
        
        Returns:
            {
                'feeding_total': float,           # 累计投料量
                'feeding_count': int,             # 投料次数
                'current_weight': float,          # 当前重量
                'upper_limit': float,             # 料仓上限值
                'batch_code': str,                # 当前批次号
                'buffer_size': int,               # 缓存大小
            }
        """
        with self._data_lock:
            return {
                'feeding_total': self._feeding_total,
                'feeding_count': self._feeding_count,
                'current_weight': self._latest_current_weight,
                'upper_limit': self._latest_upper_limit,
                'batch_code': self._current_batch_code,
                'buffer_size': len(self._feeding_records_buffer),
            }


# ============================================================
# 全局单例获取函数
# ============================================================

_feeding_plc_accumulator: Optional[FeedingPLCAccumulator] = None

def get_feeding_plc_accumulator() -> FeedingPLCAccumulator:
    """获取基于 PLC 的投料累计器单例"""
    global _feeding_plc_accumulator
    if _feeding_plc_accumulator is None:
        _feeding_plc_accumulator = FeedingPLCAccumulator()
    return _feeding_plc_accumulator

