# 代码分析Agent (Code Analysis Agent)

## 概述

代码分析Agent是一个强大的代码分析工具，提供深层次的代码理解、依赖分析、复杂度评估和AI驱动的项目意图分析。它能够自动分析项目结构、代码质量、依赖关系，并生成结构化的项目信息。

## 主要功能

### 🔍 项目结构分析
- **文件分类**: 自动识别代码文件、配置文件、测试文件、文档文件
- **项目元数据**: 检测项目类型、框架、编程语言
- **文件统计**: 统计文件数量、代码行数、文件类型分布
- **目录结构**: 生成项目文件树结构

### 📊 代码质量分析
- **复杂度评估**: 计算圈复杂度、认知复杂度、嵌套深度
- **可维护性指标**: 基于多个维度计算可维护性分数
- **代码问题检测**: 识别语法错误、代码风格问题、潜在缺陷
- **多语言支持**: 支持Python、JavaScript、TypeScript、Java、C/C++、Go、Rust等

### 🔗 依赖关系分析
- **包管理器支持**: 支持requirements.txt、package.json、Cargo.toml、pom.xml、go.mod
- **导入依赖**: 分析代码中的import/require语句
- **循环依赖检测**: 使用图算法检测循环依赖
- **依赖指标**: 计算依赖耦合度、依赖深度等指标

### 🤖 AI智能分析
- **代码意图理解**: 使用DeepSeek AI分析代码功能和意图
- **项目摘要生成**: 自动生成项目整体分析摘要
- **架构模式识别**: 识别MVC、微服务、分层架构等模式
- **改进建议**: 提供代码优化和重构建议

### 📈 项目意图分析
- **项目类型推断**: 自动识别Web应用、API服务、前端应用等
- **技术栈识别**: 检测使用的框架和库
- **关键特性提取**: 识别数据库集成、用户认证、API接口等特性
- **复杂度等级评估**: 评估项目整体复杂度

## 技术架构

### 核心组件

1. **ProjectAnalyzer**: 项目结构分析器
   - 文件系统遍历
   - 项目元数据提取
   - 文件分类和统计

2. **CodeAnalyzer**: 代码质量分析器
   - AST解析和复杂度计算
   - 多语言代码分析
   - 问题检测和报告

3. **DependencyAnalyzer**: 依赖关系分析器
   - 包管理器文件解析
   - 代码导入分析
   - 图算法循环依赖检测

4. **AIAnalysisService**: AI分析服务
   - DeepSeek API集成
   - 代码意图分析
   - 项目摘要生成

### 数据模型

```python
@dataclass
class CodeComplexityMetrics:
    cyclomatic_complexity: int
    cognitive_complexity: int
    lines_of_code: int
    function_count: int
    class_count: int
    nested_depth: int
    parameter_count: int

@dataclass
class ProjectIntent:
    project_type: str
    main_purpose: str
    key_features: List[str]
    architecture_pattern: str
    technology_stack: List[str]
    complexity_level: str
    maintainability_score: float
```

## API接口

### 基础分析接口
```http
POST /api/code-analysis/analyze
Content-Type: application/json

{
    "project_path": "/path/to/project",
    "analysis_depth": "comprehensive",
    "include_ai_analysis": true,
    "include_dependency_graph": true
}
```

### 文件上传分析
```http
POST /api/code-analysis/analyze-upload
Content-Type: multipart/form-data

files: [file1, file2, ...]
include_ai_analysis: true
analysis_depth: "comprehensive"
```

### 获取分析结果
```http
GET /api/code-analysis/summary/{analysis_id}
GET /api/code-analysis/quality/{analysis_id}
GET /api/code-analysis/dependencies/{analysis_id}
GET /api/code-analysis/ai-analysis/{analysis_id}
```

## 使用方法

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 启动API服务
```bash
python start_code_analysis_api.py
```

### 3. 使用Python API
```python
import asyncio
from agents.code_analysis_agent.agent import CodeAnalysisAgent

async def analyze_project():
    config = {
        'deepseek_api_key': 'your-api-key',
        'ai_analysis_enabled': True
    }
    
    agent = CodeAnalysisAgent(config)
    await agent.start()
    
    result = await agent.analyze_project('/path/to/project')
    
    print(f"项目类型: {result['project_intent']['project_type']}")
    print(f"复杂度等级: {result['project_intent']['complexity_level']}")
    print(f"可维护性分数: {result['project_intent']['maintainability_score']}")
    
    await agent.stop()

# 运行分析
asyncio.run(analyze_project())
```

### 4. 使用前端界面
1. 打开 `frontend/code_analysis.html`
2. 输入项目路径或上传文件
3. 选择分析深度和选项
4. 点击"开始分析"
5. 查看详细分析结果

## 配置选项

### Agent配置
```python
config = {
    'deepseek_api_key': 'your-deepseek-api-key',
    'max_file_size': 10 * 1024 * 1024,  # 10MB
    'supported_languages': ['python', 'javascript', 'typescript', 'java'],
    'ai_analysis_enabled': True
}
```

### 分析深度选项
- **basic**: 基础分析，仅包含文件结构和基本统计
- **standard**: 标准分析，包含代码质量和依赖分析
- **comprehensive**: 全面分析，包含AI分析和项目意图推断

## 输出示例

### 项目结构分析
```json
{
    "project_structure": {
        "files": [...],
        "code_files": [...],
        "test_files": [...],
        "total_lines": 1250,
        "project_metadata": {
            "name": "my-project",
            "type": "python",
            "framework": "fastapi",
            "language": "python"
        }
    }
}
```

### 代码质量分析
```json
{
    "code_quality": {
        "complexity": {
            "main.py": {
                "cyclomatic_complexity": 8,
                "cognitive_complexity": 12,
                "lines_of_code": 150,
                "function_count": 5,
                "class_count": 2
            }
        },
        "overall_metrics": {
            "average_complexity": 6.5,
            "average_maintainability": 78.3,
            "total_issues": 12,
            "error_count": 2,
            "warning_count": 8
        }
    }
}
```

### 项目意图分析
```json
{
    "project_intent": {
        "project_type": "web_application",
        "main_purpose": "API服务开发",
        "key_features": ["RESTful API", "用户认证", "数据库集成"],
        "architecture_pattern": "MVC模式",
        "technology_stack": ["Python", "FastAPI", "SQLAlchemy"],
        "complexity_level": "中等",
        "maintainability_score": 75.5,
        "confidence": 0.85
    }
}
```

## 测试

运行测试脚本验证功能：
```bash
python test_code_analysis_agent.py
```

## 扩展性

### 添加新语言支持
1. 在 `CodeAnalyzer` 中添加新的分析方法
2. 实现对应的AST解析和复杂度计算
3. 更新文件类型检测逻辑

### 添加新的分析指标
1. 扩展 `CodeComplexityMetrics` 数据类
2. 在相应的分析器中实现计算逻辑
3. 更新前端展示界面

### 集成其他AI服务
1. 实现新的AI分析服务类
2. 在 `AIAnalysisService` 中添加新的分析方法
3. 更新配置和API接口

## 性能优化

- **并行分析**: 使用 `asyncio.gather()` 并行执行多个分析任务
- **缓存机制**: 对重复分析的结果进行缓存
- **增量分析**: 只分析变更的文件
- **资源限制**: 限制同时分析的文件数量和大小

## 故障排除

### 常见问题

1. **NetworkX导入错误**
   ```bash
   pip install networkx==3.2.1
   ```

2. **AI分析失败**
   - 检查DeepSeek API密钥是否正确
   - 确认网络连接正常
   - 检查API配额是否充足

3. **文件解析错误**
   - 确认文件编码为UTF-8
   - 检查文件是否损坏
   - 验证文件路径是否正确

### 日志调试
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 贡献指南

1. Fork项目仓库
2. 创建功能分支
3. 提交代码更改
4. 创建Pull Request

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 更新日志

### v2.0.0
- 新增AI智能分析功能
- 增强依赖关系分析
- 添加项目意图推断
- 支持多语言代码分析
- 优化前端界面

### v1.0.0
- 基础项目结构分析
- 简单代码质量检测
- 基本依赖关系分析
