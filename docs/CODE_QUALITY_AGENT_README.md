# 代码质量分析Agent

## 功能概述

代码质量分析Agent专注于单文件分析，提供全面的代码质量评估和AI驱动的详细报告生成。

## 主要功能

### 1. 代码风格检查
- **行长度检查**: 检查代码行长度，默认限制120字符
- **命名规范检查**: 验证函数名（小写下划线）、类名（大驼峰）、变量名
- **缩进一致性检查**: 检测混合使用制表符和空格
- **注释覆盖率**: 计算注释覆盖率，建议最佳实践
- **导入顺序检查**: 验证导入语句顺序（标准库、第三方库、本地库）

### 2. 质量指标计算
- **基础统计**: 代码行数、注释行数、空白行数
- **结构分析**: 函数数量、类数量、平均函数长度
- **复杂度分析**: 圈复杂度、复杂度评分
- **可维护性评分**: 基于多个因素的综合性评分
- **可读性评分**: 评估代码的可读性水平

### 3. AI质量报告生成
- **总体评分**: 0-100分的综合质量评分
- **等级划分**: A、B、C、D、F五个等级
- **详细评分**: 7个维度的详细评分
  - 代码风格 (15分)
  - 代码结构 (20分)
  - 性能效率 (15分)
  - 安全性 (15分)
  - 可维护性 (15分)
  - 可测试性 (10分)
  - 文档质量 (10分)
- **AI洞察**: 代码优势、改进建议、总体评价

## 使用方法

### 方式一：通过Web界面

1. **启动服务**
   ```bash
   python start_api.py  # 启动API服务器
   ```

2. **上传文件**
   - 打开浏览器访问 `http://localhost:8001`
   - 选择"🤖 AI质量分析"复选框
   - 上传你的代码文件
   - 点击"开始检测"

3. **查看结果**
   - 等待分析完成
   - 在main.html页面底部查看AI质量报告
   - 可以下载或查看详细报告

### 方式二：通过API接口

```python
import requests

# 分析代码文件
response = requests.post(
    "http://localhost:8001/api/code-quality/analyze-file",
    json={
        "file_content": "your_code_here",
        "file_path": "example.py",
        "include_ai_analysis": True
    }
)

result = response.json()
print(f"总体评分: {result['data']['ai_report']['overall_score']}")
```

###  way三：直接使用Agent

```python
import asyncio
from agents.code_quality_agent import CodeQualityAgent

async def analyze_code():
    config = {
        'ai_api_key': 'your-deepseek-api-key',
        'max_line_length': 120
    }
    
    agent = CodeQualityAgent(config)
    await agent.start()
    
    # 分析文件
    result = await agent.analyze_single_file(
        'test.py', 
        'your_code_content'
    )
    
    print(f"评分: {result['ai_report']['overall_score']}")
    print(f"等级: {result['ai_report']['grade']}")

asyncio.run(analyze_code())
```

## 支持的编程语言

- **Python** (.py) - 完整支持
- **JavaScript** (.js) - 基础支持
- **Java** (.java) - 基础支持
- **C/C++** (.c, .cpp, .h) - 基础支持
- **C#** (.cs) - 基础支持

## API接口

### 基础端点
- `GET /api/code-quality/health` - 健康检查
- `GET /api/code-quality/capabilities` - 获取Agent能力
- `GET /api/code-quality/metrics` - 获取Agent指标

### 分析端点
- `POST /api/code-quality/analyze-file` - 分析文件内容
- `POST /api/code-quality/analyze-upload` - 分析上传的文件
- `POST /api/code-quality/analyze-file-path` - 分析文件路径

### 请求示例

```json
{
  "file_content": "def hello():\n    print('Hello World')",
  "file_path": "hello.py",
  "include_ai_analysis": true
}
```

### 响应示例

```json
{
  "success": true,
  "data": {
    "file_path": "hello.py",
    "file_size": 50,
    "analysis_time": "2024-01-01T12:00:00",
    "style_issues": [
      {
        "type": "naming",
        "severity": "warning",
        "line": 1,
        "message": "函数名建议更加描述性",
        "suggestion": "建议使用更具体的函数名"
      }
    ],
    "metrics": {
      "lines_of_code": 2,
      "comment_lines": 0,
      "complexity_score": 2.0,
      "maintainability_score": 8.5
    },
    "ai_report": {
      "overall_score": 85,
      "grade": "B",
      "detailed_scores": {
        "style": 13,
        "structure": 18,
        "performance": 12
      },
      "strengths": ["代码简洁易懂"],
      "suggestions": ["添加注释文档"],
      "summary": "代码质量良好，建议改进文档"
    }
  }
}
```

## 配置选项

```python
config = {
    'ai_api_key': 'your-deepseek-api-key',      # AI分析API密钥
    'ai_base_url': 'https://api.deepseek.com/v1/chat/completions',  # AI API地址
    'max_line_length': 120,                     # 行长度限制
    'max_workers': 1                           # 最大工作线程数
}
```

## 注意事项

1. **AI分析**: 需要有效的DeepSeek API密钥才能使用AI功能
2. **备用报告**: 没有API密钥时会使用基于规则的基础报告
3. **文件大小**: 建议单文件不超过10MB
4. **网络**: AI分析需要网络连接到DeepSeek API

## 测试

运行测试脚本验证功能：

```bash
python test_quality_agent.py    # 测试Agent核心功能
python test_quality_api.py      # 测试API接口（需要服务器运行）
```

## 故障排除

### 常见问题

1. **导入错误**: 确保安装了所有依赖
   ```bash
   pip install -r requirements.txt
   ```

2. **AI分析失败**: 检查API密钥和网络连接

3. **分析结果不准确**: 确保代码文件编码为UTF-8

### 日志信息

Agent会输出详细的日志信息，包括：
- 分析进度
- 错误信息
- 性能指标

## 扩展开发

### 添加新的检查规则

在`quality_checker.py`中的`StyleChecker`类添加新方法：

```python
def _check_new_rule(self, file_content: str) -> List[Dict[str, Any]]:
    """检查新规则"""
    issues = []
    # 实现检查逻辑
    return issues
```

### 添加新的质量指标

在`QualityMetricsCalculator`类中添加新指标：

```python
async def calculate_metrics(self, file_path: str, file_content: str) -> Dict[str, Any]:
    metrics = await super().calculate_metrics(file_path, file_content)
    
    # 添加新指标
    metrics['new_metric'] = self._calculate_new_metric(file_content)
    
    return metrics
```

---

**注意**: 这是一个专注于单文件分析的版本。对于项目级别的分析，建议使用其他分析工具组合。
