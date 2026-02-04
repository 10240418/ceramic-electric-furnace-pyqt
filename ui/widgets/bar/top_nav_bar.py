"""
顶部导航栏 - 科技风格导航栏组件
"""
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout, QPushButton, 
    QLabel, QWidget
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtSvgWidgets import QSvgWidget
from datetime import datetime
from pathlib import Path
from ui.styles.themes import ThemeManager
from ui.widgets.common.switch_theme import SwitchTheme
from ui.widgets.common.label_clock import LabelClock
from backend.bridge.data_cache import get_data_cache
from backend.bridge.service_manager import ServiceManager
from backend.plc.plc_manager import get_plc_manager
from backend.core.influxdb import check_influx_health
from loguru import logger


class TopNavBar(QFrame):
    """顶部导航栏组件"""
    
    # 导航切换信号
    nav_changed = pyqtSignal(int)
    
    # 1. 初始化导航栏
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        self.current_nav_index = 0
        self.is_settings_active = False  # 设置页面是否激活
        
        # 导航项列表
        self.nav_items = ['3# 电炉', '历史曲线', '状态监控', '泵房/料仓']
        self.nav_buttons = []
        
        # 设置按钮
        self.settings_button = None
        
        # 状态查询定时器 (5秒一次)
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status)
        self.status_timer.start(5000)  # 5秒更新
        
        # 数据缓存
        self.data_cache = get_data_cache()
        
        # 状态标签
        self.status_plc = None
        self.status_service = None
        self.status_database = None
        
        # 监听主题变化
        self.theme_manager.theme_changed.connect(self.apply_styles)
        
        # 拖动窗口相关
        self.drag_position = None
        
        self.init_ui()
        self.apply_styles()
        
        # 立即更新一次状态
        self.update_status()
    
    # 2. 初始化 UI
    def init_ui(self):
        self.setObjectName("top_nav_bar")
        self.setFixedHeight(60)
        
        # 主布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(15)
        
        # Logo 和标题
        logo_widget = self.create_logo()
        layout.addWidget(logo_widget)
        
        layout.addSpacing(8)
        
        # 导航按钮
        for i, nav_text in enumerate(self.nav_items):
            btn = self.create_nav_button(nav_text, i)
            self.nav_buttons.append(btn)
            layout.addWidget(btn)
        
        layout.addStretch()
        
        # 时钟显示
        self.clock_widget = LabelClock()
        layout.addWidget(self.clock_widget)
        
        layout.addSpacing(-8)  # 时钟和PLC状态之间减小12px (原来4px，现在-8px，总共减小12px)
        
        # 状态指示器 (PLC, 服务, 数据库)
        self.status_plc = self.create_status_indicator("PLC")
        layout.addWidget(self.status_plc)
        
        layout.addSpacing(2)  # 状态指示器之间：2px
        
        self.status_service = self.create_status_indicator("服务")
        layout.addWidget(self.status_service)
        
        layout.addSpacing(2)  # 状态指示器之间：2px
        
        self.status_database = self.create_status_indicator("数据库")
        layout.addWidget(self.status_database)
        
        layout.addSpacing(0)  # 状态指示器和设置按钮之间：0px
        
        # 设置按钮
        self.settings_button = self.create_settings_button()
        layout.addWidget(self.settings_button)
        
        layout.addSpacing(4)  # 设置按钮和窗口控制之间：4px
        
        # 窗口控制按钮
        window_controls = self.create_window_controls()
        layout.addWidget(window_controls)
    
    # 3. 创建 Logo 和标题
    def create_logo(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Logo 竖条
        logo_bar = QFrame()
        logo_bar.setObjectName("logo_bar")
        logo_bar.setFixedSize(4, 28)
        layout.addWidget(logo_bar)
        
        # 标题文字
        title = QLabel("#3电炉")
        title.setObjectName("nav_title")
        title.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        return widget
    
    # 4. 创建导航按钮
    def create_nav_button(self, text: str, index: int):
        btn = QPushButton(text)
        btn.setObjectName(f"nav_btn_{index}")
        btn.setFixedHeight(36)
        btn.setMinimumWidth(100)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(lambda: self.on_nav_clicked(index))
        return btn
    
    # 5. 创建状态指示器
    def create_status_indicator(self, name: str):
        widget = QWidget()
        widget.setObjectName(f"status_{name.lower()}")
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(0)
        
        # 状态文字
        status_text = QLabel(name)
        status_text.setObjectName(f"status_text_{name.lower()}")
        status_text.setFont(QFont("Microsoft YaHei", 13, QFont.Weight.Bold))
        layout.addWidget(status_text)
        
        return widget
    
    # 6. 创建设置按钮
    def create_settings_button(self):
        # 获取 SVG 图标路径 (从当前文件向上3层到项目根目录)
        # top_nav_bar.py -> bar -> widgets -> ui -> 项目根目录
        icon_path = Path(__file__).parent.parent.parent.parent / "assets" / "icons" / "settings.svg"
        
        btn = QPushButton()
        btn.setObjectName("settings_btn")
        btn.setFixedSize(40, 40)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setToolTip("系统设置")
        
        # 检查文件是否存在
        if not icon_path.exists():
            print(f"警告: SVG 图标不存在: {icon_path}")
            # 使用文本作为后备方案
            btn.setText("⚙")
            btn.setStyleSheet(f"font-size: 18px;")
            btn.clicked.connect(self.on_settings_clicked)
            return btn
        
        # 创建 SVG 图标容器
        self.settings_svg = QSvgWidget(str(icon_path))
        self.settings_svg.setFixedSize(24, 24)
        
        # 将 SVG 添加到按钮布局中
        layout = QHBoxLayout(btn)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.settings_svg)
        
        btn.clicked.connect(self.on_settings_clicked)
        return btn
    
    # 7. 创建窗口控制按钮
    def create_window_controls(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # 最小化按钮
        btn_minimize = QPushButton("━")
        btn_minimize.setObjectName("btn_minimize")
        btn_minimize.setFixedSize(36, 36)
        btn_minimize.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_minimize.clicked.connect(self.on_minimize_clicked)
        layout.addWidget(btn_minimize)
        
        # 全屏切换按钮
        self.btn_fullscreen = QPushButton("⛶")
        self.btn_fullscreen.setObjectName("btn_fullscreen")
        self.btn_fullscreen.setFixedSize(36, 36)
        self.btn_fullscreen.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_fullscreen.clicked.connect(self.on_fullscreen_clicked)
        layout.addWidget(self.btn_fullscreen)
        
        # 退出按钮
        btn_exit = QPushButton("✕")
        btn_exit.setObjectName("btn_exit")
        btn_exit.setFixedSize(36, 36)
        btn_exit.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_exit.clicked.connect(self.on_exit_clicked)
        layout.addWidget(btn_exit)
        
        return widget
    
    # 8. 导航按钮点击处理
    def on_nav_clicked(self, index: int):
        if self.current_nav_index == index:
            return
        
        self.current_nav_index = index
        self.is_settings_active = False  # 切换到导航页面，设置页面不激活
        self.apply_styles()
        self.nav_changed.emit(index)
    
    # 9. 设置按钮点击处理
    def on_settings_clicked(self):
        # 发送特殊索引 4 表示设置页面（因为现在有4个导航页面了）
        self.current_nav_index = -1  # 设置页面不算在导航索引中
        self.is_settings_active = True  # 激活设置页面
        self.apply_styles()
        self.nav_changed.emit(4)
    
    # 10. 更新状态显示
    def update_status(self):
        try:
            # 1. 检查 PLC 连接状态
            plc_manager = get_plc_manager()
            plc_connected = plc_manager.is_connected()
            self.update_status_indicator(self.status_plc, plc_connected)
            
            # 2. 检查服务状态 (轮询服务是否运行)
            from backend.services.polling_loops_v2 import get_polling_loops_status
            polling_status = get_polling_loops_status()
            service_running = (
                polling_status.get('db1_running', False) and 
                polling_status.get('db32_running', False) and 
                polling_status.get('status_running', False)
            )
            self.update_status_indicator(self.status_service, service_running)
            
            # 3. 检查数据库连接状态
            db_ok, _ = check_influx_health()
            self.update_status_indicator(self.status_database, db_ok)
                
        except Exception as e:
            logger.error(f"更新状态失败: {e}")
    
    # 11. 更新单个状态指示器
    def update_status_indicator(self, widget: QWidget, is_ok: bool):
        if not widget:
            return
        
        tm = self.theme_manager
        
        if is_ok:
            # 正常：绿色边框和文字
            widget.setStyleSheet(f"""
                QWidget {{
                    background: transparent;
                    border: 1px solid {tm.status_normal()};
                    border-radius: 4px;
                }}
                QLabel {{
                    color: {tm.status_normal()};
                    background: transparent;
                    border: none;
                }}
            """)
        else:
            # 异常：红色边框和文字
            widget.setStyleSheet(f"""
                QWidget {{
                    background: transparent;
                    border: 1px solid {tm.status_alarm()};
                    border-radius: 4px;
                }}
                QLabel {{
                    color: {tm.status_alarm()};
                    background: transparent;
                    border: none;
                }}
            """)
    
    # 12. 最小化按钮点击
    def on_minimize_clicked(self):
        window = self.window()
        if window:
            window.showMinimized()
    
    # 13. 全屏切换按钮点击
    def on_fullscreen_clicked(self):
        window = self.window()
        if window:
            if window.isFullScreen():
                window.showNormal()
                self.btn_fullscreen.setText("⛶")
            else:
                window.showFullScreen()
                self.btn_fullscreen.setText("⛗")
    
    # 14. 退出按钮点击
    def on_exit_clicked(self):
        window = self.window()
        if window:
            window.close()
    
    # 15. 应用样式
    def apply_styles(self):
        tm = self.theme_manager
        
        # 导航栏容器样式
        self.setStyleSheet(f"""
            QFrame#top_nav_bar {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {tm.bg_dark()}, stop:1 {tm.bg_medium()});
                border-bottom: 2px solid {tm.border_glow()};
            }}
            
            /* Logo 竖条 */
            QFrame#logo_bar {{
                background: {tm.border_glow()};
                border-radius: 2px;
            }}
            
            /* 标题 */
            QLabel#nav_title {{
                color: {tm.border_glow()};
            }}
            
            /* 窗口控制按钮 */
            QPushButton#btn_minimize,
            QPushButton#btn_fullscreen {{
                background: {tm.bg_light()};
                color: {tm.text_primary()};
                border: 1px solid {tm.border_medium()};
                border-radius: 4px;
                font-size: 16px;
                font-weight: bold;
            }}
            
            QPushButton#btn_minimize:hover,
            QPushButton#btn_fullscreen:hover {{
                background: {tm.bg_medium()};
                border: 1px solid {tm.border_glow()};
                color: {tm.border_glow()};
            }}
            
            QPushButton#btn_exit {{
                background: {tm.status_alarm()};
                color: {tm.white()};
                border: 1px solid {tm.status_alarm()};
                border-radius: 4px;
                font-size: 16px;
                font-weight: bold;
            }}
            
            QPushButton#btn_exit:hover {{
                background: #ff5544;
                border: 1px solid #ff5544;
            }}
            
            /* 设置按钮 */
            QPushButton#settings_btn {{
                background: transparent;
                border: none;
                border-radius: 4px;
            }}
            
            QPushButton#settings_btn:hover {{
                background: {tm.bg_light()};
            }}
        """)
        
        # 更新 SVG 图标颜色
        if hasattr(self, 'settings_svg'):
            # 读取 SVG 文件并替换颜色
            icon_path = Path(__file__).parent.parent.parent.parent / "assets" / "icons" / "settings.svg"
            
            # 检查文件是否存在
            if icon_path.exists():
                with open(icon_path, 'r', encoding='utf-8') as f:
                    svg_content = f.read()
                
                # 根据激活状态设置颜色
                if self.is_settings_active:
                    # 激活时使用发光色
                    svg_content = svg_content.replace('fill="currentColor"', f'fill="{tm.border_glow()}"')
                else:
                    # 未激活时使用次要文字色
                    svg_content = svg_content.replace('fill="currentColor"', f'fill="{tm.text_secondary()}"')
                
                # 重新加载 SVG
                self.settings_svg.load(svg_content.encode('utf-8'))
        
        # 更新导航按钮样式
        for i, btn in enumerate(self.nav_buttons):
            is_selected = (i == self.current_nav_index)
            
            if is_selected:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {tm.border_glow()}15;
                        color: {tm.text_selected()};
                        border: 1px solid {tm.border_glow()};
                        border-radius: 4px;
                        padding: 8px 20px;
                        font-size: 13px;
                        font-weight: 600;
                    }}
                    
                    QPushButton:hover {{
                        background: {tm.border_glow()}25;
                        border: 1px solid {tm.border_glow()};
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: transparent;
                        color: {tm.text_secondary()};
                        border: 1px solid transparent;
                        border-radius: 4px;
                        padding: 8px 20px;
                        font-size: 13px;
                        font-weight: 400;
                    }}
                    
                    QPushButton:hover {{
                        background: {tm.bg_light()};
                        border: 1px solid {tm.border_medium()};
                        color: {tm.text_primary()};
                    }}
                """)
    
    # 16. 设置当前导航索引
    def set_current_nav(self, index: int):
        if 0 <= index < len(self.nav_items):
            self.current_nav_index = index
            self.apply_styles()
    
    # 17. 清理资源
    def cleanup(self):
        if self.clock_widget:
            self.clock_widget.cleanup()
        if self.status_timer:
            self.status_timer.stop()
    
    # 18. 鼠标按下事件（开始拖动）
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.window().frameGeometry().topLeft()
            event.accept()
    
    # 19. 鼠标移动事件（拖动窗口）
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_position is not None:
            self.window().move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    # 20. 鼠标释放事件（结束拖动）
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = None
            event.accept()

