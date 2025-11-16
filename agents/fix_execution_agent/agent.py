import asyncio
import os
import subprocess
import sys
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
    
    def _resolve_temp_extract_path(self, path: str) -> str:
        """Resolve temp_extract paths to actual location at ../../api/temp_extract"""
        if path.startswith("temp_extract"):
            agent_dir = os.path.dirname(os.path.abspath(__file__))
            api_dir = os.path.join(agent_dir, "..", "..", "api")
            api_dir = os.path.abspath(api_dir)
            # Replace temp_extract and normalize the entire path to fix mixed slashes
            resolved = path.replace("temp_extract", os.path.join(api_dir, "temp_extract"), 1)
            # Normalize to fix mixed slashes (forward/backward)
            resolved = os.path.normpath(resolved)
            return resolved
        return path

    async def initialize(self) -> bool:
        return True

    def get_capabilities(self) -> List[str]:
        return ["llm_multi_issue_fix", "write_before_after_files"]

    async def process_task(self, task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        # 支持两种数据格式：
        # 1. 旧格式: { 'file_path': <path>, 'issues': <list> }
        # 2. 新格式: { 'project_path': <path>, 'issues': <list>, 'decisions': <dict> }
        self.logger.info("**************************************************************************")
        base_file_path = task_data.get("file_path") or task_data.get("project_path", "")
        issues: List[Dict[str, Any]] = task_data.get("issues", []) or []
        print(task_data)

        
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
        # Fix path: temp_extract is actually at ../../api/temp_extract relative to agent code
        original_path = base_file_path
        base_file_path = self._resolve_temp_extract_path(base_file_path)
        base_file_path = os.path.normpath(base_file_path)  # Normalize after resolution
        if base_file_path != original_path:
            self.logger.info(f"🔧 路径修正: {original_path} -> {base_file_path}")
        
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

        # Track skipped issues during validation
        skipped_issues: List[Dict[str, Any]] = []  # 追踪被跳过的问题及其原因
        
        # First pass: validate all issues and track skipped ones
        for issue in issues:
            # 获取问题所在的文件路径
            issue_file_path = issue.get("file_path") or issue.get("file")
            
            if not issue_file_path:
                # 如果没有文件路径信息，跳过这个问题
                skip_reason = "缺少文件路径信息"
                self.logger.warning(f"⚠️ 问题缺少文件路径信息，跳过: {issue.get('message', 'unknown')[:50]}")
                skipped_issues.append({
                    "issue": issue,
                    "reason": skip_reason,
                    "file_path": None
                })
                continue
            
            # 规范化路径处理
            # Fix path: if path starts with temp_extract, resolve it to ../../api/temp_extract
            issue_file_path = self._resolve_temp_extract_path(issue_file_path)
            
            if os.path.isabs(issue_file_path):
                # 已经是绝对路径
                file_name = os.path.normpath(issue_file_path)
                # 检查路径是否包含project_root（避免重复嵌套）
                if project_root not in file_name:
                    # 路径不包含项目路径，但已经是绝对路径，直接使用
                    self.logger.info(f"🔧 绝对路径不包含项目根目录，直接使用: {file_name}")
            else:
                # 相对路径，需要拼接项目根目录
                # 先规范化相对路径，移除开头的./或../
                issue_file_path = issue_file_path.lstrip('./').lstrip('../')
                file_name = os.path.normpath(os.path.join(project_root, issue_file_path))
            
            # 再次规范化路径
            file_name = os.path.normpath(file_name)
            
            # 处理路径重复嵌套问题（如 temp_extract/project_xxx/temp_extract/project_xxx/file.py）
            # 检测并移除重复的路径段序列
            path_parts = file_name.split(os.sep)
            
            # 查找重复的路径段序列
            if len(path_parts) > 2:
                # 从最大可能的模式长度开始检查（最多检查到路径长度的一半）
                max_pattern_len = min(len(path_parts) // 2, 10)  # 限制最大模式长度为10，避免性能问题
                
                for pattern_len in range(max_pattern_len, 0, -1):  # 从大到小检查，优先处理长的重复模式
                    if len(path_parts) < pattern_len * 2:
                        continue
                    
                    # 检查前pattern_len个段是否与接下来的pattern_len个段相同
                    pattern = path_parts[:pattern_len]
                    next_pattern = path_parts[pattern_len:pattern_len * 2]
                    
                    if pattern == next_pattern:
                        # 找到重复模式，移除重复的部分
                        self.logger.info(f"🔧 检测到路径重复嵌套，移除重复段: {os.sep.join(pattern)}")
                        file_name = os.sep.join(path_parts[pattern_len:])
                        file_name = os.path.normpath(file_name)
                        break
                
                # 如果路径看起来异常长，记录日志
                if len(path_parts) > 10:
                    self.logger.warning(f"⚠️ 路径异常长 ({len(path_parts)} 段)，可能存在路径问题: {file_name[:200]}")
            
            # 验证文件是否存在
            if not os.path.exists(file_name):
                skip_reason = f"文件不存在: {file_name}"
                self.logger.warning(f"⚠️ 文件不存在，跳过: {file_name}")
                self.logger.warning(f"   项目根目录: {project_root}")
                self.logger.warning(f"   原始路径: {issue_file_path}")
                skipped_issues.append({
                    "issue": issue,
                    "reason": skip_reason,
                    "file_path": file_name,
                    "original_path": issue_file_path
                })
                continue

        fix_results: List[Dict[str, Any]] = []
        errors: List[str] = []
        failed_issues_details: List[Dict[str, Any]] = []  # 追踪修复失败的问题详情
        
        # Process issues one by one instead of grouping by file
        total_issues_to_process = len(issues) - len(skipped_issues)
        processed_issues = 0

        self.logger.info(f"{'='*60}")
        self.logger.info(f"🔧 修复Agent开始处理修复任务")
        self.logger.info(f"   任务ID: {task_id}")
        self.logger.info(f"   总问题数: {len(issues)}")
        self.logger.info(f"   需要处理的问题数: {total_issues_to_process}")
        self.logger.info(f"   跳过的问题数: {len(skipped_issues)}")
        self.logger.info(f"   输出目录: {output_dir}")
        self.logger.info(f"   使用 fix-code-agent 逐个修复问题")
        self.logger.info(f"{'='*60}")
        
        # Process each issue individually
        for issue_index, issue in enumerate(issues, 1):
            # Skip if this issue was already skipped during path validation
            issue_file_path = issue.get("file_path") or issue.get("file")
            if not issue_file_path:
                continue  # Already handled in skipped_issues
            
            # Normalize path for comparison
            # Fix path: if path starts with temp_extract, resolve it to ../../api/temp_extract
            issue_file_path = self._resolve_temp_extract_path(issue_file_path)
            
            if os.path.isabs(issue_file_path):
                normalized_path = os.path.normpath(issue_file_path)
            else:
                issue_file_path_clean = issue_file_path.lstrip('./').lstrip('../')
                normalized_path = os.path.normpath(os.path.join(project_root, issue_file_path_clean))
            
            # Check if this issue was skipped by comparing normalized file_path and line
            is_skipped = any(
                skipped.get("file_path") == normalized_path and 
                skipped.get("issue", {}).get("line") == issue.get("line")
                for skipped in skipped_issues
            )
            if is_skipped:
                continue
            
            processed_issues += 1
            issue_message = issue.get("message", "")
            issue_line = issue.get("line", "N/A")
            issue_file = issue.get("file") or issue.get("file_path", "unknown")
            
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"🔧 [{issue_index}/{len(issues)}] 正在处理问题")
            self.logger.info(f"   文件: {issue_file}")
            self.logger.info(f"   行号: {issue_line}")
            self.logger.info(f"   问题: {issue_message[:100]}...")
            self.logger.info(f"   进度: {processed_issues}/{total_issues_to_process} ({processed_issues*100//max(total_issues_to_process, 1)}%)")
            self.logger.info(f"{'='*60}")
            
            try:
                # Normalize file path
                # Fix path: if path starts with temp_extract, resolve it to ../../api/temp_extract
                issue_file_path = self._resolve_temp_extract_path(issue_file_path)
                
                if os.path.isabs(issue_file_path):
                    abs_path = os.path.normpath(issue_file_path)
                else:
                    issue_file_path = issue_file_path.lstrip('./').lstrip('../')
                    abs_path = os.path.normpath(os.path.join(project_root, issue_file_path))
                
                # Handle path duplication (same logic as before)
                path_parts = abs_path.split(os.sep)
                if len(path_parts) > 2:
                    max_pattern_len = min(len(path_parts) // 2, 10)
                    for pattern_len in range(max_pattern_len, 0, -1):
                        if len(path_parts) < pattern_len * 2:
                            continue
                        pattern = path_parts[:pattern_len]
                        next_pattern = path_parts[pattern_len:pattern_len * 2]
                        if pattern == next_pattern:
                            abs_path = os.sep.join(path_parts[pattern_len:])
                            abs_path = os.path.normpath(abs_path)
                            break
                
                # Verify file exists
                if not os.path.exists(abs_path):
                    error_msg = f"文件不存在: {abs_path}"
                    self.logger.error(f"❌ {error_msg}")
                    errors.append(error_msg)
                    failed_issues_details.append({
                        "issue": issue,
                        "file": abs_path,
                        "reason": error_msg,
                        "status": "file_not_found"
                    })
                    continue
                
                # Save before state
                with open(abs_path, "r", encoding="utf-8") as f:
                    before_code = f.read()
                
                # Prepare comprehensive task description for fix-code-agent
                # Include information from original_task and task_data
                task_parts = []
                
                # Main issue message
                if issue_message:
                    task_parts.append(f"Task: {issue_message}")
                else:
                    task_parts.append(f"Fix the issue at line {issue_line} in {os.path.basename(abs_path)}")
                
                # Add context from original_task if available
                original_task = issue.get("original_task", {})
                if original_task:
                    task_parts.append("\nContext Information:")
                    
                    problem_file = original_task.get("problem_file")
                    if problem_file:
                        task_parts.append(f"Problem File: {problem_file}")
                    
                    orig_project_root = original_task.get("project_root")
                    if orig_project_root:
                        task_parts.append(f"Project Root: {orig_project_root}")
                    
                    agent_test_path = original_task.get("agent_test_path")
                    if agent_test_path:
                        task_parts.append(f"Agent Test Path: {agent_test_path}")
                    
                    backup_agent_path = original_task.get("backup_agent_path")
                    if backup_agent_path:
                        task_parts.append(f"Backup Agent Path: {backup_agent_path}")
                    
                    defect_info = original_task.get("defect_info", {})
                    if defect_info:
                        task_parts.append(f"Defect Info: {defect_info}")
                
                # Add file path information
                task_parts.append(f"\nFile to fix: {abs_path}")
                task_parts.append(f"Line number: {issue_line}")
                
                # Add issue metadata
                if issue.get("severity"):
                    task_parts.append(f"Severity: {issue.get('severity')}")
                if issue.get("type"):
                    task_parts.append(f"Issue Type: {issue.get('type')}")
                if issue.get("tool"):
                    task_parts.append(f"Detection Tool: {issue.get('tool')}")
                
                # Add decisions from task_data if available
                decisions = task_data.get("decisions", {})
                if decisions:
                    task_parts.append(f"\nDecisions: {decisions}")
                
                task_description = "\n".join(task_parts)
                
                # Save task description to a file (use absolute path)
                task_file = os.path.abspath(os.path.join(output_dir, f"task_{issue_index}.txt"))
                with open(task_file, "w", encoding="utf-8") as tf:
                    tf.write(task_description)
                
                # Call fix-code-agent using PowerShell
                self.logger.info(f"🤖 调用 fix-code-agent 修复问题...")
                self.logger.info(f"   任务描述: {task_description[:200]}...")
                self.logger.info(f"   任务文件: {task_file}")
                
                try:
                    # Use Python module instead of direct command to avoid PATH issues
                    # Prepare environment with UTF-8 encoding for Windows
                    env = os.environ.copy()
                    env["PYTHONIOENCODING"] = "utf-8"
                    env["FIXCODE_SILENT_STARTUP"] = "1"  # Suppress emoji output
                    
                    # Read task content from file
                    with open(task_file, "r", encoding="utf-8") as tf:
                        task_content = tf.read()
                    
                    # Get the path to fixcodeagent module
                    # The module is at agents/fix_execution_agent/src/fixcodeagent
                    agent_dir = os.path.dirname(os.path.abspath(__file__))
                    fixcodeagent_src = os.path.join(agent_dir, "src")
                    
                    # Add the src directory to PYTHONPATH so we can import fixcodeagent
                    pythonpath = env.get("PYTHONPATH", "")
                    if pythonpath:
                        env["PYTHONPATH"] = f"{fixcodeagent_src}{os.pathsep}{pythonpath}"
                    else:
                        env["PYTHONPATH"] = fixcodeagent_src
                    
                    self.logger.info(f"   执行命令: python -m fixcodeagent --task \"[from file]\" --yolo --exit-immediately")
                    self.logger.debug(f"   完整任务描述已保存到: {task_file}")
                    self.logger.debug(f"   Working directory: {project_root}")
                    self.logger.debug(f"   PYTHONPATH: {fixcodeagent_src}")
                    
                    # Run using Python module - pass task content directly
                    # cwd=project_root so fix-code-agent can find the files to fix
                    process = await asyncio.create_subprocess_exec(
                        sys.executable,
                        "-m", "fixcodeagent",
                        "--task", task_content,
                        "--yolo",
                        "--exit-immediately",
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        cwd=project_root,
                        env=env
                    )
                    
                    stdout, stderr = await process.communicate()
                    return_code = process.returncode
                    
                    if return_code == 0:
                        self.logger.info(f"✅ fix-code-agent 执行成功")
                        if stdout:
                            self.logger.debug(f"   输出: {stdout.decode('utf-8', errors='ignore')[:500]}")
                        
                        # Read after state
                        with open(abs_path, "r", encoding="utf-8") as f:
                            after_code = f.read()
                        
                        # Save before/after files
                        base, ext = os.path.splitext(os.path.basename(abs_path))
                        issue_id = f"{base}_issue_{issue_index}"
                        before_out = os.path.join(output_dir, f"{issue_id}_before{ext}")
                        after_out = os.path.join(output_dir, f"{issue_id}_after{ext}")
                        
                        with open(before_out, "w", encoding="utf-8") as bf:
                            bf.write(before_code)
                        with open(after_out, "w", encoding="utf-8") as af:
                            af.write(after_code)
                        
                        before_out_abs = os.path.abspath(before_out)
                        after_out_abs = os.path.abspath(after_out)
                        
                        self.logger.info(f"✅ 问题修复完成")
                        self.logger.info(f"   📁 修复前: {before_out_abs}")
                        self.logger.info(f"   📁 修复后: {after_out_abs}")
                        
                        fix_results.append({
                            "issue_index": issue_index,
                            "file": abs_path,
                            "before": before_out_abs,
                            "after": after_out_abs,
                            "task_file": os.path.abspath(task_file),
                            "issue": issue,
                            "task_description": task_description,
                            "output_dir": output_dir,
                            "fixed": True
                        })
                    else:
                        error_msg = f"fix-code-agent 执行失败 (返回码: {return_code})"
                        if stderr:
                            error_detail = stderr.decode('utf-8', errors='ignore')
                            error_msg += f": {error_detail[:200]}"
                        self.logger.error(f"❌ {error_msg}")
                        errors.append(error_msg)
                        failed_issues_details.append({
                            "issue": issue,
                            "file": abs_path,
                            "reason": error_msg,
                            "status": "fix_code_agent_failed",
                            "return_code": return_code
                        })
                        
                except Exception as e:
                    error_msg = f"调用 fix-code-agent 时出错: {str(e)}"
                    self.logger.error(f"❌ {error_msg}")
                    import traceback
                    error_trace = traceback.format_exc()
                    self.logger.error(f"   错误详情: {error_trace}")
                    errors.append(error_msg)
                    failed_issues_details.append({
                        "issue": issue,
                        "file": abs_path,
                        "reason": error_msg,
                        "error_detail": error_trace,
                        "status": "execution_failed"
                    })
                    
            except Exception as e:
                error_msg = f"处理问题失败: {e}"
                self.logger.error(f"❌ {error_msg}")
                errors.append(error_msg)
                failed_issues_details.append({
                    "issue": issue,
                    "file": issue_file,
                    "reason": error_msg,
                    "status": "processing_failed"
                })

        total_issues = len(issues)
        fixed_count = len([r for r in fix_results if r.get("fixed", False)])
        skipped_count = len(skipped_issues)
        failed_count = len(failed_issues_details)
        
        # 生成修复结果摘要
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"🎉 修复任务完成！")
        self.logger.info(f"   任务ID: {task_id}")
        self.logger.info(f"   总问题数: {total_issues}")
        self.logger.info(f"   成功修复问题数: {fixed_count}")
        self.logger.info(f"   跳过问题数: {skipped_count}")
        self.logger.info(f"   失败问题数: {failed_count}")
        self.logger.info(f"   输出目录: {output_dir}")
        
        if fix_results:
            self.logger.info(f"\n📁 修复结果文件位置:")
            for idx, result in enumerate(fix_results, 1):
                file_name = os.path.basename(result.get('file', 'unknown'))
                self.logger.info(f"   {idx}. {file_name}")
                self.logger.info(f"      修复前: {result.get('before', 'N/A')}")
                self.logger.info(f"      修复后: {result.get('after', 'N/A')}")
        
        if skipped_issues:
            self.logger.warning(f"\n⚠️ 被跳过的问题 ({skipped_count} 个):")
            for idx, skipped in enumerate(skipped_issues[:10], 1):  # 只显示前10个
                issue = skipped.get("issue", {})
                reason = skipped.get("reason", "未知原因")
                file_path = skipped.get("file_path", "N/A")
                line = issue.get("line", "N/A")
                msg = issue.get("message", "")[:50]
                self.logger.warning(f"   {idx}. [{file_path}:{line}] {msg}")
                self.logger.warning(f"      原因: {reason}")
            if len(skipped_issues) > 10:
                self.logger.warning(f"   ... 还有 {len(skipped_issues) - 10} 个被跳过的问题")
        
        if failed_issues_details:
            self.logger.warning(f"\n❌ 修复失败的问题 ({failed_count} 个):")
            # 按失败原因分组统计
            failure_reasons = {}
            for failed in failed_issues_details:
                reason = failed.get("reason", "未知原因")
                if reason not in failure_reasons:
                    failure_reasons[reason] = []
                failure_reasons[reason].append(failed)
            
            for reason, failed_list in failure_reasons.items():
                self.logger.warning(f"   {reason}: {len(failed_list)} 个问题")
                # 显示前5个失败问题的详情
                for idx, failed in enumerate(failed_list[:5], 1):
                    issue = failed.get("issue", {})
                    file_path = failed.get("file", "N/A")
                    line = issue.get("line", "N/A")
                    msg = issue.get("message", "")[:50]
                    self.logger.warning(f"      {idx}. [{file_path}:{line}] {msg}")
                if len(failed_list) > 5:
                    self.logger.warning(f"      ... 还有 {len(failed_list) - 5} 个类似问题")
        
        if errors:
            self.logger.warning(f"\n⚠️ 修复过程中的错误:")
            for idx, error in enumerate(errors, 1):
                self.logger.warning(f"   {idx}. {error}")
        
        self.logger.info(f"{'='*60}\n")
        
        return {
            "success": len(errors) == 0 and failed_count == 0,
            "task_id": task_id,
            "fix_results": fix_results,
            "total_issues": total_issues,
            "fixed_issues": fixed_count,
            "failed_issues": failed_count,
            "skipped_issues": skipped_count,
            "errors": errors,
            "skipped_issues_details": skipped_issues,  # 添加被跳过的问题详情
            "failed_issues_details": failed_issues_details,  # 添加失败问题的详情
            "output_dir": output_dir,
            "timestamp": asyncio.get_event_loop().time(),
            "message": f"修复完成: {fixed_count}/{total_issues} 个问题 (跳过: {skipped_count}, 失败: {failed_count})" if not errors else f"修复完成但有错误: {fixed_count}/{total_issues} 个问题 (跳过: {skipped_count}, 失败: {failed_count})",
        }
