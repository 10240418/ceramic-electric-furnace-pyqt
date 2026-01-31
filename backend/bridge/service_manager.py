"""
后端服务管理器
"""
from threading import Thread, Event
from typing import Optional
import asyncio
from loguru import logger

from backend.bridge.data_cache import get_data_cache
from backend.bridge.data_bridge import get_data_bridge


class ServiceManager:
    
    # 1. 初始化服务管理器
    def __init__(self, use_mock: bool = False):
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
        
        # 停止 asyncio 事件循环
        if self.loop and self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)
        
        # 设置停止事件
        self.stop_event.set()
        
        # 等待所有线程结束
        for thread in self.threads:
            thread.join(timeout=2)
            if thread.is_alive():
                logger.warning(f"线程 {thread.name} 未能在 2 秒内停止")
        
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

