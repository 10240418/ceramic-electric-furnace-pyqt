"""
报警检查器 - 在轮询数据中检查是否超过报警阈值，超过则写入报警记录
"""
from datetime import datetime, timezone
from typing import Dict, Any
from loguru import logger

from backend.alarm_thresholds import get_alarm_threshold_manager
from backend.core.alarm_store import log_alarm


# 设备ID常量
DEVICE_FURNACE = "furnace_1"
DEVICE_ELECTRODE = "electrode"


def check_arc_data_alarms(arc_cache: Dict[str, Any], batch_code: str = ""):
    """检查弧流弧压数据是否超过报警阈值
    
    在 process_arc_data() 中调用，检查:
    - 三相弧流 (arc_current_u/v/w)
    - 三相弧压 (arc_voltage_u/v/w)
    
    Args:
        arc_cache: 弧流弧压缓存数据
        batch_code: 当前批次号
    """
    if not arc_cache:
        return
    
    manager = get_alarm_threshold_manager()
    
    # 相位映射: U->u, V->v, W->w
    phase_map = {'U': 'u', 'V': 'v', 'W': 'w'}
    phase_display = {'U': '1#', 'V': '2#', 'W': '3#'}
    
    # 1. 检查三相弧流
    arc_current = arc_cache.get('arc_current', {})
    for phase_key, param_suffix in phase_map.items():
        value = arc_current.get(phase_key)
        if value is None:
            continue
        
        param_name = f"arc_current_{param_suffix}"
        level = manager.check_value(param_name, value)
        
        if level in ('warning', 'alarm'):
            config = manager.get_threshold(param_name)
            # 确定超过的是哪个阈值
            threshold = _get_exceeded_threshold(config, value, level)
            log_alarm(
                device_id=DEVICE_ELECTRODE,
                alarm_type="arc_current",
                param_name=param_name,
                value=value,
                threshold=threshold,
                level=level,
                message=f"{phase_display[phase_key]}弧流 {value:.1f}A 超过{_level_text(level)} {threshold:.1f}A",
                batch_code=batch_code
            )
    
    # 2. 检查三相弧压
    arc_voltage = arc_cache.get('arc_voltage', {})
    for phase_key, param_suffix in phase_map.items():
        value = arc_voltage.get(phase_key)
        if value is None:
            continue
        
        param_name = f"arc_voltage_{param_suffix}"
        level = manager.check_value(param_name, value)
        
        if level in ('warning', 'alarm'):
            config = manager.get_threshold(param_name)
            threshold = _get_exceeded_threshold(config, value, level)
            log_alarm(
                device_id=DEVICE_ELECTRODE,
                alarm_type="arc_voltage",
                param_name=param_name,
                value=value,
                threshold=threshold,
                level=level,
                message=f"{phase_display[phase_key]}弧压 {value:.1f}V 超过{_level_text(level)} {threshold:.1f}V",
                batch_code=batch_code
            )


def check_sensor_data_alarms(
    parsed: Dict[str, Any],
    furnace_shell_pressure: float,
    furnace_cover_pressure: float,
    batch_code: str = ""
):
    """检查DB32传感器数据是否超过报警阈值
    
    在 process_modbus_data() 中调用，检查:
    - 三相电极深度 (electrode_depth_u/v/w)
    - 炉皮冷却水压力 (cooling_pressure_shell)
    - 炉盖冷却水压力 (cooling_pressure_cover)
    - 炉皮冷却水流速 (cooling_flow_shell)
    - 炉盖冷却水流速 (cooling_flow_cover)
    - 过滤器压差 (filter_pressure_diff)
    
    Args:
        parsed: DB32解析后的数据
        furnace_shell_pressure: 炉皮水压 (kPa)
        furnace_cover_pressure: 炉盖水压 (kPa)
        batch_code: 当前批次号
    """
    manager = get_alarm_threshold_manager()
    
    # 1. 检查三相电极深度
    electrode_depths = parsed.get('electrode_depths', {})
    depth_map = {
        'LENTH1': ('electrode_depth_u', '1#'),
        'LENTH2': ('electrode_depth_v', '2#'),
        'LENTH3': ('electrode_depth_w', '3#'),
    }
    
    for key, (param_name, phase_display) in depth_map.items():
        depth_data = electrode_depths.get(key, {})
        value = depth_data.get('distance_mm') if isinstance(depth_data, dict) else None
        if value is None:
            continue
        
        level = manager.check_value(param_name, value)
        if level in ('warning', 'alarm'):
            config = manager.get_threshold(param_name)
            threshold = _get_exceeded_threshold(config, value, level)
            log_alarm(
                device_id=DEVICE_FURNACE,
                alarm_type="electrode_depth",
                param_name=param_name,
                value=value,
                threshold=threshold,
                level=level,
                message=f"{phase_display}电极深度 {value:.1f}mm 超过{_level_text(level)} {threshold:.1f}mm",
                batch_code=batch_code
            )
    
    # 2. 检查炉皮冷却水压力
    if furnace_shell_pressure is not None:
        param_name = "cooling_pressure_shell"
        level = manager.check_value(param_name, furnace_shell_pressure)
        if level in ('warning', 'alarm'):
            config = manager.get_threshold(param_name)
            threshold = _get_exceeded_threshold(config, furnace_shell_pressure, level)
            log_alarm(
                device_id=DEVICE_FURNACE,
                alarm_type="cooling_water",
                param_name=param_name,
                value=furnace_shell_pressure,
                threshold=threshold,
                level=level,
                message=f"炉皮冷却水压力 {furnace_shell_pressure:.2f}kPa 超过{_level_text(level)} {threshold:.2f}kPa",
                batch_code=batch_code
            )
    
    # 3. 检查炉盖冷却水压力
    if furnace_cover_pressure is not None:
        param_name = "cooling_pressure_cover"
        level = manager.check_value(param_name, furnace_cover_pressure)
        if level in ('warning', 'alarm'):
            config = manager.get_threshold(param_name)
            threshold = _get_exceeded_threshold(config, furnace_cover_pressure, level)
            log_alarm(
                device_id=DEVICE_FURNACE,
                alarm_type="cooling_water",
                param_name=param_name,
                value=furnace_cover_pressure,
                threshold=threshold,
                level=level,
                message=f"炉盖冷却水压力 {furnace_cover_pressure:.2f}kPa 超过{_level_text(level)} {threshold:.2f}kPa",
                batch_code=batch_code
            )
    
    # 4. 检查炉皮冷却水流速
    cooling_flows = parsed.get('cooling_flows', {})
    flow_1_data = cooling_flows.get('WATER_FLOW_1', {})
    furnace_shell_flow = flow_1_data.get('flow') if isinstance(flow_1_data, dict) else None
    if furnace_shell_flow is not None:
        param_name = "cooling_flow_shell"
        level = manager.check_value(param_name, furnace_shell_flow)
        if level in ('warning', 'alarm'):
            config = manager.get_threshold(param_name)
            threshold = _get_exceeded_threshold(config, furnace_shell_flow, level)
            log_alarm(
                device_id=DEVICE_FURNACE,
                alarm_type="cooling_water_flow",
                param_name=param_name,
                value=furnace_shell_flow,
                threshold=threshold,
                level=level,
                message=f"炉皮冷却水流速 {furnace_shell_flow:.2f}m\u00b3/h 超过{_level_text(level)} {threshold:.2f}m\u00b3/h",
                batch_code=batch_code
            )
    
    # 5. 检查炉盖冷却水流速
    flow_2_data = cooling_flows.get('WATER_FLOW_2', {})
    furnace_cover_flow = flow_2_data.get('flow') if isinstance(flow_2_data, dict) else None
    if furnace_cover_flow is not None:
        param_name = "cooling_flow_cover"
        level = manager.check_value(param_name, furnace_cover_flow)
        if level in ('warning', 'alarm'):
            config = manager.get_threshold(param_name)
            threshold = _get_exceeded_threshold(config, furnace_cover_flow, level)
            log_alarm(
                device_id=DEVICE_FURNACE,
                alarm_type="cooling_water_flow",
                param_name=param_name,
                value=furnace_cover_flow,
                threshold=threshold,
                level=level,
                message=f"炉盖冷却水流速 {furnace_cover_flow:.2f}m\u00b3/h 超过{_level_text(level)} {threshold:.2f}m\u00b3/h",
                batch_code=batch_code
            )
    
    # 6. 检查过滤器压差
    filter_diff_data = parsed.get('filter_pressure_diff', {})
    filter_diff_value = filter_diff_data.get('value') if isinstance(filter_diff_data, dict) else None
    if filter_diff_value is not None:
        param_name = "filter_pressure_diff"
        level = manager.check_value(param_name, filter_diff_value)
        if level in ('warning', 'alarm'):
            config = manager.get_threshold(param_name)
            threshold = _get_exceeded_threshold(config, filter_diff_value, level)
            log_alarm(
                device_id=DEVICE_FURNACE,
                alarm_type="filter",
                param_name=param_name,
                value=filter_diff_value,
                threshold=threshold,
                level=level,
                message=f"过滤器压差 {filter_diff_value:.2f}kPa 超过{_level_text(level)} {threshold:.2f}kPa",
                batch_code=batch_code
            )


def check_emergency_stop_alarm(parsed: Dict[str, Any], batch_code: str = ""):
    """检查高压紧急停电是否触发
    
    在 process_arc_data() 中调用，当功能使能(enabled=True)且停电标志(flag=True)时记录报警
    
    Args:
        parsed: DB1 解析后的原始数据，包含 emergency_stop 字段
        batch_code: 当前批次号
    """
    emergency_stop = parsed.get('emergency_stop', {})
    if not emergency_stop:
        return
    
    enabled = emergency_stop.get('emergency_stop_enabled', False)
    flag = emergency_stop.get('emergency_stop_flag', False)
    
    if not enabled or not flag:
        return
    
    arc_limit = emergency_stop.get('emergency_stop_arc_limit', 0)
    delay_ms = emergency_stop.get('emergency_stop_delay', 0)
    
    log_alarm(
        device_id=DEVICE_ELECTRODE,
        alarm_type="emergency_stop",
        param_name="emergency_stop_flag",
        value=1.0,
        threshold=arc_limit,
        level="alarm",
        message=f"高压紧急停电触发, 弧流上限 {arc_limit}A, 消抖 {delay_ms}ms",
        batch_code=batch_code
    )


def _get_exceeded_threshold(config, value: float, level: str) -> float:
    """获取被超过的阈值数值"""
    if not config:
        return 0.0
    
    if level == 'alarm':
        if config.alarm_max is not None and value > config.alarm_max:
            return config.alarm_max
        if config.alarm_min is not None and value < config.alarm_min:
            return config.alarm_min
    elif level == 'warning':
        if config.warning_max is not None and value > config.warning_max:
            return config.warning_max
        if config.warning_min is not None and value < config.warning_min:
            return config.warning_min
    
    return 0.0


def _level_text(level: str) -> str:
    """报警级别文本"""
    return "报警阈值" if level == 'alarm' else "警告阈值"
