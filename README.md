# AI Agent 多语言代码检测系统

一个基于多Agent协作的智能软件开发系统，专注于多语言代码缺陷检测、智能分析与自动修复。

## 🌟 主要特性

- **🌍 多语言支持**: Python, Java, C/C++, JavaScript, Go
- **🤖 AI智能分析**: 集成DeepSeek API进行智能代码分析和修复建议
- **📁 项目级检测**: 支持大型项目文件上传和分析（支持.zip, .tar.gz等格式）
- **📊 自然语言报告**: 生成专业的AI分析报告和结构化数据导出
- **🔧 多种检测模式**: 支持静态检测、动态检测、综合检测
- **⚡ 自动修复**: 集成FixExecutionAgent，支持代码自动修复
- **🧪 测试生成与验证**: 自动生成测试用例并验证修复效果
- **📈 可视化界面**: 现代化的Web前端界面（10个专业页面）
- **🐳 Docker支持**: 提供容器化方案，解决依赖和环境问题
- **🔄 协调中心**: 基于Coordinator的任务调度和Agent协作机制

## 🏗️ 系统架构

系统采用分层架构设计，从用户接口到数据存储共分为5层：

### 1. 用户接口层
系统与用户交互的入口，提供多种接入方式：
- **Web前端界面 (UI)**：10个专业HTML页面，提供可视化操作界面
  - `index.html` / `login.html` - 登录页面
  - `main.html` - 主界面
  - `analyse.html` - 静态分析页面
  - `deep_analysis.html` - 深度分析页面
  - `dynamic_detection.html` - 动态检测页面
  - `comprehensive_detection.html` - 综合检测页面
  - `fix_execution.html` - 修复执行页面
  - `projects.html` - 项目管理页面
  - `explore.html` - 探索页面
- **REST API接口**：FastAPI构建的模块化API，支持CI/CD集成
- **命令行接口 (CLI)**：`main.py` 提供命令行工具

**流向**：所有用户请求通过API层统一接收，传递给协调控制层。

### 2. 协调控制层
系统的"大脑"和"中枢神经系统"，负责指挥调度：
- **协调中心 (Coordinator)**：请求的总入口和总出口，管理所有Agent
- **任务管理器 (TaskManager)**：核心调度器，将任务分解为子任务并调度相应Agent执行
- **决策引擎 (DecisionEngine)**：提供智能决策，如修复方案选择
- **事件总线 (EventBus)**：采用发布-订阅模式，实现Agent间异步通信和解耦
- **核心管理器**：
  - `CoordinatorManager`：管理Coordinator生命周期
  - `AgentManager`：统一管理所有Agent的启动、停止和注册

### 3. Agent执行层
系统的"四肢"，由多个职责单一的智能体组成：

#### 3.1 感知分析组
- **Bug检测Agent (BugDetectionAgent)**：代码缺陷、安全漏洞、风格问题检测
- **代码分析Agent (CodeAnalysisAgent)**：代码理解、依赖分析、复杂度评估
- **代码质量Agent (CodeQualityAgent)**：代码质量评估和评分报告
- **动态检测Agent (DynamicDetectionAgent)**：运行时行为分析和动态检测

#### 3.2 决策执行组
- **修复执行Agent (FixExecutionAgent)**：代码自动修复和格式化
- **测试验证Agent (TestValidationAgent)**：测试用例运行和验证
- **测试生成Agent (TestGenerationAgent)**：自动生成测试用例
- **性能优化Agent (PerformanceOptimizationAgent)**：性能分析和优化建议

### 4. 工具集成层
系统的"工具箱"，Agent调用外部专业工具：
- **静态分析工具**：Pylint, Flake8, Bandit, Mypy, Black, isort
- **AI分析工具**：DeepSeek API（核心），支持OpenAI等大模型API
- **测试工具**：pytest, pytest-cov等测试框架
- **代码生成工具**：代码格式化、自动修复工具
- **Docker支持**：可选Docker容器化运行，解决依赖问题

### 5. 数据存储层
数据持久化支持：
- **文件存储**：代码仓库、报告文件（`api/reports/`）、结构化数据（`api/structured_data/`）
- **任务状态**：任务状态跟踪（`api/tasks_state.json`）
- **日志系统**：系统运行日志记录

## 📁 项目结构

```
CodeAgent/
├── agents/                          # Agent模块
│   ├── bug_detection_agent/         # 缺陷检测Agent
│   ├── code_analysis_agent/         # 代码分析Agent
│   ├── code_quality_agent/          # 代码质量Agent
│   ├── fix_execution_agent/         # 修复执行Agent（集成MiniSWE-agent）
│   ├── test_validation_agent/       # 测试验证Agent
│   ├── test_generation_agent/       # 测试生成Agent
│   ├── performance_optimization_agent/ # 性能优化Agent
│   ├── dynamic_detection_agent/     # 动态检测Agent
│   ├── base_agent.py               # Agent基类
│   └── __init__.py
├── coordinator/                     # 协调中心
│   ├── coordinator.py              # 主协调器
│   ├── task_manager.py             # 任务管理器
│   ├── decision_engine.py          # 决策引擎
│   ├── event_bus.py                # 事件总线
│   ├── message_types.py            # 消息类型定义
│   └── __init__.py
├── api/                            # API接口层（统一入口）
│   ├── main_api.py                 # 主API入口（FastAPI应用）
│   ├── coordinator_api.py          # Coordinator管理API
│   ├── bug_detection_api.py        # 缺陷检测API
│   ├── code_analysis_api.py        # 代码分析API
│   ├── code_quality_api.py         # 代码质量API
│   ├── dynamic_api.py              # 动态检测API
│   ├── fix_execution_api.py        # 修复执行API
│   ├── comprehensive_detection_api.py # 综合检测API
│   ├── core/                       # 核心管理模块
│   │   ├── agent_manager.py        # Agent生命周期管理
│   │   └── coordinator_manager.py  # Coordinator管理
│   ├── deepseek_config.py          # DeepSeek配置
│   ├── docs/                       # API文档
│   ├── reports/                    # 检测报告目录
│   ├── structured_data/            # 结构化数据导出
│   ├── uploads/                    # 文件上传目录
│   ├── comprehensive_detection_results/ # 综合检测结果
│   └── requirements.txt            # API依赖
├── frontend/                       # 前端界面（多页面）
│   ├── index.html                  # 登录页面
│   ├── main.html                   # 主界面
│   ├── analyse.html                # 静态分析页面
│   ├── deep_analysis.html          # 深度分析页面
│   ├── dynamic_detection.html      # 动态检测页面
│   ├── comprehensive_detection.html # 综合检测页面
│   ├── fix_execution.html          # 修复执行页面
│   ├── explore.html                # 探索页面
│   ├── login.html                  # 登录表单
│   └── projects.html               # 项目管理页面
├── tools/                          # 工具集成层
│   ├── static_analysis/           # 静态分析工具
│   │   ├── custom_checker.py      # 自定义检查器
│   │   ├── pylint_runner.py       # Pylint运行器
│   │   └── flake8_runner.py       # Flake8运行器
│   ├── ai_static_analyzer.py       # AI静态分析器
│   └── flask_d_class_detector.py   # Flask装饰器检测器
├── config/                         # 配置文件
│   ├── settings.py                # 系统设置
│   └── agent_config.py            # Agent配置
├── docs/                           # 文档目录（41个文档文件）
│   ├── Pandas测试指南.md           # Pandas测试详细指南
│   ├── Flask_2_0_0_TEST_GUIDE.md   # Flask测试指南
│   ├── 扩展Bug列表说明.md          # 扩展Bug列表文档
│   ├── API_DOCUMENTATION.md       # API文档
│   ├── DEEPSEEK_API_GUIDE.md   # DeepSeek API指南
│   ├── system_architecture.md     # 系统架构说明
│   └── ...                        # 更多文档
├── flask_simple_test/              # Flask测试项目
│   ├── app.py                     # Flask应用
│   ├── flask-2.0.0.zip            # Flask 2.0.0源码
│   └── README.md                  # Flask测试说明
├── examples/                       # 示例项目
│   ├── buggy_project_simple/       # 简单Bug项目示例
│   └── sample_py_project/          # Python项目示例
├── tests/                          # 测试文件和测试数据
│   ├── flask-2.0.0.zip            # Flask测试数据
│   └── test_python.py             # Python测试
├── utils/                          # 工具函数
│   ├── project_runner.py          # 项目运行器
│   └── docker_runner.py            # Docker运行器
├── scripts/                        # 脚本工具
│   ├── cleanup_temp_dirs.py       # 清理临时目录
│   └── init_db.py                 # 初始化数据库
├── extended_bugs.py                # 扩展Bug列表（25个已知Bug）
├── compare_pandas_bugs.py          # Pandas Bug对比分析脚本
├── main.py                         # 主程序入口（命令行版本）
├── start_api.py                    # API启动脚本（推荐）
├── requirements.txt                # 项目依赖
├── docker-compose.flask-test.yml   # Docker Compose配置
├── Dockerfile.flask-test           # Docker镜像定义
└── README.md                       # 项目说明
```

### 🆕 新增测试文件说明

**测试评估文件**：
- **`extended_bugs.py`** - 扩展Bug列表定义文件
  - 包含25个Pandas 1.0.0的已知Bug详细信息
  - 运行 `python extended_bugs.py` 可查看Bug统计
  - 可选文件：如果不存在，对比脚本会使用内置的8个核心Bug
  
- **`compare_pandas_bugs.py`** - Bug对比分析脚本
  - 读取系统检测报告（`api/reports/`目录）
  - 与已知Bug列表对比分析
  - 生成详细的评估报告和统计信息
  - 自动适配：有`extended_bugs.py`用25个Bug，否则用8个Bug

**使用方法**：
```bash
# 1. 查看Bug统计（可选）
python extended_bugs.py

# 2. 运行检测（Web界面上传Pandas代码）
python start_api.py

# 3. 对比分析（检测完成后）
python compare_pandas_bugs.py
```

## ⚠️ 实际实现与原设计的关键差异

### 主要变化
1. **新增核心管理层**：`api/core/` 目录包含 `agent_manager.py` 和 `coordinator_manager.py`
2. **API架构模块化**：5个独立的 API 模块（bug_detection, code_quality, code_analysis, dynamic, coordinator）
3. **统一启动入口**：`main_api.py` 作为唯一启动点，管理所有组件生命周期
4. **Coordinator优先启动**：先启动 Coordinator，再启动 Agent（确保协调中心就绪）
5. **新增动态检测**：`DynamicDetectionAgent` 和 `dynamic_api.py`（运行时行为分析）
6. **三种分析模式**：file（单文件）、project（项目）、dynamic（动态检测）
7. **多页面前端**：8个HTML页面（login, main, analyse, deep_analysis, dynamic_detection等）

### 工作流更新
- **原设计**：用户请求 → API → Agent → 返回结果
- **实际实现**：用户请求 → API路由 → Coordinator协调 → TaskManager分配 → Agent执行 → 返回结果

### API层次结构
```
main_api.py (FastAPI主应用)
  ├── coordinator_api.py (任务状态、Agent管理)
  ├── bug_detection_api.py (缺陷检测)
  ├── code_quality_api.py (代码质量)
  ├── code_analysis_api.py (代码分析)
  └── dynamic_api.py (动态检测)
```

## 🔄 实际工作流程

### 系统启动顺序
```
python start_api.py
  ↓
main_api.py 启动
  ↓
1️⃣ CoordinatorManager → Coordinator (TaskManager + EventBus + DecisionEngine)
  ↓
2️⃣ AgentManager → 启动所有Agent并注册到Coordinator
  ↓
3️⃣ 挂载API路由（bug_detection, code_quality, code_analysis, dynamic, coordinator）
  ↓
✅ 系统就绪，监听 0.0.0.0:8001
```

### 用户请求流程
```
前端界面 → API路由分发 → Coordinator协调 → Agent执行 → 生成报告 → 返回前端
```

### API访问地址
启动后可访问：
- **API文档**: http://localhost:8001/docs （Swagger UI）
- **ReDoc文档**: http://localhost:8001/redoc
- **健康检查**: http://localhost:8001/health
- **根路径**: http://localhost:8001/

### 主要API端点

#### 系统相关
- `GET /` - 根路径（API摘要和状态）
- `GET /health` - 健康检查

#### Coordinator管理
- `GET /api/v1/coordinator/status` - Coordinator状态
- `GET /api/v1/agents` - 所有Agent状态
- `GET /api/v1/agents/{agent_id}` - 指定Agent状态
- `GET /api/v1/tasks/{task_id}` - 查询任务状态
- `POST /api/v1/tasks/{task_id}/cancel` - 取消任务

#### 缺陷检测
- `POST /api/v1/detection/upload` - 上传文件/项目进行检测
- `GET /api/v1/detection/rules` - 获取检测规则
- `GET /api/v1/ai-reports/{task_id}` - 获取AI分析报告
- `GET /api/v1/ai-reports/{task_id}/download` - 下载AI报告
- `GET /api/v1/structured-data/{task_id}` - 获取结构化数据
- `GET /api/v1/reports/{task_id}` - 下载检测报告

#### 代码质量分析
- `POST /api/code-quality/analyze-file` - 分析单个文件
- `POST /api/code-quality/analyze-upload` - 分析上传的文件

#### 代码深度分析
- `POST /api/code-analysis/analyze` - 分析项目
- `POST /api/code-analysis/analyze-upload` - 分析上传的文件
- `POST /api/code-analysis/analyze-file` - 分析单个文件
- `GET /api/code-analysis/health` - 健康检查

#### 动态检测
- `POST /api/dynamic/detect` - 动态检测（运行时行为分析）

#### 综合检测
- `POST /api/comprehensive/detect` - 综合检测（静态+动态+运行时）
- `GET /api/comprehensive/status` - 检测状态
- `GET /api/comprehensive/health` - 健康检查

## 🚀 快速开始

### 环境要求
- Python 3.8+
- 现代浏览器 (Chrome, Firefox, Safari, Edge)

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd CodeAgent
```

2. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
pip install -r api/requirements.txt
```

4. **配置AI分析**
```bash
# 方法1: 环境变量
export DEEPSEEK_API_KEY="your_api_key_here"

# 方法2: 直接编辑配置文件
# 编辑 api/deepseek_config.py 文件
```

5. **启动系统**
```bash
# 启动API服务（推荐方式）
python start_api.py

# 或直接使用 uvicorn
cd api
python -m uvicorn main_api:app --host 0.0.0.0 --port 8001 --reload

# 打开前端界面
# 浏览器访问: frontend/index.html 或 frontend/main.html
```

## 🌍 多语言支持

### 支持的语言
- **Python**: 使用 Pylint + Flake8 + 自定义检测器 + AI分析
- **Java**: 使用 AI分析检测空指针、内存泄漏等问题
- **C/C++**: 使用 AI分析检测缓冲区溢出、内存泄漏等问题
- **JavaScript/TypeScript**: 使用 AI分析检测 XSS、内存泄漏等问题
- **Go**: 使用 AI分析检测并发安全、错误处理等问题

### 检测类型
- **语法错误和编译问题**
- **逻辑错误和算法问题**
- **内存泄漏和资源管理问题**
- **安全漏洞和输入验证问题**
- **性能问题和优化建议**
- **代码规范和最佳实践问题**

## 📁 项目分析功能

### 支持的项目格式
- **压缩文件**: `.zip`, `.tar`, `.tar.gz`, `.rar`, `.7z`
- **目录**: 直接上传项目文件夹

### 项目分析特性
- **自动语言检测**: 根据文件扩展名和内容自动识别编程语言
- **并行分析**: 支持多文件并行检测，提高分析效率
- **文件过滤**: 自动过滤大文件和无关文件
- **结果合并**: 将多个文件的检测结果合并为统一报告

### 项目限制
- **最大项目大小**: 100MB
- **最大文件数量**: 1000个文件
- **单文件大小限制**: 10MB
- **每种语言最多分析**: 50个文件

## 🤖 AI智能分析

### AI分析优势
- **编译无关**: 不需要编译代码即可分析
- **跨语言**: 支持多种编程语言
- **智能检测**: 能够发现传统工具难以检测的问题
- **上下文理解**: 理解代码的业务逻辑和设计意图

### AI检测类型
1. **语法错误和编译问题**
2. **逻辑错误和算法问题**
3. **内存泄漏和资源管理问题**
4. **安全漏洞和输入验证问题**
5. **性能问题和优化建议**
6. **代码规范和最佳实践问题**

## 📊 使用方法

### 单文件分析
1. 选择"单文件分析"模式
2. 上传代码文件（支持多种语言）
3. 选择检测选项
4. 查看检测结果和AI报告

### 项目分析
1. 选择"项目分析"模式
2. 上传项目压缩包或文件夹
3. 系统自动解压和扫描
4. 查看多文件综合检测报告

## 📈 检测结果

### 结果格式
- **文件级别**: 每个文件的详细检测结果
- **项目级别**: 整个项目的综合统计
- **语言分类**: 按编程语言分类的检测结果
- **严重性分级**: 错误、警告、信息三个级别

### AI自然语言报告
- **总体评估**: 代码质量整体评价
- **主要问题分析**: 重点问题详细说明
- **改进建议**: 具体的修复建议
- **优先级排序**: 按重要性排序的问题列表

## 🔧 配置选项

### 检测选项
- **enable_static**: 启用自定义静态检测（Python）
- **enable_pylint**: 启用Pylint检测（Python）
- **enable_flake8**: 启用Flake8检测（Python）
- **enable_ai_analysis**: 启用AI分析（所有语言）

### 分析类型
- **file**: 单文件分析（静态代码检测）
- **project**: 项目分析（批量文件检测）
- **dynamic**: 动态检测（运行时行为分析）

## 📝 示例

### Python文件检测
```python
# 上传 test.py 文件
# 系统使用 Pylint + Flake8 + 自定义检测器 + AI分析
# 返回详细的缺陷报告和AI自然语言分析
```

### Java项目检测
```bash
# 上传 java_project.zip
# 系统解压后扫描所有 .java 文件
# 使用AI分析每个文件
# 生成项目级别的综合报告
```

### 混合语言项目
```bash
# 上传包含 Python + Java + C++ 的项目
# 系统自动识别不同语言的文件
# 分别使用相应的检测工具
# 生成多语言综合报告
```

## 🎯 最佳实践

1. **选择合适的分析类型**: 单文件用于快速检测，项目用于全面分析
2. **启用AI分析**: 获得更智能的检测结果和修复建议
3. **关注高优先级问题**: 优先修复错误级别的问题
4. **定期检测**: 建议在代码提交前进行检测
5. **结合人工审查**: AI检测结果需要结合人工判断

## 📚 文档

### 🧪 测试指南

**推荐：Pandas 1.0.0测试** - 大型项目，Bug类型丰富

- **[Pandas测试指南](docs/Pandas测试指南.md)** 📖 **完整指南** ⭐ **推荐阅读**
  - 详细的测试流程说明
  - 核心版（8个Bug）vs 扩展版（25个Bug）对比
  - 文件位置和使用方法说明
  - 预期结果分析和解读

- **[扩展Bug列表说明](docs/扩展Bug列表说明.md)** 📊 **详细文档**
  - 25个已知Bug的详细列表
  - 按类型、严重性、检测方法分类
  - 完整的统计信息

**测试文件**：
- `extended_bugs.py` - 25个Bug定义（可选，推荐使用）
- `compare_pandas_bugs.py` - 对比分析脚本（必备）

**快速开始**：
```bash
# 查看Bug统计
python extended_bugs.py

# 运行检测后对比
python compare_pandas_bugs.py
```

### 🧪 Flask 2.0.0 测试对比

项目提供了 Flask 版本的评测脚本和测试项目：
- **测试项目位置**：`flask_simple_test/` 目录
- **评测脚本**：`compare_flask_bugs.py`（如果存在）

#### 金标数据

- **内置 32 条 Flask 2.0.x 修复的 Issue**，涵盖：
  - **简单问题（8条）**：静态可检类型（S）- 类型注解、API参数等
  - **中等问题（18条）**：AI辅助类型（A）- 蓝图路由、JSON行为等  
  - **困难问题（6条）**：动态验证类型（D）- 异步上下文、运行时验证等

#### 子域分类系统

脚本将检测结果自动分类到以下子域：
- `typing_decorators`：类型注解和装饰器问题
- `blueprint_routing`：蓝图路由相关问题
- `helpers_send_file`：文件发送API问题
- `cli_loader`：CLI加载器问题
- `json_behavior`：JSON行为问题
- `static_pathlike`：路径类型问题
- `blueprint_naming`：蓝图命名问题
- `blueprint_registration`：蓝图注册问题
- `async_ctx_order`：异步上下文和顺序问题

#### 使用方法

```bash
# 自动检测最新报告（推荐）
python compare_flask_bugs.py

# 指定报告文件
python compare_flask_bugs.py --agent-json path/to/report.json
```

#### 输出格式（与 Pandas 完全一致）

脚本生成三段式输出格式：

1. **已知Issue vs 系统检测对比**：按子域分类显示检测结果
2. **总体检测率和预期检测率**：显示检测率统计
3. **系统能力评估与改进建议**：评估静态分析、AI分析、动态分析能力

#### 评估标准

- **总体检测率**：基于所有已知Issue的检测率
- **预期检测率**：基于可检测Issue的检测率（排除需要运行时验证的问题）
- **能力评估**：分别评估静态分析、AI分析、动态分析能力

#### 自动发现机制

默认自动搜索目录（按优先级）：
- `api/reports`
- `project/CodeAgent/api/reports`  
- `project/CodeAgent/frontend/uploads`

#### 详细说明

更多关于脚本映射实现、子域分类逻辑等技术细节，请参考：[Flask脚本映射实现指南](docs/Flask脚本映射实现指南.md)

---

### 📖 系统文档

#### 核心文档
- [API接口文档](docs/API_DOCUMENTATION.md) - 详细的API使用说明
- [DeepSeek API指南](docs/DEEPSEEK_API_GUIDE.md) - AI分析功能配置指南
- [系统架构说明](docs/system_architecture.md) - 系统架构和Agent设计
- [工作流程图](docs/workflow_diagram.md) - 系统工作流程说明

#### 测试指南
- [Pandas测试指南](docs/Pandas测试指南.md) - Pandas 1.0.0测试完整指南 ⭐
- [Flask测试指南](docs/FLASK_2_0_0_TEST_GUIDE.md) - Flask 2.0.0测试指南
- [扩展Bug列表说明](docs/扩展Bug列表说明.md) - 25个已知Bug详细列表
- [Flask脚本映射实现指南](docs/Flask脚本映射实现指南.md) - Flask测试脚本技术实现详解
- [Flask版本选择与Issue策略](docs/Flask版本选择与Issue策略.md) - Flask测试项目选择策略

#### Agent文档
- [代码分析Agent说明](docs/CODE_ANALYSIS_AGENT_README.md)
- [代码质量Agent说明](docs/CODE_QUALITY_AGENT_README.md)
- [修复执行Agent使用指南](docs/FIX_EXECUTION_AGENT_USAGE.md)
- [动态检测实现总结](docs/DYNAMIC_DETECTION_IMPLEMENTATION_SUMMARY.md)

#### 其他文档
- [Docker设置指南](DOCKER_SETUP_GUIDE.md) - Docker容器化部署指南
- [数据集测试指南](docs/DATASET_TESTING_GUIDE.md) - 数据集测试说明

## 🤖 Agent详细说明

### 已实现的Agent

1. **BugDetectionAgent** - 缺陷检测Agent
   - 支持多语言静态分析
   - 集成Pylint、Flake8、Bandit等工具
   - AI智能分析代码缺陷
   - 生成详细检测报告

2. **CodeAnalysisAgent** - 代码分析Agent
   - 代码结构分析
   - 依赖关系分析
   - 复杂度评估
   - AI深度代码理解

3. **CodeQualityAgent** - 代码质量Agent
   - 代码质量评分
   - 风格检查
   - 最佳实践评估
   - 质量报告生成

4. **FixExecutionAgent** - 修复执行Agent
   - 自动代码修复
   - 集成MiniSWE-agent框架
   - 支持多种修复策略
   - 修复验证

5. **TestValidationAgent** - 测试验证Agent
   - 测试用例运行
   - 修复效果验证
   - 测试结果分析

6. **TestGenerationAgent** - 测试生成Agent
   - 自动生成测试用例
   - 支持多语言测试生成
   - 测试用例优化

7. **DynamicDetectionAgent** - 动态检测Agent
   - 运行时行为分析
   - 动态缺陷检测
   - 性能监控

8. **PerformanceOptimizationAgent** - 性能优化Agent
   - 性能分析
   - 优化建议生成
   - 性能报告

## 🔮 未来扩展

- 支持更多编程语言（Rust, Swift, Kotlin等）
- 集成更多专业检测工具
- 支持自定义检测规则
- 增强代码修复能力
- 支持CI/CD集成
- 支持更多AI模型（本地模型、其他API）
- 增强动态检测能力
- 支持增量分析

## 📄 许可证

本项目采用 MIT 许可证。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 GitHub Issue
- 发送邮件至项目维护者

---

## 📝 更新日志

### 最新更新

#### 架构升级
- ✅ 新增 `api/core/` 核心管理层
  - `agent_manager.py`: Agent生命周期管理
  - `coordinator_manager.py`: Coordinator管理
- ✅ API架构模块化重构
  - 多个独立API模块，使用 APIRouter
  - `main_api.py` 作为统一启动入口
- ✅ 完善协调中心（Coordinator）
  - TaskManager: 任务管理器
  - EventBus: 事件总线
  - DecisionEngine: 决策引擎
  - Message Types: 消息类型定义

#### 功能增强
- ✅ 新增动态检测功能
  - `DynamicDetectionAgent`: 运行时行为分析
  - `dynamic_api.py`: 动态检测API
  - `dynamic_detection.html`: 动态检测界面
- ✅ 新增综合检测功能
  - `comprehensive_detection_api.py`: 综合检测API
  - 支持静态+动态+运行时分析
- ✅ 三种分析模式
  - file: 单文件分析
  - project: 项目批量分析
  - dynamic: 动态检测
- ✅ 多页面前端设计
  - 10个专业界面页面
  - 更好的用户体验

#### Agent增强
- ✅ 集成FixExecutionAgent（MiniSWE-agent）
- ✅ 新增TestGenerationAgent
- ✅ 完善所有Agent功能

#### 测试支持
- ✅ Pandas 1.0.0测试支持（25个已知Bug）
- ✅ Flask 2.0.0测试支持（32个已知Issue）
- ✅ 测试对比分析脚本

#### Docker支持
- ✅ Docker容器化方案
- ✅ Docker Compose配置
- ✅ 解决依赖和环境问题

#### 工作流优化
- ✅ Coordinator优先启动
- ✅ API路由分发机制
- ✅ 任务状态跟踪
- ✅ Agent状态监控

#### 文档更新
- ✅ 41个文档文件
- ✅ 完整的测试指南
- ✅ API文档完善
- ✅ Agent使用说明

---

*最后更新: 2024年*

## 🐳 使用 Docker 运行（推荐，解决本地依赖卡顿/兼容性问题）

本项目已提供容器化方案，适用于在 Windows 上因虚拟环境/依赖安装卡住的场景。容器内将隔离运行依赖安装、静态/动态检测以及针对上传的测试包创建独立 venv。

### 快速开始

```bash
# 1) 构建镜像（初次或依赖变更后）
docker compose build

# 2) 启动服务（默认映射到宿主 8000）
docker compose up -d

# 3) 查看日志
docker compose logs -f

# 4) 关闭服务
docker compose down
```

启动成功后访问：
- API 文档: http://localhost:8000/docs
- 前端页面: 打开 `frontend/index.html`（或按你现有前端入口）

### 前端上传与动态检测
- 上传的压缩包将保存到容器内 `/app/api/uploads`（宿主机同步映射到 `api/uploads/`）
- 系统会读取压缩包内的 `requirements.txt`，在容器内为该次任务创建隔离的虚拟环境（默认目录：`/tmp/venvs/<task-id>`），再安装依赖（如 Flask==2.0.0、兼容的 Werkzeug 等），随后执行静态+动态检测

### 环境变量配置
如需修改任务虚拟环境位置，可设置环境变量：
```bash
docker compose down
# 修改 docker-compose.yml 中 environment 部分
# 例如: CODEAGENT_JOB_VENVS_DIR=/tmp/venvs
# 然后重新启动
docker compose up -d
```

### 常见问题
- **依赖安装缓慢**：首次构建镜像时保持网络可用；`.dockerignore` 已忽略大体积目录；镜像内已安装基础编译依赖
- **端口冲突**：修改 `docker-compose.yml` 中 `ports: - "8000:8000"` 的左侧宿主端口，例如改为 `18000:8000`
- **Windows路径/权限问题**：通过卷挂载（volumes）将项目同步到容器内 `/app`，避免在宿主创建虚拟环境失败

### 目录映射
- `./api/uploads -> /app/api/uploads`: 前端上传目录
- `./api/reports -> /app/api/reports`: 报告输出目录
- `./api/comprehensive_detection_results -> /app/api/comprehensive_detection_results`: 综合检测结果
- `./api/dynamic_detection_results -> /app/api/dynamic_detection_results`: 动态检测结果

### 使用提示
> 如需对 Flask 2.0.0 的 32 个问题进行回归测试，请参考文档 `docs/Flask版本选择与Issue策略.md`，并在上传的压缩包中包含对应的 `requirements.txt`（指定 Flask==2.0.0 及其兼容依赖）。