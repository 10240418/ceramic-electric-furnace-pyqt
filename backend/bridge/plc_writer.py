"""
PLC 写入操作桥接层
"""
import struct
from typing import Dict, Any
from loguru import logger
from backend.plc.plc_manager import get_plc_manager
from backend.config import get_settings

settings = get_settings()


def write_hopper_upper_limit_to_plc(upper_limit: float) -> Dict[str, Any]:
    """
    将料仓上限值写入 PLC DB18
    
    Args:
        upper_limit: 料仓上限值 (kg)
        
    Returns:
        Dict: {'success': bool, 'message': str}
    """
    try:
        # 1. Mock 模式检查
        if settings.mock_mode:
            logger.info(f"[Mock模式] 模拟写入料仓上限值: {upper_limit} kg")
            return {
                'success': True,
                'message': f'[Mock模式] 料仓上限值已设置为 {int(upper_limit)} kg'
            }
        
        # 2. 获取 PLC 管理器
        plc = get_plc_manager()
        
        # 3. 检查连接
        if not plc.is_connected():
            logger.warning("PLC 未连接，尝试重新连接...")
            plc.connect()
            
            if not plc.is_connected():
                return {
                    'success': False,
                    'message': 'PLC 连接失败，无法写入数据'
                }
        
        # 4. 转换数据为 DInt (有符号32位整数，大端序)
        upper_limit_int = int(upper_limit)
        data_bytes = struct.pack('>i', upper_limit_int)  # 大端序
        
        # 5. 写入 DB18 offset 40
        db_number = 18
        offset = 40
        size = 4  # DInt 占 4 字节
        
        logger.info(f"准备写入 PLC DB{db_number}.DBD{offset}: {upper_limit_int} kg")
        
        # 6. 执行写入
        result = plc.write_db(db_number, offset, data_bytes)
        
        if result:
            logger.info(f"成功写入料仓上限值: {upper_limit_int} kg")
            return {
                'success': True,
                'message': f'料仓上限值已设置为 {upper_limit_int} kg'
            }
        else:
            logger.error(f"写入 PLC 失败")
            return {
                'success': False,
                'message': '写入 PLC 失败，请检查 PLC 连接'
            }
        
    except Exception as e:
        logger.error(f"写入料仓上限值异常: {e}", exc_info=True)
        return {
            'success': False,
            'message': f'写入失败: {str(e)}'
        }


def write_arc_limit_to_plc(arc_limit: int) -> Dict[str, Any]:
    """
    将弧流上限值写入 PLC DB1 偏移量 182-183
    
    Args:
        arc_limit: 弧流上限值 (A)
        
    Returns:
        Dict: {'success': bool, 'message': str}
    """
    try:
        # 1. Mock 模式检查
        if settings.mock_mode:
            logger.info(f"[Mock模式] 模拟写入弧流上限值: {arc_limit} A")
            return {
                'success': True,
                'message': f'[Mock模式] 弧流上限值已设置为 {arc_limit} A'
            }
        
        # 2. 获取 PLC 管理器
        plc = get_plc_manager()
        
        # 3. 检查连接
        if not plc.is_connected():
            logger.warning("PLC 未连接，尝试重新连接...")
            plc.connect()
            
            if not plc.is_connected():
                return {
                    'success': False,
                    'message': 'PLC 连接失败，无法写入数据'
                }
        
        # 4. 转换数据为 Int (有符号16位整数，大端序)
        data_bytes = struct.pack('>h', arc_limit)  # 大端序
        
        # 5. 写入 DB1 offset 182
        db_number = 1
        offset = 182
        size = 2  # Int 占 2 字节
        
        logger.info(f"准备写入 PLC DB{db_number}.DBW{offset}: {arc_limit} A")
        
        # 6. 执行写入
        result = plc.write_db(db_number, offset, data_bytes)
        
        if result:
            logger.info(f"成功写入弧流上限值: {arc_limit} A")
            return {
                'success': True,
                'message': f'弧流上限值已设置为 {arc_limit} A'
            }
        else:
            logger.error(f"写入 PLC 失败")
            return {
                'success': False,
                'message': '写入 PLC 失败，请检查 PLC 连接'
            }
        
    except Exception as e:
        logger.error(f"写入弧流上限值异常: {e}", exc_info=True)
        return {
            'success': False,
            'message': f'写入失败: {str(e)}'
        }


def write_emergency_delay_to_plc(delay_ms: int) -> Dict[str, Any]:
    """
    将高压紧急停电消抖时间写入 PLC DB1 偏移量 186-189
    
    Args:
        delay_ms: 消抖时间 (毫秒)
        
    Returns:
        Dict: {'success': bool, 'message': str}
    """
    try:
        # 1. Mock 模式检查
        if settings.mock_mode:
            logger.info(f"[Mock模式] 模拟写入消抖时间: {delay_ms} ms")
            return {
                'success': True,
                'message': f'[Mock模式] 消抖时间已设置为 {delay_ms} ms'
            }
        
        # 2. 获取 PLC 管理器
        plc = get_plc_manager()
        
        # 3. 检查连接
        if not plc.is_connected():
            logger.warning("PLC 未连接，尝试重新连接...")
            plc.connect()
            
            if not plc.is_connected():
                return {
                    'success': False,
                    'message': 'PLC 连接失败，无法写入数据'
                }
        
        # 4. 转换数据为 TIME (有符号32位整数，大端序)
        # TIME 类型存储单位为毫秒
        data_bytes = struct.pack('>i', delay_ms)  # 大端序
        
        # 5. 写入 DB1 offset 186
        db_number = 1
        offset = 186
        size = 4  # TIME 占 4 字节
        
        logger.info(f"准备写入 PLC DB{db_number}.DBD{offset}: {delay_ms} ms ({delay_ms/1000:.3f} s)")
        
        # 6. 执行写入
        result = plc.write_db(db_number, offset, data_bytes)
        
        if result:
            logger.info(f"成功写入消抖时间: {delay_ms} ms ({delay_ms/1000:.3f} s)")
            return {
                'success': True,
                'message': f'消抖时间已设置为 {delay_ms} ms ({delay_ms/1000:.3f} s)'
            }
        else:
            logger.error(f"写入 PLC 失败")
            return {
                'success': False,
                'message': '写入 PLC 失败，请检查 PLC 连接'
            }
        
    except Exception as e:
        logger.error(f"写入消抖时间异常: {e}", exc_info=True)
        return {
            'success': False,
            'message': f'写入失败: {str(e)}'
        }


def write_arc_limit_and_delay_to_plc(arc_limit: int, delay_ms: int) -> Dict[str, Any]:
    """
    同时写入弧流上限值和消抖时间到 PLC DB1（批量写入）
    
    Args:
        arc_limit: 弧流上限值 (A)
        delay_ms: 消抖时间 (毫秒)
        
    Returns:
        Dict: {'success': bool, 'message': str}
    """
    try:
        # 1. Mock 模式检查
        if settings.mock_mode:
            logger.info(f"[Mock模式] 模拟批量写入: 弧流上限 {arc_limit} A, 消抖时间 {delay_ms} ms")
            return {
                'success': True,
                'message': f'[Mock模式] 已设置: 弧流上限 {arc_limit} A, 消抖时间 {delay_ms} ms'
            }
        
        # 2. 获取 PLC 管理器
        plc = get_plc_manager()
        
        # 3. 检查连接
        if not plc.is_connected():
            logger.warning("PLC 未连接，尝试重新连接...")
            plc.connect()
            
            if not plc.is_connected():
                return {
                    'success': False,
                    'message': 'PLC 连接失败，无法写入数据'
                }
        
        # 4. 构建数据包（8字节）
        # offset 182-183: arc_limit (INT, 2字节)
        # offset 184-185: 保留字节（不写入，跳过）
        # offset 186-189: delay_ms (TIME, 4字节)
        
        # 方案：分两次写入（因为中间有保留字节）
        
        # 4.1 写入弧流上限值 (offset 182)
        arc_limit_bytes = struct.pack('>h', arc_limit)
        
        # 4.2 写入消抖时间 (offset 186)
        delay_bytes = struct.pack('>i', delay_ms)
        
        db_number = 1
        
        logger.info(f"准备批量写入 PLC DB{db_number}: 弧流上限 {arc_limit} A, 消抖时间 {delay_ms} ms")
        
        # 5. 执行写入（分两次）
        result1 = plc.write_db(db_number, 182, arc_limit_bytes)
        result2 = plc.write_db(db_number, 186, delay_bytes)
        
        if result1 and result2:
            logger.info(f"成功批量写入: 弧流上限 {arc_limit} A, 消抖时间 {delay_ms} ms")
            return {
                'success': True,
                'message': f'设置成功: 弧流上限 {arc_limit} A, 消抖时间 {delay_ms} ms'
            }
        else:
            logger.error(f"批量写入 PLC 失败 (result1={result1}, result2={result2})")
            return {
                'success': False,
                'message': '写入 PLC 失败，请检查 PLC 连接'
            }
        
    except Exception as e:
        logger.error(f"批量写入异常: {e}", exc_info=True)
        return {
            'success': False,
            'message': f'写入失败: {str(e)}'
        }