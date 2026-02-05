"""
历史数据查询控制栏组件
"""
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import pyqtSignal, Qt, QDateTime, QTimer
from ui.styles.themes import ThemeManager
from ui.widgets.history_curve.dropdown_tech import DropdownTech, DropdownMultiSelect
from ui.widgets.history_curve.widget_time_selector import WidgetTimeSelector
from backend.bridge.history_query import get_history_query_service
from loguru import logger


class BarHistory(QWidget):
    """历史数据查询控制栏"""
    
    mode_changed = pyqtSignal(bool)
    batch_changed = pyqtSignal(str)
    batches_changed = pyqtSignal(list)
    time_range_changed = pyqtSignal(QDateTime, QDateTime)
    query_clicked = pyqtSignal()  # 查询按钮点击信号
    export_clicked = pyqtSignal()  # 导出按钮点击信号
    batch_time_range_loaded = pyqtSignal(str, object, object)  # 批次时间范围加载完成信号 (batch_code, start_time, end_time)
    
    # 1. 初始化组件
    def __init__(self, accent_color: str = None, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        self.accent_color = accent_color or self.theme_manager.glow_cyan()
        
        self.is_history_mode = False
        self.batch_options = []
        self.selected_batch = ""
        self.selected_batches = []
        
        # 批次时间范围
        self.batch_start_time = None
        self.batch_end_time = None
        self.batch_duration_hours = 0.0
        
        # Mock 模式标志
        self.use_mock = False
        
        self.history_service = get_history_query_service()
        
        self.init_ui()
        self.apply_styles()
        
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
        
        self.load_batch_list()
    
    # 2. 初始化 UI
    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(24)
        
        colors = self.theme_manager.get_colors()
        
        self.history_mode_btn = QPushButton("历史轮次查询")
        self.history_mode_btn.setFixedHeight(32)
        self.history_mode_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.history_mode_btn.clicked.connect(self.toggle_history_mode)
        layout.addWidget(self.history_mode_btn)
        
        self.batch_dropdown = DropdownTech(
            self.batch_options,
            self.selected_batch,
            accent_color=colors.GLOW_CYAN
        )
        self.batch_dropdown.selection_changed.connect(self.on_batch_changed)
        layout.addWidget(self.batch_dropdown)
        
        self.batch_multi_dropdown = DropdownMultiSelect(
            self.batch_options,
            self.selected_batches,
            accent_color=colors.GLOW_CYAN
        )
        self.batch_multi_dropdown.selection_changed.connect(self.on_batches_changed)
        self.batch_multi_dropdown.hide()
        layout.addWidget(self.batch_multi_dropdown)
        
        self.time_selector = WidgetTimeSelector(accent_color=colors.GLOW_CYAN)
        self.time_selector.time_range_changed.connect(self.on_time_range_changed)
        layout.addWidget(self.time_selector)
        
        # 查询按钮
        self.query_btn = QPushButton("查询")
        self.query_btn.setFixedHeight(32)
        self.query_btn.setFixedWidth(80)
        self.query_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.query_btn.clicked.connect(self.on_query_clicked)
        layout.addWidget(self.query_btn)
        
        # 导出按钮
        self.export_btn = QPushButton("导出数据")
        self.export_btn.setFixedHeight(32)
        self.export_btn.setFixedWidth(100)
        self.export_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.export_btn.clicked.connect(self.on_export_clicked)
        layout.addWidget(self.export_btn)
        
        layout.addStretch()
    
    # 3. 加载批次列表
    def load_batch_list(self, use_mock: bool = False):
        """从数据库加载批次列表（支持Mock模式）"""
        try:
            logger.info("开始加载批次列表...")
            
            # 保存 Mock 模式标志
            self.use_mock = use_mock
            
            # Mock模式：生成50个测试批次
            if use_mock:
                logger.info("使用Mock模式，生成50个测试批次...")
                from datetime import datetime, timedelta
                base_date = datetime(2026, 2, 5)
                self.batch_options = []
                for i in range(50):
                    date = base_date - timedelta(days=i)
                    batch_code = date.strftime("%Y%m%d") + f"{i % 10 + 1:02d}"
                    self.batch_options.append(batch_code)
                
                # 默认选中前3个批次
                self.selected_batch = self.batch_options[0]
                self.selected_batches = self.batch_options[:3]
                
                logger.info(f"Mock模式：生成了 {len(self.batch_options)} 个批次")
            else:
                # 真实模式：从数据库加载
                batches = self.history_service.get_batch_list(limit=50)
                
                if batches:
                    self.batch_options = [b["batch_code"] for b in batches]
                    
                    # 默认选中第一个（最新的）批次
                    if self.batch_options:
                        self.selected_batch = self.batch_options[0]
                        self.selected_batches = [self.batch_options[0]]
                        
                        logger.info(f"默认选中批次: {self.selected_batch}")
                    
                    logger.info(f"成功加载 {len(self.batch_options)} 个批次")
                else:
                    logger.warning("未查询到批次数据")
                    self.batch_options = ["无数据"]
                    self.selected_batch = ""
            
            # 更新下拉框
            self.batch_dropdown.set_options(self.batch_options)
            self.batch_dropdown.set_value(self.selected_batch)
            
            self.batch_multi_dropdown.set_options(self.batch_options)
            self.batch_multi_dropdown.set_values(self.selected_batches)
            
            # 发送批次选择变化信号
            if self.selected_batch:
                self.batch_changed.emit(self.selected_batch)
                
        except Exception as e:
            logger.error(f"加载批次列表失败: {e}")
            self.batch_options = ["加载失败"]
            self.selected_batch = ""
            self.batch_dropdown.set_options(self.batch_options)
            self.batch_multi_dropdown.set_options(self.batch_options)
    
    # 4. 切换历史模式
    def toggle_history_mode(self):
        self.is_history_mode = not self.is_history_mode
        
        if self.is_history_mode:
            self.batch_dropdown.hide()
            self.batch_multi_dropdown.show()
            self.time_selector.hide()
        else:
            self.batch_multi_dropdown.hide()
            self.batch_dropdown.show()
            self.time_selector.show()
        
        self.update_history_mode_button()
        self.mode_changed.emit(self.is_history_mode)
    
    # 5. 更新历史模式按钮样式
    def update_history_mode_button(self):
        colors = self.theme_manager.get_colors()
        
        if self.is_history_mode:
            # 选中状态：使用 TEXT_SELECTED（深色主题青色，浅色主题深绿）
            self.history_mode_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {colors.GLOW_CYAN}33;
                    color: {colors.TEXT_SELECTED};
                    border: 1.5px solid {colors.GLOW_CYAN};
                    border-radius: 4px;
                    padding: 6px 16px;
                    font-size: 14px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background: {colors.GLOW_CYAN}4D;
                }}
            """)
        else:
            # 未选中状态
            self.history_mode_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {colors.BTN_BG_NORMAL};
                    color: {colors.TEXT_PRIMARY};
                    border: 1px solid {colors.BORDER_MEDIUM};
                    border-radius: 4px;
                    padding: 6px 16px;
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background: {colors.BTN_BG_HOVER};
                    border: 1px solid {colors.GLOW_CYAN};
                }}
            """)
    
    # 6. 批次选择变化
    def on_batch_changed(self, batch: str):
        self.selected_batch = batch
        
        # Mock 模式下不查询批次时间范围
        if not self.use_mock:
            # 查询批次时间范围
            self.query_batch_time_range(batch)
        
        self.batch_changed.emit(batch)
    
    # 6.1. 查询批次时间范围
    def query_batch_time_range(self, batch_code: str):
        """查询批次的时间范围，并更新时间选择器（Mock模式下跳过）"""
        if not batch_code or batch_code in ["无数据", "加载失败"]:
            return
        
        # Mock 模式下跳过查询
        if self.use_mock:
            logger.info(f"Mock模式：跳过批次 {batch_code} 的时间范围查询")
            return
        
        try:
            logger.info(f"查询批次 {batch_code} 的时间范围...")
            start_time, end_time = self.history_service.query_batch_time_range(batch_code)
            
            if start_time and end_time:
                self.batch_start_time = start_time
                self.batch_end_time = end_time
                
                # 计算批次总时长（小时）
                duration_seconds = (end_time - start_time).total_seconds()
                self.batch_duration_hours = duration_seconds / 3600.0
                
                logger.info(f"批次 {batch_code} 时间范围: {start_time} - {end_time}, 总时长: {self.batch_duration_hours:.1f}h")
                
                # 更新时间选择器的时间范围（不触发自动查询）
                self.time_selector.set_batch_time_range(start_time, end_time, self.batch_duration_hours)
                
                # 发送批次时间范围加载完成信号
                self.batch_time_range_loaded.emit(batch_code, start_time, end_time)
                
                logger.info(f"批次时间范围已设置，请点击查询按钮查询数据")
            else:
                logger.warning(f"批次 {batch_code} 没有找到时间范围")
                self.batch_start_time = None
                self.batch_end_time = None
                self.batch_duration_hours = 0.0
                
        except Exception as e:
            logger.error(f"查询批次时间范围失败: {e}", exc_info=True)
            self.batch_start_time = None
            self.batch_end_time = None
            self.batch_duration_hours = 0.0
    
    # 7. 批次多选变化
    def on_batches_changed(self, batches: list):
        self.selected_batches = batches
        self.batches_changed.emit(batches)
    
    # 8. 时间范围变化
    def on_time_range_changed(self, start: QDateTime, end: QDateTime):
        self.time_range_changed.emit(start, end)
    
    # 9. 查询按钮点击
    def on_query_clicked(self):
        logger.info(f"点击查询按钮 - 批次: {self.selected_batch}, 时间范围: {self.time_selector.get_time_range()}")
        self.query_clicked.emit()
    
    # 9.1. 导出按钮点击
    def on_export_clicked(self):
        logger.info(f"点击导出按钮 - 批次: {self.selected_batch}")
        self.export_clicked.emit()
    
    # 10. 获取当前模式
    def get_mode(self) -> bool:
        return self.is_history_mode
    
    # 11. 获取选中的批次
    def get_selected_batch(self) -> str:
        return self.selected_batch
    
    # 12. 获取选中的批次列表
    def get_selected_batches(self) -> list:
        return self.selected_batches
    
    # 13. 获取时间范围
    def get_time_range(self) -> tuple:
        return self.time_selector.get_time_range()
    
    # 13.1. 获取批次时间范围
    def get_batch_time_range(self) -> tuple:
        """获取批次的完整时间范围"""
        return (self.batch_start_time, self.batch_end_time)
    
    # 13.2. 获取批次总时长
    def get_batch_duration_hours(self) -> float:
        """获取批次总时长（小时）"""
        return self.batch_duration_hours
    
    # 14. 刷新批次列表
    def refresh_batch_list(self):
        self.load_batch_list()
    
    # 15. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        self.setStyleSheet(f"""
            BarHistory {{
                background: {colors.BG_DARK};
                border: 1px solid {colors.BORDER_MEDIUM};
                border-radius: 4px;
            }}
        """)
        
        self.update_history_mode_button()
        self.update_query_button()
        self.update_export_button()
    
    # 16. 更新查询按钮样式
    def update_query_button(self):
        colors = self.theme_manager.get_colors()
        
        # 查询按钮：主色背景，使用 TEXT_ON_PRIMARY（深色主题深色，浅色主题白色）
        self.query_btn.setStyleSheet(f"""
            QPushButton {{
                background: {colors.GLOW_CYAN};
                color: {colors.TEXT_ON_PRIMARY};
                border: none;
                border-radius: 4px;
                padding: 6px 16px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {colors.GLOW_CYAN}CC;
            }}
            QPushButton:pressed {{
                background: {colors.GLOW_CYAN}99;
            }}
        """)
    
    # 16.1. 更新导出按钮样式
    def update_export_button(self):
        colors = self.theme_manager.get_colors()
        # 导出按钮：次要按钮样式
        self.export_btn.setStyleSheet(f"""
            QPushButton {{
                background: {colors.BTN_BG_NORMAL};
                color: {colors.TEXT_PRIMARY};
                border: 1px solid {colors.BORDER_MEDIUM};
                border-radius: 4px;
                padding: 6px 16px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {colors.BTN_BG_HOVER};
                border: 1px solid {colors.GLOW_CYAN};
            }}
            QPushButton:pressed {{
                background: {colors.BG_MEDIUM};
            }}
        """)
    
    # 17. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()

