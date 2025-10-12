# AI Agent 多语言代码检测系统

一个基于多Agent协作的智能软件开发系统，专注于多语言代码缺陷检测与AI智能分析。

## 🌟 主要特性

- **🌍 多语言支持**: Python, Java, C/C++, JavaScript, Go
- **🤖 AI智能分析**: 集成DeepSeek API进行智能代码分析
- **📁 项目级检测**: 支持大型项目文件上传和分析
- **📊 自然语言报告**: 生成专业的AI分析报告
- **🔧 实时检测**: 支持单文件和项目批量检测
- **📈 可视化界面**: 现代化的Web前端界面

## 🏗️ 系统架构

# 系统架构分层详解

## 1. 用户接口层
这是系统与用户（开发者、测试人员等）交互的入口，提供了多种接入方式：
- **Web前端界面 (UI)**：提供可视化的操作界面，如提交代码、查看报告、监控状态等。
- **REST API接口 (API)**：允许其他系统（如CI/CD流水线、Git平台Webhook）通过编程方式集成和调用平台服务。
- **命令行接口 (CLI)**：为偏好命令行的开发者提供本地工具，方便快速调用平台功能。

**流向**：所有用户请求都通过API层统一接收，并向下传递给协调控制层。


## 2. 协调控制层
这是系统的“大脑”和“中枢神经系统”，负责指挥调度。
- **协调中心 (COORD)**：请求的总入口和总出口。接收API请求，并负责将最终结果返回给用户。
- **任务管理器 (TM)**：**核心调度器**。它接收COORD派发的任务，将其分解为多个子任务（例如：先分析、再修复、最后测试），并调度**Agent执行层**中相应的Agent来执行。它跟踪整个任务的生命周期。
- **决策引擎 (DE)**：为任务处理提供智能决策。例如，当多个修复方案可用时，DE可能根据代码上下文、历史数据等决定最优方案。
- **事件总线 (EB)**：系统的**“消息脊柱”**。采用发布-订阅模式，不同组件（特别是Agent之间）通过EB进行异步通信，实现解耦。例如，当一个Agent完成任务后，可以通过EB发布一个事件，通知其他Agent开始工作。


## 3. Agent执行层
这是系统的“四肢”，由多个职责单一的智能体（Agent）组成，负责具体执行任务。它们被分为三组：

### 3.1 感知分析组
负责代码检查和分析，包含以下Agent：
- **Bug检测Agent (BDA)**：专注于寻找代码缺陷、安全漏洞、风格问题。
- **代码分析Agent (CAA)**：进行更深层次的代码理解、依赖分析、复杂度评估等。
- **代码质量Agent (CQA)**：综合评估代码质量，并生成质量评分报告。

### 3.2 决策执行组
负责执行具体的变更和优化，包含以下Agent：
- **修复执行Agent (FEA)**：接收分析结果，并执行具体的代码修复和格式化操作。
- **测试验证Agent (TVA)**：为修复后的代码生成或运行测试用例，确保修复没有引入新问题。
- **性能优化Agent (POA)**：专注于代码性能分析和优化建议。

### 3.3 监控反馈组
负责系统的观察、学习和改进，包含以下Agent：
- **监控Agent (MA)**：持续监控系统健康、任务状态和性能指标。
- **报告Agent (RA)**：生成各种人类可读的报告（HTML、PDF等）。
- **学习Agent (LA)**：非常重要的一环，从历史任务、用户反馈中学习，优化决策模型和规则，使系统越来越智能。


## 4. 工具集成层
这是系统的“工具箱”，Agent并不直接实现所有功能，而是**调用外部专业工具**来完成工作。这种设计使系统非常灵活，可以轻松集成新的工具。
- **静态分析工具**：Pylint, Flake8, Bandit 等用于基础代码检查。
- **AI分析工具**：**DeepSeek、OpenAI等大模型API是核心**，用于复杂的代码理解、修复建议生成等LLM擅长的任务。也支持本地模型。
- **测试工具**：集成各类测试框架以验证代码正确性。
- **代码生成工具**：如代码格式化、自动修复工具，用于执行具体的代码变更。


## 5. 数据存储层
为整个系统提供数据持久化支持，包含以下组件：
- **数据库 (DB)**：存储结构化数据，如用户信息、任务配置、历史记录、质量报告等。
- **缓存 (CACHE)**：提升性能，存储临时数据（如会话、热门分析结果）。
- **文件存储**：存储代码仓库、生成的报告文件、日志文件等。
- **日志系统**：记录系统运行的所有细节，用于排查问题和审计。

## 📁 项目结构

```
CodeAgent/
├── agents/                          # Agent模块
│   ├── bug_detection_agent/         # 缺陷检测Agent
│   ├── code_analysis_agent/         # 代码分析Agent
│   ├── code_quality_agent/          # 代码质量Agent
│   ├── fix_execution_agent/         # 修复执行Agent
│   ├── test_validation_agent/       # 测试验证Agent
│   ├── performance_optimization_agent/ # 性能优化Agent
│   ├── dynamic_detection_agent/     # 动态检测Agent（新增）
│   ├── base_agent.py               # Agent基类
│   └── integrated_detector.py      # 集成检测器
├── coordinator/                     # 协调中心
│   ├── coordinator.py              # 主协调器
│   ├── task_manager.py             # 任务管理器
│   ├── decision_engine.py          # 决策引擎
│   ├── event_bus.py                # 事件总线
│   └── message_types.py            # 消息类型定义
├── api/                            # API接口层（统一入口）
│   ├── main_api.py                 # 主API入口（统一启动点）
│   ├── coordinator_api.py          # Coordinator管理API
│   ├── bug_detection_api.py        # 缺陷检测API
│   ├── code_analysis_api.py        # 代码分析API
│   ├── code_quality_api.py         # 代码质量API
│   ├── dynamic_api.py              # 动态检测API
│   ├── core/                       # 核心管理模块
│   │   ├── agent_manager.py        #   - Agent生命周期管理
│   │   └── coordinator_manager.py  #   - Coordinator管理
│   ├── deepseek_config.py          # DeepSeek配置
│   ├── reports/                    # 检测报告目录
│   ├── structured_data/            # 结构化数据导出
│   ├── uploads/                    # 文件上传目录
│   └── requirements.txt            # API依赖
├── frontend/                       # 前端界面（多页面）
│   ├── index.html                  # 登录页面
│   ├── main.html                   # 主界面
│   ├── analyse.html                # 静态分析页面
│   ├── deep_analysis.html          # 深度分析页面
│   ├── dynamic_detection.html      # 动态检测页面
│   ├── explore.html                # 探索页面
│   ├── login.html                  # 登录表单
│   └── projects.html               # 项目管理页面
├── tools/                          # 工具集成层
│   └── static_analysis/            # 静态分析工具
│       ├── custom_checker.py       #   - 自定义检查器
│       ├── pylint_runner.py        #   - Pylint运行器
│       └── flake8_runner.py        #   - Flake8运行器
├── config/                         # 配置文件
│   ├── settings.py                 # 系统设置
│   └── agent_config.py             # Agent配置
├── docs/                           # 文档
│   ├── Pandas测试指南.md            # Pandas测试详细指南
│   ├── 扩展Bug列表说明.md           # 扩展Bug列表文档
│   ├── workflow_diagram.md         # 工作流程图
│   ├── system_architecture.md      # 系统架构说明
│   ├── implementation_plan.md      # 实施计划
│   ├── API_DOCUMENTATION.md        # API文档
│   └── DEEPSEEK_API_GUIDE.md       # DeepSeek API指南
├── tests/                          # 测试文件和测试数据
│   ├── test_python.py              # Python测试
│   └── pandas-1.0.0/               # Pandas测试数据（需自行下载）
├── utils/                          # 工具函数
│   └── project_runner.py           # 项目运行器
├── extended_bugs.py                # 扩展Bug列表（25个已知Bug）
├── compare_pandas_bugs.py          # Bug对比分析脚本
├── main.py                         # 主程序入口（命令行版本）
├── start_api.py                    # API启动脚本
├── requirements.txt                # 项目依赖
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
- `/api/v1/detection/upload` - 上传文件进行缺陷检测
- `/api/code-quality/analyze-upload` - 代码质量分析
- `/api/code-analysis/analyze-upload` - 代码深度分析
- `/api/dynamic/detect` - 动态检测
- `/api/v1/tasks/{task_id}` - 查询任务状态
- `/api/v1/coordinator/status` - Coordinator状态

## 🚀 快速开始

### 环境要求
- Python 3.8+
- 现代浏览器 (Chrome, Firefox, Safari, Edge)

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd ai_agent_system
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

---

### 📖 系统文档
- [API接口文档](API_DOCUMENTATION.md) - 详细的API使用说明
- [DeepSeek API指南](DEEPSEEK_API_GUIDE.md) - AI分析功能配置指南
- [Agent架构文档](AGENT_DOCUMENTATION.md) - 系统架构和Agent设计

## 🔮 未来扩展

- 支持更多编程语言（Rust, Swift, Kotlin等）
- 集成更多专业检测工具
- 支持自定义检测规则
- 提供代码修复建议
- 支持CI/CD集成

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

### 最新更新（2024年10月）

#### 架构升级
- ✅ 新增 `api/core/` 核心管理层
  - `agent_manager.py`: Agent生命周期管理
  - `coordinator_manager.py`: Coordinator管理
- ✅ API架构模块化重构
  - 5个独立API模块，使用 APIRouter
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
- ✅ 三种分析模式
  - file: 单文件分析
  - project: 项目批量分析
  - dynamic: 动态检测
- ✅ 多页面前端设计
  - 8个专业界面页面
  - 更好的用户体验

#### 工作流优化
- ✅ Coordinator优先启动
  - 确保协调中心先就绪
  - 再启动和注册Agent
- ✅ API路由分发机制
  - 统一入口，模块化路由
  - 清晰的职责划分
- ✅ 任务状态跟踪
  - 实时任务状态查询
  - Agent状态监控

#### 文档更新
- ✅ 更新项目结构说明
- ✅ 更新工作流程图
- ✅ 更新系统架构图
- ✅ 新增实际实现差异说明
- ✅ 完善API文档

---

*最后更新: 2024年10月*
