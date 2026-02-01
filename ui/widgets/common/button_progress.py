"""
带进度条的长按按钮组件
"""
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QRectF
from PyQt6.QtGui import QPainter, QColor, QPaintEvent
from ui.styles.themes import ThemeManager


class ProgressButton(QPushButton):
    """带进度条的长按按钮"""
    
    long_press_completed = pyqtSignal()  # 长按完成信号
    
    # 1. 初始化按钮
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.theme_manager = ThemeManager.instance()
        
        self.press_progress = 0.0  # 0.0 - 1.0
        self.is_pressing = False
        self.press_duration = 3000  # 3秒
        
        # 进度更新定时器
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.update_progress)
        self.progress_interval = 50  # 50ms 更新一次
        
        # 长按完成定时器
        self.complete_timer = QTimer()
        self.complete_timer.timeout.connect(self.on_complete)
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    # 2. 鼠标按下事件
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_pressing = True
            self.press_progress = 0.0
            self.progress_timer.start(self.progress_interval)
            self.complete_timer.start(self.press_duration)
            self.update()
        super().mousePressEvent(event)
    
    # 3. 鼠标释放事件
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_pressing = False
            self.press_progress = 0.0
            self.progress_timer.stop()
            self.complete_timer.stop()
            self.update()
        super().mouseReleaseEvent(event)
    
    # 4. 更新进度
    def update_progress(self):
        if self.is_pressing:
            self.press_progress += self.progress_interval / self.press_duration
            if self.press_progress > 1.0:
                self.press_progress = 1.0
            self.update()
    
    # 5. 长按完成
    def on_complete(self):
        self.is_pressing = False
        self.press_progress = 0.0
        self.progress_timer.stop()
        self.complete_timer.stop()
        self.update()
        self.long_press_completed.emit()
    
    # 6. 绘制事件
    def paintEvent(self, event: QPaintEvent):
        # 先绘制按钮本身
        super().paintEvent(event)
        
        # 如果正在按压，绘制进度条
        if self.is_pressing and self.press_progress > 0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            # 获取主题颜色
            colors = self.theme_manager.get_colors()
            
            # 进度条颜色（半透明的主色）
            progress_color = QColor(colors.GLOW_PRIMARY)
            progress_color.setAlpha(80)  # 30% 透明度
            
            # 绘制进度条（从左到右）
            rect = self.rect()
            progress_width = rect.width() * self.press_progress
            progress_rect = QRectF(0, 0, progress_width, rect.height())
            
            painter.fillRect(progress_rect, progress_color)
            
            painter.end()

