# 修复执行Agent使用说明

## 快速开始

### 1. 环境准备

确保已安装必要的依赖：

```bash
# Python格式化工具
pip install black isort autoflake

# JavaScript格式化工具
npm install -g prettier

# Java格式化工具
# 需要安装google-java-format

# Go格式化工具
# 需要安装gofmt和goimports
```

### 2. 启动API服务

```bash
# 启动简化API服务
python api/simple_agent_api.py

# 或者启动完整API服务
python start_api.py
```

### 3. 基本使用

#### 方法1: 直接调用Agent类

```python
import asyncio
from agents.fix_execution_agent.agent import FixExecutionAgent

async def fix_code():
    # 创建Agent
    agent = FixExecutionAgent({"enabled": True})
    
    # 定义问题
    issues = [
        {
            "language": "python",
            "file": "test.py",
            "type": "format",
            "message": "line too long",
            "line": 10
        }
    ]
    
    # 执行修复
    result = await agent.process_issues(issues, "/path/to/project")
    print(f"修复结果: {result}")

# 运行
asyncio.run(fix_code())
```

#### 方法2: 通过API接口

```bash
# 上传文件进行修复
curl -X POST "http://localhost:8001/api/v1/detection/upload" \
  -F "file=@your_code.py" \
  -F "enable_static=true" \
  -F "enable_pylint=true" \
  -F "enable_flake8=true"
```

#### 方法3: 使用测试脚本

```bash
# 运行完整测试
python test_fix_execution_agent.py

# 运行API测试
python test_fix_agent_api.py --file tests/test_python_bad.py
```

## 支持的问题类型

### 格式化问题
- ✅ 缩进问题 (indentation)
- ✅ 空白行问题 (blank line)
- ✅ 行长度问题 (line too long)
- ✅ 尾随空白 (trailing whitespace)
- ✅ 未使用的导入 (unused import)
- ✅ 缺少最终换行符 (missing final newline)

### 支持的语言
- ✅ Python (autoflake + isort + black)
- ✅ JavaScript (prettier)
- ✅ Java (google-java-format)
- ✅ Go (gofmt + goimports)

## 使用示例

### 示例1: 修复Python代码

```python
# 修复前的代码
import os
import sys
import unused_module

def bad_function():
    x=1+2+3+4+5+6+7+8+9+10+11+12+13+14+15+16+17+18+19+20
    return x

# 修复后的代码
import os
import sys


def bad_function():
    x = (
        1
        + 2
        + 3
        + 4
        + 5
        + 6
        + 7
        + 8
        + 9
        + 10
        + 11
        + 12
        + 13
        + 14
        + 15
        + 16
        + 17
        + 18
        + 19
        + 20
    )
    return x
```

### 示例2: 批量修复多个文件

```python
async def batch_fix():
    agent = FixExecutionAgent({})
    
    # 多个文件的问题
    issues = [
        {"language": "python", "file": "file1.py", "type": "format", "message": "line too long"},
        {"language": "python", "file": "file2.py", "type": "format", "message": "unused import"},
        {"language": "javascript", "file": "file3.js", "type": "format", "message": "formatting"}
    ]
    
    result = await agent.process_issues(issues, "/path/to/project")
    print(f"批量修复完成: {result['fixed_issues']}/{result['total_issues']}")
```

## API接口说明

### 1. 上传文件分析

**端点**: `POST /api/v1/detection/upload`

**参数**:
- `file`: 要分析的文件
- `enable_static`: 启用静态分析 (默认: true)
- `enable_pylint`: 启用Pylint检查 (默认: true)
- `enable_flake8`: 启用Flake8检查 (默认: true)
- `enable_ai_analysis`: 启用AI分析 (默认: false)
- `enable_deep_analysis`: 启用深度分析 (默认: false)

**响应**:
```json
{
  "success": true,
  "message": "文件上传成功，开始分析",
  "data": {
    "task_id": "uuid-string"
  }
}
```

### 2. 查询任务状态

**端点**: `GET /api/v1/tasks/{task_id}`

**响应**:
```json
{
  "success": true,
  "data": {
    "task_id": "uuid-string",
    "status": "completed",
    "created_at": "2024-01-01T00:00:00",
    "result": {
      "files_analyzed": 1,
      "issues_found": 5,
      "analysis_type": "basic"
    }
  }
}
```

### 3. 获取AI报告

**端点**: `GET /api/v1/ai-reports/{task_id}`

**响应**:
```json
{
  "success": true,
  "data": {
    "task_id": "uuid-string",
    "report": "# 代码分析AI报告\n\n## 项目概览\n..."
  }
}
```

## 配置选项

### Agent配置

```python
config = {
    "enabled": True,
    "max_file_size": 1024 * 1024,  # 1MB
    "supported_languages": ["python", "javascript", "java", "go"],
    "format_tools": {
        "python": ["autoflake", "isort", "black"],
        "javascript": ["prettier"],
        "java": ["google-java-format"],
        "go": ["gofmt", "goimports"]
    }
}
```

### 问题分类配置

```python
# 格式化问题关键词
format_keywords = [
    "indentation", "whitespace", "line too long",
    "missing blank line", "too many blank lines",
    "trailing whitespace", "unused import",
    "missing final newline"
]

# 安全问题关键词
security_keywords = [
    "security", "vulnerability", "injection",
    "xss", "csrf", "authentication", "authorization"
]
```

## 最佳实践

### 1. 测试前备份

```python
import shutil

# 备份原始文件
shutil.copy2("original.py", "original.py.backup")

# 执行修复
result = await agent.process_issues(issues, project_path)

# 如果修复失败，恢复备份
if not result['success']:
    shutil.copy2("original.py.backup", "original.py")
```

### 2. 渐进式修复

```python
# 先修复简单问题
simple_issues = [issue for issue in issues if issue['type'] == 'format']
result = await agent.process_issues(simple_issues, project_path)

# 再修复复杂问题
complex_issues = [issue for issue in issues if issue['type'] != 'format']
result = await agent.process_issues(complex_issues, project_path)
```

### 3. 结果验证

```python
def verify_fix(file_path):
    """验证修复结果"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # 检查语法
    try:
        compile(content, file_path, 'exec')
        print("✅ 语法检查通过")
    except SyntaxError as e:
        print(f"❌ 语法错误: {e}")
        return False
    
    # 检查格式化
    if len(max(content.split('\n'), key=len)) > 88:
        print("⚠️ 仍有长行")
    
    return True
```

## 故障排除

### 常见问题

1. **工具未安装**
   ```
   错误: Command 'black' not found
   解决: pip install black isort autoflake
   ```

2. **权限问题**
   ```
   错误: Permission denied
   解决: 确保有文件写入权限
   ```

3. **API连接失败**
   ```
   错误: Connection refused
   解决: 检查API服务是否启动
   ```

### 调试技巧

1. **启用详细日志**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **检查修复前后对比**
   ```python
   def show_diff(before, after):
       print("修复前:")
       print(before)
       print("\n修复后:")
       print(after)
   ```

3. **逐步调试**
   ```python
   # 只修复特定文件
   issues = [issue for issue in all_issues if issue['file'] == 'target.py']
   result = await agent.process_issues(issues, project_path)
   ```

## 性能优化

### 1. 批量处理

```python
# 按语言分组处理
languages = {}
for issue in issues:
    lang = issue['language']
    if lang not in languages:
        languages[lang] = []
    languages[lang].append(issue)

# 并行处理不同语言
for lang, lang_issues in languages.items():
    await agent.process_issues(lang_issues, project_path)
```

### 2. 缓存结果

```python
import hashlib

def get_file_hash(file_path):
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

# 检查文件是否已修复
file_hash = get_file_hash(file_path)
if file_hash in fixed_files_cache:
    print("文件已修复，跳过")
    continue
```

## 扩展功能

### 1. 自定义修复规则

```python
class CustomFixer(CodeFixer):
    def _apply_custom_fixes(self, content, issue):
        # 自定义修复逻辑
        if issue['type'] == 'custom_rule':
            # 应用自定义修复
            pass
        return content
```

### 2. 集成到CI/CD

```yaml
# .github/workflows/code-fix.yml
name: Auto Fix Code
on: [push, pull_request]
jobs:
  fix:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Fix Agent
        run: |
          python test_fix_execution_agent.py
```

## 总结

修复执行Agent提供了强大的代码自动修复功能，支持多种编程语言和问题类型。通过合理使用，可以：

1. 自动修复代码格式问题
2. 提高代码质量和一致性
3. 减少手动修复工作量
4. 集成到开发流程中

建议从简单的测试用例开始，逐步扩展到实际项目使用。


