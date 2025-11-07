# 数据集测试指南

本指南介绍如何使用数据集测试框架来测试您的代码缺陷检测和修复系统。

## 📋 支持的数据集

### Java数据集
- **Defects4J**: 包含6个Java项目的真实缺陷（Chart, Closure, Lang, Math, Mockito, Time）
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

## 🚀 快速开始

### 1. 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装数据集特定工具（根据需要）
# Defects4J: https://github.com/rjust/defects4j
# SWE-bench: 通常通过HuggingFace datasets库加载
```

### 2. 准备数据集

#### Defects4J

```bash
# 1. 克隆Defects4J仓库
git clone https://github.com/rjust/defects4j.git
cd defects4j

# 2. 初始化Defects4J
./init.sh

# 3. 配置环境变量
export PATH=$PATH:$(pwd)/framework/bin
export D4J_HOME=$(pwd)
```

#### SWE-bench

```bash
# SWE-bench可以通过HuggingFace datasets库加载
# 或者从官网下载: https://www.swebench.com/

# 使用HuggingFace加载
from datasets import load_dataset
dataset = load_dataset("princeton-nlp/SWE-bench")
```

#### BugsInPy

```bash
# 克隆BugsInPy仓库
git clone https://github.com/soarsmu/BugsInPy.git
cd BugsInPy

# 按照官方文档设置环境
```

### 3. 运行测试

#### 方法1: 使用命令行工具

```bash
# 运行Defects4J数据集（限制10个测试用例）
python -m datasets.test_runner \
    --dataset defects4j \
    --path /path/to/defects4j \
    --limit 10

# 运行SWE-bench数据集
python -m datasets.test_runner \
    --dataset swebench \
    --path /path/to/swebench \
    --limit 5

# 运行指定测试用例
python -m datasets.test_runner \
    --dataset bugsinpy \
    --path /path/to/bugsinpy \
    --cases pandas-1 numpy-2

# 不运行修复，只测试原始代码
python -m datasets.test_runner \
    --dataset defects4j \
    --path /path/to/defects4j \
    --no-fix \
    --output results/no_fix
```

#### 方法2: 使用Python API

```python
from datasets.test_runner import DatasetTestRunner
import asyncio

async def main():
    # 创建测试运行器
    runner = DatasetTestRunner(output_dir="results")
    
    # 运行数据集
    stats = await runner.run_dataset(
        dataset_name="defects4j",
        dataset_path="/path/to/defects4j",
        limit=10,
        run_fix=True
    )
    
    # 打印结果
    print(f"总用例数: {stats['total']}")
    print(f"成功率: {stats['success_rate']:.2f}%")
    print(f"修复率: {stats['fix_rate']:.2f}%")
    print(f"测试通过率: {stats['test_pass_rate']:.2f}%")
    print(f"编译成功率: {stats['compile_success_rate']:.2f}%")

asyncio.run(main())
```

#### 方法3: 集成到现有系统

```python
from datasets.test_runner import DatasetTestRunner
from datasets import Defects4JAdapter

# 创建适配器
adapter = Defects4JAdapter(
    dataset_path="/path/to/defects4j",
    config={"defects4j_cmd": "defects4j"}
)

# 获取测试用例
test_cases = adapter.list_test_cases(limit=5)

# 转换为任务信息格式（用于FixExecutionAgent）
for test_case in test_cases:
    task_info = adapter.convert_to_task_info(test_case)
    # 调用您的修复API
    # result = await your_fix_api(task_info)
```

## 📊 结果分析

测试结果保存在输出目录中：

```
dataset_test_results/
├── Defects4JAdapter/
│   ├── Chart-1.json
│   ├── Chart-2.json
│   └── ...
├── SWEBenchAdapter/
│   └── ...
├── defects4j_stats.json      # 统计信息
└── swebench_stats.json
```

### 结果文件格式

每个测试用例的结果文件（JSON格式）：

```json
{
  "case_id": "Chart-1",
  "success": true,
  "fixed": true,
  "tests_passed": true,
  "compile_success": true,
  "error_message": null,
  "fix_details": {
    "success": true,
    "fixed_files": {...}
  },
  "test_output": "...",
  "execution_time": 45.2
}
```

统计信息文件：

```json
{
  "total": 10,
  "success": 8,
  "fixed": 7,
  "tests_passed": 8,
  "compile_success": 9,
  "success_rate": 80.0,
  "fix_rate": 70.0,
  "test_pass_rate": 80.0,
  "compile_success_rate": 90.0,
  "timestamp": "2024-01-01T12:00:00"
}
```

## 🔧 配置选项

### 数据集配置

```python
config = {
    # Defects4J配置
    "defects4j_cmd": "defects4j",  # Defects4J命令路径
    "work_dir": "/tmp/defects4j_work",  # 工作目录
    
    # 通用配置
    "timeout": 600,  # 超时时间（秒）
    "max_workers": 4,  # 最大并发数
}
```

### 环境变量

```bash
# Defects4J
export D4J_HOME=/path/to/defects4j
export PATH=$PATH:$D4J_HOME/framework/bin

# Python环境
export PYTHONPATH=$PYTHONPATH:/path/to/project
```

## 📝 使用示例

### 示例1: 批量测试Defects4J

```python
from datasets.test_runner import DatasetTestRunner
import asyncio

async def test_defects4j():
    runner = DatasetTestRunner(output_dir="results/defects4j")
    
    # 测试所有Chart项目的bug
    stats = await runner.run_dataset(
        dataset_name="defects4j",
        dataset_path="/path/to/defects4j",
        case_ids=[f"Chart-{i}" for i in range(1, 27)],  # Chart项目有26个bug
        run_fix=True
    )
    
    print(f"Chart项目测试完成: {stats}")

asyncio.run(test_defects4j())
```

### 示例2: 对比修复前后

```python
from datasets.test_runner import DatasetTestRunner
import asyncio

async def compare_fix():
    runner = DatasetTestRunner()
    
    # 测试修复前
    stats_before = await runner.run_dataset(
        dataset_name="defects4j",
        dataset_path="/path/to/defects4j",
        limit=10,
        run_fix=False  # 不运行修复
    )
    
    # 测试修复后
    stats_after = await runner.run_dataset(
        dataset_name="defects4j",
        dataset_path="/path/to/defects4j",
        limit=10,
        run_fix=True  # 运行修复
    )
    
    print(f"修复前成功率: {stats_before['success_rate']:.2f}%")
    print(f"修复后成功率: {stats_after['success_rate']:.2f}%")
    print(f"提升: {stats_after['success_rate'] - stats_before['success_rate']:.2f}%")

asyncio.run(compare_fix())
```

### 示例3: 自定义评估逻辑

```python
from datasets import Defects4JAdapter, TestCase
from datasets.test_runner import DatasetTestRunner

async def custom_evaluation():
    runner = DatasetTestRunner()
    adapter = runner.create_adapter("defects4j", "/path/to/defects4j")
    
    test_case = adapter.get_test_case("Chart-1")
    
    # 准备环境
    env_info = adapter.prepare_environment(test_case)
    
    # 运行原始测试
    original_result = adapter.run_tests(test_case)
    
    # 应用修复
    # ... 您的修复逻辑 ...
    
    # 运行修复后测试
    fixed_result = adapter.run_tests(test_case, fixed_code_path="...")
    
    # 自定义评估
    improvement = fixed_result['tests_passed'] - original_result['tests_passed']
    print(f"改进: {improvement}")

asyncio.run(custom_evaluation())
```

## ⚠️ 注意事项

1. **环境要求**
   - Defects4J需要Java 8+和Defects4J工具
   - SWE-bench需要Git和Python环境
   - C/C++数据集需要编译工具链（GCC/Clang）

2. **资源消耗**
   - 大规模测试会消耗大量时间和资源
   - 建议先用小规模测试（limit=5-10）
   - 考虑使用并行处理提高效率

3. **网络连接**
   - 某些数据集需要从GitHub克隆仓库
   - 确保网络连接正常或使用镜像

4. **权限问题**
   - 某些操作可能需要特定权限
   - 确保有足够的磁盘空间

## 🐛 故障排除

### Defects4J命令未找到

```bash
# 检查Defects4J是否正确安装
which defects4j

# 如果未找到，添加到PATH
export PATH=$PATH:/path/to/defects4j/framework/bin
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

### 内存不足

- 减少并发数（max_workers）
- 分批处理测试用例
- 增加系统内存

## 📚 更多资源

- [Defects4J官方文档](https://github.com/rjust/defects4j)
- [SWE-bench官网](https://www.swebench.com/)
- [BugsInPy GitHub](https://github.com/soarsmu/BugsInPy)
- [数据集测试框架README](../datasets/README.md)

## 🤝 贡献

欢迎贡献新的数据集适配器或改进现有适配器！

## 📄 许可证

本框架遵循项目主许可证。

