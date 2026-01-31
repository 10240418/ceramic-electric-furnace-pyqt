"""
电炉背景面板组件 - 带背景图的右侧面板，包含炉次信息栏、电极卡片和功率能耗卡片
"""
from PyQt6.QtWidgets import QFrame, QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QPainter
from pathlib import Path
from ui.styles.themes import ThemeManager
from ui.widgets.realtime_data.panel_furnace.bar_batch_info import BarBatchInfo
from ui.widgets.realtime_data.panel_furnace.card_electrode import CardElectrode
from ui.widgets.realtime_data.panel_furnace.card_power_energy import CardPowerEnergy


class PanelFurnaceBg(QFrame):
    """电炉背景面板组件"""
    
    # 1. 初始化组件
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        self.setObjectName("furnaceContainer")
        
        # 加载背景图
        self.bg_pixmap = None
        furnace_path = Path(__file__).parent.parent.parent.parent.parent / "assets" / "images" / "furnace.png"
        if furnace_path.exists():
            self.bg_pixmap = QPixmap(str(furnace_path))
        
        self.init_ui()
        self.apply_styles()
        
        # 监听主题变化
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
    
    # 2. 初始化 UI
    def init_ui(self):
        # 使用普通布局（不使用堆叠布局）
        content_layout = QVBoxLayout(self)
        content_layout.setContentsMargins(16, 0, 16, 16)  # 顶部 0px，左右 16px，底部 16px
        content_layout.setSpacing(8)
        
        # 顶部：炉次信息栏
        self.batch_info_bar = BarBatchInfo()
        content_layout.addWidget(self.batch_info_bar)
        
        # 中间：弹性空间 + 电极卡片
        content_layout.addStretch(1)
        
        # 电极卡片容器 (品字结构)
        electrode_container = QWidget()
        electrode_container.setStyleSheet("background: transparent;")
        electrode_layout = QVBoxLayout(electrode_container)
        electrode_layout.setContentsMargins(0, 0, 0, 0)
        electrode_layout.setSpacing(16)
        
        # 上排：1# 和 2# 电极
        top_row = QHBoxLayout()
        top_row.addStretch(1)
        self.electrode_card_1 = CardElectrode(1)
        top_row.addWidget(self.electrode_card_1)
        top_row.addSpacing(40)
        self.electrode_card_2 = CardElectrode(2)
        top_row.addWidget(self.electrode_card_2)
        top_row.addStretch(1)
        electrode_layout.addLayout(top_row)
        
        # 下排：3# 电极 (居中)
        bottom_row = QHBoxLayout()
        bottom_row.addStretch(1)
        self.electrode_card_3 = CardElectrode(3)
        bottom_row.addWidget(self.electrode_card_3)
        bottom_row.addStretch(1)
        electrode_layout.addLayout(bottom_row)
        
        content_layout.addWidget(electrode_container)
        
        # 底部：功率能耗卡片（右下角）
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch(1)
        self.power_energy_card = CardPowerEnergy()
        bottom_layout.addWidget(self.power_energy_card)
        content_layout.addLayout(bottom_layout)
    
    # 3. 绘制背景图（在所有组件之下）
    def paintEvent(self, event):
        # 先绘制背景图
        if self.bg_pixmap:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            
            # 横向拉长背景图：宽度设置为 900，高度保持 700
            scaled_pixmap = self.bg_pixmap.scaled(
                900, 700,
                Qt.AspectRatioMode.IgnoreAspectRatio,  # 忽略宽高比，横向拉长
                Qt.TransformationMode.SmoothTransformation
            )
            
            x = (self.width() - scaled_pixmap.width()) // 2
            y = (self.height() - scaled_pixmap.height()) // 2
            
            # 设置透明度，让背景图更亮（降低不透明度）
            painter.setOpacity(0.7)  # 70% 不透明度，让背景图更亮
            painter.drawPixmap(x, y, scaled_pixmap)
            painter.setOpacity(1.0)  # 恢复完全不透明，用于绘制其他内容
        
        # 调用父类的 paintEvent 绘制边框等
        super().paintEvent(event)
    
    # 4. 更新炉次信息
    def update_batch_info(self, batch_no: str, start_time: str, run_duration: str):
        """更新炉次信息"""
        # 判断是否正在冶炼（batch_no 不为空表示正在冶炼）
        is_smelting = bool(batch_no)
        self.batch_info_bar.set_smelting_state(is_smelting, batch_no, start_time, run_duration)
    
    # 5. 更新电极数据
    def update_electrode(self, electrode_no: int, depth_mm: float, current_a: float, voltage_v: float):
        """
        更新指定电极的数据
        
        Args:
            electrode_no: 电极编号 (1-3)
            depth_mm: 深度（毫米）
            current_a: 弧流（安培）
            voltage_v: 弧压（伏特）
        """
        if electrode_no == 1:
            self.electrode_card_1.update_data(depth_mm, current_a, voltage_v)
        elif electrode_no == 2:
            self.electrode_card_2.update_data(depth_mm, current_a, voltage_v)
        elif electrode_no == 3:
            self.electrode_card_3.update_data(depth_mm, current_a, voltage_v)
    
    # 6. 批量更新所有电极
    def update_all_electrodes(self, electrodes_data: list):
        """
        批量更新所有电极数据
        
        Args:
            electrodes_data: 电极数据列表，每项包含 {'depth_mm': float, 'current_a': float, 'voltage_v': float}
        """
        for i, data in enumerate(electrodes_data):
            if i < 3:
                self.update_electrode(i + 1, data['depth_mm'], data['current_a'], data['voltage_v'])
    
    # 7. 更新功率能耗
    def update_power_energy(self, power_kw: float, energy_kwh: float):
        """
        更新功率能耗数据
        
        Args:
            power_kw: 总功率（千瓦）
            energy_kwh: 总能耗（千瓦时）
        """
        self.power_energy_card.update_data(power_kw, energy_kwh)
    
    # 8. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        self.setStyleSheet(f"""
            QFrame#furnaceContainer {{
                background: {colors.BG_DARK};
                border: 1px solid {colors.BORDER_DARK};
                border-radius: 8px;
            }}
        """)
    
    # 9. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()

