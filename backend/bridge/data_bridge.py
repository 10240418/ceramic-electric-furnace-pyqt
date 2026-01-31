"""
数据桥接器
"""
from PyQt6.QtCore import QObject, pyqtSignal
from typing import Dict, Any, Optional
from loguru import logger


class DataBridge(QObject):
    
    arc_data_updated = pyqtSignal(dict)
    sensor_data_updated = pyqtSignal(dict)
    batch_status_changed = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    connection_status_changed = pyqtSignal(bool)
    
    _instance: Optional['DataBridge'] = None
    
    # 1. 初始化数据桥接器（私有，通过 get_instance() 获取）
    def __init__(self):
        super().__init__()
        logger.info("数据桥接器已初始化")
    
    # 2. 获取单例实例
    @classmethod
    def get_instance(cls) -> 'DataBridge':
        if cls._instance is None:
            logger.info("创建 DataBridge 单例实例")
            cls._instance = cls()
        return cls._instance
    
    # 3. 发送弧流数据到前端
    def emit_arc_data(self, data: Dict[str, Any]):
        try:
            self.arc_data_updated.emit(data)
        except Exception as e:
            logger.error(f"发送弧流数据失败: {e}")
            self.error_occurred.emit(f"发送弧流数据失败: {e}")
    
    # 4. 发送传感器数据到前端
    def emit_sensor_data(self, data: Dict[str, Any]):
        try:
            self.sensor_data_updated.emit(data)
        except Exception as e:
            logger.error(f"发送传感器数据失败: {e}")
            self.error_occurred.emit(f"发送传感器数据失败: {e}")
    
    # 5. 发送批次状态到前端
    def emit_batch_status(self, status: Dict[str, Any]):
        try:
            self.batch_status_changed.emit(status)
        except Exception as e:
            logger.error(f"发送批次状态失败: {e}")
            self.error_occurred.emit(f"发送批次状态失败: {e}")
    
    # 6. 发送错误信息到前端
    def emit_error(self, error_msg: str):
        logger.error(f"错误: {error_msg}")
        self.error_occurred.emit(error_msg)
    
    # 7. 发送连接状态到前端
    def emit_connection_status(self, connected: bool):
        status = "已连接" if connected else "已断开"
        logger.info(f"PLC 连接状态: {status}")
        self.connection_status_changed.emit(connected)


# 8. 获取数据桥接器单例
def get_data_bridge() -> DataBridge:
    return DataBridge.get_instance()

