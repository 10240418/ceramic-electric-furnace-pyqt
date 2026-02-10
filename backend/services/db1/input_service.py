"""
弧流上限值和消抖时间写入服务
"""
from typing import Dict, Any
from loguru import logger


def set_arc_limit(arc_limit: int) -> Dict[str, Any]:
    """
    设置高压紧急停电弧流上限值（写入 PLC DB1 偏移量 182-183）
    
    Args:
        arc_limit: 弧流上限值 (A)
        
    Returns:
        Dict: {'success': bool, 'message': str}
    """
    try:
        # 1. 参数校验
        if arc_limit <= 0:
            return {
                'success': False,
                'message': f'弧流上限值必须大于0，当前值: {arc_limit} A'
            }
        
        if arc_limit > 20000:
            return {
                'success': False,
                'message': f'弧流上限值不能超过20000A，当前值: {arc_limit} A'
            }
        
        # 2. 调用桥接层写入 PLC
        from backend.bridge.plc_writer import write_arc_limit_to_plc
        
        result = write_arc_limit_to_plc(arc_limit)
        
        if result['success']:
            logger.info(f"弧流上限值已设置: {arc_limit} A")
            return {
                'success': True,
                'message': f'弧流上限值已设置为 {arc_limit} A'
            }
        else:
            logger.error(f"设置弧流上限值失败: {result['message']}")
            return result
        
    except Exception as e:
        logger.error(f"设置弧流上限值异常: {e}", exc_info=True)
        return {
            'success': False,
            'message': f'设置失败: {str(e)}'
        }


def set_emergency_delay(delay_ms: int) -> Dict[str, Any]:
    """
    设置高压紧急停电消抖时间（写入 PLC DB1 偏移量 186-189）
    
    Args:
        delay_ms: 消抖时间 (毫秒)
        
    Returns:
        Dict: {'success': bool, 'message': str}
    """
    try:
        # 1. 参数校验
        if delay_ms < 0:
            return {
                'success': False,
                'message': f'消抖时间不能为负数，当前值: {delay_ms} ms'
            }
        
        if delay_ms > 10000:
            return {
                'success': False,
                'message': f'消抖时间不能超过10000ms (10秒)，当前值: {delay_ms} ms'
            }
        
        # 2. 调用桥接层写入 PLC
        from backend.bridge.plc_writer import write_emergency_delay_to_plc
        
        result = write_emergency_delay_to_plc(delay_ms)
        
        if result['success']:
            logger.info(f"消抖时间已设置: {delay_ms} ms ({delay_ms/1000:.3f} s)")
            return {
                'success': True,
                'message': f'消抖时间已设置为 {delay_ms} ms ({delay_ms/1000:.3f} s)'
            }
        else:
            logger.error(f"设置消抖时间失败: {result['message']}")
            return result
        
    except Exception as e:
        logger.error(f"设置消抖时间异常: {e}", exc_info=True)
        return {
            'success': False,
            'message': f'设置失败: {str(e)}'
        }


def set_arc_limit_and_delay(arc_limit: int, delay_ms: int) -> Dict[str, Any]:
    """
    同时设置弧流上限值和消抖时间（批量写入）
    
    Args:
        arc_limit: 弧流上限值 (A)
        delay_ms: 消抖时间 (毫秒)
        
    Returns:
        Dict: {'success': bool, 'message': str, 'details': dict}
    """
    try:
        # 1. 参数校验
        if arc_limit <= 0 or arc_limit > 20000:
            return {
                'success': False,
                'message': f'弧流上限值必须在 1-20000A 之间，当前值: {arc_limit} A'
            }
        
        if delay_ms < 0 or delay_ms > 10000:
            return {
                'success': False,
                'message': f'消抖时间必须在 0-10000ms 之间，当前值: {delay_ms} ms'
            }
        
        # 2. 调用桥接层批量写入 PLC
        from backend.bridge.plc_writer import write_arc_limit_and_delay_to_plc
        
        result = write_arc_limit_and_delay_to_plc(arc_limit, delay_ms)
        
        if result['success']:
            logger.info(f"弧流上限和消抖时间已设置: {arc_limit} A, {delay_ms} ms")
            return {
                'success': True,
                'message': f'设置成功: 弧流上限 {arc_limit} A, 消抖时间 {delay_ms} ms',
                'details': {
                    'arc_limit': arc_limit,
                    'delay_ms': delay_ms,
                    'delay_s': delay_ms / 1000.0
                }
            }
        else:
            logger.error(f"批量设置失败: {result['message']}")
            return result
        
    except Exception as e:
        logger.error(f"批量设置异常: {e}", exc_info=True)
        return {
            'success': False,
            'message': f'设置失败: {str(e)}'
        }


