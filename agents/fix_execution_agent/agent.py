import asyncio
import os
import subprocess
from typing import Dict, List, Any


class FixExecutionAgent:
    """修复执行AGENT - 统一处理代码修复任务"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.is_running = False

    async def start(self):
        """启动AGENT"""
        self.is_running = True
        print("修复执行AGENT已启动")

    async def stop(self):
        """停止AGENT"""
        self.is_running = False
        print("修复执行AGENT已停止")

    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理任务 - 接收完整的task JSON
        task 格式参考用户传入的JSON
        """
        try:
            task_id = task.get("task_id")
            project_path = os.path.dirname(task.get("file_path", ""))
            issues = []

            # 展开 issues_by_priority 中的缺陷
            issues_by_priority = task.get("issues_by_priority", {})
            for _, issue_list in issues_by_priority.items():
                issues.extend(issue_list)

            print(f"开始处理任务 {task_id}: {len(issues)} 个缺陷")

            # 执行修复
            fix_result = await self.process_issues(issues, project_path)
            return fix_result

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def process_issues(
        self, issues: List[Dict[str, Any]], project_path: str
    ) -> Dict[str, Any]:
        """按语言和type分类，格式化问题用对应工具修复，非格式化问题跳过"""
        results = {
            "total_issues": len(issues),
            "fixed_issues": 0,
            "failed_issues": 0,
            "skipped_issues": 0,
            "changes": [],
            "errors": [],
            "timestamp": asyncio.get_event_loop().time(),
        }

        print(f"开始处理 {len(issues)} 个缺陷...")

        # 1. 按语言和type分类
        format_files = {  # lang -> set(files)
            "python": set(),
            "java": set(),
            "javascript": set(),
            "c": set(),
            "cpp": set(),
            "go": set(),
        }
        format_issue_count = {}  # (lang, file) -> int
        non_format_issues = []

        for issue in issues:
            lang = issue.get("language", "").lower()
            file = issue.get("file")
            typ = issue.get("type", "other")
            if not file or lang not in format_files:
                non_format_issues.append(issue)
                continue
            if typ == "format":
                format_files[lang].add(file)
                format_issue_count[(lang, file)] = format_issue_count.get((lang, file), 0) + 1
            else:
                non_format_issues.append(issue)

        # 2. 处理格式化问题（每个文件只修一次，fixed_issues统计所有格式化问题数）
        fix_results_by_file = {}
        for lang, files in format_files.items():
            for file in files:
                try:
                    if lang == "python":
                        fix_results_by_file[(lang, file)] = await self.fix_python({"file": file}, project_path)
                    elif lang == "java":
                        fix_results_by_file[(lang, file)] = await self.fix_java({"file": file}, project_path)
                    elif lang == "javascript":
                        fix_results_by_file[(lang, file)] = await self.fix_javascript({"file": file}, project_path)
                    elif lang in ("c", "cpp"):
                        fix_results_by_file[(lang, file)] = await self.fix_cpp({"file": file}, project_path)
                    elif lang == "go":
                        fix_results_by_file[(lang, file)] = await self.fix_go({"file": file}, project_path)
                    else:
                        fix_results_by_file[(lang, file)] = {"success": False, "message": f"暂不支持{lang}格式化"}
                except Exception as e:
                    fix_results_by_file[(lang, file)] = {"success": False, "message": str(e)}

        # 3. 统计格式化问题
        for (lang, file), count in format_issue_count.items():
            result = fix_results_by_file.get((lang, file), {"success": False, "message": "未修复"})
            if result.get("success"):
                results["fixed_issues"] += count
                if result.get("changes"):
                    results["changes"].extend(result["changes"])
            else:
                results["failed_issues"] += count
                results["errors"].append(result.get("message", "未知错误"))

        # 4. 跳过非格式化问题
        for issue in non_format_issues:
            results["skipped_issues"] += 1
            msg = issue.get("message", "")
            results["changes"].append(f"跳过非格式化缺陷: {msg[:100]}")

        if results["total_issues"] > 0:
            results["success_rate"] = results["fixed_issues"] / results["total_issues"]
        else:
            results["success_rate"] = 0.0

        print(
            f"缺陷处理完成: 总计{results['total_issues']}, 修复{results['fixed_issues']}, 失败{results['failed_issues']}, 跳过{results['skipped_issues']}"
        )
        return results

    async def fix_java(self, issue: Dict[str, Any], project_path: str) -> Dict[str, Any]:
        """Java格式化: google-java-format + checkstyle (仅格式化)"""
        try:
            file_path = os.path.join(project_path, issue["file"])
            subprocess.run(["google-java-format", "-i", file_path], check=True)
            # checkstyle 可选，仅做格式检查
            return {
                "success": True,
                "changes": [f"Java文件已格式化: {file_path}"],
                "message": "google-java-format 格式化成功",
            }
        except Exception as e:
            return {"success": False, "changes": [], "message": f"Java格式化失败: {e}"}

    async def fix_javascript(self, issue: Dict[str, Any], project_path: str) -> Dict[str, Any]:
        """JavaScript格式化: eslint --fix + prettier"""
        try:
            file_path = os.path.join(project_path, issue["file"])
            subprocess.run(["eslint", "--fix", file_path], check=True)
            subprocess.run(["prettier", "--write", file_path], check=True)
            return {
                "success": True,
                "changes": [f"JavaScript文件已格式化: {file_path}"],
                "message": "eslint + prettier 格式化成功",
            }
        except Exception as e:
            return {"success": False, "changes": [], "message": f"JavaScript格式化失败: {e}"}

    async def fix_cpp(self, issue: Dict[str, Any], project_path: str) -> Dict[str, Any]:
        """C/C++格式化: clang-format (仅格式化)"""
        try:
            file_path = os.path.join(project_path, issue["file"])
            subprocess.run(["clang-format", "-i", file_path], check=True)
            return {
                "success": True,
                "changes": [f"C/C++文件已格式化: {file_path}"],
                "message": "clang-format 格式化成功",
            }
        except Exception as e:
            return {"success": False, "changes": [], "message": f"C/C++格式化失败: {e}"}

    async def fix_go(self, issue: Dict[str, Any], project_path: str) -> Dict[str, Any]:
        """Go格式化: gofmt + goimports"""
        try:
            file_path = os.path.join(project_path, issue["file"])
            subprocess.run(["gofmt", "-w", file_path], check=True)
            subprocess.run(["goimports", "-w", file_path], check=True)
            return {
                "success": True,
                "changes": [f"Go文件已格式化: {file_path}"],
                "message": "gofmt + goimports 格式化成功",
            }
        except Exception as e:
            return {"success": False, "changes": [], "message": f"Go格式化失败: {e}"}

    async def fix_python(self, issue: Dict[str, Any], project_path: str) -> Dict[str, Any]:
        """统一的Python自动修复流程：autoflake → isort → black"""
        try:
            file_path = os.path.join(project_path, issue["file"])

            # 1. 移除未使用变量和导入
            subprocess.run(
                ["autoflake", "--in-place", "--remove-unused-variables", file_path],
                check=True,
            )

            # 2. 格式化导入
            subprocess.run(["isort", file_path], check=True)

            # 3. 统一代码风格
            subprocess.run(["black", file_path], check=True)

            return {
                "success": True,
                "changes": [f"Python文件已自动修复: {file_path}"],
                "message": "autoflake + isort + black 修复成功",
            }

        except Exception as e:
            return {"success": False, "changes": [], "message": f"Python修复失败: {e}"}

    async def fix_with_llm(
        self, issue: Dict[str, Any], project_path: str
    ) -> Dict[str, Any]:
        """调用大模型修复非Python问题（这里保留伪逻辑）"""
        file_path = os.path.join(project_path, issue["file"])
        return {
            "success": False,
            "changes": [],
            "message": f"请用LLM修复 {issue.get('language', '')} 文件 {file_path} 的问题: {issue.get('message', '')}",
        }

    async def get_fix_summary(self, results: Dict[str, Any]) -> str:
        """生成修复摘要"""
        try:
            summary = f"""
修复执行摘要:
==============
总缺陷数: {results.get('total_issues', 0)}
成功修复: {results.get('fixed_issues', 0)}
修复失败: {results.get('failed_issues', 0)}
跳过处理: {results.get('skipped_issues', 0)}
成功率: {results.get('success_rate', 0):.1%}

修复详情:
"""

            if results.get("changes"):
                summary += "\n修复内容:\n"
                for change in results["changes"][:10]:
                    summary += f"- {change}\n"

                if len(results["changes"]) > 10:
                    summary += f"... 还有 {len(results['changes']) - 10} 个修复\n"

            if results.get("errors"):
                summary += "\n错误信息:\n"
                for error in results["errors"][:5]:
                    summary += f"- {error}\n"

                if len(results["errors"]) > 5:
                    summary += f"... 还有 {len(results['errors']) - 5} 个错误\n"

            return summary.strip()

        except Exception as e:
            return f"生成摘要失败: {e}"
