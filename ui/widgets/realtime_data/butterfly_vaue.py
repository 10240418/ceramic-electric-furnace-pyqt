"""
蝶阀组件 - 包含单个蝶阀指示器和2x2网格布局（仪表盘样式）
"""
from dataclasses import dataclass

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QLinearGradient, QPen, QFont, QConicalGradient, QPainterPath
import math
from ui.styles.themes import ThemeManager


@dataclass
class ValveLayoutProfile:
    left_spacing: int = -14
    gauge_weight: int = 92
    bottom_ratio: int = 8
    bottom_background: str | None = None  # 使用时从主题获取颜色
    gauge_center_multiplier: float = 0.82
    gauge_center_offset: float = 8.0
    radius_multiplier: float = 0.45
    radius_padding: float = 4.0


class IndicatorValve(QFrame):
    """蝶阀状态指示器（仪表盘样式）"""
    
    # 1. 初始化组件
    def __init__(self, valve_id: int, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        self.valve_id = valve_id
        self.current_status = "00"  # 默认停止
        self.open_percentage = 0.0  # 默认0%
        
        self.init_ui()
        self.apply_styles()
        
        # 设置 sizePolicy 为 Expanding，让组件自适应高度
        from PyQt6.QtWidgets import QSizePolicy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # 监听主题变化
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
    
    # 2. 初始化 UI
    def init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)  # 完全无内边距
        main_layout.setSpacing(2)  # 从8px改为2px，左侧和右侧容器之间的间距
        
        # 左侧 78%：仪表盘 + 编号/百分比
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(-18)  # 从-14改为-18，让仪表盘和灰色区域更紧密
        
        # 上部分 95%：仪表盘（最大化显示区域）
        self.gauge_widget = GaugeWidget(self)
        left_layout.addWidget(self.gauge_widget, 95)
        
        # 下部分 5%：编号 + 百分比（进一步压缩）
        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(0)
        from PyQt6.QtWidgets import QSizePolicy
        bottom_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        bottom_widget.setStyleSheet("background: transparent;")
        
        # 编号 (20%) - 进一步减小字体
        self.num_label = QLabel(f"{self.valve_id}#")
        self.num_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont("Microsoft YaHei", 14)  # 从18减小到14
        font.setBold(True)
        self.num_label.setFont(font)
        bottom_layout.addWidget(self.num_label, 20)
        
        # 百分比容器 (80%)，内部再细分为70%显示区+10%空白区
        percent_container = QWidget()
        percent_container_layout = QHBoxLayout(percent_container)
        percent_container_layout.setContentsMargins(0, 0, 0, 0)
        percent_container_layout.setSpacing(0)
        
        # 百分比显示区 (70%) - 使用富文本，单独减小百分号，居中显示
        self.percent_label = QLabel()
        self.percent_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.percent_label.setTextFormat(Qt.TextFormat.RichText)  # 启用富文本
        percent_container_layout.addWidget(self.percent_label, 70)
        
        # 右侧空白区 (10%)
        spacer_widget = QWidget()
        percent_container_layout.addWidget(spacer_widget, 10)
        
        bottom_layout.addWidget(percent_container, 80)
        
        # 初始化时就设置富文本样式
        self.update_percent_display()
        
        left_layout.addWidget(bottom_widget, 5)
        
        main_layout.addWidget(left_widget, 78)  # 从76%改为78%
        
        # 右侧 22%：状态按钮容器（带边框）- 取消内边距，贴边显示
        self.status_container = QFrame()
        self.status_container.setObjectName("statusContainer")
        status_container_layout = QVBoxLayout(self.status_container)
        status_container_layout.setContentsMargins(0, 0, 0, 0)  # 从(4,4,4,4)改为(0,0,0,0)
        status_container_layout.setSpacing(0)  # 从5改为0，按钮之间无间距
        
        # 关/停/开 三个状态按钮（垂直排列）
        self.btn_close = self.create_status_button("关")
        self.btn_stop = self.create_status_button("停")
        self.btn_open = self.create_status_button("开")
        
        status_container_layout.addWidget(self.btn_close)
        status_container_layout.addWidget(self.btn_stop)
        status_container_layout.addWidget(self.btn_open)
        
        main_layout.addWidget(self.status_container, 22)  # 从24%改为22%
    
    # 3. 创建状态按钮
    def create_status_button(self, text: str) -> QLabel:
        btn = QLabel(text)
        btn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn.setObjectName("statusBtn")
        font = QFont("Microsoft YaHei", 14)
        btn.setFont(font)
        return btn
    
    # 4. 更新百分比显示
    def update_percent_display(self):
        """更新百分比显示（使用富文本，数值28px，百分号18px）"""
        colors = self.theme_manager.get_colors()
        value = int(self.open_percentage)
        self.percent_label.setText(
            f'<span style="font-size: 28px; font-weight: bold; font-family: Roboto Mono; color: {colors.TEXT_PRIMARY};">{value}</span>'
            f'<span style="font-size: 18px; font-weight: normal; font-family: Roboto Mono; color: {colors.TEXT_PRIMARY};">%</span>'
        )
    
    # 5. 设置状态
    def set_status(self, status: str, open_percent: float):
        self.current_status = status
        self.open_percentage = max(0.0, min(100.0, open_percent))
        
        # 更新百分比显示
        self.update_percent_display()
        
        # 更新样式
        self.update_status_buttons()
        self.gauge_widget.update()
    
    # 6. 更新状态按钮样式（简化为主按钮样式）
    def update_status_buttons(self):
        colors = self.theme_manager.get_colors()
        
        # 判断激活状态
        is_close_active = (self.current_status == "10")
        is_stop_active = (self.current_status == "00" or self.current_status == "11")
        is_open_active = (self.current_status == "01")
        
        # 应用样式（激活状态为主按钮）
        self.btn_close.setStyleSheet(self.get_button_style(is_close_active, colors))
        self.btn_stop.setStyleSheet(self.get_button_style(is_stop_active, colors))
        self.btn_open.setStyleSheet(self.get_button_style(is_open_active, colors))
    
    # 7. 获取按钮样式（主按钮样式，取消圆角和padding，完全贴边）
    def get_button_style(self, is_active: bool, colors) -> str:
        if is_active:
            # 激活状态：主按钮样式
            return f"""
                QLabel#statusBtn {{
                    background: {colors.GLOW_PRIMARY};
                    color: {colors.TEXT_ON_PRIMARY};
                    border: 1px solid {colors.GLOW_PRIMARY};
                    border-radius: 0px;
                    padding: 0px;
                    font-weight: bold;
                }}
            """
        else:
            # 非激活状态：普通样式
            return f"""
                QLabel#statusBtn {{
                    background: transparent;
                    color: {colors.TEXT_PRIMARY};
                    border: 1px solid {colors.BORDER_MEDIUM};
                    border-radius: 0px;
                    padding: 0px;
                    font-weight: normal;
                }}
            """
    
    # 8. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        self.setStyleSheet(f"""
            QFrame {{
                background: {colors.BG_LIGHT};
                border: 1px solid {colors.BORDER_GLOW};
                border-radius: 4px;
            }}
        """)
        
        # 状态按钮容器样式（带边框）
        self.status_container.setStyleSheet(f"""
            QFrame#statusContainer {{
                background: transparent;
                border: 1px solid {colors.BORDER_GLOW};
                border-radius: 4px;
            }}
        """)
        
        self.num_label.setStyleSheet(f"""
            QLabel {{
                color: {colors.TEXT_PRIMARY};
                background: transparent;
                border: none;
            }}
        """)
        
        # 百分比标签样式（不设置字体大小，让富文本控制）
        self.percent_label.setStyleSheet(f"""
            QLabel {{
                background: transparent;
                border: none;
            }}
        """)
        
        self.update_status_buttons()
        self.update_percent_display()
    
    # 9. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()
        self.gauge_widget.update()


class GaugeWidget(QWidget):
    """仪表盘组件（180度扇形）"""
    
    # 1. 初始化
    def __init__(self, parent: IndicatorValve):
        super().__init__(parent)
        self.indicator = parent
        self.theme_manager = ThemeManager.instance()
        # 移除固定最小高度，让仪表盘自适应布局
        # self.setMinimumHeight(120)
    
    # 2. 绘制仪表盘
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        colors = self.theme_manager.get_colors()
        
        # 计算仪表盘中心和半径（增加4px空间，让仪表盘略大）
        width = self.width()
        height = self.height()
        center_x = width / 2
        center_y = height * 0.82 + 8  # 继续下移中心，释放上方空间
        radius = max(0.0, min(width, height) * 0.76 - 4)  # 简化计算，保持留白且半径略小
        
        # 绘制背景弧（180度扇形）
        self.draw_background_arc(painter, center_x, center_y, radius, colors)
        
        # 绘制刻度和标签
        self.draw_scale_marks(painter, center_x, center_y, radius, colors)
        
        # 绘制指针
        self.draw_needle(painter, center_x, center_y, radius, colors)
        
        # 绘制中心圆
        self.draw_center_circle(painter, center_x, center_y, colors)
    
    # 3. 绘制背景弧（灰色轨道，上半部分）
    def draw_background_arc(self, painter: QPainter, cx: float, cy: float, radius: float, colors):
        rect = QRectF(cx - radius, cy - radius, radius * 2, radius * 2)
        
        # 背景弧（180度，上半部分：从180°到0°，即从左到右）
        painter.setPen(QPen(QColor(colors.TEXT_SECONDARY), 6))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(rect, 0 * 16, 180 * 16)  # 从0度（右边）逆时针到180度（左边）
    
    # 4. 绘制刻度和标签（上半部分，灰/白配色）
    def draw_scale_marks(self, painter: QPainter, cx: float, cy: float, radius: float, colors):
        # 刻度：全开(180°左) 3/4(135°) 1/2(90°上) 1/4(45°) 全关(0°右)
        scales = [
            (180, "全开"),
            (135, "3/4"),
            (90, "1/2"),
            (45, "1/4"),
            (0, "全关")
        ]
        
        painter.setPen(QColor(colors.TEXT_PRIMARY))
        font = QFont("Microsoft YaHei", 10)
        font.setBold(True)
        painter.setFont(font)
        
        for angle_deg, label in scales:
            # 转换为弧度
            angle_rad = math.radians(angle_deg)
            
            # 刻度线位置（从内圈到外圈）
            mark_start_x = cx + (radius - 12) * math.cos(angle_rad)
            mark_start_y = cy - (radius - 12) * math.sin(angle_rad)  # 注意：y轴向下，所以用减号
            mark_end_x = cx + radius * math.cos(angle_rad)
            mark_end_y = cy - radius * math.sin(angle_rad)
            
            # 绘制刻度线（灰/白色）
            painter.setPen(QPen(QColor(colors.TEXT_PRIMARY), 3))
            painter.drawLine(QPointF(mark_start_x, mark_start_y), QPointF(mark_end_x, mark_end_y))
            
            # 标签位置（向外延伸，从15px改为12px，让标签更靠近弧线）
            label_x = cx + (radius + 12) * math.cos(angle_rad)
            label_y = cy - (radius + 12) * math.sin(angle_rad)

            # 单独调整全开和全关的位置
            if label == "全开":
                label_x -= 6  # 向左移动6px
            elif label == "全关":
                label_x += 6  # 向右移动6px
            
            # 绘制标签
            painter.setPen(QColor(colors.TEXT_PRIMARY))
            painter.drawText(QRectF(label_x - 25, label_y - 12, 50, 24), Qt.AlignmentFlag.AlignCenter, label)
    
    # 5. 绘制指针（三角形指针，指向上半部分）
    def draw_needle(self, painter: QPainter, cx: float, cy: float, radius: float, colors):
        # 计算指针角度（0% = 0°全关右边, 100% = 180°全开左边）
        # 指针在上半部分旋转
        needle_angle_deg = (self.indicator.open_percentage / 100.0) * 180
        needle_angle_rad = math.radians(needle_angle_deg)
        
        # 指针长度
        needle_length = radius - 18
        
        # 指针终点（注意：y轴向下，所以用减号让指针指向上方）
        needle_x = cx + needle_length * math.cos(needle_angle_rad)
        needle_y = cy - needle_length * math.sin(needle_angle_rad)
        
        # 绘制三角形指针
        # 三角形的三个顶点：
        # 1. 尖端（指针终点）
        # 2. 左侧底部
        # 3. 右侧底部
        
        # 三角形底部宽度
        base_width = 12
        base_distance = 15  # 底部距离中心的距离
        
        # 计算底部两个点的位置（垂直于指针方向）
        perpendicular_angle = needle_angle_rad + math.radians(90)
        
        base_center_x = cx + base_distance * math.cos(needle_angle_rad)
        base_center_y = cy - base_distance * math.sin(needle_angle_rad)
        
        left_x = base_center_x + (base_width / 2) * math.cos(perpendicular_angle)
        left_y = base_center_y - (base_width / 2) * math.sin(perpendicular_angle)
        
        right_x = base_center_x - (base_width / 2) * math.cos(perpendicular_angle)
        right_y = base_center_y + (base_width / 2) * math.sin(perpendicular_angle)
        
        # 绘制三角形
        path = QPainterPath()
        path.moveTo(needle_x, needle_y)  # 尖端
        path.lineTo(left_x, left_y)      # 左侧底部
        path.lineTo(right_x, right_y)    # 右侧底部
        path.closeSubpath()
        
        # 填充三角形
        painter.setBrush(QColor(colors.TEXT_PRIMARY))
        painter.setPen(QPen(QColor(colors.TEXT_PRIMARY), 2))
        painter.drawPath(path)
    
    # 6. 绘制中心圆
    def draw_center_circle(self, painter: QPainter, cx: float, cy: float, colors):
        painter.setBrush(QColor(colors.TEXT_PRIMARY))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(cx, cy), 8, 8)


class WidgetValveGrid(QWidget):
    """蝶阀网格组件 - 2x2网格显示4个蝶阀状态"""
    
    # 1. 初始化组件
    def __init__(self, parent=None):
        super().__init__(parent)
        self.valve_indicators = []
        self.init_ui()
        
        # 设置 sizePolicy 为 Expanding，让 stretch 生效
        from PyQt6.QtWidgets import QSizePolicy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    
    # 2. 重写 sizeHint，返回一个小值，让 stretch 生效
    def sizeHint(self):
        from PyQt6.QtCore import QSize
        return QSize(400, 100)  # 返回一个小的高度值
    
    # 3. 重写 minimumSizeHint，返回一个小值
    def minimumSizeHint(self):
        from PyQt6.QtCore import QSize
        return QSize(400, 100)  # 返回一个小的高度值
    
    # 2. 初始化 UI
    def init_ui(self):
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # 取消外边距
        layout.setSpacing(6)  # 减少2px：从8px改为6px
        
        # 创建4个蝶阀指示器（2x2网格）
        for i in range(4):
            indicator = IndicatorValve(i + 1)
            row = i // 2
            col = i % 2
            layout.addWidget(indicator, row, col)
            self.valve_indicators.append(indicator)
    
    # 3. 更新蝶阀状态
    def update_valve(self, valve_no: int, status: str, open_percent: float):
        """
        更新指定蝶阀的状态
        
        Args:
            valve_no: 蝶阀编号 (1-4)
            status: 状态码 ('00', '01', '10', '11')
            open_percent: 开度百分比 (0-100)
        """
        if 1 <= valve_no <= 4:
            self.valve_indicators[valve_no - 1].set_status(status, open_percent)
    
    # 4. 批量更新所有蝶阀
    def update_all_valves(self, valves_data: list):
        """
        批量更新所有蝶阀状态
        
        Args:
            valves_data: 蝶阀数据列表，每项包含 {'status': str, 'open_percent': float}
        """
        for i, valve_data in enumerate(valves_data):
            if i < 4:
                self.valve_indicators[i].set_status(
                    valve_data['status'], 
                    valve_data['open_percent']
                )
