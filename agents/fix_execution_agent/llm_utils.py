import os
import requests
import re

class LLMFixer:
    """通用 LLM 修复工具，便于后续扩展不同大模型"""
    def __init__(self, api_key=None, model="deepseek-coder", base_url="https://api.deepseek.com/v1/chat/completions"):
        self.api_key = api_key or "sk-75db9bf464d44ee78b5d45a655431710"
        self.model = model
        self.base_url = base_url

    def fix_code(self, code, language, message):
        """
        调用 LLM 修复代码，返回修复后的纯代码
        """
        prompt = (
            f"请修复以下{language}代码中的问题：\n"
            f"{code}\n\n"
            f"# 问题描述：{message}\n"
            f"\n请只输出修复后的完整代码，不要任何解释、注释或 markdown 格式。"
        )
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是专业的代码修复助手。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 2048
        }
        resp = requests.post(self.base_url, headers=headers, json=data, timeout=60)
        resp.raise_for_status()
        result = resp.json()
        llm_content = result["choices"][0]["message"]["content"]
        code_match = re.search(r"```[a-zA-Z]*\n([\s\S]*?)```", llm_content)
        if code_match:
            llm_code = code_match.group(1).strip()
        else:
            llm_code = llm_content.strip()
        return llm_code

    def fix_code_multi(self, code: str, language: str, issues: list) -> str:
        """
        调用 LLM 修复代码（多问题汇总）；issues 为问题列表（含 message/line 等），返回修复后的纯代码
        """
        # 构建多问题说明
        summarized = []
        for i, issue in enumerate(issues, start=1):
            msg = issue.get("message", "")
            line = issue.get("line")
            symbol = issue.get("symbol") or issue.get("type")
            summarized.append(f"{i}. line={line}, type={symbol}, message={msg}")
        issues_text = "\n".join(summarized) if summarized else "无"

        prompt = (
            f"请基于以下{language}完整文件内容，修复下述所有问题：\n"
            f"\n===== 源代码 BEGIN =====\n{code}\n===== 源代码 END =====\n"
            f"\n===== 问题列表 BEGIN =====\n{issues_text}\n===== 问题列表 END =====\n"
            f"\n要求：\n"
            f"1) 保持原有功能不变；\n"
            f"2) 一次性修复所有问题；\n"
            f"3) 只输出修复后的完整代码，不要任何解释、注释或 markdown。\n"
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是专业的代码修复助手。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 4096
        }
        resp = requests.post(self.base_url, headers=headers, json=data, timeout=120)
        resp.raise_for_status()
        result = resp.json()
        llm_content = result["choices"][0]["message"]["content"]
        code_match = re.search(r"```[a-zA-Z]*\n([\s\S]*?)```", llm_content)
        if code_match:
            llm_code = code_match.group(1).strip()
        else:
            llm_code = llm_content.strip()
        return llm_code
