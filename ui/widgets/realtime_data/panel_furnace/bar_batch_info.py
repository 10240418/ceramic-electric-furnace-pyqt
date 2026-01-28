"""
炉次信息栏组件 - 显示炉次信息和控制按钮
"""
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import pyqtSignal
from ui.styles.themes import ThemeManager


class BarBatchInfo(QFrame):
    """炉次信息栏组件"""
    
    # 信号定义
    stop_clicked = pyqtSignal()   # 中止冶炼信号
    finish_clicked = pyqtSignal() # 结束冶炼信号
    
    # 1. 初始化组件
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        self.setObjectName("batchInfoBar")
        
        self.batch_no = ""
        self.start_time = ""
        self.run_duration = ""
        
        # 确保背景完全不透明
        self.setAutoFillBackground(True)
        
        self.init_ui()
        self.apply_styles()
        
        # 提升到最上层
        self.raise_()
        
        # 监听主题变化
        self.theme_manager.theme_changed.connect(self.on_theme_changed)
    
    # 2. 初始化 UI
    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(16)
        
        # 炉次信息文本
        self.info_label = QLabel()
        self.info_label.setObjectName("batchInfoLabel")
        layout.addWidget(self.info_label, stretch=1)
        
        # 中止冶炼按钮
        self.btn_stop = QPushButton("中止冶炼")
        self.btn_stop.setObjectName("btnStop")
        self.btn_stop.setFixedSize(100, 36)
        self.btn_stop.clicked.connect(self.stop_clicked.emit)
        layout.addWidget(self.btn_stop)
        
        # 结束冶炼按钮
        self.btn_finish = QPushButton("结束冶炼")
        self.btn_finish.setObjectName("btnFinish")
        self.btn_finish.setFixedSize(100, 36)
        self.btn_finish.clicked.connect(self.finish_clicked.emit)
        layout.addWidget(self.btn_finish)
    
    # 3. 设置炉次信息
    def set_batch_info(self, batch_no: str, start_time: str, run_duration: str):
        """
        设置炉次信息
        
        Args:
            batch_no: 炉次编号
            start_time: 开始时间
            run_duration: 运行时长
        """
        self.batch_no = batch_no
        self.start_time = start_time
        self.run_duration = run_duration
        self.update_display()
    
    # 4. 更新显示
    def update_display(self):
        text = f"炉次编号: {self.batch_no}  |  " \
               f"开始时间: {self.start_time}  |  " \
               f"运行时长: {self.run_duration}"
        self.info_label.setText(text)
    
    # 5. 应用样式
    def apply_styles(self):
        colors = self.theme_manager.get_colors()
        
        self.setStyleSheet(f"""
            QFrame#batchInfoBar {{
                background: {colors.BG_LIGHT};
                border: 1px solid {colors.BORDER_GLOW};
                border-radius: 4px;
            }}
            
            QLabel#batchInfoLabel {{
                color: {colors.TEXT_PRIMARY};
                font-size: 14px;
                font-weight: bold;
            }}
            
            QPushButton#btnStop, QPushButton#btnFinish {{
                background: {colors.BG_MEDIUM};
                color: {colors.TEXT_PRIMARY};
                border: 1px solid {colors.BORDER_DARK};
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
            }}
            
            QPushButton#btnStop:hover, QPushButton#btnFinish:hover {{
                border: 1px solid {colors.BORDER_GLOW};
                background: {colors.BG_LIGHT};
            }}
            
            QPushButton#btnStop:pressed, QPushButton#btnFinish:pressed {{
                background: {colors.BG_DARK};
            }}
        """)
    
    # 6. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()

