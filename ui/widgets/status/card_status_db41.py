"""
DB41 卡片
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from ui.styles.themes import ThemeManager


class CardStatusDb41(QFrame):
    """DB41 卡片"""
    
    # 1. 初始化卡片
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        self.theme_manager.theme_changed.connect(self.apply_styles)
        
        self.devices = []
        self.device_widgets = []
        
        self.init_ui()
        self.apply_styles()
    
    # 2. 初始化 UI
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 头部
        header = self.create_header()
        layout.addWidget(header)
        
        # 设备网格
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        self.grid_layout.setContentsMargins(8, 8, 8, 8)
        self.grid_layout.setSpacing(4)
        layout.addWidget(self.grid_widget)
    
    # 3. 创建头部
    def create_header(self):
        header = QWidget()
        header.setObjectName("status_header")
        header.setFixedHeight(40)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(8)
        
        # 图标
        icon_label = QLabel("")
        icon_label.setObjectName("header_icon")
        icon_label.setFont(QFont("Segoe UI Emoji", 16))
        layout.addWidget(icon_label)
        
        # 标题
        title = QLabel("DB41 ")
        title.setObjectName("header_title")
        title.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.DemiBold))
        layout.addWidget(title)
        
        layout.addStretch()
        
        # 统计标签
        self.stat_normal = self.create_stat_chip("正常", 0, "normal")
        self.stat_error = self.create_stat_chip("异常", 0, "error")
        self.stat_total = self.create_stat_chip("总数", 0, "total")
        
        layout.addWidget(self.stat_normal)
        layout.addSpacing(8)
        layout.addWidget(self.stat_error)
        layout.addSpacing(8)
        layout.addWidget(self.stat_total)
        
        return header
    
    # 4. 创建统计芯片
    def create_stat_chip(self, label: str, count: int, chip_type: str):
        chip = QWidget()
        chip.setObjectName(f"stat_chip_{chip_type}")
        
        chip_layout = QHBoxLayout(chip)
        chip_layout.setContentsMargins(10, 4, 10, 4)
        chip_layout.setSpacing(4)
        
        label_widget = QLabel(label)
        label_widget.setObjectName(f"stat_label_{chip_type}")
        label_widget.setFont(QFont("Microsoft YaHei", 11))
        chip_layout.addWidget(label_widget)
        
        count_widget = QLabel(str(count))
        count_widget.setObjectName(f"stat_count_{chip_type}")
        count_widget.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        chip_layout.addWidget(count_widget)
        
        return chip
    
    # 5. 更新设备列表
    def update_devices(self, devices: list):
        self.devices = devices
        
        # 清空现有组件
        for widget in self.device_widgets:
            widget.deleteLater()
        self.device_widgets.clear()
        
        # 创建设备卡片（3列布局）
        for i, device in enumerate(devices):
            row = i // 3
            col = i % 3
            card = self.create_device_card(device, i)
            self.grid_layout.addWidget(card, row, col)
            self.device_widgets.append(card)
        
        # 更新统计
        self.update_statistics()
    
    # 6. 创建设备卡片
    def create_device_card(self, device: dict, index: int):
        card = QWidget()
        card.setObjectName("device_card")
        card.setFixedHeight(32)
        
        layout = QHBoxLayout(card)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)
        
        # 判断是否有错误（只有 error=True 才是错误）
        has_error = device.get("error", False)
        
        # 序号
        index_label = QLabel(str(index + 1))
        index_label.setObjectName("device_index")
        index_label.setFont(QFont("Consolas", 10))
        index_label.setFixedWidth(20)
        index_label.setStyleSheet("border: none; background: transparent;")
        layout.addWidget(index_label)
        
        # 状态灯
        status_dot = QLabel("●")
        status_dot.setObjectName("status_dot_error" if has_error else "status_dot_normal")
        status_dot.setFont(QFont("Segoe UI Emoji", 10))
        status_dot.setStyleSheet("border: none; background: transparent;")
        layout.addWidget(status_dot)
        
        # 设备名
        name_label = QLabel(device.get("name", "未知设备"))
        name_label.setObjectName("device_name")
        name_label.setFont(QFont("Consolas", 11))
        name_label.setStyleSheet("border: none; background: transparent;")
        layout.addWidget(name_label, 1)
        
        # E (Error)
        error_badge = self.create_value_badge("E", "1" if device.get("error") else "0", device.get("error"), has_error)
        layout.addWidget(error_badge)
        
        layout.addSpacing(4)
        
        # S (Status - 十六进制)
        status_val = device.get("status", 0)
        status_hex = f"{status_val:04X}"
        status_badge = self.create_value_badge("S", status_hex, status_val != 0, has_error)
        layout.addWidget(status_badge)
        
        return card
    
    # 7. 创建值徽章
    def create_value_badge(self, label: str, value: str, is_active: bool, is_error: bool = False):
        badge = QWidget()
        badge.setObjectName("value_badge")
        
        layout = QHBoxLayout(badge)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)
        
        # 标签（无边框）
        label_widget = QLabel(f"{label}:")
        label_widget.setObjectName("badge_label")
        label_widget.setFont(QFont("Consolas", 9))
        label_widget.setStyleSheet("border: none; background: transparent;")
        layout.addWidget(label_widget)
        
        # 值容器（有边框）
        value_container = QLabel(value)
        if is_error:
            value_container.setObjectName("badge_value_error")
        elif is_active:
            value_container.setObjectName("badge_value_active")
        else:
            value_container.setObjectName("badge_value_inactive")
        value_container.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        value_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_container)
        
        return badge
    
    # 8. 更新统计
    def update_statistics(self):
        total = len(self.devices)
        error_count = sum(1 for d in self.devices if d.get("error", False))
        normal_count = total - error_count
        
        # 更新统计芯片
        self.stat_normal.findChild(QLabel, "stat_count_normal").setText(str(normal_count))
        self.stat_error.findChild(QLabel, "stat_count_error").setText(str(error_count))
        self.stat_total.findChild(QLabel, "stat_count_total").setText(str(total))
    
    # 9. 应用样式
    def apply_styles(self):
        tm = self.theme_manager
        
        self.setStyleSheet(f"""
            CardStatusDb41 {{
                background: {tm.card_bg()};
                border: 1px solid {tm.card_border()};
                border-radius: 12px;
            }}
            
            /* 头部 */
            QWidget#status_header {{
                background: {tm.bg_medium()};
                border: none;
                border-bottom: 1px solid {tm.border_medium()};
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }}
            
            QLabel#header_icon {{
                color: {tm.glow_orange()};
                border: none;
                background: transparent;
            }}
            
            QLabel#header_title {{
                color: {tm.text_primary()};
                border: none;
                background: transparent;
            }}
            
            /* 统计芯片 */
            QWidget#stat_chip_normal {{
                background: rgba(0, 255, 136, 0.1);
                border: 1px solid rgba(0, 255, 136, 0.3);
                border-radius: 12px;
            }}
            
            QWidget#stat_chip_error {{
                background: rgba(255, 0, 0, 0.1);
                border: 1px solid rgba(255, 0, 0, 0.3);
                border-radius: 12px;
            }}
            
            QWidget#stat_chip_total {{
                background: rgba(255, 149, 0, 0.1);
                border: 1px solid rgba(255, 149, 0, 0.3);
                border-radius: 12px;
            }}
            
            QLabel#stat_label_normal {{
                color: {tm.status_success()};
                border: none;
                background: transparent;
            }}
            
            QLabel#stat_count_normal {{
                color: {tm.status_success()};
                border: none;
                background: transparent;
            }}
            
            QLabel#stat_label_error {{
                color: {tm.status_alarm()};
                border: none;
                background: transparent;
            }}
            
            QLabel#stat_count_error {{
                color: {tm.status_alarm()};
                border: none;
                background: transparent;
            }}
            
            QLabel#stat_label_total {{
                color: {tm.glow_orange()};
                border: none;
                background: transparent;
            }}
            
            QLabel#stat_count_total {{
                color: {tm.glow_orange()};
                border: none;
                background: transparent;
            }}
            
            /* 设备卡片 */
            QWidget#device_card {{
                background: {tm.bg_surface()};
                border: 1px solid {tm.border_dark()};
                border-radius: 6px;
            }}
            
            QWidget#device_card:hover {{
                background: {tm.bg_overlay()};
                border: 1px solid {tm.border_medium()};
            }}
            
            QLabel#device_index {{
                color: {tm.text_tertiary()};
                border: none;
                background: transparent;
            }}
            
            QLabel#status_dot_normal {{
                color: {tm.status_success()};
                border: none;
                background: transparent;
            }}
            
            QLabel#status_dot_error {{
                color: {tm.status_alarm()};
                border: none;
                background: transparent;
            }}
            
            QLabel#device_name {{
                color: {tm.text_primary()};
                border: none;
                background: transparent;
            }}
            
            /* 徽章 */
            QWidget#value_badge {{
                border: none;
                background: transparent;
            }}
            
            QLabel#badge_label {{
                color: {tm.text_secondary()};
                border: none;
                background: transparent;
            }}
            
            QLabel#badge_value_active {{
                background: rgba(255, 149, 0, 0.2);
                color: {tm.glow_orange()};
                border: 1px solid {tm.glow_orange()};
                border-radius: 3px;
                padding: 2px 6px;
            }}
            
            QLabel#badge_value_inactive {{
                background: {tm.bg_medium()};
                color: {tm.text_muted()};
                border: 1px solid {tm.border_dark()};
                border-radius: 3px;
                padding: 2px 6px;
            }}
            
            QLabel#badge_value_error {{
                background: rgba(255, 0, 0, 0.15);
                color: {tm.status_alarm()};
                border: 1px solid {tm.status_alarm()};
                border-radius: 3px;
                padding: 2px 6px;
            }}
        """)

