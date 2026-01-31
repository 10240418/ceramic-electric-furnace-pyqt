"""
投料统计折线图组件 - 显示投料重量随时间变化
"""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from ui.styles.themes import ThemeManager
import pyqtgraph as pg
from datetime import datetime


class ChartFeedingStats(QFrame):
    """投料统计折线图组件"""
    
    # 1. 初始化组件
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        self.setObjectName("feedingStatsChart")
        
        self.timestamps = []
        self.weights = []
        
        self.init_ui()
        self.apply_styles()
        
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
    
    # 2. 初始化 UI
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 标题
        title_label = QLabel("投料统计")
        title_label.setObjectName("chartTitle")
        title_label.setFixedHeight(36)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 图表
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setObjectName("plotWidget")
        self.plot_widget.setBackground(None)
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        
        # 设置坐标轴标签
        self.plot_widget.setLabel('left', '重量', units='kg')
        self.plot_widget.setLabel('bottom', '时间')
        
        # 设置坐标轴颜色
        colors = self.theme_manager.get_colors()
        axis_color = colors.TEXT_SECONDARY
        self.plot_widget.getAxis('left').setPen(axis_color)
        self.plot_widget.getAxis('bottom').setPen(axis_color)
        self.plot_widget.getAxis('left').setTextPen(axis_color)
        self.plot_widget.getAxis('bottom').setTextPen(axis_color)
        
        # 创建曲线
        self.curve = self.plot_widget.plot(
            pen=pg.mkPen(color=colors.GLOW_PRIMARY, width=2),
            symbol='o',
            symbolSize=6,
            symbolBrush=colors.GLOW_PRIMARY
        )
        
        main_layout.addWidget(self.plot_widget)
    
    # 3. 添加数据点
    def add_data_point(self, timestamp: datetime, weight: float):
        """
        添加数据点
        
        Args:
            timestamp: 时间戳
            weight: 重量（kg）
        """
        self.timestamps.append(timestamp)
        self.weights.append(weight)
        
        self.update_chart()
    
    # 4. 设置数据
    def set_data(self, timestamps: list, weights: list):
        """
        设置数据
        
        Args:
            timestamps: 时间戳列表
            weights: 重量列表（kg）
        """
        self.timestamps = timestamps
        self.weights = weights
        
        self.update_chart()
    
    # 5. 更新图表
    def update_chart(self):
        """更新图表显示"""
        if not self.timestamps or not self.weights:
            self.curve.setData([], [])
            return
        
        # 转换时间戳为相对秒数
        if len(self.timestamps) > 0:
            base_time = self.timestamps[0]
            x_data = [(t - base_time).total_seconds() for t in self.timestamps]
            y_data = self.weights
            
            self.curve.setData(x_data, y_data)
            
            # 自定义 X 轴刻度标签
            if len(x_data) > 0:
                self.update_x_axis_labels()
    
    # 6. 更新 X 轴标签
    def update_x_axis_labels(self):
        """更新 X 轴时间标签"""
        if not self.timestamps:
            return
        
        # 创建时间刻度
        base_time = self.timestamps[0]
        ticks = []
        
        # 每隔一定数量的点显示一个时间标签
        step = max(1, len(self.timestamps) // 5)
        
        for i in range(0, len(self.timestamps), step):
            seconds = (self.timestamps[i] - base_time).total_seconds()
            time_str = self.timestamps[i].strftime("%H:%M")
            ticks.append((seconds, time_str))
        
        # 设置自定义刻度
        axis = self.plot_widget.getAxis('bottom')
        axis.setTicks([ticks])
    
    # 7. 清空数据
    def clear_data(self):
        """清空所有数据"""
        self.timestamps.clear()
        self.weights.clear()
        self.curve.setData([], [])
    
    # 8. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        self.setStyleSheet(f"""
            QFrame#feedingStatsChart {{
                background: {colors.BG_MEDIUM};
                border: 1px solid {colors.BORDER_DARK};
                border-radius: 6px;
            }}
            
            QLabel#chartTitle {{
                background: {colors.BG_LIGHT};
                color: {colors.TEXT_PRIMARY};
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-bottom: 1px solid {colors.BORDER_DARK};
                border-radius: 6px 6px 0 0;
            }}
        """)
        
        # 更新图表颜色
        self.plot_widget.setBackground(colors.BG_DARK)
        
        axis_color = colors.TEXT_SECONDARY
        self.plot_widget.getAxis('left').setPen(axis_color)
        self.plot_widget.getAxis('bottom').setPen(axis_color)
        self.plot_widget.getAxis('left').setTextPen(axis_color)
        self.plot_widget.getAxis('bottom').setTextPen(axis_color)
        
        # 更新曲线颜色
        self.curve.setPen(pg.mkPen(color=colors.GLOW_PRIMARY, width=2))
        self.curve.setSymbolBrush(colors.GLOW_PRIMARY)
    
    # 9. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()

