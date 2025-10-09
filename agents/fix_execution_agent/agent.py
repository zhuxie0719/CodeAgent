import asyncio
import os
from collections import defaultdict
from typing import Dict, List, Any, Optional

from ..base_agent import BaseAgent
from .llm_utils import LLMFixer


class FixExecutionAgent(BaseAgent):
    """LLM多问题修复实现：按文件聚合问题，生成 _before/_after 文件。"""

    def __init__(self, agent_id: str = "fix_execution_agent", config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, config or {})
        # API key硬编码
        self.llm = LLMFixer(
            api_key="sk-75db9bf464d44ee78b5d45a655431710",
            model=self.config.get("LLM_MODEL", "deepseek-coder"),
            base_url=self.config.get("LLM_BASE_URL", "https://api.deepseek.com/v1/chat/completions"),
        )

    async def initialize(self) -> bool:
        return True

    def get_capabilities(self) -> List[str]:
        return ["llm_multi_issue_fix", "write_before_after_files"]

    async def process_task(self, task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        # 期望 task_data: { 'file_path': <path>, 'issues': <list from bug_format.json> }
        base_file_path = task_data.get("file_path", "")
        issues: List[Dict[str, Any]] = task_data.get("issues", []) or []

        # 输出文件夹
        output_dir = os.path.join(os.path.dirname(base_file_path), "output")
        os.makedirs(output_dir, exist_ok=True)

        # 将问题按文件聚合
        issues_by_file: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for issue in issues:
            file_name = issue.get("file_path") or issue.get("file") or os.path.basename(base_file_path)
            issues_by_file[file_name].append(issue)

        fix_results: List[Dict[str, Any]] = []
        errors: List[str] = []

        for file_key, file_issues in issues_by_file.items():
            try:
                # 解析真实路径（如果 file_key 是相对名，则相对于 base_file_path 所在目录）
                if os.path.isabs(file_key):
                    abs_path = file_key
                else:
                    abs_dir = os.path.dirname(base_file_path)
                    abs_path = os.path.join(abs_dir, file_key)

                if not os.path.exists(abs_path):
                    errors.append(f"文件未找到: {abs_path}")
                    continue

                with open(abs_path, "r", encoding="utf-8") as f:
                    before_code = f.read()

                language = (file_key.split(".")[-1] or "text").lower()

                # 构建prompt
                summarized = []
                for i, issue in enumerate(file_issues, start=1):
                    msg = issue.get("message", "")
                    line = issue.get("line")
                    symbol = issue.get("symbol") or issue.get("type")
                    summarized.append(f"{i}. line={line}, type={symbol}, message={msg}")
                issues_text = "\n".join(summarized) if summarized else "无"
                # 添加 system role intent
                system_role = (
                    "You are an expert Python code refactoring assistant.\n"
                    "Your task is to fix all issues listed below without changing functionality.\n"
                )
                prompt = (
                    f"{system_role}"
                    f"请基于以下{language}完整文件内容，修复下述所有问题：\n"
                    f"\n===== 源代码 BEGIN =====\n{before_code}\n===== 源代码 END =====\n"
                    f"\n===== 问题列表 BEGIN =====\n{issues_text}\n===== 问题列表 END =====\n"
                    f"\n要求：\n"
                    f"1) 保持原有功能不变；\n"
                    f"2) 一次性修复所有问题；\n"
                    f"3) 只输出修复后的完整代码，不要任何解释、注释或 markdown。\n"
                )

                # 写出prompt到文件
                prompt_out = os.path.join(output_dir, f"{os.path.basename(abs_path)}_prompt.txt")
                with open(prompt_out, "w", encoding="utf-8") as pf:
                    pf.write(prompt)
                print(f"[LLM Prompt] 写入: {prompt_out}")

                # 调用LLM
                after_code = self.llm.fix_code_multi(before_code, language, file_issues)

                # 输出文件路径
                base, ext = os.path.splitext(os.path.basename(abs_path))
                before_out = os.path.join(output_dir, f"{base}_before{ext}")
                after_out = os.path.join(output_dir, f"{base}_after{ext}")

                # 写出 before/after 文件
                with open(before_out, "w", encoding="utf-8") as bf:
                    bf.write(before_code)
                with open(after_out, "w", encoding="utf-8") as af:
                    af.write(after_code)

                fix_results.append({
                    "file": abs_path,
                    "before": before_out,
                    "after": after_out,
                    "prompt": prompt_out,
                    "issues_fixed": len(file_issues),
                })
            except Exception as e:
                errors.append(f"处理 {file_key} 失败: {e}")

        total_issues = len(issues)
        fixed_files = len(fix_results)
        return {
            "success": len(errors) == 0,
            "task_id": task_id,
            "fix_results": fix_results,
            "total_issues": total_issues,
            "fixed_issues": total_issues if fixed_files > 0 else 0,
            "failed_issues": 0 if fixed_files > 0 else total_issues,
            "skipped_issues": 0,
            "errors": errors,
            "timestamp": asyncio.get_event_loop().time(),
            "message": "LLM multi-issue fix completed" if not errors else "LLM multi-issue fix completed with errors",
        }