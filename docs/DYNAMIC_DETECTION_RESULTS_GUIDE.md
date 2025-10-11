# 动态检测结果管理指南

## 概述

动态检测结果现在统一保存在 `api/dynamic_detection_results/` 目录下，便于管理和查看。

## 目录结构

```
api/
├── dynamic_detection_results/          # 动态检测结果目录
│   ├── detection_results_20251011_112900.json
│   ├── detection_results_20251011_112904.json
│   ├── detection_results_20251011_113146.json
│   ├── detection_results_20251011_113534.json
│   └── detection_results_20251011_113733.json
├── dynamic_api.py                      # 动态检测API
└── main_api.py                        # 主API服务
```

## API端点

### 1. 列出所有检测结果
```http
GET /api/dynamic/results
```

**响应示例**:
```json
{
  "success": true,
  "message": "获取检测结果列表成功",
  "data": {
    "results": [
      {
        "filename": "detection_results_20251011_113733.json",
        "size": 24843,
        "created_time": "2025-10-11T11:37:33.820156",
        "modified_time": "2025-10-11T11:37:33.820156"
      },
      {
        "filename": "detection_results_20251011_113534.json",
        "size": 20394,
        "created_time": "2025-10-11T11:35:34.123456",
        "modified_time": "2025-10-11T11:35:34.123456"
      }
    ]
  }
}
```

### 2. 获取特定检测结果
```http
GET /api/dynamic/results/{filename}
```

**示例**:
```http
GET /api/dynamic/results/detection_results_20251011_113733.json
```

**响应示例**:
```json
{
  "success": true,
  "message": "获取检测结果成功",
  "data": {
    "static_results": {
      "analysis_type": "static",
      "files_analyzed": 8,
      "issues_found": 1,
      "issues": [
        {
          "file": "security_issues.py",
          "type": "security_issue",
          "severity": "warning",
          "message": "使用了不安全的eval函数",
          "line": 56
        }
      ]
    },
    "dynamic_results": {
      "monitoring_type": "system",
      "result": {
        "metrics": [...],
        "alerts": [...]
      }
    },
    "runtime_results": {
      "success": false,
      "error": "项目执行失败",
      "analysis": {
        "issues": [...]
      }
    },
    "summary": {
      "overall_status": "critical",
      "total_issues": 3,
      "critical_issues": 2,
      "warning_issues": 1,
      "info_issues": 0,
      "issues_by_type": {
        "security_issue": 1,
        "execution_error": 1,
        "runtime_errors": 1
      },
      "recommendations": [
        "发现严重问题，建议立即修复",
        "发现安全问题，建议加强安全防护",
        "项目无法正常运行，请检查代码错误"
      ]
    },
    "project_info": {
      "project_path": "/tmp/project_xxx",
      "files": ["file1.py", "file2.py", ...]
    },
    "timestamp": "2025-10-11T11:37:33.820156"
  }
}
```

## 使用方法

### 1. 通过API访问

#### 列出所有结果
```bash
curl http://localhost:8001/api/dynamic/results
```

#### 获取特定结果
```bash
curl http://localhost:8001/api/dynamic/results/detection_results_20251011_113733.json
```

#### 使用PowerShell
```powershell
# 列出所有结果
Invoke-WebRequest -Uri "http://localhost:8001/api/dynamic/results" -Method GET

# 获取特定结果
Invoke-WebRequest -Uri "http://localhost:8001/api/dynamic/results/detection_results_20251011_113733.json" -Method GET
```

### 2. 直接访问文件

#### 查看文件列表
```bash
# Windows
dir api\dynamic_detection_results\

# Linux/Mac
ls api/dynamic_detection_results/
```

#### 查看文件内容
```bash
# Windows
type api\dynamic_detection_results\detection_results_20251011_113733.json

# Linux/Mac
cat api/dynamic_detection_results/detection_results_20251011_113733.json
```

### 3. 使用Python解析

```python
import json
from pathlib import Path

# 读取检测结果
results_dir = Path("api/dynamic_detection_results")
latest_file = max(results_dir.glob("detection_results_*.json"), key=lambda x: x.stat().st_mtime)

with open(latest_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 显示摘要
summary = data['summary']
print(f"整体状态: {summary['overall_status']}")
print(f"总问题数: {summary['total_issues']}")
print(f"严重问题: {summary['critical_issues']}")
print(f"警告问题: {summary['warning_issues']}")

# 显示问题分类
for issue_type, count in summary['issues_by_type'].items():
    print(f"{issue_type}: {count}个")

# 显示修复建议
for recommendation in summary['recommendations']:
    print(f"- {recommendation}")
```

## 结果文件格式

### 文件命名规则
```
detection_results_YYYYMMDD_HHMMSS.json
```

**示例**:
- `detection_results_20251011_113733.json` - 2025年10月11日 11:37:33 的检测结果

### 文件结构
```json
{
  "static_results": {
    "analysis_type": "static",
    "files_analyzed": 8,
    "issues_found": 1,
    "issues": [...],
    "summary": "静态分析完成"
  },
  "dynamic_results": {
    "monitoring_type": "system",
    "result": {
      "metrics": [...],
      "alerts": [...]
    }
  },
  "runtime_results": {
    "success": true/false,
    "run_result": {...},
    "monitor_result": {...},
    "analysis": {...}
  },
  "summary": {
    "overall_status": "good|info|warning|critical",
    "total_issues": 0,
    "critical_issues": 0,
    "warning_issues": 0,
    "info_issues": 0,
    "issues_by_type": {...},
    "recommendations": [...]
  },
  "project_info": {
    "project_path": "...",
    "files": [...]
  },
  "timestamp": "2025-10-11T11:37:33.820156"
}
```

## 管理操作

### 清理旧结果
```bash
# 删除7天前的文件
find api/dynamic_detection_results/ -name "detection_results_*.json" -mtime +7 -delete

# 删除指定日期的文件
rm api/dynamic_detection_results/detection_results_20251011_*.json
```

### 备份结果
```bash
# 创建备份目录
mkdir -p backups/dynamic_detection_results

# 复制结果文件
cp api/dynamic_detection_results/*.json backups/dynamic_detection_results/

# 压缩备份
tar -czf dynamic_detection_results_backup_$(date +%Y%m%d).tar.gz api/dynamic_detection_results/
```

### 统计信息
```python
import json
from pathlib import Path
from datetime import datetime

def analyze_results():
    results_dir = Path("api/dynamic_detection_results")
    files = list(results_dir.glob("detection_results_*.json"))
    
    print(f"总检测次数: {len(files)}")
    
    total_issues = 0
    critical_issues = 0
    warning_issues = 0
    
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            summary = data.get('summary', {})
            total_issues += summary.get('total_issues', 0)
            critical_issues += summary.get('critical_issues', 0)
            warning_issues += summary.get('warning_issues', 0)
    
    print(f"总问题数: {total_issues}")
    print(f"严重问题: {critical_issues}")
    print(f"警告问题: {warning_issues}")
    
    if files:
        latest_file = max(files, key=lambda x: x.stat().st_mtime)
        print(f"最新检测: {latest_file.name}")

analyze_results()
```

## 故障排除

### 常见问题

1. **文件不存在**
   - 检查文件路径是否正确
   - 确认文件是否在 `dynamic_detection_results` 目录中

2. **编码问题**
   - 使用 `utf-8` 编码读取文件
   - 避免使用 `gbk` 编码

3. **权限问题**
   - 确保有读取文件的权限
   - 检查目录权限

### 调试建议

1. **检查API状态**
   ```bash
   curl http://localhost:8001/api/dynamic/status
   ```

2. **查看文件列表**
   ```bash
   curl http://localhost:8001/api/dynamic/results
   ```

3. **验证文件存在**
   ```bash
   ls -la api/dynamic_detection_results/
   ```

## 最佳实践

1. **定期清理**: 建议定期清理旧的检测结果文件
2. **备份重要结果**: 对重要的检测结果进行备份
3. **监控存储空间**: 注意检测结果文件占用的存储空间
4. **使用API**: 优先使用API接口而不是直接访问文件
5. **错误处理**: 在代码中添加适当的错误处理

---

**更新日期**: 2025年10月11日  
**版本**: 1.0.0  
**目录**: `api/dynamic_detection_results/`
