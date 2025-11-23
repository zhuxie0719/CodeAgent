# Agent代码修复关键算法设计报告

## 1. 系统架构概述

本系统实现了一个基于大语言模型（LLM）的代码修复Agent，通过循环交互的方式，让AI助手能够理解任务、执行命令、观察结果，并持续迭代直到完成任务。

## 2. Mini Prompt设计

### 2.1 Prompt模板结构

Mini配置（`config/mini.yaml`）定义了三个核心Prompt模板：

#### 2.1.1 系统提示词（system_template）

系统提示词定义了Agent的基本角色和行为规范：

```yaml
system_template: |
  You are a helpful assistant that can interact with a computer.
  
  Your response must contain exactly ONE PowerShell code block with ONE command.
  Include a THOUGHT section before your command where you explain your reasoning process.
```

**关键设计要点：**
- **严格格式要求**：要求Agent每次响应必须包含且仅包含一个PowerShell代码块
- **推理过程展示**：要求Agent在命令前提供THOUGHT部分，解释执行该命令的原因
- **格式示例**：提供清晰的格式示例，确保LLM理解输出格式

#### 2.1.2 实例提示词（instance_template）

实例提示词包含具体的任务描述和工作流程指导：

```yaml
instance_template: |
  Please solve this issue: {{task}}
  
  ## Recommended Workflow
  1. Analyze the codebase by finding and reading relevant files
  2. Create a script to reproduce the issue
  3. Edit the source code to resolve the issue
  4. Verify your fix works by running your script again
  5. Test edge cases to ensure your fix is robust
  6. Submit your changes and finish your work by issuing: 
     `echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT`
```

**关键设计要点：**
- **任务注入**：通过`{{task}}`模板变量动态注入用户任务
- **工作流程指导**：提供6步推荐工作流程，引导Agent系统化地解决问题
- **完成标志**：明确任务完成的标志命令，用于终止循环
- **系统信息注入**：通过`{{system}}`等变量注入系统环境信息

#### 2.1.3 观察反馈模板（action_observation_template）

观察反馈模板用于将命令执行结果反馈给LLM：

```yaml
action_observation_template: |
  <returncode>{{output.returncode}}</returncode>
  <output>
  {{ output.output }}
  </output>
```

**关键设计要点：**
- **返回码反馈**：提供命令执行的返回码，帮助LLM判断命令是否成功
- **输出截断机制**：当输出超过10000字符时，自动截断并提示LLM使用更精确的命令
- **结构化反馈**：使用XML标签结构化输出，便于LLM解析

### 2.2 Prompt渲染机制

系统使用Jinja2模板引擎进行Prompt渲染，支持动态变量注入：

```python
def render_template(self, template: str, **kwargs) -> str:
    template_vars = asdict(self.config) | self.env.get_template_vars() | self.model.get_template_vars()
    return Template(template, undefined=StrictUndefined).render(
        **kwargs, **template_vars, **self.extra_template_vars
    )
```

**变量来源：**
- **配置变量**：来自Agent配置（AgentConfig）
- **环境变量**：来自执行环境（Environment.get_template_vars()）
- **模型变量**：来自模型统计信息（Model.get_template_vars()）
- **任务变量**：动态注入的任务描述和额外参数

## 3. Agent与终端的交互机制

### 3.1 终端命令执行流程

Agent通过`LocalEnvironment`类与本地终端进行交互：

```python
class LocalEnvironment:
    def execute(self, command: str, cwd: str = "", *, timeout: int | None = None):
        """在本地环境中执行命令并返回结果"""
        # Windows系统使用PowerShell
        if platform.system() == "Windows":
            # 使用Base64编码确保Unicode支持
            encoded_command = base64.b64encode(full_command.encode('utf-16-le')).decode('ascii')
            result = subprocess.run(
                ["powershell.exe", "-NoProfile", "-EncodedCommand", encoded_command],
                timeout=timeout or self.config.timeout,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
        return {"output": result.stdout, "returncode": result.returncode}
```

**关键设计要点：**
- **跨平台支持**：Windows使用PowerShell，其他系统使用shell
- **Unicode处理**：Windows下使用Base64编码确保中文字符正确传输
- **超时控制**：默认30秒超时，防止命令无限执行
- **统一输出**：将stderr重定向到stdout，统一返回格式

### 3.2 命令解析机制

Agent从LLM响应中提取PowerShell命令：

```python
def parse_action(self, response: dict) -> dict:
    """从LLM响应中解析出要执行的命令"""
    # 优先匹配PowerShell代码块
    actions = re.findall(r"```powershell\s*\n(.*?)\n```", response["content"], re.DOTALL)
    if len(actions) == 0:
        # 向后兼容bash格式
        actions = re.findall(r"```bash\s*\n(.*?)\n```", response["content"], re.DOTALL)
    if len(actions) == 1:
        return {"action": actions[0].strip(), **response}
    raise FormatError("必须提供且仅提供一个命令")
```

**关键设计要点：**
- **格式验证**：严格验证响应格式，确保只有一个命令
- **向后兼容**：支持bash格式以兼容旧版本
- **错误处理**：格式错误时抛出FormatError，触发重新提示

## 4. 从终端获取LLM结果的机制

### 4.1 消息历史管理

Agent维护一个消息历史列表，记录所有对话：

```python
class DefaultAgent:
    def __init__(self, model: Model, env: Environment, **kwargs):
        self.messages: list[dict] = []  # 消息历史
        self.model = model
        self.env = env
    
    def add_message(self, role: str, content: str, **kwargs):
        """添加消息到历史记录"""
        self.messages.append({"role": role, "content": content, **kwargs})
```

**消息类型：**
- **system**：系统提示词，定义Agent角色
- **user**：用户输入，包括任务描述和命令执行结果
- **assistant**：LLM响应，包含推理过程和命令

### 4.2 LLM查询流程

```python
def query(self) -> dict:
    """查询模型并返回响应"""
    # 检查限制条件
    if 0 < self.config.step_limit <= self.model.n_calls:
        raise LimitsExceeded()
    if 0 < self.config.cost_limit <= self.model.cost:
        raise LimitsExceeded()
    
    # 调用模型API
    response = self.model.query(self.messages)
    
    # 将响应添加到消息历史
    self.add_message("assistant", **response)
    return response
```

**关键设计要点：**
- **限制检查**：在执行前检查步数限制和成本限制
- **消息传递**：将完整的消息历史传递给LLM，保持上下文
- **响应记录**：将LLM响应添加到消息历史，用于后续迭代

### 4.3 模型接口实现

系统通过`LitellmModel`封装LLM调用：

```python
class LitellmModel:
    def query(self, messages: list[dict[str, str]], **kwargs) -> dict:
        """调用LLM API"""
        # 设置缓存控制（如Anthropic模型）
        if self.config.set_cache_control:
            messages = set_cache_control(messages, mode=self.config.set_cache_control)
        
        # 调用litellm API
        response = self._query(messages, **kwargs)
        
        # 计算成本
        cost = litellm.cost_calculator.completion_cost(response)
        self.cost += cost
        self.n_calls += 1
        
        # 返回格式化的响应
        return {
            "content": response.choices[0].message.content or "",
            "extra": {"response": response.model_dump()},
        }
```

**关键设计要点：**
- **统一接口**：通过litellm库统一不同LLM提供商的接口
- **成本追踪**：自动计算每次调用的成本并累加
- **重试机制**：使用tenacity库实现指数退避重试
- **错误处理**：区分可重试错误和不可重试错误

## 5. 循环执行机制

### 5.1 主循环结构

Agent的核心是一个`while True`循环，持续执行直到任务完成：

```python
def run(self, task: str, **kwargs) -> tuple[str, str]:
    """运行Agent直到任务完成"""
    # 初始化消息历史
    self.messages = []
    self.add_message("system", self.render_template(self.config.system_template))
    self.add_message("user", self.render_template(self.config.instance_template))
    
    # 主循环
    while True:
        try:
            self.step()  # 执行一步
        except NonTerminatingException as e:
            # 非终止异常：添加到消息历史，继续循环
            self.add_message("user", str(e))
        except TerminatingException as e:
            # 终止异常：结束循环，返回结果
            self.add_message("user", str(e))
            return type(e).__name__, str(e)
```

**关键设计要点：**
- **初始化阶段**：添加系统提示词和任务描述
- **异常分类**：区分终止异常和非终止异常
- **持续迭代**：非终止异常不会中断循环，而是作为反馈继续

### 5.2 单步执行流程

每一步（step）包含三个核心操作：

```python
def step(self) -> dict:
    """执行一步：查询LLM -> 执行命令 -> 获取观察"""
    return self.get_observation(self.query())

def query(self) -> dict:
    """查询LLM获取下一步命令"""
    response = self.model.query(self.messages)
    self.add_message("assistant", **response)
    return response

def get_observation(self, response: dict) -> dict:
    """执行命令并获取观察结果"""
    # 1. 解析命令
    action = self.parse_action(response)
    
    # 2. 执行命令
    output = self.execute_action(action)
    
    # 3. 格式化观察结果
    observation = self.render_template(
        self.config.action_observation_template, 
        output=output
    )
    
    # 4. 添加到消息历史
    self.add_message("user", observation)
    return output
```

**执行流程：**
1. **查询阶段**：将当前消息历史发送给LLM，获取下一步命令
2. **解析阶段**：从LLM响应中提取PowerShell命令
3. **执行阶段**：在本地环境中执行命令
4. **观察阶段**：将执行结果格式化为观察反馈
5. **反馈阶段**：将观察结果添加到消息历史，供下一轮使用

### 5.3 循环终止条件

循环在以下情况下终止：

#### 5.3.1 任务完成（Submitted）

```python
def has_finished(self, output: dict[str, str]):
    """检查任务是否完成"""
    raw_output = output.get("output", "")
    lines = raw_output.splitlines(keepends=True)
    
    # 查找完成标志
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped in {"FIX_CODE_AGENT_FINAL_OUTPUT", "COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT"}:
            # 提取完成后的输出作为最终结果
            raise Submitted("".join(lines[marker_index + 1:]))
```

**完成标志**：当命令输出包含`COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT`时，认为任务完成。

#### 5.3.2 限制超出（LimitsExceeded）

```python
if 0 < self.config.step_limit <= self.model.n_calls:
    raise LimitsExceeded()
if 0 < self.config.cost_limit <= self.model.cost:
    raise LimitsExceeded()
```

**限制类型**：
- **步数限制**：限制最大执行步数
- **成本限制**：限制最大API调用成本

#### 5.3.3 格式错误（FormatError）

当LLM响应不符合格式要求时，抛出FormatError，触发重新提示。

#### 5.3.4 执行超时（ExecutionTimeoutError）

当命令执行超时时，抛出ExecutionTimeoutError，提示LLM使用其他方法。

### 5.4 交互式模式

`InteractiveAgent`扩展了基础Agent，增加了用户交互功能：

```python
class InteractiveAgent(DefaultAgent):
    def execute_action(self, action: dict) -> dict:
        # 根据模式决定是否需要用户确认
        if self.should_ask_confirmation(action["action"]):
            self.ask_confirmation()
        return super().execute_action(action)
```

**三种模式：**
- **human模式**：用户直接输入命令，不调用LLM
- **confirm模式**：LLM生成的命令需要用户确认后执行
- **yolo模式**：LLM生成的命令直接执行，无需确认

## 6. 完整执行示例

以下是一个完整的执行流程示例：

```
1. 初始化
   - 用户输入任务："修复bug.py中的语法错误"
   - 系统添加system提示词和task提示词到消息历史

2. 第一轮循环
   - LLM响应：分析代码库，查看bug.py文件
   - 执行命令：Get-Content bug.py
   - 观察结果：返回文件内容
   - 将观察结果添加到消息历史

3. 第二轮循环
   - LLM响应：发现第10行有语法错误，修复它
   - 执行命令：编辑文件，修复语法错误
   - 观察结果：文件已修改
   - 将观察结果添加到消息历史

4. 第三轮循环
   - LLM响应：运行测试验证修复
   - 执行命令：python bug.py
   - 观察结果：程序正常运行
   - 将观察结果添加到消息历史

5. 第四轮循环
   - LLM响应：任务完成
   - 执行命令：echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT
   - 检测到完成标志，终止循环
   - 返回最终结果
```

## 7. 关键技术特点

### 7.1 上下文保持

通过维护完整的消息历史，Agent能够：
- 记住之前的命令和结果
- 基于历史信息做出决策
- 从错误中学习并调整策略

### 7.2 错误恢复

系统设计了多层次的错误处理：
- **格式错误**：重新提示LLM，不中断循环
- **执行错误**：将错误信息反馈给LLM，让其调整策略
- **超时错误**：提示LLM使用更高效的方法

### 7.3 成本控制

通过成本追踪和限制机制：
- 实时追踪API调用成本
- 设置成本上限防止意外支出
- 支持动态调整限制

### 7.4 用户控制

交互式Agent提供多种控制方式：
- 命令确认机制
- 手动干预能力
- 模式切换功能

## 8. 总结

本Agent系统通过精心设计的Prompt模板、严格的格式验证、完整的消息历史管理和循环执行机制，实现了一个能够自主执行代码修复任务的智能助手。系统在保持灵活性的同时，通过多层错误处理和用户控制机制，确保了系统的可靠性和可控性。

