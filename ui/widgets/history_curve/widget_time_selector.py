"""
时间选择器组件 - 起始时间和终止时间选择
"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import pyqtSignal, QDateTime, Qt
from ui.styles.themes import ThemeManager
from .dialog_datetime_picker import DialogDateTimePicker


class WidgetTimeSelector(QWidget):
    """时间选择器（起始时间和终止时间选择）"""
    
    # 时间范围变化信号
    time_range_changed = pyqtSignal(QDateTime, QDateTime)
    
    # 1. 初始化组件
    def __init__(self, accent_color: str = None, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        self.accent_color = accent_color or self.theme_manager.glow_cyan()
        
        # 默认时间范围：最近24小时
        self.start_time = QDateTime.currentDateTime().addDays(-1)
        self.end_time = QDateTime.currentDateTime()
        
        # 批次时间范围
        self.batch_start_time = None
        self.batch_end_time = None
        self.batch_duration_hours = 0.0
        
        self.init_ui()
        self.apply_styles()
        
        # 监听主题变化
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
    
    # 2. 初始化 UI
    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # 开始时间按钮
        self.start_button = QPushButton(self.start_time.toString("MM/dd HH:mm"))
        self.start_button.setObjectName("time_range_btn")
        self.start_button.setFixedHeight(32)
        self.start_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_button.clicked.connect(self.select_start_time)
        layout.addWidget(self.start_button)
        
        # 分隔符 -
        self.separator = QLabel("-")
        self.separator.setObjectName("separator_label")
        layout.addWidget(self.separator)
        
        # 结束时间按钮
        self.end_button = QPushButton(self.end_time.toString("MM/dd HH:mm"))
        self.end_button.setObjectName("time_range_btn")
        self.end_button.setFixedHeight(32)
        self.end_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.end_button.clicked.connect(self.select_end_time)
        layout.addWidget(self.end_button)
    
    # 3. 选择开始时间
    def select_start_time(self):
        dialog = DialogDateTimePicker(self.start_time, self.accent_color, self)
        
        if dialog.exec() == DialogDateTimePicker.DialogCode.Accepted:
            self.start_time = dialog.get_selected_datetime()
            self.start_button.setText(self.start_time.toString("MM/dd HH:mm"))
            
            # 确保开始时间不晚于结束时间
            if self.start_time > self.end_time:
                self.end_time = self.start_time.addSecs(3600)
                self.end_button.setText(self.end_time.toString("MM/dd HH:mm"))
            
            self.time_range_changed.emit(self.start_time, self.end_time)
    
    # 4. 选择结束时间
    def select_end_time(self):
        dialog = DialogDateTimePicker(self.end_time, self.accent_color, self)
        
        if dialog.exec() == DialogDateTimePicker.DialogCode.Accepted:
            self.end_time = dialog.get_selected_datetime()
            self.end_button.setText(self.end_time.toString("MM/dd HH:mm"))
            
            # 确保结束时间不早于开始时间
            if self.end_time < self.start_time:
                self.start_time = self.end_time.addSecs(-3600)
                self.start_button.setText(self.start_time.toString("MM/dd HH:mm"))
            
            self.time_range_changed.emit(self.start_time, self.end_time)
    
    # 5. 获取时间范围
    def get_time_range(self) -> tuple[QDateTime, QDateTime]:
        return self.start_time, self.end_time
    
    # 6. 设置时间范围
    def set_time_range(self, start: QDateTime, end: QDateTime):
        self.start_time = start
        self.end_time = end
        self.start_button.setText(start.toString("MM/dd HH:mm"))
        self.end_button.setText(end.toString("MM/dd HH:mm"))
    
    # 7. 设置批次时间范围
    def set_batch_time_range(self, start_time, end_time, duration_hours: float):
        """
        设置批次的时间范围，默认显示完整时间范围
        
        Args:
            start_time: 批次起始时间（datetime）
            end_time: 批次结束时间（datetime）
            duration_hours: 批次总时长（小时）
        """
        from datetime import datetime
        from loguru import logger
        
        # 保存批次时间范围
        self.batch_start_time = QDateTime(start_time)
        self.batch_end_time = QDateTime(end_time)
        self.batch_duration_hours = duration_hours
        
        # 默认显示完整时间范围
        self.start_time = self.batch_start_time
        self.end_time = self.batch_end_time
        self.start_button.setText(self.start_time.toString("MM/dd HH:mm"))
        self.end_button.setText(self.end_time.toString("MM/dd HH:mm"))
        
        logger.info(f"设置批次时间范围: {start_time} - {end_time}, 总时长: {duration_hours:.1f}h")
    
    # 8. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        # 分隔符样式（无边框，只有文字颜色）
        self.separator.setStyleSheet(f"""
            QLabel#separator_label {{
                color: {colors.TEXT_SECONDARY};
                font-size: 14px;
                border: none;
                background: transparent;
            }}
        """)
        
        # 时间按钮样式
        self.setStyleSheet(f"""
            QPushButton#time_range_btn {{
                background: {colors.BTN_BG_NORMAL};
                color: {colors.TEXT_PRIMARY};
                border: 1px solid {colors.BORDER_MEDIUM};
                border-radius: 4px;
                padding: 6px 16px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton#time_range_btn:hover {{
                background: {colors.BTN_BG_HOVER};
                border: 1px solid {self.accent_color};
            }}
            QPushButton#time_range_btn:pressed {{
                background: {colors.BG_MEDIUM};
            }}
            
            QLabel#separator_label {{
                border: none;
                background: transparent;
            }}
        """)
    
    # 9. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()

