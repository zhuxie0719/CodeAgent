# AI AGENT系统静态检测功能演示

## 概述

本演示展示了AI AGENT系统中静态代码缺陷检测功能的核心能力。通过分析Python代码，系统能够自动识别各种代码质量问题、安全风险和最佳实践违规。

## 文件结构

```
demo/
├── README.md              # 本说明文档
├── demo.py               # 演示脚本主程序
├── static_detector.py    # 静态检测器实现
├── bad_code.py           # 包含各种缺陷的示例代码
├── good_code.py          # 良好代码示例
└── test_guide.md         # 测试指南
```

## 快速开始

### 1. 运行演示程序

```bash
cd ai_agent_system/demo
python demo.py
```

### 2. 选择检测选项

程序会显示交互式菜单，您可以选择：

- **选项1**: 检测坏代码示例 (`bad_code.py`)
- **选项2**: 检测好代码示例 (`good_code.py`) 
- **选项3**: 检测指定文件
- **选项4**: 批量检测目录
- **选项5**: 查看检测规则
- **选项6**: 退出程序

### 3. 查看检测结果

检测完成后，系统会显示：
- 问题总数和严重程度分布
- 详细的问题描述和位置
- 问题类型统计
- 可选的报告保存功能

## 检测能力

### 支持的检测类型

| 检测类型 | 严重程度 | 描述 |
|---------|---------|------|
| 未使用的导入 | ⚠️ Warning | 检测导入但未使用的模块 |
| 硬编码秘密信息 | ❌ Error | 检测密码、API密钥等敏感信息 |
| 不安全的eval使用 | ❌ Error | 检测eval函数的安全风险 |
| 缺少类型注解 | ℹ️ Info | 检测函数参数和返回值类型注解 |
| 过长的函数 | ⚠️ Warning | 检测超过50行的函数 |
| 重复代码 | ⚠️ Warning | 检测相似的代码块 |
| 异常处理不当 | ⚠️ Warning | 检测裸露的except语句 |
| 全局变量使用 | ⚠️ Warning | 检测全局变量的使用 |
| 魔法数字 | ℹ️ Info | 检测硬编码的数字常量 |
| 不安全的文件操作 | ⚠️ Warning | 检测硬编码的文件路径 |
| 缺少文档字符串 | ℹ️ Info | 检测函数和类缺少文档 |
| 命名不规范 | ⚠️ Warning | 检测不符合命名规范的标识符 |
| 未处理的异常 | ⚠️ Warning | 检测可能抛出异常但未处理的代码 |
| 过深的嵌套 | ⚠️ Warning | 检测超过4层的代码嵌套 |
| 不安全的随机数 | ⚠️ Warning | 检测不安全的随机数生成 |
| 内存泄漏风险 | ⚠️ Warning | 检测可能的内存泄漏 |
| 缺少输入验证 | ⚠️ Warning | 检测用户输入处理缺少验证 |
| 代码格式问题 | ℹ️ Info | 检测缩进和格式问题 |
| 死代码 | ℹ️ Info | 检测可能未被使用的代码 |
| 未使用的变量 | ⚠️ Warning | 检测定义但未使用的变量 |

## 示例代码说明

### bad_code.py - 缺陷代码示例

这个文件包含了20种不同类型的代码缺陷，用于演示检测功能：

1. **未使用的导入** - 导入了但未使用的模块
2. **硬编码密码** - 直接在代码中写入敏感信息
3. **不安全的eval使用** - 使用eval函数的安全风险
4. **缺少类型注解** - 函数参数和返回值没有类型提示
5. **过长的函数** - 函数过长，难以维护
6. **重复代码** - 相似的代码块重复出现
7. **异常处理不当** - 使用裸露的except语句
8. **全局变量使用** - 过度使用全局变量
9. **魔法数字** - 硬编码的数字常量
10. **不安全的文件操作** - 硬编码的文件路径
11. **缺少文档字符串** - 函数和类缺少文档说明
12. **命名不规范** - 不符合Python命名规范
13. **未处理的异常** - 可能抛出异常但未处理
14. **过深的嵌套** - 代码嵌套层级过深
15. **不安全的随机数** - 使用不安全的随机数生成
16. **内存泄漏风险** - 可能造成内存泄漏的代码
17. **缺少输入验证** - 用户输入处理缺少验证
18. **代码格式问题** - 缩进和格式不规范
19. **死代码** - 定义了但永远不会被调用的代码
20. **未使用的变量** - 定义了但未使用的变量

### good_code.py - 良好代码示例

这个文件展示了如何编写高质量的Python代码：

- 完整的类型注解
- 详细的文档字符串
- 适当的异常处理
- 安全的编程实践
- 清晰的代码结构
- 良好的命名规范

## 使用方法

### 1. 基本使用

```python
from static_detector import StaticDetector

# 创建检测器实例
detector = StaticDetector()

# 检测文件
issues = detector.detect_issues('your_file.py')

# 生成报告
report = detector.generate_report(issues)
print(report)
```

### 2. 自定义检测规则

```python
# 创建检测器并配置规则
detector = StaticDetector()
detector.rules['unused_imports'] = False  # 禁用未使用导入检测
detector.rules['magic_numbers'] = False   # 禁用魔法数字检测

# 执行检测
issues = detector.detect_issues('your_file.py')
```

### 3. 批量检测

```python
import os

def detect_directory(directory):
    detector = StaticDetector()
    all_issues = []
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                issues = detector.detect_issues(file_path)
                all_issues.extend(issues)
    
    return all_issues
```

## 输出格式

### 控制台输出

```
🔍 代码检测报告
发现 15 个问题

❌ ERROR (3 个)
  • 行 5: 发现硬编码的秘密信息
  • 行 12: 使用了不安全的eval函数
  • 行 25: 使用了不安全的eval函数

⚠️ WARNING (8 个)
  • 行 8: 函数 process_data 的参数 data 缺少类型注解
  • 行 15: 函数 very_long_function 过长 (65 行)，建议拆分
  • 行 45: 发现重复代码，行 15 和行 45
  ...

ℹ️ INFO (4 个)
  • 行 8: 函数 process_data 缺少返回类型注解
  • 行 18: 发现魔法数字，建议定义为常量
  ...
```

### JSON报告格式

```json
[
  {
    "type": "hardcoded_secret",
    "severity": "error",
    "message": "发现硬编码的秘密信息",
    "line": 5,
    "file": ""
  },
  {
    "type": "missing_type_hint",
    "severity": "info",
    "message": "函数 process_data 的参数 data 缺少类型注解",
    "line": 8,
    "file": ""
  }
]
```

## 扩展开发

### 添加新的检测规则

1. 在 `StaticDetector` 类中添加新的检测方法
2. 在 `rules` 字典中添加新规则的开关
3. 在 `detect_issues` 方法中调用新的检测方法

```python
def _check_new_rule(self, tree: ast.AST, content: str):
    """检查新规则"""
    if not self.rules['new_rule']:
        return
    
    # 实现检测逻辑
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # 检测逻辑
            pass
```

### 自定义严重程度

```python
def _check_custom_rule(self, tree: ast.AST):
    """自定义规则检测"""
    # 检测逻辑
    self.issues.append({
        'type': 'custom_rule',
        'severity': 'critical',  # 自定义严重程度
        'message': '自定义问题描述',
        'line': node.lineno,
        'file': ''
    })
```

## 性能考虑

- 检测器使用AST解析，性能较好
- 对于大型文件，建议分批处理
- 可以通过配置规则来平衡检测精度和性能
- 重复代码检测可能较慢，可以禁用

## 限制和注意事项

1. **AST解析限制**: 某些动态代码可能无法正确解析
2. **误报可能**: 某些检测规则可能产生误报
3. **规则覆盖**: 当前规则集可能不覆盖所有代码质量问题
4. **性能影响**: 复杂规则可能影响检测性能

## 故障排除

### 常见问题

1. **文件编码问题**
   ```python
   # 确保文件使用UTF-8编码
   with open(file_path, 'r', encoding='utf-8') as f:
       content = f.read()
   ```

2. **语法错误**
   ```python
   # 检查文件语法是否正确
   try:
       tree = ast.parse(content)
   except SyntaxError as e:
       print(f"语法错误: {e}")
   ```

3. **内存问题**
   ```python
   # 对于大文件，可以分块处理
   if len(content) > 1000000:  # 1MB
       print("文件过大，建议拆分")
   ```

## 贡献指南

欢迎贡献新的检测规则和改进建议：

1. Fork 项目
2. 创建功能分支
3. 添加新的检测规则
4. 编写测试用例
5. 提交 Pull Request

## 许可证

MIT License

## 联系方式

如有问题或建议，请通过以下方式联系：

- 项目Issues: [GitHub Issues](https://github.com/your-repo/issues)
- 邮箱: your-email@example.com
