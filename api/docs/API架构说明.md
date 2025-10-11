# API 架构说明

## 📂 当前文件结构

```
api/
├── main_api.py                    # 主入口 - FastAPI 应用
├── coordinator_api.py             # Coordinator 管理路由
├── bug_detection_api.py          # 缺陷检测 API
├── code_quality_api.py           # 代码质量分析 API
├── code_analysis_api.py          # 代码深度分析 API
├── core/                         # 核心管理模块
│   ├── agent_manager.py          #   - Agent 生命周期管理
│   └── coordinator_manager.py    #   - Coordinator 管理
├── deepseek_config.py            # DeepSeek AI 配置
└── requirements.txt              # Python 依赖
```

---

## 🔧 核心组件说明

### 1. `main_api.py` - 主入口

**职责**：FastAPI 应用主入口

**功能**：
- 创建 FastAPI 应用实例
- 启动 Coordinator 和所有 Agent
- 挂载各个功能模块的路由
- 提供健康检查和根路径

**启动流程**：
```
main_api.py
  ↓
1. 初始化 CoordinatorManager
2. 初始化 AgentManager
3. 启动 Coordinator
4. 启动所有 Agent
5. 挂载路由:
   - coordinator_api（Coordinator 管理）
   - code_quality_api（动态创建 Agent）
   - code_analysis_api（动态创建 Agent）
   - bug_detection_api（使用 AgentManager 中的 Agent）
```

---

### 2. `coordinator_api.py` - Coordinator 管理

**职责**：Coordinator 相关的管理路由

**API 路由**：
- `GET /api/v1/tasks/{task_id}` - 查询任务状态
- `GET /api/v1/agents` - 查询所有 Agent 状态
- `GET /api/v1/agents/{agent_id}` - 查询指定 Agent 状态
- `GET /api/v1/coordinator/status` - 查询 Coordinator 状态
- `POST /api/v1/tasks/{task_id}/cancel` - 取消任务（预留）

---

### 3. `bug_detection_api.py` - 缺陷检测（APIRouter）

**职责**：专注于代码缺陷检测服务

**架构**：APIRouter 模块化路由（已集成到 main_api.py）

**API 路由**：
- `GET /health` - 健康检查
- `POST /api/v1/detection/upload` - 上传文件/项目进行检测
- `GET /api/v1/tasks/{task_id}` - 查询检测任务状态
- `GET /api/v1/detection/rules` - 获取检测规则
- `GET /api/v1/ai-reports/{task_id}` - 获取 AI 分析报告
- `GET /api/v1/ai-reports/{task_id}/download` - 下载 AI 报告
- `GET /api/v1/structured-data/{task_id}` - 获取结构化数据
- `GET /api/v1/reports/{task_id}` - 下载检测报告

**功能**：
- 单文件检测（Python, Java, C/C++, JavaScript等）
- 项目压缩包检测（支持 .zip, .tar.gz 等）
- 静态分析（Pylint, Flake8, Bandit, Mypy）
- AI 智能分析
- 生成自然语言报告
- 结构化数据导出

**Agent 管理**：通过 `set_managers()` 接收 AgentManager 中的 BugDetectionAgent

---

### 4. `code_quality_api.py` - 代码质量分析

**职责**：代码质量评估

**API 路由**：
- `POST /api/code-quality/analyze-file` - 分析单个文件
- `POST /api/code-quality/analyze-upload` - 分析上传的文件

**功能**：
- 代码质量评分
- 复杂度分析
- 风格检查
- AI 质量评估

**Agent 管理**：动态创建 `CodeQualityAgent`

---

### 5. `code_analysis_api.py` - 代码深度分析

**职责**：深度代码分析

**API 路由**：
- `POST /api/code-analysis/analyze` - 分析项目
- `POST /api/code-analysis/analyze-upload` - 分析上传的文件
- `POST /api/code-analysis/analyze-file` - 分析单个文件
- `GET /api/code-analysis/health` - 健康检查

**功能**：
- 代码结构分析
- 依赖关系分析
- 复杂度评估
- AI 深度分析

**Agent 管理**：动态创建 `CodeAnalysisAgent`

---

### 6. `core/` - 核心管理模块

#### `agent_manager.py` - Agent 管理器

**职责**：统一管理所有 Agent 的生命周期

**功能**：
- 启动所有 Agent（BugDetection, FixExecution, CodeAnalysis, CodeQuality）
- 注册 Agent 到 Coordinator
- 提供 Agent 访问接口
- 停止所有 Agent

**管理的 Agent**：
```python
agent_configs = [
    ("bug_detection_agent", BugDetectionAgent, "📦", "缺陷检测"),
    ("fix_execution_agent", FixExecutionAgent, "🔧", "自动修复"),
    ("code_analysis_agent", CodeAnalysisAgent, "📊", "代码分析"),
    ("code_quality_agent", CodeQualityAgent, "⭐", "代码质量"),
]
```

#### `coordinator_manager.py` - Coordinator 管理器

**职责**：管理 Coordinator 的生命周期

**功能**：
- 启动 Coordinator
- 停止 Coordinator
- 提供 Coordinator 实例访问

---

## 🚀 启动方式

### 方式 1：使用启动脚本（推荐）

```bash
python start_api.py
```

**说明**：
- ✅ `start_api.py` 会自动启动 **`main_api.py`**（模块化架构）
- ✅ 包含 Coordinator + AgentManager + 所有路由模块
- ✅ **已挂载** `bug_detection_api.py`（作为 APIRouter 挂载）

### 方式 2：直接使用 uvicorn

```bash
cd api
python -m uvicorn main_api:app --host 0.0.0.0 --port 8001 --reload
```

---

## 📍 API 访问地址

启动后访问以下地址：

- **API 文档**：http://localhost:8001/docs
- **ReDoc 文档**：http://localhost:8001/redoc
- **健康检查**：http://localhost:8001/health
- **根路径**：http://localhost:8001/

---

## 🔑 完整 API 路由列表

### 系统相关
- `GET /` - 根路径（API 摘要）
- `GET /health` - 健康检查

### Coordinator 管理
- `GET /api/v1/coordinator/status` - Coordinator 状态
- `GET /api/v1/agents` - 所有 Agent 状态
- `GET /api/v1/agents/{agent_id}` - 指定 Agent 状态
- `GET /api/v1/tasks/{task_id}` - 任务状态查询
- `POST /api/v1/tasks/{task_id}/cancel` - 取消任务

### 缺陷检测
- `POST /api/v1/detection/upload` - 上传文件检测
- `GET /api/v1/detection/rules` - 获取检测规则
- `GET /api/v1/ai-reports/{task_id}` - 获取 AI 报告
- `GET /api/v1/ai-reports/{task_id}/download` - 下载 AI 报告
- `GET /api/v1/structured-data/{task_id}` - 获取结构化数据
- `GET /api/v1/reports/{task_id}` - 下载检测报告

### 代码质量
- `POST /api/code-quality/analyze-file` - 分析文件质量
- `POST /api/code-quality/analyze-upload` - 上传文件质量分析

### 代码分析
- `POST /api/code-analysis/analyze` - 分析项目
- `POST /api/code-analysis/analyze-upload` - 上传文件分析
- `POST /api/code-analysis/analyze-file` - 分析单个文件
- `GET /api/code-analysis/health` - 健康检查

---

## 📊 Agent 架构

### Agent 管理方式对比

| Agent | 管理方式 | 说明 |
|-------|---------|------|
| **BugDetectionAgent** | AgentManager 统一管理 | 启动时创建，注册到 Coordinator，被 bug_detection_api 使用 |
| **FixExecutionAgent** | AgentManager 统一管理 | 启动时创建，注册到 Coordinator |
| **CodeAnalysisAgent** | 动态创建 | code_analysis_api 内部管理（独立实例）|
| **CodeQualityAgent** | 动态创建 | code_quality_api 内部管理（独立实例）|

### Agent 通信流程

```
前端上传文件
    ↓
API 接收请求
    ↓
Coordinator 创建任务
    ↓
分配给对应 Agent
    ↓
Agent 执行任务
    ↓
返回结果给 Coordinator
    ↓
API 返回结果给前端
```

---

python start_api.py
    ↓
检查依赖（FastAPI, uvicorn）
    ↓
切换到 api/ 目录
    ↓
启动 uvicorn main_api:app ← 注意：启动的是 main_api.py
    ↓
main_api.py 的 startup_event 触发
    ↓
① 创建 CoordinatorManager → 启动 Coordinator
    ├─ 启动 TaskManager
    ├─ 启动 EventBus
    └─ 启动 DecisionEngine
    ↓
② 创建 AgentManager(coordinator) → 启动所有 Agent
    ├─ BugDetectionAgent → 注册到 Coordinator
    ├─ FixExecutionAgent → 注册到 Coordinator
    ├─ CodeAnalysisAgent → 注册到 Coordinator
    └─ CodeQualityAgent → 注册到 Coordinator
    ↓
③ 挂载 API 路由模块
    ├─ coordinator_api.router（任务状态、Agent 管理）
    ├─ code_quality_api.router（代码质量分析）
    ├─ code_analysis_api.router（代码深度分析）
    └─ bug_detection_api.router（缺陷检测）
    ↓
系统启动完成，监听 0.0.0.0:8001


## 💡 架构特点

### ✅ 优势

1. **模块化设计**：每个功能独立文件，职责清晰
2. **集中管理**：Coordinator 和 Agent 统一管理
3. **易于扩展**：添加新功能只需创建新的 API 文件
4. **动态配置**：部分 Agent 支持动态创建
5. **统一入口**：main_api.py 作为唯一启动点

### 🎯 适用场景

- ✅ 代码缺陷检测
- ✅ 代码质量评估
- ✅ 代码深度分析
- ✅ 自动化修复（FixExecutionAgent）
- ✅ 多 Agent 协作任务

---

## 📝 配置文件

### `requirements.txt`

主要依赖：
```
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.11.0
pydantic-settings>=2.0.0
```

### `deepseek_config.py`

DeepSeek AI 配置：
- API Key 配置
- Base URL 配置
- 配置验证

