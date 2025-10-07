# Fix Execution Agent 集成指南

## 概述

本文档为开发 `fix_execution_agent` 的开发人员提供详细的集成指南，包括缺陷检测的预处理规则、结构化数据格式、数据流和存储机制。

## 1. 缺陷检测预处理规则

### 1.1 检测工具配置

缺陷检测系统集成了多个静态分析工具，每个工具都有特定的配置和规则：

```python
# 工具配置
TOOLS = {
    "pylint": {
        "enabled": True,
        "args": ["--output-format=json", "--disable=C0114,C0116"],
        "severity_mapping": {
            "error": "error",
            "warning": "warning", 
            "convention": "info",
            "refactor": "info"
        }
    },
    "flake8": {
        "enabled": True,
        "args": ["--format=%(path)s:%(row)d:%(col)d: %(code)s %(text)s"],
        "severity_mapping": {
            "E": "error",
            "W": "warning",
            "F": "error",
            "C": "info"
        }
    },
    "bandit": {
        "enabled": True,
        "args": ["-f", "json"],
        "severity_mapping": {
            "HIGH": "error",
            "MEDIUM": "warning",
            "LOW": "info"
        }
    },
    "mypy": {
        "enabled": True,
        "args": ["--show-error-codes", "--no-error-summary"],
        "severity_mapping": {
            "error": "error",
            "note": "info"
        }
    }
}
```

### 1.2 自定义检测规则

系统实现了自定义检测规则，用于检测特定类型的缺陷：

```python
# 自定义检测规则
CUSTOM_RULES = {
    "hardcoded_secrets": {
        "pattern": r'(API_KEY|SECRET|PASSWORD|TOKEN|PRIVATE_KEY|DATABASE_URL)\s*=\s*["\'][^"\']+["\']',
        "severity": "error",
        "category": "security"
    },
    "unsafe_eval": {
        "pattern": r'eval\s*\(',
        "severity": "error", 
        "category": "security"
    },
    "division_by_zero_risk": {
        "pattern": r'/\s*\w+',
        "severity": "warning",
        "category": "reliability"
    },
    "unhandled_exception": {
        "pattern": r'(open\(|json\.loads\(|int\()',
        "severity": "warning",
        "category": "reliability"
    },
    "missing_parameter_validation": {
        "pattern": r'def\s+\w+\s*\(',
        "severity": "info",
        "category": "maintainability"
    }
}
```

### 1.3 语言支持

系统支持多种编程语言的检测：

```python
SUPPORTED_LANGUAGES = {
    "python": {
        "extensions": [".py", ".pyw", ".pyi"],
        "tools": ["pylint", "flake8", "bandit", "mypy", "custom_analyzer"],
        "ai_analysis": True
    },
    "java": {
        "extensions": [".java"],
        "tools": ["spotbugs", "pmd", "checkstyle"],
        "ai_analysis": True
    },
    "c": {
        "extensions": [".c", ".h"],
        "tools": ["cppcheck", "clang-static-analyzer"],
        "ai_analysis": True
    },
    "cpp": {
        "extensions": [".cpp", ".cc", ".cxx", ".hpp", ".hxx"],
        "tools": ["cppcheck", "clang-static-analyzer"],
        "ai_analysis": True
    },
    "javascript": {
        "extensions": [".js", ".jsx", ".ts", ".tsx"],
        "tools": ["eslint", "jshint"],
        "ai_analysis": True
    },
    "go": {
        "extensions": [".go"],
        "tools": ["golangci-lint", "go vet"],
        "ai_analysis": True
    }
}
```

## 2. 结构化检测结果数据格式

### 2.1 核心数据结构

检测结果的核心数据结构如下：

```python
DetectionResult = {
    "project_path": str,           # 项目路径
    "total_files": int,            # 总文件数
    "total_issues": int,           # 总问题数
    "issues": List[Issue],         # 问题列表
    "files": List[FileInfo],       # 文件信息列表
    "detection_tools": List[str],  # 使用的检测工具
    "analysis_time": float,        # 分析时间（秒）
    "summary": {                   # 问题统计
        "error_count": int,
        "warning_count": int,
        "info_count": int
    },
    "languages_detected": List[str], # 检测到的语言
    "enhanced": bool               # 是否经过增强处理
}
```

### 2.2 问题对象结构

每个检测到的问题都有以下结构：

```python
Issue = {
    "type": str,                   # 问题类型
    "severity": str,               # 严重性级别 (error/warning/info)
    "message": str,                # 问题描述
    "line": int,                   # 行号
    "column": int,                 # 列号
    "file": str,                   # 文件名
    "file_path": str,              # 完整文件路径
    "language": str,               # 编程语言
    "rule": str,                   # 规则ID
    "code_snippet": List[CodeLine], # 代码片段
    "detailed_description": str,   # 详细描述
    "fix_suggestions": List[str],  # 修复建议
    "severity_info": {             # 严重性信息
        "level": int,
        "name": str,
        "color": str
    },
    "enhanced": bool               # 是否经过增强处理
}
```

### 2.3 代码片段结构

```python
CodeLine = {
    "line_number": int,            # 行号
    "content": str,                # 代码内容
    "is_issue_line": bool          # 是否为问题行
}
```

### 2.4 文件信息结构

```python
FileInfo = {
    "file": str,                   # 文件名
    "file_path": str,              # 完整路径
    "language": str,               # 编程语言
    "total_issues": int,           # 问题总数
    "issues": List[Issue],         # 该文件的问题列表
    "analysis_time": float         # 分析时间
}
```

## 3. 数据流和存储机制

### 3.1 数据流图

```
[文件上传] → [任务创建] → [缺陷检测] → [结果增强] → [结构化存储] → [API返回]
     ↓              ↓           ↓           ↓            ↓
[文件解压] → [文件扫描] → [工具分析] → [结果合并] → [JSON存储] → [前端显示]
```

### 3.2 存储位置

检测结果存储在以下位置：

```
api/
├── reports/                          # 检测报告存储
│   ├── bug_detection_report_*.json   # 详细检测报告
│   └── ai_report_*.md               # AI分析报告
├── structured_data/                  # 结构化数据存储
│   └── structured_data_*.json       # 结构化检测结果
└── tasks_state.json                 # 任务状态持久化
```

### 3.3 数据存储格式

#### 3.3.1 结构化数据文件 (structured_data_*.json)

```json
{
    "task_id": "task_1234567890ab",
    "file_path": "/path/to/file.py",
    "analysis_type": "file|project",
    "total_issues": 10,
    "issues_by_severity": {
        "error": 4,
        "warning": 3,
        "info": 3
    },
    "issues_by_type": {
        "hardcoded_secrets": 2,
        "unsafe_eval": 1,
        "missing_docstring": 3,
        "unused_import": 4
    },
    "issues_by_category": {
        "security": 3,
        "reliability": 2,
        "maintainability": 5
    },
    "detection_tools_used": ["custom_analyzer", "pylint", "bandit"],
    "analysis_time": 1.234,
    "created_at": "2025-09-28T16:00:00Z",
    "issues": [
        {
            "type": "hardcoded_secrets",
            "severity": "error",
            "message": "发现硬编码的密钥或密码",
            "line": 5,
            "column": 0,
            "file": "config.py",
            "file_path": "/path/to/config.py",
            "language": "python",
            "rule": "hardcoded_secrets",
            "code_snippet": [
                {
                    "line_number": 3,
                    "content": "# 配置文件",
                    "is_issue_line": false
                },
                {
                    "line_number": 4,
                    "content": "",
                    "is_issue_line": false
                },
                {
                    "line_number": 5,
                    "content": "API_KEY = \"sk-1234567890abcdef\"",
                    "is_issue_line": true
                }
            ],
            "detailed_description": "硬编码的密钥、密码或API密钥存在安全风险，可能被恶意用户获取。建议使用环境变量或配置文件。",
            "fix_suggestions": [
                "使用环境变量存储敏感信息",
                "使用配置文件（不提交到版本控制）",
                "使用密钥管理服务"
            ],
            "severity_info": {
                "level": 1,
                "name": "错误",
                "color": "#ff4444"
            },
            "enhanced": true
        }
    ]
}
```

#### 3.3.2 详细检测报告 (bug_detection_report_*.json)

```json
{
    "report_info": {
        "generated_at": "2025-09-28T16:00:00Z",
        "file_path": "/path/to/file.py",
        "total_issues": 10,
        "summary": {
            "error_count": 4,
            "warning_count": 3,
            "info_count": 3
        },
        "detection_tools": ["custom_analyzer", "pylint", "bandit"]
    },
    "issues": [
        // 同结构化数据中的issues格式
    ],
    "files": [
        {
            "file": "config.py",
            "file_path": "/path/to/config.py",
            "language": "python",
            "total_issues": 5,
            "issues": [
                // 该文件的问题列表
            ],
            "analysis_time": 0.5
        }
    ],
    "statistics": {
        "issues_by_severity": {
            "error": 4,
            "warning": 3,
            "info": 3
        },
        "issues_by_type": {
            "hardcoded_secrets": 2,
            "unsafe_eval": 1,
            "missing_docstring": 3,
            "unused_import": 4
        },
        "issues_by_category": {
            "security": 3,
            "reliability": 2,
            "maintainability": 5
        }
    }
}
```

## 4. API接口

### 4.1 获取结构化数据

```http
GET /api/v1/structured-data/{task_id}
```

**响应格式**：
```json
{
    "success": true,
    "message": "获取结构化数据成功",
    "timestamp": "2025-09-28T16:00:00Z",
    "data": {
        // 结构化数据内容
    }
}
```

### 4.2 下载结构化数据

```http
GET /api/v1/structured-data/{task_id}/download
```

**响应**: 直接返回JSON文件下载

### 4.3 获取任务状态

```http
GET /api/v1/tasks/{task_id}
```

**响应格式**：
```json
{
    "success": true,
    "message": "获取任务状态成功",
    "timestamp": "2025-09-28T16:00:00Z",
    "data": {
        "task_id": "task_1234567890ab",
        "status": "completed|running|failed|pending",
        "created_at": "2025-09-28T16:00:00Z",
        "started_at": "2025-09-28T16:00:01Z",
        "completed_at": "2025-09-28T16:00:05Z",
        "result": {
            "detection_results": {
                // 检测结果数据
            }
        },
        "error": null
    }
}
```

## 5. Fix Execution Agent 集成建议

### 5.1 数据获取流程

```python
# 1. 获取任务状态
task_status = await get_task_status(task_id)
if task_status["status"] != "completed":
    return {"error": "任务未完成"}

# 2. 获取结构化数据
structured_data = await get_structured_data(task_id)
issues = structured_data["issues"]

# 3. 按严重性过滤问题
critical_issues = [issue for issue in issues if issue["severity"] == "error"]
```

### 5.2 问题分类处理

```python
# 按问题类型分类
issues_by_type = {}
for issue in issues:
    issue_type = issue["type"]
    if issue_type not in issues_by_type:
        issues_by_type[issue_type] = []
    issues_by_type[issue_type].append(issue)

# 按严重性分类
issues_by_severity = {
    "error": [i for i in issues if i["severity"] == "error"],
    "warning": [i for i in issues if i["severity"] == "warning"],
    "info": [i for i in issues if i["severity"] == "info"]
}
```

### 5.3 修复优先级建议

```python
# 修复优先级排序
PRIORITY_ORDER = {
    "hardcoded_secrets": 1,      # 安全风险最高
    "unsafe_eval": 1,
    "division_by_zero_risk": 2,  # 可靠性问题
    "unhandled_exception": 2,
    "missing_parameter_validation": 3,  # 代码质量
    "missing_docstring": 4,
    "unused_import": 5
}

def get_fix_priority(issue):
    return PRIORITY_ORDER.get(issue["type"], 999)
```

### 5.4 修复建议提取

```python
def extract_fix_suggestions(issue):
    """提取修复建议"""
    suggestions = issue.get("fix_suggestions", [])
    detailed_desc = issue.get("detailed_description", "")
    
    return {
        "suggestions": suggestions,
        "description": detailed_desc,
        "code_snippet": issue.get("code_snippet", []),
        "line_number": issue["line"]
    }
```

## 6. 错误处理

### 6.1 常见错误码

- `404`: 任务不存在或数据文件不存在
- `500`: 服务器内部错误
- `400`: 请求参数错误

### 6.2 重试机制

```python
import asyncio
from typing import Optional

async def get_structured_data_with_retry(task_id: str, max_retries: int = 3) -> Optional[dict]:
    """带重试机制的数据获取"""
    for attempt in range(max_retries):
        try:
            response = await get_structured_data(task_id)
            if response["success"]:
                return response["data"]
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            await asyncio.sleep(2 ** attempt)  # 指数退避
    return None
```

## 7. 性能考虑

### 7.1 数据大小限制

- 单个问题对象: ~2KB
- 单个文件检测结果: ~50KB
- 项目检测结果: ~500KB (100个文件)

### 7.2 缓存策略

```python
# 建议实现本地缓存
CACHE_TTL = 3600  # 1小时
cached_data = {}

def get_cached_data(task_id: str):
    if task_id in cached_data:
        data, timestamp = cached_data[task_id]
        if time.time() - timestamp < CACHE_TTL:
            return data
    return None
```

## 8. 测试建议

### 8.1 单元测试

```python
def test_issue_parsing():
    """测试问题解析"""
    sample_issue = {
        "type": "hardcoded_secrets",
        "severity": "error",
        "message": "发现硬编码的密钥或密码",
        "line": 5,
        "file": "config.py",
        "fix_suggestions": ["使用环境变量"]
    }
    
    # 测试解析逻辑
    assert sample_issue["severity"] == "error"
    assert len(sample_issue["fix_suggestions"]) > 0
```

### 8.2 集成测试

```python
async def test_data_flow():
    """测试数据流"""
    # 1. 创建测试任务
    task_id = await create_test_task()
    
    # 2. 等待任务完成
    await wait_for_completion(task_id)
    
    # 3. 获取结构化数据
    data = await get_structured_data(task_id)
    
    # 4. 验证数据格式
    assert "issues" in data
    assert "total_issues" in data
    assert data["total_issues"] > 0
```

## 9. 总结

本集成指南提供了 `fix_execution_agent` 与缺陷检测系统集成的完整信息。主要要点：

1. **数据结构标准化**: 所有检测结果都遵循统一的数据格式
2. **API接口稳定**: 提供RESTful API获取检测结果
3. **数据持久化**: 结果存储在JSON文件中，支持离线访问
4. **错误处理**: 完善的错误处理和重试机制
5. **性能优化**: 支持缓存和批量处理

通过遵循本指南，`fix_execution_agent` 可以有效地获取和处理缺陷检测结果，实现自动化的代码修复功能。
