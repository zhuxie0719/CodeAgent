# AI Agent 工作流程图

## 完整工作流程图

```mermaid
flowchart TD
    START([项目接入]) --> UPLOAD{项目类型}
    
    UPLOAD -->|单文件| SINGLE[单文件分析]
    UPLOAD -->|项目包| PROJECT[项目解压扫描]
    
    SINGLE --> DETECT[缺陷检测Agent启动]
    PROJECT --> SCAN[文件扫描分类]
    SCAN --> DETECT
    
    DETECT --> STATIC{静态检测}
    DETECT --> DYNAMIC{动态检测}
    DETECT --> AI{AI分析}
    
    STATIC -->|Python| PYTHON_TOOLS[Pylint + Flake8 + 自定义]
    STATIC -->|其他语言| AI_ANALYSIS[AI智能分析]
    
    DYNAMIC --> JMETER[JMeter压力测试]
    DYNAMIC --> LOG_ANALYSIS[日志分析]
    
    AI --> DEEPSEEK[DeepSeek API分析]
    
    PYTHON_TOOLS --> ISSUES[生成缺陷清单]
    AI_ANALYSIS --> ISSUES
    JMETER --> ISSUES
    LOG_ANALYSIS --> ISSUES
    DEEPSEEK --> ISSUES
    
    ISSUES --> DECISION[决策Agent调用]
    
    DECISION --> COMPLEXITY{缺陷复杂度判断}
    
    COMPLEXITY -->|简单缺陷| SIMPLE[执行预设修复规则]
    COMPLEXITY -->|复杂缺陷| COMPLEX[调用大模型生成修复方案]
    
    SIMPLE --> AUTO_FIX[自动修复执行]
    COMPLEX --> HUMAN_CONFIRM[人工确认修复方案]
    HUMAN_CONFIRM --> AUTO_FIX
    
    AUTO_FIX --> VALIDATE[测试验证Agent]
    
    VALIDATE --> JUNIT_TEST[JUnit单元测试]
    VALIDATE --> POSTMAN_TEST[Postman API测试]
    VALIDATE --> SELENIUM_TEST[Selenium集成测试]
    
    JUNIT_TEST --> VERIFY{验证结果}
    POSTMAN_TEST --> VERIFY
    SELENIUM_TEST --> VERIFY
    
    VERIFY -->|验证通过| SUCCESS[提交修复代码]
    VERIFY -->|验证失败| RETRY[返回决策Agent重新调整]
    
    SUCCESS --> GIT[提交到Git仓库]
    SUCCESS --> UPDATE[更新缺陷状态]
    SUCCESS --> REPORT[生成量化报告]
    
    RETRY --> COMPLEXITY
    
    GIT --> MONITOR[监控Agent持续监控]
    UPDATE --> MONITOR
    REPORT --> MONITOR
    
    MONITOR --> LEARN[学习Agent分析]
    LEARN --> OPTIMIZE[优化建议]
    OPTIMIZE --> END([流程结束])
    
    style START fill:#e1f5fe
    style END fill:#e8f5e8
    style DECISION fill:#fff3e0
    style COMPLEXITY fill:#fff3e0
    style VERIFY fill:#fff3e0
    style SUCCESS fill:#e8f5e8
    style RETRY fill:#ffebee
```

## 详细工作流说明

### 阶段1: 项目接入与预处理
1. **项目接入**: 支持单文件和项目包上传
2. **文件扫描**: 自动识别编程语言和文件类型
3. **预处理**: 解压、分类、过滤大文件

### 阶段2: 多维度缺陷检测
1. **静态检测**: 
   - Python: Pylint + Flake8 + 自定义检测器
   - 其他语言: AI智能分析
2. **动态检测**: JMeter压力测试 + 日志分析
3. **AI分析**: DeepSeek API深度分析

### 阶段3: 智能决策与修复
1. **缺陷分类**: 按复杂度和类型分类
2. **修复策略选择**:
   - 简单缺陷: 自动执行预设规则
   - 复杂缺陷: AI生成方案 + 人工确认
3. **修复执行**: 自动应用修复方案

### 阶段4: 验证与反馈
1. **多维度验证**:
   - 单元测试 (JUnit)
   - API测试 (Postman)
   - 集成测试 (Selenium)
2. **结果处理**:
   - 验证通过: 提交代码，更新状态
   - 验证失败: 返回重新调整

### 阶段5: 持续监控与学习
1. **监控**: 持续监控系统状态
2. **学习**: 从历史数据中学习优化
3. **报告**: 生成量化分析报告

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
