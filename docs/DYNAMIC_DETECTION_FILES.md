# 动态缺陷检测核心文件清单

## 核心代码文件

### 1. 监控Agent
- `agents/simple_monitor_agent.py` - 简化版动态监控Agent
  - 系统资源监控（CPU、内存、磁盘）
  - 简单告警机制
  - 指标收集和存储

### 2. 项目运行器
- `utils/project_runner.py` - 项目运行器
  - 解压项目压缩包
  - 查找并运行主文件
  - 监控执行过程
  - 收集运行日志和指标

### 3. 集成检测器
- `agents/integrated_detector.py` - 集成检测器
  - 结合静态和动态检测
  - 生成综合检测报告
  - 问题分析和建议

### 4. API接口
- `api/dynamic_api.py` - 动态检测API
  - 文件上传接口
  - 检测任务管理
  - 结果查询接口

### 5. 前端界面
- `frontend/dynamic_detection.html` - 动态检测前端界面
  - 文件上传功能
  - 检测选项配置
  - 结果展示界面

### 6. 启动脚本
- `start_dynamic_detection.py` - 启动脚本
  - 依赖检查
  - 服务启动
  - 组件测试

## 核心文档

### 1. 技术文档
- `docs/dynamic_detection_core.md` - 动态检测核心概念和技术实现
- `README_DYNAMIC_DETECTION.md` - 使用说明和快速开始指南

### 2. 实施计划
- `docs/simplified_dynamic_detection_plan.md` - 3周实施计划

## 文件结构

```
CodeAgent/
├── agents/
│   ├── simple_monitor_agent.py      # 简化监控Agent
│   └── integrated_detector.py       # 集成检测器
├── utils/
│   └── project_runner.py            # 项目运行器
├── api/
│   └── dynamic_api.py               # 动态检测API
├── frontend/
│   └── dynamic_detection.html       # 前端界面
├── docs/
│   ├── dynamic_detection_core.md    # 核心概念文档
│   └── simplified_dynamic_detection_plan.md  # 实施计划
├── start_dynamic_detection.py       # 启动脚本
└── README_DYNAMIC_DETECTION.md      # 使用说明
```

## 核心功能

### 1. 系统监控
- CPU使用率监控
- 内存使用率监控
- 磁盘使用率监控
- 简单阈值告警

### 2. 项目运行
- 自动解压ZIP项目
- 查找并运行主文件
- 监控执行过程
- 收集运行日志

### 3. 综合检测
- 静态代码分析
- 动态系统监控
- 运行时错误检测
- 生成综合报告

### 4. 用户界面
- 文件上传功能
- 检测选项配置
- 结果展示界面
- 实时状态显示

## 使用流程

1. **启动服务**：`python start_dynamic_detection.py`
2. **访问界面**：打开 `frontend/dynamic_detection.html`
3. **上传项目**：选择ZIP压缩包
4. **配置选项**：选择检测类型
5. **开始检测**：系统自动处理
6. **查看结果**：获取检测报告

## 技术特点

- **简化架构**：使用成熟技术栈，避免复杂设计
- **实用功能**：专注核心功能，确保3周内完成
- **易于维护**：代码结构清晰，文档完善
- **可扩展性**：模块化设计，便于后续扩展

## 依赖要求

- Python 3.8+
- FastAPI
- Uvicorn
- psutil

## 安装和运行

```bash
# 安装依赖
pip install fastapi uvicorn psutil

# 启动服务
python start_dynamic_detection.py

# 访问界面
# 打开 frontend/dynamic_detection.html
```

这个文件清单包含了动态缺陷检测系统的所有核心文件，确保系统能够正常运行并提供完整的检测功能。
