"""
料仓卡片组件 - 显示料仓重量和投料统计
"""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal
from ui.styles.themes import ThemeManager


class CardHopper(QFrame):
    """料仓卡片组件"""
    
    # 信号：点击查看详情按钮
    detail_clicked = pyqtSignal()
    
    # 1. 初始化卡片
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        self.setObjectName("hopperCard")
        
        # 数据
        self.hopper_weight = 0.0
        self.feeding_total = 0.0
        self.upper_limit = 5000.0
        self.is_feeding = False
        
        self.init_ui()
        self.apply_styles()
        
        # 监听主题变化
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
    
    # 2. 初始化 UI
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)
        
        # 顶部：标题栏（料仓文字 + 查看详情按钮）
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)
        
        # 标题
        title_label = QLabel("料仓")
        title_label.setObjectName("hopperTitle")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # 查看详情按钮（距离父容器右边8px）
        self.detail_btn = QPushButton("查看详情")
        self.detail_btn.setObjectName("hopperDetailBtn")
        self.detail_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.detail_btn.clicked.connect(self.on_detail_clicked)
        header_layout.addWidget(self.detail_btn)
        
        main_layout.addLayout(header_layout)
        
        # 中间：三个数据项（横向排列）
        data_layout = QHBoxLayout()
        data_layout.setContentsMargins(0, 0, 0, 0)
        data_layout.setSpacing(16)
        
        # 投料累计
        self.feeding_total_widget = self.create_data_item("投料累计", "0", "kg")
        data_layout.addWidget(self.feeding_total_widget, 1)
        
        # 料仓重量
        self.hopper_weight_widget = self.create_data_item("料仓重量", "0", "kg")
        data_layout.addWidget(self.hopper_weight_widget, 1)
        
        # 料仓上限
        self.upper_limit_widget = self.create_data_item("料仓上限", "5000", "kg")
        data_layout.addWidget(self.upper_limit_widget, 1)
        
        main_layout.addLayout(data_layout)
        
        # 底部：投料状态
        self.status_label = QLabel("投料状态: 未投料")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFixedHeight(32)
        main_layout.addWidget(self.status_label)
    
    # 3. 创建数据项
    def create_data_item(self, label: str, value: str, unit: str) -> QFrame:
        item_frame = QFrame()
        item_frame.setObjectName("hopperDataItem")
        
        item_layout = QVBoxLayout(item_frame)
        item_layout.setContentsMargins(8, 8, 8, 8)
        item_layout.setSpacing(4)
        
        # 标签
        label_widget = QLabel(label)
        label_widget.setObjectName("dataLabel")
        label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        item_layout.addWidget(label_widget)
        
        # 数值 + 单位
        value_layout = QHBoxLayout()
        value_layout.setContentsMargins(0, 0, 0, 0)
        value_layout.setSpacing(4)
        value_layout.addStretch()
        
        value_label = QLabel(value)
        value_label.setObjectName("dataValue")
        value_layout.addWidget(value_label)
        
        unit_label = QLabel(unit)
        unit_label.setObjectName("dataUnit")
        value_layout.addWidget(unit_label)
        
        value_layout.addStretch()
        item_layout.addLayout(value_layout)
        
        return item_frame
    
    # 4. 更新数据
    def update_data(self, hopper_weight: float, feeding_total: float, 
                    upper_limit: float, is_feeding: bool = False):
        """
        更新料仓数据
        
        Args:
            hopper_weight: 料仓重量（kg）
            feeding_total: 投料累计（kg）
            upper_limit: 料仓上限（kg）
            is_feeding: 是否正在投料
        """
        self.hopper_weight = hopper_weight
        self.feeding_total = feeding_total
        self.upper_limit = upper_limit
        self.is_feeding = is_feeding
        
        # 更新投料累计
        feeding_value_label = self.feeding_total_widget.findChild(QLabel, "dataValue")
        if feeding_value_label:
            feeding_value_label.setText(str(int(feeding_total)))
        
        # 更新料仓重量
        weight_value_label = self.hopper_weight_widget.findChild(QLabel, "dataValue")
        if weight_value_label:
            weight_value_label.setText(str(int(hopper_weight)))
        
        # 更新料仓上限
        limit_value_label = self.upper_limit_widget.findChild(QLabel, "dataValue")
        if limit_value_label:
            limit_value_label.setText(str(int(upper_limit)))
        
        # 更新投料状态
        status_text = "投料状态: 投料中" if is_feeding else "投料状态: 未投料"
        self.status_label.setText(status_text)
        
        # 根据状态改变颜色
        colors = self.theme_manager.get_colors()
        if is_feeding:
            self.status_label.setStyleSheet(f"""
                QLabel#statusLabel {{
                    background: {colors.BG_MEDIUM};
                    color: {colors.GLOW_PRIMARY};
                    font-size: 14px;
                    font-weight: bold;
                    border: 1px solid {colors.BORDER_GLOW};
                    border-radius: 4px;
                }}
            """)
        else:
            self.status_label.setStyleSheet(f"""
                QLabel#statusLabel {{
                    background: {colors.BG_MEDIUM};
                    color: {colors.TEXT_SECONDARY};
                    font-size: 14px;
                    font-weight: bold;
                    border: 1px solid {colors.BORDER_DARK};
                    border-radius: 4px;
                }}
            """)
    
    # 5. 点击查看详情按钮
    def on_detail_clicked(self):
        """点击查看详情按钮，发射信号"""
        self.detail_clicked.emit()
    
    # 6. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        self.setStyleSheet(f"""
            QFrame#hopperCard {{
                background: {colors.BG_LIGHT};
                border: 1px solid {colors.BORDER_GLOW};
                border-radius: 6px;
            }}
            
            QLabel#hopperTitle {{
                color: {colors.GLOW_PRIMARY};
                font-size: 18px;
                font-weight: bold;
                border: none;
                background: transparent;
            }}
            
            QPushButton#hopperDetailBtn {{
                background: {colors.BUTTON_PRIMARY_BG};
                color: {colors.BUTTON_PRIMARY_TEXT};
                border: 1px solid {colors.BORDER_GLOW};
                border-radius: 4px;
                padding: 6px 16px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton#hopperDetailBtn:hover {{
                background: {colors.BUTTON_PRIMARY_HOVER};
                border: 1px solid {colors.GLOW_PRIMARY};
            }}
            QPushButton#hopperDetailBtn:pressed {{
                background: {colors.BG_MEDIUM};
            }}
            
            QFrame#hopperDataItem {{
                background: {colors.BG_MEDIUM};
                border: 1px solid {colors.BORDER_DARK};
                border-radius: 4px;
            }}
            
            QLabel#dataLabel {{
                color: {colors.TEXT_SECONDARY};
                font-size: 14px;
                border: none;
                background: transparent;
            }}
            
            QLabel#dataValue {{
                color: {colors.GLOW_PRIMARY};
                font-size: 24px;
                font-weight: bold;
                font-family: "Roboto Mono";
                border: none;
                background: transparent;
            }}
            
            QLabel#dataUnit {{
                color: {colors.TEXT_SECONDARY};
                font-size: 16px;
                border: none;
                background: transparent;
            }}
            
            QLabel#statusLabel {{
                background: {colors.BG_MEDIUM};
                color: {colors.TEXT_SECONDARY};
                font-size: 14px;
                font-weight: bold;
                border: 1px solid {colors.BORDER_DARK};
                border-radius: 4px;
            }}
        """)
    
    # 7. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()
