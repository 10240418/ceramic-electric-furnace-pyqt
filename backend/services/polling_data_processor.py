# ============================================================
# 文件说明: polling_data_processor.py - 数据处理和缓存管理
# ============================================================
# 功能:
#   1. 解析器和转换器初始化
#   2. 内存缓存管理 (最新数据供API读取)
#   3. 批量写入缓存 (双速轮询架构)
#   4. 数据处理函数 (_process_*)
#   5. 蝶阀状态队列管理
#   6. 批量写入 InfluxDB
# ============================================================
# 【数据库写入说明】
# ============================================================
# 1: DB32 传感器数据 (写入 InfluxDB)
#    - 轮询间隔: 0.5秒
#    - 批量写入: 30次轮询后写入 (15秒)
#    - 写入条件: 必须有批次号(batch_code)且冶炼状态为running/paused
#    - 数据点:
#      * 电极深度: LENTH1/2/3 (distance_mm, high_word, low_word)
#      * 冷却水压力: WATER_PRESS_1/2 (value kPa, raw)
#      * 冷却水流量: WATER_FLOW_1/2 (value m³/h, raw)
#      * 冷却水累计: furnace_shell_water_total, furnace_cover_water_total (每15秒计算)
#      * 炉皮-炉盖压差: |炉皮压力 - 炉盖压力| (kPa)
# ============================================================
# 2: DB1 弧流弧压数据 (写入 InfluxDB)
#    - 轮询间隔: 5秒(默认) / 0.2秒(冶炼中)
#    - 批量写入: 20次轮询后写入 (4秒)
#    - 写入条件: 必须有批次号(batch_code)且冶炼状态为running/paused
#    - 数据点:
#      * 弧流: arc_current_U/V/W (A) - 每次写入
#      * 弧压: arc_voltage_U/V/W (V) - 每次写入
#      * 功率: power_U/V/W (kW), power_total (kW) - 每次写入
#      * 设定值: arc_current_setpoint_U/V/W (A) - 仅变化时写入
#      * 死区: manual_deadzone_percent (%) - 仅变化时写入
# ============================================================
# 2.1: 能耗数据 (定时计算写入)
#    - 计算间隔: 每15秒计算一次
#    - 写入方式: 计算完成后立即写入
#    - 数据点:
#      * 累计能耗: energy_U/V/W_total (kWh), energy_total (kWh)
# ============================================================
# 3: 料仓重量数据 (写入 InfluxDB)
#    - 轮询间隔: 0.5秒 (与DB32同步)
#    - 批量写入: 30次轮询后写入 (15秒)
#    - 写入条件: 必须有批次号(batch_code)且冶炼状态为running/paused
#    - 数据点:
#      * 净重: net_weight (kg)
#      * 投料累计: feeding_total (kg) - 每30秒计算一次增量
#    - 不写入数据库:
#      * 投料状态: is_discharging (仅内存缓存，用于计算投料累计)
# ============================================================
# 4: 不写入数据库的数据 (仅内存缓存)
#    - DB30 通信状态 (ModbusStatusParser)
#    - DB41 数据状态 (DataStateParser)
#    - 蝶阀状态队列 (ValveStatusMonitor) - 仅用于历史记录API
# ============================================================

import threading
import traceback
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from collections import deque

from backend.core.influxdb import write_points_batch, build_point
from backend.plc.parser_config_db32 import ConfigDrivenDB32Parser
from backend.plc.parser_config_db1 import ConfigDrivenDB1Parser
from backend.plc.parser_status import ModbusStatusParser
from backend.plc.parser_status_db41 import DataStateParser
from backend.tools.converter_furnace import FurnaceConverter
from backend.tools.converter_elec_db1_simple import (
    convert_db1_arc_data_simple,
    convert_to_influx_fields_simple,
    convert_to_influx_fields_with_change_detection,
    ArcDataSimple,
)
from backend.services.feeding_accumulator import get_feeding_accumulator
from backend.services.power_energy_calculator import get_power_energy_calculator


# ============================================================
# 解析器与转换器实例
# ============================================================
_modbus_parser: Optional[ConfigDrivenDB32Parser] = None  # DB32 传感器解析器
_db1_parser: Optional[ConfigDrivenDB1Parser] = None      # DB1 弧流弧压解析器
_status_parser: Optional[ModbusStatusParser] = None       # DB30 状态解析器
_db41_parser: Optional[DataStateParser] = None            # DB41 数据状态解析器
_db18_parser: Optional['HopperDB18Parser'] = None         # DB18 料仓电气数据解析器
_furnace_converter: Optional[FurnaceConverter] = None     # 数据转换器

# ============================================================
# 内存缓存 (供 API 直接读取)
# ============================================================
_data_lock = threading.Lock()

# 最新传感器数据缓存 (DB32)
_latest_modbus_data: Dict[str, Any] = {}
_latest_modbus_timestamp: Optional[datetime] = None

# 最新弧流弧压缓存 (DB1)
_latest_arc_data: Dict[str, Any] = {}
_latest_arc_timestamp: Optional[datetime] = None

# 最新通信状态缓存 (DB30)
_latest_status_data: Dict[str, Any] = {}
_latest_status_timestamp: Optional[datetime] = None

# 最新数据状态缓存 (DB41)
_latest_db41_data: Dict[str, Any] = {}
_latest_db41_timestamp: Optional[datetime] = None

# 最新料仓重量缓存 (Modbus RTU)
_latest_weight_data: Dict[str, Any] = {}
_latest_weight_timestamp: Optional[datetime] = None

# 最新料仓上限值缓存 (DB18)
_latest_hopper_upper_limit: float = 4900.0  # 默认4900kg
_latest_hopper_upper_limit_timestamp: Optional[datetime] = None

# ============================================================
# 设定值变化检测缓存 (用于智能写入数据库)
# ============================================================
# 上一次的设定值 (U, V, W)
_prev_setpoints: Optional[tuple] = None
# 上一次的手动死区百分比
_prev_deadzone: Optional[float] = None

# ============================================================
# 累计值变化检测缓存 (用于智能写入数据库)
# ============================================================
# 上一次写入数据库的投料累计值
_prev_feeding_total: float = 0.0
# 上一次写入数据库的冷却水累计值
_prev_furnace_shell_water_total: float = 0.0
_prev_furnace_cover_water_total: float = 0.0
# 上一次写入数据库的能耗累计值
_prev_energy_total: float = 0.0

# ============================================================
# 蝶阀状态队列缓存 (Valve Status Queue Cache)
# ============================================================
# 每个蝶阀维护一个队列，存储最近100次的开关状态
# 状态格式: "10" (关闭), "01" (打开), "11" (异常), "00" (未知)
_valve_status_queues: Dict[int, deque] = {
    1: deque(maxlen=100),  # 蝶阀1状态队列
    2: deque(maxlen=100),  # 蝶阀2状态队列
    3: deque(maxlen=100),  # 蝶阀3状态队列
    4: deque(maxlen=100),  # 蝶阀4状态队列
}
_valve_status_timestamps: Dict[int, deque] = {
    1: deque(maxlen=100),
    2: deque(maxlen=100),
    3: deque(maxlen=100),
    4: deque(maxlen=100),
}

# ============================================================
# 批量写入缓存 (双速轮询架构)
# ============================================================
#  弧流弧压缓存 (高频写入)
# - 轮询间隔: 0.2s
# - 批量大小: 20次 (0.2s×20=4s写入一次)
_arc_buffer: deque = deque(maxlen=500)
_arc_buffer_count = 0
_arc_batch_size = 20  # 20次弧流轮询后批量写入 (0.2s×20=4s)

# 📊 普通数据缓存 (常规写入)
# - 轮询间隔: 5s
# - 批量大小: 20次 (5s×20=100s写入一次)
_normal_buffer: deque = deque(maxlen=1000)
_normal_buffer_count = 0
_normal_batch_size = 20  # 20次常规轮询后批量写入 (5s×20=100s)

# ============================================================
# 统计信息
# ============================================================
_stats = {
    "total_polls": 0,
    "successful_writes": 0,
    "failed_writes": 0,
    "last_poll_time": None,
    "db32_errors": 0,
    "db1_errors": 0,
    "modbus_errors": 0,
}


# ============================================================
# 1: 解析器初始化模块
# ============================================================
def init_parsers():
    """初始化解析器"""
    global _modbus_parser, _db1_parser, _status_parser, _db41_parser, _db18_parser, _furnace_converter
    
    if _modbus_parser is None:
        try:
            _modbus_parser = ConfigDrivenDB32Parser()
            print(" DB32 传感器数据解析器已初始化")
        except Exception as e:
            print(f" DB32 解析器初始化失败: {e}")
    
    if _db1_parser is None:
        try:
            _db1_parser = ConfigDrivenDB1Parser()
            print(" DB1 弧流弧压解析器已初始化")
        except Exception as e:
            print(f" DB1 解析器初始化失败: {e}")
    
    if _status_parser is None:
        try:
            _status_parser = ModbusStatusParser()
            print(" DB30 状态解析器已初始化")
        except Exception as e:
            print(f" DB30 解析器初始化失败: {e}")
    
    if _db18_parser is None:
        try:
            from backend.plc.parser_hopper_db18 import HopperDB18Parser
            _db18_parser = HopperDB18Parser()
            print(" DB18 料仓电气数据解析器已初始化")
        except Exception as e:
            print(f" DB18 解析器初始化失败: {e}")
    
    if _db41_parser is None:
        try:
            _db41_parser = DataStateParser()
            print(" DB41 数据状态解析器已初始化")
        except Exception as e:
            print(f" DB41 解析器初始化失败: {e}")
            
    if _furnace_converter is None:
        _furnace_converter = FurnaceConverter()
        print(" 电炉数据转换器已初始化")


def get_parsers():
    """获取解析器实例（供外部调用）
    
    Returns:
        tuple: (db1_parser, modbus_parser, status_parser, db41_parser, db18_parser)
        
    注意: polling_loops_v2.py 使用元组格式调用此函数
    """
    return _db1_parser, _modbus_parser, _status_parser, _db41_parser, _db18_parser


def get_parsers_dict():
    """获取解析器实例（字典格式）
    
    Returns:
        dict: 包含所有解析器和转换器的字典
    """
    return {
        'db32_parser': _modbus_parser,
        'db1_parser': _db1_parser,
        'db30_parser': _status_parser,
        'db41_parser': _db41_parser,
        'db18_parser': _db18_parser,
        'converter': _furnace_converter
    }


# ============================================================
# 2: 数据处理函数模块
# ============================================================
def process_modbus_data(raw_data: bytes):
    """处理 DB32 传感器数据
    
    数据包含: 红外测距, 压力, 流量, 蝶阀状态
    新增: 冷却水流量计算 (0.5s轮询, 15秒累计)
    优化: 冷却水累计值只在变化时写入数据库
    """
    global _latest_modbus_data, _latest_modbus_timestamp
    global _prev_furnace_shell_water_total, _prev_furnace_cover_water_total
    
    if not _modbus_parser:
        return

    try:
        # 1. 解析原始数据
        parsed = _modbus_parser.parse_all(raw_data)
        
        # ========================================
        # 2. 冷却水流量计算 (新增逻辑)
        # ========================================
        from backend.services.cooling_water_calculator import get_cooling_water_calculator
        from backend.services.batch_service import get_batch_service
        
        cooling_calc = get_cooling_water_calculator()
        batch_service = get_batch_service()
        
        # 提取冷却水数据
        # 映射关系:
        # - WATER_FLOW_1 (offset 16) -> 炉皮流量
        # - WATER_FLOW_2 (offset 18) -> 炉盖流量
        # - WATER_PRESS_1 (offset 12) -> 炉皮水压 (过滤器进口)
        # - WATER_PRESS_2 (offset 14) -> 炉盖水压 (过滤器出口)
        cooling_flows = parsed.get('cooling_flows', {})
        cooling_pressures = parsed.get('cooling_pressures', {})
        
        # 流量提取 (m³/h)
        flow_1_data = cooling_flows.get('WATER_FLOW_1', {})
        flow_2_data = cooling_flows.get('WATER_FLOW_2', {})
        furnace_shell_flow = flow_1_data.get('flow', 0.0) if isinstance(flow_1_data, dict) else 0.0
        furnace_cover_flow = flow_2_data.get('flow', 0.0) if isinstance(flow_2_data, dict) else 0.0
        
        # 压力提取 (原始单位 ×0.01 kPa)
        press_1_data = cooling_pressures.get('WATER_PRESS_1', {})
        press_2_data = cooling_pressures.get('WATER_PRESS_2', {})
        furnace_shell_pressure = press_1_data.get('pressure', 0.0) if isinstance(press_1_data, dict) else 0.0
        furnace_cover_pressure = press_2_data.get('pressure', 0.0) if isinstance(press_2_data, dict) else 0.0
        
        # 【修复】只有在运行状态时才添加测量数据和计算累计
        if batch_service.is_running:
            # 添加测量数据并获取压差
            cooling_result = cooling_calc.add_measurement(
                furnace_cover_flow=furnace_cover_flow,
                furnace_shell_flow=furnace_shell_flow,
                furnace_cover_pressure=furnace_cover_pressure,
                furnace_shell_pressure=furnace_shell_pressure,
            )
            
            # 计算后的压差存入 parsed 供后续使用
            parsed['filter_pressure_diff'] = {
                'value': cooling_result['pressure_diff'],
                'unit': 'kPa'
            }
            
            # 检查是否需要计算累计流量 (每15秒)
            if cooling_result['should_calc_volume']:
                volume_result = cooling_calc.calculate_volume_increment()
                # 更新累计流量到 parsed
                parsed['furnace_cover_total_volume'] = volume_result['furnace_cover_total']
                parsed['furnace_shell_total_volume'] = volume_result['furnace_shell_total']
            else:
                # 使用缓存的累计值
                volumes = cooling_calc.get_total_volumes()
                parsed['furnace_cover_total_volume'] = volumes['furnace_cover']
                parsed['furnace_shell_total_volume'] = volumes['furnace_shell']
        else:
            # 【修复】终止冶炼后，只计算压差，不累计流量
            parsed['filter_pressure_diff'] = {
                'value': furnace_shell_pressure - furnace_cover_pressure,
                'unit': 'kPa'
            }
            # 使用缓存的累计值（不再增加）
            volumes = cooling_calc.get_total_volumes()
            parsed['furnace_cover_total_volume'] = volumes['furnace_cover']
            parsed['furnace_shell_total_volume'] = volumes['furnace_shell']
        
        # 3. 更新内存缓存 (供实时API使用)
        with _data_lock:
            _latest_modbus_data = parsed
            _latest_modbus_timestamp = datetime.now()
            
            # ========================================
            # 蝶阀状态队列更新逻辑 (旧版 - 仅用于历史记录API)
            # ========================================
            valve_status_data = parsed.get('valve_status', {})
            valve_status_byte = valve_status_data.get('raw_byte', 0)
            timestamp = datetime.now(timezone.utc)
            
            # 解析每个蝶阀的2-bit状态
            for valve_id in range(1, 5):  # 蝶阀1-4
                bit_offset = (valve_id - 1) * 2
                bit_close = (valve_status_byte >> bit_offset) & 0x01
                bit_open = (valve_status_byte >> (bit_offset + 1)) & 0x01
                
                # 组合成状态字符串: "10"(关), "01"(开), "11"(异常), "00"(未知)
                status = f"{bit_close}{bit_open}"
                
                # 添加到队列
                _valve_status_queues[valve_id].append(status)
                _valve_status_timestamps[valve_id].append(timestamp.isoformat())
        
        # ========================================
        # 3.1 写入统一缓存 DataCache + 发送信号 DataBridge
        # ========================================
        try:
            from backend.bridge.data_cache import get_data_cache
            from backend.bridge.data_bridge import get_data_bridge
            import time
            
            data_cache = get_data_cache()
            data_bridge = get_data_bridge()
            
            # 获取蝶阀开度数据
            from backend.services.valve_calculator_service import get_all_valve_openness
            valve_openness_list = get_all_valve_openness()
            valve_openness_dict = {v['valve_id']: v['openness_percent'] for v in valve_openness_list}
            
            # 构建传感器数据
            sensor_data = {
                'electrode_depths': parsed.get('electrode_depths', {}),
                'cooling': {
                    'flows': parsed.get('cooling_flows', {}),
                    'pressures': parsed.get('cooling_pressures', {}),
                    'pressure_diff': parsed.get('filter_pressure_diff', {}),
                    'cover_total': parsed.get('furnace_cover_total_volume', 0.0),  # 炉盖累计流量
                    'shell_total': parsed.get('furnace_shell_total_volume', 0.0),  # 炉皮累计流量
                },
                'hopper': _latest_weight_data.copy() if _latest_weight_data else {},
                'valve_status': parsed.get('valve_status', {}),
                'valve_openness': valve_openness_dict,
                'energy_total': 0.0,  # 占位，后续从功率计算器获取
                'timestamp': time.time()
            }
            
            # 获取最新能耗数据
            try:
                from backend.services.power_energy_calculator import get_power_energy_calculator
                power_calc = get_power_energy_calculator()
                realtime_power_data = power_calc.get_realtime_data()
                sensor_data['energy_total'] = realtime_power_data.get('energy_total', 0.0)
            except Exception as e:
                pass  # 能耗数据获取失败不影响主流程
            
            # 写入缓存
            data_cache.set_sensor_data(sensor_data)
            
            # 发送信号到前端
            data_bridge.emit_sensor_data(sensor_data)
            
        except Exception as bridge_err:
            print(f" 写入 DataCache/DataBridge 失败: {bridge_err}")
        
        # ========================================
        # 4. 蝶阀开度计算服务 (新增 - 滑动窗口 + 自动校准)
        # ========================================
        try:
            from backend.services.valve_calculator_service import batch_add_valve_statuses
            valve_status_data = parsed.get('valve_status', {})
            valve_status_byte = valve_status_data.get('raw_byte', 0)
            batch_add_valve_statuses(valve_status_byte, datetime.now(timezone.utc))
        except Exception as valve_err:
            print(f" 蝶阀开度计算失败: {valve_err}")
        
        # 5. 转换为 InfluxDB Points (供历史存储)
        # 重要: 只有在有批次号时才写入数据库，避免产生无批次的杂乱数据
        now = datetime.now(timezone.utc)
        
        # 获取当前批次号 (仅由前端提供，后端不自动生成)
        from backend.services.polling_service import ensure_batch_code
        batch_code = ensure_batch_code()
        
        # 只有在有批次号时才写入历史数据库
        if batch_code and _furnace_converter:
            dict_points = _furnace_converter.convert_to_points(parsed, now, batch_code)
            _normal_buffer.extend(dict_points)
            
            # ========================================
            # 6. 添加冷却水累计量 Point (用于历史查询)
            # 【优化】只在累计值变化时写入
            # ========================================
            shell_total = parsed.get('furnace_shell_total_volume', 0.0)
            cover_total = parsed.get('furnace_cover_total_volume', 0.0)
            
            # 检查是否变化（变化超过 0.01 m³ 才写入）
            shell_changed = abs(shell_total - _prev_furnace_shell_water_total) > 0.01
            cover_changed = abs(cover_total - _prev_furnace_cover_water_total) > 0.01
            
            if shell_changed or cover_changed:
                water_point = {
                    'measurement': 'sensor_data',
                    'tags': {
                        'device_type': 'electric_furnace',
                        'module_type': 'cooling_water_total',
                        'device_id': 'furnace_1',
                        'batch_code': batch_code
                    },
                    'fields': {
                        'furnace_shell_water_total': shell_total,
                        'furnace_cover_water_total': cover_total,
                    },
                    'time': now
                }
                _normal_buffer.append(water_point)
                
                # 更新上次写入的值
                _prev_furnace_shell_water_total = shell_total
                _prev_furnace_cover_water_total = cover_total
            
            # ========================================
            # 7. 添加炉皮-炉盖压差绝对值 Point (用于历史查询)
            # ========================================
            pressure_diff_abs = abs(furnace_shell_pressure - furnace_cover_pressure)
            pressure_diff_point = {
                'measurement': 'sensor_data',
                'tags': {
                    'device_type': 'electric_furnace',
                    'module_type': 'cooling_system',
                    'device_id': 'furnace_1',
                    'metric': 'pressure_diff',
                    'batch_code': batch_code
                },
                'fields': {
                    'value': pressure_diff_abs,
                },
                'time': now
            }
            _normal_buffer.append(pressure_diff_point)
            
    except Exception as e:
        print(f" 处理 DB32 数据失败: {e}")
        import traceback
        traceback.print_exc()


def process_arc_data(raw_data: bytes, batch_code: str):
    """处理 DB1 弧流弧压数据 (缓存 + 写入数据库)
    
    设定值和死区仅在变化时才写入数据库
    新增: 功率计算和能耗累计
    优化: 能耗累计值只在变化时写入数据库
    
    重要: 无论是否有批次号，都会更新实时缓存（供前端显示）
          只有有批次号时才写入历史数据库
    
    Args:
        raw_data: DB1 原始字节数据
        batch_code: 当前批次号（可能为空）
    """
    global _latest_arc_data, _latest_arc_timestamp
    global _prev_setpoints, _prev_deadzone, _prev_energy_total
    
    if not _db1_parser:
        return

    try:
        # 1. 解析原始数据
        parsed = _db1_parser.parse_all(raw_data)
        
        # 2. 使用简化转换器 (直接使用原始值)
        arc_data_obj: ArcDataSimple = convert_db1_arc_data_simple(parsed)
        
        # ========================================
        # 3. 计算三相功率 (新增)
        # ========================================
        power_calc = get_power_energy_calculator()
        power_result = power_calc.calculate_power(
            arc_current_U=arc_data_obj.phase_U.current_A,
            arc_voltage_U=arc_data_obj.phase_U.voltage_V,
            arc_current_V=arc_data_obj.phase_V.current_A,
            arc_voltage_V=arc_data_obj.phase_V.voltage_V,
            arc_current_W=arc_data_obj.phase_W.current_A,
            arc_voltage_W=arc_data_obj.phase_W.voltage_V,
        )
        
        # 4. 构建缓存数据 (UVW三相 + 三个设定值 + 手动死区 + 功率)
        setpoints = arc_data_obj.get_setpoints_A()
        arc_cache = {
            'parsed': parsed,
            'converted': arc_data_obj.to_dict(),
            'arc_current': {
                'U': arc_data_obj.phase_U.current_A,
                'V': arc_data_obj.phase_V.current_A,
                'W': arc_data_obj.phase_W.current_A,
            },
            'arc_voltage': {
                'U': arc_data_obj.phase_U.voltage_V,
                'V': arc_data_obj.phase_V.voltage_V,
                'W': arc_data_obj.phase_W.voltage_V,
            },
            'power_total': power_result['power_total'],
            'setpoints': {
                'U': setpoints[0],
                'V': setpoints[1],
                'W': setpoints[2],
            },
            'manual_deadzone_percent': arc_data_obj.manual_deadzone_percent,
            'timestamp': arc_data_obj.timestamp
        }
        
        # 5. 更新内存缓存
        with _data_lock:
            _latest_arc_data = arc_cache
            _latest_arc_timestamp = datetime.now()
        
        # ========================================
        # 5.1 写入统一缓存 DataCache + 发送信号 DataBridge
        # ========================================
        try:
            from backend.bridge.data_cache import get_data_cache
            from backend.bridge.data_bridge import get_data_bridge
            import time
            
            data_cache = get_data_cache()
            data_bridge = get_data_bridge()
            
            # 获取最新能耗数据（使用已导入的 get_power_energy_calculator）
            realtime_power_data = power_calc.get_realtime_data()
            
            # 构建弧流数据（包含能耗和紧急停电数据）
            arc_data = {
                'arc_current': arc_cache['arc_current'],
                'arc_voltage': arc_cache['arc_voltage'],
                'power_total': arc_cache['power_total'],
                'energy_total': realtime_power_data.get('energy_total', 0.0),  # 添加能耗
                'setpoints': arc_cache['setpoints'],
                'manual_deadzone_percent': arc_cache['manual_deadzone_percent'],
                'emergency_stop': parsed.get('emergency_stop', {}),  # 添加紧急停电数据
                'timestamp': time.time()
            }
            
            # 写入缓存
            data_cache.set_arc_data(arc_data)
            
            # 发送信号到前端
            data_bridge.emit_arc_data(arc_data)
            
        except Exception as bridge_err:
            print(f" 写入 DataCache/DataBridge 失败: {bridge_err}")
        
        # 6. 使用变化检测转换为 InfluxDB 字段
        now = datetime.now(timezone.utc)
        change_result = convert_to_influx_fields_with_change_detection(
            arc_data_obj, _prev_setpoints, _prev_deadzone
        )
        arc_fields = change_result['fields']
        
        # 7. 添加总功率字段到 arc_fields
        arc_fields['power_total'] = power_result['power_total']
        
        # 8: 更新上一次的值
        _prev_setpoints = change_result['current_setpoints']
        _prev_deadzone = change_result['current_deadzone']

        # ========================================
        # 9: 写入历史数据库（仅在有批次号时）
        # ========================================
        if batch_code and arc_fields:
            point_dict = {
                'measurement': 'sensor_data',
                'tags': {
                    'device_type': 'electric_furnace',
                    'module_type': 'arc_data',
                    'device_id': 'electrode',
                    'batch_code': batch_code
                },
                'fields': arc_fields,
                'time': now
            }
            _arc_buffer.append(point_dict)
            
            # 日志：只在设定值或死区变化时输出
            # setpoint_info = ""
            # if change_result['has_setpoint_change']:
            #     setpoint_info = f", 设定值变化: U={setpoints[0]}A V={setpoints[1]}A W={setpoints[2]}A"
            # if change_result['has_deadzone_change']:
            #     setpoint_info += f", 死区变化: {arc_data_obj.manual_deadzone_percent}%"
            
            # print(f" [DB1] 弧流弧压+功率数据已缓存: U相弧流={arc_data_obj.phase_U.current_A}A, "
            #       f"功率={power_result['power_total']:.2f}kW{setpoint_info}")
        
        # ========================================
        # 10. 检查是否需要计算能耗 (每15秒)
        # 【优化】只在能耗累计值变化时写入
        # ========================================
        # 【修复】只有在运行状态且有批次号时才计算能耗
        from backend.services.batch_service import get_batch_service
        batch_service_check = get_batch_service()
        
        if batch_code and batch_service_check.is_running and power_result['should_calc_energy']:
            energy_result = power_calc.calculate_energy_increment()
            current_energy_total = energy_result['energy_total']
            
            # 检查能耗是否变化（变化超过 0.01 kWh 才写入）
            energy_changed = abs(current_energy_total - _prev_energy_total) > 0.01
            
            if energy_changed:
                # 将能耗数据添加到缓存（批量写入）
                energy_point = {
                    'measurement': 'sensor_data',
                    'tags': {
                        'device_type': 'electric_furnace',
                        'module_type': 'energy_consumption',
                        'device_id': 'electrode',
                        'batch_code': batch_code
                    },
                    'fields': {
                        'energy_total': current_energy_total,
                    },
                    'time': now
                }
                _arc_buffer.append(energy_point)
                
                # 更新上次写入的值
                _prev_energy_total = current_energy_total
            
    except Exception as e:
        print(f" 处理 DB1 弧流弧压数据失败: {e}")
        traceback.print_exc()


def process_status_data(raw_data: bytes):
    """处理 DB30 状态数据 (只缓存，不写入数据库)"""
    global _latest_status_data, _latest_status_timestamp
    
    if not _status_parser:
        return

    try:
        parsed = _status_parser.parse_all(raw_data)
        
        with _data_lock:
            _latest_status_data = parsed
            _latest_status_timestamp = datetime.now()
        
        # ========================================
        # 发送连接状态到前端 (可选)
        # ========================================
        try:
            from backend.bridge.data_bridge import get_data_bridge
            data_bridge = get_data_bridge()
            
            # 检查 PLC 连接状态
            plc_connected = parsed.get('plc_connected', False)
            data_bridge.emit_connection_status(plc_connected)
            
        except Exception as bridge_err:
            pass  # 状态数据不是关键数据，失败不影响主流程
            
    except Exception as e:
        print(f" 处理 DB30 状态数据失败: {e}")


def process_db41_data(raw_data: bytes):
    """处理 DB41 数据状态 (只缓存，不写入数据库)"""
    global _latest_db41_data, _latest_db41_timestamp
    
    if not _db41_parser:
        return

    try:
        parsed = _db41_parser.parse_all(raw_data)
        
        with _data_lock:
            _latest_db41_data = parsed
            _latest_db41_timestamp = datetime.now()
            
    except Exception as e:
        print(f" 处理 DB41 数据状态失败: {e}")


# ============================================================
# 3: 批量写入 InfluxDB 模块
# ============================================================

def process_weight_data(
    weight_result: Dict[str, Any],
    batch_code: str,
    is_discharging: bool = False,
    is_requesting: bool = False
):
    """处理料仓重量数据 (Modbus RTU + PLC 投料信号)
    
    优化: 只在投料累计值变化时写入数据库，避免重复写入相同的累计值
    
    Args:
        weight_result: read_hopper_weight() 返回的结果
        batch_code: 当前批次号
        is_discharging: %Q3.7 秤排料信号 (True=正在投料)
        is_requesting: %Q4.0 秤要料信号
    """
    global _latest_weight_data, _latest_weight_timestamp, _prev_feeding_total

    try:
        # 1. 更新内存缓存 (始终更新，即使没有批次号)
        with _data_lock:
            _latest_weight_data = weight_result
            _latest_weight_timestamp = datetime.now()
        
        # 只有有批次号时才写入数据库
        if not batch_code:
            return
        
        # 2. 如果读取成功，处理投料累计
        if weight_result.get('success') and weight_result.get('weight') is not None:
            weight_kg = float(weight_result['weight'])
            now = datetime.now(timezone.utc)
            
            # ========================================
            # 2.1 投料累计器：添加数据点到队列
            # 【修复】只有在运行状态时才添加数据和计算
            # ========================================
            from backend.services.batch_service import get_batch_service
            batch_service = get_batch_service()
            
            feeding_acc = get_feeding_accumulator()
            
            if batch_service.is_running:
                feeding_result = feeding_acc.add_measurement(
                    weight_kg=weight_kg,
                    is_discharging=is_discharging,
                    is_requesting=is_requesting
                )
                
                # 2.2 检查是否需要计算投料 (每30秒)
                if feeding_result['should_calc']:
                    calc_result = feeding_acc.calculate_feeding()
                    # print(f"📊 投料计算完成: 本次新增 {calc_result['total_added']:.1f}kg, 累计 {calc_result['feeding_total']:.1f}kg")
            
            # 获取当前累计值
            current_feeding_total = feeding_acc.get_feeding_total()
            
            # 更新缓存中的投料总量
            with _data_lock:
                _latest_weight_data['feeding_total'] = current_feeding_total
                _latest_weight_data['is_discharging'] = is_discharging
            
            # ========================================
            # 2.2.1 更新 DataCache 中的料仓数据
            # ========================================
            try:
                from backend.bridge.data_cache import get_data_cache
                data_cache = get_data_cache()
                
                # 获取最新的传感器数据并更新料仓部分
                sensor_data = data_cache.get_sensor_data()
                if sensor_data:
                    sensor_data['hopper'] = {
                        'weight': weight_kg,
                        'feeding_total': current_feeding_total,
                        'is_discharging': is_discharging,
                        'is_requesting': is_requesting
                    }
                    sensor_data['timestamp'] = datetime.now().timestamp()
                    data_cache.set_sensor_data(sensor_data)
            except Exception as cache_err:
                pass  # 缓存更新失败不影响主流程
            
            # ========================================
            # 2.3 转换为 InfluxDB Point
            # 【优化】只在投料累计值变化时写入 feeding_total
            # ========================================
            if batch_service.is_running:
                # 检查累计值是否变化（变化超过 0.1kg 才写入）
                feeding_total_changed = abs(current_feeding_total - _prev_feeding_total) > 0.1
                
                # 构建 fields
                fields = {'net_weight': weight_kg}
                
                # 只在累计值变化时添加 feeding_total 字段
                if feeding_total_changed:
                    fields['feeding_total'] = current_feeding_total
                    _prev_feeding_total = current_feeding_total  # 更新上次写入的值
                
                point_dict = {
                    'measurement': 'sensor_data',
                    'tags': {
                        'device_type': 'electric_furnace',
                        'module_type': 'hopper_weight',
                        'device_id': 'hopper_1',
                        'batch_code': batch_code
                    },
                    'fields': fields,
                    'time': now
                }
                
                _normal_buffer.append(point_dict)
            
    except Exception as e:
        print(f" 处理料仓重量数据失败: {e}")
        import traceback
        traceback.print_exc()


# ============================================================
# 批量写入 InfluxDB
# ============================================================
async def flush_arc_buffer():
    """批量写入 DB1 弧流弧压缓存
    
    注意: 只有在运行状态 (is_running=True) 时才写入数据库
    终止冶炼后（PAUSED状态）不写入数据库
    断电恢复后状态为 running，会继续写入数据
    """
    global _stats, _arc_buffer
    
    if not _arc_buffer:
        return
    
    # 检查批次状态 - 只有运行中（RUNNING）才写数据库
    from backend.services.batch_service import get_batch_service
    batch_service = get_batch_service()
    
    if not batch_service.is_running:
        # 未运行时（IDLE/PAUSED/STOPPED），清空缓存但不写入
        skipped_count = len(_arc_buffer)
        _arc_buffer.clear()
        if skipped_count > 0:
            print(f"⏸️ [DB1] 跳过写入 {skipped_count} 个数据点 (状态: {batch_service.state.value})")
        return
    
    dict_points_list = list(_arc_buffer)
    _arc_buffer.clear()
    
    influx_points = []
    for dp in dict_points_list:
        p = build_point(dp['measurement'], dp['tags'], dp['fields'], dp['time'])
        if p:
            influx_points.append(p)
            
    if not influx_points:
        return

    try:
        success, err = write_points_batch(influx_points)
        if success:
            _stats["successful_writes"] += len(influx_points)
            print(f" [DB1] 批量写入成功: {len(influx_points)} 个数据点")
        else:
            _stats["failed_writes"] += len(influx_points)
            print(f" [DB1] 批量写入失败: {err}")
        
    except Exception as e:
        _stats["failed_writes"] += len(influx_points)
        print(f" [DB1] 批量写入异常: {e}")


async def flush_normal_buffer():
    """批量写入 DB32/重量缓存
    
    注意: 只有在运行状态 (is_running=True) 时才写入数据库
    终止冶炼后（PAUSED状态）不写入数据库
    断电恢复后状态为 running，会继续写入数据
    """
    global _stats, _normal_buffer
    
    if not _normal_buffer:
        return
    
    # 检查批次状态 - 只有运行中（RUNNING）才写数据库
    from backend.services.batch_service import get_batch_service
    batch_service = get_batch_service()
    
    if not batch_service.is_running:
        # 未运行时（IDLE/PAUSED/STOPPED），清空缓存但不写入
        skipped_count = len(_normal_buffer)
        _normal_buffer.clear()
        if skipped_count > 0:
            print(f"⏸️ [DB32] 跳过写入 {skipped_count} 个数据点 (状态: {batch_service.state.value})")
        return
    
    dict_points_list = list(_normal_buffer)
    _normal_buffer.clear()
    
    influx_points = []
    for dp in dict_points_list:
        p = build_point(dp['measurement'], dp['tags'], dp['fields'], dp['time'])
        if p:
            influx_points.append(p)
            
    if not influx_points:
        return

    try:
        success, err = write_points_batch(influx_points)
        if success:
            _stats["successful_writes"] += len(influx_points)
            print(f" [DB32] 批量写入成功: {len(influx_points)} 个数据点")
        else:
            _stats["failed_writes"] += len(influx_points)
            print(f" [DB32] 批量写入失败: {err}")
        
    except Exception as e:
        _stats["failed_writes"] += len(influx_points)
        print(f" [DB32] 批量写入异常: {e}")


# ============================================================
# 4: 缓存数据获取函数模块 (供 API 调用)
# ============================================================
def get_latest_modbus_data() -> Dict[str, Any]:
    """获取最新的 DB32 传感器数据"""
    with _data_lock:
        return {
            'data': _latest_modbus_data.copy() if _latest_modbus_data else {},
            'timestamp': _latest_modbus_timestamp.isoformat() if _latest_modbus_timestamp else None
        }


def get_latest_arc_data() -> Dict[str, Any]:
    """获取最新的 DB1 弧流弧压数据"""
    with _data_lock:
        return {
            'data': _latest_arc_data.copy() if _latest_arc_data else {},
            'timestamp': _latest_arc_timestamp.isoformat() if _latest_arc_timestamp else None
        }


def get_latest_status_data() -> Dict[str, Any]:
    """获取最新的 DB30 通信状态数据"""
    with _data_lock:
        return {
            'data': _latest_status_data.copy() if _latest_status_data else {},
            'timestamp': _latest_status_timestamp.isoformat() if _latest_status_timestamp else None
        }


def get_latest_db41_data() -> Dict[str, Any]:
    """获取最新的 DB41 数据状态"""
    with _data_lock:
        return {
            'data': _latest_db41_data.copy() if _latest_db41_data else {},
            'timestamp': _latest_db41_timestamp.isoformat() if _latest_db41_timestamp else None
        }


def get_latest_weight_data() -> Dict[str, Any]:
    """获取最新的料仓重量数据"""
    with _data_lock:
        return {
            'data': _latest_weight_data.copy() if _latest_weight_data else {},
            'timestamp': _latest_weight_timestamp.isoformat() if _latest_weight_timestamp else None
        }


def get_latest_electricity_data() -> Dict[str, Any]:
    """获取最新的电表数据
    
    注意: 当前版本无独立电表采集，返回空数据。
    电力相关数据请使用 get_latest_arc_data() 获取弧流弧压。
    """
    return {
        'data': {
            'converted': {
                'Pt': 0.0,       # 总功率 kW (暂无)
                'Ua_0': 0.0,     # A相电压 V (暂无)
                'I_0': 0.0,      # A相电流 A (暂无)
                'I_1': 0.0,      # B相电流 A (暂无)
                'I_2': 0.0,      # C相电流 A (暂无)
                'ImpEp': 0.0,    # 累计电能 kWh (暂无)
            },
            'summary': {},
            'ct_ratio': 20,
        },
        'timestamp': None
    }


def get_valve_status_queues() -> Dict[int, List[Dict[str, Any]]]:
    """获取4个蝶阀的状态队列"""
    with _data_lock:
        result = {}
        for valve_id in range(1, 5):
            status_list = list(_valve_status_queues[valve_id])
            timestamp_list = list(_valve_status_timestamps[valve_id])
            
            result[valve_id] = [
                {
                    "status": status,
                    "timestamp": ts,
                    "state_name": _parse_valve_state_name(status)
                }
                for status, ts in zip(status_list, timestamp_list)
            ]
        
        return result


def _parse_valve_state_name(status: str) -> str:
    """解析蝶阀状态名称"""
    state_map = {
        "10": "closed",
        "01": "open",
        "11": "error",
        "00": "unknown"
    }
    return state_map.get(status, "unknown")


def get_buffer_status() -> Dict[str, Any]:
    """获取缓存状态"""
    return {
        'arc_buffer_size': len(_arc_buffer),
        'normal_buffer_size': len(_normal_buffer),
        'arc_batch_size': _arc_batch_size,
        'normal_batch_size': _normal_batch_size,
        'stats': _stats.copy()
    }


def update_stats(key: str, value: Any):
    """更新统计信息"""
    global _stats
    _stats[key] = value


# ============================================================
# DB18 料仓电气数据处理模块
# ============================================================
def process_hopper_db18_data(raw_data: bytes):
    """处理 DB18 料仓电气数据
    
    主要功能: 解析料仓上限值
    
    Args:
        raw_data: DB18 原始字节数据
    """
    global _latest_hopper_upper_limit, _latest_hopper_upper_limit_timestamp
    
    if not _db18_parser:
        return
    
    try:
        # 解析 DB18 数据
        parsed = _db18_parser.parse(raw_data)
        
        # 提取料仓上限值
        upper_limit = parsed.get('upper_limit', 4900.0)
        
        # 更新内存缓存
        with _data_lock:
            _latest_hopper_upper_limit = upper_limit
            _latest_hopper_upper_limit_timestamp = datetime.now()
        
    except Exception as e:
        print(f"处理 DB18 数据失败: {e}")
        import traceback
        traceback.print_exc()


def get_hopper_upper_limit() -> float:
    """获取料仓上限值
    
    Returns:
        料仓上限值 (kg)
    """
    with _data_lock:
        return _latest_hopper_upper_limit
