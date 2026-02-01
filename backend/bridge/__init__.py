"""
前后端桥接层
"""

__version__ = "1.0.0"

# 1. 延迟导入，避免在不需要 PyQt6 时加载
def get_data_bridge():
    from .data_bridge import get_data_bridge as _get_data_bridge
    return _get_data_bridge()

# 直接导入不依赖 PyQt6 的模块
from .data_cache import DataCache, get_data_cache
from .data_models import (
    ElectrodeData,
    ArcData,
    CoolingWaterData,
    HopperData,
    ValveStatus,
    DustCollectorData,
    SensorData,
    BatchStatus,
    AlarmRecord,
    HistoryDataPoint,
    dict_to_arc_data,
    dict_to_sensor_data,
    dict_to_batch_status,
)
from .history_query import HistoryQueryService, get_history_query_service

__all__ = [
    # 桥接器（延迟导入）
    "get_data_bridge",
    # 缓存管理器
    "DataCache",
    "get_data_cache",
    # 历史查询服务
    "HistoryQueryService",
    "get_history_query_service",
    # 数据模型
    "ElectrodeData",
    "ArcData",
    "CoolingWaterData",
    "HopperData",
    "ValveStatus",
    "DustCollectorData",
    "SensorData",
    "BatchStatus",
    "AlarmRecord",
    "HistoryDataPoint",
    # 转换函数
    "dict_to_arc_data",
    "dict_to_sensor_data",
    "dict_to_batch_status",
]

