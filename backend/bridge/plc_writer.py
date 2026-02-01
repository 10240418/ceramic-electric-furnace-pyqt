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
