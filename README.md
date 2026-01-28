# #3电炉 - PyQt6 前端

## 项目简介

基于 PyQt6 的#3电炉前端，使用单进程多线程架构，直接复用后端 PLC 通信代码。

## 架构特点

- **单进程多线程**: PyQt6 GUI + 后端逻辑在同一进程
- **零延迟通信**: 线程间通过 Qt 信号槽通信（<0.01ms）
- **100% 代码复用**: 直接导入后端 PLC 通信模块
- **深色科技风**: 复刻 Flutter App 的 UI 设计

## 目录结构

```
ceramic-electric-furnace-pyqt/
├── main.py                 # 应用入口
├── config.py               # 配置文件
├── requirements.txt        # 依赖
│
├── ui/                     # UI 层
│   ├── main_window.py      # 主窗口
│   ├── pages/              # 页面
│   ├── widgets/            # 组件
│   └── styles/             # 样式
│
├── threads/                # 后台线程
│   ├── plc_arc_thread.py   # 弧流轮询（0.2s）
│   └── plc_sensor_thread.py # 传感器轮询（2s）
│
├── models/                 # 数据模型
├── utils/                  # 工具函数
└── assets/                 # 资源文件
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行

```bash
python main.py
```

## 开发进度

查看 `../ceramic-electric-furnace-backend/IMPLEMENTATION_CHECKLIST.md`

## 技术栈

- **GUI 框架**: PyQt6 6.6.1
- **图表库**: PyQtGraph 0.13.3
- **数据处理**: NumPy 1.26.3
- **后端复用**: 直接导入 ceramic-electric-furnace-backend 模块

## 性能指标

- **内存占用**: < 150MB
- **CPU 占用**: < 5%
- **数据延迟**: < 1ms
- **刷新频率**: 弧流 0.2s, 传感器 2s

## 维护者

Clutch Team

## 许可证

MIT

