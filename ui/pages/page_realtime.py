"""
3#电炉实时数据页面 - 使用组件化架构
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt6.QtCore import QTimer
from datetime import datetime
from ui.styles.themes import ThemeManager
from ui.widgets.common.panel_tech import PanelTech
from ui.widgets.common.chart_tech import ChartTech
from ui.widgets.common.dialog_message import show_error, show_warning
from ui.widgets.realtime_data.card_data import CardData, DataItem
from ui.widgets.realtime_data.chart_electrode import ChartElectrode, ElectrodeData
from ui.widgets.realtime_data.butterfly_vaue import WidgetValveGrid
from ui.widgets.realtime_data import PanelFurnaceBg
from ui.widgets.realtime_data.panel_furnace.dialog_batch_config import DialogBatchConfig
from ui.widgets.realtime_data.hopper.card_hopper import CardHopper
from backend.services.batch_service import get_batch_service
from backend.bridge.data_cache import get_data_cache
from loguru import logger


class PageRealtime(QWidget):
    """3#电炉实时数据页面"""
    
    # 1. 初始化页面
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        
        # 获取后端服务
        self.batch_service = get_batch_service()
        self.data_cache = get_data_cache()
        
        # 实时数据（初始值全部为 0，从后端读取真实数据）
        self.mock_data = {
            'batch_no': '',
            'start_time': '',
            'run_duration': '00:00:00',
            'is_smelting': False,
            'electrodes': [
                {'depth_mm': 0.0, 'current_a': 0.0, 'voltage_v': 0.0},
                {'depth_mm': 0.0, 'current_a': 0.0, 'voltage_v': 0.0},
                {'depth_mm': 0.0, 'current_a': 0.0, 'voltage_v': 0.0},
            ],
            'valves': [
                {'status': '00', 'open_percent': 0.0},
                {'status': '00', 'open_percent': 0.0},
                {'status': '00', 'open_percent': 0.0},
                {'status': '00', 'open_percent': 0.0},
            ],
            'cooling_shell': {
                'flow': 0.0,
                'pressure': 0.0,
                'total': 0.0,
            },
            'cooling_cover': {
                'flow': 0.0,
                'pressure': 0.0,
                'total': 0.0,
            },
            'filter_diff': 0.0,
            'hopper': {
                'weight': 0.0,
                'feeding_total': 0.0,
                'upper_limit': 5000.0,  # 上限保持默认值
            },
            'power': 0.0,      # 总功率 kW
            'energy': 0.0,     # 总能耗 kWh
        }
        
        self.init_ui()
        self.apply_styles()
        
        # 高弧流报警弹窗标志（防止重复弹窗）
        self.high_current_alarm_shown = False
        
        # 监听主题变化
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
        
        # 启动卡片数据更新定时器（固定 0.5s 刷新一次）
        self.card_update_timer = QTimer()
        self.card_update_timer.timeout.connect(self.update_realtime_data)
        self.card_update_timer.start(500)  # 500ms = 0.5s（固定，不受轮询速度影响）
        
        # 启动图表数据更新定时器（跟随 DB1 轮询速度）
        self.chart_update_timer = QTimer()
        self.chart_update_timer.timeout.connect(self.update_chart_data)
        
        # 从配置获取初始刷新间隔
        from backend.config.polling_config import get_polling_config
        self.polling_config = get_polling_config()
        initial_interval = int(self.polling_config.get_polling_interval() * 1000)  # 转换为毫秒
        self.chart_update_timer.start(initial_interval)
        
        # 监听轮询速度变化
        self.polling_config.register_callback(self.on_polling_speed_changed)
        
        logger.info(f"图表定时器已启动: {initial_interval}ms 刷新")
        
        # 初始化批次状态（只在启动时更新一次）
        # 这里会自动同步后端状态，如果后端正在冶炼，UI 会自动恢复
        self.update_batch_status()
        
        # 如果后端正在冶炼，切换 DB1 到高速模式，并初始化投料记录
        try:
            status = self.batch_service.get_status()
            if status['is_smelting']:
                from backend.services.polling_loops_v2 import switch_db1_speed
                switch_db1_speed(high_speed=True)
                logger.info(f"检测到后端正在冶炼（批次: {status['batch_code']}），已切换 DB1 到高速模式")
                
                # 初始化投料记录
                batch_code = status['batch_code']
                if batch_code:
                    logger.info(f"初始化批次 {batch_code} 的投料记录...")
                    self.hopper_card.init_feeding_records(batch_code)
        except Exception as e:
            logger.error(f"检查后端状态失败: {e}", exc_info=True)
    
    # 2. 初始化 UI
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        
        # 上部分 74%
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(8)
        
        # 左侧 40%
        self.create_left_panel()
        top_layout.addWidget(self.left_panel, stretch=40)
        
        # 右侧 60% (电炉背景面板组件)
        self.furnace_panel = PanelFurnaceBg()
        self.furnace_panel.batch_info_bar.start_smelting_clicked.connect(self.on_start_smelting)
        self.furnace_panel.batch_info_bar.abandon_batch_clicked.connect(self.on_abandon_batch)
        self.furnace_panel.batch_info_bar.terminate_smelting_clicked.connect(self.on_terminate_smelting)
        top_layout.addWidget(self.furnace_panel, stretch=60)
        
        main_layout.addWidget(top_widget, stretch=74)
        
        # 下部分 26%
        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(8)
        
        # 料仓模块 40%（和上方左侧对齐）
        self.create_hopper_panel()
        bottom_layout.addWidget(self.hopper_card, stretch=40)
        
        # 炉盖/炉皮/过滤器容器 60%（和上方右侧对齐）
        cooling_container = QWidget()
        cooling_layout = QHBoxLayout(cooling_container)
        cooling_layout.setContentsMargins(0, 0, 0, 0)
        cooling_layout.setSpacing(8)
        
        # 炉皮模块 37%
        self.create_cooling_shell_panel()
        cooling_layout.addWidget(self.cooling_shell_panel, stretch=37)
        
        # 炉盖模块 37%
        self.create_cooling_cover_panel()
        cooling_layout.addWidget(self.cooling_cover_panel, stretch=37)
        
        # 过滤器压差模块 26%
        self.create_filter_panel()
        cooling_layout.addWidget(self.filter_panel, stretch=26)
        
        bottom_layout.addWidget(cooling_container, stretch=60)
        
        main_layout.addWidget(bottom_widget, stretch=26)
        
        # 激活主布局，让上下部分的 stretch 生效
        main_layout.activate()
        
        # 设置 SizePolicy 让 stretch 生效
        from PyQt6.QtWidgets import QSizePolicy
        top_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        bottom_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # 调试：延迟打印实际高度
        from PyQt6.QtCore import QTimer
        def print_heights():
            logger.info(f"=== 布局调试信息 ===")
            logger.info(f"页面总高度: {self.height()}")
            logger.info(f"上部分高度: {top_widget.height()} (应该是 84%)")
            logger.info(f"下部分高度: {bottom_widget.height()} (应该是 26%)")
            logger.info(f"上部分实际比例: {top_widget.height() / self.height() * 100:.1f}%")
            logger.info(f"下部分实际比例: {bottom_widget.height() / self.height() * 100:.1f}%")
            logger.info(f"左侧蝶阀高度: {self.valve_grid.height()}")
            logger.info(f"左侧弧流高度: {self.chart_panel.height()}")
        QTimer.singleShot(1000, print_heights)  # 1秒后打印
    
    # 3. 创建左侧面板
    def create_left_panel(self):
        self.left_panel = QWidget()
        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)
        
        # 上半部分：蝶阀网格组件 45%
        self.valve_grid = WidgetValveGrid()
        # 设置 sizePolicy 为 Expanding，让 stretch 生效
        from PyQt6.QtWidgets import QSizePolicy
        self.valve_grid.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        left_layout.addWidget(self.valve_grid, stretch=45)
        
        # 下半部分：弧流柱状图 55%
        self.create_electrode_chart()
        self.chart_panel.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        left_layout.addWidget(self.chart_panel, stretch=55)
        
        # 激活布局，让 stretch 生效
        left_layout.activate()
    
    # 4. 创建电极电流图表
    def create_electrode_chart(self):
        self.chart_panel = ChartTech()  # 使用图表专用组件，内边距为0
        
        # 创建电极电流图表 (固定Y轴0-8 KA)
        self.electrode_chart = ChartElectrode()
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.electrode_chart)
        self.chart_panel.set_content_layout(layout)
    
    # 5. 创建料仓重量面板
    def create_hopper_panel(self):
        # 直接使用 CardHopper 组件，不使用 PanelTech 包裹
        self.hopper_card = CardHopper()
        self.hopper_card.set_limit_clicked.connect(self.show_hopper_detail)
    
    # 6. 创建炉皮冷却水面板（新布局：左对齐，3行显示）
    def create_cooling_shell_panel(self):
        from ui.widgets.realtime_data.card_cooling import CardCooling
        
        self.cooling_shell_panel = CardCooling(
            title="炉皮冷却水",
            alarm_id="cooling_shell",  # 英文标识符
            items=[
                {"label": "流速:", "value": "0.00", "unit": "m\u00b3/h", "alarm_param": "cooling_flow_shell"},
                {"label": "水压:", "value": "0.0", "unit": "kPa", "alarm_param": "cooling_pressure_shell"},
                {"label": "用量:", "value": "0.00", "unit": "m\u00b3", "alarm_param": None},
            ]
        )
    
    # 7. 创建炉盖冷却水面板（新布局：左对齐，3行显示）
    def create_cooling_cover_panel(self):
        from ui.widgets.realtime_data.card_cooling import CardCooling
        
        self.cooling_cover_panel = CardCooling(
            title="炉盖冷却水",
            alarm_id="cooling_cover",  # 英文标识符
            items=[
                {"label": "流速:", "value": "0.00", "unit": "m\u00b3/h", "alarm_param": "cooling_flow_cover"},
                {"label": "水压:", "value": "0.0", "unit": "kPa", "alarm_param": "cooling_pressure_cover"},
                {"label": "用量:", "value": "0.00", "unit": "m\u00b3", "alarm_param": None},
            ]
        )
    
    # 8. 创建过滤器压差面板（新布局：左对齐，3行显示）
    def create_filter_panel(self):
        from ui.widgets.realtime_data.card_cooling import CardCooling
        
        self.filter_panel = CardCooling(
            title="过滤器",
            alarm_id="filter",  # 英文标识符
            items=[
                {"label": "压差:", "value": "0.0", "unit": "kPa", "alarm_param": "filter_pressure_diff"},
            ]
        )
    
    # 8. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        self.setStyleSheet(f"""
            PageRealtime {{
                background: {colors.BG_DEEP};
            }}
        """)
    
    # 9. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()
    
    # 10. 更新实时数据（每 0.5s 刷新一次）
    def update_realtime_data(self):
        """
        每 0.5s 刷新一次的数据：
        1. 蝶阀开度和状态
        2. 三相电极电流、电压
        3. 电极深度
        4. 冷却水流量、水压、累计流量
        5. 过滤器压差
        6. 料仓重量、投料累计
        7. 功率、能耗
        """
        try:
            # 从 DataCache 读取实时数据
            sensor_data = self.data_cache.get_sensor_data()
            arc_data = self.data_cache.get_arc_data()
            
            # ========================================
            # 1. 更新蝶阀开度和状态（每 0.5s）
            # ========================================
            if sensor_data and 'valve_openness' in sensor_data:
                valve_openness = sensor_data['valve_openness']
                valve_status = sensor_data.get('valve_status', {})
                valve_status_byte = valve_status.get('raw_byte', 0)
                
                valves_data = []
                for valve_id in range(1, 5):
                    # 解析状态
                    bit_offset = (valve_id - 1) * 2
                    bit_close = (valve_status_byte >> bit_offset) & 0x01
                    bit_open = (valve_status_byte >> (bit_offset + 1)) & 0x01
                    status = f"{bit_close}{bit_open}"
                    
                    # 获取开度
                    openness = valve_openness.get(valve_id, 0.0)
                    
                    valves_data.append({
                        'status': status,
                        'open_percent': openness
                    })
                
                # 批量更新蝶阀
                self.valve_grid.update_all_valves(valves_data)
            
            # ========================================
            # 2. 更新三相电极电流、电压（每 0.5s）
            # ========================================
            if arc_data:
                arc_current = arc_data.get('arc_current', {})
                arc_voltage = arc_data.get('arc_voltage', {})
                setpoints = arc_data.get('setpoints', {})
                
                # 更新电极数据
                electrodes = []
                for phase in ['U', 'V', 'W']:
                    current = arc_current.get(phase, 0.0)
                    voltage = arc_voltage.get(phase, 0.0)
                    setpoint = setpoints.get(phase, 0.0)
                    
                    # 更新电极卡片（电流、电压）
                    phase_idx = ['U', 'V', 'W'].index(phase)
                    self.mock_data['electrodes'][phase_idx]['current_a'] = current
                    self.mock_data['electrodes'][phase_idx]['voltage_v'] = voltage
                    
                    # 添加到电极图表数据（包含弧压）
                    electrodes.append(ElectrodeData(
                        f"{phase}相",
                        setpoint,  # 设定值
                        current,   # 实际值
                        voltage    # 弧压
                    ))
                
                # 更新电极电流图表
                deadzone = arc_data.get('manual_deadzone_percent', 15.0)
                self.electrode_chart.update_data(electrodes, deadzone)
                
                # 高弧流报警检测（>8000A 弹窗 + 声音）
                if self.mock_data['is_smelting']:
                    alarm_phases = []
                    for phase in ['U', 'V', 'W']:
                        c = arc_current.get(phase, 0.0)
                        if c > 8000:
                            alarm_phases.append(f"{phase}相: {c:.0f}A")
                    
                    from ui.utils.alarm_sound_manager import get_alarm_sound_manager
                    if alarm_phases and not self.high_current_alarm_shown:
                        self.high_current_alarm_shown = True
                        # 播放报警声音
                        get_alarm_sound_manager().play_alarm("high_current")
                        # 延迟弹窗，避免阻塞当前更新周期
                        msg = f"弧流超过 8000A!\n\n" + "\n".join(alarm_phases)
                        QTimer.singleShot(0, lambda m=msg: show_warning(self, "高弧流报警", m))
                    elif not alarm_phases:
                        self.high_current_alarm_shown = False
                        get_alarm_sound_manager().stop_alarm("high_current")
            
            # ========================================
            # 3. 更新电极深度（每 0.5s）
            # ========================================
            if sensor_data and 'electrode_depths' in sensor_data:
                electrode_depths = sensor_data['electrode_depths']
                for i, (key, data) in enumerate(electrode_depths.items()):
                    if isinstance(data, dict):
                        depth_mm = data.get('distance_mm', 0.0)
                        self.mock_data['electrodes'][i]['depth_mm'] = depth_mm
            
            # 批量更新电极卡片
            self.furnace_panel.update_all_electrodes(self.mock_data['electrodes'])
            
            # ========================================
            # 4. 更新冷却水数据（每 0.5s）
            # ========================================
            if sensor_data and 'cooling' in sensor_data:
                cooling = sensor_data['cooling']
                flows = cooling.get('flows', {})
                pressures = cooling.get('pressures', {})
                pressure_diff = cooling.get('pressure_diff', {})
                cover_total = cooling.get('cover_total', 0.0)
                shell_total = cooling.get('shell_total', 0.0)
                
                # 更新炉皮冷却水
                flow_1 = flows.get('WATER_FLOW_1', {})
                press_1 = pressures.get('WATER_PRESS_1', {})
                self.mock_data['cooling_shell']['flow'] = flow_1.get('flow', 0.0) if isinstance(flow_1, dict) else 0.0
                self.mock_data['cooling_shell']['pressure'] = press_1.get('pressure', 0.0) if isinstance(press_1, dict) else 0.0
                self.mock_data['cooling_shell']['total'] = shell_total
                
                # 更新炉盖冷却水
                flow_2 = flows.get('WATER_FLOW_2', {})
                press_2 = pressures.get('WATER_PRESS_2', {})
                self.mock_data['cooling_cover']['flow'] = flow_2.get('flow', 0.0) if isinstance(flow_2, dict) else 0.0
                self.mock_data['cooling_cover']['pressure'] = press_2.get('pressure', 0.0) if isinstance(press_2, dict) else 0.0
                self.mock_data['cooling_cover']['total'] = cover_total
                
                # 过滤器压差
                self.mock_data['filter_diff'] = pressure_diff.get('value', 0.0) if isinstance(pressure_diff, dict) else 0.0
            
            # 更新冷却水卡片（无论 sensor_data 是否有新数据，都用缓存值刷新，保证报警状态能被检测）
            self.cooling_shell_panel.update_items([
                {"label": "流速:", "value": f"{self.mock_data['cooling_shell']['flow']:.2f}", "unit": "m\u00b3/h", "alarm_param": "cooling_flow_shell"},
                {"label": "水压:", "value": f"{self.mock_data['cooling_shell']['pressure']:.1f}", "unit": "kPa", "alarm_param": "cooling_pressure_shell"},
                {"label": "用量:", "value": f"{self.mock_data['cooling_shell']['total']:.2f}", "unit": "m\u00b3", "alarm_param": None},
            ])
            
            self.cooling_cover_panel.update_items([
                {"label": "流速:", "value": f"{self.mock_data['cooling_cover']['flow']:.2f}", "unit": "m\u00b3/h", "alarm_param": "cooling_flow_cover"},
                {"label": "水压:", "value": f"{self.mock_data['cooling_cover']['pressure']:.1f}", "unit": "kPa", "alarm_param": "cooling_pressure_cover"},
                {"label": "用量:", "value": f"{self.mock_data['cooling_cover']['total']:.2f}", "unit": "m\u00b3", "alarm_param": None},
            ])
            
            self.filter_panel.update_items([
                {"label": "压差:", "value": f"{self.mock_data['filter_diff']:.1f}", "unit": "kPa", "alarm_param": "filter_pressure_diff"},
            ])
            
            # ========================================
            # 5. 更新料仓数据（每 0.5s）
            # ========================================
            if sensor_data and 'hopper' in sensor_data:
                hopper = sensor_data['hopper']
                new_weight = hopper.get('weight', 0.0)
                new_feeding_total = hopper.get('feeding_total', 0.0)
                
                # 数据验证：如果新数据都为0，且已有历史数据，则跳过本次更新
                # 原因：PLC通信异常时会读取到0值，保持上一次的有效数据更合理
                should_update_ui = True
                
                if new_weight == 0.0 and new_feeding_total == 0.0:
                    # 如果已经有历史数据，跳过本次UI更新
                    if self.mock_data['hopper']['weight'] > 0.0 or self.mock_data['hopper']['feeding_total'] > 0.0:
                        should_update_ui = False  # 关键：不更新UI，避免闪烁
                    else:
                        # 如果是首次数据（都为0），则正常更新
                        self.mock_data['hopper']['weight'] = new_weight
                        self.mock_data['hopper']['feeding_total'] = new_feeding_total
                else:
                    # 数据有效，正常更新
                    self.mock_data['hopper']['weight'] = new_weight
                    self.mock_data['hopper']['feeding_total'] = new_feeding_total
                
                # 只有在需要更新UI时才调用 update_data()
                if should_update_ui:
                    # 获取料仓状态（四种状态）
                    hopper_state = hopper.get('state', 'idle')
                    
                    # 从 DB18 读取料仓上限值
                    upper_limit = self.data_cache.get_hopper_upper_limit()
                    self.mock_data['hopper']['upper_limit'] = upper_limit
                    
                    # 获取当前批次号
                    batch_code = self.mock_data.get('batch_no', '')
                    
                    # 使用验证后的数据更新卡片（传入批次号，用于检测投料累计变化）
                    self.hopper_card.update_data(
                        hopper_weight=self.mock_data['hopper']['weight'],
                        feeding_total=self.mock_data['hopper']['feeding_total'],
                        upper_limit=upper_limit,
                        state=hopper_state,
                        batch_code=batch_code
                    )
            
            # ========================================
            # 6. 更新功率能耗（每 0.5s）
            # ========================================
            if arc_data:
                power_total = arc_data.get('power_total', 0.0)
                energy_total = arc_data.get('energy_total', 0.0)  # 从缓存读取能耗
                
                self.mock_data['power'] = power_total
                self.mock_data['energy'] = energy_total  # 更新能耗
                
                self.furnace_panel.update_power_energy(
                    self.mock_data['power'],
                    self.mock_data['energy']
                )
            
        except Exception as e:
            logger.error(f"更新实时数据异常: {e}", exc_info=True)
        
        # ========================================
        # 7. 更新批次运行时长（每 0.5s）
        # ========================================
        if self.mock_data['is_smelting']:
            try:
                status = self.batch_service.get_status()
                elapsed_seconds = status['elapsed_seconds']
                hours = int(elapsed_seconds // 3600)
                minutes = int((elapsed_seconds % 3600) // 60)
                seconds = int(elapsed_seconds % 60)
                self.mock_data['run_duration'] = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            except:
                pass
        
        # 更新炉次信息
        self.furnace_panel.update_batch_info(
            self.mock_data['batch_no'],
            self.mock_data['start_time'],
            self.mock_data['run_duration']
        )
    
    # 10.1 更新图表数据（跟随轮询速度）
    def update_chart_data(self):
        """
        更新图表数据（刷新频率跟随轮询速度）
        - 0.2s 轮询时，图表每 0.2s 刷新
        - 0.5s 轮询时，图表每 0.5s 刷新
        """
        try:
            # 从 DataCache 读取弧流数据
            arc_data = self.data_cache.get_arc_data()
            
            if arc_data:
                arc_current = arc_data.get('arc_current', {})
                setpoints = arc_data.get('setpoints', {})
                deadzone = arc_data.get('manual_deadzone_percent', 15.0)
                
                # 构建电极数据
                electrodes = []
                for phase in ['U', 'V', 'W']:
                    current = arc_current.get(phase, 0.0)
                    setpoint = setpoints.get(phase, 0.0)
                    
                    electrodes.append(ElectrodeData(
                        f"{phase}相",
                        setpoint,  # 设定值
                        current    # 实际值
                    ))
                
                # 更新电极电流图表
                self.electrode_chart.update_data(electrodes, deadzone)
        
        except Exception as e:
            logger.error(f"更新图表数据异常: {e}", exc_info=True)
    
    # 10.2 轮询速度变化回调
    def on_polling_speed_changed(self, speed):
        """轮询速度变化时，更新图表刷新间隔
        
        Args:
            speed: "0.2s" 或 "0.5s"
        """
        if speed == "0.2s":
            interval_ms = 200
        else:
            interval_ms = 500
        
        # 更新图表定时器间隔
        self.chart_update_timer.setInterval(interval_ms)
        logger.info(f"图表刷新间隔已更新: {interval_ms}ms")
    
    # 11. 开始冶炼（显示批次配置对话框）
    def on_start_smelting(self):
        """点击开始冶炼按钮，弹出批次配置对话框"""
        logger.info("点击开始冶炼按钮")
        
        # 先检查后端状态，如果已经在冶炼，则同步 UI 状态
        try:
            status = self.batch_service.get_status()
            if status['is_smelting']:
                logger.warning(f"后端已在冶炼中，批次号: {status['batch_code']}，同步 UI 状态")
                
                # 同步 UI 状态
                self.update_batch_status()
                
                # 提示用户
                from ui.widgets.common.dialog_message import show_warning
                show_warning(
                    self,
                    "冶炼已在进行中",
                    f"当前批次: {status['batch_code']}\n已运行: {int(status['elapsed_seconds'])}秒\n\nUI 状态已同步"
                )
                return
        except Exception as e:
            logger.error(f"检查后端状态失败: {e}", exc_info=True)
        
        # 创建批次配置对话框（炉号从 .env 配置读取）
        dialog = DialogBatchConfig(parent=self)
        dialog.batch_confirmed.connect(self.on_batch_confirmed)
        dialog.exec()
    
    # 12. 批次配置确认
    def on_batch_confirmed(self, batch_code: str):
        """批次配置确认后，调用后端服务开始冶炼"""
        logger.info(f"批次配置确认: {batch_code}")
        
        try:
            # 调用后端服务开始冶炼
            result = self.batch_service.start(batch_code)
            
            if result['success']:
                logger.info(f"冶炼开始成功: {result['message']}")
                
                # 切换 DB1 轮询速度到高速模式 (0.5s)
                from backend.services.polling_loops_v2 import switch_db1_speed
                switch_db1_speed(high_speed=True)
                logger.info("已切换 DB1 轮询到高速模式 (0.5s)")
                
                # 成功时不弹窗，直接更新批次状态
                self.update_batch_status()
                
                # 初始化料仓投料记录（查询该批次的历史投料记录）
                logger.info(f"初始化批次 {batch_code} 的投料记录...")
                self.hopper_card.init_feeding_records(batch_code)
            else:
                # 失败时显示自定义错误弹窗
                logger.warning(f"冶炼开始失败: {result['message']}")
                show_warning(self, "开始冶炼失败", result['message'])
        
        except Exception as e:
            # 异常时显示自定义错误弹窗
            logger.error(f"开始冶炼异常: {e}", exc_info=True)
            show_error(self, "开始冶炼错误", f"开始冶炼失败: {str(e)}")
    
    # 13. 放弃炉次（先停止冶炼，再删除数据）
    def on_abandon_batch(self):
        """放弃炉次（先停止冶炼，再删除该批次的所有数据）"""
        logger.info("点击放弃炉次按钮")
        
        # 获取当前批次号
        batch_code = self.mock_data.get('batch_no', '')
        if not batch_code:
            from ui.widgets.common.dialog_confirm import DialogError
            dialog = DialogError(
                "警告",
                "当前没有进行中的批次",
                self
            )
            dialog.exec()
            return
        
        # 二次确认
        from ui.widgets.common.dialog_confirm import DialogConfirm
        message = (
            f"确定要放弃当前炉次吗？\n\n"
            f"批次号: {batch_code}\n"
            f"开始时间: {self.mock_data.get('start_time', '')}\n"
            f"运行时长: {self.mock_data.get('run_duration', '')}\n\n"
            f"警告: 此操作将删除该批次的所有历史数据，且无法恢复！"
        )
        dialog = DialogConfirm("确认放弃炉次", message, self)
        
        if dialog.exec() == dialog.DialogCode.Accepted:
            try:
                # 1. 删除该批次的所有数据
                from backend.bridge.history_query import get_history_query_service
                history_service = get_history_query_service()
                
                delete_result = history_service.delete_batch_data(batch_code)
                
                if delete_result['success']:
                    logger.info(f"批次数据已删除: {delete_result['message']}")
                    
                    # 2. 停止批次（清除批次状态）
                    result = self.batch_service.stop()
                    
                    if result['success']:
                        logger.info(f"批次已停止: {result['message']}")
                    
                    # 3. 切换 DB1 轮询速度回低速模式 (5s)
                    from backend.services.polling_loops_v2 import switch_db1_speed
                    switch_db1_speed(high_speed=False)
                    logger.info("已切换 DB1 轮询到低速模式 (5s)")
                    
                    # 4. 立即更新批次状态（成功不弹窗）
                    self.update_batch_status()
                else:
                    # 失败时显示错误弹窗
                    logger.error(f"删除批次数据失败: {delete_result['message']}")
                    from ui.widgets.common.dialog_confirm import DialogError
                    error_dialog = DialogError(
                        "操作失败",
                        f"删除数据失败: {delete_result['message']}",
                        self
                    )
                    error_dialog.exec()
            
            except Exception as e:
                logger.error(f"放弃炉次异常: {e}", exc_info=True)
                from ui.widgets.common.dialog_confirm import DialogError
                error_dialog = DialogError(
                    "操作失败",
                    f"放弃炉次失败: {str(e)}",
                    self
                )
                error_dialog.exec()
    
    # 14. 终止记录（长按3秒触发）
    def on_terminate_smelting(self):
        """终止记录（长按3秒后触发，结束批次并清除状态）"""
        logger.info("长按3秒，触发终止记录")
        
        # 二次确认
        from ui.widgets.common.dialog_confirm import DialogConfirm
        message = (
            "确定要终止当前记录吗？\n\n"
            "终止后将结束当前批次，停止写入数据库。\n"
            "批次数据将保留在数据库中。"
        )
        dialog = DialogConfirm("确认终止", message, self)
        
        if dialog.exec() == dialog.DialogCode.Accepted:
            try:
                # 调用后端服务停止冶炼（结束批次）
                result = self.batch_service.stop()
                
                if result['success']:
                    logger.info(f"记录终止成功: {result['message']}")
                    
                    # 切换 DB1 轮询速度回低速模式 (5s)
                    from backend.services.polling_loops_v2 import switch_db1_speed
                    switch_db1_speed(high_speed=False)
                    logger.info("已切换 DB1 轮询到低速模式 (5s)")
                    
                    # 立即更新批次状态（成功不弹窗）
                    self.update_batch_status()
                else:
                    # 失败时显示错误弹窗
                    logger.warning(f"记录终止失败: {result['message']}")
                    from ui.widgets.common.dialog_confirm import DialogError
                    error_dialog = DialogError(
                        "操作失败",
                        result['message'],
                        self
                    )
                    error_dialog.exec()
            
            except Exception as e:
                logger.error(f"终止记录异常: {e}", exc_info=True)
                from ui.widgets.common.dialog_confirm import DialogError
                error_dialog = DialogError(
                    "操作失败",
                    f"终止记录失败: {str(e)}",
                    self
                )
                error_dialog.exec()
    
    # 15. 更新批次状态（从后端服务读取）
    def update_batch_status(self):
        """从后端服务读取批次状态并更新UI"""
        try:
            status = self.batch_service.get_status()
            
            is_smelting = status['is_smelting']
            batch_code = status['batch_code'] or ''
            start_time_str = status['start_time'] or ''
            elapsed_seconds = status['elapsed_seconds']
            
            # 格式化开始时间（只显示时分秒）
            if start_time_str:
                try:
                    start_dt = datetime.fromisoformat(start_time_str)
                    start_time_display = start_dt.strftime('%H:%M:%S')
                except:
                    start_time_display = start_time_str
            else:
                start_time_display = ''
            
            # 格式化运行时长
            hours = int(elapsed_seconds // 3600)
            minutes = int((elapsed_seconds % 3600) // 60)
            seconds = int(elapsed_seconds % 60)
            run_duration = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
            # 更新 UI（is_smelting 包含 RUNNING 和 PAUSED 状态）
            self.furnace_panel.batch_info_bar.set_smelting_state(
                is_smelting=is_smelting,
                batch_no=batch_code,
                start_time=start_time_display,
                run_duration=run_duration
            )
            
            # 更新模拟数据
            self.mock_data['is_smelting'] = is_smelting
            self.mock_data['batch_no'] = batch_code
            self.mock_data['start_time'] = start_time_display
            self.mock_data['run_duration'] = run_duration
        
        except Exception as e:
            logger.error(f"更新批次状态异常: {e}", exc_info=True)
    
    # 16. 显示料仓详情弹窗（设置料仓上限）
    def show_hopper_detail(self):
        """显示设置料仓上限弹窗"""
        try:
            from ui.widgets.realtime_data.hopper.dialog_set_limit import DialogSetLimit
            
            # 获取当前料仓上限
            sensor_data = self.data_cache.get_sensor_data()
            if sensor_data and 'hopper' in sensor_data:
                upper_limit = sensor_data['hopper'].get('upper_limit', 5000.0)
            else:
                upper_limit = self.mock_data['hopper']['upper_limit']
            
            # 创建弹窗
            dialog = DialogSetLimit(upper_limit, self)
            dialog.limit_set.connect(self.on_hopper_upper_limit_set)
            dialog.exec()
            
        except Exception as e:
            logger.error(f"显示设置料仓上限弹窗失败: {e}", exc_info=True)
            from ui.widgets.common.dialog_message import show_error
            show_error(self, "打开失败", f"无法打开设置料仓上限弹窗:\n{str(e)}")
    
    # 17. 料仓上限设置完成
    def on_hopper_upper_limit_set(self, limit: float):
        """料仓上限设置完成"""
        logger.info(f"料仓上限已设置: {limit} kg")
        
        # 更新模拟数据
        self.mock_data['hopper']['upper_limit'] = limit
        
        # TODO: 将料仓上限保存到配置文件或数据库
        
        # 立即更新料仓面板显示
        self.update_hopper_card()
    
    # 17.1 更新料仓卡片
    def update_hopper_card(self):
        """更新料仓卡片 (从缓存读取实时数据)"""
        try:
            # 从缓存读取传感器数据
            sensor_data = self.data_cache.get_sensor_data()
            
            if sensor_data and 'hopper' in sensor_data:
                hopper_data = sensor_data['hopper']
                hopper_weight = hopper_data.get('weight', 0.0)
                feeding_total = hopper_data.get('feeding_total', 0.0)
                upper_limit = hopper_data.get('upper_limit', 5000.0)
                hopper_state = hopper_data.get('state', 'idle')
            else:
                # 使用模拟数据
                hopper_weight = self.mock_data['hopper']['weight']
                feeding_total = self.mock_data['hopper']['feeding_total']
                upper_limit = self.mock_data['hopper']['upper_limit']
                hopper_state = 'idle'
            
            # 更新卡片
            self.hopper_card.update_data(hopper_weight, feeding_total, upper_limit, hopper_state)
            
        except Exception as e:
            logger.error(f"更新料仓卡片失败: {e}", exc_info=True)
    
    # 18. 页面隐藏时停止定时器（防止定时器泄漏）
    def hideEvent(self, event):
        """页面隐藏时停止定时器"""
        logger.info("PageRealtime 隐藏，停止定时器")
        self.card_update_timer.stop()
        self.chart_update_timer.stop()
        super().hideEvent(event)
    
    # 19. 页面显示时启动定时器
    def showEvent(self, event):
        """页面显示时启动定时器"""
        logger.info("PageRealtime 显示，启动定时器")
        self.card_update_timer.start(500)
        
        # 图表定时器使用当前配置的间隔
        interval_ms = int(self.polling_config.get_polling_interval() * 1000)
        self.chart_update_timer.start(interval_ms)
        
        super().showEvent(event)
    
    # 20. 页面销毁时清理资源
    def closeEvent(self, event):
        """页面关闭时清理资源"""
        logger.info("PageRealtime 关闭，清理资源")
        
        # 停止定时器
        self.card_update_timer.stop()
        self.chart_update_timer.stop()
        
        # 断开信号连接
        try:
            self.theme_manager.theme_changed.disconnect(self.on_theme_changed)
            self.polling_config.unregister_callback(self.on_polling_speed_changed)
        except:
            pass
        
        super().closeEvent(event)
    

