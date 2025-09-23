# AI Agent 多语言代码检测系统

一个基于多Agent协作的智能软件开发系统，专注于多语言代码缺陷检测与AI智能分析。

## 🌟 主要特性

- **🌍 多语言支持**: Python, Java, C/C++, JavaScript, Go
- **🤖 AI智能分析**: 集成DeepSeek API进行智能代码分析
- **📁 项目级检测**: 支持大型项目文件上传和分析
- **📊 自然语言报告**: 生成专业的AI分析报告
- **🔧 实时检测**: 支持单文件和项目批量检测
- **📈 可视化界面**: 现代化的Web前端界面

## 🏗️ 系统架构

### 核心组件

1. **协调中心 (Coordinator)**
   - 任务分配和调度
   - Agent间通信协调
   - 工作流管理
   - 决策制定

2. **Agent团队**
   - **缺陷检测Agent**: 多语言代码缺陷检测，支持AI分析
   - **代码分析Agent**: 理解项目结构、代码逻辑和依赖关系
   - **修复执行Agent**: 根据检测结果自动生成和执行修复方案
   - **测试验证Agent**: 确保修复后的代码质量和功能正确性
   - **性能优化Agent**: 持续监控和优化应用性能
   - **代码质量Agent**: 维护代码质量和编码标准

3. **工具集成层**
   - 静态分析工具 (Pylint, Flake8, 自定义检测器)
   - AI分析工具 (DeepSeek API集成)
   - 多语言检测引擎
   - 项目分析工具

## 📁 项目结构

```
ai_agent_system/
├── agents/                          # Agent模块
│   ├── bug_detection_agent/         # 缺陷检测Agent
│   ├── code_analysis_agent/         # 代码分析Agent
│   ├── fix_execution_agent/         # 修复执行Agent
│   ├── test_validation_agent/       # 测试验证Agent
│   ├── performance_optimization_agent/ # 性能优化Agent
│   └── code_quality_agent/          # 代码质量Agent
├── coordinator/                     # 协调中心
│   ├── coordinator.py              # 主协调器
│   └── task_manager.py             # 任务管理器
├── tools/                          # 工具集成层
│   ├── static_analysis/            # 静态分析工具
│   ├── dynamic_testing/            # 动态测试工具
│   ├── code_generation/            # 代码生成工具
│   └── monitoring/                 # 监控工具
├── config/                         # 配置文件
│   ├── settings.py                 # 系统设置
│   └── agent_config.py             # Agent配置
├── api/                           # API接口层
│   ├── bug_detection_api.py       # 缺陷检测API
│   ├── deepseek_config.py         # DeepSeek配置
│   └── requirements.txt           # API依赖
├── frontend/                      # 前端界面
│   └── index.html                 # Web界面
├── demo/                          # 演示文件
├── tests/                         # 测试文件
├── docs/                          # 文档
├── main.py                        # 主程序入口
├── start_api.py                   # API启动脚本
└── README.md                      # 项目说明
```

## 🚀 快速开始

### 环境要求
- Python 3.8+
- 现代浏览器 (Chrome, Firefox, Safari, Edge)

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd ai_agent_system
```

2. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
pip install -r api/requirements.txt
```

4. **配置AI分析**
```bash
# 方法1: 环境变量
export DEEPSEEK_API_KEY="your_api_key_here"

# 方法2: 直接编辑配置文件
# 编辑 api/deepseek_config.py 文件
```

5. **启动系统**
```bash
# 启动API服务
python start_api.py

# 打开前端界面
# 浏览器访问: frontend/index.html
```

## 🌍 多语言支持

### 支持的语言
- **Python**: 使用 Pylint + Flake8 + 自定义检测器 + AI分析
- **Java**: 使用 AI分析检测空指针、内存泄漏等问题
- **C/C++**: 使用 AI分析检测缓冲区溢出、内存泄漏等问题
- **JavaScript/TypeScript**: 使用 AI分析检测 XSS、内存泄漏等问题
- **Go**: 使用 AI分析检测并发安全、错误处理等问题

### 检测类型
- **语法错误和编译问题**
- **逻辑错误和算法问题**
- **内存泄漏和资源管理问题**
- **安全漏洞和输入验证问题**
- **性能问题和优化建议**
- **代码规范和最佳实践问题**

## 📁 项目分析功能

### 支持的项目格式
- **压缩文件**: `.zip`, `.tar`, `.tar.gz`, `.rar`, `.7z`
- **目录**: 直接上传项目文件夹

### 项目分析特性
- **自动语言检测**: 根据文件扩展名和内容自动识别编程语言
- **并行分析**: 支持多文件并行检测，提高分析效率
- **文件过滤**: 自动过滤大文件和无关文件
- **结果合并**: 将多个文件的检测结果合并为统一报告

### 项目限制
- **最大项目大小**: 100MB
- **最大文件数量**: 1000个文件
- **单文件大小限制**: 10MB
- **每种语言最多分析**: 50个文件

## 🤖 AI智能分析

### AI分析优势
- **编译无关**: 不需要编译代码即可分析
- **跨语言**: 支持多种编程语言
- **智能检测**: 能够发现传统工具难以检测的问题
- **上下文理解**: 理解代码的业务逻辑和设计意图

### AI检测类型
1. **语法错误和编译问题**
2. **逻辑错误和算法问题**
3. **内存泄漏和资源管理问题**
4. **安全漏洞和输入验证问题**
5. **性能问题和优化建议**
6. **代码规范和最佳实践问题**

## 📊 使用方法

### 单文件分析
1. 选择"单文件分析"模式
2. 上传代码文件（支持多种语言）
3. 选择检测选项
4. 查看检测结果和AI报告

### 项目分析
1. 选择"项目分析"模式
2. 上传项目压缩包或文件夹
3. 系统自动解压和扫描
4. 查看多文件综合检测报告

## 📈 检测结果

### 结果格式
- **文件级别**: 每个文件的详细检测结果
- **项目级别**: 整个项目的综合统计
- **语言分类**: 按编程语言分类的检测结果
- **严重性分级**: 错误、警告、信息三个级别

### AI自然语言报告
- **总体评估**: 代码质量整体评价
- **主要问题分析**: 重点问题详细说明
- **改进建议**: 具体的修复建议
- **优先级排序**: 按重要性排序的问题列表

## 🔧 配置选项

### 检测选项
- **enable_static**: 启用自定义静态检测（Python）
- **enable_pylint**: 启用Pylint检测（Python）
- **enable_flake8**: 启用Flake8检测（Python）
- **enable_ai_analysis**: 启用AI分析（所有语言）

### 分析类型
- **file**: 单文件分析
- **project**: 项目分析

## 📝 示例

### Python文件检测
```python
# 上传 test.py 文件
# 系统使用 Pylint + Flake8 + 自定义检测器 + AI分析
# 返回详细的缺陷报告和AI自然语言分析
```

### Java项目检测
```bash
# 上传 java_project.zip
# 系统解压后扫描所有 .java 文件
# 使用AI分析每个文件
# 生成项目级别的综合报告
```

### 混合语言项目
```bash
# 上传包含 Python + Java + C++ 的项目
# 系统自动识别不同语言的文件
# 分别使用相应的检测工具
# 生成多语言综合报告
```

## 🎯 最佳实践

1. **选择合适的分析类型**: 单文件用于快速检测，项目用于全面分析
2. **启用AI分析**: 获得更智能的检测结果和修复建议
3. **关注高优先级问题**: 优先修复错误级别的问题
4. **定期检测**: 建议在代码提交前进行检测
5. **结合人工审查**: AI检测结果需要结合人工判断

## 📚 文档

- [API接口文档](API_DOCUMENTATION.md) - 详细的API使用说明
- [DeepSeek API指南](DEEPSEEK_API_GUIDE.md) - AI分析功能配置指南
- [Agent架构文档](AGENT_DOCUMENTATION.md) - 系统架构和Agent设计

## 🔮 未来扩展

- 支持更多编程语言（Rust, Swift, Kotlin等）
- 集成更多专业检测工具
- 支持自定义检测规则
- 提供代码修复建议
- 支持CI/CD集成

## 📄 许可证

本项目采用 MIT 许可证。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 GitHub Issue
- 发送邮件至项目维护者

---

*最后更新: 2024年*
