"""
系统配置页面 - 系统设置和配置管理
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QSizePolicy,
    QPushButton, QFrame, QDoubleSpinBox, QCheckBox, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon
from ui.styles.themes import ThemeManager, Theme, THEME_REGISTRY
from ui.widgets.common.scroll_area_draggable import ScrollAreaDraggable
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
        
        # 主题按钮引用
        self.theme_buttons: dict[Theme, QPushButton] = {}
        
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
            {"title": "蝶阀配置", "icon": "🔧"},
            {"title": "轮询速度", "icon": "⏱"},
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
        
        # 停止弧流设置定时器（如果存在）
        if hasattr(self, 'arc_limit_timer') and self.arc_limit_timer is not None:
            self.arc_limit_timer.stop()
            self.arc_limit_timer = None
        
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
        elif index == 3:
            self.show_valve_config_content()
        elif index == 4:
            self.show_polling_config_content()
        
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
        
        # 滚动区域（支持拖拽滚动）
        scroll_area = ScrollAreaDraggable()
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
        
        # 滚动区域（支持拖拽滚动）
        scroll_area = ScrollAreaDraggable()
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
        
        # 滚动区域（支持拖拽滚动）
        scroll_area = ScrollAreaDraggable()
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
        
        # 主题标签
        theme_label = QLabel("主题模式:")
        theme_label.setObjectName("setting_label")
        theme_label.setFont(QFont("Microsoft YaHei", 13))
        layout.addWidget(theme_label)
        
        # 主题按钮网格（深色/浅色分区）
        cols = 5
        dark_themes = [
            Theme.DARK, Theme.OCEAN_BLUE, Theme.EMERALD_NIGHT, Theme.VIOLET_DREAM,
            Theme.IRON_FORGE, Theme.CONTROL_ROOM, Theme.NIGHT_SHIFT, Theme.SLATE_GRID,
        ]
        light_themes = [
            Theme.LIGHT, Theme.LIGHT_CHANGE, Theme.ROSE_GOLD, Theme.SUNSET_AMBER,
            Theme.ARCTIC_FROST, Theme.STEEL_LINE, Theme.POLAR_FRAME,
        ]
        
        dark_title = QLabel("深色主题")
        dark_title.setObjectName("setting_label")
        dark_title.setFont(QFont("Microsoft YaHei", 13, QFont.Weight.Bold))
        layout.addWidget(dark_title)
        
        dark_grid = QGridLayout()
        dark_grid.setSpacing(10)
        for i, theme in enumerate(dark_themes):
            entry = THEME_REGISTRY.get(theme.value, {})
            label = entry.get('label', theme.value)
            accent = entry.get('accent', '#888888')
            
            btn = QPushButton(label)
            btn.setFixedHeight(40)
            btn.setMinimumWidth(80)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn.setFont(QFont("Microsoft YaHei", 12))
            btn.setProperty('accent', accent)
            btn.clicked.connect(lambda checked, t=theme: self._on_theme_btn_clicked(t))
            
            row = i // cols
            col = i % cols
            dark_grid.addWidget(btn, row, col)
            self.theme_buttons[theme] = btn
        layout.addLayout(dark_grid)
        
        light_title = QLabel("浅色主题")
        light_title.setObjectName("setting_label")
        light_title.setFont(QFont("Microsoft YaHei", 13, QFont.Weight.Bold))
        layout.addWidget(light_title)
        
        light_grid = QGridLayout()
        light_grid.setSpacing(10)
        for i, theme in enumerate(light_themes):
            entry = THEME_REGISTRY.get(theme.value, {})
            label = entry.get('label', theme.value)
            accent = entry.get('accent', '#888888')
            
            btn = QPushButton(label)
            btn.setFixedHeight(40)
            btn.setMinimumWidth(80)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn.setFont(QFont("Microsoft YaHei", 12))
            btn.setProperty('accent', accent)
            btn.clicked.connect(lambda checked, t=theme: self._on_theme_btn_clicked(t))
            
            row = i // cols
            col = i % cols
            light_grid.addWidget(btn, row, col)
            self.theme_buttons[theme] = btn
        layout.addLayout(light_grid)
        
        # 主题说明
        theme_desc = QLabel("选择您喜欢的主题模式，更改将立即生效")
        theme_desc.setObjectName("setting_desc")
        theme_desc.setFont(QFont("Microsoft YaHei", 11))
        layout.addWidget(theme_desc)
        
        return section
    
    # 11. 主题按钮点击
    def _on_theme_btn_clicked(self, theme: Theme):
        self.theme_manager.set_theme(theme)
        logger.info(f"切换到主题: {theme.value}")
    
    # 12. 判断强调色是否偏深
    @staticmethod
    def _is_dark_accent(hex_color: str) -> bool:
        hex_color = hex_color.lstrip('#')
        if len(hex_color) < 6:
            return True
        r, g, b = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        return (0.299 * r + 0.587 * g + 0.114 * b) < 160
    
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
        delay_ms = emergency_stop.get('emergency_stop_delay', 0)
        
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
        set_btn = QPushButton("设置参数")
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
        
        # 消抖时间
        delay_layout = QHBoxLayout()
        delay_layout.setSpacing(15)
        
        delay_label = QLabel("消抖时间:")
        delay_label.setObjectName("status_label")
        delay_label.setFont(QFont("Microsoft YaHei", 14))
        delay_layout.addWidget(delay_label)
        
        self.delay_value = QLabel(f"{delay_ms} ms")
        self.delay_value.setObjectName("delay_value")
        self.delay_value.setFont(QFont("Roboto Mono", 14, QFont.Weight.Bold))
        delay_layout.addWidget(self.delay_value)
        
        delay_layout.addStretch()
        
        status_layout.addLayout(delay_layout)
        
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
            # 检查控件是否存在（防止页面切换后定时器仍在运行）
            if not hasattr(self, 'arc_limit_value') or self.arc_limit_value is None:
                return
            
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
                
                # 更新消抖时间
                delay_ms = emergency_stop.get('emergency_stop_delay', 0)
                self.delay_value.setText(f"{delay_ms} ms")
        except Exception as e:
            logger.error(f"更新弧流设置显示异常: {e}")
    
    # 12.7. 设置弧流上限按钮点击
    def on_set_arc_limit_clicked(self):
        """打开设置弧流上限和消抖时间弹窗"""
        from backend.bridge.data_cache import DataCache
        
        # 获取当前值
        data_cache = DataCache()  # 单例模式，直接实例化
        arc_data = data_cache.get_arc_data()  # 使用正确的方法
        
        current_limit = 8000
        current_delay = 0
        if arc_data and 'emergency_stop' in arc_data:
            current_limit = arc_data['emergency_stop'].get('emergency_stop_arc_limit', 8000)
            current_delay = arc_data['emergency_stop'].get('emergency_stop_delay', 0)
        
        # 打开弹窗
        from ui.widgets.settings.dialog_set_arc_limit import DialogSetArcLimit
        dialog = DialogSetArcLimit(current_limit, current_delay, self)
        dialog.limit_set.connect(self.on_arc_limit_set)
        dialog.exec()
    
    # 12.8. 弧流上限和消抖时间设置完成
    def on_arc_limit_set(self, new_limit: int, new_delay: int):
        """弧流上限和消抖时间设置完成回调"""
        logger.info(f"设置完成 - 弧流上限: {new_limit} A, 消抖时间: {new_delay} ms")
    
    # 12.9. 显示蝶阀配置内容
    def show_valve_config_content(self):
        """显示蝶阀配置内容"""
        # 标题栏
        title_bar = self.create_title_bar("蝶阀配置")
        self.right_layout.addWidget(title_bar)
        
        # 滚动区域（支持拖拽滚动）
        scroll_area = ScrollAreaDraggable()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setObjectName("content_scroll")
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(20)
        
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
        
        desc = QLabel("设置4个蝶阀从完全关闭到完全打开（全开时间）和从完全打开到完全关闭（全关时间）所需的时间，用于精确计算蝶阀开度百分比")
        desc.setObjectName("info_text")
        desc.setFont(QFont("Microsoft YaHei", 13))
        desc.setWordWrap(True)
        desc_layout.addWidget(desc, stretch=1)
        
        scroll_layout.addWidget(desc_frame)
        
        # 蝶阀配置区域
        valve_section = self.create_valve_config_section()
        scroll_layout.addWidget(valve_section)
        
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        self.right_layout.addWidget(scroll_area)
    
    # 12.91. 显示轮询速度配置内容
    def show_polling_config_content(self):
        """显示轮询速度配置内容"""
        from ui.pages.page_polling_config import PagePollingConfig
        
        # 创建轮询速度配置页面
        polling_config_page = PagePollingConfig(self)
        self.right_layout.addWidget(polling_config_page)
    
    # 12.10. 创建蝶阀配置区域
    def create_valve_config_section(self):
        """创建蝶阀配置区域"""
        from backend.services.db32.valve_config import get_valve_config_service
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        
        # 获取蝶阀配置服务
        self.valve_config_service = get_valve_config_service()
        
        # 存储输入控件引用
        self.valve_config_inputs = {}
        
        # 为4个蝶阀创建配置卡片
        for valve_id in range(1, 5):
            valve_card = self.create_valve_config_card(valve_id)
            layout.addWidget(valve_card)
        
        return container
    
    # 12.11. 创建单个蝶阀配置卡片
    def create_valve_config_card(self, valve_id: int):
        """创建单个蝶阀配置卡片"""
        card = QFrame()
        card.setObjectName("valve_config_card")
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 卡片标题
        title = QLabel(f"蝶阀 {valve_id}")
        title.setObjectName("valve_card_title")
        title.setFont(QFont("Microsoft YaHei", 18, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # 获取当前配置
        config = self.valve_config_service.get_config(valve_id)
        
        # 全开时间设置行
        open_time_row = QHBoxLayout()
        open_time_row.setSpacing(15)
        
        open_time_label = QLabel("全开时间:")
        open_time_label.setObjectName("valve_config_label")
        open_time_label.setFont(QFont("Microsoft YaHei", 14))
        open_time_label.setFixedWidth(120)
        open_time_row.addWidget(open_time_label)
        
        # 全开时间 - 减少按钮
        btn_open_minus = QPushButton("-")
        btn_open_minus.setObjectName("btnMinus")
        btn_open_minus.setFixedSize(45, 45)
        btn_open_minus.setCursor(Qt.CursorShape.PointingHandCursor)
        open_time_row.addWidget(btn_open_minus)
        
        # 全开时间输入框
        open_time_input = QDoubleSpinBox()
        open_time_input.setObjectName("valve_time_input")
        open_time_input.setRange(1.0, 300.0)
        open_time_input.setDecimals(1)
        open_time_input.setSingleStep(1.0)
        open_time_input.setValue(config.full_open_time)
        open_time_input.setFixedSize(120, 45)
        open_time_input.setFont(QFont("Microsoft YaHei", 13))
        open_time_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        open_time_input.setSuffix(" 秒")
        open_time_row.addWidget(open_time_input)
        
        # 全开时间 - 增加按钮
        btn_open_plus = QPushButton("+")
        btn_open_plus.setObjectName("btnPlus")
        btn_open_plus.setFixedSize(45, 45)
        btn_open_plus.setCursor(Qt.CursorShape.PointingHandCursor)
        open_time_row.addWidget(btn_open_plus)
        
        # 连接按钮信号
        btn_open_minus.clicked.connect(lambda: open_time_input.setValue(open_time_input.value() - open_time_input.singleStep()))
        btn_open_plus.clicked.connect(lambda: open_time_input.setValue(open_time_input.value() + open_time_input.singleStep()))
        
        open_time_row.addStretch()
        
        # 说明文字
        open_time_desc = QLabel("从完全关闭到完全打开所需时间")
        open_time_desc.setObjectName("valve_config_desc")
        open_time_desc.setFont(QFont("Microsoft YaHei", 11))
        open_time_row.addWidget(open_time_desc)
        
        layout.addLayout(open_time_row)
        
        # 全关时间设置行
        close_time_row = QHBoxLayout()
        close_time_row.setSpacing(15)
        
        close_time_label = QLabel("全关时间:")
        close_time_label.setObjectName("valve_config_label")
        close_time_label.setFont(QFont("Microsoft YaHei", 14))
        close_time_label.setFixedWidth(120)
        close_time_row.addWidget(close_time_label)
        
        # 全关时间 - 减少按钮
        btn_close_minus = QPushButton("-")
        btn_close_minus.setObjectName("btnMinus")
        btn_close_minus.setFixedSize(45, 45)
        btn_close_minus.setCursor(Qt.CursorShape.PointingHandCursor)
        close_time_row.addWidget(btn_close_minus)
        
        # 全关时间输入框
        close_time_input = QDoubleSpinBox()
        close_time_input.setObjectName("valve_time_input")
        close_time_input.setRange(1.0, 300.0)
        close_time_input.setDecimals(1)
        close_time_input.setSingleStep(1.0)
        close_time_input.setValue(config.full_close_time)
        close_time_input.setFixedSize(120, 45)
        close_time_input.setFont(QFont("Microsoft YaHei", 13))
        close_time_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        close_time_input.setSuffix(" 秒")
        close_time_row.addWidget(close_time_input)
        
        # 全关时间 - 增加按钮
        btn_close_plus = QPushButton("+")
        btn_close_plus.setObjectName("btnPlus")
        btn_close_plus.setFixedSize(45, 45)
        btn_close_plus.setCursor(Qt.CursorShape.PointingHandCursor)
        close_time_row.addWidget(btn_close_plus)
        
        # 连接按钮信号
        btn_close_minus.clicked.connect(lambda: close_time_input.setValue(close_time_input.value() - close_time_input.singleStep()))
        btn_close_plus.clicked.connect(lambda: close_time_input.setValue(close_time_input.value() + close_time_input.singleStep()))
        
        close_time_row.addStretch()
        
        # 说明文字
        close_time_desc = QLabel("从完全打开到完全关闭所需时间")
        close_time_desc.setObjectName("valve_config_desc")
        close_time_desc.setFont(QFont("Microsoft YaHei", 11))
        close_time_row.addWidget(close_time_desc)
        
        layout.addLayout(close_time_row)
        
        # 保存输入控件引用
        self.valve_config_inputs[valve_id] = {
            'full_open_time': open_time_input,
            'full_close_time': close_time_input,
        }
        
        return card
    
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
        
        # 冷却水流速阈值
        cooling_flow_group = self.create_threshold_group(
            "冷却水流速 (m\u00b3/h)",
            [
                ("cooling_flow_shell", "炉皮流速"),
                ("cooling_flow_cover", "炉盖流速"),
            ]
        )
        layout.addWidget(cooling_flow_group)
        
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
        warning_min_label.setObjectName("threshold_sub_label")
        warning_min_label.setFont(QFont("Microsoft YaHei", 13))
        warning_layout.addWidget(warning_min_label)
        
        # 警告下限 - 按钮
        btn_warning_min_minus = QPushButton("-")
        btn_warning_min_minus.setObjectName("btnMinus")
        btn_warning_min_minus.setFixedSize(45, 45)
        btn_warning_min_minus.setCursor(Qt.CursorShape.PointingHandCursor)
        warning_layout.addWidget(btn_warning_min_minus)
        
        warning_min = QDoubleSpinBox()
        warning_min.setObjectName("threshold_input")
        warning_min.setRange(-10000, 10000)
        warning_min.setDecimals(1)
        warning_min.setValue(config.warning_min if config and config.warning_min is not None else 0.0)
        warning_min.setFixedSize(120, 45)
        warning_min.setFont(QFont("Microsoft YaHei", 13))
        warning_min.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warning_min.setSpecialValueText("无限制")
        if config and config.warning_min is None:
            warning_min.setValue(warning_min.minimum())
        warning_layout.addWidget(warning_min)
        
        btn_warning_min_plus = QPushButton("+")
        btn_warning_min_plus.setObjectName("btnPlus")
        btn_warning_min_plus.setFixedSize(45, 45)
        btn_warning_min_plus.setCursor(Qt.CursorShape.PointingHandCursor)
        warning_layout.addWidget(btn_warning_min_plus)
        
        # 连接按钮信号
        btn_warning_min_minus.clicked.connect(lambda: warning_min.setValue(warning_min.value() - warning_min.singleStep()))
        btn_warning_min_plus.clicked.connect(lambda: warning_min.setValue(warning_min.value() + warning_min.singleStep()))
        
        # 警告上限
        warning_max_label = QLabel("上限:")
        warning_max_label.setObjectName("threshold_sub_label")
        warning_max_label.setFont(QFont("Microsoft YaHei", 13))
        warning_layout.addWidget(warning_max_label)
        
        # 警告上限 - 按钮
        btn_warning_max_minus = QPushButton("-")
        btn_warning_max_minus.setObjectName("btnMinus")
        btn_warning_max_minus.setFixedSize(45, 45)
        btn_warning_max_minus.setCursor(Qt.CursorShape.PointingHandCursor)
        warning_layout.addWidget(btn_warning_max_minus)
        
        warning_max = QDoubleSpinBox()
        warning_max.setObjectName("threshold_input")
        warning_max.setRange(-10000, 10000)
        warning_max.setDecimals(1)
        warning_max.setValue(config.warning_max if config and config.warning_max is not None else 0.0)
        warning_max.setFixedSize(120, 45)
        warning_max.setFont(QFont("Microsoft YaHei", 13))
        warning_max.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warning_max.setSpecialValueText("无限制")
        if config and config.warning_max is None:
            warning_max.setValue(warning_max.maximum())
        warning_layout.addWidget(warning_max)
        
        btn_warning_max_plus = QPushButton("+")
        btn_warning_max_plus.setObjectName("btnPlus")
        btn_warning_max_plus.setFixedSize(45, 45)
        btn_warning_max_plus.setCursor(Qt.CursorShape.PointingHandCursor)
        warning_layout.addWidget(btn_warning_max_plus)
        
        # 连接按钮信号
        btn_warning_max_minus.clicked.connect(lambda: warning_max.setValue(warning_max.value() - warning_max.singleStep()))
        btn_warning_max_plus.clicked.connect(lambda: warning_max.setValue(warning_max.value() + warning_max.singleStep()))
        
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
        alarm_min_label.setObjectName("threshold_sub_label")
        alarm_min_label.setFont(QFont("Microsoft YaHei", 13))
        alarm_layout.addWidget(alarm_min_label)
        
        # 报警下限 - 按钮
        btn_alarm_min_minus = QPushButton("-")
        btn_alarm_min_minus.setObjectName("btnMinus")
        btn_alarm_min_minus.setFixedSize(45, 45)
        btn_alarm_min_minus.setCursor(Qt.CursorShape.PointingHandCursor)
        alarm_layout.addWidget(btn_alarm_min_minus)
        
        alarm_min = QDoubleSpinBox()
        alarm_min.setObjectName("threshold_input")
        alarm_min.setRange(-10000, 10000)
        alarm_min.setDecimals(1)
        alarm_min.setValue(config.alarm_min if config and config.alarm_min is not None else 0.0)
        alarm_min.setFixedSize(120, 45)
        alarm_min.setFont(QFont("Microsoft YaHei", 13))
        alarm_min.setAlignment(Qt.AlignmentFlag.AlignCenter)
        alarm_min.setSpecialValueText("无限制")
        if config and config.alarm_min is None:
            alarm_min.setValue(alarm_min.minimum())
        alarm_layout.addWidget(alarm_min)
        
        btn_alarm_min_plus = QPushButton("+")
        btn_alarm_min_plus.setObjectName("btnPlus")
        btn_alarm_min_plus.setFixedSize(45, 45)
        btn_alarm_min_plus.setCursor(Qt.CursorShape.PointingHandCursor)
        alarm_layout.addWidget(btn_alarm_min_plus)
        
        # 连接按钮信号
        btn_alarm_min_minus.clicked.connect(lambda: alarm_min.setValue(alarm_min.value() - alarm_min.singleStep()))
        btn_alarm_min_plus.clicked.connect(lambda: alarm_min.setValue(alarm_min.value() + alarm_min.singleStep()))
        
        # 报警上限
        alarm_max_label = QLabel("上限:")
        alarm_max_label.setObjectName("threshold_sub_label")
        alarm_max_label.setFont(QFont("Microsoft YaHei", 13))
        alarm_layout.addWidget(alarm_max_label)
        
        # 报警上限 - 按钮
        btn_alarm_max_minus = QPushButton("-")
        btn_alarm_max_minus.setObjectName("btnMinus")
        btn_alarm_max_minus.setFixedSize(45, 45)
        btn_alarm_max_minus.setCursor(Qt.CursorShape.PointingHandCursor)
        alarm_layout.addWidget(btn_alarm_max_minus)
        
        alarm_max = QDoubleSpinBox()
        alarm_max.setObjectName("threshold_input")
        alarm_max.setRange(-10000, 10000)
        alarm_max.setDecimals(1)
        alarm_max.setValue(config.alarm_max if config and config.alarm_max is not None else 0.0)
        alarm_max.setFixedSize(120, 45)
        alarm_max.setFont(QFont("Microsoft YaHei", 13))
        alarm_max.setAlignment(Qt.AlignmentFlag.AlignCenter)
        alarm_max.setSpecialValueText("无限制")
        if config and config.alarm_max is None:
            alarm_max.setValue(alarm_max.maximum())
        alarm_layout.addWidget(alarm_max)
        
        btn_alarm_max_plus = QPushButton("+")
        btn_alarm_max_plus.setObjectName("btnPlus")
        btn_alarm_max_plus.setFixedSize(45, 45)
        btn_alarm_max_plus.setCursor(Qt.CursorShape.PointingHandCursor)
        alarm_layout.addWidget(btn_alarm_max_plus)
        
        # 连接按钮信号
        btn_alarm_max_minus.clicked.connect(lambda: alarm_max.setValue(alarm_max.value() - alarm_max.singleStep()))
        btn_alarm_max_plus.clicked.connect(lambda: alarm_max.setValue(alarm_max.value() + alarm_max.singleStep()))
        
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
        """保存所有配置（根据当前页面）"""
        try:
            if self.current_nav_index == 1:
                # 保存报警阈值配置
                self.save_alarm_threshold_config()
            elif self.current_nav_index == 3:
                # 保存蝶阀配置
                self.save_valve_config()
            else:
                # 其他页面暂不支持保存
                self.show_warning_dialog("当前页面无需保存配置")
        except Exception as e:
            logger.error(f"保存配置异常: {e}", exc_info=True)
            self.show_error_dialog(f"保存配置失败: {e}")
    
    # 16.1. 保存报警阈值配置
    def save_alarm_threshold_config(self):
        """保存报警阈值配置"""
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
            self.show_success_dialog("报警阈值配置已保存")
            logger.info("报警阈值配置已保存")
        else:
            self.show_warning_dialog("保存报警阈值配置失败，请检查日志")
    
    # 16.2. 保存蝶阀配置
    def save_valve_config(self):
        """保存蝶阀配置"""
        if not hasattr(self, 'valve_config_inputs') or not self.valve_config_inputs:
            self.show_warning_dialog("蝶阀配置输入控件未初始化")
            return
        
        # 遍历所有蝶阀，更新配置
        for valve_id, inputs in self.valve_config_inputs.items():
            full_open_time = inputs['full_open_time'].value()
            full_close_time = inputs['full_close_time'].value()
            
            # 更新配置
            self.valve_config_service.update_config(
                valve_id=valve_id,
                full_open_time=full_open_time,
                full_close_time=full_close_time
            )
        
        self.show_success_dialog("蝶阀配置已保存，重启程序后生效")
        logger.info("蝶阀配置已保存")
    
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
                background: transparent;
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
                background: transparent;
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
                background: transparent;
            }}
            
            /* 设置标签 */
            QLabel#setting_label {{
                color: {tm.text_primary()};
                background: transparent;
            }}
            
            /* 设置说明 */
            QLabel#setting_desc {{
                color: {tm.text_secondary()};
                background: transparent;
            }}
            
            /* 信息框 */
            QFrame#info_frame {{
                background: {tm.glow_primary()}1A;
                border: 1px solid {tm.glow_primary()}4D;
                border-radius: 6px;
            }}
            
            QLabel#info_icon {{
                color: {tm.glow_primary()};
                background: transparent;
            }}
            
            QLabel#info_text {{
                color: {tm.text_secondary()};
                background: transparent;
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
                background: transparent;
            }}
            
            /* 阈值行 */
            QFrame#threshold_row {{
                background: {tm.bg_light()};
                border: 1px solid {tm.border_dark()};
                border-radius: 6px;
            }}
            
            /* 参数名称 */
            QLabel#param_name {{
                color: {tm.text_primary()};
                background: transparent;
            }}
            
            /* 阈值标签 */
            QLabel#threshold_label {{
                color: {tm.text_primary()};
                font-weight: bold;
                background: transparent;
            }}
            
            /* 阈值子标签（上限、下限） */
            QLabel#threshold_sub_label {{
                color: {tm.text_primary()};
                background: transparent;
            }}
            
            /* 阈值输入框 */
            QDoubleSpinBox#threshold_input {{
                background: {tm.bg_medium()};
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
            
            /* 隐藏 SpinBox 的上下按钮 */
            QDoubleSpinBox#threshold_input::up-button,
            QDoubleSpinBox#threshold_input::down-button {{
                width: 0px;
                height: 0px;
            }}
            
            /* -/+ 按钮样式 */
            QPushButton#btnMinus, QPushButton#btnPlus {{
                background: {tm.bg_light()};
                color: {tm.text_primary()};
                border: 1px solid {tm.border_dark()};
                border-radius: 6px;
                font-size: 20px;
                font-weight: bold;
            }}
            
            QPushButton#btnMinus:hover, QPushButton#btnPlus:hover {{
                border: 1px solid {tm.border_glow()};
                background: {tm.bg_medium()};
            }}
            
            QPushButton#btnMinus:pressed, QPushButton#btnPlus:pressed {{
                background: {tm.bg_dark()};
            }}
            
            /* 启用复选框 */
            QCheckBox#enable_checkbox {{
                color: {tm.text_primary()};
                background: transparent;
            }}
            
            QCheckBox#enable_checkbox::indicator {{
                width: 22px;
                height: 22px;
                border: 2px solid {tm.border_dark()};
                border-radius: 4px;
                background: {tm.bg_medium()};
            }}
            
            QCheckBox#enable_checkbox::indicator:hover {{
                border: 2px solid {tm.border_glow()};
            }}
            
            QCheckBox#enable_checkbox::indicator:checked {{
                background: {tm.glow_primary()};
                border: 2px solid {tm.glow_primary()};
            }}
            
            /* 蝶阀配置卡片 */
            QFrame#valve_config_card {{
                background: {tm.bg_dark()};
                border: 1px solid {tm.border_medium()};
                border-radius: 8px;
            }}
            
            QLabel#valve_card_title {{
                color: {tm.border_glow()};
                background: transparent;
            }}
            
            QLabel#valve_config_label {{
                color: {tm.text_primary()};
                font-weight: bold;
                background: transparent;
            }}
            
            QLabel#valve_config_desc {{
                color: {tm.text_secondary()};
                background: transparent;
            }}
            
            /* 蝶阀时间输入框 */
            QDoubleSpinBox#valve_time_input {{
                background: {tm.bg_medium()};
                color: {tm.text_primary()};
                border: 1px solid {tm.border_dark()};
                border-radius: 6px;
                padding: 8px;
            }}
            
            QDoubleSpinBox#valve_time_input:hover {{
                border: 1px solid {tm.border_glow()};
            }}
            
            QDoubleSpinBox#valve_time_input:focus {{
                border: 2px solid {tm.glow_primary()};
            }}
            
            /* 隐藏 SpinBox 的上下按钮 */
            QDoubleSpinBox#valve_time_input::up-button,
            QDoubleSpinBox#valve_time_input::down-button {{
                width: 0px;
                height: 0px;
            }}
            
            /* 弧流设置卡片 */
            QFrame#arc_limit_card, QFrame#status_card {{
                background: {tm.bg_dark()};
                border: 1px solid {tm.border_medium()};
                border-radius: 8px;
            }}
            
            QLabel#card_title {{
                color: {tm.border_glow()};
                background: transparent;
            }}
            
            QLabel#value_label, QLabel#status_label {{
                color: {tm.text_primary()};
                background: transparent;
            }}
            
            QLabel#arc_limit_value {{
                color: {tm.glow_primary()};
                background: transparent;
            }}
            
            QLabel#stop_flag_active, QLabel#stop_enabled_active {{
                color: {tm.glow_green()};
                background: transparent;
            }}
            
            QLabel#stop_flag_inactive, QLabel#stop_enabled_inactive {{
                color: {tm.text_secondary()};
                background: transparent;
            }}
            
            QLabel#delay_value {{
                color: {tm.glow_primary()};
                background: transparent;
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
        current_theme = self.theme_manager.get_current_theme()
        for theme, btn in self.theme_buttons.items():
            accent = btn.property('accent')
            is_dark = self._is_dark_accent(accent)
            text_color = '#ffffff' if is_dark else '#000000'
            
            if theme == current_theme:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {accent};
                        color: {text_color};
                        border: 2px solid {accent};
                        border-radius: 6px;
                        font-size: 13px;
                        font-weight: bold;
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {tm.bg_dark()};
                        color: {tm.text_primary()};
                        border: 1px solid {tm.border_medium()};
                        border-radius: 6px;
                        font-size: 13px;
                        font-weight: normal;
                    }}
                    QPushButton:hover {{
                        background: {accent};
                        color: {text_color};
                        border: 1px solid {accent};
                    }}
                """)

