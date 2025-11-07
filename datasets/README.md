# 数据集测试框架

本框架支持多种标准缺陷数据集，用于测试代码缺陷检测和修复系统。

## 支持的数据集

### Java数据集
- **Defects4J**: 包含6个Java项目的真实缺陷
- **Bears**: 基于Defects4J的缺陷数据集
- **Bugs**: Java缺陷数据集

### C/C++数据集
- **BigVul**: C/C++漏洞数据集
- **Devign**: C/C++漏洞检测数据集

### Python数据集
- **SWE-bench**: 软件工程基准测试数据集
- **BugsInPy**: Python缺陷数据集

### 混合数据集
- **DebugBench**: 包含多种编程语言的混合数据集

## 快速开始

### 1. 安装依赖

```bash
# 安装数据集特定工具（如Defects4J）
# 参考各数据集的官方文档

# 安装Python依赖
pip install -r requirements.txt
```

### 2. 准备数据集

下载并准备数据集：

```bash
# Defects4J
# 参考: https://github.com/rjust/defects4j

# SWE-bench
# 参考: https://www.swebench.com/

# BugsInPy
# 参考: https://github.com/soarsmu/BugsInPy

# 其他数据集请参考各自的官方文档
```

### 3. 运行测试

#### 使用命令行工具

```bash
# 运行Defects4J数据集（限制10个测试用例）
python -m datasets.test_runner --dataset defects4j --path /path/to/defects4j --limit 10

# 运行SWE-bench数据集
python -m datasets.test_runner --dataset swebench --path /path/to/swebench --limit 5

# 运行指定测试用例
python -m datasets.test_runner --dataset bugsinpy --path /path/to/bugsinpy --cases case1 case2 case3

# 不运行修复，只测试原始代码
python -m datasets.test_runner --dataset defects4j --path /path/to/defects4j --no-fix
```

#### 使用Python API

```python
from datasets.test_runner import DatasetTestRunner
import asyncio

async def main():
    runner = DatasetTestRunner(output_dir="results")
    
    # 运行数据集
    stats = await runner.run_dataset(
        dataset_name="defects4j",
        dataset_path="/path/to/defects4j",
        limit=10,
        run_fix=True
    )
    
    print(f"成功率: {stats['success_rate']:.2f}%")
    print(f"修复率: {stats['fix_rate']:.2f}%")

asyncio.run(main())
```

## 数据集适配器

每个数据集都有对应的适配器类，实现了以下接口：

- `list_test_cases()`: 列出所有测试用例
- `get_test_case()`: 获取指定测试用例
- `prepare_environment()`: 准备测试环境
- `run_tests()`: 运行测试
- `evaluate_fix()`: 评估修复结果

### 自定义适配器

如果需要支持新的数据集，可以继承 `BaseDatasetAdapter` 类：

```python
from datasets.base_adapter import BaseDatasetAdapter, TestCase, DatasetResult

class MyDatasetAdapter(BaseDatasetAdapter):
    def list_test_cases(self, limit=None):
        # 实现列出测试用例的逻辑
        pass
    
    def get_test_case(self, case_id):
        # 实现获取测试用例的逻辑
        pass
    
    # ... 实现其他必需方法
```

## 配置

可以通过配置文件或环境变量配置数据集：

```python
config = {
    "defects4j_cmd": "defects4j",  # Defects4J命令路径
    "work_dir": "/tmp/dataset_work",  # 工作目录
    "timeout": 600,  # 超时时间（秒）
}
```

## 输出结果

测试结果保存在输出目录中：

```
dataset_test_results/
├── Defects4JAdapter/
│   ├── Chart-1.json
│   ├── Chart-2.json
│   └── ...
├── SWEBenchAdapter/
│   └── ...
├── defects4j_stats.json
└── swebench_stats.json
```

每个测试用例的结果包含：
- `success`: 是否成功
- `fixed`: 是否成功修复
- `tests_passed`: 测试是否通过
- `compile_success`: 编译是否成功
- `error_message`: 错误信息
- `fix_details`: 修复详情
- `test_output`: 测试输出

## 注意事项

1. **环境要求**: 不同数据集需要不同的工具和环境
   - Defects4J需要Java和Defects4J工具
   - SWE-bench需要Git和Python环境
   - C/C++数据集需要编译工具链

2. **权限问题**: 某些操作可能需要特定权限，确保有足够的权限

3. **网络连接**: 某些数据集需要从GitHub克隆仓库，确保网络连接正常

4. **资源消耗**: 大规模测试会消耗大量时间和资源，建议先用小规模测试

## 故障排除

### Defects4J命令未找到
```bash
# 确保Defects4J已正确安装并配置到PATH
export PATH=$PATH:/path/to/defects4j/bin
```

### 测试超时
```python
# 增加超时时间
config = {"timeout": 1200}  # 20分钟
```

### 编译失败
- 检查项目依赖是否已安装
- 检查编译工具是否正确配置
- 查看详细错误日志

## 贡献

欢迎贡献新的数据集适配器或改进现有适配器！

## 许可证

本框架遵循项目主许可证。

