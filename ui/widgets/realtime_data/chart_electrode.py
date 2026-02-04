"""
电极电流柱状图组件 - 显示三个电极的设定值和实际值对比
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, QRectF, QTimer
from PyQt6.QtGui import QPainter, QColor, QLinearGradient, QPen, QFont
from ui.styles.themes import ThemeManager


class ElectrodeData:
    """电极数据模型"""

    def __init__(self, name: str, set_value: float, actual_value: float, voltage: float = 0):
        self.name = name
        self.set_value = set_value
        self.actual_value = actual_value
        self.voltage = voltage  # 弧压


class ChartElectrode(QWidget):
    """电极电流柱状图组件"""

    # 1. 初始化组件
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        # 设置默认值：设定值 0A，实际值 0A，弧压 0V（等待真实数据）
        self.electrodes = [
            ElectrodeData("1#电极", 0, 0, 0),
            ElectrodeData("2#电极", 0, 0, 0),
            ElectrodeData("3#电极", 0, 0, 0),
        ]
        self.deadzone_percent = 15.0  # 死区百分比，默认15%
        
        # 标记是否已接收到真实数据
        self._has_real_data = False

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
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(0)

        # 垂直居中：上方添加 stretch
        top_layout.addStretch()
        
        # 标题：弧流(KA)
        title_label = QLabel("弧流(KA)")
        title_label.setObjectName("dataTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        font = QFont("Microsoft YaHei", 13)
        font.setBold(True)
        title_label.setFont(font)
        top_layout.addWidget(title_label)

        # 弧压
        voltage_label = QLabel("弧压(10V)")
        voltage_label.setObjectName("voltageLabel")
        voltage_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        font = QFont("Microsoft YaHei", 13)
        voltage_label.setFont(font)
        top_layout.addWidget(voltage_label)

        # 死区
        self.deadzone_label = QLabel(f"死区: {int(self.deadzone_percent)}%")
        self.deadzone_label.setObjectName("deadzoneLabel")
        self.deadzone_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        font = QFont("Microsoft YaHei", 13)
        self.deadzone_label.setFont(font)
        top_layout.addWidget(self.deadzone_label)

        # 垂直居中：下方添加 stretch
        top_layout.addStretch()
        layout.addWidget(top_widget, stretch=26)

        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setObjectName("separator")
        layout.addWidget(separator)

        # 中部分：上限（37%高度）
        upper_widget = QWidget()
        upper_layout = QVBoxLayout(upper_widget)
        upper_layout.setContentsMargins(0, 0, 0, 0)
        upper_layout.setSpacing(0)

        # 垂直居中：上方添加 stretch
        upper_layout.addStretch()
        
        # 上限标题
        upper_title = QLabel("上限")
        upper_title.setObjectName("sectionTitle")
        upper_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        font = QFont("Microsoft YaHei", 13)
        font.setBold(True)
        upper_title.setFont(font)
        upper_layout.addWidget(upper_title)

        # 上限数据
        self.upper_labels = []
        for i in range(3):
            label = QLabel(f"{i+1}#: 0 A")
            label.setObjectName(f"upperLabel_{i}")
            label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            upper_layout.addWidget(label)
            self.upper_labels.append(label)

        # 垂直居中：下方添加 stretch
        upper_layout.addStretch()
        layout.addWidget(upper_widget, stretch=37)

        # 分隔线
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.Shape.HLine)
        separator2.setFrameShadow(QFrame.Shadow.Sunken)
        separator2.setObjectName("separator")
        layout.addWidget(separator2)

        # 下部分：下限（37%高度）
        lower_widget = QWidget()
        lower_layout = QVBoxLayout(lower_widget)
        lower_layout.setContentsMargins(0, 0, 0, 0)
        lower_layout.setSpacing(0)

        # 垂直居中：上方添加 stretch
        lower_layout.addStretch()
        
        # 下限标题
        lower_title = QLabel("下限")
        lower_title.setObjectName("sectionTitle")
        lower_title.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        font = QFont("Microsoft YaHei", 13)
        font.setBold(True)
        lower_title.setFont(font)
        lower_layout.addWidget(lower_title)

        # 下限数据
        self.lower_labels = []
        for i in range(3):
            label = QLabel(f"{i+1}#: 0 A")
            label.setObjectName(f"lowerLabel_{i}")
            label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            lower_layout.addWidget(label)
            self.lower_labels.append(label)

        # 垂直居中：下方添加 stretch
        lower_layout.addStretch()
        layout.addWidget(lower_widget, stretch=37)

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

        # 更新上限和下限标签
        for i, electrode in enumerate(electrodes):
            if i < len(self.upper_labels):
                # 计算上限：设定值 * (1 + 死区%)
                upper_limit = int(electrode.set_value * (1 + deadzone_percent / 100.0))
                # 使用纯文本格式
                self.upper_labels[i].setText(f"{i+1}#: {upper_limit} A")
            
            if i < len(self.lower_labels):
                # 计算下限：设定值 * (1 - 死区%)
                lower_limit = int(electrode.set_value * (1 - deadzone_percent / 100.0))
                # 使用纯文本格式
                self.lower_labels[i].setText(f"{i+1}#: {lower_limit} A")

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
            data: 包含弧流和弧压数据的字典
                {
                    'arc_current': {'U': 5978, 'V': 5980, 'W': 5975},
                    'arc_voltage': {'U': 85, 'V': 86, 'W': 84},
                    'setpoints': {'U': 5978, 'V': 5978, 'W': 5978},
                    'manual_deadzone_percent': 10.0
                }
        """
        arc_current = data.get('arc_current', {})
        arc_voltage = data.get('arc_voltage', {})
        setpoints = data.get('setpoints', {})
        deadzone = data.get('manual_deadzone_percent', 15.0)
        
        # 标记已接收到真实数据
        if arc_current or arc_voltage or setpoints:
            self._has_real_data = True
        
        # 构建电极数据列表
        # 如果数据为空或设定值为0，则使用0作为默认值
        electrodes = [
            ElectrodeData(
                "1#电极", 
                setpoints.get('U', 0),
                arc_current.get('U', 0), 
                arc_voltage.get('U', 0)
            ),
            ElectrodeData(
                "2#电极", 
                setpoints.get('V', 0),
                arc_current.get('V', 0), 
                arc_voltage.get('V', 0)
            ),
            ElectrodeData(
                "3#电极", 
                setpoints.get('W', 0),
                arc_current.get('W', 0), 
                arc_voltage.get('W', 0)
            ),
        ]
        
        self.update_data(electrodes, deadzone)

    # 5. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()

        # 数据面板样式（上下左右都有border，左边框使用主题色）
        border_left_color = colors.GLOW_PRIMARY
        
        self.data_panel.setStyleSheet(f"""
            QFrame#dataPanel {{
                background: {colors.CARD_BG};
                border-top: 1px solid {colors.BORDER_DARK};
                border-right: 1px solid {colors.BORDER_DARK};
                border-bottom: 1px solid {colors.BORDER_DARK};
                border-left: 1px solid {border_left_color};
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
                    padding: 2px 0px 0px 0px;
                }}
            """)

        # 死区标签
        self.deadzone_label.setStyleSheet(f"""
            QLabel {{
                color: {colors.TEXT_PRIMARY};
                background: transparent;
                border: none;
                padding: 2px 0px 0px 0px;
            }}
        """)

        # 弧压标签
        voltage_label = self.data_panel.findChild(QLabel, "voltageLabel")
        if voltage_label:
            voltage_label.setStyleSheet(f"""
                QLabel {{
                    color: {colors.TEXT_PRIMARY};
                    background: transparent;
                    border: none;
                    padding: 2px 0px 0px 0px;
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

        # 章节标题（上限/下限）
        section_titles = self.data_panel.findChildren(QLabel, "sectionTitle")
        for title in section_titles:
            title.setStyleSheet(f"""
                QLabel {{
                    color: {colors.TEXT_PRIMARY};
                    background: transparent;
                    border: none;
                    padding: 2px 0px 0px 0px;
                }}
            """)

        # 上限标签颜色（使用主题配色，字体 18px 不加粗）
        for label in self.upper_labels:
            label.setStyleSheet(f"""
                QLabel {{
                    color: {colors.TEXT_PRIMARY};
                    background: transparent;
                    border: none;
                    padding: 2px 0px 0px 0px;
                    font-size: 18px;
                }}
            """)

        # 下限标签颜色（使用主题配色，字体 18px 不加粗）
        for label in self.lower_labels:
            label.setStyleSheet(f"""
                QLabel {{
                    color: {colors.TEXT_PRIMARY};
                    background: transparent;
                    border: none;
                    padding: 2px 0px 0px 0px;
                    font-size: 18px;
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
        
        # 固定Y轴范围
        min_current = 0
        max_current = 8000  # 8KA = 8000A（左侧Y轴：弧流）
        min_voltage = 0
        max_voltage = 150  # 150V（右侧Y轴：弧压）
        
        # 绘制区域（左右都有Y轴，左侧Y轴10px，右侧Y轴20px，X轴标签高度22px）
        left_y_axis_width = 10  # 左侧Y轴刻度宽度
        right_y_axis_width = 20  # 右侧Y轴刻度宽度（减小10px）
        x_axis_height = 22  # X轴高度
        chart_rect = QRectF(
            left_y_axis_width + 4,  # 左边距14px（为左侧Y轴刻度留空间）
            8,  # 顶部边距8px
            self.width() - left_y_axis_width - right_y_axis_width - 4,  # 减去左右Y轴宽度，右边距减小
            self.height() - x_axis_height - 8  # 底部留22px给X轴标签
        )
        
        # 绘制Y轴和X轴
        self.draw_axes(painter, chart_rect, colors)
        
        # 绘制左侧Y轴刻度（弧流：0-8 KA）
        self.draw_left_y_axis(painter, min_current, max_current, left_y_axis_width, chart_rect, colors)
        
        # 绘制右侧Y轴刻度（弧压：0-150 V）
        self.draw_right_y_axis(painter, min_voltage, max_voltage, chart_rect, colors)
        
        # 绘制上下限线（根据死区计算）
        self.draw_limit_lines(painter, chart_rect, min_current, max_current, colors)
        
        # 绘制柱状图（9根柱子：3个电极 x 3种值）
        self.draw_bars(painter, chart_rect, min_current, max_current, min_voltage, max_voltage, colors)
        
        # 绘制X轴标签（1#电极、2#电极、3#电极）
        self.draw_x_labels(painter, chart_rect, colors)
    
    # 3. 绘制坐标轴（带箭头，左右两侧Y轴）
    def draw_axes(self, painter: QPainter, chart_rect: QRectF, colors):
        painter.setPen(QPen(QColor(colors.BORDER_DARK), 2))
        
        # 左侧Y轴
        painter.drawLine(
            int(chart_rect.left()), 
            int(chart_rect.top()), 
            int(chart_rect.left()), 
            int(chart_rect.bottom())
        )
        
        # 左侧Y轴箭头（三角形）
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
        
        # 右侧Y轴
        painter.drawLine(
            int(chart_rect.right()), 
            int(chart_rect.top()), 
            int(chart_rect.right()), 
            int(chart_rect.bottom())
        )
        
        # 右侧Y轴箭头（三角形）
        y_arrow_points_right = [
            (chart_rect.right(), chart_rect.top()),
            (chart_rect.right() - arrow_size / 2, chart_rect.top() + arrow_size),
            (chart_rect.right() + arrow_size / 2, chart_rect.top() + arrow_size),
        ]
        painter.drawPolygon(QPolygonF([QPointF(x, y) for x, y in y_arrow_points_right]))
        
        # X轴（不带箭头）
        painter.drawLine(
            int(chart_rect.left()), 
            int(chart_rect.bottom()), 
            int(chart_rect.right()), 
            int(chart_rect.bottom())
        )
    
    # 4. 绘制左侧Y轴刻度（弧流：0-8 KA）
    def draw_left_y_axis(self, painter: QPainter, min_value: float, max_value: float, width: int, chart_rect: QRectF, colors):
        painter.setPen(QColor(colors.TEXT_PRIMARY))
        font = QFont("Microsoft YaHei", 10)
        font.setBold(True)
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
            # 刻度值绘制区域：从左边缘到Y轴左侧
            painter.drawText(
                QRectF(0, y - 8, chart_rect.left() - 4, 16),
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                text
            )
    
    # 4.5 绘制右侧Y轴刻度（弧压：0-150 V）
    def draw_right_y_axis(self, painter: QPainter, min_value: float, max_value: float, chart_rect: QRectF, colors):
        painter.setPen(QColor(colors.TEXT_PRIMARY))
        font = QFont("Microsoft YaHei", 9)
        font.setBold(True)
        painter.setFont(font)

        # 16个刻度：0, 1, 2, ..., 15（代表 0V, 10V, 20V, ..., 150V）
        for i in range(16):
            value_v = i * 10  # 电压值（V）
            ratio = value_v / max_value
            y = chart_rect.bottom() - chart_rect.height() * ratio

            # 绘制刻度线
            painter.setPen(QPen(QColor(colors.BORDER_DARK), 1))
            painter.drawLine(
                int(chart_rect.right()),
                int(y),
                int(chart_rect.right() + 4),
                int(y)
            )

            # 绘制刻度值（在Y轴右侧）
            painter.setPen(QColor(colors.TEXT_PRIMARY))
            text = f"{i}"
            # 刻度值绘制区域：从Y轴右侧开始
            painter.drawText(
                QRectF(chart_rect.right() + 6, y - 8, 24, 16),
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                text
            )
    
    # 5. 绘制上下限线（根据死区计算，在最右边添加文字标注）
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
        upper_color = QColor(colors.STATUS_ALARM)
        
        # 绘制上限线
        upper_ratio = (max_upper_limit - min_value) / value_range
        upper_y = chart_rect.bottom() - chart_rect.height() * upper_ratio
        
        painter.setPen(QPen(upper_color, 2, Qt.PenStyle.DashLine))
        painter.drawLine(int(chart_rect.left()), int(upper_y), int(chart_rect.right()), int(upper_y))
        
        # 在上限线最右边添加文字标注（右移 14px）
        painter.setPen(upper_color)
        font = QFont("Microsoft YaHei", 11)
        font.setBold(True)
        painter.setFont(font)
        text_rect = QRectF(chart_rect.right() - 60 + 14, upper_y - 20, 55, 20)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, "上限")
        
        # 下限线颜色（适配主题）
        lower_color = QColor(colors.STATUS_INFO)
        
        # 绘制下限线
        lower_ratio = (min_lower_limit - min_value) / value_range
        lower_y = chart_rect.bottom() - chart_rect.height() * lower_ratio
        
        painter.setPen(QPen(lower_color, 2, Qt.PenStyle.DashLine))
        painter.drawLine(int(chart_rect.left()), int(lower_y), int(chart_rect.right()), int(lower_y))
        
        # 在下限线最右边添加文字标注（右移 14px）
        painter.setPen(lower_color)
        painter.setFont(font)
        text_rect = QRectF(chart_rect.right() - 60 + 14, lower_y - 20, 55, 20)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, "下限")
    
    # 6. 绘制柱状图（9根柱子：3个电极 x 3种值）
    def draw_bars(self, painter: QPainter, chart_rect: QRectF, min_current: float, max_current: float, min_voltage: float, max_voltage: float, colors):
        electrode_count = len(self.chart.electrodes)
        if electrode_count == 0:
            return

        current_range = max_current - min_current
        voltage_range = max_voltage - min_voltage
        if current_range <= 0 or voltage_range <= 0:
            return

        # 计算每个电极组的宽度
        group_width = chart_rect.width() / electrode_count
        bar_width = 30  # 单个柱子宽度
        bar_spacing = 6  # 每组内柱子间距
        group_spacing = -4  # 组间距调整（加大2px，从-6px改为-4px）
        
        # 配色方案（使用主题变量）
        colors = self.theme_manager.get_colors()
        set_color = QColor(colors.ELECTRODE_SET_VALUE)       # 设定值弧流
        actual_color = QColor(colors.ELECTRODE_ACTUAL_VALUE) # 实际值弧流
        voltage_color = QColor(colors.ELECTRODE_VOLTAGE)     # 弧压
        
        for i, electrode in enumerate(self.chart.electrodes):
            # 计算组的中心位置（考虑组间距调整）
            group_center_x = chart_rect.left() + group_width * (i + 0.5) + group_spacing * i
            
            # 设定值弧流柱（左侧）
            set_x = group_center_x - bar_width * 1.5 - bar_spacing
            self.draw_single_bar(
                painter,
                set_x,
                chart_rect,
                electrode.set_value,
                min_current,
                max_current,
                set_color,
                bar_width,
                "current"
            )
            
            # 实际值弧流柱（中间）
            actual_x = group_center_x - bar_width / 2
            self.draw_single_bar(
                painter,
                actual_x,
                chart_rect,
                electrode.actual_value,
                min_current,
                max_current,
                actual_color,
                bar_width,
                "current"
            )
            
            # 弧压柱（右侧，使用右侧Y轴比例）
            voltage_x = group_center_x + bar_width / 2 + bar_spacing
            self.draw_single_bar(
                painter,
                voltage_x,
                chart_rect,
                electrode.voltage,
                min_voltage,
                max_voltage,
                voltage_color,
                bar_width,
                "voltage"
            )
    
    # 7. 绘制单个柱子
    def draw_single_bar(self, painter: QPainter, x: float, chart_rect: QRectF, value: float, min_value: float, max_value: float, color: QColor, bar_width: float, bar_type: str = "current"):
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
        painter.drawRoundedRect(bar_rect, 2, 2)
        
        # 绘制精确数值标签
        if height_ratio > 0.05:
            painter.setPen(color)
            font = QFont("Roboto Mono", 11)
            font.setBold(True)
            painter.setFont(font)
            
            # 根据类型显示不同的数值（弧压不显示单位V）
            if bar_type == "voltage":
                label = f"{int(value)}"  # 只显示数值，不显示单位
            else:
                label = f"{int(value)}"
            
            label_rect = QRectF(x - 10, bar_rect.top() - 20, bar_width + 20, 18)
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

