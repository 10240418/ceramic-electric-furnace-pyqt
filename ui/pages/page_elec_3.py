"""
3#电炉页面 - 使用组件化架构
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import QTimer
from ui.styles.themes import ThemeManager
from ui.widgets.common.panel_tech import PanelTech
from ui.widgets.realtime_data.card_data import CardData, DataItem
from ui.widgets.realtime_data.chart_electrode import ChartElectrode, ElectrodeData
from ui.widgets.realtime_data.butterfly_vaue import WidgetValveGrid
from ui.widgets.realtime_data import PanelFurnaceBg


class PageElec3(QWidget):
    """3#电炉页面"""
    
    # 1. 初始化页面
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        
        # 模拟数据
        self.mock_data = {
            'batch_no': '03260128',
            'start_time': '2026-01-28 08:30:00',
            'run_duration': '02:15:30',
            'electrodes': [
                {'depth_mm': -150.0, 'current_a': 2989.0, 'voltage_v': 145.0},
                {'depth_mm': -150.0, 'current_a': 3050.0, 'voltage_v': 148.0},
                {'depth_mm': -150.0, 'current_a': 2950.0, 'voltage_v': 142.0},
            ],
            'valves': [
                {'status': '01', 'open_percent': 75.0},
                {'status': '00', 'open_percent': 50.0},
                {'status': '10', 'open_percent': 25.0},
                {'status': '01', 'open_percent': 90.0},
            ],
            'cooling_shell': {
                'flow': 3.5,
                'pressure': 180.0,
                'total': 125.5,
            },
            'cooling_cover': {
                'flow': 2.8,
                'pressure': 165.0,
                'total': 98.3,
            },
            'hopper': {
                'weight': 1250.0,
                'feeding_total': 3580.0,
            },
            'power': 1850.5,      # 总功率 kW
            'energy': 12580.3,    # 总能耗 kWh
        }
        
        self.init_ui()
        self.apply_styles()
        
        # 监听主题变化
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
        
        # 启动数据更新定时器（模拟数据变化）
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_mock_data)
        self.update_timer.start(500)
    
    # 2. 初始化 UI
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        
        # 上部分 70%
        top_widget = QWidget()
        top_layout = QHBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(8)
        
        # 左侧 40%
        self.create_left_panel()
        top_layout.addWidget(self.left_panel, stretch=40)
        
        # 右侧 60% (电炉背景面板组件)
        self.furnace_panel = PanelFurnaceBg()
        self.furnace_panel.batch_info_bar.stop_clicked.connect(self.on_stop_smelting)
        self.furnace_panel.batch_info_bar.finish_clicked.connect(self.on_finish_smelting)
        top_layout.addWidget(self.furnace_panel, stretch=60)
        
        main_layout.addWidget(top_widget, stretch=70)
        
        # 下部分 30%
        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(8)
        
        # 料仓模块 42%
        self.create_hopper_panel()
        bottom_layout.addWidget(self.hopper_panel, stretch=42)
        
        # 炉盖模块 29%
        self.create_cooling_cover_panel()
        bottom_layout.addWidget(self.cooling_cover_panel, stretch=29)
        
        # 炉皮模块 29%
        self.create_cooling_shell_panel()
        bottom_layout.addWidget(self.cooling_shell_panel, stretch=29)
        
        main_layout.addWidget(bottom_widget, stretch=30)
    
    # 3. 创建左侧面板
    def create_left_panel(self):
        self.left_panel = QWidget()
        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)
        
        # 上半部分：蝶阀网格组件
        self.valve_grid = WidgetValveGrid()
        left_layout.addWidget(self.valve_grid, stretch=50)
        
        # 下半部分：弧流柱状图
        self.create_electrode_chart()
        left_layout.addWidget(self.chart_panel, stretch=50)
    
    # 4. 创建电极电流图表
    def create_electrode_chart(self):
        self.chart_panel = PanelTech("")  # 移除"弧流柱状图"标题
        
        # 创建电极电流图表 (固定Y轴0-8 KA)
        self.electrode_chart = ChartElectrode()
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.electrode_chart)
        self.chart_panel.set_content_layout(layout)
    
    # 5. 创建料仓重量面板
    def create_hopper_panel(self):
        self.hopper_panel = PanelTech("料仓")
        
        items = [
            DataItem(
                label="料仓重量",
                value="1250",
                unit="kg",
                icon="⚖️"
            ),
            DataItem(
                label="投料重量",
                value="3580",
                unit="kg",
                icon="⬇️"
            ),
        ]
        
        card = CardData(items)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(card)
        self.hopper_panel.set_content_layout(layout)
    
    # 6. 创建炉皮冷却水面板
    def create_cooling_shell_panel(self):
        self.cooling_shell_panel = PanelTech("炉皮冷却水")
        
        items = [
            DataItem(
                label="冷却水流速",
                value="3.50",
                unit="m³/h",
                icon="💧"
            ),
            DataItem(
                label="冷却水水压",
                value="180.0",
                unit="kPa",
                icon="💦"
            ),
            DataItem(
                label="冷却水用量",
                value="125.50",
                unit="m³",
                icon="🌊"
            ),
        ]
        
        card = CardData(items)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(card)
        self.cooling_shell_panel.set_content_layout(layout)
    
    # 7. 创建炉盖冷却水面板
    def create_cooling_cover_panel(self):
        self.cooling_cover_panel = PanelTech("炉盖冷却水")
        
        items = [
            DataItem(
                label="冷却水流速",
                value="2.80",
                unit="m³/h",
                icon="💧"
            ),
            DataItem(
                label="冷却水水压",
                value="165.0",
                unit="kPa",
                icon="💦"
            ),
            DataItem(
                label="冷却水用量",
                value="98.30",
                unit="m³",
                icon="🌊"
            ),
        ]
        
        card = CardData(items)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(card)
        self.cooling_cover_panel.set_content_layout(layout)
    
    # 8. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        self.setStyleSheet(f"""
            PageElec3 {{
                background: {colors.BG_DEEP};
            }}
        """)
    
    # 9. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()
    
    # 10. 更新模拟数据
    def update_mock_data(self):
        import random
        
        # 更新蝶阀数据
        for i, valve_data in enumerate(self.mock_data['valves']):
            valve_data['open_percent'] += random.uniform(-5, 5)
            valve_data['open_percent'] = max(0, min(100, valve_data['open_percent']))
        
        # 批量更新蝶阀
        self.valve_grid.update_all_valves(self.mock_data['valves'])
        
        # 更新电极数据
        for i in range(3):
            data = self.mock_data['electrodes'][i]
            data['current_a'] += random.uniform(-50, 50)
            data['current_a'] = max(0, min(8000, data['current_a']))
        
        # 更新功率能耗（模拟变化）
        self.mock_data['power'] += random.uniform(-50, 50)
        self.mock_data['power'] = max(1000, min(3000, self.mock_data['power']))
        self.mock_data['energy'] += random.uniform(0, 1)
        
        # 更新炉次信息
        self.furnace_panel.update_batch_info(
            self.mock_data['batch_no'],
            self.mock_data['start_time'],
            self.mock_data['run_duration']
        )
        
        # 批量更新电极卡片
        self.furnace_panel.update_all_electrodes(self.mock_data['electrodes'])
        
        # 更新功率能耗
        self.furnace_panel.update_power_energy(
            self.mock_data['power'],
            self.mock_data['energy']
        )
        
        # 更新电极电流图表（设定值设置为实际值的85%-95%之间）
        electrodes = []
        for i in range(3):
            data = self.mock_data['electrodes'][i]
            # 设定值为实际值的85%-95%
            set_value = data['current_a'] * random.uniform(0.85, 0.95)
            electrodes.append(ElectrodeData(
                f"{i+1}#电极",
                set_value,  # 设定值
                data['current_a']  # 实际值
            ))
        
        self.electrode_chart.update_data(electrodes, 15.0)
    
    # 11. 中止冶炼
    def on_stop_smelting(self):
        print("中止冶炼")
    
    # 12. 结束冶炼
    def on_finish_smelting(self):
        print("结束冶炼")
