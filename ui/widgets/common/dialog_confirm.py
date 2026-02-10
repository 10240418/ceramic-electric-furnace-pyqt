"""
确认弹窗组件 - 统一样式的确认对话框
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from ui.styles.themes import ThemeManager


class DialogConfirm(QDialog):
    """确认弹窗"""
    
    confirmed = pyqtSignal()  # 确认信号
    
    # 1. 初始化弹窗
    def __init__(self, title: str, message: str, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedWidth(450)
        
        # 设置窗口标志，去除问号按钮
        self.setWindowFlags(
            Qt.WindowType.Dialog | 
            Qt.WindowType.CustomizeWindowHint | 
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.WindowCloseButtonHint
        )
        
        self.init_ui(title, message)
        self.apply_styles()
        
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
    
    # 2. 初始化 UI
    def init_ui(self, title: str, message: str):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)
        
        # 标题
        title_label = QLabel(title)
        title_label.setObjectName("dialogTitle")
        main_layout.addWidget(title_label)
        
        # 消息内容
        message_label = QLabel(message)
        message_label.setObjectName("messageLabel")
        message_label.setWordWrap(True)
        main_layout.addWidget(message_label)
        
        main_layout.addStretch()
        
        # 底部按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        button_layout.addStretch()
        
        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.setObjectName("cancelBtn")
        cancel_btn.setFixedWidth(100)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        # 确认按钮
        confirm_btn = QPushButton("确认")
        confirm_btn.setObjectName("confirmBtn")
        confirm_btn.setFixedWidth(100)
        confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        confirm_btn.clicked.connect(self.on_confirm)
        button_layout.addWidget(confirm_btn)
        
        main_layout.addLayout(button_layout)
    
    # 3. 确认
    def on_confirm(self):
        self.confirmed.emit()
        self.accept()
    
    # 4. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        self.setStyleSheet(f"""
            QDialog {{
                background: {colors.BG_DARK};
                border: 2px solid {colors.BORDER_DARK};
                border-radius: 8px;
            }}
            
            QLabel#dialogTitle {{
                color: {colors.GLOW_PRIMARY};
                font-size: 18px;
                font-weight: bold;
                border: none;
                background: transparent;
            }}
            
            QLabel#messageLabel {{
                color: {colors.TEXT_PRIMARY};
                font-size: 14px;
                line-height: 1.6;
                border: none;
                background: transparent;
            }}
            
            QPushButton#cancelBtn {{
                background: {colors.BG_MEDIUM};
                color: {colors.TEXT_PRIMARY};
                border: 1px solid {colors.BORDER_DARK};
                border-radius: 4px;
                padding: 8px 20px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton#cancelBtn:hover {{
                background: {colors.BG_LIGHT};
                border: 1px solid {colors.BORDER_MEDIUM};
            }}
            QPushButton#cancelBtn:pressed {{
                background: {colors.BG_DARK};
            }}
            
            QPushButton#confirmBtn {{
                background: {colors.BUTTON_PRIMARY_BG};
                color: {colors.BUTTON_PRIMARY_TEXT};
                border: 1px solid {colors.BORDER_DARK};
                border-radius: 4px;
                padding: 8px 20px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton#confirmBtn:hover {{
                background: {colors.BUTTON_PRIMARY_HOVER};
                border: 1px solid {colors.GLOW_PRIMARY};
            }}
            QPushButton#confirmBtn:pressed {{
                background: {colors.BG_MEDIUM};
            }}
        """)
    
    # 5. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()


class DialogError(QDialog):
    """错误弹窗"""
    
    # 1. 初始化弹窗
    def __init__(self, title: str, message: str, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedWidth(450)
        
        # 设置窗口标志，去除问号按钮
        self.setWindowFlags(
            Qt.WindowType.Dialog | 
            Qt.WindowType.CustomizeWindowHint | 
            Qt.WindowType.WindowTitleHint |
            Qt.WindowType.WindowCloseButtonHint
        )
        
        self.init_ui(title, message)
        self.apply_styles()
        
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
    
    # 2. 初始化 UI
    def init_ui(self, title: str, message: str):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)
        
        # 标题
        title_label = QLabel(title)
        title_label.setObjectName("dialogTitle")
        main_layout.addWidget(title_label)
        
        # 消息内容
        message_label = QLabel(message)
        message_label.setObjectName("messageLabel")
        message_label.setWordWrap(True)
        main_layout.addWidget(message_label)
        
        main_layout.addStretch()
        
        # 底部按钮
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        button_layout.addStretch()
        
        # 确认按钮
        confirm_btn = QPushButton("确认")
        confirm_btn.setObjectName("confirmBtn")
        confirm_btn.setFixedWidth(100)
        confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        confirm_btn.clicked.connect(self.accept)
        button_layout.addWidget(confirm_btn)
        
        main_layout.addLayout(button_layout)
    
    # 3. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        self.setStyleSheet(f"""
            QDialog {{
                background: {colors.BG_DARK};
                border: 2px solid {colors.STATUS_ALARM};
                border-radius: 8px;
            }}
            
            QLabel#dialogTitle {{
                color: {colors.STATUS_ALARM};
                font-size: 18px;
                font-weight: bold;
                border: none;
                background: transparent;
            }}
            
            QLabel#messageLabel {{
                color: {colors.TEXT_PRIMARY};
                font-size: 14px;
                line-height: 1.6;
                border: none;
                background: transparent;
            }}
            
            QPushButton#confirmBtn {{
                background: {colors.STATUS_ALARM}33;
                color: {colors.STATUS_ALARM};
                border: 1px solid {colors.STATUS_ALARM};
                border-radius: 4px;
                padding: 8px 20px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton#confirmBtn:hover {{
                background: {colors.STATUS_ALARM}4D;
                border: 1px solid {colors.STATUS_ALARM};
            }}
            QPushButton#confirmBtn:pressed {{
                background: {colors.STATUS_ALARM}66;
            }}
        """)
    
    # 4. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()

