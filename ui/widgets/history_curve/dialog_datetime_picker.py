"""
科技风格日期时间选择器对话框
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QPushButton, QSpinBox, QGridLayout, QWidget)
from PyQt6.QtCore import Qt, QDateTime, pyqtSignal
from PyQt6.QtGui import QFont
from ui.styles.themes import ThemeManager


class DialogDateTimePicker(QDialog):
    """科技风格日期时间选择器"""
    
    # 时间选择完成信号
    datetime_selected = pyqtSignal(QDateTime)
    
    # 1. 初始化对话框
    def __init__(self, initial_datetime: QDateTime, accent_color: str = None, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        self.accent_color = accent_color or self.theme_manager.glow_cyan()
        self.selected_datetime = initial_datetime
        
        # 当前显示的年月
        self.current_year = initial_datetime.date().year()
        self.current_month = initial_datetime.date().month()
        
        # 选中的日期时间
        self.selected_day = initial_datetime.date().day()
        self.selected_hour = initial_datetime.time().hour()
        
        self.init_ui()
        self.apply_styles()
        
        # 无边框窗口
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
    
    # 2. 初始化 UI
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 容器（用于边框）
        container = QWidget()
        container.setObjectName("datetime_picker_container")
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(16, 16, 16, 16)
        container_layout.setSpacing(12)
        
        # 标题栏
        title_bar = self.create_title_bar()
        container_layout.addWidget(title_bar)
        
        # 年月选择器
        year_month_selector = self.create_year_month_selector()
        container_layout.addWidget(year_month_selector)
        
        # 日历网格
        self.calendar_grid = self.create_calendar_grid()
        container_layout.addWidget(self.calendar_grid)
        
        # 小时选择器
        hour_selector = self.create_hour_selector()
        container_layout.addWidget(hour_selector)
        
        # 底部按钮
        button_bar = self.create_button_bar()
        container_layout.addWidget(button_bar)
        
        main_layout.addWidget(container)
    
    # 3. 创建标题栏
    def create_title_bar(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("选择日期时间")
        title.setObjectName("dialog_title")
        title.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        
        close_btn = QPushButton("✕")
        close_btn.setObjectName("close_btn")
        close_btn.setFixedSize(28, 28)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.reject)
        
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(close_btn)
        
        return widget
    
    # 4. 创建年月选择器
    def create_year_month_selector(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # 上一月按钮
        prev_btn = QPushButton("◀")
        prev_btn.setObjectName("nav_btn")
        prev_btn.setFixedSize(32, 32)
        prev_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        prev_btn.clicked.connect(self.prev_month)
        
        # 年份选择器
        self.year_spin = QSpinBox()
        self.year_spin.setObjectName("year_spin")
        self.year_spin.setRange(2020, 2030)
        self.year_spin.setValue(self.current_year)
        self.year_spin.setFixedHeight(32)
        self.year_spin.setSuffix(" 年")
        self.year_spin.valueChanged.connect(self.on_year_changed)
        
        # 月份选择器
        self.month_spin = QSpinBox()
        self.month_spin.setObjectName("month_spin")
        self.month_spin.setRange(1, 12)
        self.month_spin.setValue(self.current_month)
        self.month_spin.setFixedHeight(32)
        self.month_spin.setSuffix(" 月")
        self.month_spin.valueChanged.connect(self.on_month_changed)
        
        # 下一月按钮
        next_btn = QPushButton("▶")
        next_btn.setObjectName("nav_btn")
        next_btn.setFixedSize(32, 32)
        next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        next_btn.clicked.connect(self.next_month)
        
        layout.addWidget(prev_btn)
        layout.addWidget(self.year_spin)
        layout.addWidget(self.month_spin)
        layout.addWidget(next_btn)
        layout.addStretch()
        
        return widget
    
    # 5. 创建日历网格
    def create_calendar_grid(self):
        widget = QWidget()
        layout = QGridLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        # 星期标题
        weekdays = ["一", "二", "三", "四", "五", "六", "日"]
        for i, day in enumerate(weekdays):
            label = QLabel(day)
            label.setObjectName("weekday_label")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setFixedSize(40, 30)
            layout.addWidget(label, 0, i)
        
        # 日期按钮（占位，后续动态生成）
        self.day_buttons = []
        for row in range(6):
            for col in range(7):
                btn = QPushButton()
                btn.setObjectName("day_btn")
                btn.setFixedSize(40, 40)
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.clicked.connect(lambda checked, r=row, c=col: self.on_day_clicked(r, c))
                layout.addWidget(btn, row + 1, col)
                self.day_buttons.append(btn)
        
        self.update_calendar()
        return widget
    
    # 6. 创建小时选择器
    def create_hour_selector(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        label = QLabel("选择小时")
        label.setObjectName("section_label")
        layout.addWidget(label)
        
        # 小时按钮网格（0-23）
        hour_grid = QWidget()
        hour_layout = QGridLayout(hour_grid)
        hour_layout.setContentsMargins(0, 0, 0, 0)
        hour_layout.setSpacing(4)
        
        self.hour_buttons = []
        for hour in range(24):
            btn = QPushButton(f"{hour:02d}")
            btn.setObjectName("hour_btn")
            btn.setFixedSize(45, 32)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, h=hour: self.on_hour_clicked(h))
            hour_layout.addWidget(btn, hour // 6, hour % 6)
            self.hour_buttons.append(btn)
        
        layout.addWidget(hour_grid)
        
        self.update_hour_selection()
        return widget
    
    # 7. 创建底部按钮栏
    def create_button_bar(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        layout.addStretch()
        
        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.setObjectName("cancel_btn")
        cancel_btn.setFixedHeight(36)
        cancel_btn.setMinimumWidth(80)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        
        # 确定按钮
        ok_btn = QPushButton("确定")
        ok_btn.setObjectName("ok_btn")
        ok_btn.setFixedHeight(36)
        ok_btn.setMinimumWidth(80)
        ok_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        ok_btn.clicked.connect(self.accept_selection)
        
        layout.addWidget(cancel_btn)
        layout.addWidget(ok_btn)
        
        return widget
    
    # 8. 更新日历显示
    def update_calendar(self):
        from datetime import date, timedelta
        
        # 获取当月第一天是星期几（0=周一，6=周日）
        first_day = date(self.current_year, self.current_month, 1)
        weekday = first_day.weekday()
        
        # 获取当月天数
        if self.current_month == 12:
            next_month = date(self.current_year + 1, 1, 1)
        else:
            next_month = date(self.current_year, self.current_month + 1, 1)
        days_in_month = (next_month - first_day).days
        
        # 更新按钮
        day = 1
        for i, btn in enumerate(self.day_buttons):
            if i < weekday or day > days_in_month:
                btn.setText("")
                btn.setEnabled(False)
                btn.setProperty("selected", False)
            else:
                btn.setText(str(day))
                btn.setEnabled(True)
                btn.setProperty("selected", day == self.selected_day)
                day += 1
        
        # 刷新样式
        for btn in self.day_buttons:
            btn.style().unpolish(btn)
            btn.style().polish(btn)
    
    # 9. 更新小时选择显示
    def update_hour_selection(self):
        for i, btn in enumerate(self.hour_buttons):
            btn.setProperty("selected", i == self.selected_hour)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
    
    # 10. 上一月
    def prev_month(self):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        
        self.year_spin.setValue(self.current_year)
        self.month_spin.setValue(self.current_month)
        self.update_calendar()
    
    # 11. 下一月
    def next_month(self):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        
        self.year_spin.setValue(self.current_year)
        self.month_spin.setValue(self.current_month)
        self.update_calendar()
    
    # 12. 年份变化
    def on_year_changed(self, year):
        self.current_year = year
        self.update_calendar()
    
    # 13. 月份变化
    def on_month_changed(self, month):
        self.current_month = month
        self.update_calendar()
    
    # 14. 日期点击
    def on_day_clicked(self, row, col):
        btn = self.day_buttons[row * 7 + col]
        if btn.text():
            self.selected_day = int(btn.text())
            self.update_calendar()
    
    # 15. 小时点击
    def on_hour_clicked(self, hour):
        self.selected_hour = hour
        self.update_hour_selection()
    
    # 16. 确认选择
    def accept_selection(self):
        # 构建选中的日期时间
        self.selected_datetime = QDateTime(
            self.current_year,
            self.current_month,
            self.selected_day,
            self.selected_hour,
            0, 0
        )
        self.datetime_selected.emit(self.selected_datetime)
        self.accept()
    
    # 17. 获取选中的日期时间
    def get_selected_datetime(self) -> QDateTime:
        return self.selected_datetime
    
    # 18. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        self.setStyleSheet(f"""
            /* 容器 */
            QWidget#datetime_picker_container {{
                background: {colors.BG_DARK};
                border: 2px solid {self.accent_color};
                border-radius: 8px;
            }}
            
            /* 标题 */
            QLabel#dialog_title {{
                color: {self.accent_color};
            }}
            
            /* 关闭按钮 */
            QPushButton#close_btn {{
                background: transparent;
                color: {colors.TEXT_SECONDARY};
                border: none;
                border-radius: 4px;
                font-size: 18px;
            }}
            QPushButton#close_btn:hover {{
                background: {colors.STATUS_ALARM}33;
                color: {colors.STATUS_ALARM};
            }}
            
            /* 导航按钮 */
            QPushButton#nav_btn {{
                background: {colors.BG_MEDIUM};
                color: {self.accent_color};
                border: 1px solid {colors.BORDER_MEDIUM};
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton#nav_btn:hover {{
                background: {self.accent_color}33;
                border: 1px solid {self.accent_color};
            }}
            
            /* 年月选择器 */
            QSpinBox#year_spin, QSpinBox#month_spin {{
                background: {colors.BG_MEDIUM};
                color: {colors.TEXT_PRIMARY};
                border: 1px solid {colors.BORDER_MEDIUM};
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 14px;
                font-weight: bold;
            }}
            QSpinBox#year_spin:focus, QSpinBox#month_spin:focus {{
                border: 1px solid {self.accent_color};
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                background: {colors.BG_LIGHT};
                border: none;
                width: 20px;
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background: {self.accent_color}33;
            }}
            
            /* 星期标签 */
            QLabel#weekday_label {{
                color: {self.accent_color};
                font-size: 12px;
                font-weight: bold;
            }}
            
            /* 日期按钮 */
            QPushButton#day_btn {{
                background: {colors.BG_MEDIUM};
                color: {colors.TEXT_PRIMARY};
                border: 1px solid {colors.BORDER_DARK};
                border-radius: 4px;
                font-size: 13px;
            }}
            QPushButton#day_btn:hover:enabled {{
                background: {self.accent_color}33;
                border: 1px solid {self.accent_color};
            }}
            QPushButton#day_btn:disabled {{
                background: transparent;
                border: none;
            }}
            QPushButton#day_btn[selected="true"] {{
                background: {self.accent_color};
                color: {colors.BG_DARK};
                border: 1px solid {self.accent_color};
                font-weight: bold;
            }}
            
            /* 小时按钮 */
            QPushButton#hour_btn {{
                background: {colors.BG_MEDIUM};
                color: {colors.TEXT_PRIMARY};
                border: 1px solid {colors.BORDER_DARK};
                border-radius: 4px;
                font-size: 12px;
            }}
            QPushButton#hour_btn:hover {{
                background: {self.accent_color}33;
                border: 1px solid {self.accent_color};
            }}
            QPushButton#hour_btn[selected="true"] {{
                background: {self.accent_color};
                color: {colors.BG_DARK};
                border: 1px solid {self.accent_color};
                font-weight: bold;
            }}
            
            /* 分节标签 */
            QLabel#section_label {{
                color: {colors.TEXT_SECONDARY};
                font-size: 12px;
                font-weight: bold;
            }}
            
            /* 取消按钮 */
            QPushButton#cancel_btn {{
                background: {colors.BG_MEDIUM};
                color: {colors.TEXT_PRIMARY};
                border: 1px solid {colors.BORDER_MEDIUM};
                border-radius: 4px;
                font-size: 14px;
            }}
            QPushButton#cancel_btn:hover {{
                background: {colors.BG_LIGHT};
                border: 1px solid {colors.BORDER_LIGHT};
            }}
            
            /* 确定按钮 */
            QPushButton#ok_btn {{
                background: {self.accent_color};
                color: {colors.BG_DARK};
                border: 1px solid {self.accent_color};
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton#ok_btn:hover {{
                background: {self.accent_color}CC;
            }}
        """)

