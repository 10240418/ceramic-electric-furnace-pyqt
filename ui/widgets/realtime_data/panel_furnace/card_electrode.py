"""
电极数据卡片组件 - 显示单个电极的深度、弧流、弧压
"""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from ui.styles.themes import ThemeManager


class CardElectrode(QFrame):
    """电极数据卡片组件"""
    
    # 1. 初始化组件
    def __init__(self, electrode_no: int, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        self.electrode_no = electrode_no
        self.setObjectName("electrodeCard")
        self.setFixedSize(180, 140)
        
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
        layout.setSpacing(8)
        
        # 标题（居中）
        self.title_label = QLabel(f"{self.electrode_no}#电极")
        self.title_label.setObjectName("electrodeTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)
        
        # 深度（左对齐）
        self.depth_label = QLabel("深度 0.000m")
        self.depth_label.setObjectName(f"depth_{self.electrode_no}")
        self.depth_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.depth_label)
        
        # 弧流（左对齐）
        self.current_label = QLabel("弧流 0A")
        self.current_label.setObjectName(f"current_{self.electrode_no}")
        self.current_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.current_label)
        
        # 弧压（左对齐）
        self.voltage_label = QLabel("弧压 0V")
        self.voltage_label.setObjectName(f"voltage_{self.electrode_no}")
        self.voltage_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.voltage_label)
    
    # 3. 更新电极数据
    def update_data(self, depth_mm: float, current_a: float, voltage_v: float):
        """
        更新电极数据
        
        Args:
            depth_mm: 深度（毫米）
            current_a: 弧流（安培）
            voltage_v: 弧压（伏特）
        """
        self.depth_label.setText(f"深度 {depth_mm:.3f}m")
        self.current_label.setText(f"弧流 {current_a:.0f}A")
        self.voltage_label.setText(f"弧压 {voltage_v:.0f}V")
    
    # 4. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        self.setStyleSheet(f"""
            QFrame#electrodeCard {{
                background: {colors.BG_LIGHT};
                border: 1px solid {colors.BORDER_GLOW};
                border-radius: 8px;
            }}
            
            QLabel#electrodeTitle {{
                color: {colors.GLOW_PRIMARY};
                font-size: 18px;
                font-weight: bold;
            }}
            
            QLabel[objectName^="depth_"] {{
                color: {colors.TEXT_PRIMARY};
                font-size: 16px;
                font-weight: bold;
            }}
            
            QLabel[objectName^="current_"] {{
                color: {colors.GLOW_ORANGE};
                font-size: 16px;
                font-weight: bold;
            }}
            
            QLabel[objectName^="voltage_"] {{
                color: {colors.GLOW_GREEN};
                font-size: 16px;
                font-weight: bold;
            }}
        """)
    
    # 5. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()

