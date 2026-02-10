"""
功率能耗卡片组件 - 显示总功率和总能耗
"""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from ui.styles.themes import ThemeManager


class CardPowerEnergy(QFrame):
    """功率能耗卡片组件"""
    
    # 1. 初始化组件
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        self.setObjectName("powerEnergyCard")
        self.setFixedSize(200, 112)
        
        # 确保背景完全不透明
        self.setAutoFillBackground(True)
        
        # 保存当前数值
        self._power_kw = 0.0
        self._energy_kwh = 0.0
        
        self.init_ui()
        self.apply_styles()
        
        # 提升到最上层
        self.raise_()
        
        # 监听主题变化
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
    
    # 2. 初始化 UI
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)
        
        # 标题（居中）
        self.title_label = QLabel("功率能耗")
        self.title_label.setObjectName("powerEnergyTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)
        
        # 总功率（左对齐，支持 HTML）
        self.power_label = QLabel()
        self.power_label.setObjectName("power_label")
        self.power_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.power_label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(self.power_label)
        
        # 总能耗（左对齐，支持 HTML）
        self.energy_label = QLabel()
        self.energy_label.setObjectName("energy_label")
        self.energy_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.energy_label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(self.energy_label)
    
    # 3. 刷新 HTML 文本（使用当前主题颜色）
    def _refresh_html_text(self):
        colors = self.theme_manager.get_colors()
        self.power_label.setText(
            f'<span style="color: {colors.TEXT_PRIMARY}; font-size: 16px; font-weight: bold;">功率: </span>'
            f'<span style="color: {colors.TEXT_ACCENT}; font-size: 16px; font-weight: bold;">{self._power_kw:.1f}kW</span>'
        )
        self.energy_label.setText(
            f'<span style="color: {colors.TEXT_PRIMARY}; font-size: 16px; font-weight: bold;">能耗: </span>'
            f'<span style="color: {colors.TEXT_ACCENT}; font-size: 16px; font-weight: bold;">{self._energy_kwh:.1f}kWh</span>'
        )
    
    # 4. 更新数据
    def update_data(self, power_kw: float, energy_kwh: float):
        self._power_kw = power_kw
        self._energy_kwh = energy_kwh
        self._refresh_html_text()
    
    # 5. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        # 将背景色转换为 RGBA 格式，设置 100% 不透明度
        from PyQt6.QtGui import QColor
        qcolor_bg = QColor(colors.BG_DEEP)
        bg_color_rgba = f"rgba({qcolor_bg.red()}, {qcolor_bg.green()}, {qcolor_bg.blue()}, 1.0)"
        
        self.setStyleSheet(f"""
            QFrame#powerEnergyCard {{
                background: {bg_color_rgba};
                border: 1px solid {colors.BORDER_DARK};
                border-radius: 8px;
            }}
            
            QLabel#powerEnergyTitle {{
                color: {colors.TEXT_PRIMARY};
                font-size: 18px;
                font-weight: bold;
            }}
        """)
        
        # 添加阴影效果（颜色为BORDER_DARK）
        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(4)
        shadow.setXOffset(2)
        shadow.setYOffset(2)
        shadow.setColor(QColor(colors.BORDER_DARK))
        self.setGraphicsEffect(shadow)
        
        # 刷新 HTML 文本颜色
        self._refresh_html_text()
    
    # 6. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()

