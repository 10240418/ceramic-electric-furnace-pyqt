"""
弧流上限值写入服务
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

