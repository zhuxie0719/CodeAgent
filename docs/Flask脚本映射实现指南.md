# Flask 脚本映射实现指南

## 概述

本文档详细说明了 `compare_flask_bugs.py` 脚本的实现原理，包括金标数据管理、子域分类系统、检测结果映射等核心技术细节。

## 1. 金标数据管理

### 1.1 数据结构设计

金标数据采用内置字典结构，包含以下字段：

```python
{
    "flask#4024": {
        "difficulty": "simple",      # 难度：simple/medium/hard
        "capability": "S",           # 能力：S(静态)/A(AI辅助)/D(动态验证)
        "fixed_version": "2.0.1",   # 首次修复版本
        "url": "https://github.com/pallets/flask/issues/4024"
    }
}
```

### 1.2 Issue 分类策略

#### 简单问题（8条）- 静态可检类型（S）
- **类型注解问题**：`g` 的类型提示、顶层导出名可见性
- **API参数问题**：`send_file` 函数签名、参数重命名
- **命名约束问题**：蓝图命名规则、点号冲突检测

#### 中等问题（18条）- AI辅助类型（A）
- **蓝图路由问题**：URL前缀合并、嵌套蓝图注册
- **JSON行为问题**：`decimal.Decimal` 处理、编码策略
- **CLI加载问题**：懒加载错误处理、工厂函数支持

#### 困难问题（6条）- 动态验证类型（D）
- **异步上下文问题**：异步处理器生命周期、上下文交互
- **运行时顺序问题**：回调触发顺序、URL匹配时机
- **复杂验证问题**：多级蓝图前缀、嵌套命名冲突

## 2. 子域分类系统

### 2.1 子域定义

基于 Flask 2.0.x 变更记录，定义了9个主要子域：

```python
SUBDOMAINS = {
    "typing_decorators": "类型注解和装饰器问题",
    "blueprint_routing": "蓝图路由相关问题", 
    "helpers_send_file": "文件发送API问题",
    "cli_loader": "CLI加载器问题",
    "json_behavior": "JSON行为问题",
    "static_pathlike": "路径类型问题",
    "blueprint_naming": "蓝图命名问题",
    "blueprint_registration": "蓝图注册问题",
    "async_ctx_order": "异步上下文和顺序问题"
}
```

### 2.2 映射规则设计

#### 2.2.1 金标到子域的映射

```python
def gold_subdomain_distribution(gold):
    """将内置 issue 汇总为子域分布"""
    submap = {}
    for iid, meta in gold.items():
        url = meta["url"]
        num = int(url.rsplit("/", 1)[1])
        
        # 基于 Issue 编号的精确映射
        if num in (4019, 4069, 1091, 4037):
            key = "blueprint_routing"
        elif num in (4024, 4044, 4026):
            key = "helpers_send_file"
        elif num in (4093, 4104, 4098, 4295, 4040, 4020, 4060, 4095):
            key = "typing_decorators"
        # ... 更多映射规则
```

#### 2.2.2 检测结果到子域的映射

```python
def classify_issue_to_subdomain(issue: dict) -> str:
    """基于文件路径与消息关键词，将检测结果归类到子域"""
    path = (issue.get("file") or "").lower()
    msg = (issue.get("message") or "").lower()
    
    # 文件路径强信号
    if "/flask/blueprints.py" in path:
        if "blueprint" in msg or "url_prefix" in msg:
            return "blueprint_routing"
        if "name" in msg or "dotted" in msg:
            return "blueprint_naming"
        if "duplicate" in msg or "twice" in msg:
            return "blueprint_registration"
    
    # 关键词弱信号补充
    if "typing" in msg or "annotation" in msg:
        return "typing_decorators"
    if "send_file" in msg or "send_from_directory" in msg:
        return "helpers_send_file"
    # ... 更多分类规则
```

### 2.3 映射策略优化

#### 强信号优先原则
1. **文件路径匹配**：基于 Flask 源码结构，优先匹配具体文件
2. **关键词组合**：使用多个关键词的组合提高准确性
3. **上下文感知**：考虑消息的上下文信息

#### 弱信号补充机制
1. **关键词匹配**：当强信号不足时，使用关键词匹配
2. **规则优先级**：定义规则的优先级顺序
3. **默认分类**：无法分类时归入 "other" 类别

## 3. 检测结果处理

### 3.1 Issue ID 标准化

```python
def normalize_issue_id(value: str) -> str:
    """标准化 Issue ID 格式"""
    if value.startswith("https://github.com/pallets/flask/issues/"):
        num = value.rsplit("/", 1)[1]
        return f"flask#{num}" if num.isdigit() else ""
    if value.startswith("flask#"):
        return value
    if value.isdigit():
        return f"flask#{value}"
    return ""
```

### 3.2 检测结果聚合

```python
def aggregate_detected_by_subdomain(results) -> dict:
    """聚合检测结果到子域"""
    issues = results.get("issues", [])
    agg = {}
    for issue in issues:
        key = classify_issue_to_subdomain(issue)
        agg[key] = agg.get(key, 0) + 1
    return agg
```

## 4. 对比算法实现

### 4.1 精确匹配对比

```python
def compare_with_gold(detected_ids, gold):
    """精确的 Issue ID 对比"""
    gold_ids = set(gold.keys())
    tp = sorted(gold_ids & detected_ids)      # 真正例
    missing = sorted(gold_ids - detected_ids) # 假负例
    extra = sorted(detected_ids - gold_ids)   # 假正例
    
    precision = len(tp) / (len(tp) + len(extra)) if (len(tp) + len(extra)) else 0
    recall = len(tp) / (len(tp) + len(missing)) if (len(tp) + len(missing)) else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0
    
    return {"tp": tp, "missing": missing, "extra": extra, 
            "precision": precision, "recall": recall, "f1": f1}
```

### 4.2 子域聚合对比

```python
def compare_subdomain(results, gold):
    """子域聚合对比（不依赖 issue_id）"""
    gold_dist = gold_subdomain_distribution(gold)
    det_dist = aggregate_detected_by_subdomain(results)
    
    # 计算子域覆盖率
    hits = 0
    for k, support in gold_dist.items():
        if det_dist.get(k, 0) > 0:
            hits += 1
    covered = hits / len(gold_dist) if gold_dist else 0.0
    
    return gold_dist, det_dist, covered
```

## 5. 输出格式设计

### 5.1 三段式结构

#### 第一段：已知Issue vs 系统检测
```
已知Issue vs 系统检测:
----------------------------------------------------------------------
[OK] typing_decorators   : 已知  8, 预期可检测  8, 检测到   3 个
[MISS] blueprint_routing : 已知  4, 预期可检测  2, 未检测到
[SKIP] async_ctx_order   : 已知  4, 预期可检测  0, 预期无法检测
```

#### 第二段：总体检测率统计
```
----------------------------------------------------------------------
总体检测率: 9/26 (34.6%) - 基于所有已知Issue
预期检测率: 9/20 (45.0%) - 基于预期可检测Issue
```

#### 第三段：系统能力评估
```
[评估] 系统能力评估:
----------------------------------------------------------------------
[OK] 类型注解检测: 优秀 (静态分析) - 检测到 3 个
[WARN] 蓝图路由检测: 未检测到 (AI能力有限)
[SKIP] 异步上下文检测: 需要运行时分析（预期无法静态检测）

[建议] 改进建议:
----------------------------------------------------------------------
   1. [OK] 静态分析能力强 - 继续保持类型检查和API检测
   2. [WARN] 增强AI分析 - 提升对蓝图路由和JSON行为的理解
   3. [INFO] 增加动态检测 - 集成异步上下文和运行时检测工具
```

### 5.2 状态标识系统

- `[OK]`：成功检测到预期可检测的问题
- `[MISS]`：未检测到预期可检测的问题
- `[WARN]`：检测到意外问题或AI能力有限
- `[SKIP]`：预期无法检测的问题（如需要运行时验证）

## 6. 自动发现机制

### 6.1 报告文件搜索

```python
def load_latest_report():
    """加载最新的检测报告"""
    reports_dir = Path("api/reports")
    
    # 优先 bug_detection_report_*.json，其次 structured_*.json
    json_files = list(reports_dir.glob("bug_detection_report_*.json"))
    if not json_files:
        json_files = list(reports_dir.glob("structured_*.json"))
    
    # 按修改时间选择最新文件
    latest = max(json_files, key=lambda p: p.stat().st_mtime)
    return json.load(open(latest, "r", encoding="utf-8"))
```

### 6.2 搜索目录优先级

1. `api/reports` - 主要报告目录
2. `project/CodeAgent/api/reports` - 项目内报告目录
3. `project/CodeAgent/frontend/uploads` - 前端上传目录

## 7. 扩展性设计

### 7.1 新增子域

要添加新的子域，需要：

1. **更新子域定义**：
```python
SUBDOMAINS["new_domain"] = "新子域描述"
```

2. **添加映射规则**：
```python
# 在金标映射中添加
elif num in (new_issue_numbers):
    key = "new_domain"

# 在检测结果映射中添加
if "new_keyword" in msg:
    return "new_domain"
```

3. **更新能力评估**：
```python
# 在系统能力评估中添加相应的检查项
```

### 7.2 新增金标数据

要添加新的金标数据：

1. **在 `embedded_gold()` 函数中添加**：
```python
row(new_issue_id, "difficulty", "capability", "fixed_version")
```

2. **更新子域映射规则**：
```python
# 在 gold_subdomain_distribution 中添加映射
```

3. **更新文档**：
```markdown
# 在 Flask版本选择与Issue策略.md 中添加说明
```

## 8. 性能优化

### 8.1 缓存机制

- 金标数据在脚本启动时加载一次
- 子域映射结果可以缓存
- 报告文件按修改时间排序，避免重复扫描

### 8.2 内存优化

- 使用生成器处理大型报告文件
- 及时释放不需要的数据结构
- 避免重复的字符串操作

## 9. 错误处理

### 9.1 文件读取错误

```python
try:
    with open(latest, "r", encoding="utf-8") as f:
        return json.load(f)
except Exception as e:
    print(f"[错误] 读取报告失败: {e}")
    return None
```

### 9.2 数据格式错误

```python
def normalize_issue_id(value: str) -> str:
    try:
        # 标准化逻辑
        return normalized_id
    except Exception:
        return ""  # 返回空字符串表示无法处理
```

### 9.3 编码问题处理

- 统一使用 UTF-8 编码
- 移除 emoji 字符避免 Windows 控制台编码问题
- 使用 ASCII 兼容的状态标识

## 10. 测试与验证

### 10.1 单元测试

建议为以下函数编写单元测试：

- `normalize_issue_id()` - Issue ID 标准化
- `classify_issue_to_subdomain()` - 子域分类
- `gold_subdomain_distribution()` - 金标子域分布
- `compare_with_gold()` - 精确对比
- `compare_subdomain()` - 子域聚合对比

### 10.2 集成测试

- 使用真实的检测报告进行端到端测试
- 验证输出格式与 Pandas 脚本的一致性
- 测试各种边界情况和错误处理

### 10.3 性能测试

- 测试大型报告文件的处理性能
- 验证内存使用情况
- 测试并发访问的稳定性

## 11. 维护指南

### 11.1 定期更新

- 根据 Flask 新版本更新金标数据
- 根据检测能力提升调整子域映射规则
- 根据用户反馈优化输出格式

### 11.2 版本兼容性

- 保持与 Pandas 脚本的输出格式兼容
- 维护向后兼容性
- 提供迁移指南

### 11.3 文档维护

- 及时更新技术文档
- 保持示例代码的准确性
- 记录重要的设计决策

---

## 总结

`compare_flask_bugs.py` 脚本通过精心设计的子域分类系统和映射规则，实现了与 Pandas 脚本一致的输出格式，同时针对 Flask 项目的特殊性进行了优化。脚本具有良好的扩展性和维护性，能够适应未来需求的变化。
