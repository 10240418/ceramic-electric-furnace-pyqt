# ============================================================
# 文件说明: emergency_stop_service.py - 高压紧急停电监控服务
# ============================================================
# 功能:
#   1. 缓存高压紧急停电的4个数据（单例模式）
#   2. 变化检测逻辑（只有变化时更新缓存）
#   3. 报警触发逻辑（enabled=True 且 flag=True 时触发）
#   4. 发射 PyQt 信号通知前端
# ============================================================
# 数据结构 (DB1 offset 182-189, 共8字节):
#   - offset 182-183: emergency_stop_arc_limit (INT, 2字节) - 弧流上限值
#   - offset 184: emergency_stop_flag (bit 0) + emergency_stop_enabled (bit 1)
#   - offset 185: 保留字节
#   - offset 186-189: emergency_stop_delay (TIME, 4字节) - 消抖时间（毫秒）
# ============================================================

import threading
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal
from loguru import logger


@dataclass
class EmergencyStopData:
    """高压紧急停电数据"""
    arc_limit: int              # 弧流上限值 (A)
    flag: bool                  # 紧急停电标志
    enabled: bool               # 功能使能
    delay_ms: int               # 消抖时间 (ms)
    timestamp: datetime         # 时间戳
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'arc_limit': self.arc_limit,
            'flag': self.flag,
            'enabled': self.enabled,
            'delay_ms': self.delay_ms,
            'delay_s': self.delay_ms / 1000.0,
            'timestamp': self.timestamp.isoformat(),
        }


class EmergencyStopService(QObject):
    """高压紧急停电监控服务 - 单例模式
    
    特点:
    1. 缓存管理：只保存一组最新数据
    2. 变化检测：只有数据变化时才更新缓存
    3. 报警触发：enabled=True 且 flag=True 时发射信号
    4. 线程安全：使用锁保护共享数据
    """
    
    # ============================================================
    # PyQt 信号定义
    # ============================================================
    # 数据变化信号（任意数据变化时发射）
    data_changed = pyqtSignal(dict)  # 发射最新数据字典
    
    # 报警触发信号（最高优先级，enabled=True 且 flag=True 时发射）
    emergency_alarm_triggered = pyqtSignal(dict)  # 发射报警数据
    
    # 报警解除信号（flag 从 True 变为 False 时发射）
    emergency_alarm_cleared = pyqtSignal()
    
    # ============================================================
    # 单例模式（由模块级 get_emergency_stop_service() 管理）
    # ============================================================
    
    def __init__(self):
        super().__init__()
        
        self._data_lock = threading.Lock()
        
        # ============================================================
        # 缓存数据（只保存一组）
        # ============================================================
        self._cached_data: Optional[EmergencyStopData] = None
        
        # ============================================================
        # 上一次的报警状态（用于检测报警触发/解除）
        # ============================================================
        self._last_alarm_active: bool = False
        
        logger.info("高压紧急停电监控服务已初始化")
    
    # ============================================================
    # 1. 数据更新模块
    # ============================================================
    def update_data(
        self,
        arc_limit: int,
        flag: bool,
        enabled: bool,
        delay_ms: int
    ) -> bool:
        """更新缓存数据（只有变化时才更新）
        
        Args:
            arc_limit: 弧流上限值 (A)
            flag: 紧急停电标志
            enabled: 功能使能
            delay_ms: 消抖时间 (ms)
            
        Returns:
            bool: True 如果数据有变化，False 如果没有变化
        """
        with self._data_lock:
            # 创建新数据
            new_data = EmergencyStopData(
                arc_limit=arc_limit,
                flag=flag,
                enabled=enabled,
                delay_ms=delay_ms,
                timestamp=datetime.now()
            )
            
            # 检查是否变化
            if self._cached_data is None:
                # 第一次更新
                self._cached_data = new_data
                changed = True
                logger.info(f"首次缓存高压紧急停电数据: {new_data.to_dict()}")
            else:
                # 比较数据是否变化
                changed = (
                    self._cached_data.arc_limit != new_data.arc_limit or
                    self._cached_data.flag != new_data.flag or
                    self._cached_data.enabled != new_data.enabled or
                    self._cached_data.delay_ms != new_data.delay_ms
                )
                
                if changed:
                    logger.info(f"高压紧急停电数据变化: {self._cached_data.to_dict()} -> {new_data.to_dict()}")
                    self._cached_data = new_data
            
            # 如果数据变化，发射信号
            if changed:
                self.data_changed.emit(new_data.to_dict())
            
            # 检查报警状态
            self._check_alarm_status(new_data)
            
            return changed
    
    # ============================================================
    # 2. 报警检测模块
    # ============================================================
    def _check_alarm_status(self, data: EmergencyStopData):
        """检查报警状态并发射信号
        
        报警触发条件: enabled=True 且 flag=True
        """
        # 当前报警状态
        current_alarm_active = data.enabled and data.flag
        
        # 检测报警触发（从 False 变为 True）
        if current_alarm_active and not self._last_alarm_active:
            logger.critical(f"⚠️ 高压紧急停电报警触发！弧流上限: {data.arc_limit} A, 消抖时间: {data.delay_ms} ms")
            self.emergency_alarm_triggered.emit(data.to_dict())
        
        # 检测报警解除（从 True 变为 False）
        elif not current_alarm_active and self._last_alarm_active:
            logger.info("✅ 高压紧急停电报警已解除")
            self.emergency_alarm_cleared.emit()
        
        # 更新上一次的报警状态
        self._last_alarm_active = current_alarm_active
    
    # ============================================================
    # 3. 数据获取模块
    # ============================================================
    def get_cached_data(self) -> Optional[Dict[str, Any]]:
        """获取缓存的数据（供前端调用）
        
        Returns:
            Dict 或 None（如果还没有数据）
        """
        with self._data_lock:
            if self._cached_data is None:
                return None
            return self._cached_data.to_dict()
    
    def is_alarm_active(self) -> bool:
        """检查报警是否激活
        
        Returns:
            bool: True 如果报警激活（enabled=True 且 flag=True）
        """
        with self._data_lock:
            if self._cached_data is None:
                return False
            return self._cached_data.enabled and self._cached_data.flag
    
    def get_arc_limit(self) -> int:
        """获取弧流上限值
        
        Returns:
            int: 弧流上限值 (A)，如果没有数据返回 0
        """
        with self._data_lock:
            if self._cached_data is None:
                return 0
            return self._cached_data.arc_limit
    
    def get_delay_ms(self) -> int:
        """获取消抖时间
        
        Returns:
            int: 消抖时间 (ms)，如果没有数据返回 0
        """
        with self._data_lock:
            if self._cached_data is None:
                return 0
            return self._cached_data.delay_ms
    
    # ============================================================
    # 4. 便捷方法
    # ============================================================
    def update_from_parsed_data(self, parsed_data: Dict[str, Any]) -> bool:
        """从解析器返回的数据中更新缓存
        
        Args:
            parsed_data: parser_config_db1.py 返回的解析结果
            
        Returns:
            bool: True 如果数据有变化
        """
        emergency_stop = parsed_data.get('emergency_stop', {})
        
        if not emergency_stop:
            logger.warning("解析数据中没有 emergency_stop 字段")
            return False
        
        return self.update_data(
            arc_limit=emergency_stop.get('emergency_stop_arc_limit', 0),
            flag=emergency_stop.get('emergency_stop_flag', False),
            enabled=emergency_stop.get('emergency_stop_enabled', False),
            delay_ms=emergency_stop.get('emergency_stop_delay', 0)
        )


# ============================================================
# 全局单例获取函数
# ============================================================

_emergency_stop_service: Optional[EmergencyStopService] = None

def get_emergency_stop_service() -> EmergencyStopService:
    """获取高压紧急停电监控服务单例"""
    global _emergency_stop_service
    if _emergency_stop_service is None:
        _emergency_stop_service = EmergencyStopService()
    return _emergency_stop_service


# ============================================================
# 便捷函数
# ============================================================

def update_emergency_stop_data(
    arc_limit: int,
    flag: bool,
    enabled: bool,
    delay_ms: int
) -> bool:
    """更新高压紧急停电数据（便捷函数）"""
    service = get_emergency_stop_service()
    return service.update_data(arc_limit, flag, enabled, delay_ms)


def get_emergency_stop_data() -> Optional[Dict[str, Any]]:
    """获取缓存的高压紧急停电数据（便捷函数）"""
    service = get_emergency_stop_service()
    return service.get_cached_data()


def is_emergency_alarm_active() -> bool:
    """检查高压紧急停电报警是否激活（便捷函数）"""
    service = get_emergency_stop_service()
    return service.is_alarm_active()

