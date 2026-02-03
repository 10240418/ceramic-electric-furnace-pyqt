"""
电极电流柱状图组件 - 显示三个电极的设定值和实际值对比
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, QRectF, QTimer
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

        # 节流优化：缓存最新数据，定时更新UI
        self._pending_update = False
        self._pending_electrodes = None
        self._pending_deadzone = None
        self._throttle_timer = QTimer()
        self._throttle_timer.setSingleShot(True)
        self._throttle_timer.timeout.connect(self._do_pending_update)

        self.init_ui()

        # 监听主题变化
        self.theme_manager.theme_changed.connect(self.on_theme_changed)

        # 监听轮询速度变化
        from backend.config.polling_config import get_polling_config
        self.polling_config = get_polling_config()
        self.polling_config.register_callback(self.on_polling_speed_changed)

    # 2. 初始化 UI
    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(8, 0, 0, 0)
        main_layout.setSpacing(4)

        # 左侧：图表区域（80%）
        self.chart_widget = ChartWidget(self)
        main_layout.addWidget(self.chart_widget, stretch=80)

        # 右侧：数据列表区域（20%）
        self.data_panel = self.create_data_panel()
        main_layout.addWidget(self.data_panel, stretch=20)

        self.apply_styles()

    # 3. 创建数据面板
    def create_data_panel(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("dataPanel")

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 上部分：弧流+死区（26%高度）
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(8, 8, 8, 8)
        top_layout.setSpacing(4)

        # 标题：弧流(KA)
        title_label = QLabel("弧流(KA)")
        title_label.setObjectName("dataTitle")
        font = QFont("Microsoft YaHei", 13)
        font.setBold(True)
        title_label.setFont(font)
        top_layout.addWidget(title_label)

        # 死区
        self.deadzone_label = QLabel(f"死区: {int(self.deadzone_percent)}%")
        self.deadzone_label.setObjectName("deadzoneLabel")
        font = QFont("Microsoft YaHei", 13)
        self.deadzone_label.setFont(font)
        top_layout.addWidget(self.deadzone_label)

        top_layout.addStretch()
        layout.addWidget(top_widget, stretch=26)

        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setObjectName("separator")
        layout.addWidget(separator)

        # 中部分：设定值（37%高度）
        set_widget = QWidget()
        set_layout = QVBoxLayout(set_widget)
        set_layout.setContentsMargins(8, 8, 8, 8)
        set_layout.setSpacing(4)

        # 设定值标题
        set_title = QLabel("设定值")
        set_title.setObjectName("sectionTitle")
        font = QFont("Microsoft YaHei", 13)
        font.setBold(True)
        set_title.setFont(font)
        set_layout.addWidget(set_title)

        # 设定值数据
        self.set_labels = []
        for i in range(3):
            label = QLabel(f"{i+1}#: 0")
            label.setObjectName(f"setLabel_{i}")
            font = QFont("Roboto Mono", 13)
            label.setFont(font)
            set_layout.addWidget(label)
            self.set_labels.append(label)

        set_layout.addStretch()
        layout.addWidget(set_widget, stretch=37)

        # 分隔线
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        separator2.setObjectName("separator")
        layout.addWidget(separator2)

        # 下部分：实际值（37%高度）
        actual_widget = QWidget()
        actual_layout = QVBoxLayout(actual_widget)
        actual_layout.setContentsMargins(8, 8, 8, 8)
        actual_layout.setSpacing(4)

        # 实际值标题
        actual_title = QLabel("实际值")
        actual_title.setObjectName("sectionTitle")
        font = QFont("Microsoft YaHei", 13)
        font.setBold(True)
        actual_title.setFont(font)
        actual_layout.addWidget(actual_title)

        # 实际值数据
        self.actual_labels = []
        for i in range(3):
            label = QLabel(f"{i+1}#: 0")
            label.setObjectName(f"actualLabel_{i}")
            font = QFont("Roboto Mono", 13)
            label.setFont(font)
            actual_layout.addWidget(label)
            self.actual_labels.append(label)

        actual_layout.addStretch()
        layout.addWidget(actual_widget, stretch=37)

        return panel

    # 4. 更新数据（优化性能）
    def update_data(self, electrodes: list, deadzone_percent: float = 15.0):
        """更新电极数据（节流优化，避免频繁重绘）

        Args:
            electrodes: 电极数据列表，每个元素包含 name, set_value, actual_value
                       例如: [
                           ElectrodeData("1#电极", 5978, 5980),
                           ElectrodeData("2#电极", 5978, 5975),
                           ElectrodeData("3#电极", 5978, 5982),
                       ]
            deadzone_percent: 死区百分比（默认15%）
        """
        # 检查数据是否变化，避免无效重绘
        data_changed = False

        # 检查电极数据是否变化
        if len(self.electrodes) != len(electrodes):
            data_changed = True
        else:
            for i, (old, new) in enumerate(zip(self.electrodes, electrodes)):
                if (old.set_value != new.set_value or
                    old.actual_value != new.actual_value):
                    data_changed = True
                    break

        # 检查死区是否变化
        if abs(self.deadzone_percent - deadzone_percent) > 0.01:
            data_changed = True

        # 只有数据变化时才更新
        if data_changed:
            # 节流优化：缓存待更新数据，延迟执行
            self._pending_electrodes = electrodes
            self._pending_deadzone = deadzone_percent

            if not self._pending_update:
                self._pending_update = True
                # 延迟 50ms 执行更新，避免频繁重绘
                self._throttle_timer.start(50)

    # 4.1 执行待处理的更新
    def _do_pending_update(self):
        """执行待处理的更新（节流优化）"""
        if self._pending_electrodes is None:
            return

        electrodes = self._pending_electrodes
        deadzone_percent = self._pending_deadzone

        self.electrodes = electrodes
        self.deadzone_percent = deadzone_percent

        # 更新死区显示
        self.deadzone_label.setText(f"死区: {int(deadzone_percent)}%")

        # 更新设定值标签
        for i, electrode in enumerate(electrodes):
            if i < len(self.set_labels):
                self.set_labels[i].setText(f"{i+1}#: {int(electrode.set_value)}")

        # 更新实际值标签
        for i, electrode in enumerate(electrodes):
            if i < len(self.actual_labels):
                self.actual_labels[i].setText(f"{i+1}#: {int(electrode.actual_value)}")

        # 触发重绘
        self.chart_widget.update()

        # 清除待更新标记
        self._pending_update = False
        self._pending_electrodes = None
        self._pending_deadzone = None
    
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

    # 5. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()

        # 数据面板样式（上下左右都有border）
        self.data_panel.setStyleSheet(f"""
            QFrame#dataPanel {{
                background: {colors.CARD_BG};
                border: 1px solid {colors.BORDER_DARK};
                border-radius: 0px;
            }}
        """)

        # 标题样式（弧流文字颜色和死区一样）
        title_label = self.data_panel.findChild(QLabel, "dataTitle")
        if title_label:
            title_label.setStyleSheet(f"""
                QLabel {{
                    color: {colors.TEXT_PRIMARY};
                    background: transparent;
                    border: none;
                    padding: 4px 0px;
                }}
            """)

        # 死区标签
        self.deadzone_label.setStyleSheet(f"""
            QLabel {{
                color: {colors.TEXT_PRIMARY};
                background: transparent;
                border: none;
                padding: 2px 0px;
            }}
        """)

        # 分隔线（完整连接左右边距）
        separators = self.data_panel.findChildren(QFrame, "separator")
        for sep in separators:
            sep.setStyleSheet(f"""
                QFrame {{
                    background: {colors.BORDER_DARK};
                    max-height: 1px;
                    margin-left: 0px;
                    margin-right: 0px;
                }}
            """)

        # 章节标题（设定值/实际值）
        section_titles = self.data_panel.findChildren(QLabel, "sectionTitle")
        for title in section_titles:
            title.setStyleSheet(f"""
                QLabel {{
                    color: {colors.TEXT_PRIMARY};
                    background: transparent;
                    border: none;
                    padding: 4px 0px;
                }}
            """)

        # 设定值标签颜色
        if self.theme_manager.is_dark_mode():
            set_color = "#00D4FF"  # 深色主题：青蓝色
        else:
            set_color = "#007663"  # 浅色主题：深绿色

        for label in self.set_labels:
            label.setStyleSheet(f"""
                QLabel {{
                    color: {set_color};
                    background: transparent;
                    border: none;
                    padding: 2px 0px;
                }}
            """)

        # 实际值标签颜色
        if self.theme_manager.is_dark_mode():
            actual_color = "#FFB84D"  # 深色主题：橙黄色
        else:
            actual_color = "#D4A017"  # 浅色主题：金黄色

        for label in self.actual_labels:
            label.setStyleSheet(f"""
                QLabel {{
                    color: {actual_color};
                    background: transparent;
                    border: none;
                    padding: 2px 0px;
                }}
            """)

    # 6. 主题变化时重新应用样式
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
        
        # 性能优化：启用双缓冲，减少闪烁
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, False)
    
    # 2. 绘制图表
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        colors = self.theme_manager.get_colors()
        
        # 固定Y轴范围：1-8 (KA)
        min_value = 0
        max_value = 8000  # 8KA = 8000A
        
        # 绘制区域（紧凑布局，Y轴14px，X轴标签高度22px）
        y_axis_width = 14  # Y轴刻度宽度（加大4px）
        x_axis_height = 22  # X轴高度（加大6px）
        chart_rect = QRectF(
            y_axis_width + 4,  # 左边距18px（为Y轴刻度留空间+4px）
            8,  # 顶部边距8px（4px+4px）
            self.width() - y_axis_width - 8 - 4,  # 右边距8px（紧凑）
            self.height() - x_axis_height - 8  # 底部留22px给X轴标签
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
        font = QFont("Microsoft YaHei", 10)  # 紧凑字号10
        font.setBold(True)  # 加粗
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
                int(chart_rect.left() - 4),
                int(y),
                int(chart_rect.left()),
                int(y)
            )

            # 绘制刻度值（在Y轴左侧）
            painter.setPen(QColor(colors.TEXT_PRIMARY))
            text = f"{value}"
            # 刻度值绘制区域：从左边缘到Y轴左侧（紧凑）
            painter.drawText(
                QRectF(0, y - 8, chart_rect.left() - 4, 16),
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
        bar_width = 28  # 单个柱子宽度（紧凑）
        spacing = 18  # 柱子间距（加大6px）
        
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
        font = QFont("Microsoft YaHei", 12)  # 字号加大到12
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
            # X轴标签位置：紧贴X轴下方，高度22px
            label_rect = QRectF(group_center_x - 50, chart_rect.bottom() + 2, 100, 22)
            painter.drawText(label_rect, Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter, labels[i])

