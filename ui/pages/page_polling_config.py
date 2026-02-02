"""
轮询速度配置页面
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QRadioButton, QButtonGroup, QFrame
)
from PyQt6.QtCore import Qt
from ui.styles.themes import ThemeManager
from backend.config.polling_config import get_polling_config
from loguru import logger


class PagePollingConfig(QWidget):
    """轮询速度配置页面"""
    
    # 1. 初始化页面
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        self.polling_config = get_polling_config()
        
        self.init_ui()
        self.apply_styles()
        
        # 监听主题变化
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
    
    # 2. 初始化 UI
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 标题
        title_label = QLabel("轮询速度配置")
        title_label.setObjectName("title")
        main_layout.addWidget(title_label)
        
        # 说明文字
        desc_label = QLabel(
            "调整 DB1 弧流弧压数据的轮询速度。\n"
            "高速模式（0.2s）适合精细监控，低速模式（0.5s）适合常规监控。"
        )
        desc_label.setObjectName("description")
        desc_label.setWordWrap(True)
        main_layout.addWidget(desc_label)
        
        # 配置面板
        config_panel = QFrame()
        config_panel.setObjectName("configPanel")
        config_layout = QVBoxLayout(config_panel)
        config_layout.setContentsMargins(20, 20, 20, 20)
        config_layout.setSpacing(15)
        
        # 轮询速度选择
        speed_label = QLabel("DB1 轮询速度:")
        speed_label.setObjectName("sectionLabel")
        config_layout.addWidget(speed_label)
        
        # 单选按钮组
        self.speed_button_group = QButtonGroup(self)
        
        # 0.5s 选项
        self.radio_05s = QRadioButton("0.5s (推荐)")
        self.radio_05s.setObjectName("radio_05s")
        self.speed_button_group.addButton(self.radio_05s, 0)
        config_layout.addWidget(self.radio_05s)
        
        speed_05s_desc = QLabel("    常规监控模式，平衡性能与数据精度")
        speed_05s_desc.setObjectName("optionDesc")
        config_layout.addWidget(speed_05s_desc)
        
        # 0.2s 选项
        self.radio_02s = QRadioButton("0.2s (高速)")
        self.radio_02s.setObjectName("radio_02s")
        self.speed_button_group.addButton(self.radio_02s, 1)
        config_layout.addWidget(self.radio_02s)
        
        speed_02s_desc = QLabel("    高速监控模式，图表刷新更流畅，数据更精细")
        speed_02s_desc.setObjectName("optionDesc")
        config_layout.addWidget(speed_02s_desc)
        
        main_layout.addWidget(config_panel)
        
        # 影响说明
        impact_label = QLabel("配置影响:")
        impact_label.setObjectName("sectionLabel")
        main_layout.addWidget(impact_label)
        
        impact_panel = QFrame()
        impact_panel.setObjectName("impactPanel")
        impact_layout = QVBoxLayout(impact_panel)
        impact_layout.setContentsMargins(15, 15, 15, 15)
        impact_layout.setSpacing(10)
        
        impact_items = [
            "卡片数据: 始终保持 0.5s 刷新（不受影响）",
            "图表刷新: 跟随轮询速度（0.2s 或 0.5s）",
            "能耗计算: 每 30 条数据触发一次（不受影响）",
            "数据库写入: 批量写入频率不变",
        ]
        
        for item in impact_items:
            item_label = QLabel(f"• {item}")
            item_label.setObjectName("impactItem")
            impact_layout.addWidget(item_label)
        
        main_layout.addWidget(impact_panel)
        
        main_layout.addStretch()
        
        # 加载当前配置
        self.load_current_config()
        
        # 连接信号
        self.speed_button_group.buttonClicked.connect(self.on_speed_changed)
    
    # 3. 加载当前配置
    def load_current_config(self):
        """从配置管理器加载当前配置"""
        current_speed = self.polling_config.get_polling_speed()
        
        if current_speed == "0.2s":
            self.radio_02s.setChecked(True)
        else:
            self.radio_05s.setChecked(True)
    
    # 4. 轮询速度变化
    def on_speed_changed(self, button):
        """轮询速度单选按钮变化"""
        if button == self.radio_02s:
            new_speed = "0.2s"
        else:
            new_speed = "0.5s"
        
        # 更新配置
        self.polling_config.set_polling_speed(new_speed)
        logger.info(f"轮询速度已修改: {new_speed}")
    
    # 5. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        self.setStyleSheet(f"""
            PagePollingConfig {{
                background: {colors.BG_DEEP};
            }}
            
            QLabel#title {{
                color: {colors.GLOW_PRIMARY};
                font-size: 24px;
                font-weight: bold;
            }}
            
            QLabel#description {{
                color: {colors.TEXT_PRIMARY};
                font-size: 14px;
                line-height: 1.6;
            }}
            
            QFrame#configPanel {{
                background: {colors.BG_LIGHT};
                border: 1px solid {colors.BORDER_GLOW};
                border-radius: 8px;
            }}
            
            QLabel#sectionLabel {{
                color: {colors.GLOW_PRIMARY};
                font-size: 16px;
                font-weight: bold;
            }}
            
            QRadioButton {{
                color: {colors.TEXT_PRIMARY};
                font-size: 14px;
                font-weight: bold;
                spacing: 8px;
            }}
            
            QRadioButton::indicator {{
                width: 18px;
                height: 18px;
            }}
            
            QRadioButton::indicator:unchecked {{
                border: 2px solid {colors.BORDER_DARK};
                border-radius: 9px;
                background: {colors.BG_DEEP};
            }}
            
            QRadioButton::indicator:checked {{
                border: 2px solid {colors.GLOW_PRIMARY};
                border-radius: 9px;
                background: {colors.GLOW_PRIMARY};
            }}
            
            QLabel#optionDesc {{
                color: {colors.TEXT_SECONDARY};
                font-size: 12px;
                margin-left: 26px;
            }}
            
            QFrame#impactPanel {{
                background: {colors.BG_LIGHT};
                border: 1px solid {colors.BORDER_DARK};
                border-radius: 8px;
            }}
            
            QLabel#impactItem {{
                color: {colors.TEXT_PRIMARY};
                font-size: 13px;
            }}
        """)
    
    # 6. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()

