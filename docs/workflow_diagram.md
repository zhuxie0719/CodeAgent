# AI Agent 工作流程图

## 系统启动流程图

```mermaid
flowchart TD
    START([启动 start_api.py]) --> MAIN[main_api.py 启动]
    
    MAIN --> COORD[1. 启动 CoordinatorManager]
    COORD --> COORD_SUB[启动 Coordinator 核心组件]
    COORD_SUB --> TM[TaskManager 任务管理器]
    COORD_SUB --> EB[EventBus 事件总线]
    COORD_SUB --> DE[DecisionEngine 决策引擎]
    
    TM --> AGENT_MGR[2. 启动 AgentManager]
    EB --> AGENT_MGR
    DE --> AGENT_MGR
    
    AGENT_MGR --> REG[注册所有 Agent 到 Coordinator]
    REG --> BDA[BugDetectionAgent]
    REG --> FEA[FixExecutionAgent]
    REG --> CAA[CodeAnalysisAgent]
    REG --> CQA[CodeQualityAgent]
    REG --> DDA[DynamicDetectionAgent]
    
    BDA --> MOUNT[3. 挂载 API 路由]
    FEA --> MOUNT
    CAA --> MOUNT
    CQA --> MOUNT
    DDA --> MOUNT
    
    MOUNT --> API1[coordinator_api]
    MOUNT --> API2[bug_detection_api]
    MOUNT --> API3[code_quality_api]
    MOUNT --> API4[code_analysis_api]
    MOUNT --> API5[dynamic_api]
    
    API1 --> READY[系统启动完成]
    API2 --> READY
    API3 --> READY
    API4 --> READY
    API5 --> READY
    
    READY --> LISTEN[监听 0.0.0.0:8001]
    
    style START fill:#e1f5fe
    style READY fill:#e8f5e8
    style LISTEN fill:#e8f5e8
    style COORD fill:#fff3e0
    style AGENT_MGR fill:#fff3e0
    style MOUNT fill:#fff3e0
```

## 完整工作流程图（用户请求处理）

```mermaid
flowchart TD
    START([用户请求]) --> FRONTEND[前端界面]
    
    FRONTEND -->|选择模式| MODE{分析模式}
    
    MODE -->|静态分析| STATIC_PAGE[analyse.html]
    MODE -->|深度分析| DEEP_PAGE[deep_analysis.html]
    MODE -->|动态检测| DYNAMIC_PAGE[dynamic_detection.html]
    
    STATIC_PAGE --> UPLOAD[上传文件/项目]
    DEEP_PAGE --> UPLOAD
    DYNAMIC_PAGE --> UPLOAD_DYN[上传项目+配置]
    
    UPLOAD --> API_ROUTE{API路由分发}
    UPLOAD_DYN --> API_DYN[dynamic_api]
    
    API_ROUTE -->|缺陷检测| BUG_API[bug_detection_api]
    API_ROUTE -->|代码质量| QUALITY_API[code_quality_api]
    API_ROUTE -->|代码分析| ANALYSIS_API[code_analysis_api]
    
    BUG_API --> COORD[Coordinator协调中心]
    QUALITY_API --> COORD
    ANALYSIS_API --> COORD
    API_DYN --> COORD
    
    COORD --> TASK_MGR[TaskManager创建任务]
    TASK_MGR --> AGENT_ASSIGN{Agent分配}
    
    AGENT_ASSIGN -->|缺陷检测任务| BDA[BugDetectionAgent]
    AGENT_ASSIGN -->|质量分析任务| CQA[CodeQualityAgent]
    AGENT_ASSIGN -->|深度分析任务| CAA[CodeAnalysisAgent]
    AGENT_ASSIGN -->|动态检测任务| DDA[DynamicDetectionAgent]
    
    BDA --> DETECT[执行检测]
    CQA --> DETECT
    CAA --> DETECT
    DDA --> DYN_DETECT[动态检测执行]
    
    DETECT --> STATIC{静态检测}
    DETECT --> AI{AI分析}
    
    STATIC -->|Python| PYTHON_TOOLS[Pylint + Flake8 + Bandit + Mypy]
    STATIC -->|其他语言| AI_ANALYSIS[AI智能分析]
    
    DYN_DETECT --> RUN_PROJECT[运行项目]
    DYN_DETECT --> MONITOR[监控运行时行为]
    
    AI --> DEEPSEEK[DeepSeek API分析]
    
    PYTHON_TOOLS --> ISSUES[生成缺陷清单]
    AI_ANALYSIS --> ISSUES
    DEEPSEEK --> ISSUES
    RUN_PROJECT --> DYN_ISSUES[动态检测结果]
    MONITOR --> DYN_ISSUES
    
    ISSUES --> REPORT[生成报告]
    DYN_ISSUES --> REPORT
    
    REPORT --> JSON[JSON格式报告]
    REPORT --> MD[Markdown AI报告]
    REPORT --> STRUCT[结构化数据]
    
    JSON --> RETURN[返回结果给前端]
    MD --> RETURN
    STRUCT --> RETURN
    
    RETURN --> DISPLAY[前端展示结果]
    DISPLAY --> END([流程结束])
    
    style START fill:#e1f5fe
    style END fill:#e8f5e8
    style COORD fill:#fff3e0
    style TASK_MGR fill:#fff3e0
    style AGENT_ASSIGN fill:#fff3e0
    style REPORT fill:#e8f5e8
```

## 详细工作流说明

### 阶段1: 系统启动（Coordinator 优先）
1. **启动 CoordinatorManager**:
   - 初始化 Coordinator（协调中心）
   - 启动 TaskManager（任务管理器）
   - 启动 EventBus（事件总线）
   - 启动 DecisionEngine（决策引擎）
2. **启动 AgentManager**:
   - 创建并启动所有 Agent
   - 将 Agent 注册到 Coordinator
3. **挂载 API 路由**:
   - coordinator_api（任务状态、Agent 管理）
   - bug_detection_api（缺陷检测）
   - code_quality_api（代码质量分析）
   - code_analysis_api（代码深度分析）
   - dynamic_api（动态检测）

### 阶段2: 用户请求处理
1. **前端选择分析模式**:
   - 静态分析（analyse.html）
   - 深度分析（deep_analysis.html）
   - 动态检测（dynamic_detection.html）
2. **上传文件/项目**: 支持单文件、压缩包、项目目录
3. **API 路由分发**: 根据分析类型路由到相应的 API 模块

### 阶段3: Coordinator 任务协调
1. **接收 API 请求**: 各 API 模块将请求转发给 Coordinator
2. **TaskManager 创建任务**: 
   - 生成唯一 task_id
   - 设置任务类型和优先级
   - 存储任务状态
3. **Agent 分配**: 根据任务类型分配给相应的 Agent

### 阶段4: Agent 执行任务
1. **BugDetectionAgent** (缺陷检测):
   - Python: Pylint + Flake8 + Bandit + Mypy + 自定义检测器
   - 其他语言: AI智能分析
   - 生成缺陷清单和 AI 报告
2. **CodeQualityAgent** (代码质量):
   - 代码质量评分
   - 复杂度分析
   - 风格检查
3. **CodeAnalysisAgent** (深度分析):
   - 代码结构分析
   - 依赖关系分析
   - 架构模式识别
4. **DynamicDetectionAgent** (动态检测):
   - 运行项目
   - 监控运行时行为
   - 分析性能指标

### 阶段5: 结果生成与返回
1. **生成多格式报告**:
   - JSON 格式（完整检测结果）
   - Markdown AI 报告（自然语言分析）
   - 结构化数据（用于进一步分析）
2. **返回结果**: 
   - 通过 Coordinator 返回给 API
   - API 返回给前端
3. **前端展示**: 
   - 可视化展示检测结果
   - 提供下载选项

## 关键决策点

### 1. 缺陷复杂度判断
```mermaid
flowchart LR
    ISSUE[检测到缺陷] --> TYPE{缺陷类型}
    TYPE -->|语法错误| SIMPLE[简单修复]
    TYPE -->|逻辑错误| COMPLEX[复杂修复]
    TYPE -->|安全漏洞| COMPLEX
    TYPE -->|性能问题| COMPLEX
    SIMPLE --> AUTO[自动修复]
    COMPLEX --> AI[AI分析]
```

### 2. 修复策略选择
```mermaid
flowchart TD
    STRATEGY[修复策略选择] --> RULE{是否有预设规则}
    RULE -->|有| APPLY[应用预设规则]
    RULE -->|无| AI_GEN[AI生成方案]
    AI_GEN --> CONFIRM{需要人工确认?}
    CONFIRM -->|是| HUMAN[人工确认]
    CONFIRM -->|否| AUTO[自动执行]
    HUMAN --> AUTO
    APPLY --> AUTO
```

### 3. 验证策略
```mermaid
flowchart TD
    VALIDATE[验证策略] --> TEST_TYPE{测试类型}
    TEST_TYPE -->|单元测试| JUNIT[JUnit测试]
    TEST_TYPE -->|API测试| POSTMAN[Postman测试]
    TEST_TYPE -->|集成测试| SELENIUM[Selenium测试]
    JUNIT --> RESULT[测试结果]
    POSTMAN --> RESULT
    SELENIUM --> RESULT
    RESULT --> PASS{是否通过}
    PASS -->|是| SUCCESS[修复成功]
    PASS -->|否| FAIL[修复失败]
```

## 错误处理与重试机制

### 1. 检测失败处理
- 工具不可用: 自动切换到备用工具
- AI分析失败: 降级到传统分析
- 网络超时: 自动重试机制

### 2. 修复失败处理
- 自动修复失败: 回滚到原始状态
- 验证失败: 返回决策引擎重新分析
- 多次失败: 标记为需要人工干预

### 3. 系统异常处理
- Agent崩溃: 自动重启和任务转移
- 资源不足: 动态调整并发数
- 存储空间: 自动清理临时文件
