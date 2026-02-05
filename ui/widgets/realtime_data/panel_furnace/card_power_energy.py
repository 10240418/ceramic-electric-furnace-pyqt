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
        self.setFixedSize(180, 112)
        
        # 确保背景完全不透明
        self.setAutoFillBackground(True)
        
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
        
        # 总功率（左对齐）
        self.power_label = QLabel("总功率: 0.0kW")
        self.power_label.setObjectName("power_label")
        self.power_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.power_label)
        
        # 总能耗（左对齐）
        self.energy_label = QLabel("总能耗: 0.0kWh")
        self.energy_label.setObjectName("energy_label")
        self.energy_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.energy_label)
    
    # 3. 更新数据
    def update_data(self, power_kw: float, energy_kwh: float):
        """
        更新功率能耗数据
        
        Args:
            power_kw: 总功率（千瓦）
            energy_kwh: 总能耗（千瓦时）
        """
        # 标签和数值统一使用 26px
        self.power_label.setText(f'总功率: {power_kw:.1f}kW')
        self.energy_label.setText(f'总能耗: {energy_kwh:.1f}kWh')
    
    # 4. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        self.setStyleSheet(f"""
            QFrame#powerEnergyCard {{
                background: {colors.BG_LIGHT};
                border: 1px solid {colors.BORDER_GLOW};
                border-radius: 8px;
            }}
            
            QLabel#powerEnergyTitle {{
                color: {colors.TEXT_PRIMARY};
                font-size: 18px;
                font-weight: bold;
            }}
            
            QLabel#power_label {{
                color: {colors.GLOW_PRIMARY};
                font-size: 18px;
                font-weight: bold;
            }}
            
            QLabel#energy_label {{
                color: {colors.GLOW_PRIMARY};
                font-size: 18px;
                font-weight: bold;
            }}
        """)
    
    # 5. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()

