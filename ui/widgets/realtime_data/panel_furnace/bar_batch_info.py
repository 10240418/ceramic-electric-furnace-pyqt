"""
炉次信息栏组件 - 显示炉次信息和控制按钮
"""
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import pyqtSignal, QTimer, Qt
from ui.styles.themes import ThemeManager
from ui.widgets.common.button_progress import ProgressButton
from loguru import logger


class BarBatchInfo(QFrame):
    """炉次信息栏组件"""
    
    # 信号定义
    start_smelting_clicked = pyqtSignal()  # 开始记录信号
    abandon_batch_clicked = pyqtSignal()   # 放弃炉次信号
    terminate_smelting_clicked = pyqtSignal()  # 终止记录信号（长按3秒）
    
    # 1. 初始化组件
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        self.setObjectName("batchInfoBar")
        
        self.batch_no = ""
        self.start_time = ""
        self.run_duration = ""
        self.is_smelting = False  # 是否正在记录
        
        # 确保背景完全不透明
        self.setAutoFillBackground(True)
        
        self.init_ui()
        self.apply_styles()
        
        # 提升到最上层
        self.raise_()
        
        # 监听主题变化
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
    
    # 2. 初始化 UI
    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 8)  # 顶部 12px，左右 12px，底部 8px
        layout.setSpacing(16)
        
        # 炉次信息文本
        self.info_label = QLabel("未开始冶炼")
        self.info_label.setObjectName("batchInfoLabel")
        layout.addWidget(self.info_label, stretch=1)
        
        # 放弃炉次按钮
        self.btn_abandon = QPushButton("放弃炉次")
        self.btn_abandon.setObjectName("btnAbandon")
        self.btn_abandon.setFixedSize(100, 36)
        self.btn_abandon.clicked.connect(self.abandon_batch_clicked.emit)
        layout.addWidget(self.btn_abandon)
        
        # 开始记录按钮
        self.btn_start = QPushButton("开始记录")
        self.btn_start.setObjectName("btnStart")
        self.btn_start.setFixedSize(100, 36)
        self.btn_start.clicked.connect(self.start_smelting_clicked.emit)
        layout.addWidget(self.btn_start)
        
        # 终止记录按钮（需要长按3秒，带进度条）
        self.btn_terminate = ProgressButton("终止记录", parent=self)
        self.btn_terminate.setObjectName("btnTerminate")
        self.btn_terminate.setFixedSize(100, 36)
        self.btn_terminate.setVisible(False)  # 初始隐藏
        self.btn_terminate.long_press_completed.connect(self.on_long_press_complete)
        layout.addWidget(self.btn_terminate)
    
    # 3. 设置冶炼状态
    def set_smelting_state(self, is_smelting: bool, batch_no: str = "", start_time: str = "", run_duration: str = ""):
        """
        设置冶炼状态
        
        Args:
            is_smelting: 是否正在冶炼
            batch_no: 炉次编号
            start_time: 开始时间
            run_duration: 运行时长
        """
        self.is_smelting = is_smelting
        self.batch_no = batch_no
        self.start_time = start_time
        self.run_duration = run_duration
        
        # 根据状态切换按钮显示
        if is_smelting:
            # 冶炼中：显示放弃炉次和终止冶炼按钮
            self.btn_start.setVisible(False)
            self.btn_abandon.setVisible(True)
            self.btn_terminate.setVisible(True)
        else:
            # 未冶炼：显示开始冶炼按钮
            self.btn_start.setVisible(True)
            self.btn_abandon.setVisible(False)
            self.btn_terminate.setVisible(False)
        
        self.update_display()
    
    # 4. 更新显示
    def update_display(self):
        if self.is_smelting and self.batch_no:
            text = f"炉次编号: {self.batch_no}  |  " \
                   f"开始时间: {self.start_time}  |  " \
                   f"运行时长: {self.run_duration}"
        else:
            text = "未开始记录"
        self.info_label.setText(text)
    
    # 5. 长按完成
    def on_long_press_complete(self):
        """长按3秒完成，触发终止记录"""
        logger.info("长按3秒完成，触发终止记录")
        
        # 先强制刷新所有缓存，再触发终止记录信号
        self.force_flush_caches_async()
    
    # 6. 异步强制刷新所有缓存
    def force_flush_caches_async(self):
        """异步强制刷新所有缓存，立即写入数据库（不阻塞 UI）"""
        try:
            from backend.services.batch_service import get_batch_service
            from backend.bridge.service_manager import get_service_manager
            import asyncio
            
            batch_service = get_batch_service()
            service_manager = get_service_manager()
            
            # 检查后端事件循环是否存在
            if not service_manager or not service_manager.loop:
                logger.error("后端事件循环不存在，无法刷新缓存")
                self.terminate_smelting_clicked.emit()
                return
            
            # 在后端的 asyncio 事件循环中执行刷新操作
            future = asyncio.run_coroutine_threadsafe(
                batch_service.force_flush_all_caches(),
                service_manager.loop
            )
            
            # 添加回调，刷新完成后触发终止记录信号
            future.add_done_callback(self.on_flush_finished)
            
            logger.info("缓存刷新任务已提交到后端事件循环...")
        
        except Exception as e:
            logger.error(f"提交缓存刷新任务失败: {e}", exc_info=True)
            # 即使刷新失败，也要触发终止记录信号
            self.terminate_smelting_clicked.emit()
    
    # 7. 缓存刷新完成回调
    def on_flush_finished(self, future):
        """缓存刷新完成后的回调"""
        try:
            result = future.result()
            
            if result["success"]:
                logger.info(f"缓存刷新完成: {result['message']}")
            else:
                logger.warning(f"缓存刷新失败: {result['message']}")
        
        except Exception as e:
            logger.error(f"获取缓存刷新结果失败: {e}", exc_info=True)
        
        finally:
            # 触发终止记录信号
            self.terminate_smelting_clicked.emit()
    
    # 7. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        self.setStyleSheet(f"""
            QFrame#batchInfoBar {{
                background: {colors.BG_LIGHT};
                border: 1px solid {colors.BORDER_GLOW};
                border-radius: 4px;
            }}
            
            QLabel#batchInfoLabel {{
                color: {colors.TEXT_PRIMARY};
                font-size: 14px;
                font-weight: bold;
            }}
            
            QPushButton#btnStart {{
                background: {colors.GLOW_PRIMARY}33;
                color: {colors.GLOW_PRIMARY};
                border: 1px solid {colors.GLOW_PRIMARY};
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
            }}
            
            QPushButton#btnStart:hover {{
                background: {colors.GLOW_PRIMARY}4D;
                border: 1px solid {colors.GLOW_PRIMARY};
            }}
            
            QPushButton#btnStart:pressed {{
                background: {colors.GLOW_PRIMARY}66;
            }}
            
            QPushButton#btnAbandon, QPushButton#btnTerminate {{
                background: {colors.BG_MEDIUM};
                color: {colors.TEXT_PRIMARY};
                border: 1px solid {colors.BORDER_DARK};
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
            }}
            
            QPushButton#btnAbandon:hover, QPushButton#btnTerminate:hover {{
                border: 1px solid {colors.BORDER_GLOW};
                background: {colors.BG_LIGHT};
            }}
            
            QPushButton#btnAbandon:pressed, QPushButton#btnTerminate:pressed {{
                background: {colors.BG_DARK};
            }}
            
            QPushButton#btnAbandon:disabled {{
                background: {colors.BG_DARK};
                color: {colors.TEXT_DISABLED};
                border: 1px solid {colors.BORDER_DARK};
            }}
        """)
    
    # 8. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()

