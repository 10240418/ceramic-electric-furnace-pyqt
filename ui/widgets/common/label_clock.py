"""
时钟标签组件 - 显示当前日期和时间
"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont
from datetime import datetime
from ui.styles.themes import ThemeManager


class LabelClock(QWidget):
    """时钟标签组件，显示格式：yyyy年mm月dd日 HH:MM:SS"""
    
    # 1. 初始化组件
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        
        # 时钟定时器
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_clock)
        
        # 监听主题变化
        self.theme_manager.theme_changed.connect(self.apply_styles)
        
        self.init_ui()
        self.apply_styles()
        
        # 立即更新一次时钟
        self.update_clock()
        
        # 启动定时器
        self.clock_timer.start(1000)  # 每秒更新
    
    # 2. 初始化 UI
    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)
        
        # 日期标签 (yyyy年mm月dd日)
        self.date_label = QLabel()
        self.date_label.setObjectName("clock_date")
        self.date_label.setFont(QFont("Consolas", 14, QFont.Weight.DemiBold))
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.date_label)
        
        # 时间标签 (HH:MM:SS)
        self.time_label = QLabel()
        self.time_label.setObjectName("clock_time")
        self.time_label.setFont(QFont("Consolas", 14, QFont.Weight.DemiBold))
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.time_label)
    
    # 3. 更新时钟显示
    def update_clock(self):
        now = datetime.now()
        date_str = now.strftime("%Y年%m月%d日")
        time_str = now.strftime("%H:%M:%S")
        self.date_label.setText(date_str)
        self.time_label.setText(time_str)
    
    # 4. 应用样式
    def apply_styles(self):
        tm = self.theme_manager
        
        self.setStyleSheet(f"""
            QLabel#clock_date {{
                color: {tm.border_glow()};
                background: transparent;
                border: none;
                padding: 4px 2px;
            }}
            
            QLabel#clock_time {{
                color: {tm.border_glow()};
                background: transparent;
                border: none;
                padding: 4px 2px;
            }}
        """)
    
    # 5. 清理资源
    def cleanup(self):
        if self.clock_timer:
            self.clock_timer.stop()

