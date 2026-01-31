"""
颜色常量定义 - 深色/浅色主题配色方案
"""
class DarkColors:
    """深色主题颜色（科技风格）"""
    
    # ===== 背景层级 =====
    BG_DEEP = '#0d1117'      # 最深背景
    BG_DARK = '#161b22'      # 深色背景
    BG_MEDIUM = '#21262d'    # 中等背景
    BG_LIGHT = '#30363d'     # 浅色背景
    BG_SURFACE = '#1c2128'   # 表面背景
    BG_OVERLAY = '#2d333b'   # 覆盖层背景
    
    # ===== 边框与线条 =====
    BORDER_DARK = '#30363d'   # 深色边框
    BORDER_MEDIUM = '#444c56' # 中等边框
    BORDER_LIGHT = '#6e7681'  # 浅色边框
    BORDER_GLOW = '#00d4ff'   # 发光边框（青色）⭐ 主强调色
    BORDER_ACCENT = '#00f0ff' # 强调边框（浅青色）
    GRID_LINE = '#21262d'     # 网格线
    DIVIDER = '#30363d'       # 分割线
    
    # ===== 发光色（强调色）=====
    GLOW_PRIMARY = '#00d4ff'      # 主要发光（青色）⭐
    GLOW_SECONDARY = '#00f0ff'    # 次要发光（浅青色）
    GLOW_CYAN = '#00d4ff'         # 青色发光
    GLOW_CYAN_LIGHT = '#00f0ff'   # 浅青色发光
    GLOW_GREEN = '#00ff88'        # 绿色发光
    GLOW_ORANGE = '#ff9500'       # 橙色发光
    GLOW_RED = '#ff3b30'          # 红色发光
    GLOW_BLUE = '#0088ff'         # 蓝色发光
    GLOW_YELLOW = '#ffcc00'       # 黄色发光
    GLOW_PURPLE = '#bf5af2'       # 紫色发光
    
    # ===== 文字颜色 =====
    TEXT_PRIMARY = '#e6edf3'    # 主要文字
    TEXT_SECONDARY = '#8b949e'  # 次要文字
    TEXT_TERTIARY = '#6e7681'   # 三级文字
    TEXT_MUTED = '#484f58'      # 弱化文字
    TEXT_DISABLED = '#3d444d'   # 禁用文字
    TEXT_INVERSE = '#0d1117'    # 反色文字（用于深色背景上的浅色文字）
    TEXT_LINK = '#00d4ff'       # 链接文字
    TEXT_ACCENT = '#00f0ff'     # 强调文字
    
    # ===== 状态色 =====
    STATUS_NORMAL = '#00ff88'    # 正常状态（绿色）
    STATUS_SUCCESS = '#00ff88'   # 成功状态
    STATUS_WARNING = '#ffcc00'   # 警告状态（黄色）
    STATUS_ALARM = '#ff0000'     # 报警状态（鲜红色）⭐
    STATUS_ERROR = '#ff0000'     # 错误状态（鲜红色）⭐
    STATUS_INFO = '#0088ff'      # 信息状态（蓝色）
    STATUS_OFFLINE = '#484f58'   # 离线状态（灰色）
    STATUS_DISABLED = '#3d444d'  # 禁用状态
    
    # ===== 按钮颜色 =====
    BUTTON_PRIMARY_BG = '#00d4ff'       # 主要按钮背景
    BUTTON_PRIMARY_TEXT = '#0d1117'     # 主要按钮文字
    BUTTON_PRIMARY_HOVER = '#00f0ff'    # 主要按钮悬停
    BUTTON_SECONDARY_BG = '#21262d'     # 次要按钮背景
    BUTTON_SECONDARY_TEXT = '#e6edf3'   # 次要按钮文字
    BUTTON_SECONDARY_HOVER = '#30363d'  # 次要按钮悬停
    BUTTON_DANGER_BG = '#ff3b30'        # 危险按钮背景
    BUTTON_DANGER_TEXT = '#ffffff'      # 危险按钮文字
    BUTTON_DANGER_HOVER = '#ff5544'     # 危险按钮悬停
    BUTTON_DISABLED_BG = '#161b22'      # 禁用按钮背景
    BUTTON_DISABLED_TEXT = '#484f58'    # 禁用按钮文字
    
    # ===== 输入框颜色 =====
    INPUT_BG = '#30363d'           # 输入框背景
    INPUT_BORDER = '#444c56'       # 输入框边框
    INPUT_BORDER_FOCUS = '#00d4ff' # 输入框聚焦边框
    INPUT_TEXT = '#e6edf3'         # 输入框文字
    INPUT_PLACEHOLDER = '#6e7681'  # 输入框占位符
    INPUT_DISABLED_BG = '#161b22'  # 禁用输入框背景
    INPUT_DISABLED_TEXT = '#484f58'# 禁用输入框文字
    
    # ===== 卡片颜色 =====
    CARD_BG = '#21262d'            # 卡片背景
    CARD_BORDER = '#30363d'        # 卡片边框
    CARD_HOVER_BG = '#2d333b'      # 卡片悬停背景
    CARD_HOVER_BORDER = '#00d4ff'  # 卡片悬停边框
    CARD_HEADER_BG = '#161b22'     # 卡片头部背景
    CARD_HEADER_TEXT = '#00d4ff'   # 卡片头部文字
    
    # ===== 表格颜色 =====
    TABLE_BG = '#21262d'           # 表格背景
    TABLE_HEADER_BG = '#161b22'    # 表头背景
    TABLE_HEADER_TEXT = '#00d4ff'  # 表头文字
    TABLE_ROW_EVEN = '#21262d'     # 偶数行背景
    TABLE_ROW_ODD = '#1c2128'      # 奇数行背景
    TABLE_ROW_HOVER = '#2d333b'    # 行悬停背景
    TABLE_ROW_SELECTED = '#30363d' # 行选中背景
    TABLE_BORDER = '#30363d'       # 表格边框
    
    # ===== 图表颜色 =====
    CHART_LINE_1 = '#00d4ff'    # 图表线条1（青色）
    CHART_LINE_2 = '#00ff88'    # 图表线条2（绿色）
    CHART_LINE_3 = '#ff9500'    # 图表线条3（橙色）
    CHART_LINE_4 = '#0088ff'    # 图表线条4（蓝色）
    CHART_LINE_5 = '#bf5af2'    # 图表线条5（紫色）
    CHART_LINE_6 = '#ffcc00'    # 图表线条6（黄色）
    CHART_GRID = '#21262d'      # 图表网格
    CHART_AXIS = '#8b949e'      # 图表坐标轴
    CHART_BG = '#161b22'        # 图表背景
    CHART_TOOLTIP_BG = '#2d333b'# 图表提示框背景
    CHART_TOOLTIP_BORDER = '#00d4ff' # 图表提示框边框
    
    # ===== 下拉框颜色 =====
    DROPDOWN_BG = '#30363d'        # 下拉框背景
    DROPDOWN_BORDER = '#444c56'    # 下拉框边框
    DROPDOWN_HOVER = '#00d4ff'     # 下拉框悬停边框
    DROPDOWN_ITEM_BG = '#21262d'   # 下拉项背景
    DROPDOWN_ITEM_HOVER = '#2d333b'# 下拉项悬停
    DROPDOWN_ITEM_SELECTED = '#30363d' # 下拉项选中
    
    # ===== 开关/复选框颜色 =====
    SWITCH_TRACK_OFF = '#30363d'   # 开关轨道（关闭）
    SWITCH_TRACK_ON = '#00ff88'    # 开关轨道（打开）
    SWITCH_THUMB_OFF = '#6e7681'   # 开关滑块（关闭）
    SWITCH_THUMB_ON = '#ffffff'    # 开关滑块（打开）
    CHECKBOX_BG = '#30363d'        # 复选框背景
    CHECKBOX_BORDER = '#444c56'    # 复选框边框
    CHECKBOX_CHECKED_BG = '#00d4ff'# 复选框选中背景
    CHECKBOX_CHECKED_BORDER = '#00d4ff' # 复选框选中边框
    
    # ===== 滑块/进度条颜色 =====
    SLIDER_TRACK = '#30363d'       # 滑块轨道
    SLIDER_TRACK_ACTIVE = '#00d4ff'# 滑块激活轨道
    SLIDER_THUMB = '#00d4ff'       # 滑块滑块
    PROGRESS_BG = '#30363d'        # 进度条背景
    PROGRESS_FILL = '#00d4ff'      # 进度条填充
    
    # ===== 标签页颜色 =====
    TAB_BG = '#161b22'             # 标签页背景
    TAB_BORDER = '#30363d'         # 标签页边框
    TAB_ACTIVE_BG = '#21262d'      # 激活标签页背景
    TAB_ACTIVE_BORDER = '#00d4ff'  # 激活标签页边框
    TAB_ACTIVE_TEXT = '#00d4ff'    # 激活标签页文字
    TAB_INACTIVE_TEXT = '#8b949e'  # 非激活标签页文字
    TAB_HOVER_BG = '#1c2128'       # 标签页悬停背景
    
    # ===== 阴影与发光效果 =====
    SHADOW_LIGHT = 'rgba(0, 212, 255, 0.3)'   # 浅色阴影
    SHADOW_MEDIUM = 'rgba(0, 212, 255, 0.5)'  # 中等阴影
    SHADOW_HEAVY = 'rgba(0, 212, 255, 0.7)'   # 重度阴影
    GLOW_EFFECT = 'rgba(0, 212, 255, 0.6)'    # 发光效果
    OVERLAY_LIGHT = 'rgba(0, 0, 0, 0.3)'      # 浅色覆盖层
    OVERLAY_MEDIUM = 'rgba(0, 0, 0, 0.5)'     # 中等覆盖层
    OVERLAY_HEAVY = 'rgba(0, 0, 0, 0.7)'      # 重度覆盖层

class LightColors:
    """浅色主题颜色（绿色系，基于 #E9EEA8）"""
    
    # ===== 背景层级 =====
    BG_DEEP = '#e9eea8'      # 最深背景（主色调）⭐
    BG_DARK = '#f2fedc'      # 深色背景（浅绿）
    BG_MEDIUM = '#fafbe7'    # 中等背景（米白）
    BG_LIGHT = '#ffffff'     # 浅色背景（纯白）
    BG_SURFACE = '#f6ede0'   # 表面背景（米色）
    BG_OVERLAY = '#fafaf0'   # 覆盖层背景（浅米色）
    
    # ===== 边框与线条 =====
    BORDER_DARK = '#d5a339'   # 深色边框（金棕色）
    BORDER_MEDIUM = '#8e7344' # 中等边框（棕色）
    BORDER_LIGHT = '#acac9a'  # 浅色边框（灰绿）
    BORDER_GLOW = '#007663'   # 发光边框（深绿色）⭐ 主强调色
    BORDER_ACCENT = '#008b67' # 强调边框（中绿色）
    GRID_LINE = '#e0e8d8'     # 网格线（浅灰绿）
    DIVIDER = '#d5a339'       # 分割线（金棕）
    
    # ===== 发光色（强调色）=====
    GLOW_PRIMARY = '#007663'      # 主要发光（深绿）⭐
    GLOW_SECONDARY = '#008b67'    # 次要发光（中绿）
    GLOW_CYAN = '#007663'         # 青色发光（深绿）
    GLOW_CYAN_LIGHT = '#008b67'   # 浅青色发光（中绿）
    GLOW_GREEN = '#008b67'        # 绿色发光
    GLOW_ORANGE = '#d5a339'       # 橙色发光（金棕）
    GLOW_RED = '#b95d3b'          # 红色发光（棕红）
    GLOW_BLUE = '#00ced4'         # 蓝色发光（青蓝）
    GLOW_YELLOW = '#859a00'       # 黄色发光（橄榄绿）
    GLOW_PURPLE = '#95b0b1'       # 紫色发光（灰蓝）
    
    # ===== 文字颜色 =====
    TEXT_PRIMARY = '#1b3d2f'    # 主要文字（深绿）
    TEXT_SECONDARY = '#474838'  # 次要文字（深灰绿）
    TEXT_TERTIARY = '#5f5f4f'   # 三级文字（灰绿）
    TEXT_MUTED = '#8b949e'      # 弱化文字（灰色）
    TEXT_DISABLED = '#acac9a'   # 禁用文字（浅灰）
    TEXT_INVERSE = '#ffffff'    # 反色文字（用于深色背景上的浅色文字）
    TEXT_LINK = '#007663'       # 链接文字（深绿）
    TEXT_ACCENT = '#008b67'     # 强调文字（中绿）
    
    # ===== 状态色 =====
    STATUS_NORMAL = '#008b67'    # 正常状态（绿色）
    STATUS_SUCCESS = '#008b67'   # 成功状态
    STATUS_WARNING = '#d5a339'   # 警告状态（金棕）
    STATUS_ALARM = '#ff0000'     # 报警状态（鲜红色）⭐
    STATUS_ERROR = '#ff0000'     # 错误状态（鲜红色）⭐
    STATUS_INFO = '#00ced4'      # 信息状态（青蓝）
    STATUS_OFFLINE = '#8b949e'   # 离线状态（灰色）
    STATUS_DISABLED = '#acac9a'  # 禁用状态
    
    # ===== 按钮颜色 =====
    BUTTON_PRIMARY_BG = '#007663'       # 主要按钮背景（深绿）
    BUTTON_PRIMARY_TEXT = '#ffffff'     # 主要按钮文字
    BUTTON_PRIMARY_HOVER = '#008b67'    # 主要按钮悬停（中绿）
    BUTTON_SECONDARY_BG = '#fafbe7'     # 次要按钮背景
    BUTTON_SECONDARY_TEXT = '#1b3d2f'   # 次要按钮文字
    BUTTON_SECONDARY_HOVER = '#f2fedc'  # 次要按钮悬停
    BUTTON_DANGER_BG = '#b95d3b'        # 危险按钮背景（棕红）
    BUTTON_DANGER_TEXT = '#ffffff'      # 危险按钮文字
    BUTTON_DANGER_HOVER = '#c76d4b'     # 危险按钮悬停
    BUTTON_DISABLED_BG = '#fafaf0'      # 禁用按钮背景
    BUTTON_DISABLED_TEXT = '#acac9a'    # 禁用按钮文字
    
    # ===== 输入框颜色 =====
    INPUT_BG = '#ffffff'           # 输入框背景
    INPUT_BORDER = '#acac9a'       # 输入框边框
    INPUT_BORDER_FOCUS = '#007663' # 输入框聚焦边框（深绿）
    INPUT_TEXT = '#1b3d2f'         # 输入框文字
    INPUT_PLACEHOLDER = '#8b949e'  # 输入框占位符
    INPUT_DISABLED_BG = '#fafaf0'  # 禁用输入框背景
    INPUT_DISABLED_TEXT = '#acac9a'# 禁用输入框文字
    
    # ===== 卡片颜色 =====
    CARD_BG = '#ffffff'            # 卡片背景
    CARD_BORDER = '#d5a339'        # 卡片边框（金棕）
    CARD_HOVER_BG = '#fafbe7'      # 卡片悬停背景
    CARD_HOVER_BORDER = '#007663'  # 卡片悬停边框（深绿）
    CARD_HEADER_BG = '#f2fedc'     # 卡片头部背景
    CARD_HEADER_TEXT = '#007663'   # 卡片头部文字（深绿）
    
    # ===== 表格颜色 =====
    TABLE_BG = '#ffffff'           # 表格背景
    TABLE_HEADER_BG = '#f2fedc'    # 表头背景
    TABLE_HEADER_TEXT = '#007663'  # 表头文字（深绿）
    TABLE_ROW_EVEN = '#ffffff'     # 偶数行背景
    TABLE_ROW_ODD = '#fafbe7'      # 奇数行背景
    TABLE_ROW_HOVER = '#f2fedc'    # 行悬停背景
    TABLE_ROW_SELECTED = '#e9eea8' # 行选中背景
    TABLE_BORDER = '#d5a339'       # 表格边框（金棕）
    
    # ===== 图表颜色 =====
    CHART_LINE_1 = '#007663'    # 图表线条1（深绿）
    CHART_LINE_2 = '#008b67'    # 图表线条2（中绿）
    CHART_LINE_3 = '#d5a339'    # 图表线条3（金棕）
    CHART_LINE_4 = '#00ced4'    # 图表线条4（青蓝）
    CHART_LINE_5 = '#95b0b1'    # 图表线条5（灰蓝）
    CHART_LINE_6 = '#859a00'    # 图表线条6（橄榄绿）
    CHART_GRID = '#e0e8d8'      # 图表网格
    CHART_AXIS = '#474838'      # 图表坐标轴
    CHART_BG = '#fafbe7'        # 图表背景
    CHART_TOOLTIP_BG = '#ffffff'# 图表提示框背景
    CHART_TOOLTIP_BORDER = '#007663' # 图表提示框边框
    
    # ===== 下拉框颜色 =====
    DROPDOWN_BG = '#ffffff'        # 下拉框背景
    DROPDOWN_BORDER = '#acac9a'    # 下拉框边框
    DROPDOWN_HOVER = '#007663'     # 下拉框悬停边框
    DROPDOWN_ITEM_BG = '#ffffff'   # 下拉项背景
    DROPDOWN_ITEM_HOVER = '#f2fedc'# 下拉项悬停
    DROPDOWN_ITEM_SELECTED = '#e9eea8' # 下拉项选中
    
    # ===== 开关/复选框颜色 =====
    SWITCH_TRACK_OFF = '#acac9a'   # 开关轨道（关闭）
    SWITCH_TRACK_ON = '#008b67'    # 开关轨道（打开）
    SWITCH_THUMB_OFF = '#8b949e'   # 开关滑块（关闭）
    SWITCH_THUMB_ON = '#ffffff'    # 开关滑块（打开）
    CHECKBOX_BG = '#ffffff'        # 复选框背景
    CHECKBOX_BORDER = '#acac9a'    # 复选框边框
    CHECKBOX_CHECKED_BG = '#007663'# 复选框选中背景
    CHECKBOX_CHECKED_BORDER = '#007663' # 复选框选中边框
    
    # ===== 滑块/进度条颜色 =====
    SLIDER_TRACK = '#e0e8d8'       # 滑块轨道
    SLIDER_TRACK_ACTIVE = '#007663'# 滑块激活轨道
    SLIDER_THUMB = '#007663'       # 滑块滑块
    PROGRESS_BG = '#e0e8d8'        # 进度条背景
    PROGRESS_FILL = '#007663'      # 进度条填充
    
    # ===== 标签页颜色 =====
    TAB_BG = '#f2fedc'             # 标签页背景
    TAB_BORDER = '#d5a339'         # 标签页边框
    TAB_ACTIVE_BG = '#ffffff'      # 激活标签页背景
    TAB_ACTIVE_BORDER = '#007663'  # 激活标签页边框
    TAB_ACTIVE_TEXT = '#007663'    # 激活标签页文字
    TAB_INACTIVE_TEXT = '#474838'  # 非激活标签页文字
    TAB_HOVER_BG = '#fafbe7'       # 标签页悬停背景
    
    # ===== 阴影与发光效果 =====
    SHADOW_LIGHT = 'rgba(0, 118, 99, 0.2)'    # 浅色阴影
    SHADOW_MEDIUM = 'rgba(0, 118, 99, 0.3)'   # 中等阴影
    SHADOW_HEAVY = 'rgba(0, 118, 99, 0.5)'    # 重度阴影
    GLOW_EFFECT = 'rgba(0, 118, 99, 0.4)'     # 发光效果
    OVERLAY_LIGHT = 'rgba(255, 255, 255, 0.3)'# 浅色覆盖层
    OVERLAY_MEDIUM = 'rgba(255, 255, 255, 0.5)'# 中等覆盖层
    OVERLAY_HEAVY = 'rgba(255, 255, 255, 0.7)'# 重度覆盖层

# ===== 通用颜色（不随主题变化）=====
class CommonColors:
    """通用颜色常量"""
    
    # 透明度
    TRANSPARENT = 'transparent'
    
    # 纯色
    BLACK = '#000000'
    WHITE = '#ffffff'
    
    # 半透明遮罩
    OVERLAY_LIGHT = 'rgba(0, 0, 0, 0.3)'
    OVERLAY_MEDIUM = 'rgba(0, 0, 0, 0.5)'
    OVERLAY_HEAVY = 'rgba(0, 0, 0, 0.7)'
