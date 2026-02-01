"""
炉次信息栏组件 - 显示炉次信息和控制按钮
"""
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import pyqtSignal, QTimer, Qt
from ui.styles.themes import ThemeManager
from loguru import logger


class BarBatchInfo(QFrame):
    """炉次信息栏组件"""
    
    # 信号定义
    start_smelting_clicked = pyqtSignal()  # 开始冶炼信号
    abandon_batch_clicked = pyqtSignal()   # 放弃炉次信号
    terminate_smelting_clicked = pyqtSignal()  # 终止冶炼信号（长按3秒）
    
    # 1. 初始化组件
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_manager = ThemeManager.instance()
        self.setObjectName("batchInfoBar")
        
        self.batch_no = ""
        self.start_time = ""
        self.run_duration = ""
        self.is_smelting = False  # 是否正在冶炼
        
        # 长按计时器
        self.long_press_timer = QTimer()
        self.long_press_timer.timeout.connect(self.on_long_press_complete)
        self.long_press_duration = 3000  # 3秒
        self.press_start_time = 0
        
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
        layout.setContentsMargins(12, 12, 12, 8)  # 顶部 12px，左右 12px，底部 8px
        layout.setSpacing(16)
        
        # 炉次信息文本
        self.info_label = QLabel("未开始冶炼")
        self.info_label.setObjectName("batchInfoLabel")
        layout.addWidget(self.info_label, stretch=1)
        
        # 放弃炉次按钮（暂不实现功能）
        self.btn_abandon = QPushButton("放弃炉次")
        self.btn_abandon.setObjectName("btnAbandon")
        self.btn_abandon.setFixedSize(100, 36)
        self.btn_abandon.clicked.connect(self.abandon_batch_clicked.emit)
        layout.addWidget(self.btn_abandon)
        
        # 开始冶炼按钮
        self.btn_start = QPushButton("开始冶炼")
        self.btn_start.setObjectName("btnStart")
        self.btn_start.setFixedSize(100, 36)
        self.btn_start.clicked.connect(self.start_smelting_clicked.emit)
        layout.addWidget(self.btn_start)
        
        # 终止冶炼按钮（需要长按3秒）
        self.btn_terminate = QPushButton("终止冶炼")
        self.btn_terminate.setObjectName("btnTerminate")
        self.btn_terminate.setFixedSize(100, 36)
        self.btn_terminate.setVisible(False)  # 初始隐藏
        layout.addWidget(self.btn_terminate)
        
        # 为终止按钮安装事件过滤器
        self.btn_terminate.installEventFilter(self)
    
    # 3. 设置冶炼状态
    def set_smelting_state(self, is_smelting: bool, batch_no: str = "", start_time: str = "", run_duration: str = ""):
        """
        设置冶炼状态
        
        Args:
            is_smelting: 是否正在冶炼
            batch_no: 炉次编号
            start_time: 开始时间
            run_duration: 运行时长
        """
        self.is_smelting = is_smelting
        self.batch_no = batch_no
        self.start_time = start_time
        self.run_duration = run_duration
        
        # 根据状态切换按钮显示
        if is_smelting:
            # 冶炼中：显示放弃炉次和终止冶炼按钮
            self.btn_start.setVisible(False)
            self.btn_abandon.setVisible(True)
            self.btn_terminate.setVisible(True)
        else:
            # 未冶炼：显示开始冶炼按钮
            self.btn_start.setVisible(True)
            self.btn_abandon.setVisible(False)
            self.btn_terminate.setVisible(False)
        
        self.update_display()
    
    # 4. 更新显示
    def update_display(self):
        if self.is_smelting and self.batch_no:
            text = f"炉次编号: {self.batch_no}  |  " \
                   f"开始时间: {self.start_time}  |  " \
                   f"运行时长: {self.run_duration}"
        else:
            text = "未开始冶炼"
        self.info_label.setText(text)
    
    # 5. 事件过滤器（处理长按）
    def eventFilter(self, obj, event):
        if obj == self.btn_terminate:
            if event.type() == event.Type.MouseButtonPress:
                # 鼠标按下，开始计时
                self.long_press_timer.start(self.long_press_duration)
                self.btn_terminate.setText("按住3秒...")
                logger.debug("开始长按终止冶炼按钮")
                return True
            elif event.type() == event.Type.MouseButtonRelease:
                # 鼠标释放，取消计时
                if self.long_press_timer.isActive():
                    self.long_press_timer.stop()
                    self.btn_terminate.setText("终止冶炼")
                    logger.debug("取消长按终止冶炼")
                return True
        
        return super().eventFilter(obj, event)
    
    # 6. 长按完成
    def on_long_press_complete(self):
        """长按3秒完成，触发终止冶炼"""
        self.long_press_timer.stop()
        self.btn_terminate.setText("终止冶炼")
        logger.info("长按3秒完成，触发终止冶炼")
        self.terminate_smelting_clicked.emit()
    
    # 7. 应用样式
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
            
            QPushButton#btnStart {{
                background: {colors.GLOW_PRIMARY}33;
                color: {colors.GLOW_PRIMARY};
                border: 1px solid {colors.GLOW_PRIMARY};
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
            }}
            
            QPushButton#btnStart:hover {{
                background: {colors.GLOW_PRIMARY}4D;
                border: 1px solid {colors.GLOW_PRIMARY};
            }}
            
            QPushButton#btnStart:pressed {{
                background: {colors.GLOW_PRIMARY}66;
            }}
            
            QPushButton#btnAbandon, QPushButton#btnTerminate {{
                background: {colors.BG_MEDIUM};
                color: {colors.TEXT_PRIMARY};
                border: 1px solid {colors.BORDER_DARK};
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
            }}
            
            QPushButton#btnAbandon:hover, QPushButton#btnTerminate:hover {{
                border: 1px solid {colors.BORDER_GLOW};
                background: {colors.BG_LIGHT};
            }}
            
            QPushButton#btnAbandon:pressed, QPushButton#btnTerminate:pressed {{
                background: {colors.BG_DARK};
            }}
            
            QPushButton#btnAbandon:disabled {{
                background: {colors.BG_DARK};
                color: {colors.TEXT_DISABLED};
                border: 1px solid {colors.BORDER_DARK};
            }}
        """)
    
    # 8. 主题变化时重新应用样式
    def on_theme_changed(self):
        self.apply_styles()

