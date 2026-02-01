"""
自定义消息对话框 - 无系统标题栏，适配主题颜色
"""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt
from ui.styles.themes import ThemeManager


class DialogMessage(QDialog):
    """自定义消息对话框"""
    
    # 1. 初始化对话框
    def __init__(self, title: str, message: str, dialog_type: str = "error", parent=None):
        """
        Args:
            title: 标题
            message: 消息内容
            dialog_type: 对话框类型 ("error", "warning", "info", "success")
            parent: 父组件
        """
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        self.dialog_type = dialog_type
        
        self.setModal(True)
        
        # 去除系统标题栏
        self.setWindowFlags(
            Qt.WindowType.Dialog | 
            Qt.WindowType.FramelessWindowHint
        )
        
        self.title_text = title
        self.message_text = message
        
        self.init_ui()
        self.apply_styles()
        
        # 监听主题变化
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
    
    # 2. 初始化 UI
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 顶部标题栏（带关闭按钮）
        title_bar = QHBoxLayout()
        title_bar.setContentsMargins(20, 16, 16, 16)
        title_bar.setSpacing(12)
        
        # 图标
        icon_map = {
            "error": "❌",
            "warning": "⚠️",
            "info": "ℹ️",
            "success": "✅"
        }
        icon_label = QLabel(icon_map.get(self.dialog_type, "ℹ️"))
        icon_label.setObjectName("iconLabel")
        title_bar.addWidget(icon_label)
        
        # 标题
        title_label = QLabel(self.title_text)
        title_label.setObjectName("titleLabel")
        title_bar.addWidget(title_label)
        
        title_bar.addStretch()
        
        # 关闭按钮
        btn_close = QPushButton("×")
        btn_close.setObjectName("btnClose")
        btn_close.setFixedSize(32, 32)
        btn_close.clicked.connect(self.close)
        title_bar.addWidget(btn_close)
        
        main_layout.addLayout(title_bar)
        
        # 分隔线
        separator = QLabel()
        separator.setObjectName("separator")
        separator.setFixedHeight(1)
        main_layout.addWidget(separator)
        
        # 消息内容
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(20)
        
        message_label = QLabel(self.message_text)
        message_label.setObjectName("messageLabel")
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        content_layout.addWidget(message_label)
        
        # 确定按钮
        btn_ok = QPushButton("确定")
        btn_ok.setObjectName("btnOk")
        btn_ok.setFixedHeight(44)
        btn_ok.clicked.connect(self.accept)
        content_layout.addWidget(btn_ok)
        
        main_layout.addLayout(content_layout)
    
    # 3. 显示事件（调整窗口大小和位置）
    def showEvent(self, event):
        super().showEvent(event)
        
        # 固定窗口大小
        self.setFixedSize(400, 200)
        
        # 居中显示
        if self.parent():
            parent_rect = self.parent().geometry()
            x = parent_rect.x() + (parent_rect.width() - 400) // 2
            y = parent_rect.y() + (parent_rect.height() - 200) // 2
            self.move(x, y)
    
    # 4. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        # 根据类型选择颜色
        type_colors = {
            "error": "#ff4444",
            "warning": "#ffaa00",
            "info": colors.GLOW_PRIMARY,
            "success": "#00cc66"
        }
        accent_color = type_colors.get(self.dialog_type, colors.GLOW_PRIMARY)
        
        self.setStyleSheet(f"""
            QDialog {{
                background: {colors.BG_DARK};
                border: 2px solid {accent_color};
                border-radius: 8px;
            }}
            
            QLabel#iconLabel {{
                font-size: 24px;
                border: none;
                background: transparent;
            }}
            
            QLabel#titleLabel {{
                color: {colors.TEXT_PRIMARY};
                font-size: 18px;
                font-weight: bold;
                border: none;
                background: transparent;
            }}
            
            QPushButton#btnClose {{
                background: transparent;
                color: {colors.TEXT_SECONDARY};
                border: none;
                border-radius: 4px;
                font-size: 24px;
                font-weight: bold;
            }}
            
            QPushButton#btnClose:hover {{
                background: {colors.BG_LIGHT};
                color: {colors.TEXT_PRIMARY};
            }}
            
            QPushButton#btnClose:pressed {{
                background: {colors.BG_MEDIUM};
            }}
            
            QLabel#separator {{
                background: {accent_color};
            }}
            
            QLabel#messageLabel {{
                color: {colors.TEXT_PRIMARY};
                font-size: 15px;
                border: none;
                background: transparent;
            }}
            
            QPushButton#btnOk {{
                background: {accent_color}33;
                color: {accent_color};
                border: 1px solid {accent_color};
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
            }}
            
            QPushButton#btnOk:hover {{
                background: {accent_color}4D;
            }}
            
            QPushButton#btnOk:pressed {{
                background: {accent_color}66;
            }}
        """)
    
    # 5. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()


# 6. 便捷方法
def show_error(parent, title: str, message: str):
    """显示错误对话框"""
    dialog = DialogMessage(title, message, "error", parent)
    dialog.exec()


def show_warning(parent, title: str, message: str):
    """显示警告对话框"""
    dialog = DialogMessage(title, message, "warning", parent)
    dialog.exec()


def show_info(parent, title: str, message: str):
    """显示信息对话框"""
    dialog = DialogMessage(title, message, "info", parent)
    dialog.exec()


def show_success(parent, title: str, message: str):
    """显示成功对话框"""
    dialog = DialogMessage(title, message, "success", parent)
    dialog.exec()

