"""
电极数据卡片组件 - 显示单个电极的深度、弧流、弧压
"""
from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation
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
        
        # 闪烁定时器
        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self.toggle_blink)
        self.blink_visible = True
        
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
        
        # 深度（左对齐）
        self.depth_label = QLabel("深度: 0.000m")
        self.depth_label.setObjectName(f"depth_{self.electrode_no}")
        self.depth_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.depth_label)
        
        # 弧流（左对齐）
        self.current_label = QLabel("弧流: 0A")
        self.current_label.setObjectName(f"current_{self.electrode_no}")
        self.current_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.current_label)
        
        # 弧压（左对齐）
        self.voltage_label = QLabel("弧压: 0V")
        self.voltage_label.setObjectName(f"voltage_{self.electrode_no}")
        self.voltage_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.voltage_label)
    
    # 3. 更新电极数据（带报警检查）
    def update_data(self, depth_mm: float, current_a: float, voltage_v: float):
        """
        更新电极数据
        
        Args:
            depth_mm: 深度（毫米）
            current_a: 弧流（安培）
            voltage_v: 弧压（伏特）
        """
        # 深度转换为米（保留3位小数）
        depth_m = depth_mm / 1000.0
        self.depth_label.setText(f"深度: {depth_m:.3f}m")
        
        # 弧流和弧压使用 HTML 格式，标签正常大小，数值 26px
        self.current_label.setText(f'弧流: <span style="font-size: 26px;">{current_a:.0f}A</span>')
        self.voltage_label.setText(f'弧压: <span style="font-size: 26px;">{voltage_v:.0f}V</span>')
        
        # 报警检查
        phase_map = {1: 'u', 2: 'v', 3: 'w'}
        phase = phase_map.get(self.electrode_no, 'u')
        
        # 记录旧的报警状态
        old_depth_status = self.depth_status
        old_current_status = self.current_status
        old_voltage_status = self.voltage_status
        
        # 检查电极深度（AlarmChecker 内部会检查批次状态）
        self.depth_status = self.alarm_checker.check_value(f'electrode_depth_{phase}', depth_mm)
        
        # 检查弧流
        self.current_status = self.alarm_checker.check_value(f'arc_current_{phase}', current_a)
        
        # 检查弧压
        self.voltage_status = self.alarm_checker.check_value(f'arc_voltage_{phase}', voltage_v)
        
        # 如果从非报警变为报警，播放声音（只有在记录时才播放）
        has_old_alarm = any([self.alarm_checker.should_blink(s) for s in [old_depth_status, old_current_status, old_voltage_status]])
        has_new_alarm = any([self.alarm_checker.should_blink(s) for s in [self.depth_status, self.current_status, self.voltage_status]])
        
        if not has_old_alarm and has_new_alarm:
            # 播放报警声音（通过全局管理器，内部会检查批次状态）
            sound_manager = get_alarm_sound_manager()
            sound_manager.play_alarm()
        
        # 更新样式
        self.update_alarm_styles()
        
        # 启动或停止闪烁（只有在记录时才闪烁）
        need_blink = (self.alarm_checker.should_blink(self.depth_status) or 
                      self.alarm_checker.should_blink(self.current_status) or 
                      self.alarm_checker.should_blink(self.voltage_status))
        
        # 检查是否正在记录
        if not self._is_recording():
            need_blink = False
        
        if need_blink and not self.blink_timer.isActive():
            self.blink_timer.start(500)  # 500ms 闪烁一次
        elif not need_blink and self.blink_timer.isActive():
            self.blink_timer.stop()
            self.blink_visible = True
            self.update_alarm_styles()
    
    # 3.5 检查是否正在记录
    def _is_recording(self) -> bool:
        """检查是否正在记录（有批次号且正在冶炼）"""
        try:
            from backend.services.batch_service import get_batch_service
            batch_service = get_batch_service()
            return batch_service.is_smelting
        except Exception as e:
            return False
    
    # 4. 切换闪烁状态
    def toggle_blink(self):
        """切换闪烁状态"""
        self.blink_visible = not self.blink_visible
        self.update_alarm_styles()
    
    # 5. 更新报警样式
    def update_alarm_styles(self):
        """根据报警状态更新样式"""
        colors = self.theme_manager.get_colors()
        
        # 深度颜色
        depth_color = self.alarm_checker.get_status_color(self.depth_status, colors)
        if self.alarm_checker.should_blink(self.depth_status) and not self.blink_visible:
            depth_color = colors.BG_LIGHT  # 闪烁时隐藏
        
        # 弧流颜色
        current_color = self.alarm_checker.get_status_color(self.current_status, colors)
        if self.alarm_checker.should_blink(self.current_status) and not self.blink_visible:
            current_color = colors.BG_LIGHT  # 闪烁时隐藏
        
        # 弧压颜色
        voltage_color = self.alarm_checker.get_status_color(self.voltage_status, colors)
        if self.alarm_checker.should_blink(self.voltage_status) and not self.blink_visible:
            voltage_color = colors.BG_LIGHT  # 闪烁时隐藏
        
        # 应用样式
        self.depth_label.setStyleSheet(f"""
            color: {depth_color};
            font-size: 16px;
            font-weight: bold;
        """)
        
        self.current_label.setStyleSheet(f"""
            color: {current_color};
            font-size: 16px;
            font-weight: bold;
        """)
        
        self.voltage_label.setStyleSheet(f"""
            color: {voltage_color};
            font-size: 16px;
            font-weight: bold;
        """)
    
    # 6. 应用样式
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
        """)
        
        # 更新报警样式
        self.update_alarm_styles()
    
    # 7. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()

