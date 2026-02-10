"""
主题切换组件 - 支持 9 套主题配色方案
"""
from PyQt6.QtWidgets import (
    QWidget, QPushButton, QGridLayout, QLabel, QVBoxLayout, QSizePolicy
)
from PyQt6.QtCore import Qt
from ui.styles.themes import ThemeManager, Theme, THEME_REGISTRY


class SwitchTheme(QWidget):
    """主题切换组件（网格布局，9 个主题按钮）"""
    
    # 1. 初始化组件
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        self.buttons: dict[Theme, QPushButton] = {}
        self.setup_ui()
        self.connect_signals()
        self.update_button_states()
    
    # 2. 设置 UI
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)
        
        # 标题
        self.title_label = QLabel("-- 主题切换 --")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.title_label)
        
        # 按钮网格 (3列 x 3行)
        grid = QGridLayout()
        grid.setSpacing(4)
        
        all_themes = list(Theme)
        for i, theme in enumerate(all_themes):
            entry = THEME_REGISTRY.get(theme.value, {})
            label = entry.get('label', theme.value)
            accent = entry.get('accent', '#888888')
            
            btn = QPushButton(label)
            btn.setFixedHeight(32)
            btn.setMinimumWidth(70)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn.setProperty('theme_value', theme)
            btn.setProperty('accent', accent)
            btn.clicked.connect(lambda checked, t=theme: self.switch_theme(t))
            
            row = i // 3
            col = i % 3
            grid.addWidget(btn, row, col)
            self.buttons[theme] = btn
        
        main_layout.addLayout(grid)
        self.apply_styles()
    
    # 3. 应用样式
    def apply_styles(self):
        tm = self.theme_manager
        
        self.title_label.setStyleSheet(f"""
            QLabel {{
                color: {tm.text_secondary()};
                font-size: 12px;
                background: transparent;
                border: none;
                padding: 2px 0;
            }}
        """)
        
        self.setStyleSheet(f"""
            SwitchTheme {{
                background-color: {tm.bg_medium()};
                border: 1px solid {tm.border_dark()};
                border-radius: 6px;
            }}
        """)
    
    # 4. 连接信号
    def connect_signals(self):
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
    
    # 5. 切换主题
    def switch_theme(self, theme: Theme):
        self.theme_manager.set_theme(theme)
    
    # 6. 主题变更回调
    def on_theme_changed(self, theme: Theme):
        self.apply_styles()
        self.update_button_states()
    
    # 7. 更新所有按钮样式（当前主题高亮）
    def update_button_states(self):
        tm = self.theme_manager
        current = tm.get_current_theme()
        
        for theme, btn in self.buttons.items():
            accent = btn.property('accent')
            
            if theme == current:
                # 当前主题: 高亮强调
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {accent};
                        color: {'#ffffff' if self._is_dark_accent(accent) else '#000000'};
                        border: 2px solid {accent};
                        border-radius: 4px;
                        font-size: 13px;
                        font-weight: 700;
                        padding: 2px 6px;
                    }}
                """)
            else:
                # 非当前主题: 低调显示
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {tm.text_secondary()};
                        border: 1px solid {tm.border_dark()};
                        border-radius: 4px;
                        font-size: 12px;
                        font-weight: 500;
                        padding: 2px 6px;
                    }}
                    QPushButton:hover {{
                        background-color: {accent};
                        color: {'#ffffff' if self._is_dark_accent(accent) else '#000000'};
                        border: 1px solid {accent};
                    }}
                """)
    
    # 8. 判断强调色是否偏深（决定文字用白色还是黑色）
    @staticmethod
    def _is_dark_accent(hex_color: str) -> bool:
        hex_color = hex_color.lstrip('#')
        if len(hex_color) < 6:
            return True
        r, g, b = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        # 亮度公式
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        return luminance < 160
