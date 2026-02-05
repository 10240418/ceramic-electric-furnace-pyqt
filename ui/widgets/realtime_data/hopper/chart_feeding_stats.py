"""
投料统计折线图组件 - 显示投料重量随时间变化
"""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget
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
        
        # 保存原始数据范围（用于复原）
        self.original_x_range = None
        self.original_y_range = None
        
        self.init_ui()
        self.apply_styles()
        
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
    
    # 2. 初始化 UI
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 标题栏（包含标题和复原按钮）
        title_bar = QWidget()
        title_bar.setObjectName("chartTitleBar")
        title_bar.setFixedHeight(36)
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(12, 0, 12, 0)
        title_bar_layout.setSpacing(8)
        
        # 标题
        title_label = QLabel("投料累计(kg)")
        title_label.setObjectName("chartTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        title_bar_layout.addWidget(title_label)
        
        title_bar_layout.addStretch()
        
        # 复原按钮
        self.reset_btn = QPushButton("复原")
        self.reset_btn.setObjectName("resetBtn")
        self.reset_btn.setFixedHeight(24)
        self.reset_btn.setFixedWidth(60)
        self.reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.reset_btn.clicked.connect(self.reset_view)
        title_bar_layout.addWidget(self.reset_btn)
        
        main_layout.addWidget(title_bar)
        
        # 图表
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setObjectName("plotWidget")
        self.plot_widget.setBackground(None)
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        
        # 不设置坐标轴标签（删除左侧和底部的描述）
        self.plot_widget.setLabel('left', '')
        self.plot_widget.setLabel('bottom', '')
        
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
            x_data = [(t - base_time).total_seconds() / 3600.0 for t in self.timestamps]  # 转换为小时
            y_data = self.weights
            
            self.curve.setData(x_data, y_data)
            
            # 保存原始范围（用于复原）
            if x_data and y_data:
                self.original_x_range = (min(x_data), max(x_data))
                y_margin = (max(y_data) - min(y_data)) * 0.1 if max(y_data) != min(y_data) else 100
                self.original_y_range = (min(y_data) - y_margin, max(y_data) + y_margin)
            
            # 自定义 X 轴刻度标签
            if len(x_data) > 0:
                self.update_x_axis_labels()
    
    # 5.5 复原视图
    def reset_view(self):
        """复原图表视图到原始范围"""
        if self.original_x_range and self.original_y_range:
            # 添加一些边距
            x_margin = (self.original_x_range[1] - self.original_x_range[0]) * 0.05
            
            self.plot_widget.setXRange(
                self.original_x_range[0] - x_margin,
                self.original_x_range[1] + x_margin,
                padding=0
            )
            self.plot_widget.setYRange(
                self.original_y_range[0],
                self.original_y_range[1],
                padding=0
            )
    
    # 6. 更新 X 轴标签
    def update_x_axis_labels(self):
        """更新 X 轴时间标签"""
        if not self.timestamps:
            return
        
        # 创建时间刻度
        base_time = self.timestamps[0]
        ticks = []
        
        # 根据数据点数量决定显示多少个标签
        num_labels = min(8, len(self.timestamps))
        step = max(1, len(self.timestamps) // num_labels)
        
        for i in range(0, len(self.timestamps), step):
            hours = (self.timestamps[i] - base_time).total_seconds() / 3600.0
            time_str = self.timestamps[i].strftime("%m-%d %H:%M")
            ticks.append((hours, time_str))
        
        # 添加最后一个点
        if len(self.timestamps) > 1:
            last_hours = (self.timestamps[-1] - base_time).total_seconds() / 3600.0
            last_time_str = self.timestamps[-1].strftime("%m-%d %H:%M")
            if ticks[-1][0] != last_hours:
                ticks.append((last_hours, last_time_str))
        
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
        is_dark = self.theme_manager.is_dark_mode()
        
        # 复原按钮样式（参考历史曲线页面）
        if is_dark:
            btn_bg_normal = "rgba(42, 63, 95, 0.3)"
            btn_bg_hover = "rgba(42, 63, 95, 0.5)"
        else:
            btn_bg_normal = colors.BG_LIGHT
            btn_bg_hover = colors.BG_MEDIUM
        
        self.setStyleSheet(f"""
            QFrame#feedingStatsChart {{
                background: {colors.BG_MEDIUM};
                border: 1px solid {colors.BORDER_DARK};
                border-radius: 6px;
            }}
            
            QWidget#chartTitleBar {{
                background: {colors.BG_LIGHT};
                border: none;
                border-bottom: 1px solid {colors.BORDER_DARK};
                border-radius: 6px 6px 0 0;
            }}
            
            QLabel#chartTitle {{
                background: transparent;
                color: {colors.TEXT_PRIMARY};
                font-size: 14px;
                font-weight: bold;
                border: none;
            }}
            
            QPushButton#resetBtn {{
                background: {btn_bg_normal};
                color: {colors.TEXT_PRIMARY};
                border: 1px solid {colors.BORDER_DARK};
                border-radius: 4px;
                padding: 4px 12px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton#resetBtn:hover {{
                background: {btn_bg_hover};
                border: 1px solid {colors.GLOW_PRIMARY};
            }}
            QPushButton#resetBtn:pressed {{
                background: {colors.BG_MEDIUM};
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

