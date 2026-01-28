"""
主窗口 - 实现全屏、最小化、页面切换等基础功能
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QStackedWidget, QPushButton, QLabel, QFrame
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QKeySequence, QShortcut, QFont
from ui.styles.themes import ThemeManager, Theme
from ui.styles.qss_styles import QSSStyles
from ui.widgets.bar.top_nav_bar import TopNavBar
from ui.pages.page_status import PageStatus
from ui.pages.page_elec_3 import PageElec3
from ui.pages.page_pump_hopper import PagePumpHopper
from ui.pages.page_history_curve import PageHistoryCurve


class MainWindow(QMainWindow):
    """主窗口类"""
    
    # 1. 初始化主窗口
    def __init__(self):
        super().__init__()
        self.theme_manager = ThemeManager.instance()
        self.qss_styles = QSSStyles(self.theme_manager)
        
        # 监听主题变化
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
        
        self.init_ui()
        self.setup_shortcuts()
        
    # 2. 初始化UI
    def init_ui(self):
        self.setWindowTitle("#3电炉 - PyQt6")
        
        # 隐藏系统标题栏，使用自定义工具栏
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        # 设置窗口大小为 1280x1024
        self.resize(1280, 1024)
        
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
        
        # 页面 4: 系统设置
        page4 = self.create_page("系统设置", "⚙ 系统配置")
        self.page_stack.addWidget(page4)
    
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
            f"✅ {title}页面已创建\n\n"
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
            self.showNormal()
        else:
            self.showFullScreen()
    
    # 8. 主题变化回调
    def on_theme_changed(self, theme: Theme):
        # 重新应用样式
        self.apply_theme()
    
    # 9. 应用主题样式
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
            
    # 10. 添加页面到页面栈
    def add_page(self, page: QWidget, name: str = ""):
        index = self.page_stack.addWidget(page)
        return index
        
    # 11. 切换到指定页面
    def switch_page(self, index: int):
        if 0 <= index < self.page_stack.count():
            self.page_stack.setCurrentIndex(index)
            
    # 12. 获取当前页面索引
    def get_current_page_index(self):
        return self.page_stack.currentIndex()
