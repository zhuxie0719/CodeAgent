# Flask简单测试工具

这是一个用于测试Flask应用的简单工具，支持静态和动态检测。

## 功能特性

- **静态检测**: 基于Flask 2.0.0的已知问题进行代码分析
- **动态检测**: 通过实际运行Flask应用来检测问题
- **多模式支持**: 支持静态、动态或混合检测模式

## 文件说明

- `run_tests.py`: 主运行脚本
- `dynamic_test_runner.py`: 动态检测运行器
- `test_flask_simple.py`: 静态检测运行器
- `flask_app.py`: 示例Flask应用
- `README.md`: 说明文档

## 使用方法

### 基本用法

```bash
# 运行所有检测
python run_tests.py

# 只运行静态检测
python run_tests.py --mode static

# 只运行动态检测
python run_tests.py --mode dynamic

# 指定目标文件或目录
python run_tests.py --target /path/to/flask/app

# 保存结果到文件
python run_tests.py --output results.json
```

### 参数说明

- `--mode`: 检测模式 (static/dynamic/both)
- `--target`: 目标文件或目录路径
- `--output`: 输出文件路径（可选）

## 检测内容

### 静态检测

- Flask 2.0.0 已知问题检测
- 代码质量问题
- 安全问题
- 性能问题

### 动态检测

- Flask应用启动测试
- 路由功能测试
- 错误处理测试
- 性能测试

## 环境要求

- Python 3.6+
- Flask 2.0.0+
- Werkzeug (兼容版本)

## 注意事项

1. 动态检测需要Flask应用能够正常启动
2. 某些Flask版本可能与Werkzeug版本不兼容
3. 检测结果会保存为JSON格式

## 示例输出

```json
{
  "summary": {
    "total_issues": 5,
    "high_severity_issues": 2,
    "flask_issues_count": 3,
    "code_quality_issues_count": 1,
    "security_issues_count": 1,
    "performance_issues_count": 0
  },
  "details": {
    "flask_issues": [...],
    "code_quality": [...],
    "security_issues": [...],
    "performance_issues": [...]
  }
}
```
