# AI Agent 代码检测系统 API 文档

## 概述

AI Agent 代码检测系统是一个智能的静态代码分析平台，支持多种编程语言的缺陷检测、项目分析和结构化数据生成。

## 主要功能

### 1. 文件上传和检测
- 支持单文件分析（Python, Java, C/C++, JavaScript, Go等）
- 支持项目压缩包分析（.zip, .tar, .tar.gz等）
- 多种检测工具集成（自定义静态检测、Pylint、Flake8、AI分析）

### 2. 项目分析
- 自动解压项目文件
- 多语言文件扫描
- 批量文件分析
- 结果合并和优先级排序

### 3. 结构化数据生成
- 按优先级分类问题
- 生成修复建议
- 项目结构分析
- 为修复agent提供结构化信息

## API 端点

### 基础信息
- **基础URL**: `http://localhost:8001`
- **API版本**: v1
- **内容类型**: `application/json`

### 1. 健康检查
```http
GET /health
```

**响应示例**:
```json
{
  "status": "healthy",
  "message": "API服务运行正常，Agent状态: running",
  "timestamp": "2025-01-27T10:30:00"
}
```

### 2. 文件上传检测
```http
POST /api/v1/detection/upload
```

**参数**:
- `file`: 上传的文件（multipart/form-data）
- `enable_static`: 启用自定义静态检测（boolean，默认true）
- `enable_pylint`: 启用Pylint检测（boolean，默认true）
- `enable_flake8`: 启用Flake8检测（boolean，默认true）
- `enable_ai_analysis`: 启用AI分析（boolean，默认true）
- `analysis_type`: 分析类型（string，"file"或"project"，默认"file"）

**响应示例**:
```json
{
  "success": true,
  "message": "文件上传成功，开始检测",
  "timestamp": "2025-01-27T10:30:00",
  "data": {
    "task_id": "task_abc123",
    "filename": "example.py",
    "file_size": 1024,
    "agent_id": "bug_detection_agent",
    "analysis_type": "file"
  }
}
```

### 3. 获取任务状态
```http
GET /api/v1/tasks/{task_id}
```

**响应示例**:
```json
{
  "success": true,
  "message": "获取任务状态成功",
  "data": {
    "task_id": "task_abc123",
    "status": "completed",
    "created_at": "2025-01-27T10:30:00",
    "started_at": "2025-01-27T10:30:01",
    "completed_at": "2025-01-27T10:30:05",
    "result": {
      "success": true,
      "detection_results": {
        "file_path": "uploads/example.py",
        "language": "python",
        "total_issues": 5,
        "issues": [
          {
            "type": "unused_import",
            "severity": "warning",
            "message": "未使用的导入",
            "line": 3,
            "file": "example.py",
            "language": "python",
            "code_snippet": [...],
            "fix_suggestions": ["删除未使用的导入语句"]
          }
        ],
        "summary": {
          "error_count": 1,
          "warning_count": 3,
          "info_count": 1
        }
      }
    }
  }
}
```

### 4. 获取AI报告
```http
GET /api/v1/ai-reports/{task_id}
```

**响应示例**:
```json
{
  "success": true,
  "message": "获取AI报告成功",
  "data": {
    "task_id": "task_abc123",
    "ai_report": "# 代码质量检测报告\n\n## 总体评估\n...",
    "report_type": "markdown"
  }
}
```

### 5. 下载AI报告
```http
GET /api/v1/ai-reports/{task_id}/download
```

返回Markdown格式的AI报告文件。

### 6. 下载JSON报告
```http
GET /api/v1/reports/{task_id}
```

返回JSON格式的详细检测报告。

### 7. 获取结构化数据
```http
GET /api/v1/structured-data/{task_id}
```

**响应示例**:
```json
{
  "success": true,
  "message": "获取结构化数据成功",
  "data": {
    "task_id": "task_abc123",
    "file_path": "uploads/example.py",
    "analysis_type": "file",
    "timestamp": "2025-01-27T10:30:00",
    "summary": {
      "total_issues": 5,
      "error_count": 1,
      "warning_count": 3,
      "info_count": 1,
      "languages_detected": ["python"],
      "total_files": 1
    },
    "issues_by_priority": {
      "critical": [],
      "high": [{"type": "security_issue", ...}],
      "medium": [{"type": "unused_import", ...}],
      "low": [{"type": "missing_docstring", ...}]
    },
    "fix_recommendations": {
      "immediate_actions": ["修复 1 个错误级别的问题"],
      "short_term_improvements": ["进行代码审查"],
      "long_term_optimizations": ["建立持续集成流程"]
    },
    "project_structure": {
      "analysis_type": "file",
      "file_count": 1,
      "languages": ["python"],
      "complexity_indicators": {
        "high_issue_files": 0,
        "average_issues_per_file": 5.0
      }
    }
  }
}
```

### 8. 下载结构化数据
```http
GET /api/v1/structured-data/{task_id}/download
```

返回JSON格式的结构化数据文件，供修复agent使用。

## 支持的文件类型

### 单文件分析
- **Python**: .py, .pyw, .pyi
- **Java**: .java
- **C/C++**: .c, .cpp, .h, .hpp, .hxx
- **JavaScript/TypeScript**: .js, .jsx, .ts, .tsx
- **Go**: .go

### 项目分析
- **压缩格式**: .zip, .tar, .tar.gz, .rar, .7z
- **文件大小限制**: 单文件最大10MB，项目最大100MB

## 检测工具

### 1. 自定义静态检测
- 未使用导入检测
- 硬编码密钥检测
- 不安全函数使用检测
- 代码规范检查

### 2. Pylint检测
- 代码质量分析
- 编码规范检查
- 潜在错误检测

### 3. Flake8检测
- 代码风格检查
- 语法错误检测
- 复杂度分析

### 4. AI智能分析
- 使用DeepSeek API进行智能分析
- 多语言支持
- 上下文理解

## 优先级分类

### Critical（关键）
- 安全相关问题
- 可能导致系统崩溃的错误

### High（高）
- 错误级别问题
- 功能性问题

### Medium（中）
- 警告级别问题
- 代码质量问题

### Low（低）
- 信息级别问题
- 代码风格问题

## 错误处理

### 常见错误码
- `400`: 请求参数错误
- `413`: 文件过大
- `404`: 任务或文件不存在
- `500`: 服务器内部错误

### 错误响应格式
```json
{
  "success": false,
  "message": "错误描述",
  "timestamp": "2025-01-27T10:30:00"
}
```

## 使用示例

### 1. 上传Python文件进行分析
```bash
curl -X POST "http://localhost:8001/api/v1/detection/upload?analysis_type=file" \
  -F "file=@example.py" \
  -F "enable_static=true" \
  -F "enable_pylint=true"
```

### 2. 上传项目压缩包进行分析
```bash
curl -X POST "http://localhost:8001/api/v1/detection/upload?analysis_type=project" \
  -F "file=@project.zip" \
  -F "enable_ai_analysis=true"
```

### 3. 获取检测结果
```bash
curl "http://localhost:8001/api/v1/tasks/task_abc123"
```

## 前端集成

系统提供了完整的前端界面，包括：

1. **index.html**: 主上传页面
2. **main.html**: 结果展示页面
3. **analyse.html**: 项目分析页面

前端支持：
- 拖拽上传
- 实时状态更新
- 结果可视化
- 报告下载
- 结构化数据导出

## 部署说明

### 启动服务
```bash
python start_api.py
```

### 访问地址
- API文档: http://localhost:8001/docs
- 前端界面: file:///path/to/frontend/index.html
- 健康检查: http://localhost:8001/health

### 依赖要求
- Python 3.8+
- FastAPI
- Uvicorn
- 相关检测工具（Pylint, Flake8等）

## 注意事项

1. 确保已安装所有依赖的检测工具
2. 大文件分析可能需要较长时间
3. AI分析需要配置DeepSeek API密钥
4. 结构化数据文件存储在`structured_data/`目录
5. 报告文件存储在`reports/`目录