"""
主题管理器 - 管理深色/浅色主题切换
"""
from enum import Enum
from typing import Optional
from PyQt6.QtCore import QObject, pyqtSignal
from .colors import (
    DarkColors, LightColors, LightChange, CommonColors,
    OceanBlue, RoseGold, EmeraldNight, SunsetAmber, VioletDream, ArcticFrost,
    IronForge, ControlRoom, NightShift, SteelLine, SlateGrid, PolarFrame
)


# 主题枚举与颜色类、显示名称的映射
THEME_REGISTRY = {
    'dark': {'colors': DarkColors, 'label': '深色', 'accent': '#00d4ff'},
    'light': {'colors': LightColors, 'label': '浅色', 'accent': '#007663'},
    'light_change': {'colors': LightChange, 'label': '强浅', 'accent': '#00014D'},
    'ocean_blue': {'colors': OceanBlue, 'label': '深海蓝', 'accent': '#00b4d8'},
    'rose_gold': {'colors': RoseGold, 'label': '玫瑰金', 'accent': '#b76e79'},
    'emerald_night': {'colors': EmeraldNight, 'label': '翡翠夜', 'accent': '#00d68f'},
    'sunset_amber': {'colors': SunsetAmber, 'label': '日落琥珀', 'accent': '#c06014'},
    'violet_dream': {'colors': VioletDream, 'label': '紫罗兰', 'accent': '#a855f7'},
    'arctic_frost': {'colors': ArcticFrost, 'label': '极地霜', 'accent': '#2563eb'},
    'iron_forge': {'colors': IronForge, 'label': '铁锻', 'accent': '#f0c75e'},
    'control_room': {'colors': ControlRoom, 'label': '中控室', 'accent': '#e85d4a'},
    'night_shift': {'colors': NightShift, 'label': '夜班', 'accent': '#c9956a'},
    'steel_line': {'colors': SteelLine, 'label': '钢线', 'accent': '#455a64'},
    'slate_grid': {'colors': SlateGrid, 'label': '石墨网格', 'accent': '#8899a6'},
    'polar_frame': {'colors': PolarFrame, 'label': '极光框架', 'accent': '#0d9488'},
}


class Theme(Enum):
    """主题枚举"""
    DARK = "dark"
    LIGHT = "light"
    LIGHT_CHANGE = "light_change"
    OCEAN_BLUE = "ocean_blue"
    ROSE_GOLD = "rose_gold"
    EMERALD_NIGHT = "emerald_night"
    SUNSET_AMBER = "sunset_amber"
    VIOLET_DREAM = "violet_dream"
    ARCTIC_FROST = "arctic_frost"
    IRON_FORGE = "iron_forge"
    CONTROL_ROOM = "control_room"
    NIGHT_SHIFT = "night_shift"
    STEEL_LINE = "steel_line"
    SLATE_GRID = "slate_grid"
    POLAR_FRAME = "polar_frame"


class ThemeManager(QObject):
    """主题管理器（单例模式）"""
    
    # 主题变更信号
    theme_changed = pyqtSignal(Theme)
    
    _instance: Optional['ThemeManager'] = None
    _initialized: bool = False
    
    # 1. 单例模式实现
    def __new__(cls):
        if cls._instance is None:
            instance = super().__new__(cls)
            # 必须先调用 QObject.__init__
            QObject.__init__(instance)
            instance._initialized = False
            instance._current_theme = Theme.LIGHT_CHANGE  # 默认使用多色主题
            cls._instance = instance
        return cls._instance
    
    # 2. 初始化主题管理器（单例模式下只执行一次）
    def __init__(self):
        pass
    
    # 3. 获取单例实例
    @classmethod
    def instance(cls) -> 'ThemeManager':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    # 4. 获取当前主题
    def get_current_theme(self) -> Theme:
        return self._current_theme
    
    # 5. 设置主题
    def set_theme(self, theme: Theme):
        if self._current_theme != theme:
            self._current_theme = theme
            self.theme_changed.emit(theme)
    
    # 6. 切换主题（循环切换所有主题）
    def toggle_theme(self):
        all_themes = list(Theme)
        current_index = all_themes.index(self._current_theme) if self._current_theme in all_themes else 0
        next_index = (current_index + 1) % len(all_themes)
        self.set_theme(all_themes[next_index])
    
    # 7. 是否为深色模式
    def is_dark_mode(self) -> bool:
        return self._current_theme in (
            Theme.DARK, Theme.OCEAN_BLUE, Theme.EMERALD_NIGHT, Theme.VIOLET_DREAM,
            Theme.IRON_FORGE, Theme.CONTROL_ROOM, Theme.NIGHT_SHIFT, Theme.SLATE_GRID
        )
    
    # 8. 获取当前主题的颜色类
    def get_colors(self):
        entry = THEME_REGISTRY.get(self._current_theme.value)
        if entry:
            return entry['colors']
        return DarkColors
    
    # 8.1 获取当前主题的显示名称
    def get_theme_label(self) -> str:
        entry = THEME_REGISTRY.get(self._current_theme.value)
        return entry['label'] if entry else ''
    
    # 8.2 获取当前主题的强调色
    def get_theme_accent(self) -> str:
        entry = THEME_REGISTRY.get(self._current_theme.value)
        return entry['accent'] if entry else '#00d4ff'
    
    # 9. 获取指定颜色
    def get_color(self, color_name: str) -> str:
        colors = self.get_colors()
        return getattr(colors, color_name, '#000000')
    
    # ===== 便捷访问方法 =====
    
    # 10. 背景色
    def bg_deep(self) -> str:
        return self.get_color('BG_DEEP')
    
    # 11. 背景色
    def bg_dark(self) -> str:
        return self.get_color('BG_DARK')
    
    # 12. 背景色
    def bg_medium(self) -> str:
        return self.get_color('BG_MEDIUM')
    
    # 13. 背景色
    def bg_light(self) -> str:
        return self.get_color('BG_LIGHT')
    
    # 14. 边框色
    def border_dark(self) -> str:
        return self.get_color('BORDER_DARK')
    
    # 17. 边框色
    def border_medium(self) -> str:
        return self.get_color('BORDER_MEDIUM')
    
    # 18. 边框色
    def border_light(self) -> str:
        return self.get_color('BORDER_LIGHT')
    
    # 17. 边框色
    def border_glow(self) -> str:
        return self.get_color('BORDER_GLOW')
    
    # 18. 发光色
    def glow_primary(self) -> str:
        return self.get_color('GLOW_PRIMARY')
    
    # 24. 发光色
    def glow_secondary(self) -> str:
        return self.get_color('GLOW_SECONDARY')
    
    # 19. 发光色
    def glow_cyan(self) -> str:
        return self.get_color('GLOW_CYAN')
    
    # 20. 发光色
    def glow_green(self) -> str:
        return self.get_color('GLOW_GREEN')
    
    # 28. 发光色
    def glow_orange(self) -> str:
        return self.get_color('GLOW_ORANGE')
    
    # 29. 发光色
    def glow_red(self) -> str:
        return self.get_color('GLOW_RED')
    
    # 30. 发光色
    def glow_blue(self) -> str:
        return self.get_color('GLOW_BLUE')
    
    # 31. 发光色
    def glow_yellow(self) -> str:
        return self.get_color('GLOW_YELLOW')
    
    # 26. 文字色
    def text_primary(self) -> str:
        return self.get_color('TEXT_PRIMARY')
    
    # 27. 文字色
    def text_secondary(self) -> str:
        return self.get_color('TEXT_SECONDARY')
    
    # 28. 文字色
    def text_muted(self) -> str:
        return self.get_color('TEXT_MUTED')
    
    # 37. 文字色
    def text_disabled(self) -> str:
        return self.get_color('TEXT_DISABLED')
    
    # 30. 文字色
    def text_accent(self) -> str:
        return self.get_color('TEXT_ACCENT')
    
    # 41. 文字色
    def text_on_primary(self) -> str:
        return self.get_color('TEXT_ON_PRIMARY')
    
    # 32. 文字色
    def text_selected(self) -> str:
        return self.get_color('TEXT_SELECTED')
    
    # 33. 状态色
    def status_success(self) -> str:
        return self.get_color('STATUS_SUCCESS')
    
    # 46. 状态色
    def status_warning(self) -> str:
        return self.get_color('STATUS_WARNING')
    
    # 47. 状态色
    def status_alarm(self) -> str:
        return self.get_color('STATUS_ALARM')
    
    # 36. 状态色
    def status_error(self) -> str:
        return self.get_color('STATUS_ERROR')
    
    # 37. 按钮色
    def button_primary_bg(self) -> str:
        return self.get_color('BUTTON_PRIMARY_BG')
    
    # 53. 按钮色
    def button_primary_text(self) -> str:
        return self.get_color('BUTTON_PRIMARY_TEXT')
    
    # 54. 按钮色
    def button_primary_hover(self) -> str:
        return self.get_color('BUTTON_PRIMARY_HOVER')
    
    # 55. 输入框色
    def input_bg(self) -> str:
        return self.get_color('INPUT_BG')
    
    # 56. 输入框色
    def input_border(self) -> str:
        return self.get_color('INPUT_BORDER')
    
    # 57. 输入框色
    def input_border_focus(self) -> str:
        return self.get_color('INPUT_BORDER_FOCUS')
    
    # 40. 卡片色
    def card_bg(self) -> str:
        return self.get_color('CARD_BG')
    
    # 41. 图表色
    def chart_line_1(self) -> str:
        return self.get_color('CHART_LINE_1')
    
    # 65. 图表色
    def chart_line_2(self) -> str:
        return self.get_color('CHART_LINE_2')
    
    # 66. 图表色
    def chart_line_3(self) -> str:
        return self.get_color('CHART_LINE_3')
    
    # 67. 图表色
    def chart_line_4(self) -> str:
        return self.get_color('CHART_LINE_4')
    
    # 68. 图表色
    def chart_line_5(self) -> str:
        return self.get_color('CHART_LINE_5')
    
    # 47. 图表色
    def chart_line_6(self) -> str:
        return self.get_color('CHART_LINE_6')
    
    # 48. 阴影与发光
    def overlay_light(self) -> str:
        return self.get_color('OVERLAY_LIGHT')
    
    # 49. 阴影与发光
    def overlay_medium(self) -> str:
        return self.get_color('OVERLAY_MEDIUM')
    
    # 50. 通用色
    @staticmethod
    def transparent() -> str:
        return CommonColors.TRANSPARENT
    
    # 86. 通用色
    @staticmethod
    def black() -> str:
        return CommonColors.BLACK
    
    # 87. 通用色
    @staticmethod
    def white() -> str:
        return CommonColors.WHITE


# 88. 全局单例访问函数
def get_theme_manager() -> ThemeManager:
    return ThemeManager.instance()

