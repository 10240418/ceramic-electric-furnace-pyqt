"""
时间选择器组件（合并版）- 包含时间范围选择和快速选择
"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import pyqtSignal, QDateTime, Qt
from ui.styles.themes import ThemeManager
from .dialog_datetime_picker import DialogDateTimePicker


class WidgetTimeSelector(QWidget):
    """时间选择器（合并时间范围选择和快速选择）"""
    
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
        
        # 快速时间选项（小时）
        self.quick_options = [3, 7, 12, 24, 32]
        self.selected_hours = None
        self.quick_buttons = []
        
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
        self.start_button.setFixedHeight(28)
        self.start_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_button.clicked.connect(self.select_start_time)
        layout.addWidget(self.start_button)
        
        # 分隔符 -
        self.separator1 = QLabel("-")
        self.separator1.setObjectName("separator_label")
        layout.addWidget(self.separator1)
        
        # 结束时间按钮
        self.end_button = QPushButton(self.end_time.toString("MM/dd HH:mm"))
        self.end_button.setObjectName("time_range_btn")
        self.end_button.setFixedHeight(28)
        self.end_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.end_button.clicked.connect(self.select_end_time)
        layout.addWidget(self.end_button)
        
        # 分隔符 |
        self.separator2 = QLabel("|")
        self.separator2.setObjectName("separator_label")
        layout.addWidget(self.separator2)
        
        # 快速时间选择按钮
        for hours in self.quick_options:
            btn = QPushButton(f"{hours}H")
            btn.setObjectName("quick_time_btn")
            btn.setFixedHeight(28)
            btn.setMinimumWidth(45)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, h=hours: self.on_quick_time_selected(h))
            btn.setProperty("selected", False)
            layout.addWidget(btn)
            self.quick_buttons.append(btn)
    
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
            
            # 清除快速选择状态
            self.clear_quick_selection()
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
            
            # 清除快速选择状态
            self.clear_quick_selection()
            self.time_range_changed.emit(self.start_time, self.end_time)
    
    # 5. 快速时间选择
    def on_quick_time_selected(self, hours: int):
        # 更新选中状态
        self.selected_hours = hours
        
        # 计算时间范围
        self.end_time = QDateTime.currentDateTime()
        self.start_time = self.end_time.addSecs(-hours * 3600)
        
        # 更新时间按钮显示
        self.start_button.setText(self.start_time.toString("MM/dd HH:mm"))
        self.end_button.setText(self.end_time.toString("MM/dd HH:mm"))
        
        # 更新快速按钮样式
        for i, btn in enumerate(self.quick_buttons):
            btn.setProperty("selected", self.quick_options[i] == hours)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        
        # 发送信号
        self.time_range_changed.emit(self.start_time, self.end_time)
    
    # 6. 清除快速选择状态
    def clear_quick_selection(self):
        self.selected_hours = None
        for btn in self.quick_buttons:
            btn.setProperty("selected", False)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
    
    # 7. 获取时间范围
    def get_time_range(self) -> tuple[QDateTime, QDateTime]:
        return self.start_time, self.end_time
    
    # 8. 设置时间范围
    def set_time_range(self, start: QDateTime, end: QDateTime):
        self.start_time = start
        self.end_time = end
        self.start_button.setText(start.toString("MM/dd HH:mm"))
        self.end_button.setText(end.toString("MM/dd HH:mm"))
        self.clear_quick_selection()
    
    # 9. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        is_dark = self.theme_manager.is_dark_mode()
        
        # 浅色主题：未选中用白色背景，深色主题：用半透明背景
        if is_dark:
            bg_normal = f"{colors.BG_LIGHT}4D"
            bg_hover = f"{self.accent_color}33"
            selected_text = colors.BG_DARK
        else:
            bg_normal = colors.BG_LIGHT  # 白色
            bg_hover = f"{self.accent_color}1A"  # 浅绿色半透明
            selected_text = colors.TEXT_ON_PRIMARY  # 深色主题深色，浅色主题白色
        
        # 分隔符样式（无边框，只有文字颜色）
        self.separator1.setStyleSheet(f"""
            QLabel#separator_label {{
                color: {colors.TEXT_SECONDARY};
                font-size: 14px;
                border: none;
                background: transparent;
            }}
        """)
        
        self.separator2.setStyleSheet(f"""
            QLabel#separator_label {{
                color: {colors.BORDER_MEDIUM};
                font-size: 14px;
                border: none;
                background: transparent;
            }}
        """)
        
        # 整体样式（包含时间按钮和快速选择按钮）
        self.setStyleSheet(f"""
            QPushButton#time_range_btn {{
                background: {bg_normal};
                color: {colors.TEXT_PRIMARY};
                border: 1px solid {colors.BORDER_MEDIUM};
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
                font-weight: 500;
            }}
            QPushButton#time_range_btn:hover {{
                background: {bg_hover};
                border: 1px solid {self.accent_color}80;
            }}
            QPushButton#time_range_btn:pressed {{
                background: {self.accent_color}4D;
            }}
            
            QPushButton#quick_time_btn {{
                background: {bg_normal};
                color: {colors.TEXT_SECONDARY};
                border: 1px solid {colors.BORDER_MEDIUM};
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 12px;
                font-weight: 500;
            }}
            QPushButton#quick_time_btn:hover {{
                background: {bg_hover};
                border: 1px solid {self.accent_color}80;
                color: {colors.TEXT_PRIMARY};
            }}
            QPushButton#quick_time_btn[selected="true"] {{
                background: {self.accent_color};
                color: {selected_text};
                border: 1px solid {self.accent_color};
                font-weight: bold;
            }}
            QPushButton#quick_time_btn[selected="true"]:hover {{
                background: {self.accent_color}CC;
            }}
            
            QLabel#separator_label {{
                border: none;
                background: transparent;
            }}
        """)
    
    # 10. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()

