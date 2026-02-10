# 投料详情弹窗 - 禁用 Mock 数据指南

## 文件位置

`ui/widgets/realtime_data/hopper/dialog_hopper_detail.py`

## 当前状态（开发环境）

当前代码包含 Mock 数据逻辑，用于开发和测试。在以下情况会显示 Mock 数据：

1. 没有批次号（`batch_code` 为空）
2. 数据库查询失败（连接错误、认证失败等）
3. 查询结果为空（该批次没有数据）

## 生产环境禁用 Mock 数据

搜索代码中的 `TODO: 生产环境禁用 Mock` 标志，共有 **5 处**需要修改：

---

### 修改 1：showEvent() 方法

**位置**：第 ~280 行

**当前代码**：
```python
# 加载历史投料数据（如果失败则加载 Mock 数据）
# TODO: 生产环境禁用 Mock - 删除下面的 except 分支，让异常直接抛出
try:
    self.load_feeding_history()
except Exception as e:
    logger.warning(f"加载历史数据失败，使用 Mock 数据: {e}")
    self.load_mock_data()  # TODO: 生产环境禁用 Mock - 删除这行
```

**修改为**：
```python
# 加载历史投料数据
self.load_feeding_history()
```

---

### 修改 2：load_feeding_history() - 没有批次号时

**位置**：第 ~290 行

**当前代码**：
```python
# TODO: 生产环境禁用 Mock - 将下面 3 行改为: if not batch_code: return
if not batch_code:
    logger.warning("未获取到当前批次号，加载 Mock 数据")
    self.load_mock_data()  # TODO: 生产环境禁用 Mock - 删除这行
    return
```

**修改为**：
```python
if not batch_code:
    logger.warning("未获取到当前批次号")
    return
```

---

### 修改 3：load_feeding_history() - 没有查询到数据时

**位置**：第 ~350 行

**当前代码**：
```python
# TODO: 生产环境禁用 Mock - 删除下面 3 行，没有数据时显示空白
# 如果没有任何数据，加载 Mock 数据
if not feeding_records_data and not feeding_total_data:
    logger.warning("没有查询到任何投料数据，加载 Mock 数据")
    self.load_mock_data()  # TODO: 生产环境禁用 Mock - 删除这行
```

**修改为**：
```python
# 如果没有任何数据，显示空白
if not feeding_records_data and not feeding_total_data:
    logger.warning("没有查询到任何投料数据")
```

---

### 修改 4：删除 load_mock_data() 方法

**位置**：第 ~360 行

**当前代码**：
```python
# 12. 加载 Mock 数据
# TODO: 生产环境禁用 Mock - 删除整个 load_mock_data() 方法
def load_mock_data(self):
    """加载 Mock 数据用于 UI 测试"""
    logger.info("加载 Mock 投料数据...")
    
    # ... 50 行 Mock 数据生成代码 ...
```

**修改为**：
```python
# 删除整个方法（约 50 行代码）
```

---

## 修改后的效果

### 开发环境（当前）

- ✅ 有批次号 + 有数据 → 显示真实数据
- ✅ 有批次号 + 无数据 → 显示 Mock 数据
- ✅ 无批次号 → 显示 Mock 数据
- ✅ 数据库连接失败 → 显示 Mock 数据

### 生产环境（修改后）

- ✅ 有批次号 + 有数据 → 显示真实数据
- ✅ 有批次号 + 无数据 → 显示空白（不显示 Mock）
- ✅ 无批次号 → 显示空白（不显示 Mock）
- ❌ 数据库连接失败 → 抛出异常（需要修复数据库连接）

---

## 快速修改脚本

如果您想一键禁用 Mock，可以使用以下 Python 脚本：

```python
import re

file_path = r"c:\Users\20216\Documents\GitHub\Clutch\ceramic-electric-furnace-pyqt\ui\widgets\realtime_data\hopper\dialog_hopper_detail.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 修改 showEvent()
content = re.sub(
    r'# 加载历史投料数据（如果失败则加载 Mock 数据）\s*# TODO:.*?\s*try:\s*self\.load_feeding_history\(\)\s*except Exception as e:\s*logger\.warning\(.*?\)\s*self\.load_mock_data\(\)\s*# TODO:.*?$',
    '# 加载历史投料数据\n        self.load_feeding_history()',
    content,
    flags=re.MULTILINE | re.DOTALL
)

# 2. 修改没有批次号时的处理
content = re.sub(
    r'# TODO:.*?\s*if not batch_code:\s*logger\.warning\("未获取到当前批次号，加载 Mock 数据"\)\s*self\.load_mock_data\(\)\s*# TODO:.*?\s*return',
    'if not batch_code:\n                logger.warning("未获取到当前批次号")\n                return',
    content,
    flags=re.MULTILINE | re.DOTALL
)

# 3. 修改没有数据时的处理
content = re.sub(
    r'# TODO:.*?\s*# 如果没有任何数据，加载 Mock 数据\s*if not feeding_records_data and not feeding_total_data:\s*logger\.warning\("没有查询到任何投料数据，加载 Mock 数据"\)\s*self\.load_mock_data\(\)\s*# TODO:.*?$',
    '# 如果没有任何数据，显示空白\n            if not feeding_records_data and not feeding_total_data:\n                logger.warning("没有查询到任何投料数据")',
    content,
    flags=re.MULTILINE | re.DOTALL
)

# 4. 删除 load_mock_data() 方法
content = re.sub(
    r'    # 12\. 加载 Mock 数据.*?(?=    # 13\.)',
    '',
    content,
    flags=re.DOTALL
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Mock 数据已禁用！")
```

---

## 注意事项

1. **确保数据库连接正常**：禁用 Mock 后，数据库连接失败会导致弹窗无法显示数据
2. **确保批次号已设置**：需要在 `DataCache` 中设置 `batch_code`
3. **确保数据已写入**：需要后端服务正在运行并写入投料数据

---

## 测试建议

禁用 Mock 后，建议测试以下场景：

1. ✅ **正常场景**：有批次号 + 有数据 → 应该显示真实数据
2. ✅ **空数据场景**：有批次号 + 无数据 → 应该显示空白（不报错）
3. ✅ **无批次号场景**：无批次号 → 应该显示空白（不报错）
4. ❌ **数据库故障场景**：数据库连接失败 → 应该抛出异常并记录日志

---

## 相关文件

- `ui/widgets/realtime_data/hopper/dialog_hopper_detail.py` - 投料详情弹窗
- `ui/widgets/realtime_data/hopper/table_feeding_record.py` - 投料记录表
- `ui/widgets/realtime_data/hopper/chart_feeding_stats.py` - 投料累计曲线
- `backend/bridge/history_query.py` - 历史数据查询服务
- `backend/bridge/data_cache.py` - 数据缓存

---

## 更新日期

2026-02-05




