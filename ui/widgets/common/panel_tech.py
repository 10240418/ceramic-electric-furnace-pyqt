"""
科技风格面板组件
"""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen
from ui.styles.themes import ThemeManager


class PanelTech(QFrame):
    """科技风格面板组件"""
    
    # 1. 初始化面板
    def __init__(self, title: str = "", parent=None):
        super().__init__(parent)
        self.title = title
        self.theme_manager = ThemeManager.instance()
        self.content_widget = None
        self.title_label = None
        self.init_ui()
        self.apply_styles()
        
        # 监听主题变化
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
    
    # 2. 初始化 UI
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)
        
        # 标题栏
        if self.title:
            self.title_layout = QHBoxLayout()
            self.title_layout.setContentsMargins(0, 0, 0, 0)
            
            self.title_label = QLabel(self.title)
            self.title_label.setObjectName("panelTechTitle")
            self.title_layout.addWidget(self.title_label)
            self.title_layout.addStretch()
            
            main_layout.addLayout(self.title_layout)
        
        # 内容区域
        self.content_widget = QWidget()
        self.content_widget.setObjectName("panelTechContent")
        main_layout.addWidget(self.content_widget)
    
    # 3. 设置内容布局
    def set_content_layout(self, layout):
        if self.content_widget.layout():
            old_layout = self.content_widget.layout()
            while old_layout.count():
                item = old_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
        self.content_widget.setLayout(layout)
    
    # 4. 添加内容组件
    def add_content_widget(self, widget):
        if not self.content_widget.layout():
            layout = QVBoxLayout(self.content_widget)
            layout.setContentsMargins(0, 0, 0, 0)
        self.content_widget.layout().addWidget(widget)
    
    # 5. 添加标题栏操作按钮
    def add_header_action(self, widget):
        if hasattr(self, 'title_layout'):
            self.title_layout.addWidget(widget)
    
    # 6. 应用样式
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
        
        # 标题样式
        if self.title_label:
            self.title_label.setStyleSheet(f"""
                QLabel#panelTechTitle {{
                    color: {colors.GLOW_PRIMARY};
                    font-size: 18px;
                    font-weight: bold;
                    border: none;
                    background: transparent;
                }}
            """)
        
        # 内容区域样式
        if self.content_widget:
            self.content_widget.setStyleSheet(f"""
                QWidget#panelTechContent {{
                    background: transparent;
                    border: none;
                }}
            """)
    
    # 7. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()


class PanelTechGlow(PanelTech):
    """带发光效果的科技风格面板"""
    
    # 1. 初始化面板
    def __init__(self, title: str = "", parent=None):
        super().__init__(title, parent)
        self.glow_enabled = True
    
    # 2. 应用样式（带发光效果）
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        # 面板样式（带阴影发光）
        self.setStyleSheet(f"""
            QFrame {{
                background: {colors.CARD_BG};
                border: 1px solid {colors.GLOW_PRIMARY};
                border-radius: 6px;
            }}
        """)
        
        # 标题样式
        if self.title_label:
            self.title_label.setStyleSheet(f"""
                QLabel#panelTechTitle {{
                    color: {colors.GLOW_PRIMARY};
                    font-size: 18px;
                    font-weight: bold;
                    border: none;
                    background: transparent;
                }}
            """)
        
        # 内容区域样式
        if self.content_widget:
            self.content_widget.setStyleSheet(f"""
                QWidget#panelTechContent {{
                    background: transparent;
                    border: none;
                }}
            """)
    
    # 3. 绘制发光效果
    def paintEvent(self, event):
        super().paintEvent(event)
        
        if not self.glow_enabled:
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        colors = self.theme_manager.get_colors()
        glow_color = QColor(colors.GLOW_PRIMARY)
        
        # 绘制外发光
        for i in range(3):
            alpha = int(30 - i * 10)
            glow_color.setAlpha(alpha)
            pen = QPen(glow_color, 2 + i)
            painter.setPen(pen)
            painter.drawRoundedRect(
                self.rect().adjusted(i, i, -i, -i),
                12 - i, 12 - i
            )

