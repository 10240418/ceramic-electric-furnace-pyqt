"""
电极数据卡片组件 - 显示单个电极的深度、弧流、弧压
"""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor
from ui.styles.themes import ThemeManager
from ui.utils.alarm_checker import get_alarm_checker
from ui.utils.alarm_sound_manager import get_alarm_sound_manager


class CardElectrode(QFrame):
    """电极数据卡片组件"""
    
    # 1. 初始化组件
    def __init__(self, electrode_no: int, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        self.alarm_checker = get_alarm_checker()
        self.electrode_no = electrode_no
        self.setObjectName("electrodeCard")
        self.setFixedSize(180, 140)
        
        # 确保背景完全不透明
        self.setAutoFillBackground(True)
        
        # 报警状态
        self.depth_status = 'normal'
        self.current_status = 'normal'
        self.voltage_status = 'normal'
        
        # 当前数据值（用于闪烁时重绘）
        self._depth_mm = 0.0
        self._current_a = 0.0
        self._voltage_v = 0.0
        
        # 闪烁状态（与 CardCooling 一致的实现）
        self.has_alarm = False
        self.blink_visible = True
        
        # 闪烁定时器
        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self.toggle_blink)
        
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
        self.title_label = QLabel(f"{self.electrode_no}#电极")
        self.title_label.setObjectName("electrodeTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)
        
        # 深度（左对齐，启用 HTML 格式）
        self.depth_label = QLabel("深度: 0.000m")
        self.depth_label.setObjectName(f"depth_{self.electrode_no}")
        self.depth_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.depth_label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(self.depth_label)
        
        # 弧流（左对齐，启用 HTML 格式）
        self.current_label = QLabel("弧流: 0A")
        self.current_label.setObjectName(f"current_{self.electrode_no}")
        self.current_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.current_label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(self.current_label)
        
        # 弧压（左对齐，启用 HTML 格式）
        self.voltage_label = QLabel("弧压: 0V")
        self.voltage_label.setObjectName(f"voltage_{self.electrode_no}")
        self.voltage_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.voltage_label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(self.voltage_label)
    
    # 3. 更新电极数据（带报警检查）
    def update_data(self, depth_mm: float, current_a: float, voltage_v: float):
        # 保存当前数据值
        self._depth_mm = depth_mm
        self._current_a = current_a
        self._voltage_v = voltage_v
        
        # 报警检查（先检查再显示，避免延迟一帧）
        phase_map = {1: 'u', 2: 'v', 3: 'w'}
        phase = phase_map.get(self.electrode_no, 'u')
        
        old_has_alarm = self.has_alarm
        
        self.depth_status = self.alarm_checker.check_value(f'electrode_depth_{phase}', depth_mm)
        self.current_status = self.alarm_checker.check_value(f'arc_current_{phase}', current_a)
        self.voltage_status = self.alarm_checker.check_value(f'arc_voltage_{phase}', voltage_v)
        
        # 判断是否有报警
        self.has_alarm = (self.alarm_checker.should_blink(self.depth_status) or 
                          self.alarm_checker.should_blink(self.current_status) or 
                          self.alarm_checker.should_blink(self.voltage_status))
        
        # 如果未记录，不报警
        if not self._is_recording():
            self.has_alarm = False
        
        # 播放报警声音（从无报警变为有报警）
        alarm_source = f"electrode_{self.electrode_no}"
        if not old_has_alarm and self.has_alarm:
            sound_manager = get_alarm_sound_manager()
            sound_manager.play_alarm(alarm_source)
        elif old_has_alarm and not self.has_alarm:
            sound_manager = get_alarm_sound_manager()
            sound_manager.stop_alarm(alarm_source)
        
        # 启动或停止闪烁定时器
        if self.has_alarm and not self.blink_timer.isActive():
            self.blink_timer.start(500)
        elif not self.has_alarm and self.blink_timer.isActive():
            self.blink_timer.stop()
            self.blink_visible = True
        
        # 更新 HTML 文本显示
        self._update_labels()
        
        # 更新边框样式
        self.apply_styles()
    
    # 3.1 更新标签文本（根据报警状态和闪烁状态设置颜色）
    def _update_labels(self):
        colors = self.theme_manager.get_colors()
        depth_m = self._depth_mm / 1000.0
        is_recording = self._is_recording()
        
        # 深度颜色
        depth_label_color = colors.TEXT_PRIMARY
        depth_value_color = colors.TEXT_PRIMARY
        depth_value_size = 16
        if self.alarm_checker.should_blink(self.depth_status) and is_recording:
            if self.blink_visible:
                depth_value_color = colors.STATUS_ALARM
            else:
                depth_value_color = self._dim_color(colors.STATUS_ALARM, 0.3)
            depth_value_size = 18
        
        self.depth_label.setText(
            f'<span style="color: {depth_label_color}; font-size: 16px; font-weight: bold;">深度: </span>'
            f'<span style="color: {depth_value_color}; font-size: {depth_value_size}px; font-weight: bold;">{depth_m:.3f}m</span>'
        )
        
        # 弧流颜色
        current_label_color = colors.TEXT_PRIMARY
        current_value_color = colors.TEXT_ACCENT
        current_value_size = 26
        if self.alarm_checker.should_blink(self.current_status) and is_recording:
            if self.blink_visible:
                current_value_color = colors.STATUS_ALARM
            else:
                current_value_color = self._dim_color(colors.STATUS_ALARM, 0.3)
            current_value_size = 28
        
        self.current_label.setText(
            f'<span style="color: {current_label_color}; font-size: 16px; font-weight: bold;">\u5f27\u6d41: </span>'
            f'<span style="color: {current_value_color}; font-size: {current_value_size}px; font-weight: bold;">{self._current_a:.0f}A</span>'
        )
        
        # 弧压颜色
        voltage_label_color = colors.TEXT_PRIMARY
        voltage_value_color = colors.TEXT_ACCENT
        voltage_value_size = 26
        if self.alarm_checker.should_blink(self.voltage_status) and is_recording:
            if self.blink_visible:
                voltage_value_color = colors.STATUS_ALARM
            else:
                voltage_value_color = self._dim_color(colors.STATUS_ALARM, 0.3)
            voltage_value_size = 28
        
        self.voltage_label.setText(
            f'<span style="color: {voltage_label_color}; font-size: 16px; font-weight: bold;">\u5f27\u538b: </span>'
            f'<span style="color: {voltage_value_color}; font-size: {voltage_value_size}px; font-weight: bold;">{self._voltage_v:.0f}V</span>'
        )
    
    # 3.2 将颜色变暗（闪烁低亮度阶段用）
    def _dim_color(self, color: str, alpha: float) -> str:
        qcolor = QColor(color)
        return f"rgba({qcolor.red()}, {qcolor.green()}, {qcolor.blue()}, {alpha})"
    
    # 3.5 检查是否正在记录
    def _is_recording(self) -> bool:
        try:
            from backend.services.batch_service import get_batch_service
            batch_service = get_batch_service()
            return batch_service.is_smelting
        except Exception as e:
            return False
    
    # 4. 切换闪烁状态（与 CardCooling 一致）
    def toggle_blink(self):
        self.blink_visible = not self.blink_visible
        self._update_labels()
        self.apply_styles()
    
    # 5. 应用样式（支持边框闪烁，与 CardCooling 一致）
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        # 根据电极编号选择对应的边框颜色（与图表柱状图颜色一致）
        electrode_colors = {
            1: colors.ELECTRODE_1,
            2: colors.ELECTRODE_2,
            3: colors.ELECTRODE_3,
        }
        normal_border = electrode_colors.get(self.electrode_no, colors.BORDER_GLOW)
        
        # 报警时边框闪烁（与 CardCooling 完全一致的逻辑）
        if self.has_alarm:
            if self.blink_visible:
                border_color = colors.STATUS_ALARM
            else:
                border_color = normal_border
        else:
            border_color = normal_border
        
        # 根据电极编号选择对应的背景颜色（100% 不透明度）
        electrode_bg_colors = {
            1: colors.ELECTRODE_CARD_BG_1,
            2: colors.ELECTRODE_CARD_BG_2,
            3: colors.ELECTRODE_CARD_BG_3,
        }
        bg_color_hex = electrode_bg_colors.get(self.electrode_no, colors.BG_LIGHT)
        
        # 将背景色转换为 RGBA 格式，设置 100% 不透明度
        qcolor_bg = QColor(bg_color_hex)
        bg_color_rgba = f"rgba({qcolor_bg.red()}, {qcolor_bg.green()}, {qcolor_bg.blue()}, 1.0)"
        
        self.setStyleSheet(f"""
            QFrame#electrodeCard {{
                background: {bg_color_rgba};
                border: 1px solid {border_color};
                border-radius: 8px;
            }}
            
            QLabel#electrodeTitle {{
                color: {colors.TEXT_PRIMARY};
                font-size: 18px;
                font-weight: bold;
            }}
        """)
        
        # 设置阴影效果
        from PyQt6.QtWidgets import QGraphicsDropShadowEffect
        dark_factor = 250 if self.electrode_no == 2 else 150
        qcolor = QColor(border_color).darker(dark_factor)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(4)
        shadow.setXOffset(2)
        shadow.setYOffset(2)
        shadow.setColor(qcolor)
        self.setGraphicsEffect(shadow)
    
    # 6. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()
        self._update_labels()

