# 测试指南

## 测试环境准备

### 1. 环境要求

- Python 3.8+
- 无额外依赖包（仅使用标准库）

### 2. 文件准备

确保以下文件存在：
- `demo.py` - 主演示程序
- `static_detector.py` - 检测器实现
- `bad_code.py` - 缺陷代码示例
- `good_code.py` - 良好代码示例

## 测试步骤

### 步骤1: 基本功能测试

1. **运行演示程序**
   ```bash
   python demo.py
   ```

2. **测试选项1 - 检测坏代码**
   - 选择选项 `1`
   - 观察检测结果
   - 验证是否检测到预期的问题

3. **测试选项2 - 检测好代码**
   - 选择选项 `2`
   - 观察检测结果
   - 验证是否检测到较少问题

### 步骤2: 功能验证测试

#### 2.1 检测规则验证

对 `bad_code.py` 进行检测，验证以下规则是否被正确识别：

| 行号 | 问题类型 | 预期结果 |
|------|----------|----------|
| 5 | 硬编码密码 | ERROR |
| 12 | 不安全的eval | ERROR |
| 8 | 缺少类型注解 | INFO |
| 15 | 过长的函数 | WARNING |
| 45 | 重复代码 | WARNING |
| 35 | 异常处理不当 | WARNING |
| 50 | 全局变量使用 | WARNING |
| 55 | 魔法数字 | INFO |
| 60 | 硬编码文件路径 | WARNING |
| 65 | 缺少文档字符串 | INFO |
| 70 | 命名不规范 | WARNING |
| 75 | 未处理的异常 | WARNING |
| 80 | 过深的嵌套 | WARNING |
| 85 | 不安全的随机数 | WARNING |
| 90 | 内存泄漏风险 | WARNING |
| 95 | 缺少输入验证 | WARNING |
| 100 | 代码格式问题 | INFO |
| 105 | 死代码 | INFO |
| 110 | 未使用的变量 | WARNING |

#### 2.2 检测精度测试

1. **误报测试**
   - 检测 `good_code.py`
   - 验证是否产生误报
   - 记录误报情况

2. **漏报测试**
   - 手动检查 `bad_code.py`
   - 验证是否有问题未被检测到
   - 记录漏报情况

### 步骤3: 性能测试

#### 3.1 单文件性能测试

```python
import time
from static_detector import StaticDetector

def performance_test():
    detector = StaticDetector()
    
    # 测试不同大小的文件
    test_files = [
        'bad_code.py',
        'good_code.py',
        # 添加更大的测试文件
    ]
    
    for file in test_files:
        start_time = time.time()
        issues = detector.detect_issues(file)
        end_time = time.time()
        
        print(f"{file}: {len(issues)} 个问题, 耗时: {end_time - start_time:.2f}秒")
```

#### 3.2 批量检测性能测试

```python
def batch_performance_test():
    detector = StaticDetector()
    
    # 测试目录检测性能
    start_time = time.time()
    issues = detect_directory('.')
    end_time = time.time()
    
    print(f"批量检测: {len(issues)} 个问题, 耗时: {end_time - start_time:.2f}秒")
```

### 步骤4: 边界条件测试

#### 4.1 空文件测试

创建空文件 `empty.py`：
```python
# 空文件
```

测试检测器是否能正确处理空文件。

#### 4.2 语法错误文件测试

创建语法错误文件 `syntax_error.py`：
```python
def broken_function(
    # 缺少闭合括号
    return "error"
```

测试检测器是否能正确处理语法错误。

#### 4.3 大文件测试

创建大文件 `large_file.py`：
```python
# 生成包含大量代码的文件
def generate_large_file():
    content = "def test_function():\n"
    for i in range(1000):
        content += f"    x{i} = {i}\n"
    content += "    return x0\n"
    
    with open('large_file.py', 'w') as f:
        f.write(content)

generate_large_file()
```

测试检测器处理大文件的性能。

### 步骤5: 配置测试

#### 5.1 规则开关测试

```python
def test_rule_switches():
    detector = StaticDetector()
    
    # 测试禁用特定规则
    detector.rules['unused_imports'] = False
    detector.rules['magic_numbers'] = False
    
    issues = detector.detect_issues('bad_code.py')
    
    # 验证特定类型的问题未被检测到
    unused_import_issues = [i for i in issues if i['type'] == 'unused_import']
    magic_number_issues = [i for i in issues if i['type'] == 'magic_number']
    
    assert len(unused_import_issues) == 0, "未使用导入检测应该被禁用"
    assert len(magic_number_issues) == 0, "魔法数字检测应该被禁用"
```

#### 5.2 自定义规则测试

```python
def test_custom_rules():
    detector = StaticDetector()
    
    # 添加自定义检测规则
    def _check_custom_rule(self, tree, content):
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if 'test' in node.name.lower():
                    self.issues.append({
                        'type': 'test_function',
                        'severity': 'info',
                        'message': f'发现测试函数: {node.name}',
                        'line': node.lineno,
                        'file': ''
                    })
    
    # 绑定自定义方法
    detector._check_custom_rule = _check_custom_rule.__get__(detector, StaticDetector)
    
    issues = detector.detect_issues('test_file.py')
    # 验证自定义规则是否生效
```

## 测试用例

### 测试用例1: 基本检测功能

```python
def test_basic_detection():
    """测试基本检测功能"""
    detector = StaticDetector()
    issues = detector.detect_issues('bad_code.py')
    
    # 验证检测到问题
    assert len(issues) > 0, "应该检测到问题"
    
    # 验证问题类型
    issue_types = [i['type'] for i in issues]
    expected_types = ['hardcoded_secret', 'unsafe_eval', 'missing_type_hint']
    
    for expected_type in expected_types:
        assert expected_type in issue_types, f"应该检测到 {expected_type} 类型的问题"
```

### 测试用例2: 检测精度

```python
def test_detection_accuracy():
    """测试检测精度"""
    detector = StaticDetector()
    
    # 测试坏代码
    bad_issues = detector.detect_issues('bad_code.py')
    assert len(bad_issues) >= 15, "坏代码应该检测到至少15个问题"
    
    # 测试好代码
    good_issues = detector.detect_issues('good_code.py')
    assert len(good_issues) <= 5, "好代码应该检测到较少问题"
```

### 测试用例3: 性能测试

```python
def test_performance():
    """测试性能"""
    import time
    
    detector = StaticDetector()
    
    start_time = time.time()
    issues = detector.detect_issues('bad_code.py')
    end_time = time.time()
    
    detection_time = end_time - start_time
    assert detection_time < 1.0, f"检测时间应该小于1秒，实际: {detection_time:.2f}秒"
```

## 测试报告模板

### 测试结果记录

| 测试项目 | 预期结果 | 实际结果 | 状态 | 备注 |
|----------|----------|----------|------|------|
| 基本检测功能 | 检测到问题 | ✅ | 通过 | 检测到20个问题 |
| 检测精度 | 坏代码>好代码 | ✅ | 通过 | 坏代码20个，好代码2个 |
| 性能测试 | <1秒 | ✅ | 通过 | 0.3秒 |
| 空文件处理 | 无错误 | ✅ | 通过 | 正常处理 |
| 语法错误处理 | 捕获错误 | ✅ | 通过 | 正确捕获语法错误 |
| 规则开关 | 按预期工作 | ✅ | 通过 | 禁用规则生效 |

### 问题记录

| 问题描述 | 严重程度 | 状态 | 解决方案 |
|----------|----------|------|----------|
| 误报：某些正常代码被标记 | 低 | 待修复 | 优化检测规则 |
| 性能：大文件检测较慢 | 中 | 待优化 | 优化算法实现 |

## 自动化测试

### 创建测试脚本

```python
# test_runner.py
import unittest
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from static_detector import StaticDetector

class TestStaticDetector(unittest.TestCase):
    def setUp(self):
        self.detector = StaticDetector()
    
    def test_basic_detection(self):
        """测试基本检测功能"""
        issues = self.detector.detect_issues('bad_code.py')
        self.assertGreater(len(issues), 0)
    
    def test_good_code_detection(self):
        """测试好代码检测"""
        issues = self.detector.detect_issues('good_code.py')
        self.assertLessEqual(len(issues), 5)
    
    def test_rule_switches(self):
        """测试规则开关"""
        self.detector.rules['unused_imports'] = False
        issues = self.detector.detect_issues('bad_code.py')
        unused_issues = [i for i in issues if i['type'] == 'unused_import']
        self.assertEqual(len(unused_issues), 0)

if __name__ == '__main__':
    unittest.main()
```

### 运行自动化测试

```bash
python test_runner.py
```

## 持续集成

### GitHub Actions配置

```yaml
# .github/workflows/test.yml
name: Test Static Detector

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.8
    - name: Run tests
      run: |
        cd demo
        python test_runner.py
```

## 总结

本测试指南提供了完整的测试方案，包括：

1. **功能测试** - 验证检测功能是否正常工作
2. **精度测试** - 验证检测的准确性和误报率
3. **性能测试** - 验证检测性能是否满足要求
4. **边界测试** - 验证异常情况的处理
5. **配置测试** - 验证配置选项是否生效
6. **自动化测试** - 提供自动化测试框架

通过执行这些测试，可以确保静态检测功能的稳定性和可靠性。
