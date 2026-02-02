"""
主窗口 - 实现全屏、最小化、页面切换等基础功能
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QStackedWidget, QPushButton, QLabel, QFrame, QMessageBox, QApplication, QDialog
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QKeySequence, QShortcut, QFont, QIcon
from loguru import logger

from ui.styles.themes import ThemeManager, Theme
from ui.styles.qss_styles import QSSStyles
from ui.widgets.bar.top_nav_bar import TopNavBar
from ui.pages.page_status import PageStatus
from ui.pages.page_elec_3 import PageElec3
from ui.pages.page_pump_hopper import PagePumpHopper
from ui.pages.page_history_curve import PageHistoryCurve
from ui.pages.page_settings import PageSettings

# 导入后端服务管理器
from backend.bridge.service_manager import ServiceManager
from backend.bridge.data_bridge import get_data_bridge
from backend.bridge.data_cache import get_data_cache


class MainWindow(QMainWindow):
    """主窗口类"""
    
    # 1. 初始化主窗口
    def __init__(self, use_mock: bool = True):
        """
        初始化主窗口
        
        Args:
            use_mock: 是否使用 Mock 数据（默认 True，开发测试用）
        """
        super().__init__()
        
        # 主题管理器
        logger.info("初始化主题管理器...")
        self.theme_manager = ThemeManager.instance()
        self.qss_styles = QSSStyles(self.theme_manager)
        logger.info("主题管理器初始化完成")
        
        # 后端服务管理器
        logger.info("初始化后端服务管理器...")
        self.service_manager = ServiceManager(use_mock=use_mock)
        logger.info("后端服务管理器初始化完成")
        
        # 数据桥接器（用于接收后端数据）
        logger.info("初始化数据桥接器...")
        self.data_bridge = get_data_bridge()
        logger.info("数据桥接器初始化完成")
        
        # 数据缓存（用于读取后端数据）
        logger.info("初始化数据缓存...")
        self.data_cache = get_data_cache()
        logger.info("数据缓存初始化完成")
        
        # 连接后端信号
        logger.info("连接后端信号...")
        self.connect_backend_signals()
        logger.info("后端信号连接完成")
        
        # 监听主题变化
        logger.info("连接主题变化信号...")
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
        logger.info("主题变化信号连接完成")
        
        # 初始化 UI
        logger.info("初始化 UI...")
        self.init_ui()
        logger.info("UI 初始化完成")
        
        logger.info("设置快捷键...")
        self.setup_shortcuts()
        logger.info("快捷键设置完成")
        
        # 启动后端服务
        logger.info("启动后端服务...")
        self.service_manager.start_all()
        logger.info("后端服务已启动")
        
        # 【测试用】强制切换 DB1 到高速模式 (0.5s)
        logger.info("切换 DB1 轮询到高速模式 (0.5s)...")
        from backend.services.polling_loops_v2 import switch_db1_speed
        switch_db1_speed(high_speed=True)
        logger.info("DB1 轮询已切换到高速模式 (0.5s)")
        
    # 2. 连接后端信号
    def connect_backend_signals(self):
        """连接后端数据桥接器的信号"""
        # 连接错误信号
        self.data_bridge.error_occurred.connect(self.on_backend_error)
        
        # 可以在这里连接更多信号，例如：
        # self.data_bridge.arc_data_updated.connect(self.on_arc_data_updated)
        # self.data_bridge.sensor_data_updated.connect(self.on_sensor_data_updated)
        
    # 3. 处理后端错误
    def on_backend_error(self, error_msg: str):
        """处理后端错误"""
        logger.error(f"后端错误: {error_msg}")
        # 可以在这里显示错误提示给用户
        
    # 2. 初始化UI
    def init_ui(self):
        self.setWindowTitle("#3电炉 - PyQt6")
        
        # 隐藏系统标题栏，使用自定义工具栏
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        # 设置窗口大小为 19 寸 4:3 标准分辨率 (1280x1024)
        self.resize(1280, 1024)
        
        # 设置最小和最大尺寸，固定窗口大小
        self.setMinimumSize(1280, 1024)
        self.setMaximumSize(1280, 1024)
        
        # 窗口居中显示
        self.center_window()
        
        # 应用全局样式
        self.apply_theme()
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 顶部导航栏
        self.nav_bar = TopNavBar()
        self.nav_bar.nav_changed.connect(self.on_nav_changed)
        main_layout.addWidget(self.nav_bar)
        
        # 页面容器（使用 QStackedWidget 实现页面切换）
        self.page_stack = QStackedWidget()
        main_layout.addWidget(self.page_stack)
        
        # 添加页面
        self.create_pages()
        
    # 3. 创建页面
    def create_pages(self):
        # 页面 0: 3# 电炉（实际页面）
        self.page_elec_3 = PageElec3()
        self.page_stack.addWidget(self.page_elec_3)
        
        # 页面 1: 历史曲线（实际页面）
        self.page_history_curve = PageHistoryCurve()
        self.page_stack.addWidget(self.page_history_curve)
        
        # 页面 2: 状态监控（实际页面）
        self.page_status = PageStatus()
        self.page_stack.addWidget(self.page_status)
        
        # 页面 3: 泵房/料仓（实际页面）
        self.page_pump_hopper = PagePumpHopper()
        self.page_stack.addWidget(self.page_pump_hopper)
        
        # 页面 4: 系统设置（实际页面）
        self.page_settings = PageSettings()
        self.page_stack.addWidget(self.page_settings)
    
    # 4. 创建单个页面（占位页面）
    def create_page(self, title: str, subtitle: str):
        page = QWidget()
        page.setObjectName(f"page_{title}")
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # 页面标题
        title_label = QLabel(subtitle)
        title_label.setObjectName("page_title")
        title_label.setFont(QFont("Microsoft YaHei", 48, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 页面说明
        info_label = QLabel(
            f" {title}页面已创建\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "这是一个占位页面\n"
            "后续将实现具体功能\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        info_label.setObjectName("page_info")
        info_label.setFont(QFont("Microsoft YaHei", 16))
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(title_label)
        layout.addSpacing(40)
        layout.addWidget(info_label)
        
        return page
    
    # 5. 导航切换回调
    def on_nav_changed(self, index: int):
        self.switch_page(index)
        
    # 6. 设置快捷键
    def setup_shortcuts(self):
        # Esc 退出程序
        shortcut_exit = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        shortcut_exit.activated.connect(self.close)
        
        # F11 切换全屏
        shortcut_fullscreen = QShortcut(QKeySequence(Qt.Key.Key_F11), self)
        shortcut_fullscreen.activated.connect(self.toggle_fullscreen)
        
        # Alt+F4 退出程序（Windows标准）
        shortcut_alt_f4 = QShortcut(QKeySequence("Alt+F4"), self)
        shortcut_alt_f4.activated.connect(self.close)
        
    # 7. 切换全屏/窗口模式
    def toggle_fullscreen(self):
        if self.isFullScreen():
            # 退出全屏，恢复固定大小
            self.showNormal()
            self.setMinimumSize(1280, 1024)
            self.setMaximumSize(1280, 1024)
            self.center_window()
        else:
            # 进入全屏，取消尺寸限制
            self.setMinimumSize(0, 0)
            self.setMaximumSize(16777215, 16777215)  # Qt 最大值
            self.showFullScreen()
    
    # 8. 窗口居中
    def center_window(self):
        """将窗口居中显示在屏幕上"""
        screen = QApplication.primaryScreen().geometry()
        window_geometry = self.frameGeometry()
        center_point = screen.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())
    
    # 9. 主题变化回调
    def on_theme_changed(self, theme: Theme):
        # 重新应用样式
        self.apply_theme()
    
    # 10. 应用主题样式
    def apply_theme(self):
        tm = self.theme_manager
        
        # 全局样式
        self.setStyleSheet(f"""
            /* ===== 主窗口 ===== */
            QMainWindow {{
                background: {tm.bg_deep()};
            }}
            
            /* ===== 页面样式 ===== */
            QWidget[objectName^="page_"] {{
                background: {tm.bg_dark()};
            }}
            
            QLabel#page_title {{
                color: {tm.border_glow()};
            }}
            
            QLabel#page_info {{
                color: {tm.text_primary()};
                line-height: 2.0;
                background: {tm.bg_medium()};
                border: 2px solid {tm.border_glow()};
                border-radius: 12px;
                padding: 40px;
            }}
            
            /* ===== 滚动条 ===== */
            QScrollBar:vertical {{
                background: {tm.bg_medium()};
                width: 14px;
                border: none;
                border-radius: 7px;
            }}
            
            QScrollBar::handle:vertical {{
                background: {tm.border_dark()};
                min-height: 30px;
                border-radius: 7px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background: {tm.border_glow()};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
            
    # 11. 添加页面到页面栈
    def add_page(self, page: QWidget, name: str = ""):
        index = self.page_stack.addWidget(page)
        return index
        
    # 12. 切换到指定页面
    def switch_page(self, index: int):
        if 0 <= index < self.page_stack.count():
            self.page_stack.setCurrentIndex(index)
            
    # 13. 获取当前页面索引
    def get_current_page_index(self):
        return self.page_stack.currentIndex()
    
    # 14. 关闭窗口事件（二次确认 + 终止记录 + 停止后端服务 + 断开信号连接）
    def closeEvent(self, event):
        """关闭窗口时二次确认并停止后端服务"""
        logger.info("用户尝试关闭窗口...")
        
        # 1. 创建自定义大字体确认对话框
        dialog = ConfirmExitDialog(self)
        result = dialog.exec()
        
        # 2. 用户选择"否"，取消关闭
        if result == QDialog.DialogCode.Rejected:
            logger.info("用户取消关闭")
            event.ignore()
            return
        
        # 3. 用户选择"是"，开始关闭流程
        logger.info("用户确认关闭，开始关闭流程...")
        
        # 4. 检查是否正在记录，如果是则先终止记录
        try:
            from backend.services.batch_service import get_batch_service
            batch_service = get_batch_service()
            status = batch_service.get_status()
            
            if status['is_smelting']:
                logger.info(f"检测到正在记录中（批次号: {status['batch_code']}），先终止记录...")
                
                # 强制刷新所有缓存（同步方式，确保数据写入）
                logger.info("正在刷新缓存，写入数据库...")
                self._flush_caches_sync()
                logger.info("缓存刷新完成")
                
                # 停止批次记录
                result = batch_service.stop()
                if result['success']:
                    logger.info(f"批次记录已终止: {result['message']}")
                else:
                    logger.warning(f"批次记录终止失败: {result['message']}")
                
                # 切换 DB1 轮询速度回低速模式 (5s)
                from backend.services.polling_loops_v2 import switch_db1_speed
                switch_db1_speed(high_speed=False)
                logger.info("已切换 DB1 轮询到低速模式 (5s)")
            else:
                logger.info("当前未在记录中，无需终止记录")
        
        except Exception as e:
            logger.error(f"终止记录失败: {e}", exc_info=True)
        
        # 5. 断开所有信号连接（防止信号槽泄漏）
        try:
            logger.info("正在断开信号连接...")
            self.theme_manager.theme_changed.disconnect(self.on_theme_changed)
            self.data_bridge.error_occurred.disconnect(self.on_backend_error)
            logger.info("信号连接已断开")
        except Exception as e:
            logger.warning(f"断开信号连接失败: {e}")
        
        # 6. 停止后端服务
        try:
            logger.info("正在停止后端服务...")
            self.service_manager.stop_all()
            logger.info("后端服务已停止")
        except Exception as e:
            logger.error(f"停止后端服务失败: {e}")
        
        # 7. 接受关闭事件
        event.accept()
        logger.info("窗口已关闭")
        
        # 8. 完全退出应用（包括系统托盘）
        QApplication.quit()
        logger.info("应用已完全退出")
    
    # 15. 同步刷新所有缓存
    def _flush_caches_sync(self):
        """同步刷新所有缓存，立即写入数据库（阻塞方式）"""
        try:
            from backend.services.batch_service import get_batch_service
            from backend.bridge.service_manager import get_service_manager
            import asyncio
            
            batch_service = get_batch_service()
            service_manager = get_service_manager()
            
            # 检查后端事件循环是否存在
            if not service_manager or not service_manager.loop:
                logger.error("后端事件循环不存在，无法刷新缓存")
                return
            
            # 在后端的 asyncio 事件循环中执行刷新操作（同步等待）
            future = asyncio.run_coroutine_threadsafe(
                batch_service.force_flush_all_caches(),
                service_manager.loop
            )
            
            # 等待刷新完成（最多等待 5 秒）
            result = future.result(timeout=5.0)
            
            if result["success"]:
                logger.info(f"缓存刷新成功: {result['message']}")
            else:
                logger.warning(f"缓存刷新失败: {result['message']}")
        
        except Exception as e:
            logger.error(f"刷新缓存异常: {e}", exc_info=True)


class ConfirmExitDialog(QDialog):
    """自定义退出确认对话框（大字体、大窗口）"""
    
    # 1. 初始化对话框
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        self.init_ui()
        self.apply_styles()
    
    # 2. 初始化 UI
    def init_ui(self):
        self.setWindowTitle("确认退出")
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setModal(True)
        
        # 设置对话框大小（更大）
        self.setFixedSize(600, 320)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(30)
        
        # 标题
        title_label = QLabel("确认退出")
        title_label.setObjectName("dialogTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_title = QFont("Microsoft YaHei", 28)
        font_title.setBold(True)
        title_label.setFont(font_title)
        main_layout.addWidget(title_label)
        
        # 提示信息
        message_label = QLabel("确定要退出程序吗？\n\n后端服务将会完全停止。")
        message_label.setObjectName("dialogMessage")
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setWordWrap(True)
        font_message = QFont("Microsoft YaHei", 18)
        message_label.setFont(font_message)
        main_layout.addWidget(message_label)
        
        main_layout.addStretch()
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        
        # 取消按钮
        self.btn_cancel = QPushButton("取消")
        self.btn_cancel.setObjectName("btnCancel")
        self.btn_cancel.setFixedSize(200, 60)
        font_button = QFont("Microsoft YaHei", 18)
        font_button.setBold(True)
        self.btn_cancel.setFont(font_button)
        self.btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(self.btn_cancel)
        
        # 确认按钮
        self.btn_confirm = QPushButton("确认退出")
        self.btn_confirm.setObjectName("btnConfirm")
        self.btn_confirm.setFixedSize(200, 60)
        self.btn_confirm.setFont(font_button)
        self.btn_confirm.clicked.connect(self.accept)
        button_layout.addWidget(self.btn_confirm)
        
        main_layout.addLayout(button_layout)
    
    # 3. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        self.setStyleSheet(f"""
            QDialog {{
                background: {colors.BG_MEDIUM};
                border: 2px solid {colors.BORDER_GLOW};
                border-radius: 12px;
            }}
            
            QLabel#dialogTitle {{
                color: {colors.GLOW_PRIMARY};
                background: transparent;
                border: none;
            }}
            
            QLabel#dialogMessage {{
                color: {colors.TEXT_PRIMARY};
                background: transparent;
                border: none;
                line-height: 1.6;
            }}
            
            QPushButton#btnCancel {{
                background: {colors.BG_LIGHT};
                color: {colors.TEXT_PRIMARY};
                border: 2px solid {colors.BORDER_DARK};
                border-radius: 8px;
                padding: 10px;
            }}
            
            QPushButton#btnCancel:hover {{
                background: {colors.BG_MEDIUM};
                border: 2px solid {colors.BORDER_GLOW};
            }}
            
            QPushButton#btnCancel:pressed {{
                background: {colors.BG_DARK};
            }}
            
            QPushButton#btnConfirm {{
                background: {colors.GLOW_PRIMARY};
                color: {colors.TEXT_ON_PRIMARY};
                border: 2px solid {colors.GLOW_PRIMARY};
                border-radius: 8px;
                padding: 10px;
            }}
            
            QPushButton#btnConfirm:hover {{
                background: {colors.BORDER_GLOW};
                border: 2px solid {colors.BORDER_GLOW};
            }}
            
            QPushButton#btnConfirm:pressed {{
                background: {colors.BORDER_DARK};
            }}
        """)
    
    # 4. 键盘事件（Esc 取消，Enter 确认）
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.accept()
        else:
            super().keyPressEvent(event)
