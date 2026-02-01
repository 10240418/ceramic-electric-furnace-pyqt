"""
系统配置页面 - 系统设置和配置管理
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFrame, QScrollArea, QDoubleSpinBox, QCheckBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
from ui.styles.themes import ThemeManager, Theme
from backend.alarm_thresholds import get_alarm_threshold_manager, ThresholdConfig
from loguru import logger


class PageSettings(QWidget):
    """系统配置页面"""
    
    # 1. 初始化页面
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        self.alarm_manager = get_alarm_threshold_manager()
        
        # 存储所有输入控件的引用
        self.threshold_inputs = {}
        
        # 当前选中的导航索引
        self.current_nav_index = 0
        
        # 监听主题变化
        self.theme_manager.theme_changed.connect(self.apply_styles)
        
        self.init_ui()
        self.apply_styles()
    
    # 2. 初始化 UI
    def init_ui(self):
        # 主布局（水平布局：左侧导航 + 右侧内容）
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 左侧导航栏
        left_nav = self.create_left_nav()
        main_layout.addWidget(left_nav)
        
        # 右侧内容区
        self.right_content = QWidget()
        self.right_content.setObjectName("right_content")
        self.right_layout = QVBoxLayout(self.right_content)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(20)
        
        main_layout.addWidget(self.right_content, stretch=1)
        
        # 默认显示系统配置页面
        self.switch_content(0)
    
    # 3. 创建左侧导航栏
    def create_left_nav(self):
        nav_widget = QFrame()
        nav_widget.setObjectName("left_nav")
        nav_widget.setFixedWidth(220)
        
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(16, 16, 16, 16)
        nav_layout.setSpacing(20)
        
        # 导航标题
        nav_title = QLabel("配置中心")
        nav_title.setObjectName("nav_title")
        nav_title.setFont(QFont("Microsoft YaHei", 20, QFont.Weight.Bold))
        nav_layout.addWidget(nav_title)
        
        # 导航项
        nav_items = [
            {"title": "系统配置", "icon": "⚙"},
            {"title": "报警阈值", "icon": "⚠"},
            {"title": "弧流设置", "icon": "⚡"},
        ]
        
        self.nav_buttons = []
        for index, item in enumerate(nav_items):
            btn = self.create_nav_button(item["title"], item["icon"], index)
            self.nav_buttons.append(btn)
            nav_layout.addWidget(btn)
        
        nav_layout.addStretch()
        
        return nav_widget
    
    # 4. 创建导航按钮
    def create_nav_button(self, title: str, icon: str, index: int):
        btn = QPushButton(f"{icon}  {title}")
        btn.setObjectName("nav_button")
        btn.setFixedHeight(50)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setFont(QFont("Microsoft YaHei", 15))
        btn.clicked.connect(lambda: self.switch_content(index))
        return btn
    
    # 5. 切换内容区
    def switch_content(self, index: int):
        self.current_nav_index = index
        
        # 清空右侧内容
        while self.right_layout.count():
            item = self.right_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 根据索引显示不同内容
        if index == 0:
            self.show_system_config_content()
        elif index == 1:
            self.show_alarm_threshold_content()
        elif index == 2:
            self.show_arc_limit_content()
        
        # 更新导航按钮样式
        self.update_nav_buttons()
    
    # 6. 更新导航按钮样式
    def update_nav_buttons(self):
        for index, btn in enumerate(self.nav_buttons):
            if index == self.current_nav_index:
                btn.setProperty("selected", True)
            else:
                btn.setProperty("selected", False)
            btn.style().unpolish(btn)
            btn.style().polish(btn)
    
    # 7. 显示系统配置内容
    def show_system_config_content(self):
        # 标题栏
        title_bar = self.create_title_bar("系统配置")
        self.right_layout.addWidget(title_bar)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setObjectName("content_scroll")
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(20)
        
        # 主题设置区域
        theme_section = self.create_theme_section()
        scroll_layout.addWidget(theme_section)
        
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        self.right_layout.addWidget(scroll_area)
    
    # 8. 显示报警阈值内容
    def show_alarm_threshold_content(self):
        # 标题栏
        title_bar = self.create_title_bar("报警阈值")
        self.right_layout.addWidget(title_bar)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setObjectName("content_scroll")
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(20)
        
        # 报警阈值设置区域
        alarm_section = self.create_alarm_section()
        scroll_layout.addWidget(alarm_section)
        
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        self.right_layout.addWidget(scroll_area)
    
    # 8.5. 显示弧流设置内容
    def show_arc_limit_content(self):
        # 标题栏
        title_bar = self.create_title_bar("弧流设置")
        self.right_layout.addWidget(title_bar)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setObjectName("content_scroll")
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(20)
        
        # 弧流设置区域
        arc_section = self.create_arc_limit_section()
        scroll_layout.addWidget(arc_section)
        
        # 添加弹性空间，让内容置顶显示
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        self.right_layout.addWidget(scroll_area)
    
    # 9. 创建标题栏
    def create_title_bar(self, title: str):
        title_bar = QFrame()
        title_bar.setObjectName("title_bar")
        
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(12)
        
        # 装饰条
        decorator = QFrame()
        decorator.setObjectName("title_decorator")
        decorator.setFixedSize(4, 28)
        title_layout.addWidget(decorator)
        
        # 标题文字
        title_label = QLabel(title)
        title_label.setObjectName("content_title")
        title_label.setFont(QFont("Microsoft YaHei", 22, QFont.Weight.Bold))
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        # 保存按钮
        btn_save = QPushButton("保存配置")
        btn_save.setObjectName("btn_save")
        btn_save.setFixedSize(140, 45)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        btn_save.clicked.connect(self.on_save_clicked)
        title_layout.addWidget(btn_save)
        
        return title_bar
    
    # 10. 创建主题设置区域
    def create_theme_section(self):
        section = QFrame()
        section.setObjectName("settings_section")
        
        layout = QVBoxLayout(section)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 区域标题
        section_title = QLabel("外观设置")
        section_title.setObjectName("section_title")
        section_title.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        layout.addWidget(section_title)
        
        # 主题切换行
        theme_row = QHBoxLayout()
        theme_row.setSpacing(15)
        
        # 主题标签
        theme_label = QLabel("主题模式:")
        theme_label.setObjectName("setting_label")
        theme_label.setFont(QFont("Microsoft YaHei", 13))
        theme_row.addWidget(theme_label)
        
        # 浅色主题按钮
        self.btn_light_theme = QPushButton("浅色主题")
        self.btn_light_theme.setObjectName("btn_light_theme")
        self.btn_light_theme.setFixedSize(120, 40)
        self.btn_light_theme.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_light_theme.clicked.connect(self.on_light_theme_clicked)
        theme_row.addWidget(self.btn_light_theme)
        
        # 深色主题按钮
        self.btn_dark_theme = QPushButton("深色主题")
        self.btn_dark_theme.setObjectName("btn_dark_theme")
        self.btn_dark_theme.setFixedSize(120, 40)
        self.btn_dark_theme.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_dark_theme.clicked.connect(self.on_dark_theme_clicked)
        theme_row.addWidget(self.btn_dark_theme)
        
        theme_row.addStretch()
        
        layout.addLayout(theme_row)
        
        # 主题说明
        theme_desc = QLabel("选择您喜欢的主题模式，更改将立即生效")
        theme_desc.setObjectName("setting_desc")
        theme_desc.setFont(QFont("Microsoft YaHei", 11))
        layout.addWidget(theme_desc)
        
        return section
    
    # 11. 浅色主题按钮点击
    def on_light_theme_clicked(self):
        self.theme_manager.set_theme(Theme.LIGHT)
        logger.info("切换到浅色主题")
    
    # 12. 深色主题按钮点击
    def on_dark_theme_clicked(self):
        self.theme_manager.set_theme(Theme.DARK)
        logger.info("切换到深色主题")
    
    # 12.5. 创建弧流设置区域
    def create_arc_limit_section(self):
        """创建弧流设置区域"""
        from backend.bridge.data_cache import DataCache
        
        section = QFrame()
        section.setObjectName("settings_section")
        
        layout = QVBoxLayout(section)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 说明文字
        desc_frame = QFrame()
        desc_frame.setObjectName("info_frame")
        desc_layout = QHBoxLayout(desc_frame)
        desc_layout.setContentsMargins(12, 12, 12, 12)
        desc_layout.setSpacing(10)
        
        info_icon = QLabel("ℹ")
        info_icon.setObjectName("info_icon")
        info_icon.setFont(QFont("Microsoft YaHei", 16))
        desc_layout.addWidget(info_icon)
        
        desc = QLabel("高压紧急停电弧流设置，当弧流超过上限值时触发紧急停电保护")
        desc.setObjectName("info_text")
        desc.setFont(QFont("Microsoft YaHei", 13))
        desc.setWordWrap(True)
        desc_layout.addWidget(desc, stretch=1)
        
        layout.addWidget(desc_frame)
        
        # 获取缓存数据（使用正确的方法）
        data_cache = DataCache()  # 单例模式，直接实例化
        arc_data = data_cache.get_arc_data()  # 使用正确的方法
        
        # 提取紧急停电数据
        emergency_stop = {}
        if arc_data and 'emergency_stop' in arc_data:
            emergency_stop = arc_data['emergency_stop']
        
        arc_limit = emergency_stop.get('emergency_stop_arc_limit', 8000)
        stop_flag = emergency_stop.get('emergency_stop_flag', False)
        stop_enabled = emergency_stop.get('emergency_stop_enabled', True)
        
        # 弧流上限值显示卡片
        limit_card = QFrame()
        limit_card.setObjectName("arc_limit_card")
        limit_layout = QVBoxLayout(limit_card)
        limit_layout.setContentsMargins(20, 20, 20, 20)
        limit_layout.setSpacing(15)
        
        # 卡片标题
        card_title = QLabel("高压紧急停电弧流上限")
        card_title.setObjectName("card_title")
        card_title.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        limit_layout.addWidget(card_title)
        
        # 当前值显示
        value_layout = QHBoxLayout()
        value_layout.setSpacing(15)
        
        value_label = QLabel("当前上限值:")
        value_label.setObjectName("value_label")
        value_label.setFont(QFont("Microsoft YaHei", 14))
        value_layout.addWidget(value_label)
        
        self.arc_limit_value = QLabel(f"{arc_limit} A")
        self.arc_limit_value.setObjectName("arc_limit_value")
        self.arc_limit_value.setFont(QFont("Roboto Mono", 20, QFont.Weight.Bold))
        value_layout.addWidget(self.arc_limit_value)
        
        value_layout.addStretch()
        
        # 设置按钮
        set_btn = QPushButton("设置上限值")
        set_btn.setObjectName("set_arc_limit_btn")
        set_btn.setFixedSize(140, 45)
        set_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        set_btn.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        set_btn.clicked.connect(self.on_set_arc_limit_clicked)
        value_layout.addWidget(set_btn)
        
        limit_layout.addLayout(value_layout)
        
        layout.addWidget(limit_card)
        
        # 状态信息卡片
        status_card = QFrame()
        status_card.setObjectName("status_card")
        status_layout = QVBoxLayout(status_card)
        status_layout.setContentsMargins(20, 20, 20, 20)
        status_layout.setSpacing(15)
        
        # 卡片标题
        status_title = QLabel("状态信息")
        status_title.setObjectName("card_title")
        status_title.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        status_layout.addWidget(status_title)
        
        # 停电标志
        flag_layout = QHBoxLayout()
        flag_layout.setSpacing(15)
        
        flag_label = QLabel("高压紧急停电标志:")
        flag_label.setObjectName("status_label")
        flag_label.setFont(QFont("Microsoft YaHei", 14))
        flag_layout.addWidget(flag_label)
        
        self.stop_flag_value = QLabel("是" if stop_flag else "否")
        self.stop_flag_value.setObjectName("stop_flag_active" if stop_flag else "stop_flag_inactive")
        self.stop_flag_value.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        flag_layout.addWidget(self.stop_flag_value)
        
        flag_layout.addStretch()
        
        status_layout.addLayout(flag_layout)
        
        # 功能使能
        enabled_layout = QHBoxLayout()
        enabled_layout.setSpacing(15)
        
        enabled_label = QLabel("高压紧急停电功能使能:")
        enabled_label.setObjectName("status_label")
        enabled_label.setFont(QFont("Microsoft YaHei", 14))
        enabled_layout.addWidget(enabled_label)
        
        self.stop_enabled_value = QLabel("已启用" if stop_enabled else "已禁用")
        self.stop_enabled_value.setObjectName("stop_enabled_active" if stop_enabled else "stop_enabled_inactive")
        self.stop_enabled_value.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        enabled_layout.addWidget(self.stop_enabled_value)
        
        enabled_layout.addStretch()
        
        status_layout.addLayout(enabled_layout)
        
        layout.addWidget(status_card)
        
        # 启动定时器，定期更新显示
        from PyQt6.QtCore import QTimer
        self.arc_limit_timer = QTimer()
        self.arc_limit_timer.timeout.connect(self.update_arc_limit_display)
        self.arc_limit_timer.start(1000)
        
        return section
    
    # 12.6. 更新弧流设置显示
    def update_arc_limit_display(self):
        """更新弧流设置显示"""
        from backend.bridge.data_cache import DataCache
        
        try:
            data_cache = DataCache()  # 单例模式，直接实例化
            arc_data = data_cache.get_arc_data()  # 使用正确的方法
            
            if arc_data and 'emergency_stop' in arc_data:
                emergency_stop = arc_data['emergency_stop']
                
                # 更新弧流上限值
                arc_limit = emergency_stop.get('emergency_stop_arc_limit', 8000)
                self.arc_limit_value.setText(f"{arc_limit} A")
                
                # 更新停电标志
                stop_flag = emergency_stop.get('emergency_stop_flag', False)
                self.stop_flag_value.setText("是" if stop_flag else "否")
                self.stop_flag_value.setObjectName("stop_flag_active" if stop_flag else "stop_flag_inactive")
                self.stop_flag_value.style().unpolish(self.stop_flag_value)
                self.stop_flag_value.style().polish(self.stop_flag_value)
                
                # 更新功能使能
                stop_enabled = emergency_stop.get('emergency_stop_enabled', True)
                self.stop_enabled_value.setText("已启用" if stop_enabled else "已禁用")
                self.stop_enabled_value.setObjectName("stop_enabled_active" if stop_enabled else "stop_enabled_inactive")
                self.stop_enabled_value.style().unpolish(self.stop_enabled_value)
                self.stop_enabled_value.style().polish(self.stop_enabled_value)
        except Exception as e:
            logger.error(f"更新弧流设置显示异常: {e}")
    
    # 12.7. 设置弧流上限按钮点击
    def on_set_arc_limit_clicked(self):
        """打开设置弧流上限弹窗"""
        from backend.bridge.data_cache import DataCache
        
        # 获取当前值
        data_cache = DataCache()  # 单例模式，直接实例化
        arc_data = data_cache.get_arc_data()  # 使用正确的方法
        
        current_limit = 8000
        if arc_data and 'emergency_stop' in arc_data:
            current_limit = arc_data['emergency_stop'].get('emergency_stop_arc_limit', 8000)
        
        # 打开弹窗
        from ui.widgets.settings.dialog_set_arc_limit import DialogSetArcLimit
        dialog = DialogSetArcLimit(current_limit, self)
        dialog.limit_set.connect(self.on_arc_limit_set)
        dialog.exec()
    
    # 12.8. 弧流上限设置完成
    def on_arc_limit_set(self, new_limit: int):
        """弧流上限设置完成回调"""
        logger.info(f"弧流上限已设置为: {new_limit} A")
    
    # 13. 创建报警阈值设置区域
    def create_alarm_section(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # 说明文字
        desc_frame = QFrame()
        desc_frame.setObjectName("info_frame")
        desc_layout = QHBoxLayout(desc_frame)
        desc_layout.setContentsMargins(12, 12, 12, 12)
        desc_layout.setSpacing(10)
        
        info_icon = QLabel("ℹ")
        info_icon.setObjectName("info_icon")
        info_icon.setFont(QFont("Microsoft YaHei", 16))
        desc_layout.addWidget(info_icon)
        
        desc = QLabel("设置各参数的警告和报警阈值，超出范围时系统将发出提示")
        desc.setObjectName("info_text")
        desc.setFont(QFont("Microsoft YaHei", 13))
        desc.setWordWrap(True)
        desc_layout.addWidget(desc, stretch=1)
        
        layout.addWidget(desc_frame)
        
        # 电极深度阈值
        electrode_depth_group = self.create_threshold_group(
            "电极深度 (mm)",
            [
                ("electrode_depth_u", "U相电极深度"),
                ("electrode_depth_v", "V相电极深度"),
                ("electrode_depth_w", "W相电极深度"),
            ]
        )
        layout.addWidget(electrode_depth_group)
        
        # 电极弧流阈值
        arc_current_group = self.create_threshold_group(
            "电极弧流 (A)",
            [
                ("arc_current_u", "U相弧流"),
                ("arc_current_v", "V相弧流"),
                ("arc_current_w", "W相弧流"),
            ]
        )
        layout.addWidget(arc_current_group)
        
        # 电极弧压阈值
        arc_voltage_group = self.create_threshold_group(
            "电极弧压 (V)",
            [
                ("arc_voltage_u", "U相弧压"),
                ("arc_voltage_v", "V相弧压"),
                ("arc_voltage_w", "W相弧压"),
            ]
        )
        layout.addWidget(arc_voltage_group)
        
        # 冷却水压力阈值
        cooling_pressure_group = self.create_threshold_group(
            "冷却水压力 (kPa)",
            [
                ("cooling_pressure_shell", "炉皮水压"),
                ("cooling_pressure_cover", "炉盖水压"),
            ]
        )
        layout.addWidget(cooling_pressure_group)
        
        # 过滤器压差阈值
        filter_diff_group = self.create_threshold_group(
            "过滤器压差 (kPa)",
            [
                ("filter_pressure_diff", "压差"),
            ]
        )
        layout.addWidget(filter_diff_group)
        
        return container
    
    # 14. 创建阈值组
    def create_threshold_group(self, group_title: str, params: list):
        """创建阈值配置组
        
        Args:
            group_title: 组标题
            params: 参数列表 [(param_name, display_name), ...]
        """
        group = QFrame()
        group.setObjectName("threshold_group")
        
        layout = QVBoxLayout(group)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 组标题
        title = QLabel(group_title)
        title.setObjectName("group_title")
        title.setFont(QFont("Microsoft YaHei", 16, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # 为每个参数创建输入行
        for param_name, display_name in params:
            param_row = self.create_threshold_row(param_name, display_name)
            layout.addWidget(param_row)
        
        return group
    
    # 15. 创建阈值输入行（增大字体和按钮）
    def create_threshold_row(self, param_name: str, display_name: str):
        """创建单个参数的阈值输入行"""
        row = QFrame()
        row.setObjectName("threshold_row")
        
        layout = QVBoxLayout(row)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # 第一行：参数名称 + 启用复选框
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)
        
        # 参数名称（增大字体）
        name_label = QLabel(display_name)
        name_label.setObjectName("param_name")
        name_label.setFont(QFont("Microsoft YaHei", 15, QFont.Weight.Bold))
        header_layout.addWidget(name_label)
        
        header_layout.addStretch()
        
        # 获取当前配置
        config = self.alarm_manager.get_threshold(param_name)
        
        # 启用复选框（增大）
        # 对于冷却水流速，默认禁用
        default_enabled = True
        if param_name in ['cooling_flow_shell', 'cooling_flow_cover']:
            default_enabled = False
        
        enable_checkbox = QCheckBox("启用报警")
        enable_checkbox.setObjectName("enable_checkbox")
        enable_checkbox.setChecked(config.enabled if config else default_enabled)
        enable_checkbox.setFont(QFont("Microsoft YaHei", 13))
        header_layout.addWidget(enable_checkbox)
        
        layout.addLayout(header_layout)
        
        # 第二行：警告阈值
        warning_layout = QHBoxLayout()
        warning_layout.setSpacing(15)
        
        warning_title = QLabel("警告阈值:")
        warning_title.setObjectName("threshold_label")
        warning_title.setFont(QFont("Microsoft YaHei", 14))
        warning_title.setFixedWidth(100)
        warning_layout.addWidget(warning_title)
        
        # 警告下限
        warning_min_label = QLabel("下限:")
        warning_min_label.setFont(QFont("Microsoft YaHei", 13))
        warning_layout.addWidget(warning_min_label)
        
        warning_min = QDoubleSpinBox()
        warning_min.setObjectName("threshold_input")
        warning_min.setRange(-10000, 10000)
        warning_min.setDecimals(1)
        warning_min.setValue(config.warning_min if config and config.warning_min is not None else 0.0)
        warning_min.setFixedSize(140, 45)
        warning_min.setFont(QFont("Microsoft YaHei", 13))
        warning_min.setSpecialValueText("无限制")
        if config and config.warning_min is None:
            warning_min.setValue(warning_min.minimum())
        warning_layout.addWidget(warning_min)
        
        # 警告上限
        warning_max_label = QLabel("上限:")
        warning_max_label.setFont(QFont("Microsoft YaHei", 13))
        warning_layout.addWidget(warning_max_label)
        
        warning_max = QDoubleSpinBox()
        warning_max.setObjectName("threshold_input")
        warning_max.setRange(-10000, 10000)
        warning_max.setDecimals(1)
        warning_max.setValue(config.warning_max if config and config.warning_max is not None else 0.0)
        warning_max.setFixedSize(140, 45)
        warning_max.setFont(QFont("Microsoft YaHei", 13))
        warning_max.setSpecialValueText("无限制")
        if config and config.warning_max is None:
            warning_max.setValue(warning_max.maximum())
        warning_layout.addWidget(warning_max)
        
        warning_layout.addStretch()
        layout.addLayout(warning_layout)
        
        # 第三行：报警阈值
        alarm_layout = QHBoxLayout()
        alarm_layout.setSpacing(15)
        
        alarm_title = QLabel("报警阈值:")
        alarm_title.setObjectName("threshold_label")
        alarm_title.setFont(QFont("Microsoft YaHei", 14))
        alarm_title.setFixedWidth(100)
        alarm_layout.addWidget(alarm_title)
        
        # 报警下限
        alarm_min_label = QLabel("下限:")
        alarm_min_label.setFont(QFont("Microsoft YaHei", 13))
        alarm_layout.addWidget(alarm_min_label)
        
        alarm_min = QDoubleSpinBox()
        alarm_min.setObjectName("threshold_input")
        alarm_min.setRange(-10000, 10000)
        alarm_min.setDecimals(1)
        alarm_min.setValue(config.alarm_min if config and config.alarm_min is not None else 0.0)
        alarm_min.setFixedSize(140, 45)
        alarm_min.setFont(QFont("Microsoft YaHei", 13))
        alarm_min.setSpecialValueText("无限制")
        if config and config.alarm_min is None:
            alarm_min.setValue(alarm_min.minimum())
        alarm_layout.addWidget(alarm_min)
        
        # 报警上限
        alarm_max_label = QLabel("上限:")
        alarm_max_label.setFont(QFont("Microsoft YaHei", 13))
        alarm_layout.addWidget(alarm_max_label)
        
        alarm_max = QDoubleSpinBox()
        alarm_max.setObjectName("threshold_input")
        alarm_max.setRange(-10000, 10000)
        alarm_max.setDecimals(1)
        alarm_max.setValue(config.alarm_max if config and config.alarm_max is not None else 0.0)
        alarm_max.setFixedSize(140, 45)
        alarm_max.setFont(QFont("Microsoft YaHei", 13))
        alarm_max.setSpecialValueText("无限制")
        if config and config.alarm_max is None:
            alarm_max.setValue(alarm_max.maximum())
        alarm_layout.addWidget(alarm_max)
        
        alarm_layout.addStretch()
        layout.addLayout(alarm_layout)
        
        # 保存控件引用
        self.threshold_inputs[param_name] = {
            'enabled': enable_checkbox,
            'warning_min': warning_min,
            'warning_max': warning_max,
            'alarm_min': alarm_min,
            'alarm_max': alarm_max,
        }
        
        return row
    
    # 16. 保存配置
    def on_save_clicked(self):
        """保存所有阈值配置"""
        try:
            # 遍历所有输入控件，更新配置
            for param_name, inputs in self.threshold_inputs.items():
                # 获取输入值
                enabled = inputs['enabled'].isChecked()
                warning_min = inputs['warning_min'].value()
                warning_max = inputs['warning_max'].value()
                alarm_min = inputs['alarm_min'].value()
                alarm_max = inputs['alarm_max'].value()
                
                # 处理"无限制"的情况
                if warning_min == inputs['warning_min'].minimum():
                    warning_min = None
                if warning_max == inputs['warning_max'].maximum():
                    warning_max = None
                if alarm_min == inputs['alarm_min'].minimum():
                    alarm_min = None
                if alarm_max == inputs['alarm_max'].maximum():
                    alarm_max = None
                
                # 创建配置对象
                config = ThresholdConfig(
                    warning_min=warning_min,
                    warning_max=warning_max,
                    alarm_min=alarm_min,
                    alarm_max=alarm_max,
                    enabled=enabled
                )
                
                # 更新到管理器
                self.alarm_manager.set_threshold(param_name, config)
            
            # 保存到文件
            if self.alarm_manager.save():
                self.show_success_dialog("配置已保存")
                logger.info("配置已保存")
            else:
                self.show_warning_dialog("保存配置失败，请检查日志")
        
        except Exception as e:
            logger.error(f"保存配置异常: {e}", exc_info=True)
            self.show_error_dialog(f"保存配置失败: {e}")
    
    # 17. 显示成功对话框
    def show_success_dialog(self, message: str):
        """显示成功对话框（大尺寸）"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("成功")
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Information)
        
        # 设置字体大小
        font = QFont("Microsoft YaHei", 14)
        msg_box.setFont(font)
        
        # 设置最小尺寸
        msg_box.setMinimumSize(400, 200)
        
        # 自定义按钮
        ok_button = msg_box.addButton("确定", QMessageBox.ButtonRole.AcceptRole)
        ok_button.setMinimumSize(120, 50)
        ok_button.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        
        # 应用样式
        tm = self.theme_manager
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background: {tm.bg_dark()};
                color: {tm.text_primary()};
            }}
            QLabel {{
                color: {tm.text_primary()};
                font-size: 16px;
                min-width: 300px;
                min-height: 80px;
            }}
            QPushButton {{
                background: {tm.glow_green()};
                color: {tm.white()};
                border: 2px solid {tm.glow_green()};
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {tm.border_glow()};
                border: 2px solid {tm.border_glow()};
            }}
        """)
        
        msg_box.exec()
    
    # 18. 显示警告对话框
    def show_warning_dialog(self, message: str):
        """显示警告对话框（大尺寸）"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("警告")
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        
        # 设置字体大小
        font = QFont("Microsoft YaHei", 14)
        msg_box.setFont(font)
        
        # 设置最小尺寸
        msg_box.setMinimumSize(400, 200)
        
        # 自定义按钮
        ok_button = msg_box.addButton("确定", QMessageBox.ButtonRole.AcceptRole)
        ok_button.setMinimumSize(120, 50)
        ok_button.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        
        # 应用样式
        tm = self.theme_manager
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background: {tm.bg_dark()};
                color: {tm.text_primary()};
            }}
            QLabel {{
                color: {tm.text_primary()};
                font-size: 16px;
                min-width: 300px;
                min-height: 80px;
            }}
            QPushButton {{
                background: {tm.glow_orange()};
                color: {tm.white()};
                border: 2px solid {tm.glow_orange()};
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {tm.border_glow()};
                border: 2px solid {tm.border_glow()};
            }}
        """)
        
        msg_box.exec()
    
    # 19. 显示错误对话框
    def show_error_dialog(self, message: str):
        """显示错误对话框（大尺寸）"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("错误")
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        
        # 设置字体大小
        font = QFont("Microsoft YaHei", 14)
        msg_box.setFont(font)
        
        # 设置最小尺寸
        msg_box.setMinimumSize(400, 200)
        
        # 自定义按钮
        ok_button = msg_box.addButton("确定", QMessageBox.ButtonRole.AcceptRole)
        ok_button.setMinimumSize(120, 50)
        ok_button.setFont(QFont("Microsoft YaHei", 14, QFont.Weight.Bold))
        
        # 应用样式
        tm = self.theme_manager
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background: {tm.bg_dark()};
                color: {tm.text_primary()};
            }}
            QLabel {{
                color: {tm.text_primary()};
                font-size: 16px;
                min-width: 300px;
                min-height: 80px;
            }}
            QPushButton {{
                background: {tm.status_alarm()};
                color: {tm.white()};
                border: 2px solid {tm.status_alarm()};
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {tm.border_glow()};
                border: 2px solid {tm.border_glow()};
            }}
        """)
        
        msg_box.exec()
    
    # 20. 应用样式
    def apply_styles(self):
        tm = self.theme_manager
        current_theme = tm.get_current_theme()
        
        # 页面背景
        self.setStyleSheet(f"""
            QWidget {{
                background: {tm.bg_deep()};
                color: {tm.text_primary()};
            }}
            
            /* 左侧导航栏 */
            QFrame#left_nav {{
                background: {tm.bg_dark()};
                border: 1px solid {tm.border_medium()};
                border-radius: 8px;
            }}
            
            /* 导航标题 */
            QLabel#nav_title {{
                color: {tm.text_primary()};
            }}
            
            /* 导航按钮 */
            QPushButton#nav_button {{
                background: transparent;
                color: {tm.text_secondary()};
                border: 1px solid transparent;
                border-radius: 6px;
                padding: 10px 12px;
                text-align: left;
            }}
            
            QPushButton#nav_button:hover {{
                background: {tm.bg_medium()};
                border: 1px solid {tm.border_dark()};
            }}
            
            QPushButton#nav_button[selected="true"] {{
                background: {tm.border_glow()}33;
                color: {tm.border_glow()};
                border: 1px solid {tm.border_glow()};
                font-weight: bold;
            }}
            
            /* 右侧内容区 */
            QWidget#right_content {{
                background: transparent;
            }}
            
            /* 标题栏 */
            QFrame#title_bar {{
                background: transparent;
            }}
            
            /* 标题装饰条 */
            QFrame#title_decorator {{
                background: {tm.border_glow()};
                border-radius: 2px;
            }}
            
            /* 内容标题 */
            QLabel#content_title {{
                color: {tm.text_primary()};
            }}
            
            /* 保存按钮 */
            QPushButton#btn_save {{
                background: {tm.border_glow()};
                color: {tm.white()};
                border: 2px solid {tm.border_glow()};
                border-radius: 8px;
            }}
            
            QPushButton#btn_save:hover {{
                background: {tm.glow_primary()};
                border: 2px solid {tm.glow_primary()};
            }}
            
            QPushButton#btn_save:pressed {{
                background: {tm.bg_medium()};
            }}
            
            /* 滚动区域 */
            QScrollArea#content_scroll {{
                background: transparent;
                border: none;
            }}
            
            /* 设置区域 */
            QFrame#settings_section {{
                background: {tm.bg_dark()};
                border: 1px solid {tm.border_medium()};
                border-radius: 8px;
            }}
            
            /* 区域标题 */
            QLabel#section_title {{
                color: {tm.border_glow()};
            }}
            
            /* 设置标签 */
            QLabel#setting_label {{
                color: {tm.text_primary()};
            }}
            
            /* 设置说明 */
            QLabel#setting_desc {{
                color: {tm.text_secondary()};
            }}
            
            /* 信息框 */
            QFrame#info_frame {{
                background: {tm.glow_primary()}1A;
                border: 1px solid {tm.glow_primary()}4D;
                border-radius: 6px;
            }}
            
            QLabel#info_icon {{
                color: {tm.glow_primary()};
            }}
            
            QLabel#info_text {{
                color: {tm.text_secondary()};
            }}
            
            /* 阈值组 */
            QFrame#threshold_group {{
                background: {tm.bg_dark()};
                border: 1px solid {tm.border_medium()};
                border-radius: 8px;
            }}
            
            /* 组标题 */
            QLabel#group_title {{
                color: {tm.border_glow()};
            }}
            
            /* 阈值行 */
            QFrame#threshold_row {{
                background: {tm.bg_medium()};
                border: 1px solid {tm.border_dark()};
                border-radius: 6px;
            }}
            
            /* 参数名称 */
            QLabel#param_name {{
                color: {tm.text_primary()};
            }}
            
            /* 阈值标签 */
            QLabel#threshold_label {{
                color: {tm.text_primary()};
                font-weight: bold;
            }}
            
            /* 阈值输入框 */
            QDoubleSpinBox#threshold_input {{
                background: {tm.bg_dark()};
                color: {tm.text_primary()};
                border: 1px solid {tm.border_dark()};
                border-radius: 6px;
                padding: 8px;
            }}
            
            QDoubleSpinBox#threshold_input:hover {{
                border: 1px solid {tm.border_glow()};
            }}
            
            QDoubleSpinBox#threshold_input:focus {{
                border: 2px solid {tm.glow_primary()};
            }}
            
            QDoubleSpinBox#threshold_input::up-button,
            QDoubleSpinBox#threshold_input::down-button {{
                width: 20px;
                height: 20px;
                border-radius: 3px;
                background: {tm.bg_medium()};
            }}
            
            QDoubleSpinBox#threshold_input::up-button:hover,
            QDoubleSpinBox#threshold_input::down-button:hover {{
                background: {tm.border_glow()};
            }}
            
            /* 启用复选框 */
            QCheckBox#enable_checkbox {{
                color: {tm.text_primary()};
            }}
            
            QCheckBox#enable_checkbox::indicator {{
                width: 22px;
                height: 22px;
                border: 2px solid {tm.border_dark()};
                border-radius: 4px;
                background: {tm.bg_dark()};
            }}
            
            QCheckBox#enable_checkbox::indicator:hover {{
                border: 2px solid {tm.border_glow()};
            }}
            
            QCheckBox#enable_checkbox::indicator:checked {{
                background: {tm.glow_primary()};
                border: 2px solid {tm.glow_primary()};
            }}
            
            /* 弧流设置卡片 */
            QFrame#arc_limit_card, QFrame#status_card {{
                background: {tm.bg_dark()};
                border: 1px solid {tm.border_medium()};
                border-radius: 8px;
            }}
            
            QLabel#card_title {{
                color: {tm.border_glow()};
            }}
            
            QLabel#value_label, QLabel#status_label {{
                color: {tm.text_primary()};
            }}
            
            QLabel#arc_limit_value {{
                color: {tm.glow_primary()};
            }}
            
            QLabel#stop_flag_active, QLabel#stop_enabled_active {{
                color: {tm.glow_green()};
            }}
            
            QLabel#stop_flag_inactive, QLabel#stop_enabled_inactive {{
                color: {tm.text_secondary()};
            }}
            
            QPushButton#set_arc_limit_btn {{
                background: {tm.border_glow()};
                color: {tm.white()};
                border: 2px solid {tm.border_glow()};
                border-radius: 8px;
            }}
            
            QPushButton#set_arc_limit_btn:hover {{
                background: {tm.glow_primary()};
                border: 2px solid {tm.glow_primary()};
            }}
            
            QPushButton#set_arc_limit_btn:pressed {{
                background: {tm.bg_medium()};
            }}
            
            /* 滚动条 */
            QScrollBar:vertical {{
                background: {tm.bg_medium()};
                width: 10px;
                border-radius: 5px;
            }}
            
            QScrollBar::handle:vertical {{
                background: {tm.border_medium()};
                border-radius: 5px;
                min-height: 20px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background: {tm.border_glow()};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        
        # 更新主题按钮样式
        if current_theme == Theme.LIGHT:
            # 浅色主题激活
            self.btn_light_theme.setStyleSheet(f"""
                QPushButton {{
                    background: {tm.border_glow()};
                    color: {tm.white()};
                    border: 2px solid {tm.border_glow()};
                    border-radius: 6px;
                    font-size: 13px;
                    font-weight: bold;
                }}
                
                QPushButton:hover {{
                    background: {tm.glow_primary()};
                    border: 2px solid {tm.glow_primary()};
                }}
            """)
            
            self.btn_dark_theme.setStyleSheet(f"""
                QPushButton {{
                    background: {tm.bg_medium()};
                    color: {tm.text_primary()};
                    border: 1px solid {tm.border_medium()};
                    border-radius: 6px;
                    font-size: 13px;
                    font-weight: normal;
                }}
                
                QPushButton:hover {{
                    background: {tm.bg_light()};
                    border: 1px solid {tm.border_glow()};
                }}
            """)
        else:
            # 深色主题激活
            self.btn_dark_theme.setStyleSheet(f"""
                QPushButton {{
                    background: {tm.border_glow()};
                    color: {tm.white()};
                    border: 2px solid {tm.border_glow()};
                    border-radius: 6px;
                    font-size: 13px;
                    font-weight: bold;
                }}
                
                QPushButton:hover {{
                    background: {tm.glow_primary()};
                    border: 2px solid {tm.glow_primary()};
                }}
            """)
            
            self.btn_light_theme.setStyleSheet(f"""
                QPushButton {{
                    background: {tm.bg_medium()};
                    color: {tm.text_primary()};
                    border: 1px solid {tm.border_medium()};
                    border-radius: 6px;
                    font-size: 13px;
                    font-weight: normal;
                }}
                
                QPushButton:hover {{
                    background: {tm.bg_light()};
                    border: 1px solid {tm.border_glow()};
                }}
            """)

