"""
主题切换组件 - 切换深色/浅色主题
"""
from PyQt6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from ui.styles.themes import ThemeManager, Theme


class SwitchTheme(QWidget):
    """主题切换组件"""
    
    # 1. 初始化组件
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        self.setup_ui()
        self.connect_signals()
        self.update_button_states()
    
    # 2. 设置 UI
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 深色主题按钮
        self.dark_button = QPushButton("🌙 深色")
        self.dark_button.setFixedSize(100, 36)
        self.dark_button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # 浅色主题按钮
        self.light_button = QPushButton("☀️ 浅色")
        self.light_button.setFixedSize(100, 36)
        self.light_button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout.addWidget(self.dark_button)
        layout.addWidget(self.light_button)
        
        # 应用样式
        self.apply_styles()
    
    # 3. 应用样式
    def apply_styles(self):
        tm = self.theme_manager
        
        # 容器样式
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {tm.bg_medium()};
                border: 1px solid {tm.border_dark()};
                border-radius: 4px;
            }}
        """)
        
        # 按钮基础样式
        button_style = f"""
            QPushButton {{
                background-color: transparent;
                color: {tm.text_secondary()};
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: 500;
            }}
            
            QPushButton:hover {{
                background-color: {tm.bg_light()};
                color: {tm.text_primary()};
            }}
        """
        
        self.dark_button.setStyleSheet(button_style)
        self.light_button.setStyleSheet(button_style)
    
    # 4. 连接信号
    def connect_signals(self):
        self.dark_button.clicked.connect(lambda: self.switch_theme(Theme.DARK))
        self.light_button.clicked.connect(lambda: self.switch_theme(Theme.LIGHT))
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
    
    # 5. 切换主题
    def switch_theme(self, theme: Theme):
        self.theme_manager.set_theme(theme)
    
    # 6. 主题变更回调
    def on_theme_changed(self, theme: Theme):
        self.update_button_states()
        self.apply_styles()
    
    # 7. 更新按钮状态
    def update_button_states(self):
        tm = self.theme_manager
        is_dark = tm.is_dark_mode()
        
        # 更新深色按钮
        if is_dark:
            self.dark_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {tm.border_glow()};
                    color: {tm.bg_dark()};
                    border: none;
                    border-radius: 4px;
                    font-size: 14px;
                    font-weight: 600;
                }}
            """)
        else:
            self.dark_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {tm.text_secondary()};
                    border: none;
                    border-radius: 4px;
                    font-size: 14px;
                    font-weight: 500;
                }}
                
                QPushButton:hover {{
                    background-color: {tm.bg_light()};
                    color: {tm.text_primary()};
                }}
            """)
        
        # 更新浅色按钮
        if not is_dark:
            self.light_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {tm.border_glow()};
                    color: {tm.bg_dark()};
                    border: none;
                    border-radius: 4px;
                    font-size: 14px;
                    font-weight: 600;
                }}
            """)
        else:
            self.light_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: {tm.text_secondary()};
                    border: none;
                    border-radius: 4px;
                    font-size: 14px;
                    font-weight: 500;
                }}
                
                QPushButton:hover {{
                    background-color: {tm.bg_light()};
                    color: {tm.text_primary()};
                }}
            """)
