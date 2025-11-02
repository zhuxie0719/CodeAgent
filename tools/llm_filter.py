"""
智能误报过滤工具
使用大模型API对静态分析工具的输出进行二次判断，过滤误报
"""

import json
import re
import asyncio
import hashlib
from typing import Dict, List, Any, Optional
from pathlib import Path
import httpx
from api.deepseek_config import deepseek_config


class FalsePositiveFilter:
    """使用LLM过滤静态分析的误报"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化误报过滤器
        
        Args:
            config: 配置字典，包含：
                - confidence_threshold: 置信度阈值 (默认0.7)
                - batch_size: 批量处理大小 (默认20)
                - enabled: 是否启用 (默认True)
                - model: 使用的模型 (默认"deepseek-chat")
                - cache_enabled: 是否启用缓存 (默认True)
        """
        self.config_obj = deepseek_config
        self.config = config or {}
        
        # 配置参数
        self.confidence_threshold = self.config.get("confidence_threshold", 0.7)
        self.batch_size = self.config.get("batch_size", 20)
        self.enabled = self.config.get("enabled", True)
        self.model = self.config.get("model", "deepseek-chat")
        self.cache_enabled = self.config.get("cache_enabled", True)
        
        # 缓存（简单的内存缓存，可扩展为持久化）
        self.cache = {} if self.cache_enabled else None
        
        # Flask 2.0.0 已知问题列表（用于提高判断准确性）
        self.known_flask_issues = [
            "蓝图嵌套命名", "蓝图重复注册", "蓝图URL前缀合并",
            "send_from_directory参数", "Config.from_json",
            "类型注解", "jsonify Decimal", "CLI loader",
            "static_folder PathLike", "errorhandler",
            "before_request", "回调顺序", "上下文边界"
        ]
    
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一个专业的Python和Flask代码审查助手。你的任务是准确判断静态分析工具报告的问题是否为真实的代码缺陷，过滤掉误报。

你熟悉Flask 2.0.0的已知问题类型，包括：
- 类型注解问题（如errorhandler、before_request装饰器的类型注解）
- 蓝图注册问题（嵌套蓝图命名、重复注册、URL前缀合并）
- API一致性问题（参数重命名、方法缺失）
- 上下文相关问题（回调顺序、上下文边界）

判断标准：
1. 这个问题是否会导致运行时错误或不符合预期的行为？
2. 是否符合Flask 2.0.0已知的32个问题类型之一？
3. 是否为类型系统过于严格导致的误报？
4. 代码是否有明确的错误逻辑，还是仅仅是代码风格问题？

请以JSON格式回复你的判断结果。"""
    
    def _build_filter_prompt(self, issue: Dict[str, Any], source_code: str) -> str:
        """
        构建过滤提示词
        
        Args:
            issue: 问题详情字典
            source_code: 相关源码片段
        """
        tool = issue.get('tool', 'unknown')
        file_path = issue.get('file', 'unknown')
        line = issue.get('line', 0)
        message = issue.get('message', '')
        severity = issue.get('severity', 'warning')
        issue_type = issue.get('type', '')
        
        # 限制源码长度
        if len(source_code) > 2000:
            source_code = source_code[:1000] + "\n... (代码过长，已截断) ...\n" + source_code[-500:]
        
        prompt = f"""请判断以下静态分析问题是否为真实缺陷（而非误报）：

**问题详情：**
- 工具：{tool}
- 文件：{file_path}
- 行号：{line}
- 严重程度：{severity}
- 类型：{issue_type}
- 消息：{message}

**相关代码：**
```python
{source_code}
```

**判断要求：**
1. 这个问题是否会导致运行时错误或不符合预期的行为？
2. 是否符合Flask 2.0.0已知的32个问题类型之一？
3. 是否为类型系统过于严格导致的误报？
4. 代码是否有明确的错误逻辑，还是仅仅是代码风格问题？

请以JSON格式回复：
{{
    "is_real_issue": true/false,
    "confidence": 0.0-1.0,
    "reason": "判断理由（简要说明）"
}}"""
        
        return prompt
    
    def _build_batch_prompt(self, issues: List[Dict[str, Any]], source_code: str) -> str:
        """
        构建批量过滤提示词
        
        Args:
            issues: 问题列表
            source_code: 源码
        """
        # 限制源码长度
        if len(source_code) > 3000:
            source_code = source_code[:1500] + "\n... (代码过长，已截断) ...\n" + source_code[-1000:]
        
        issues_summary = []
        for idx, issue in enumerate(issues, 1):
            issues_summary.append(f"""
问题 {idx}:
- 工具：{issue.get('tool', 'unknown')}
- 行号：{issue.get('line', 0)}
- 严重程度：{issue.get('severity', 'warning')}
- 消息：{issue.get('message', '')}
""")
        
        prompt = f"""请批量判断以下静态分析问题是否为真实缺陷（而非误报）：

**文件代码：**
```python
{source_code}
```

**待判断的问题：**
{''.join(issues_summary)}

**判断要求：**
1. 每个问题是否会导致运行时错误或不符合预期的行为？
2. 是否符合Flask 2.0.0已知的32个问题类型之一？
3. 是否为类型系统过于严格导致的误报？

请以JSON数组格式回复，按顺序对应每个问题：
[
    {{
        "is_real_issue": true/false,
        "confidence": 0.0-1.0,
        "reason": "判断理由"
    }},
    ...
]"""
        
        return prompt
    
    def _get_cache_key(self, issue: Dict[str, Any], source_code: str) -> str:
        """生成缓存键"""
        # 使用问题的关键信息生成哈希
        key_data = f"{issue.get('tool')}:{issue.get('file')}:{issue.get('line')}:{issue.get('message')}"
        key_data += source_code[:500]  # 包含部分源码
        return hashlib.md5(key_data.encode('utf-8')).hexdigest()
    
    async def _call_llm_api(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        调用LLM API
        
        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
        
        Returns:
            LLM返回的文本内容
        """
        if not self.config_obj.is_configured():
            raise ValueError("LLM API未配置，请设置API密钥")
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.config_obj.base_url}/chat/completions",
                    headers=self.config_obj.get_headers(),
                    json={
                        "model": self.model,
                        "messages": messages,
                        "max_tokens": 2000,
                        "temperature": 0.1,  # 降低随机性，提高一致性
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result["choices"][0]["message"]["content"]
                else:
                    error_msg = f"LLM API调用失败: {response.status_code} - {response.text}"
                    raise RuntimeError(error_msg)
                    
        except Exception as e:
            raise RuntimeError(f"LLM API调用异常: {str(e)}")
    
    def _parse_judgment(self, judgment: str) -> Dict[str, Any]:
        """
        解析LLM返回的判断结果
        
        Args:
            judgment: LLM返回的文本
        
        Returns:
            解析后的判断结果字典
        """
        try:
            # 尝试提取JSON
            json_patterns = [
                r'```json\s*(\{.*?\})\s*```',  # 单个对象
                r'```json\s*(\[.*?\])\s*```',  # 数组
                r'(\{.*?\})',  # 直接对象
                r'(\[.*?\])',  # 直接数组
            ]
            
            json_content = None
            for pattern in json_patterns:
                match = re.search(pattern, judgment, re.DOTALL)
                if match:
                    json_content = match.group(1)
                    break
            
            if not json_content:
                # 尝试直接解析整个文本
                json_content = judgment.strip()
            
            result = json.loads(json_content)
            
            # 处理单个对象
            if isinstance(result, dict):
                return {
                    "is_real_issue": result.get("is_real_issue", False),
                    "confidence": float(result.get("confidence", 0.5)),
                    "reason": result.get("reason", "")
                }
            
            # 处理数组（批量结果）
            if isinstance(result, list):
                return result
            
        except json.JSONDecodeError as e:
            # JSON解析失败，尝试文本解析
            judgment_lower = judgment.lower()
            if "true" in judgment_lower or "real" in judgment_lower:
                confidence = 0.7
                if "high" in judgment_lower or "strong" in judgment_lower:
                    confidence = 0.9
                elif "low" in judgment_lower or "weak" in judgment_lower:
                    confidence = 0.5
                
                return {
                    "is_real_issue": True,
                    "confidence": confidence,
                    "reason": "LLM判断为真实问题"
                }
            else:
                return {
                    "is_real_issue": False,
                    "confidence": 0.3,
                    "reason": "LLM判断为误报"
                }
        
        return {
            "is_real_issue": False,
            "confidence": 0.0,
            "reason": "无法解析LLM响应"
        }
    
    async def filter_issue(self, issue: Dict[str, Any], source_code: str) -> Optional[Dict[str, Any]]:
        """
        过滤单个问题
        
        Args:
            issue: 问题详情
            source_code: 相关源码
        
        Returns:
            如果为真实问题则返回增强后的问题字典，否则返回None
        """
        if not self.enabled:
            return issue
        
        # 检查缓存
        if self.cache is not None:
            cache_key = self._get_cache_key(issue, source_code)
            if cache_key in self.cache:
                cached_result = self.cache[cache_key]
                if cached_result["is_real_issue"] and cached_result["confidence"] >= self.confidence_threshold:
                    issue["llm_confidence"] = cached_result["confidence"]
                    issue["llm_reason"] = cached_result.get("reason", "")
                    return issue
                else:
                    return None
        
        try:
            # 构建提示词
            prompt = self._build_filter_prompt(issue, source_code)
            system_prompt = self._get_system_prompt()
            
            # 调用LLM
            judgment_text = await self._call_llm_api(prompt, system_prompt)
            
            # 解析结果
            judgment = self._parse_judgment(judgment_text)
            
            # 如果是批量结果（列表），取第一个
            if isinstance(judgment, list) and len(judgment) > 0:
                judgment = judgment[0]
            
            # 缓存结果
            if self.cache is not None:
                self.cache[cache_key] = judgment
            
            # 判断是否保留
            if judgment.get("is_real_issue") and judgment.get("confidence", 0.0) >= self.confidence_threshold:
                issue["llm_confidence"] = judgment.get("confidence", 0.5)
                issue["llm_reason"] = judgment.get("reason", "")
                return issue
            else:
                return None
                
        except Exception as e:
            # API调用失败，保留原问题但添加警告标记
            issue["llm_filter_error"] = str(e)
            issue["llm_confidence"] = 0.5  # 默认置信度
            return issue
    
    async def filter_issues(self, static_results: List[Dict[str, Any]], 
                          source_code_provider: callable) -> List[Dict[str, Any]]:
        """
        过滤问题列表
        
        Args:
            static_results: 静态工具输出的问题列表
            source_code_provider: 函数，接收file_path返回源码
        
        Returns:
            过滤后的高置信度问题列表
        """
        if not self.enabled:
            return static_results
        
        filtered = []
        
        # 按文件分组
        issues_by_file = {}
        for issue in static_results:
            file_path = issue.get('file', '')
            if file_path not in issues_by_file:
                issues_by_file[file_path] = []
            issues_by_file[file_path].append(issue)
        
        # 逐个文件处理
        for file_path, issues in issues_by_file.items():
            try:
                source_code = source_code_provider(file_path)
            except:
                source_code = ""  # 如果无法读取源码，使用空字符串
            
            # 对每个问题调用过滤器
            for issue in issues:
                filtered_issue = await self.filter_issue(issue, source_code)
                if filtered_issue:
                    filtered.append(filtered_issue)
        
        return filtered
    
    async def filter_issues_batch(self, static_results: List[Dict[str, Any]], 
                                 source_code_provider: callable) -> List[Dict[str, Any]]:
        """
        批量过滤问题列表（优化版本，减少API调用次数）
        
        Args:
            static_results: 静态工具输出的问题列表
            source_code_provider: 函数，接收file_path返回源码
        
        Returns:
            过滤后的高置信度问题列表
        """
        if not self.enabled:
            return static_results
        
        filtered = []
        
        # 按文件分组
        issues_by_file = {}
        for issue in static_results:
            file_path = issue.get('file', '')
            if file_path not in issues_by_file:
                issues_by_file[file_path] = []
            issues_by_file[file_path].append(issue)
        
        # 按文件批量处理
        for file_path, issues in issues_by_file.items():
            try:
                source_code = source_code_provider(file_path)
            except:
                source_code = ""
            
            # 将问题分批
            for i in range(0, len(issues), self.batch_size):
                batch = issues[i:i + self.batch_size]
                
                # 检查缓存
                cached_results = []
                uncached_issues = []
                
                for issue in batch:
                    if self.cache is not None:
                        cache_key = self._get_cache_key(issue, source_code)
                        if cache_key in self.cache:
                            cached_results.append((issue, self.cache[cache_key]))
                        else:
                            uncached_issues.append(issue)
                    else:
                        uncached_issues.append(issue)
                
                # 处理缓存结果
                for issue, cached_judgment in cached_results:
                    if cached_judgment.get("is_real_issue") and cached_judgment.get("confidence", 0.0) >= self.confidence_threshold:
                        issue["llm_confidence"] = cached_judgment.get("confidence", 0.5)
                        issue["llm_reason"] = cached_judgment.get("reason", "")
                        filtered.append(issue)
                
                # 批量处理未缓存的问题
                if uncached_issues:
                    try:
                        batch_prompt = self._build_batch_prompt(uncached_issues, source_code)
                        system_prompt = self._get_system_prompt()
                        
                        judgment_text = await self._call_llm_api(batch_prompt, system_prompt)
                        judgments = self._parse_judgment(judgment_text)
                        
                        # 确保judgments是列表
                        if isinstance(judgments, dict):
                            judgments = [judgments]
                        
                        # 处理每个判断结果
                        for issue, judgment in zip(uncached_issues, judgments[:len(uncached_issues)]):
                            # 如果是单个字典，直接使用；如果是列表，取对应索引
                            if isinstance(judgment, list):
                                judgment = judgment[0] if judgment else {}
                            
                            # 缓存结果
                            if self.cache is not None:
                                cache_key = self._get_cache_key(issue, source_code)
                                self.cache[cache_key] = judgment
                            
                            # 判断是否保留
                            if judgment.get("is_real_issue") and judgment.get("confidence", 0.0) >= self.confidence_threshold:
                                issue["llm_confidence"] = judgment.get("confidence", 0.5)
                                issue["llm_reason"] = judgment.get("reason", "")
                                filtered.append(issue)
                    
                    except Exception as e:
                        # 批量处理失败，回退到单个处理或保留原问题
                        self.config.get("logger", print)(f"批量过滤失败，回退处理: {e}")
                        for issue in uncached_issues:
                            issue["llm_filter_error"] = str(e)
                            issue["llm_confidence"] = 0.5
                            filtered.append(issue)  # 失败时保留原问题
        
        return filtered


# 全局单例实例
_false_positive_filter = None

def get_false_positive_filter(config: Optional[Dict[str, Any]] = None) -> FalsePositiveFilter:
    """获取误报过滤器单例"""
    global _false_positive_filter
    if _false_positive_filter is None:
        _false_positive_filter = FalsePositiveFilter(config)
    return _false_positive_filter

