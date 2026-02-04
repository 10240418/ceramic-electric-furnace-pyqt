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
    
    # ===== 按钮透明背景 =====
    BTN_BG_NORMAL = '#30363d4D'  # 按钮正常背景（30%透明）
    BTN_BG_HOVER = '#30363d80'   # 按钮悬停背景（50%透明）
    
    # ===== 边框与线条 =====
    BORDER_DARK = '#30363d'   # 深色边框
    BORDER_MEDIUM = '#444c56' # 中等边框
    BORDER_LIGHT = '#6e7681'  # 浅色边框
    BORDER_GLOW = '#00d4ff'   # 发光边框（青色）
    BORDER_ACCENT = '#00f0ff' # 强调边框（浅青色）
    GRID_LINE = '#21262d'     # 网格线
    DIVIDER = '#30363d'       # 分割线
    
    # ===== 发光色（强调色）=====
    GLOW_PRIMARY = '#00d4ff'      # 主要发光（青色）
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
    TEXT_INVERSE = '#0d1117'    # 反色文字
    TEXT_LINK = '#00d4ff'       # 链接文字
    TEXT_ACCENT = '#00f0ff'     # 强调文字
    TEXT_ON_PRIMARY = '#0d1117' # 主色背景上的文字
    TEXT_SELECTED = '#00d4ff'   # 选中状态文字
    TEXT_FOCUS = '#00f0ff'      # 焦点状态文字
    
    # ===== 状态色 =====
    STATUS_NORMAL = '#00ff88'    # 正常状态（绿色）
    STATUS_SUCCESS = '#00ff88'   # 成功状态
    STATUS_WARNING = '#ffcc00'   # 警告状态（黄色）
    STATUS_ALARM = '#ff0000'     # 报警状态（鲜红色）
    STATUS_ERROR = '#ff0000'     # 错误状态（鲜红色）
    STATUS_INFO = '#0088ff'      # 信息状态（蓝色）
    STATUS_OFFLINE = '#484f58'   # 离线状态（灰色）
    STATUS_DISABLED = '#3d444d'  # 禁用状态
    
    # ===== 按钮颜色 =====
    BUTTON_PRIMARY_BG = '#00d4ff'       # 主要按钮背景
    BUTTON_PRIMARY_TEXT = '#0d1117'     # 主要按钮文字
    BUTTON_PRIMARY_HOVER = '#00f0ff'    # 主要按钮悬停
    BUTTON_DANGER_HOVER = '#ff5544'     # 危险按钮悬停
    
    # ===== 输入框颜色 =====
    INPUT_BG = '#30363d'           # 输入框背景
    INPUT_BORDER = '#444c56'       # 输入框边框
    INPUT_BORDER_FOCUS = '#00d4ff' # 输入框聚焦边框
    
    # ===== 卡片颜色 =====
    CARD_BG = '#21262d'            # 卡片背景
    CARD_BORDER = '#30363d'        # 卡片边框
    CARD_HOVER_BORDER = '#00d4ff'  # 卡片悬停边框
    
    # ===== 表格颜色 =====
    TABLE_BG = '#21262d'           # 表格背景
    TABLE_HEADER_BG = '#161b22'    # 表头背景
    TABLE_HEADER_TEXT = '#00d4ff'  # 表头文字
    
    # ===== 图表颜色 =====
    CHART_LINE_1 = '#00d4ff'    # 图表线条1（亮青色）
    CHART_LINE_2 = '#ff3b8e'    # 图表线条2（粉红色）
    CHART_LINE_3 = '#ffcc00'    # 图表线条3（亮黄色）
    CHART_LINE_4 = '#0088ff'    # 图表线条4（蓝色）
    CHART_LINE_5 = '#bf5af2'    # 图表线条5（紫色）
    CHART_LINE_6 = '#00ff88'    # 图表线条6（绿色）
    CHART_GRID = '#21262d'      # 图表网格
    CHART_AXIS = '#8b949e'      # 图表坐标轴
    CHART_BG = '#161b22'        # 图表背景
    
    # ===== 电极图表专用颜色 =====
    ELECTRODE_SET_VALUE = '#00d4ff'    # 设定值弧流（青色）
    ELECTRODE_ACTUAL_VALUE = '#ffb84d' # 实际值弧流（橙黄色）
    ELECTRODE_VOLTAGE = '#00ff88'      # 弧压（绿色）
    
    # ===== 下拉框颜色 =====
    DROPDOWN_BG = '#30363d'        # 下拉框背景
    DROPDOWN_BORDER = '#444c56'    # 下拉框边框
    
    # ===== 标签页颜色 =====
    TAB_BG = '#161b22'             # 标签页背景
    TAB_ACTIVE_BG = '#21262d'      # 激活标签页背景
    TAB_ACTIVE_BORDER = '#00d4ff'  # 激活标签页边框
    
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
    BG_DEEP = '#e9eea8'      # 最深背景（主色调）
    BG_DARK = '#f2fedc'      # 深色背景（浅绿）
    BG_MEDIUM = '#fafbe7'    # 中等背景（米白）
    BG_LIGHT = '#ffffff'     # 浅色背景（纯白）
    BG_SURFACE = '#f6ede0'   # 表面背景（米色）
    BG_OVERLAY = '#fafaf0'   # 覆盖层背景（浅米色）
    
    # ===== 按钮透明背景 =====
    BTN_BG_NORMAL = '#ffffff'    # 按钮正常背景（白色）
    BTN_BG_HOVER = '#fafbe7'     # 按钮悬停背景（米白）
    
    # ===== 边框与线条 =====
    BORDER_DARK = '#d5a339'   # 深色边框（金棕色）
    BORDER_MEDIUM = '#8e7344' # 中等边框（棕色）
    BORDER_LIGHT = '#acac9a'  # 浅色边框（灰绿）
    BORDER_GLOW = '#007663'   # 发光边框（深绿色）
    BORDER_ACCENT = '#008b67' # 强调边框（中绿色）
    GRID_LINE = '#e0e8d8'     # 网格线（浅灰绿）
    DIVIDER = '#d5a339'       # 分割线（金棕）
    
    # ===== 发光色（强调色）=====
    GLOW_PRIMARY = '#007663'      # 主要发光（深绿）
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
    TEXT_INVERSE = '#ffffff'    # 反色文字
    TEXT_LINK = '#007663'       # 链接文字（深绿）
    TEXT_ACCENT = '#008b67'     # 强调文字（中绿）
    TEXT_ON_PRIMARY = '#ffffff' # 主色背景上的文字
    TEXT_SELECTED = '#007663'   # 选中状态文字（深绿）
    TEXT_FOCUS = '#008b67'      # 焦点状态文字（中绿）
    
    # ===== 状态色 =====
    STATUS_NORMAL = '#008b67'    # 正常状态（绿色）
    STATUS_SUCCESS = '#008b67'   # 成功状态
    STATUS_WARNING = '#d5a339'   # 警告状态（金棕）
    STATUS_ALARM = '#ff0000'     # 报警状态（鲜红色）
    STATUS_ERROR = '#ff0000'     # 错误状态（鲜红色）
    STATUS_INFO = '#00ced4'      # 信息状态（青蓝）
    STATUS_OFFLINE = '#8b949e'   # 离线状态（灰色）
    STATUS_DISABLED = '#acac9a'  # 禁用状态
    
    # ===== 按钮颜色 =====
    BUTTON_PRIMARY_BG = '#007663'       # 主要按钮背景（深绿）
    BUTTON_PRIMARY_TEXT = '#ffffff'     # 主要按钮文字
    BUTTON_PRIMARY_HOVER = '#008b67'    # 主要按钮悬停（中绿）
    BUTTON_DANGER_HOVER = '#c76d4b'     # 危险按钮悬停
    
    # ===== 输入框颜色 =====
    INPUT_BG = '#ffffff'           # 输入框背景
    INPUT_BORDER = '#acac9a'       # 输入框边框
    INPUT_BORDER_FOCUS = '#007663' # 输入框聚焦边框（深绿）
    
    # ===== 卡片颜色 =====
    CARD_BG = '#ffffff'            # 卡片背景
    CARD_BORDER = '#d5a339'        # 卡片边框（金棕）
    CARD_HOVER_BORDER = '#007663'  # 卡片悬停边框（深绿）
    
    # ===== 表格颜色 =====
    TABLE_BG = '#ffffff'           # 表格背景
    TABLE_HEADER_BG = '#f2fedc'    # 表头背景
    TABLE_HEADER_TEXT = '#007663'  # 表头文字（深绿）
    
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
    
    # ===== 电极图表专用颜色 =====
    ELECTRODE_SET_VALUE = '#007663'    # 设定值弧流（深绿）
    ELECTRODE_ACTUAL_VALUE = '#d4a017' # 实际值弧流（金黄色）
    ELECTRODE_VOLTAGE = '#00aa55'      # 弧压（深绿）
    
    # ===== 下拉框颜色 =====
    DROPDOWN_BG = '#ffffff'        # 下拉框背景
    DROPDOWN_BORDER = '#acac9a'    # 下拉框边框
    
    # ===== 标签页颜色 =====
    TAB_BG = '#f2fedc'             # 标签页背景
    TAB_ACTIVE_BG = '#ffffff'      # 激活标签页背景
    TAB_ACTIVE_BORDER = '#007663'  # 激活标签页边框
    
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
    TRANSPARENT = 'transparent'
    BLACK = '#000000'
    WHITE = '#ffffff'
