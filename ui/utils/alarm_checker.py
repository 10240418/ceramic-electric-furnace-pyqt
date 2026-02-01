"""
报警检查工具 - 用于前端 UI 显示
"""
from typing import Tuple, Optional
from backend.alarm_thresholds import get_alarm_threshold_manager, ThresholdConfig


class AlarmChecker:
    """报警检查器 - 单例模式"""
    
    _instance: Optional['AlarmChecker'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self.alarm_manager = get_alarm_threshold_manager()
    
    # 1. 检查数值状态
    def check_value(self, param_name: str, value: float) -> str:
        """
        检查数值是否超限
        
        Args:
            param_name: 参数名称（如 'electrode_depth_u', 'arc_current_u'）
            value: 当前值
        
        Returns:
            'normal': 正常（绿色/白色）
            'warning': 警告（黄色）
            'alarm': 报警（红色+闪烁）
        """
        return self.alarm_manager.check_value(param_name, value)
    
    # 2. 获取阈值配置
    def get_threshold(self, param_name: str) -> Optional[ThresholdConfig]:
        """获取指定参数的阈值配置"""
        return self.alarm_manager.get_threshold(param_name)
    
    # 3. 获取状态颜色
    def get_status_color(self, status: str, theme_colors) -> str:
        """
        根据状态获取颜色
        
        Args:
            status: 'normal', 'warning', 'alarm'
            theme_colors: 主题颜色对象
        
        Returns:
            颜色字符串
        """
        if status == 'warning':
            return theme_colors.STATUS_WARNING  # 黄色
        elif status == 'alarm':
            return theme_colors.STATUS_ALARM    # 红色
        else:
            return theme_colors.TEXT_PRIMARY    # 正常颜色
    
    # 4. 判断是否需要闪烁
    def should_blink(self, status: str) -> bool:
        """判断是否需要闪烁（仅报警状态闪烁）"""
        return status == 'alarm'


# 全局单例
_alarm_checker: Optional[AlarmChecker] = None


def get_alarm_checker() -> AlarmChecker:
    """获取报警检查器单例"""
    global _alarm_checker
    if _alarm_checker is None:
        _alarm_checker = AlarmChecker()
    return _alarm_checker

