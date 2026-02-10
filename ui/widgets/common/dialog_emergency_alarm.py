"""
高压紧急停电全局报警弹窗 - 最高优先级红色 Error 弹窗
"""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from ui.styles.themes import ThemeManager
from loguru import logger


class DialogEmergencyAlarm(QDialog):
    """高压紧急停电全局报警弹窗
    
    特点:
    1. 红色 Error 样式（最高优先级）
    2. 可在任意 page 显示（全局弹窗）
    3. 模态对话框（阻塞其他操作）
    4. 显示报警信息和操作提示
    """
    
    # 信号：用户确认报警
    alarm_confirmed = pyqtSignal()
    
    # 1. 初始化弹窗
    def __init__(self, alarm_data: dict = None, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        self.alarm_data = alarm_data or {}
        
        self.setWindowTitle("高压紧急停电报警")
        self.setModal(True)  # 模态对话框
        self.setFixedSize(600, 300)
        
        # 设置窗口标志（最高优先级，始终置顶）
        self.setWindowFlags(
            Qt.WindowType.Dialog | 
            Qt.WindowType.WindowStaysOnTopHint |  # 始终置顶
            Qt.WindowType.CustomizeWindowHint | 
            Qt.WindowType.WindowTitleHint
        )
        
        self.init_ui()
        self.apply_styles()
        
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
    
    # 2. 初始化 UI
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 32, 32, 32)
        main_layout.setSpacing(24)
        
        # 标题区域（红色警告图标 + 标题）
        title_layout = QHBoxLayout()
        title_layout.setSpacing(16)
        
        # 警告图标（使用大号红色文字）
        icon_label = QLabel("⚠")
        icon_label.setObjectName("alarmIcon")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont("Microsoft YaHei", 48)
        font.setBold(True)
        icon_label.setFont(font)
        title_layout.addWidget(icon_label)
        
        # 标题文字
        title_label = QLabel("高压紧急停电")
        title_label.setObjectName("alarmTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        title_layout.addWidget(title_label, 1)
        
        main_layout.addLayout(title_layout)
        
        # 分隔线
        separator = QLabel()
        separator.setObjectName("separator")
        separator.setFixedHeight(2)
        main_layout.addWidget(separator)
        
        # 报警信息
        message_label = QLabel("高压已紧急停电，请确保手动操作电极，并重新送电")
        message_label.setObjectName("alarmMessage")
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        main_layout.addWidget(message_label)
        
        # 详细信息（如果有）
        if self.alarm_data:
            arc_limit = self.alarm_data.get('arc_limit', 0)
            delay_ms = self.alarm_data.get('delay_ms', 0)
            
            detail_text = f"弧流上限: {arc_limit} A  |  消抖时间: {delay_ms} ms"
            
            detail_label = QLabel(detail_text)
            detail_label.setObjectName("alarmDetail")
            detail_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            main_layout.addWidget(detail_label)
        
        main_layout.addStretch()
        
        # 底部按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        button_layout.addStretch()
        
        # 确认按钮（红色）
        confirm_btn = QPushButton("我已知晓")
        confirm_btn.setObjectName("confirmBtn")
        confirm_btn.setFixedSize(120, 40)
        confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        confirm_btn.clicked.connect(self.on_confirm)
        button_layout.addWidget(confirm_btn)
        
        main_layout.addLayout(button_layout)
    
    # 3. 确认报警
    def on_confirm(self):
        """用户确认报警"""
        logger.info("用户已确认高压紧急停电报警")
        self.alarm_confirmed.emit()
        self.accept()
    
    # 4. 应用样式（红色 Error 主题）
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        # 定义红色报警颜色
        ALARM_RED = "#FF3B30"  # 鲜艳的红色
        ALARM_RED_DARK = "#CC2E26"  # 深红色
        ALARM_BG = "#2D1B1B"  # 深红色背景
        ALARM_BORDER = "#FF6B60"  # 红色边框
        
        self.setStyleSheet(f"""
            QDialog {{
                background: {ALARM_BG};
                border: 3px solid {ALARM_RED};
                border-radius: 12px;
            }}
            
            QLabel#alarmIcon {{
                color: {ALARM_RED};
                border: none;
                background: transparent;
            }}
            
            QLabel#alarmTitle {{
                color: {ALARM_RED};
                font-size: 32px;
                font-weight: bold;
                border: none;
                background: transparent;
            }}
            
            QLabel#separator {{
                background: {ALARM_RED};
                border: none;
            }}
            
            QLabel#alarmMessage {{
                color: {colors.TEXT_PRIMARY};
                font-size: 18px;
                font-weight: bold;
                border: none;
                background: transparent;
                line-height: 1.6;
            }}
            
            QLabel#alarmDetail {{
                color: {colors.TEXT_SECONDARY};
                font-size: 14px;
                border: none;
                background: transparent;
            }}
            
            QPushButton#confirmBtn {{
                background: {ALARM_RED};
                color: white;
                border: 2px solid {ALARM_RED_DARK};
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton#confirmBtn:hover {{
                background: {ALARM_RED_DARK};
                border: 2px solid {ALARM_BORDER};
            }}
            QPushButton#confirmBtn:pressed {{
                background: {ALARM_RED_DARK};
                border: 2px solid {ALARM_RED};
            }}
        """)
    
    # 5. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()
    
    # 6. 重写关闭事件（防止用户直接关闭，必须点击确认）
    def closeEvent(self, event):
        """重写关闭事件，防止用户直接关闭"""
        # 只允许通过确认按钮关闭
        event.ignore()
        logger.warning("用户尝试直接关闭报警弹窗，已阻止")
    
    # 7. 重写键盘事件（禁用 ESC 键关闭）
    def keyPressEvent(self, event):
        """重写键盘事件，禁用 ESC 键"""
        if event.key() == Qt.Key.Key_Escape:
            # 禁用 ESC 键关闭
            event.ignore()
            logger.warning("用户尝试使用 ESC 键关闭报警弹窗，已阻止")
        else:
            super().keyPressEvent(event)


# ============================================================
# 便捷函数
# ============================================================

def show_emergency_alarm(alarm_data: dict = None, parent=None) -> DialogEmergencyAlarm:
    """显示高压紧急停电报警弹窗（便捷函数）
    
    Args:
        alarm_data: 报警数据字典
        parent: 父窗口
        
    Returns:
        DialogEmergencyAlarm 实例
    """
    dialog = DialogEmergencyAlarm(alarm_data, parent)
    dialog.exec()  # 模态显示
    return dialog

