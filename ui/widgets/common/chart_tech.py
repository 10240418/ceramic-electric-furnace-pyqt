"""
图表专用科技风格面板组件 - 内边距全部为0
"""
from PyQt6.QtWidgets import QFrame, QVBoxLayout
from ui.styles.themes import ThemeManager


class ChartTech(QFrame):
    """图表专用科技风格面板组件（内边距为0）"""
    
    # 1. 初始化面板
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        self.init_ui()
        self.apply_styles()
        
        # 监听主题变化
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
    
    # 2. 初始化 UI
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)  # 内边距全部为0
        main_layout.setSpacing(0)
    
    # 3. 设置内容布局
    def set_content_layout(self, layout):
        if self.layout().count() > 0:
            old_layout = self.layout()
            while old_layout.count():
                item = old_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        
        # 清空当前布局
        while self.layout().count():
            self.layout().takeAt(0)
        
        # 添加新布局的所有组件
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    self.layout().addWidget(item.widget())
                elif item.layout():
                    self.layout().addLayout(item.layout())
    
    # 4. 添加内容组件
    def add_content_widget(self, widget):
        self.layout().addWidget(widget)
    
    # 5. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        # 面板样式（使用科技风亮色边框）
        self.setStyleSheet(f"""
            QFrame {{
                background: {colors.CARD_BG};
                border: 1px solid {colors.BORDER_GLOW};
                border-radius: 6px;
            }}
        """)
    
    # 6. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()

