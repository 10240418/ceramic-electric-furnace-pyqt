"""
QSS 样式表生成器 - 根据当前主题生成 QSS 样式
"""
from .themes import ThemeManager


class QSSStyles:
    """QSS 样式表生成器"""
    
    # 1. 初始化样式生成器
    def __init__(self, theme_manager: ThemeManager):
        self.theme = theme_manager
    
    # 2. 获取全局样式
    def get_global_style(self) -> str:
        return f"""
        /* ===== 全局样式 ===== */
        QWidget {{
            background-color: {self.theme.bg_dark()};
            color: {self.theme.text_primary()};
            font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
            font-size: 14px;
        }}
        
        /* ===== 主窗口 ===== */
        QMainWindow {{
            background-color: {self.theme.bg_dark()};
        }}
        
        /* ===== 滚动条 ===== */
        QScrollBar:vertical {{
            background-color: {self.theme.bg_medium()};
            width: 12px;
            border: none;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {self.theme.border_dark()};
            min-height: 30px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {self.theme.border_glow()};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        QScrollBar:horizontal {{
            background-color: {self.theme.bg_medium()};
            height: 12px;
            border: none;
        }}
        
        QScrollBar::handle:horizontal {{
            background-color: {self.theme.border_dark()};
            min-width: 30px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background-color: {self.theme.border_glow()};
        }}
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        
        /* ===== 工具提示 ===== */
        QToolTip {{
            background-color: {self.theme.bg_medium()};
            color: {self.theme.text_primary()};
            border: 1px solid {self.theme.border_glow()};
            padding: 4px;
            border-radius: 4px;
        }}
        """
    
    # 3. 获取按钮样式
    def get_button_style(self) -> str:
        return f"""
        /* ===== 普通按钮 ===== */
        QPushButton {{
            background-color: {self.theme.bg_medium()};
            color: {self.theme.text_primary()};
            border: 1px solid {self.theme.border_dark()};
            border-radius: 4px;
            padding: 8px 16px;
            font-size: 14px;
            font-weight: 500;
        }}
        
        QPushButton:hover {{
            background-color: {self.theme.bg_light()};
            border: 1px solid {self.theme.border_glow()};
        }}
        
        QPushButton:pressed {{
            background-color: {self.theme.bg_dark()};
            border: 1px solid {self.theme.border_glow()};
        }}
        
        QPushButton:disabled {{
            background-color: {self.theme.bg_dark()};
            color: {self.theme.text_muted()};
            border: 1px solid {self.theme.border_dark()};
        }}
        
        /* ===== 主要按钮（强调）===== */
        QPushButton[primary="true"] {{
            background-color: {self.theme.border_glow()};
            color: {self.theme.bg_dark()};
            border: 1px solid {self.theme.border_glow()};
            font-weight: 600;
        }}
        
        QPushButton[primary="true"]:hover {{
            background-color: {self.theme.glow_cyan_light()};
            border: 1px solid {self.theme.glow_cyan_light()};
        }}
        
        QPushButton[primary="true"]:pressed {{
            background-color: {self.theme.glow_cyan()};
        }}
        
        /* ===== 危险按钮 ===== */
        QPushButton[danger="true"] {{
            background-color: {self.theme.glow_red()};
            color: {self.theme.white()};
            border: 1px solid {self.theme.glow_red()};
        }}
        
        QPushButton[danger="true"]:hover {{
            background-color: #ff5544;
            border: 1px solid #ff5544;
        }}
        """
    
    # 4. 获取面板样式
    def get_panel_style(self) -> str:
        return f"""
        /* ===== 科技风面板 ===== */
        QFrame[tech_panel="true"] {{
            background-color: {self.theme.bg_medium()};
            border: 1px solid {self.theme.border_glow()};
            border-radius: 4px;
        }}
        
        /* ===== 面板标题 ===== */
        QLabel[panel_title="true"] {{
            background-color: {self.theme.bg_dark()};
            color: {self.theme.border_glow()};
            font-size: 16px;
            font-weight: 600;
            padding: 8px 12px;
            border-bottom: 1px solid {self.theme.border_glow()};
        }}
        
        /* ===== 数据卡片 ===== */
        QFrame[data_card="true"] {{
            background-color: {self.theme.bg_light()};
            border: 1px solid {self.theme.border_dark()};
            border-radius: 4px;
            padding: 12px;
        }}
        
        QFrame[data_card="true"]:hover {{
            border: 1px solid {self.theme.border_glow()};
        }}
        """
    
    # 5. 获取输入框样式
    def get_input_style(self) -> str:
        return f"""
        /* ===== 文本输入框 ===== */
        QLineEdit {{
            background-color: {self.theme.bg_light()};
            color: {self.theme.text_primary()};
            border: 1px solid {self.theme.border_dark()};
            border-radius: 4px;
            padding: 6px 10px;
            font-size: 14px;
        }}
        
        QLineEdit:focus {{
            border: 1px solid {self.theme.border_glow()};
        }}
        
        QLineEdit:disabled {{
            background-color: {self.theme.bg_dark()};
            color: {self.theme.text_muted()};
        }}
        
        /* ===== 文本编辑框 ===== */
        QTextEdit {{
            background-color: {self.theme.bg_light()};
            color: {self.theme.text_primary()};
            border: 1px solid {self.theme.border_dark()};
            border-radius: 4px;
            padding: 8px;
            font-size: 14px;
        }}
        
        QTextEdit:focus {{
            border: 1px solid {self.theme.border_glow()};
        }}
        
        /* ===== 下拉框 ===== */
        QComboBox {{
            background-color: {self.theme.bg_light()};
            color: {self.theme.text_primary()};
            border: 1px solid {self.theme.border_dark()};
            border-radius: 4px;
            padding: 6px 10px;
            font-size: 14px;
        }}
        
        QComboBox:hover {{
            border: 1px solid {self.theme.border_glow()};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 6px solid {self.theme.text_primary()};
            margin-right: 8px;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {self.theme.bg_medium()};
            color: {self.theme.text_primary()};
            border: 1px solid {self.theme.border_glow()};
            selection-background-color: {self.theme.bg_light()};
            selection-color: {self.theme.border_glow()};
        }}
        
        /* ===== 数字输入框 ===== */
        QSpinBox, QDoubleSpinBox {{
            background-color: {self.theme.bg_light()};
            color: {self.theme.text_primary()};
            border: 1px solid {self.theme.border_dark()};
            border-radius: 4px;
            padding: 6px 10px;
            font-size: 14px;
        }}
        
        QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 1px solid {self.theme.border_glow()};
        }}
        
        QSpinBox::up-button, QDoubleSpinBox::up-button {{
            background-color: {self.theme.bg_medium()};
            border-left: 1px solid {self.theme.border_dark()};
            border-radius: 0px 4px 0px 0px;
        }}
        
        QSpinBox::down-button, QDoubleSpinBox::down-button {{
            background-color: {self.theme.bg_medium()};
            border-left: 1px solid {self.theme.border_dark()};
            border-radius: 0px 0px 4px 0px;
        }}
        """
    
    # 6. 获取标签样式
    def get_label_style(self) -> str:
        return f"""
        /* ===== 普通标签 ===== */
        QLabel {{
            color: {self.theme.text_primary()};
            background-color: transparent;
            font-size: 14px;
        }}
        
        /* ===== 标题标签 ===== */
        QLabel[heading="h1"] {{
            font-size: 24px;
            font-weight: 700;
            color: {self.theme.border_glow()};
        }}
        
        QLabel[heading="h2"] {{
            font-size: 20px;
            font-weight: 600;
            color: {self.theme.border_glow()};
        }}
        
        QLabel[heading="h3"] {{
            font-size: 16px;
            font-weight: 600;
            color: {self.theme.text_primary()};
        }}
        
        /* ===== 次要文字 ===== */
        QLabel[secondary="true"] {{
            color: {self.theme.text_secondary()};
            font-size: 13px;
        }}
        
        /* ===== 弱化文字 ===== */
        QLabel[muted="true"] {{
            color: {self.theme.text_muted()};
            font-size: 12px;
        }}
        
        /* ===== 数值标签（大号）===== */
        QLabel[value="true"] {{
            font-size: 28px;
            font-weight: 700;
            color: {self.theme.border_glow()};
            font-family: "Consolas", "Courier New", monospace;
        }}
        
        /* ===== 状态标签 ===== */
        QLabel[status="normal"] {{
            color: {self.theme.status_normal()};
            font-weight: 600;
        }}
        
        QLabel[status="warning"] {{
            color: {self.theme.status_warning()};
            font-weight: 600;
        }}
        
        QLabel[status="alarm"] {{
            color: {self.theme.status_alarm()};
            font-weight: 600;
        }}
        
        QLabel[status="offline"] {{
            color: {self.theme.status_offline()};
            font-weight: 600;
        }}
        """
    
    # 7. 获取表格样式
    def get_table_style(self) -> str:
        return f"""
        /* ===== 表格 ===== */
        QTableWidget {{
            background-color: {self.theme.bg_medium()};
            color: {self.theme.text_primary()};
            border: 1px solid {self.theme.border_dark()};
            gridline-color: {self.theme.grid_line()};
            selection-background-color: {self.theme.bg_light()};
            selection-color: {self.theme.border_glow()};
        }}
        
        QTableWidget::item {{
            padding: 8px;
            border: none;
        }}
        
        QTableWidget::item:hover {{
            background-color: {self.theme.bg_light()};
        }}
        
        QTableWidget::item:selected {{
            background-color: {self.theme.bg_light()};
            color: {self.theme.border_glow()};
        }}
        
        QHeaderView::section {{
            background-color: {self.theme.bg_dark()};
            color: {self.theme.border_glow()};
            padding: 8px;
            border: none;
            border-bottom: 1px solid {self.theme.border_glow()};
            font-weight: 600;
        }}
        
        QHeaderView::section:hover {{
            background-color: {self.theme.bg_medium()};
        }}
        """
    
    # 8. 获取选项卡样式
    def get_tab_style(self) -> str:
        return f"""
        /* ===== 选项卡容器 ===== */
        QTabWidget::pane {{
            background-color: {self.theme.bg_medium()};
            border: 1px solid {self.theme.border_dark()};
            border-radius: 4px;
        }}
        
        /* ===== 选项卡栏 ===== */
        QTabBar::tab {{
            background-color: {self.theme.bg_dark()};
            color: {self.theme.text_secondary()};
            border: 1px solid {self.theme.border_dark()};
            border-bottom: none;
            padding: 10px 20px;
            margin-right: 2px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }}
        
        QTabBar::tab:hover {{
            background-color: {self.theme.bg_medium()};
            color: {self.theme.text_primary()};
        }}
        
        QTabBar::tab:selected {{
            background-color: {self.theme.bg_medium()};
            color: {self.theme.border_glow()};
            border: 1px solid {self.theme.border_glow()};
            border-bottom: none;
            font-weight: 600;
        }}
        """
    
    # 9. 获取复选框样式
    def get_checkbox_style(self) -> str:
        return f"""
        /* ===== 复选框 ===== */
        QCheckBox {{
            color: {self.theme.text_primary()};
            spacing: 8px;
        }}
        
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 1px solid {self.theme.border_dark()};
            border-radius: 3px;
            background-color: {self.theme.bg_light()};
        }}
        
        QCheckBox::indicator:hover {{
            border: 1px solid {self.theme.border_glow()};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {self.theme.border_glow()};
            border: 1px solid {self.theme.border_glow()};
        }}
        
        /* ===== 单选框 ===== */
        QRadioButton {{
            color: {self.theme.text_primary()};
            spacing: 8px;
        }}
        
        QRadioButton::indicator {{
            width: 18px;
            height: 18px;
            border: 1px solid {self.theme.border_dark()};
            border-radius: 9px;
            background-color: {self.theme.bg_light()};
        }}
        
        QRadioButton::indicator:hover {{
            border: 1px solid {self.theme.border_glow()};
        }}
        
        QRadioButton::indicator:checked {{
            background-color: {self.theme.border_glow()};
            border: 1px solid {self.theme.border_glow()};
        }}
        """
    
    # 10. 获取滑块样式
    def get_slider_style(self) -> str:
        return f"""
        /* ===== 滑块 ===== */
        QSlider::groove:horizontal {{
            background-color: {self.theme.bg_light()};
            height: 6px;
            border-radius: 3px;
        }}
        
        QSlider::handle:horizontal {{
            background-color: {self.theme.border_glow()};
            width: 16px;
            height: 16px;
            margin: -5px 0;
            border-radius: 8px;
        }}
        
        QSlider::handle:horizontal:hover {{
            background-color: {self.theme.glow_cyan_light()};
        }}
        
        QSlider::sub-page:horizontal {{
            background-color: {self.theme.border_glow()};
            border-radius: 3px;
        }}
        """
    
    # 11. 获取进度条样式
    def get_progress_style(self) -> str:
        return f"""
        /* ===== 进度条 ===== */
        QProgressBar {{
            background-color: {self.theme.bg_light()};
            border: 1px solid {self.theme.border_dark()};
            border-radius: 4px;
            text-align: center;
            color: {self.theme.text_primary()};
            font-weight: 600;
        }}
        
        QProgressBar::chunk {{
            background-color: {self.theme.border_glow()};
            border-radius: 3px;
        }}
        """
    
    # 12. 获取所有样式（合并）
    def get_all_styles(self) -> str:
        return '\n'.join([
            self.get_global_style(),
            self.get_button_style(),
            self.get_panel_style(),
            self.get_input_style(),
            self.get_label_style(),
            self.get_table_style(),
            self.get_tab_style(),
            self.get_checkbox_style(),
            self.get_slider_style(),
            self.get_progress_style(),
        ])

