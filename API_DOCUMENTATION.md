# API接口文档

## 概述

AI Agent 多语言代码检测系统提供RESTful API接口，支持单文件和项目级别的代码缺陷检测。

## 基础信息

- **Base URL**: `http://localhost:8001`
- **API版本**: v1
- **数据格式**: JSON
- **认证方式**: 无需认证

## 通用响应格式

### 成功响应
```json
{
  "success": true,
  "message": "操作成功",
  "timestamp": "2024-01-01T12:00:00Z",
  "data": {
    // 具体数据
  }
}
```

### 错误响应
```json
{
  "success": false,
  "message": "错误描述",
  "timestamp": "2024-01-01T12:00:00Z",
  "data": null
}
```

## 接口列表

### 1. 健康检查

**GET** `/health`

检查API服务状态。

#### 响应示例
```json
{
  "status": "healthy",
  "message": "API服务运行正常，Agent状态: running",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 2. 文件上传检测

**POST** `/api/v1/detection/upload`

上传文件进行缺陷检测。

#### 请求参数

**Form Data:**
- `file` (file, required): 要检测的文件
- `enable_static` (boolean, optional): 启用自定义静态检测，默认true
- `enable_pylint` (boolean, optional): 启用Pylint检测，默认true
- `enable_flake8` (boolean, optional): 启用Flake8检测，默认true
- `enable_ai_analysis` (boolean, optional): 启用AI分析，默认true
- `analysis_type` (string, optional): 分析类型，`file`或`project`，默认`file`

#### 支持的文件类型

**单文件分析:**
- Python: `.py`, `.pyw`, `.pyi`
- Java: `.java`
- C/C++: `.c`, `.cpp`, `.cc`, `.cxx`, `.h`, `.hpp`, `.hxx`
- JavaScript/TypeScript: `.js`, `.jsx`, `.ts`, `.tsx`
- Go: `.go`

**项目分析:**
- 压缩文件: `.zip`, `.tar`, `.tar.gz`, `.rar`, `.7z`

#### 文件大小限制
- 单文件: 最大10MB
- 项目文件: 最大100MB

#### 响应示例
```json
{
  "success": true,
  "message": "文件上传成功，开始检测",
  "timestamp": "2024-01-01T12:00:00Z",
  "data": {
    "task_id": "task_abc123def456",
    "filename": "test.py",
    "file_size": 1024,
    "agent_id": "bug_detection_agent"
  }
}
```

### 3. 获取任务状态

**GET** `/api/v1/tasks/{task_id}`

获取检测任务的状态和结果。

#### 路径参数
- `task_id` (string, required): 任务ID

#### 响应示例
```json
{
  "success": true,
  "message": "获取任务状态成功",
  "timestamp": "2024-01-01T12:00:00Z",
  "data": {
    "task_id": "task_abc123def456",
    "status": "completed",
    "created_at": "2024-01-01T12:00:00Z",
    "started_at": "2024-01-01T12:00:01Z",
    "completed_at": "2024-01-01T12:00:05Z",
    "result": {
      "success": true,
      "detection_results": {
        "file_path": "test.py",
        "language": "python",
        "total_issues": 2,
        "issues": [
          {
            "type": "unused_import",
            "severity": "warning",
            "message": "未使用的导入",
            "line": 1,
            "column": 0,
            "file": "test.py",
            "language": "python",
            "code_snippet": [
              "import os",
              "import sys",
              "import unused_module  # 未使用的导入"
            ],
            "detailed_description": "检测到未使用的导入语句，建议删除以提高代码质量。",
            "fix_suggestions": [
              "删除未使用的导入语句",
              "检查是否真的不需要这个模块"
            ]
          }
        ],
        "detection_tools": ["static_detector", "pylint", "flake8"],
        "analysis_time": 2.5,
        "summary": {
          "error_count": 0,
          "warning_count": 1,
          "info_count": 0
        }
      }
    },
    "error": null
  }
}
```

### 4. 下载JSON报告

**GET** `/api/v1/reports/{task_id}`

下载检测结果的JSON格式报告。

#### 路径参数
- `task_id` (string, required): 任务ID

#### 响应
返回JSON格式的检测报告文件。

### 5. 获取AI报告

**GET** `/api/v1/ai-reports/{task_id}`

获取AI生成的自然语言分析报告。

#### 路径参数
- `task_id` (string, required): 任务ID

#### 响应示例
```json
{
  "success": true,
  "message": "获取AI报告成功",
  "timestamp": "2024-01-01T12:00:00Z",
  "data": {
    "task_id": "task_abc123def456",
    "ai_report": "# 代码质量检测报告\n\n## 总体评估\n根据静态代码分析结果，您的代码整体质量良好...",
    "generated_at": "2024-01-01T12:00:05Z"
  }
}
```

### 6. 下载AI报告

**GET** `/api/v1/ai-reports/{task_id}/download`

下载AI报告的Markdown文件。

#### 路径参数
- `task_id` (string, required): 任务ID

#### 响应
返回Markdown格式的AI报告文件。

## 任务状态说明

| 状态 | 描述 |
|------|------|
| `pending` | 任务已创建，等待处理 |
| `processing` | 任务正在处理中 |
| `completed` | 任务已完成 |
| `failed` | 任务处理失败 |

## 错误码说明

| HTTP状态码 | 描述 |
|------------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 413 | 文件过大 |
| 500 | 服务器内部错误 |

## 使用示例

### Python示例

```python
import requests
import time

# 1. 上传文件
files = {'file': open('test.py', 'rb')}
data = {
    'enable_static': 'true',
    'enable_pylint': 'true',
    'enable_flake8': 'true',
    'enable_ai_analysis': 'true',
    'analysis_type': 'file'
}

response = requests.post(
    'http://localhost:8001/api/v1/detection/upload',
    files=files,
    data=data
)

result = response.json()
task_id = result['data']['task_id']

# 2. 轮询任务状态
while True:
    response = requests.get(f'http://localhost:8001/api/v1/tasks/{task_id}')
    task_status = response.json()
    
    if task_status['data']['status'] == 'completed':
        print("检测完成！")
        print(task_status['data']['result'])
        break
    elif task_status['data']['status'] == 'failed':
        print("检测失败！")
        break
    
    time.sleep(1)

# 3. 获取AI报告
response = requests.get(f'http://localhost:8001/api/v1/ai-reports/{task_id}')
ai_report = response.json()
print(ai_report['data']['ai_report'])
```

### JavaScript示例

```javascript
// 1. 上传文件
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('enable_static', 'true');
formData.append('enable_pylint', 'true');
formData.append('enable_flake8', 'true');
formData.append('enable_ai_analysis', 'true');
formData.append('analysis_type', 'file');

const uploadResponse = await fetch('http://localhost:8001/api/v1/detection/upload', {
    method: 'POST',
    body: formData
});

const uploadResult = await uploadResponse.json();
const taskId = uploadResult.data.task_id;

// 2. 轮询任务状态
const pollStatus = async () => {
    const response = await fetch(`http://localhost:8001/api/v1/tasks/${taskId}`);
    const taskStatus = await response.json();
    
    if (taskStatus.data.status === 'completed') {
        console.log('检测完成！', taskStatus.data.result);
        return taskStatus.data.result;
    } else if (taskStatus.data.status === 'failed') {
        console.log('检测失败！');
        return null;
    } else {
        // 继续轮询
        setTimeout(pollStatus, 1000);
    }
};

// 3. 获取AI报告
const getAIReport = async () => {
    const response = await fetch(`http://localhost:8001/api/v1/ai-reports/${taskId}`);
    const aiReport = await response.json();
    console.log(aiReport.data.ai_report);
};
```

### cURL示例

```bash
# 1. 上传文件
curl -X POST "http://localhost:8001/api/v1/detection/upload" \
  -F "file=@test.py" \
  -F "enable_static=true" \
  -F "enable_pylint=true" \
  -F "enable_flake8=true" \
  -F "enable_ai_analysis=true" \
  -F "analysis_type=file"

# 2. 获取任务状态
curl "http://localhost:8001/api/v1/tasks/task_abc123def456"

# 3. 获取AI报告
curl "http://localhost:8001/api/v1/ai-reports/task_abc123def456"

# 4. 下载JSON报告
curl "http://localhost:8001/api/v1/reports/task_abc123def456" -o report.json

# 5. 下载AI报告
curl "http://localhost:8001/api/v1/ai-reports/task_abc123def456/download" -o ai_report.md
```

## 注意事项

1. **文件大小限制**: 单文件最大10MB，项目文件最大100MB
2. **支持格式**: 确保上传的文件格式在支持列表中
3. **任务超时**: 大型项目分析可能需要较长时间，建议设置合理的超时时间
4. **并发限制**: 建议控制并发请求数量，避免服务器过载
5. **错误处理**: 请妥善处理API返回的错误信息

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 支持单文件和项目分析
- 集成AI智能分析
- 支持多语言代码检测

