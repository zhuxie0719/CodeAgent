# Agent与SWE-bench集成工作机制报告

## 1. 系统概述

本系统实现了一个完整的SWE-bench（Software Engineering Benchmark）评估框架，允许Agent在标准化的软件工程任务上进行批量评估。SWE-bench是一个包含真实GitHub问题修复任务的基准测试集，用于评估AI代码修复Agent的能力。

## 2. SWE-bench数据集集成

### 2.1 数据集映射机制

系统通过`DATASET_MAPPING`字典支持多个SWE-bench数据集变体：

```python
DATASET_MAPPING = {
    "full": "princeton-nlp/SWE-Bench",
    "verified": "princeton-nlp/SWE-Bench_Verified",
    "lite": "princeton-nlp/SWE-Bench_Lite",
    "multimodal": "princeton-nlp/SWE-Bench_Multimodal",
    "multilingual": "swe-bench/SWE-Bench_Multilingual",
    "smith": "SWE-bench/SWE-smith",
    "_test": "klieret/swe-bench-dummy-test-dataset",
}
```

**关键设计要点：**
- **多数据集支持**：支持SWE-bench的多个子集，从轻量级的`lite`到完整的`full`数据集
- **灵活路径**：支持直接指定HuggingFace数据集路径，不限于预定义映射
- **测试支持**：提供`_test`数据集用于开发和测试

### 2.2 数据集加载

系统使用HuggingFace的`datasets`库加载SWE-bench数据集：

```python
from datasets import load_dataset

dataset_path = DATASET_MAPPING.get(subset, subset)
instances = list(load_dataset(dataset_path, split=split))
```

**关键设计要点：**
- **动态加载**：根据用户指定的`subset`和`split`参数动态加载数据集
- **实例结构**：每个实例包含`instance_id`、`problem_statement`等关键字段
- **内存管理**：使用列表转换确保数据在内存中可用

### 2.3 实例过滤和切片

系统提供了灵活的实例选择机制：

```python
def filter_instances(
    instances: list[dict], 
    *, 
    filter_spec: str, 
    slice_spec: str = "", 
    shuffle: bool = False
) -> list[dict]:
    """过滤和切片SWEBench实例列表"""
    # 随机打乱
    if shuffle:
        instances = sorted(instances.copy(), key=lambda x: x["instance_id"])
        random.seed(42)
        random.shuffle(instances)
    
    # 正则过滤
    instances = [instance for instance in instances 
                 if re.match(filter_spec, instance["instance_id"])]
    
    # 切片选择
    if slice_spec:
        values = [int(x) if x else None for x in slice_spec.split(":")]
        instances = instances[slice(*values)]
    
    return instances
```

**关键设计要点：**
- **正则过滤**：支持通过正则表达式过滤特定实例ID
- **切片选择**：支持Python切片语法（如`0:5`选择前5个实例）
- **随机打乱**：支持随机化实例顺序，使用固定种子确保可复现性
- **跳过已处理**：自动跳过已存在于`preds.json`中的实例

## 3. Docker环境集成

### 3.1 SWE-bench Docker镜像管理

系统为每个SWE-bench实例创建对应的Docker环境：

```python
def get_swebench_docker_image_name(instance: dict) -> str:
    """获取SWEBench实例的Docker镜像名称"""
    image_name = instance.get("image_name", None)
    if image_name is None:
        # Docker不允许双下划线，使用特殊标记替换
        iid = instance["instance_id"]
        id_docker_compatible = iid.replace("__", "_1776_")
        image_name = f"docker.io/swebench/sweb.eval.x86_64.{id_docker_compatible}:latest".lower()
    return image_name
```

**关键设计要点：**
- **镜像命名规范**：遵循SWE-bench官方镜像命名规范
- **兼容性处理**：处理Docker镜像名称限制（不允许双下划线）
- **自动发现**：如果实例包含`image_name`字段，直接使用；否则根据`instance_id`生成

### 3.2 环境初始化

系统通过`get_sb_environment`函数创建SWE-bench专用环境：

```python
def get_sb_environment(config: dict, instance: dict) -> Environment:
    env_config = config.setdefault("environment", {})
    env_config["environment_class"] = env_config.get("environment_class", "docker")
    image_name = get_swebench_docker_image_name(instance)
    
    if env_config["environment_class"] == "docker":
        env_config["image"] = image_name
    elif env_config["environment_class"] == "singularity":
        env_config["image"] = "docker://" + image_name
    
    env = get_environment(env_config)
    
    # 执行启动命令（如果配置了）
    if startup_command := config.get("run", {}).get("env_startup_command"):
        startup_command = Template(startup_command, undefined=StrictUndefined).render(**instance)
        out = env.execute(startup_command)
        if out["returncode"] != 0:
            raise RuntimeError(f"Error executing startup command: {out}")
    
    return env
```

**关键设计要点：**
- **多容器支持**：支持Docker和Singularity两种容器技术
- **启动命令**：支持通过Jinja2模板配置环境启动命令
- **错误处理**：启动命令失败时抛出异常，确保环境正确初始化
- **工作目录**：默认工作目录为`/testbed`，符合SWE-bench规范

### 3.3 SWE-ReX集成（可选）

系统还支持使用SWE-ReX进行更严格的沙箱隔离：

```python
class SwerexDockerEnvironment:
    def __init__(self, **kwargs):
        """使用SWE-ReX在Docker容器中执行bash命令"""
        self.config = SwerexDockerEnvironmentConfig(**kwargs)
        self.deployment = DockerDeployment(
            image=self.config.image, 
            **self.config.deployment_extra_kwargs
        )
        asyncio.run(self.deployment.start())
    
    def execute(self, command: str, cwd: str = "", *, timeout: int | None = None):
        """在环境中执行命令并返回原始输出"""
        output = asyncio.run(
            self.deployment.runtime.execute(
                RexCommand(
                    command=command,
                    shell=True,
                    check=False,
                    cwd=cwd or self.config.cwd,
                    timeout=timeout or self.config.timeout,
                    merge_output_streams=True,
                )
            )
        )
        return {
            "output": output.stdout,
            "returncode": output.exit_code,
        }
```

**关键设计要点：**
- **异步执行**：使用asyncio实现异步命令执行
- **沙箱隔离**：通过SWE-ReX提供更强的安全隔离
- **统一接口**：与标准Environment接口保持一致

## 4. 批量处理机制

### 4.1 批量执行架构

系统使用线程池实现并行批量处理：

```python
def main(
    subset: str = "lite",
    split: str = "dev",
    workers: int = 1,
    output: str = "",
    # ... 其他参数
):
    # 加载数据集
    instances = list(load_dataset(dataset_path, split=split))
    instances = filter_instances(instances, filter_spec=filter_spec, 
                                 slice_spec=slice_spec, shuffle=shuffle)
    
    # 创建进度管理器
    progress_manager = RunBatchProgressManager(len(instances), 
                                               output_path / f"exit_statuses_{time.time()}.yaml")
    
    # 使用线程池并行处理
    with Live(progress_manager.render_group, refresh_per_second=4):
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(process_instance, instance, output_path, 
                               config, progress_manager): instance["instance_id"]
                for instance in instances
            }
            try:
                process_futures(futures)
            except KeyboardInterrupt:
                # 优雅处理中断
                logger.info("Cancelling all pending jobs...")
                for future in futures:
                    if not future.running() and not future.done():
                        future.cancel()
                process_futures(futures)
```

**关键设计要点：**
- **并行处理**：使用`ThreadPoolExecutor`实现多线程并行处理
- **进度跟踪**：实时显示每个实例的处理状态和整体进度
- **优雅中断**：支持Ctrl+C中断，取消未开始的任务
- **异常处理**：捕获并记录每个实例处理过程中的异常

### 4.2 单实例处理流程

每个实例的处理流程如下：

```python
def process_instance(
    instance: dict,
    output_dir: Path,
    config: dict,
    progress_manager: RunBatchProgressManager,
) -> None:
    """处理单个SWEBench实例"""
    instance_id = instance["instance_id"]
    instance_dir = output_dir / instance_id
    
    # 清理之前的状态
    remove_from_preds_file(output_dir / "preds.json", instance_id)
    (instance_dir / f"{instance_id}.traj.json").unlink(missing_ok=True)
    
    # 初始化模型和Agent
    model = get_model(config=config.get("model", {}))
    task = instance["problem_statement"]
    
    progress_manager.on_instance_start(instance_id)
    progress_manager.update_instance_status(instance_id, "Pulling/starting docker")
    
    agent = None
    extra_info = None
    
    try:
        # 创建环境
        env = get_sb_environment(config, instance)
        
        # 创建Agent（带进度跟踪）
        agent = ProgressTrackingAgent(
            model,
            env,
            progress_manager=progress_manager,
            instance_id=instance_id,
            **config.get("agent", {}),
        )
        
        # 运行Agent
        exit_status, result = agent.run(task)
        
    except Exception as e:
        logger.error(f"Error processing instance {instance_id}: {e}", exc_info=True)
        exit_status, result = type(e).__name__, str(e)
        extra_info = {"traceback": traceback.format_exc()}
        
    finally:
        # 保存轨迹和结果
        save_traj(
            agent,
            instance_dir / f"{instance_id}.traj.json",
            exit_status=exit_status,
            result=result,
            extra_info=extra_info,
            instance_id=instance_id,
        )
        update_preds_file(output_dir / "preds.json", instance_id, 
                         model.config.model_name, result)
        progress_manager.on_instance_end(instance_id, exit_status)
```

**关键设计要点：**
- **状态清理**：处理前清理之前的状态，避免不一致
- **进度跟踪**：每个步骤都更新进度管理器
- **异常捕获**：捕获所有异常，确保结果被保存
- **结果保存**：同时保存详细轨迹（traj.json）和预测结果（preds.json）

### 4.3 进度跟踪Agent

系统提供了专门的`ProgressTrackingAgent`来跟踪处理进度：

```python
class ProgressTrackingAgent(DefaultAgent):
    """包装DefaultAgent，提供进度更新功能"""
    
    def __init__(self, *args, progress_manager: RunBatchProgressManager, 
                 instance_id: str = "", **kwargs):
        super().__init__(*args, **kwargs)
        self.progress_manager: RunBatchProgressManager = progress_manager
        self.instance_id = instance_id
    
    def step(self) -> dict:
        """重写step方法以提供进度更新"""
        self.progress_manager.update_instance_status(
            self.instance_id, 
            f"Step {self.model.n_calls + 1:3d} (${self.model.cost:.2f})"
        )
        return super().step()
```

**关键设计要点：**
- **透明包装**：完全兼容DefaultAgent，只添加进度跟踪功能
- **实时更新**：每执行一步都更新进度和成本信息
- **状态显示**：显示当前步数和累计成本

## 5. 进度管理和可视化

### 5.1 进度管理器设计

`RunBatchProgressManager`提供了丰富的进度跟踪功能：

```python
class RunBatchProgressManager:
    def __init__(self, num_instances: int, yaml_report_path: Path | None = None):
        self._instances_by_exit_status = collections.defaultdict(list)
        
        # 主进度条：显示整体进度
        self._main_progress_bar = Progress(
            SpinnerColumn(spinner_name="dots2"),
            TextColumn("[progress.description]{task.description} (${task.fields[total_cost]})"),
            BarColumn(),
            MofNCompleteColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            TextColumn("[cyan]{task.fields[eta]}[/cyan]"),
            speed_estimate_period=60 * 5,
        )
        
        # 任务进度条：显示每个实例的状态
        self._task_progress_bar = Progress(
            SpinnerColumn(spinner_name="dots2"),
            TextColumn("{task.fields[instance_id]}"),
            TextColumn("{task.fields[status]}"),
            TimeElapsedColumn(),
        )
        
        # 退出状态表：统计不同退出状态的实例数量
        self.render_group = Group(Table(), self._task_progress_bar, self._main_progress_bar)
```

**关键设计要点：**
- **多层级显示**：同时显示整体进度、单个任务状态和统计信息
- **成本追踪**：实时显示累计API调用成本
- **ETA估算**：基于当前速度估算剩余时间
- **状态分类**：按退出状态分类统计实例

### 5.2 状态更新机制

```python
def update_instance_status(self, instance_id: str, message: str):
    """更新实例状态"""
    with self._lock:
        self._task_progress_bar.update(
            self._spinner_tasks[instance_id],
            status=_shorten_str(message, 30),
            instance_id=_shorten_str(instance_id, 25, shorten_left=True),
        )
    self._update_total_costs()

def on_instance_end(self, instance_id: str, exit_status: str | None) -> None:
    """实例处理完成时的回调"""
    self._instances_by_exit_status[exit_status].append(instance_id)
    with self._lock:
        self._task_progress_bar.remove_task(self._spinner_tasks[instance_id])
        self._main_progress_bar.update(TaskID(0), advance=1, eta=self._get_eta_text())
    self.update_exit_status_table()
    self._update_total_costs()
    if self._yaml_report_path is not None:
        self._save_overview_data_yaml(self._yaml_report_path)
```

**关键设计要点：**
- **线程安全**：使用锁保护共享状态
- **实时刷新**：使用Rich库的Live功能实现实时刷新
- **状态持久化**：定期保存状态到YAML文件
- **自动清理**：实例完成后自动从任务列表中移除

## 6. 结果保存和输出

### 6.1 预测结果文件（preds.json）

系统按照SWE-bench标准格式保存预测结果：

```python
def update_preds_file(output_path: Path, instance_id: str, model_name: str, result: str):
    """更新输出JSON文件，包含单个实例的结果"""
    with _OUTPUT_FILE_LOCK:
        output_data = {}
        if output_path.exists():
            output_data = json.loads(output_path.read_text())
        output_data[instance_id] = {
            "model_name_or_path": model_name,
            "instance_id": instance_id,
            "model_patch": result,
        }
        output_path.write_text(json.dumps(output_data, indent=2))
```

**关键设计要点：**
- **标准格式**：遵循SWE-bench的`preds.json`格式规范
- **线程安全**：使用文件锁确保并发写入安全
- **增量更新**：每个实例完成后立即更新，不等待全部完成
- **结果提取**：从Agent的最终输出中提取`model_patch`（通常是git diff）

### 6.2 轨迹文件（traj.json）

系统为每个实例保存详细的执行轨迹：

```python
def save_traj(
    agent: Agent | None,
    path: Path,
    *,
    exit_status: str | None = None,
    result: str | None = None,
    extra_info: dict | None = None,
    **kwargs,
):
    """保存Agent的轨迹到文件"""
    data = {
        "info": {
            "exit_status": exit_status,
            "submission": result,
            "model_stats": {
                "instance_cost": 0.0,
                "api_calls": 0,
            },
            "fix_code_agent_version": __version__,
            "config": {
                "agent": _asdict(agent.config),
                "model": _asdict(agent.model.config),
                "environment": _asdict(agent.env.config),
            },
        },
        "messages": agent.messages if agent else [],
        "trajectory_format": "fix-code-agent-1",
    } | kwargs
```

**关键设计要点：**
- **完整记录**：保存所有消息历史、配置信息和统计信息
- **可复现性**：包含完整的配置信息，支持结果复现
- **调试支持**：包含异常堆栈等调试信息
- **版本追踪**：记录Agent版本，便于结果分析

### 6.3 退出状态报告

系统自动生成YAML格式的退出状态报告：

```yaml
instances_by_exit_status:
  Submitted: 
    - instance_id_1
    - instance_id_2
  LimitsExceeded:
    - instance_id_3
  FormatError:
    - instance_id_4
```

**关键设计要点：**
- **状态分类**：按退出状态自动分类统计
- **实时更新**：每个实例完成后立即更新
- **便于分析**：YAML格式便于后续分析和可视化

## 7. 单实例运行模式

### 7.1 交互式单实例运行

系统提供了单实例运行模式，支持交互式调试：

```python
@app.command()
def main(
    subset: str = "lite",
    split: str = "dev",
    instance_spec: str = 0,  # 可以是ID或索引
    model_name: str | None = None,
    config_path: Path = builtin_config_dir / "extra" / "swebench.yaml",
    exit_immediately: bool = False,
    output: Path = DEFAULT_OUTPUT,
):
    """在单个SWE-Bench实例上运行"""
    # 加载数据集
    instances = {
        inst["instance_id"]: inst
        for inst in load_dataset(dataset_path, split=split)
    }
    
    # 支持索引或ID
    if instance_spec.isnumeric():
        instance_spec = sorted(instances.keys())[int(instance_spec)]
    instance = instances[instance_spec]
    
    # 创建交互式Agent
    agent = InteractiveAgent(
        get_model(model_name, config.get("model", {})),
        env,
        **({"mode": "yolo"} | config.get("agent", {})),
    )
    
    # 运行Agent
    exit_status, result = agent.run(instance["problem_statement"])
```

**关键设计要点：**
- **灵活选择**：支持通过索引或实例ID选择实例
- **交互模式**：使用`InteractiveAgent`支持用户交互
- **快速测试**：适合快速测试和调试单个实例
- **默认输出**：保存到固定位置，便于查看

## 8. SWE-bench专用配置

### 8.1 配置文件结构

系统提供了专门的SWE-bench配置文件（`config/extra/swebench.yaml`）：

```yaml
agent:
  system_template: |
    # 系统提示词，定义Agent角色和行为
  instance_template: |
    <pr_description>
    Consider the following PR description:
    {{task}}
    </pr_description>
    # 详细的任务指令
  step_limit: 250
  cost_limit: 3.0

environment:
  cwd: "/testbed"
  timeout: 60
  environment_class: docker

model:
  model_name: "anthropic/claude-sonnet-4-5-20250929"
  model_kwargs:
    temperature: 0.0
```

**关键设计要点：**
- **任务格式**：将SWE-bench的`problem_statement`作为PR描述传递给Agent
- **工作目录**：设置为`/testbed`，符合SWE-bench规范
- **限制设置**：设置合理的步数和成本限制
- **环境配置**：配置Docker环境和超时设置

### 8.2 配置变量注入

系统支持通过Jinja2模板注入实例特定信息：

```python
def get_sb_environment(config: dict, instance: dict) -> Environment:
    # 启动命令可以使用实例变量
    if startup_command := config.get("run", {}).get("env_startup_command"):
        startup_command = Template(startup_command, undefined=StrictUndefined).render(**instance)
        out = env.execute(startup_command)
```

**关键设计要点：**
- **动态配置**：支持基于实例数据的动态配置
- **模板渲染**：使用Jinja2模板引擎渲染配置
- **变量访问**：可以访问实例的所有字段（如`instance_id`、`repo`等）

## 9. 完整执行流程示例

以下是一个完整的SWE-bench批量评估流程：

```
1. 初始化阶段
   - 用户指定数据集子集（如"lite"）和分割（如"dev"）
   - 系统从HuggingFace加载数据集
   - 应用过滤和切片（如"--slice 0:10"选择前10个实例）
   - 创建输出目录和日志文件

2. 并行处理阶段
   - 为每个实例创建线程任务
   - 每个任务执行以下步骤：
     a. 根据instance_id生成Docker镜像名称
     b. 拉取/启动Docker容器
     c. 创建ProgressTrackingAgent
     d. 将problem_statement作为任务传递给Agent
     e. Agent循环执行直到完成或达到限制
     f. 保存轨迹文件（traj.json）
     g. 更新预测文件（preds.json）
     h. 更新进度管理器

3. 结果汇总阶段
   - 所有实例处理完成后
   - 生成退出状态报告（YAML格式）
   - 输出最终的preds.json文件
   - 可以用于SWE-bench官方评估工具
```

## 10. 关键技术特点

### 10.1 标准化集成

- **格式兼容**：完全遵循SWE-bench的数据格式和输出格式规范
- **评估兼容**：生成的`preds.json`可以直接用于SWE-bench官方评估
- **镜像规范**：使用SWE-bench官方Docker镜像命名规范

### 10.2 可扩展性

- **多数据集**：轻松支持新的SWE-bench数据集变体
- **多容器**：支持Docker和Singularity
- **多模型**：支持任何通过litellm兼容的LLM模型

### 10.3 可靠性

- **错误恢复**：每个实例独立处理，单个失败不影响其他实例
- **状态持久化**：实时保存结果，避免意外中断导致数据丢失
- **线程安全**：使用锁保护共享资源

### 10.4 可观测性

- **实时进度**：丰富的进度显示，包括成本、ETA等
- **详细日志**：每个步骤都有日志记录
- **完整轨迹**：保存完整的执行轨迹，便于分析和调试

## 11. 使用示例

### 11.1 批量评估

```bash
# 在SWE-bench Lite数据集上运行，使用4个并行worker
python -m fixcodeagent.run.extra.swebench \
    --subset lite \
    --split dev \
    --slice 0:10 \
    --workers 4 \
    --output ./results \
    --model anthropic/claude-sonnet-4-5-20250929
```

### 11.2 单实例调试

```bash
# 运行单个实例进行调试
python -m fixcodeagent.run.extra.swebench_single \
    --subset lite \
    --instance 0 \
    --model anthropic/claude-sonnet-4-5-20250929
```

### 11.3 过滤特定实例

```bash
# 只运行匹配特定模式的实例
python -m fixcodeagent.run.extra.swebench \
    --filter "django__django.*" \
    --subset lite
```

## 12. 总结

本系统通过精心设计的数据集集成、Docker环境管理、批量处理机制和结果保存系统，实现了一个完整的SWE-bench评估框架。系统在保持与SWE-bench标准完全兼容的同时，提供了丰富的功能特性，包括并行处理、进度跟踪、错误恢复等，使得大规模评估变得简单高效。通过模块化设计，系统还支持灵活的配置和扩展，可以轻松适配不同的评估需求。

