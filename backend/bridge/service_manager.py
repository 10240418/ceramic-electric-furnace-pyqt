"""
后端服务管理器
"""
from threading import Thread, Event
from typing import Optional
import asyncio
from loguru import logger

from backend.bridge.data_cache import get_data_cache
from backend.bridge.data_bridge import get_data_bridge


# 全局服务管理器实例
_service_manager_instance: Optional['ServiceManager'] = None


class ServiceManager:
    
    # 1. 初始化服务管理器
    def __init__(self, use_mock: bool = False):
        global _service_manager_instance
        _service_manager_instance = self
        
        logger.info(f"ServiceManager 开始初始化 (Mock模式: {use_mock})")
        
        self.use_mock = use_mock
        self.threads = []
        self.stop_event = Event()
        self.loop = None
        
        logger.info("初始化数据缓存...")
        # 初始化缓存
        self.cache = get_data_cache()
        logger.info("数据缓存初始化完成")
        
        logger.info("初始化数据桥接器...")
        # 初始化数据桥接器
        self.bridge = get_data_bridge()
        logger.info("数据桥接器初始化完成")
        
        logger.info(f"服务管理器初始化完成 (Mock模式: {use_mock})")
    
    # 2. 启动所有后端服务
    def start_all(self):
        try:
            # 在独立线程中运行 asyncio 事件循环
            asyncio_thread = Thread(
                target=self._run_asyncio_loop,
                daemon=True,
                name="AsyncioEventLoop"
            )
            asyncio_thread.start()
            self.threads.append(asyncio_thread)
            
            logger.info("所有后端服务已启动")
        except Exception as e:
            logger.error(f"启动后端服务失败: {e}", exc_info=True)
            self.bridge.error_occurred.emit(f"启动后端服务失败: {e}")
    
    # 3. 在独立线程中运行 asyncio 事件循环
    def _run_asyncio_loop(self):
        try:
            # 创建新的事件循环
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            
            if self.use_mock:
                # Mock 模式：启动 Mock 轮询服务
                self.loop.run_until_complete(self._start_mock_services())
            else:
                # 真实模式：启动真实轮询服务
                self.loop.run_until_complete(self._start_real_services())
            
            # 保持事件循环运行
            self.loop.run_forever()
            
        except Exception as e:
            logger.error(f"Asyncio 事件循环异常: {e}", exc_info=True)
            self.bridge.error_occurred.emit(f"后端服务异常: {e}")
        finally:
            if self.loop:
                self.loop.close()
    
    # 4. 启动真实服务（asyncio）
    async def _start_real_services(self):
        from backend.services.polling_loops_v2 import start_all_polling_loops
        
        logger.info("启动真实 PLC 轮询服务...")
        
        # 启动所有轮询循环（DB1, DB32, Status）
        await start_all_polling_loops()
        
        logger.info("真实 PLC 轮询服务已启动")
    
    # 5. 启动 Mock 服务（asyncio）
    async def _start_mock_services(self):
        from backend.services.polling_loops_v2 import start_all_polling_loops
        
        logger.info("使用 Mock 数据模式")
        
        # 启动所有轮询循环（Mock 模式）
        await start_all_polling_loops()
        
        logger.info("Mock 数据轮询服务已启动")
    
    # 6. 停止所有服务
    def stop_all(self):
        logger.info("正在停止所有后端服务...")
        
        # 1. 停止 asyncio 事件循环中的所有任务
        if self.loop and self.loop.is_running():
            logger.info("正在停止 asyncio 事件循环...")
            
            # 停止所有轮询任务
            try:
                from backend.services.polling_loops_v2 import stop_all_polling_loops
                import asyncio
                
                # 在事件循环中执行停止操作
                future = asyncio.run_coroutine_threadsafe(
                    stop_all_polling_loops(),
                    self.loop
                )
                # 等待停止完成（最多2秒）
                future.result(timeout=2.0)
                logger.info("轮询任务已停止")
            except Exception as e:
                logger.warning(f"停止轮询任务失败: {e}")
            
            # 停止事件循环
            self.loop.call_soon_threadsafe(self.loop.stop)
            logger.info("事件循环已停止")
        
        # 2. 关闭 PLC 连接
        try:
            from backend.plc.plc_manager import get_plc_manager
            plc = get_plc_manager()
            plc.disconnect()
            logger.info("PLC 连接已关闭")
        except Exception as e:
            logger.warning(f"关闭 PLC 连接失败: {e}")
        
        # 3. 关闭 InfluxDB 客户端
        try:
            from backend.core.influxdb import close_influx_client
            close_influx_client()
            logger.info("InfluxDB 客户端已关闭")
        except Exception as e:
            logger.warning(f"关闭 InfluxDB 客户端失败: {e}")
        
        # 4. 设置停止事件
        self.stop_event.set()
        
        # 5. 等待所有线程结束
        for thread in self.threads:
            thread.join(timeout=3)
            if thread.is_alive():
                logger.warning(f"线程 {thread.name} 未能在 3 秒内停止")
        
        # 6. 关闭事件循环
        if self.loop:
            try:
                # 等待事件循环完全停止
                import time
                timeout = 3
                start_time = time.time()
                while self.loop.is_running() and (time.time() - start_time) < timeout:
                    time.sleep(0.1)
                
                # 关闭事件循环
                if not self.loop.is_closed():
                    self.loop.close()
                    logger.info("事件循环已关闭")
            except Exception as e:
                logger.warning(f"关闭事件循环失败: {e}")
        
        logger.info("所有后端服务已停止")
    
    # 7. 获取服务状态
    def get_status(self) -> dict:
        from backend.services.polling_loops_v2 import get_polling_loops_status
        from backend.services.batch_service import get_batch_service
        
        polling_status = get_polling_loops_status()
        batch_service = get_batch_service()
        batch_status = batch_service.get_status()
        
        # 更新批次状态到 DataCache
        try:
            self.cache.set_batch_status({
                'is_smelting': batch_status['is_smelting'],
                'batch_code': batch_status['batch_code'],
                'start_time': batch_status['start_time'],
                'elapsed_time': batch_status['elapsed_seconds']
            })
            
            # 发送批次状态信号到前端
            self.bridge.emit_batch_status({
                'is_smelting': batch_status['is_smelting'],
                'batch_code': batch_status['batch_code'],
                'start_time': batch_status['start_time'],
                'elapsed_time': batch_status['elapsed_seconds']
            })
        except Exception as e:
            logger.error(f"更新批次状态失败: {e}")
        
        return {
            "use_mock": self.use_mock,
            "threads": [
                {
                    "name": thread.name,
                    "alive": thread.is_alive()
                }
                for thread in self.threads
            ],
            "polling_loops": polling_status,
            "batch_status": batch_status
        }


# ============================================================
# 全局单例获取函数
# ============================================================

def get_service_manager() -> Optional[ServiceManager]:
    """获取服务管理器单例"""
    return _service_manager_instance

