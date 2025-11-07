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
        # 支持两种数据格式：
        # 1. 旧格式: { 'file_path': <path>, 'issues': <list> }
        # 2. 新格式: { 'project_path': <path>, 'issues': <list>, 'decisions': <dict> }
        base_file_path = task_data.get("file_path") or task_data.get("project_path", "")
        issues: List[Dict[str, Any]] = task_data.get("issues", []) or []
        
        # 添加调试日志
        self.logger.info(f"🔧 修复Agent接收任务数据:")
        self.logger.info(f"   文件路径: {base_file_path}")
        self.logger.info(f"   问题数量: {len(issues)}")
        self.logger.info(f"   任务数据键: {list(task_data.keys())}")
        
        if not base_file_path:
            return {
                "success": False,
                "task_id": task_id,
                "fix_results": [],
                "total_issues": 0,
                "fixed_issues": 0,
                "failed_issues": 0,
                "skipped_issues": 0,
                "errors": ["未提供文件路径"],
                "timestamp": asyncio.get_event_loop().time(),
                "message": "修复失败：未提供文件路径"
            }

        # 确定项目根目录和输出目录
        # 如果base_file_path是目录，直接使用；如果是文件，使用其父目录
        if os.path.isdir(base_file_path):
            project_root = base_file_path
        else:
            project_root = os.path.dirname(base_file_path) if base_file_path else os.getcwd()
        
        # 输出文件夹：使用项目根目录下的output子目录
        output_dir = os.path.join(project_root, "output")
        
        # 创建输出目录（处理权限问题）
        try:
            os.makedirs(output_dir, exist_ok=True)
            self.logger.info(f"✅ 输出目录已创建: {output_dir}")
        except PermissionError as e:
            # 如果项目目录权限不足，尝试使用临时目录
            import tempfile
            output_dir = os.path.join(tempfile.gettempdir(), f"fix_output_{task_id[:8]}")
            os.makedirs(output_dir, exist_ok=True)
            self.logger.warning(f"⚠️ 项目目录权限不足，使用临时目录: {output_dir}")
            self.logger.warning(f"   原始错误: {e}")
        except Exception as e:
            self.logger.error(f"❌ 创建输出目录失败: {e}")
            return {
                "success": False,
                "task_id": task_id,
                "fix_results": [],
                "total_issues": len(issues),
                "fixed_issues": 0,
                "failed_issues": len(issues),
                "skipped_issues": 0,
                "errors": [f"创建输出目录失败: {str(e)}"],
                "timestamp": asyncio.get_event_loop().time(),
                "message": f"修复失败：无法创建输出目录"
            }

        # 将问题按文件聚合
        issues_by_file: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for issue in issues:
            # 获取问题所在的文件路径
            issue_file_path = issue.get("file_path") or issue.get("file")
            
            if issue_file_path:
                # 如果是绝对路径，直接使用
                if os.path.isabs(issue_file_path):
                    file_name = issue_file_path
                else:
                    # 如果是相对路径，相对于项目根目录
                    file_name = os.path.join(project_root, issue_file_path)
            else:
                # 如果没有文件路径信息，跳过这个问题
                self.logger.warning(f"⚠️ 问题缺少文件路径信息，跳过: {issue.get('message', 'unknown')[:50]}")
                continue
            
            # 规范化路径（处理Windows路径分隔符）
            file_name = os.path.normpath(file_name)
            
            # 验证文件是否存在
            if not os.path.exists(file_name):
                self.logger.warning(f"⚠️ 文件不存在，跳过: {file_name}")
                continue
                
            issues_by_file[file_name].append(issue)

        fix_results: List[Dict[str, Any]] = []
        errors: List[str] = []
        total_files = len(issues_by_file)
        processed_files = 0

        self.logger.info(f"{'='*60}")
        self.logger.info(f"🔧 修复Agent开始处理修复任务")
        self.logger.info(f"   任务ID: {task_id}")
        self.logger.info(f"   总文件数: {total_files}")
        self.logger.info(f"   总问题数: {len(issues)}")
        self.logger.info(f"   输出目录: {output_dir}")
        self.logger.info(f"{'='*60}")
        
        for file_index, (file_key, file_issues) in enumerate(issues_by_file.items(), 1):
            processed_files += 1
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"📄 [{file_index}/{total_files}] 正在处理文件: {file_key}")
            self.logger.info(f"   该文件的问题数量: {len(file_issues)}")
            self.logger.info(f"   进度: {processed_files}/{total_files} ({processed_files*100//total_files}%)")
            self.logger.info(f"{'='*60}")
        try:
                # file_key 已经是完整的文件路径
                abs_path = file_key
                self.logger.info(f"🔧 检查文件是否存在: {abs_path}")

                if not os.path.exists(abs_path):
                    self.logger.error(f"❌ 文件未找到: {abs_path}")
                    errors.append(f"文件未找到: {abs_path}")
                    continue

                self.logger.info(f"🔧 读取文件内容: {abs_path}")
                with open(abs_path, "r", encoding="utf-8") as f:
                    before_code = f.read()
                self.logger.info(f"🔧 文件内容长度: {len(before_code)}")

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
                try:
                    self.logger.info(f"🤖 开始调用LLM修复文件: {os.path.basename(abs_path)}")
                    self.logger.info(f"   修复前代码长度: {len(before_code)} 字符")
                    self.logger.info(f"   需要修复的问题数: {len(file_issues)}")
                    
                    # 显示问题详情
                    for idx, issue in enumerate(file_issues[:5], 1):  # 只显示前5个问题
                        line = issue.get("line", "N/A")
                        msg = issue.get("message", "")[:50]  # 截断消息
                        self.logger.info(f"   问题 {idx}: 第{line}行 - {msg}")
                    if len(file_issues) > 5:
                        self.logger.info(f"   ... 还有 {len(file_issues) - 5} 个问题")
                    
                    # 使用LLM修复（在后台线程中执行，避免阻塞事件循环）
                    self.logger.info(f"🤖 正在调用LLM API（这可能需要一些时间）...")
                    import concurrent.futures
                    loop = asyncio.get_event_loop()
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        after_code = await loop.run_in_executor(
                            executor,
                            lambda: self.llm.fix_code_multi(before_code, language, file_issues)
                        )
                    
                    self.logger.info(f"✅ LLM修复完成")
                    self.logger.info(f"   修复后代码长度: {len(after_code)} 字符")
                    self.logger.info(f"   代码变化: {len(after_code) - len(before_code):+d} 字符")
                    
                except Exception as e:
                    self.logger.error(f"❌ LLM修复失败: {abs_path}")
                    self.logger.error(f"   错误信息: {str(e)}")
                    import traceback
                    self.logger.error(f"   错误详情: {traceback.format_exc()}")
                    errors.append(f"修复失败: {e}")
                    continue

                # 输出文件路径
                base, ext = os.path.splitext(os.path.basename(abs_path))
                before_out = os.path.join(output_dir, f"{base}_before{ext}")
                after_out = os.path.join(output_dir, f"{base}_after{ext}")

                # 写出 before/after 文件
                self.logger.info(f"💾 正在保存修复结果文件...")
                with open(before_out, "w", encoding="utf-8") as bf:
                    bf.write(before_code)
                with open(after_out, "w", encoding="utf-8") as af:
                    af.write(after_code)
                
                # 获取绝对路径用于显示
                before_out_abs = os.path.abspath(before_out)
                after_out_abs = os.path.abspath(after_out)
                prompt_out_abs = os.path.abspath(prompt_out)

                # 输出完整路径到终端和日志
                self.logger.info(f"✅ 文件修复完成: {os.path.basename(abs_path)}")
                self.logger.info(f"   📁 修复前文件: {before_out_abs}")
                self.logger.info(f"   📁 修复后文件: {after_out_abs}")
                self.logger.info(f"   📝 提示词文件: {prompt_out_abs}")
                self.logger.info(f"   ✅ 已修复问题数: {len(file_issues)}")
                
                print(f"\n{'='*60}")
                print(f"✅ 修复完成: {os.path.basename(abs_path)}")
                print(f"📁 修复前: {before_out_abs}")
                print(f"📁 修复后: {after_out_abs}")
                print(f"📝 提示词: {prompt_out_abs}")
                print(f"✅ 已修复: {len(file_issues)} 个问题")
                print(f"{'='*60}\n")

                # 保存每个修复的问题的详细信息
                fixed_issues_details = []
                for issue in file_issues:
                    fixed_issues_details.append({
                        "line": issue.get("line", 0),
                        "message": issue.get("message", ""),
                        "severity": issue.get("severity", "info"),
                        "type": issue.get("type", "unknown"),
                        "tool": issue.get("tool", "unknown"),
                        "source": issue.get("source", "static"),
                        "file": issue.get("file") or issue.get("file_path", abs_path)
                    })
                
                fix_results.append({
                    "file": abs_path,
                    "before": before_out_abs,
                    "after": after_out_abs,
                    "prompt": prompt_out_abs,
                    "issues_fixed": len(file_issues),
                    "file_name": os.path.basename(abs_path),
                    "output_dir": output_dir,
                    "fixed_issues_details": fixed_issues_details  # 添加修复的问题详情
                })
            except Exception as e:
                errors.append(f"处理 {file_key} 失败: {e}")

        total_issues = len(issues)
        fixed_files = len(fix_results)
        total_fixed_issues = sum(r.get("issues_fixed", 0) for r in fix_results)
        
        # 生成修复结果摘要
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"🎉 修复任务完成！")
        self.logger.info(f"   任务ID: {task_id}")
        self.logger.info(f"   总问题数: {total_issues}")
        self.logger.info(f"   成功修复文件数: {fixed_files}/{total_files}")
        self.logger.info(f"   成功修复问题数: {total_fixed_issues}")
        self.logger.info(f"   失败问题数: {len(errors)}")
        self.logger.info(f"   输出目录: {output_dir}")
        
        if fix_results:
            self.logger.info(f"\n📁 修复结果文件位置:")
            for idx, result in enumerate(fix_results, 1):
                self.logger.info(f"   {idx}. {result.get('file_name', 'unknown')}")
                self.logger.info(f"      修复前: {result.get('before', 'N/A')}")
                self.logger.info(f"      修复后: {result.get('after', 'N/A')}")
        
        if errors:
            self.logger.warning(f"\n⚠️ 修复过程中的错误:")
            for idx, error in enumerate(errors, 1):
                self.logger.warning(f"   {idx}. {error}")
        
        self.logger.info(f"{'='*60}\n")
        
        return {
            "success": len(errors) == 0,
            "task_id": task_id,
            "fix_results": fix_results,
            "total_issues": total_issues,
            "total_files": total_files,
            "fixed_files": fixed_files,
            "fixed_issues": total_fixed_issues,
            "failed_issues": total_issues - total_fixed_issues,
            "skipped_issues": 0,
            "errors": errors,
            "output_dir": output_dir,
            "timestamp": asyncio.get_event_loop().time(),
            "message": f"修复完成: {fixed_files}/{total_files} 个文件, {total_fixed_issues}/{total_issues} 个问题" if not errors else f"修复完成但有错误: {fixed_files}/{total_files} 个文件, {total_fixed_issues}/{total_issues} 个问题",
        }
