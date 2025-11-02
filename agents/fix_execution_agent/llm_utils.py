"""
LLM修复工具
提供LLM代码修复功能
"""

import httpx
from typing import Dict, Any, Optional


class LLMFixer:
    """LLM代码修复工具"""
    
    def __init__(self, api_key: str, model: str = "deepseek-coder", base_url: str = "https://api.deepseek.com/v1/chat/completions"):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
    
    async def fix_code(self, code: str, issues: list, context: Optional[str] = None) -> str:
        """
        使用LLM修复代码
        
        Args:
            code: 原始代码
            issues: 问题列表
            context: 上下文信息
        
        Returns:
            修复后的代码
        """
        # 构建提示词
        prompt = self._build_fix_prompt(code, issues, context)
        
        # 调用LLM API
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(
                self.base_url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.2,
                    "max_tokens": 4000
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                fixed_code = result["choices"][0]["message"]["content"]
                # 清理可能的markdown代码块标记
                fixed_code = self._clean_code_output(fixed_code)
                return fixed_code
            else:
                raise Exception(f"LLM API调用失败: {response.status_code} - {response.text}")
    
    def fix_code_multi(self, code: str, language: str, issues: list) -> str:
        """
        使用LLM修复多个问题（同步版本，用于兼容现有代码）
        
        Args:
            code: 原始代码
            language: 编程语言
            issues: 问题列表
        
        Returns:
            修复后的代码
        """
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(self.fix_code(code, issues, f"语言: {language}"))
    
    def _clean_code_output(self, code: str) -> str:
        """清理LLM输出的代码，移除可能的markdown标记"""
        # 移除可能的 ```python 和 ``` 标记
        code = code.strip()
        if code.startswith("```"):
            # 移除开头的代码块标记
            lines = code.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            # 移除结尾的 ```
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            code = "\n".join(lines)
        return code.strip()
    
    def _build_fix_prompt(self, code: str, issues: list, context: Optional[str] = None) -> str:
        """构建修复提示词"""
        # 格式化问题列表
        issues_text = ""
        if isinstance(issues, list):
            for i, issue in enumerate(issues, 1):
                if isinstance(issue, dict):
                    issue_desc = issue.get("message", str(issue))
                    issue_file = issue.get("file", "")
                    issue_line = issue.get("line", 0)
                    issues_text += f"{i}. {issue_desc}"
                    if issue_file:
                        issues_text += f" (文件: {issue_file}"
                        if issue_line:
                            issues_text += f", 行: {issue_line}"
                        issues_text += ")"
                    issues_text += "\n"
                else:
                    issues_text += f"{i}. {issue}\n"
        else:
            issues_text = str(issues)
        
        prompt = f"""请修复以下代码中的所有问题：

代码：
```python
{code}
```

问题列表：
{issues_text}
"""
        if context:
            prompt += f"\n上下文信息：\n{context}\n"
        
        prompt += "\n要求：\n"
        prompt += "1) 保持原有功能不变；\n"
        prompt += "2) 一次性修复所有问题；\n"
        prompt += "3) 只输出修复后的完整代码，不要任何解释、注释或markdown。\n"
        
        return prompt

