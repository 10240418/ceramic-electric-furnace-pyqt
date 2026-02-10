"""
带进度条的长按按钮组件 - 支持鼠标和触摸屏长按
"""
from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QRectF, QEvent
from PyQt6.QtGui import QPainter, QColor, QPaintEvent
from ui.styles.themes import ThemeManager


class ProgressButton(QPushButton):
    """带进度条的长按按钮，同时支持鼠标左键和触摸屏长按"""
    
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
        
        # 启用触摸事件接收
        self.setAttribute(Qt.WidgetAttribute.WA_AcceptTouchEvents, True)
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    # 2. 开始长按（鼠标和触摸共用）
    def start_press(self):
        self.is_pressing = True
        self.press_progress = 0.0
        self.progress_timer.start(self.progress_interval)
        self.complete_timer.start(self.press_duration)
        self.update()
    
    # 3. 取消长按（鼠标和触摸共用）
    def cancel_press(self):
        self.is_pressing = False
        self.press_progress = 0.0
        self.progress_timer.stop()
        self.complete_timer.stop()
        self.update()
    
    # 4. 统一事件处理（触摸事件在此拦截）
    def event(self, e: QEvent) -> bool:
        t = e.type()
        if t == QEvent.Type.TouchBegin:
            e.accept()
            self.start_press()
            return True
        if t in (QEvent.Type.TouchEnd, QEvent.Type.TouchCancel):
            e.accept()
            self.cancel_press()
            return True
        if t == QEvent.Type.TouchUpdate:
            # 检查手指是否移出按钮区域
            e.accept()
            points = e.points()
            if points:
                pos = points[0].position()
                if not self.rect().contains(pos.toPoint()):
                    self.cancel_press()
            return True
        return super().event(e)
    
    # 5. 鼠标按下事件
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_press()
        super().mousePressEvent(event)
    
    # 6. 鼠标释放事件
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.cancel_press()
        super().mouseReleaseEvent(event)
    
    # 7. 更新进度
    def update_progress(self):
        if self.is_pressing:
            self.press_progress += self.progress_interval / self.press_duration
            if self.press_progress > 1.0:
                self.press_progress = 1.0
            self.update()
    
    # 8. 长按完成
    def on_complete(self):
        self.is_pressing = False
        self.press_progress = 0.0
        self.progress_timer.stop()
        self.complete_timer.stop()
        self.update()
        self.long_press_completed.emit()
    
    # 9. 绘制事件
    def paintEvent(self, event: QPaintEvent):
        super().paintEvent(event)
        
        if self.is_pressing and self.press_progress > 0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            colors = self.theme_manager.get_colors()
            
            progress_color = QColor(colors.GLOW_PRIMARY)
            progress_color.setAlpha(80)
            
            rect = self.rect()
            progress_width = rect.width() * self.press_progress
            progress_rect = QRectF(0, 0, progress_width, rect.height())
            
            painter.fillRect(progress_rect, progress_color)
            
            painter.end()

