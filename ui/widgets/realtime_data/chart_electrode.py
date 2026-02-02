"""
电极电流柱状图组件 - 显示三个电极的设定值和实际值对比
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QColor, QLinearGradient, QPen, QFont
from ui.styles.themes import ThemeManager


class ElectrodeData:
    """电极数据模型"""
    
    def __init__(self, name: str, set_value: float, actual_value: float):
        self.name = name
        self.set_value = set_value
        self.actual_value = actual_value


class ChartElectrode(QWidget):
    """电极电流柱状图组件"""
    
    # 1. 初始化组件
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        self.electrodes = [
            ElectrodeData("1#电极", 0, 0),
            ElectrodeData("2#电极", 0, 0),
            ElectrodeData("3#电极", 0, 0),
        ]
        self.deadzone_percent = 15.0  # 死区百分比，默认15%
        
        # 刷新间隔（毫秒）- 跟随轮询速度
        self._refresh_interval_ms = 200  # 默认 200ms (0.2s)
        
        self.init_ui()
        
        # 监听主题变化
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
        
        # 监听轮询速度变化
        from backend.config.polling_config import get_polling_config
        self.polling_config = get_polling_config()
        self.polling_config.register_callback(self.on_polling_speed_changed)
    
    # 2. 初始化 UI
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 0, 8, 2)  # 左右8px，上0px（减小顶部距离），下2px
        main_layout.setSpacing(2)  # 紧凑间距2px
        
        # 顶部：标题和图例
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(15, 0, 0, 0)  # 标题左边距15px（从30px减小到15px，对齐Y轴）
        
        # 标题：弧流(KA)
        title_label = QLabel("弧流(KA)")
        title_label.setObjectName("chartTitle")
        font = QFont("Microsoft YaHei", 14)  # 字号从18减小到14
        font.setBold(True)
        title_label.setFont(font)
        title_label.setContentsMargins(0, 0, 0, 0)
        top_layout.addWidget(title_label)
        
        top_layout.addStretch()
        
        # 图例
        self.legend_widget = self.create_legend()
        top_layout.addWidget(self.legend_widget)
        
        main_layout.addLayout(top_layout)
        
        # 图表主体
        self.chart_widget = ChartWidget(self)
        main_layout.addWidget(self.chart_widget, 1)
        
        self.apply_styles()
    
    # 3. 创建图例
    def create_legend(self) -> QWidget:
        legend = QFrame()
        legend.setObjectName("legend")
        
        layout = QHBoxLayout(legend)
        layout.setContentsMargins(4, 2, 4, 2)  # 减小边距
        layout.setSpacing(10)  # 减小间距
        
        # 死区显示
        deadzone_label = QLabel(f"死区: {int(self.deadzone_percent)}%")
        deadzone_label.setObjectName("deadzoneLabel")
        font = QFont("Microsoft YaHei", 14)  # 字号从12改为14
        deadzone_label.setFont(font)
        layout.addWidget(deadzone_label)
        
        # 设定值图例
        set_item = self.create_legend_item("设定值:", "set")
        layout.addWidget(set_item)
        
        # 实际值图例
        actual_item = self.create_legend_item("实际值:", "actual")
        layout.addWidget(actual_item)
        
        return legend
    
    # 4. 创建图例项
    def create_legend_item(self, text: str, item_type: str) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)  # 减小间距
        
        # 文字
        label = QLabel(text)
        label.setObjectName(f"legendLabel_{item_type}")
        font = QFont("Microsoft YaHei", 14)  # 字号从12改为14
        label.setFont(font)
        layout.addWidget(label)
        
        # 颜色块
        color_box = QFrame()
        color_box.setFixedSize(14, 10)  # 减小尺寸
        color_box.setObjectName(f"legendBox_{item_type}")
        layout.addWidget(color_box)
        
        return widget
    
    # 5. 更新数据
    def update_data(self, electrodes: list, deadzone_percent: float = 15.0):
        """更新电极数据
        
        Args:
            electrodes: 电极数据列表，每个元素包含 name, set_value, actual_value
                       例如: [
                           ElectrodeData("1#电极", 5978, 5980),
                           ElectrodeData("2#电极", 5978, 5975),
                           ElectrodeData("3#电极", 5978, 5982),
                       ]
            deadzone_percent: 死区百分比（默认15%）
        """
        self.electrodes = electrodes
        self.deadzone_percent = deadzone_percent
        
        # 更新死区显示
        deadzone_label = self.legend_widget.findChild(QLabel, "deadzoneLabel")
        if deadzone_label:
            deadzone_label.setText(f"死区: {int(deadzone_percent)}%")
        
        self.chart_widget.update()
    
    # 6. 从字典更新数据（便捷方法）
    def update_from_dict(self, data: dict):
        """从字典数据更新图表
        
        Args:
            data: 包含弧流数据的字典
                {
                    'arc_current': {'U': 5978, 'V': 5980, 'W': 5975},
                    'setpoints': {'U': 5978, 'V': 5978, 'W': 5978},
                    'manual_deadzone_percent': 10.0
                }
        """
        arc_current = data.get('arc_current', {})
        setpoints = data.get('setpoints', {})
        deadzone = data.get('manual_deadzone_percent', 15.0)
        
        # 构建电极数据列表
        electrodes = [
            ElectrodeData("1#电极", setpoints.get('U', 0), arc_current.get('U', 0)),
            ElectrodeData("2#电极", setpoints.get('V', 0), arc_current.get('V', 0)),
            ElectrodeData("3#电极", setpoints.get('W', 0), arc_current.get('W', 0)),
        ]
        
        self.update_data(electrodes, deadzone)
    
    # 6. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        # 标题样式
        title_label = self.findChild(QLabel, "chartTitle")
        if title_label:
            title_label.setStyleSheet(f"""
                QLabel {{
                    color: {colors.GLOW_PRIMARY};
                    background: transparent;
                    border: none;
                }}
            """)
        
        # 图例容器
        self.legend_widget.setStyleSheet(f"""
            QFrame#legend {{
                background: transparent;
                border: none;
            }}
        """)
        
        # 死区标签
        deadzone_label = self.legend_widget.findChild(QLabel, "deadzoneLabel")
        if deadzone_label:
            deadzone_label.setStyleSheet(f"""
                QLabel {{
                    color: {colors.TEXT_PRIMARY};
                    background: transparent;
                    border: none;
                }}
            """)
        
        # 设定值图例（适配主题配色）
        if self.theme_manager.is_dark_mode():
            set_color = "#00D4FF"  # 深色主题：青蓝色
        else:
            set_color = "#007663"  # 浅色主题：深绿色
            
        set_box = self.legend_widget.findChild(QFrame, "legendBox_set")
        if set_box:
            set_box.setStyleSheet(f"""
                QFrame {{
                    background: {set_color};
                    border: 1px solid {set_color};
                    border-radius: 2px;
                }}
            """)
        
        set_label = self.legend_widget.findChild(QLabel, "legendLabel_set")
        if set_label:
            set_label.setStyleSheet(f"""
                QLabel {{
                    color: {colors.TEXT_PRIMARY};
                    background: transparent;
                    border: none;
                }}
            """)
        
        # 实际值图例（适配主题配色）
        if self.theme_manager.is_dark_mode():
            actual_color = "#FFB84D"  # 深色主题：橙黄色
        else:
            actual_color = "#D4A017"  # 浅色主题：金黄色
            
        actual_box = self.legend_widget.findChild(QFrame, "legendBox_actual")
        if actual_box:
            actual_box.setStyleSheet(f"""
                QFrame {{
                    background: {actual_color};
                    border: 1px solid {actual_color};
                    border-radius: 2px;
                }}
            """)
        
        actual_label = self.legend_widget.findChild(QLabel, "legendLabel_actual")
        if actual_label:
            actual_label.setStyleSheet(f"""
                QLabel {{
                    color: {colors.TEXT_PRIMARY};
                    background: transparent;
                    border: none;
                }}
            """)
    
    # 7. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()
        self.chart_widget.update()
    
    # 8. 轮询速度变化时更新刷新间隔
    def on_polling_speed_changed(self, speed):
        """轮询速度变化回调
        
        Args:
            speed: "0.2s" 或 "0.5s"
        """
        if speed == "0.2s":
            self._refresh_interval_ms = 200  # 0.2s = 200ms
        else:
            self._refresh_interval_ms = 500  # 0.5s = 500ms
        
        print(f" 图表刷新间隔已更新: {self._refresh_interval_ms}ms")
    
    # 9. 获取刷新间隔
    def get_refresh_interval_ms(self) -> int:
        """获取刷新间隔（毫秒）
        
        Returns:
            200 或 500
        """
        return self._refresh_interval_ms


class ChartWidget(QWidget):
    """图表绘制组件"""
    
    # 1. 初始化
    def __init__(self, parent: ChartElectrode):
        super().__init__(parent)
        self.chart = parent
        self.theme_manager = ThemeManager.instance()
        # 移除最小高度限制，让 stretch 参数生效
        # self.setMinimumHeight(250)
    
    # 2. 绘制图表
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        colors = self.theme_manager.get_colors()
        
        # 固定Y轴范围：1-8 (KA)
        min_value = 0
        max_value = 8000  # 8KA = 8000A
        
        # 绘制区域（紧凑布局，Y轴12px，X轴标签高度18px）
        y_axis_width = 12  # Y轴刻度宽度（从25px减小到12px）
        x_axis_height = 18  # X轴高度（改为18px）
        chart_rect = QRectF(
            y_axis_width,  # 左边距12px（为Y轴刻度留空间）
            5,  # 顶部边距5px（紧凑）
            self.width() - y_axis_width - 10,  # 右边距10px（紧凑）
            self.height() - x_axis_height - 5  # 底部留18px给X轴标签
        )
        
        # 绘制Y轴和X轴
        self.draw_axes(painter, chart_rect, colors)
        
        # 绘制Y轴刻度（1-8）
        self.draw_y_axis(painter, min_value, max_value, y_axis_width, chart_rect, colors)
        
        # 绘制上下限线（根据死区计算）
        self.draw_limit_lines(painter, chart_rect, min_value, max_value, colors)
        
        # 绘制柱状图（6根柱子：3个电极 x 2种值）
        self.draw_bars(painter, chart_rect, min_value, max_value, colors)
        
        # 绘制X轴标签（1#电极、2#电极、3#电极）
        self.draw_x_labels(painter, chart_rect, colors)
    
    # 3. 绘制坐标轴（带箭头）
    def draw_axes(self, painter: QPainter, chart_rect: QRectF, colors):
        painter.setPen(QPen(QColor(colors.BORDER_DARK), 2))
        
        # Y轴
        painter.drawLine(
            int(chart_rect.left()), 
            int(chart_rect.top()), 
            int(chart_rect.left()), 
            int(chart_rect.bottom())
        )
        
        # Y轴箭头（三角形）
        arrow_size = 8
        y_arrow_points = [
            (chart_rect.left(), chart_rect.top()),
            (chart_rect.left() - arrow_size / 2, chart_rect.top() + arrow_size),
            (chart_rect.left() + arrow_size / 2, chart_rect.top() + arrow_size),
        ]
        painter.setBrush(QColor(colors.BORDER_DARK))
        from PyQt6.QtGui import QPolygonF
        from PyQt6.QtCore import QPointF
        painter.drawPolygon(QPolygonF([QPointF(x, y) for x, y in y_arrow_points]))
        
        # X轴
        painter.drawLine(
            int(chart_rect.left()), 
            int(chart_rect.bottom()), 
            int(chart_rect.right()), 
            int(chart_rect.bottom())
        )
        
        # X轴箭头（三角形）
        x_arrow_points = [
            (chart_rect.right(), chart_rect.bottom()),
            (chart_rect.right() - arrow_size, chart_rect.bottom() - arrow_size / 2),
            (chart_rect.right() - arrow_size, chart_rect.bottom() + arrow_size / 2),
        ]
        painter.drawPolygon(QPolygonF([QPointF(x, y) for x, y in x_arrow_points]))
    
    # 4. 绘制Y轴刻度（1-8 KA）
    def draw_y_axis(self, painter: QPainter, min_value: float, max_value: float, width: int, chart_rect: QRectF, colors):
        painter.setPen(QColor(colors.TEXT_PRIMARY))
        font = QFont("Microsoft YaHei", 11)  # 字号从12减小到11
        painter.setFont(font)
        
        # 9个刻度：0, 1, 2, 3, 4, 5, 6, 7, 8
        for i in range(9):
            value = i  # KA
            value_a = i * 1000  # 转换为A
            ratio = value_a / max_value
            y = chart_rect.bottom() - chart_rect.height() * ratio
            
            # 绘制刻度线
            painter.setPen(QPen(QColor(colors.BORDER_DARK), 1))
            painter.drawLine(
                int(chart_rect.left() - 5), 
                int(y), 
                int(chart_rect.left()), 
                int(y)
            )
            
            # 绘制刻度值（在Y轴左侧）
            painter.setPen(QColor(colors.TEXT_PRIMARY))
            text = f"{value}"
            # 刻度值绘制区域：从左边缘到Y轴左侧（Y轴左移后空间更小）
            painter.drawText(
                QRectF(0, y - 10, chart_rect.left() - 5, 20), 
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, 
                text
            )
    
    # 5. 绘制上下限线（根据死区计算，不显示数值标签）
    def draw_limit_lines(self, painter: QPainter, chart_rect: QRectF, min_value: float, max_value: float, colors):
        value_range = max_value - min_value
        if value_range <= 0:
            return
        
        # 计算所有电极的上下限
        all_upper_limits = []
        all_lower_limits = []
        
        for electrode in self.chart.electrodes:
            if electrode.set_value > 0:
                upper = electrode.set_value * (1 + self.chart.deadzone_percent / 100.0)
                lower = electrode.set_value * (1 - self.chart.deadzone_percent / 100.0)
                all_upper_limits.append(upper)
                all_lower_limits.append(lower)
        
        if not all_upper_limits:
            return
        
        # 取最大值的上限和最小值的下限
        max_upper_limit = max(all_upper_limits)
        min_lower_limit = min(all_lower_limits)
        
        # 上限线颜色（适配主题）
        upper_color = QColor(colors.STATUS_ALARM) if hasattr(colors, 'STATUS_ALARM') else QColor("#FF4444")
        
        # 绘制上限线
        upper_ratio = (max_upper_limit - min_value) / value_range
        upper_y = chart_rect.bottom() - chart_rect.height() * upper_ratio
        
        painter.setPen(QPen(upper_color, 2, Qt.PenStyle.DashLine))
        painter.drawLine(int(chart_rect.left()), int(upper_y), int(chart_rect.right()), int(upper_y))
        
        # 下限线颜色（适配主题）
        lower_color = QColor(colors.STATUS_INFO) if hasattr(colors, 'STATUS_INFO') else QColor("#4444FF")
        
        # 绘制下限线
        lower_ratio = (min_lower_limit - min_value) / value_range
        lower_y = chart_rect.bottom() - chart_rect.height() * lower_ratio
        
        painter.setPen(QPen(lower_color, 2, Qt.PenStyle.DashLine))
        painter.drawLine(int(chart_rect.left()), int(lower_y), int(chart_rect.right()), int(lower_y))
    
    # 6. 绘制柱状图（6根柱子）
    def draw_bars(self, painter: QPainter, chart_rect: QRectF, min_value: float, max_value: float, colors):
        electrode_count = len(self.chart.electrodes)
        if electrode_count == 0:
            return
        
        value_range = max_value - min_value
        if value_range <= 0:
            return
        
        # 计算每个电极组的宽度
        group_width = chart_rect.width() / electrode_count
        bar_width = 33  # 单个柱子宽度（增加3px）
        spacing = 16  # 柱子间距（增加8px）
        
        # 配色方案（适配主题）
        if self.theme_manager.is_dark_mode():
            # 深色主题：青蓝色 + 橙黄色
            set_color = QColor("#00D4FF")      # 青蓝色（设定值）
            actual_color = QColor("#FFB84D")   # 橙黄色（实际值）
        else:
            # 浅色主题：深绿色 + 金黄色
            set_color = QColor("#007663")      # 深绿色（设定值）
            actual_color = QColor("#D4A017")   # 金黄色（实际值）
        
        for i, electrode in enumerate(self.chart.electrodes):
            # 计算组的中心位置
            group_center_x = chart_rect.left() + group_width * (i + 0.5)
            
            # 设定值柱（左侧）
            set_x = group_center_x - bar_width - spacing / 2
            self.draw_single_bar(
                painter,
                set_x,
                chart_rect,
                electrode.set_value,
                min_value,
                max_value,
                set_color,
                bar_width
            )
            
            # 实际值柱（右侧）
            actual_x = group_center_x + spacing / 2
            self.draw_single_bar(
                painter,
                actual_x,
                chart_rect,
                electrode.actual_value,
                min_value,
                max_value,
                actual_color,
                bar_width
            )
    
    # 7. 绘制单个柱子
    def draw_single_bar(self, painter: QPainter, x: float, chart_rect: QRectF, value: float, min_value: float, max_value: float, color: QColor, bar_width: float):
        value_range = max_value - min_value
        if value_range <= 0:
            return
        
        # 计算高度比例
        height_ratio = min(1.0, max(0.0, (value - min_value) / value_range))
        bar_height = chart_rect.height() * height_ratio
        
        # 柱子位置
        bar_rect = QRectF(
            x,
            chart_rect.bottom() - bar_height,
            bar_width,
            bar_height
        )
        
        # 绘制柱子（渐变，带边框）
        gradient = QLinearGradient(bar_rect.left(), bar_rect.bottom(), bar_rect.left(), bar_rect.top())
        gradient.setColorAt(0, color)
        gradient.setColorAt(1, QColor(color.red(), color.green(), color.blue(), 180))
        
        painter.setBrush(gradient)
        painter.setPen(QPen(color, 2))  # 2px边框
        painter.drawRoundedRect(bar_rect, 2, 2)  # 圆角从4减小到2
        
        # 绘制精确数值标签（显示完整数值，字体更大）
        if height_ratio > 0.05:
            painter.setPen(color)
            font = QFont("Roboto Mono", 14)  # 字体大小从11增加到14
            font.setBold(True)
            painter.setFont(font)
            
            label = f"{int(value)}"
            label_rect = QRectF(x - 10, bar_rect.top() - 24, bar_width + 20, 20)
            painter.drawText(label_rect, Qt.AlignmentFlag.AlignCenter, label)
    
    # 8. 绘制X轴标签
    def draw_x_labels(self, painter: QPainter, chart_rect: QRectF, colors):
        painter.setPen(QColor(colors.TEXT_PRIMARY))
        font = QFont("Microsoft YaHei", 11)  # 紧凑字号11
        font.setBold(True)
        painter.setFont(font)
        
        electrode_count = len(self.chart.electrodes)
        if electrode_count == 0:
            return
        
        group_width = chart_rect.width() / electrode_count
        
        # X轴标签文字：1#电极、2#电极、3#电极
        labels = ["1#电极", "2#电极", "3#电极"]
        
        for i in range(min(electrode_count, len(labels))):
            group_center_x = chart_rect.left() + group_width * (i + 0.5)
            # X轴标签位置：紧贴X轴下方，高度18px
            label_rect = QRectF(group_center_x - 60, chart_rect.bottom() + 2, 120, 18)
            painter.drawText(label_rect, Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter, labels[i])

