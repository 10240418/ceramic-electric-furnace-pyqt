# ============================================================
# 文件说明: polling_loops_v2.py - 独立的三速轮询架构
# ============================================================
# 功能:
#   1. DB1 弧流弧压轮询 (可变速: 5s/0.2s)
#   2. DB32 传感器轮询 (固定: 5s)
#   3. DB30/DB41 状态轮询 (固定: 5s, 仅缓存)
# ============================================================
# 设计原则:
#   - 三个独立的 asyncio.Task
#   - 自动启动 (无需前端触发)
#   - 开始冶炼时切换 DB1 速度
# ============================================================
# 【数据库写入说明 - 轮询架构】
# ============================================================
# 1: DB1 弧流弧压轮询 (_db1_arc_polling_loop)
#    - 轮询间隔: 5秒(默认) / 0.2秒(冶炼中)
#    - 批量写入: 20次轮询后写入 (4秒)
#    - 写入条件: 必须有批次号(batch_code)且冶炼状态为running/paused
#    - 数据点: 弧流(3) + 弧压(3) + 设定值(3,仅变化) + 死区(1,仅变化)
# ============================================================
# 2: DB32 传感器轮询 (_db32_sensor_polling_loop)
#    - 轮询间隔: 0.5秒
#    - 批量写入: 30次轮询后写入 (15秒)
#    - 写入条件: 必须有批次号(batch_code)且冶炼状态为running/paused
#    - 数据点: 电极深度(3) + 冷却水压力(2) + 冷却水流量(2) + 冷却水累计(2)
# ============================================================
# 3: 料仓重量轮询 (与DB32同步)
#    - 轮询间隔: 0.5秒
#    - 批量写入: 30次轮询后写入 (15秒)
#    - 写入条件: 必须有批次号(batch_code)且冶炼状态为running/paused
#    - 数据点: 净重(1) + 投料累计(1) + 投料状态(1)
# ============================================================
# 4: DB30/DB41 状态轮询 (_status_polling_loop)
#    - 轮询间隔: 5秒
#    - 写入: 不写入数据库，仅内存缓存
#    - 数据点: 通信状态 + 数据有效性状态
# ============================================================

import asyncio
import traceback
from datetime import datetime, timezone
from typing import Optional

from backend.config import get_settings
from backend.plc.plc_manager import get_plc_manager
from loguru import logger

settings = get_settings()

# ============================================================
# 全局变量 (轮询任务)
# ============================================================
_db1_task: Optional[asyncio.Task] = None
_db32_task: Optional[asyncio.Task] = None
_status_task: Optional[asyncio.Task] = None
_db36_task: Optional[asyncio.Task] = None

# 运行标志
_db1_running = False
_db32_running = False
_status_running = False
_db36_running = False

# DB1 轮询间隔 (秒) - 可动态修改 (默认值从 .env 读取)
_db1_interval: float = settings.db1_polling_interval

# 批量写入缓存 (与旧架构保持一致)
_arc_buffer_count = 0
_arc_batch_size = 20  #  DB1: 20次轮询后写入 (0.5s×20=10s)

_normal_buffer_count = 0
_normal_batch_size = 30  # 📊 DB32: 30次轮询后写入 (0.5s×30=15s)

_valve_buffer_count = 0
_valve_batch_size = 30  #  Valve: 30次轮询后写入 (0.5s×30=15s)


# ============================================================
# 1: 批量写入函数模块
# ============================================================
async def _flush_arc_buffer():
    """批量写入 DB1 弧流弧压缓存"""
    from backend.services.polling_data_processor import flush_arc_buffer
    await flush_arc_buffer()


async def _flush_normal_buffer():
    """批量写入 DB32/重量缓存"""
    from backend.services.polling_data_processor import flush_normal_buffer
    await flush_normal_buffer()


async def _flush_valve_buffer():
    """批量写入蝶阀开度缓存"""
    from backend.services.db32.valve_calculator import flush_valve_openness_buffers
    await flush_valve_openness_buffers()


# ============================================================
# 2: 状态查询函数模块
# ============================================================
def get_polling_loops_status() -> dict:
    """获取所有轮询循环的状态
    
    Returns:
        dict: {
            'db1_running': bool,
            'db32_running': bool,
            'status_running': bool,
            'db1_interval': float
        }
    """
    return {
        'db1_running': _db1_running,
        'db32_running': _db32_running,
        'status_running': _status_running,
        'db1_interval': _db1_interval
    }


# ============================================================
# 3: DB1 弧流弧压轮询模块 (可变速)
# ============================================================
async def _db1_arc_polling_loop(
    parser,
    process_func,
    is_mock: bool = False
):
    """DB1 弧流弧压轮询 (可变速: 5s -> 0.5s)
    
    Args:
        parser: DB1 解析器
        process_func: 数据处理函数
        is_mock: 是否 Mock 模式
    """
    global _db1_interval, _arc_buffer_count, _arc_batch_size
    poll_count = 0
    error_count = 0  # 连续错误计数器
    MAX_ERROR_COUNT = 10  # 最大错误次数，超过后固定30s
    FIXED_WAIT_TIME = 30  # 固定等待时间（秒）
    
    logger.info(f"DB1 弧流弧压轮询已启动 (初始间隔: {_db1_interval}s)")
    
    if not is_mock:
        plc = get_plc_manager()
        db_number = parser.get_db_number() if parser else 1
        db_size = parser.get_total_size() if parser else 182
    
    while _db1_running:
        try:
            poll_count += 1
            
            if is_mock:
                # Mock 模式: 生成随机数据
                from backend.services.polling_data_generator import generate_mock_db1_data
                db1_data = generate_mock_db1_data()
            else:
                # PLC 模式: 读取真实数据
                if not plc.is_connected():
                    plc.connect()
                
                result = plc.read_db(db_number, 0, db_size)
                if isinstance(result, (tuple, list)) and len(result) == 2:
                    db1_data, err = result
                else:
                    db1_data = None
                
                if not db1_data:
                    await asyncio.sleep(1)
                    continue
            
            # 处理数据 (获取当前批次号)
            from backend.services.polling_service import get_batch_info
            batch_info = get_batch_info()
            current_batch = batch_info.get('batch_code', '')  # 没有批次号时传空字符串
            
            # 无论是否冶炼，都处理数据（更新实时缓存）
            # process_arc_data 内部会判断：有批次号时写入历史数据库，无批次号时只更新缓存
            process_func(db1_data, current_batch)
            
            # 批量写入逻辑
            _arc_buffer_count += 1
            if _arc_buffer_count >= _arc_batch_size:
                await _flush_arc_buffer()
                _arc_buffer_count = 0
            
            # 成功后重置错误计数器
            error_count = 0
            
            # 动态间隔 (可被外部修改)
            await asyncio.sleep(_db1_interval)
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            error_count += 1
            
            # 10次失败后，固定等待30秒
            if error_count >= MAX_ERROR_COUNT:
                logger.error(f"DB1 轮询异常 (第{error_count}次，已达上限): {e}")
                if error_count == MAX_ERROR_COUNT:
                    logger.warning(f"DB1 连续失败 {MAX_ERROR_COUNT} 次，后续每次固定等待 {FIXED_WAIT_TIME}s")
                await asyncio.sleep(FIXED_WAIT_TIME)
            else:
                # 前10次使用指数退避
                wait_time = min(FIXED_WAIT_TIME, 2 ** min(error_count - 1, 4))
                logger.error(f"DB1 轮询异常 (第{error_count}次): {e}")
                if error_count <= 3:
                    logger.error(traceback.format_exc())
                await asyncio.sleep(wait_time)
    
    logger.info("DB1 弧流弧压轮询已停止")


# ============================================================
# 4: DB32 传感器轮询模块 (固定 0.5s)
# ============================================================
async def _db32_sensor_polling_loop(
    parser,
    process_func,
    db18_parser,
    db19_parser,
    process_hopper_plc_func,
    is_mock: bool = False
):
    """DB32 传感器 + 料仓 PLC 数据轮询 (固定 0.5s)
    
    Args:
        parser: DB32 解析器
        process_func: 数据处理函数
        db18_parser: DB18 解析器
        db19_parser: DB19 解析器
        process_hopper_plc_func: 料仓 PLC 数据处理函数
        is_mock: 是否 Mock 模式
    """
    global _normal_buffer_count, _normal_batch_size, _valve_buffer_count, _valve_batch_size
    poll_count = 0
    error_count = 0  # 连续错误计数器
    MAX_ERROR_COUNT = 10  # 最大错误次数，超过后固定30s
    FIXED_WAIT_TIME = 30  # 固定等待时间（秒）
    interval = settings.db32_polling_interval  # 从 .env 配置读取
    
    logger.info(f"DB32 传感器轮询已启动 (间隔: {interval}s)")
    
    if not is_mock:
        plc = get_plc_manager()
        db_number = parser.get_db_number() if parser else 32
        db_size = parser.get_total_size() if parser else 29
    
    while _db32_running:
        try:
            poll_count += 1
            
            # 1. 读取 DB32 传感器数据
            if is_mock:
                from backend.services.polling_data_generator import generate_mock_db32_data
                db32_data = generate_mock_db32_data()
            else:
                if not plc.is_connected():
                    plc.connect()
                
                result = plc.read_db(db_number, 0, db_size)
                if isinstance(result, (tuple, list)) and len(result) == 2:
                    db32_data, err = result
                else:
                    db32_data = None
                
                if not db32_data:
                    await asyncio.sleep(1)
                    continue
            
            process_func(db32_data)
            
            # 2. 读取料仓 PLC 数据 (DB18 + DB19 + Q区 + I区)
            # 2.1 读取 DB18 (料仓重量、本次排料重量、上限值)
            db18_data = None
            if is_mock:
                from backend.services.polling_data_generator import generate_mock_db18_data
                db18_data = generate_mock_db18_data()
            else:
                try:
                    if db18_parser:
                        db18_number = db18_parser.get_db_number()
                        db18_size = db18_parser.get_total_size()
                        result = plc.read_db(db18_number, 0, db18_size)
                        if isinstance(result, (tuple, list)) and len(result) == 2:
                            db18_data, err = result
                except Exception as db18_err:
                    logger.debug(f"读取 DB18 失败: {db18_err}")
                
            # 2.2 读取 DB19 (排料重量待读取标志)
            db19_data = None
            if is_mock:
                from backend.services.polling_data_generator import generate_mock_db19_data
                db19_data = generate_mock_db19_data()
            else:
                try:
                    if db19_parser:
                        db19_number = db19_parser.get_db_number()
                        db19_size = db19_parser.get_total_size()
                        result = plc.read_db(db19_number, 0, db19_size)
                        if isinstance(result, (tuple, list)) and len(result) == 2:
                            db19_data, err = result
                except Exception as db19_err:
                    logger.debug(f"读取 DB19 失败: {db19_err}")
            
            # 2.3 读取 Q区信号 (Q3.7 排料, Q4.0 要料)
            q_data = None
            if is_mock:
                from backend.services.polling_data_generator import generate_mock_q_data
                q_data = generate_mock_q_data()
            else:
                try:
                    q_data, q_err = plc.read_output_area(3, 2)  # 读取 Q3, Q4
                except Exception as q_err:
                    logger.debug(f"读取 Q区失败: {q_err}")
            
            # 2.4 读取 I区信号 (I4.6 供料反馈)
            i_data = None
            if is_mock:
                from backend.services.polling_data_generator import generate_mock_i_data
                i_data = generate_mock_i_data()
            else:
                try:
                    i_data, i_err = plc.read_input_area(4, 1)  # 读取 I4
                except Exception as i_err:
                    logger.debug(f"读取 I区失败: {i_err}")
                
            # 2.5 处理料仓 PLC 数据
            from backend.services.polling_service import get_batch_info
            batch_info = get_batch_info()
            current_batch = batch_info.get('batch_code', '')
            is_smelting = batch_info.get('is_smelting', False)
            
            # 修复: 无论是否冶炼，都处理料仓数据（更新实时状态）
            # 只有在冶炼状态时才写入历史数据库
            if db18_data and db19_data:
                process_hopper_plc_func(
                    db18_data=db18_data,
                    db19_data=db19_data,
                    q_data=q_data,
                    i_data=i_data,
                    batch_code=current_batch  # 无批次号时传空字符串
                )
            
            # 批量写入逻辑 (每15秒写一次: 0.5s×30=15s)
            _normal_buffer_count += 1
            if _normal_buffer_count >= _normal_batch_size:
                await _flush_normal_buffer()
                _normal_buffer_count = 0
            
            # 蝶阀开度批量写入逻辑 (每15秒写一次: 0.5s×30=15s)
            _valve_buffer_count += 1
            if _valve_buffer_count >= _valve_batch_size:
                await _flush_valve_buffer()
                _valve_buffer_count = 0
            
            # 成功后重置错误计数器
            error_count = 0
            
            await asyncio.sleep(interval)
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            error_count += 1
            
            # 10次失败后，固定等待30秒
            if error_count >= MAX_ERROR_COUNT:
                logger.error(f"DB32 轮询异常 (第{error_count}次，已达上限): {e}")
                if error_count == MAX_ERROR_COUNT:
                    logger.warning(f"DB32 连续失败 {MAX_ERROR_COUNT} 次，后续每次固定等待 {FIXED_WAIT_TIME}s")
                await asyncio.sleep(FIXED_WAIT_TIME)
            else:
                # 前10次使用指数退避
                wait_time = min(FIXED_WAIT_TIME, 2 ** min(error_count - 1, 4))
                logger.error(f"DB32 轮询异常 (第{error_count}次): {e}")
                if error_count <= 3:
                    logger.error(traceback.format_exc())
                await asyncio.sleep(wait_time)
    
    logger.info("DB32 传感器轮询已停止")


# ============================================================
# 5: DB30/DB41 状态轮询模块 (固定 5s, 仅缓存)
# ============================================================
async def _status_polling_loop(
    db30_parser,
    db41_parser,
    process_db30_func,
    process_db41_func,
    is_mock: bool = False
):
    """DB30/DB41 状态轮询 (固定 5s, 仅缓存)
    
    Args:
        db30_parser: DB30 解析器
        db41_parser: DB41 解析器
        process_db30_func: DB30 处理函数
        process_db41_func: DB41 处理函数
        is_mock: 是否 Mock 模式
    """
    poll_count = 0
    error_count = 0  # 连续错误计数器
    MAX_ERROR_COUNT = 10  # 最大错误次数，超过后固定30s
    FIXED_WAIT_TIME = 30  # 固定等待时间（秒）
    interval = settings.status_polling_interval  # 从 .env 配置读取
    
    logger.info(f"状态轮询已启动 (DB30+DB41, 间隔: {interval}s)")
    
    if not is_mock:
        plc = get_plc_manager()
        db30_number = db30_parser.get_db_number() if db30_parser else 30
        db30_size = db30_parser.get_total_size() if db30_parser else 40
        db41_number = db41_parser.get_db_number() if db41_parser else 41
        db41_size = db41_parser.get_total_size() if db41_parser else 28  # 7设备×4字节=28
    
    while _status_running:
        try:
            poll_count += 1
            
            # 1. 读取 DB30 通信状态
            if is_mock:
                from backend.services.polling_data_generator import generate_mock_db30_data
                db30_data = generate_mock_db30_data()
            else:
                if not plc.is_connected():
                    plc.connect()
                
                result = plc.read_db(db30_number, 0, db30_size)
                if isinstance(result, (tuple, list)) and len(result) == 2:
                    db30_data, err = result
                else:
                    db30_data = None
            
            if db30_data:
                process_db30_func(db30_data)
            
            # 2. 读取 DB41 数据状态
            if is_mock:
                from backend.services.polling_data_generator import generate_mock_db41_data
                db41_data = generate_mock_db41_data()
            else:
                result = plc.read_db(db41_number, 0, db41_size)
                if isinstance(result, (tuple, list)) and len(result) == 2:
                    db41_data, err = result
                else:
                    db41_data = None
            
            if db41_data:
                process_db41_func(db41_data)
            
            # 成功后重置错误计数器
            error_count = 0
            
            await asyncio.sleep(interval)
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            error_count += 1
            
            # 10次失败后，固定等待30秒
            if error_count >= MAX_ERROR_COUNT:
                logger.error(f"状态轮询异常 (第{error_count}次，已达上限): {e}")
                if error_count == MAX_ERROR_COUNT:
                    logger.warning(f"状态轮询连续失败 {MAX_ERROR_COUNT} 次，后续每次固定等待 {FIXED_WAIT_TIME}s")
                await asyncio.sleep(FIXED_WAIT_TIME)
            else:
                # 前10次使用指数退避
                wait_time = min(FIXED_WAIT_TIME, 2 ** min(error_count - 1, 4))
                logger.error(f"状态轮询异常 (第{error_count}次): {e}")
                if error_count <= 3:
                    logger.error(traceback.format_exc())
                await asyncio.sleep(wait_time)
    
    logger.info("状态轮询已停止")


# ============================================================
# 6: DB36 持久化配置轮询模块 (固定 5s)
# ============================================================
async def _db36_config_polling_loop(
    parser,
    process_func,
    is_mock: bool = False
):
    """DB36 持久化配置轮询 (固定 5s)
    
    读取紧急停机参数: 弧流上限、消抖延时、使能标志
    
    Args:
        parser: DB36 解析器
        process_func: 数据处理函数 (process_db36_data)
        is_mock: 是否 Mock 模式
    """
    poll_count = 0
    error_count = 0
    MAX_ERROR_COUNT = 10
    FIXED_WAIT_TIME = 30
    interval = 5  # 配置数据变化不频繁, 5s 轮询即可
    
    db_number = parser.get_db_number()
    db_size = parser.get_total_size()
    
    logger.info(f"DB36 配置轮询已启动 (DB{db_number}, size={db_size}, 间隔: {interval}s)")
    
    if not is_mock:
        plc = get_plc_manager()
    
    while _db36_running:
        try:
            poll_count += 1
            
            if is_mock:
                from backend.services.polling_data_generator import generate_mock_db36_data
                raw_data = generate_mock_db36_data()
            else:
                if not plc.is_connected():
                    plc.connect()
                
                result = plc.read_db(db_number, 0, db_size)
                if isinstance(result, (tuple, list)) and len(result) == 2:
                    raw_data, err = result
                else:
                    raw_data = None
            
            if raw_data:
                process_func(raw_data)
            
            # 成功后重置错误计数器
            error_count = 0
            
            await asyncio.sleep(interval)
            
        except asyncio.CancelledError:
            break
        except Exception as e:
            error_count += 1
            
            if error_count >= MAX_ERROR_COUNT:
                logger.error(f"DB36 配置轮询异常 (第{error_count}次, 已达上限): {e}")
                if error_count == MAX_ERROR_COUNT:
                    logger.warning(f"DB36 配置轮询连续失败 {MAX_ERROR_COUNT} 次, 后续固定等待 {FIXED_WAIT_TIME}s")
                await asyncio.sleep(FIXED_WAIT_TIME)
            else:
                wait_time = min(FIXED_WAIT_TIME, 2 ** min(error_count - 1, 4))
                logger.error(f"DB36 配置轮询异常 (第{error_count}次): {e}")
                if error_count <= 3:
                    logger.error(traceback.format_exc())
                await asyncio.sleep(wait_time)
    
    logger.info("DB36 配置轮询已停止")


# ============================================================
# 启动/停止函数 (供 main.py 调用)
# ============================================================
async def start_all_polling_loops():
    """启动所有轮询任务 (自动启动)"""
    global _db1_task, _db32_task, _status_task, _db36_task
    global _db1_running, _db32_running, _status_running, _db36_running
    global _db1_interval
    
    from backend.services.polling_data_processor import (
        init_parsers,
        get_parsers,
        process_arc_data,
        process_modbus_data,
        process_status_data,
        process_db41_data,
        process_hopper_plc_data,
        process_db36_data,
    )
    
    # 初始化解析器
    init_parsers()
    
    # 获取解析器
    db1_parser, modbus_parser, status_parser, db41_parser, db18_parser, db19_parser, db36_parser = get_parsers()
    
    # 从配置管理器获取轮询间隔
    from backend.config.polling_config import get_polling_config
    polling_config = get_polling_config()
    _db1_interval = polling_config.get_polling_interval()
    
    # 注册配置变化回调
    def on_polling_speed_changed(speed):
        global _db1_interval
        _db1_interval = polling_config.get_polling_interval()
        logger.info(f"DB1 轮询速度已更新: {speed} (间隔: {_db1_interval}s)")
    
    polling_config.register_callback(on_polling_speed_changed)
    
    # 启动标志
    _db1_running = True
    _db32_running = True
    _status_running = True
    _db36_running = True
    
    is_mock = settings.mock_mode
    mode_text = "Mock" if is_mock else "PLC"
    
    logger.info("=" * 60)
    logger.info(f"启动三速轮询架构 ({mode_text} 模式)")
    logger.info("   DB1 弧流弧压: 0.5s (固定高速)")
    logger.info("   DB32 传感器: 0.5s (高频, 含冷却水流量计算)")
    logger.info("   料仓 PLC: 0.5s (DB18+DB19+Q区+I区)")
    logger.info("   DB30/DB41 状态: 5s (固定)")
    logger.info("   DB36 持久化配置: 5s (固定)")
    logger.info("=" * 60)
    
    # 创建任务
    _db1_task = asyncio.create_task(_db1_arc_polling_loop(
        db1_parser,
        process_arc_data,
        is_mock=is_mock
    ))
    
    _db32_task = asyncio.create_task(_db32_sensor_polling_loop(
        modbus_parser,
        process_modbus_data,
        db18_parser,
        db19_parser,
        process_hopper_plc_data,
        is_mock=is_mock
    ))
    
    _status_task = asyncio.create_task(_status_polling_loop(
        status_parser,
        db41_parser,
        process_status_data,
        process_db41_data,
        is_mock=is_mock
    ))
    
    _db36_task = asyncio.create_task(_db36_config_polling_loop(
        db36_parser,
        process_db36_data,
        is_mock=is_mock
    ))


async def stop_all_polling_loops():
    """停止所有轮询任务"""
    global _db1_task, _db32_task, _status_task, _db36_task
    global _db1_running, _db32_running, _status_running, _db36_running
    
    _db1_running = False
    _db32_running = False
    _status_running = False
    _db36_running = False
    
    tasks = [_db1_task, _db32_task, _status_task, _db36_task]
    for task in tasks:
        if task:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
    
    logger.info("所有轮询任务已停止")


def switch_db1_speed(high_speed: bool):
    """切换 DB1 轮询速度
    
    Args:
        high_speed: True=0.5s (冶炼中), False=5s (空闲)
    """
    global _db1_interval
    
    if high_speed:
        _db1_interval = settings.db1_polling_interval
        logger.info(f"DB1 轮询切换到高速模式 ({_db1_interval}s)")
    else:
        _db1_interval = settings.db1_idle_polling_interval
        logger.info(f"DB1 轮询切换到低速模式 ({_db1_interval}s)")


def get_polling_loops_status():
    """获取轮询任务状态"""
    return {
        "db1_running": _db1_running,
        "db1_interval": _db1_interval,
        "db32_running": _db32_running,
        "status_running": _status_running,
        "db36_running": _db36_running,
    }
