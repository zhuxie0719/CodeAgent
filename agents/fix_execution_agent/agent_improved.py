"""
改进后的Agent代码 - 修复版本
主要改进：
1. 异步非阻塞执行
2. 完整错误信息捕获
3. 超时控制机制
"""
import asyncio
import os
import subprocess
import sys
from typing import Dict, List, Any, Optional

from ..base_agent import BaseAgent


class FixExecutionAgent(BaseAgent):
    """修复执行Agent - 改进版本"""
    
    def __init__(self, agent_id: str = "fix_execution_agent", config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, config or {})
        # 默认配置
        self.default_timeout = self.config.get("default_timeout", 300)  # 默认300秒超时
        self.max_concurrent_fixes = self.config.get("max_concurrent_fixes", 1)  # 默认串行执行
    
    async def initialize(self) -> bool:
        return True
    
    def get_capabilities(self) -> List[str]:
        return ["fix_code_issues"]
    
    def _resolve_temp_extract_path(self, path: str) -> str:
        """Resolve temp_extract paths to actual location at ../../api/temp_extract"""
        if path and path.startswith("temp_extract"):
            agent_dir = os.path.dirname(os.path.abspath(__file__))
            api_dir = os.path.join(agent_dir, "..", "..", "api")
            api_dir = os.path.abspath(api_dir)
            resolved = path.replace("temp_extract", os.path.join(api_dir, "temp_extract"), 1)
            resolved = os.path.normpath(resolved)
            return resolved
        return path
    
    async def _run_fixcodeagent(
        self, 
        task: str, 
        problem_file: str, 
        project_root: str,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        运行 fixcodeagent 命令修复单个问题 - 改进版本
        
        Args:
            task: 修复任务描述
            problem_file: 问题文件路径
            project_root: 项目根目录
            timeout: 超时时间（秒），默认使用配置值
        
        Returns:
            包含执行结果的字典
        """
        # 使用配置的超时时间或默认值
        if timeout is None:
            timeout = self.default_timeout
        
        # 设置Windows环境下的编码
        if sys.platform == "win32":
            os.environ["PYTHONIOENCODING"] = "utf-8"
            os.environ["FIXCODE_SILENT_STARTUP"] = "1"
        
        # 构建完整的任务描述
        full_task = f"Task: {task}\n\nProblem File: {problem_file}\nProject Root: {project_root}"
        
        # 准备命令参数
        cmd = [
            sys.executable,
            "-m",
            "fixcodeagent",
            "--task",
            full_task,
            "--yolo",
            "--exit-immediately"
        ]
        
        # 准备环境变量
        env = os.environ.copy()
        if sys.platform == "win32":
            env["PYTHONIOENCODING"] = "utf-8"
            env["FIXCODE_SILENT_STARTUP"] = "1"
        
        self.logger.info(f"🤖 执行修复命令: {' '.join(cmd[:3])} ...")
        self.logger.info(f"   任务: {task[:100]}...")
        self.logger.info(f"   超时设置: {timeout}秒")
        
        try:
            # 改进1: 使用异步子进程，非阻塞执行
            process = await asyncio.create_subprocess_exec(
                *cmd,
                env=env,
                stdout=asyncio.subprocess.PIPE,  # 改进2: 捕获标准输出
                stderr=asyncio.subprocess.PIPE,  # 改进2: 捕获标准错误
                cwd=project_root  # 设置工作目录
            )
            
            # 改进3: 使用超时控制
            try:
                # 异步等待进程完成并读取输出
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
                return_code = process.returncode
                
            except asyncio.TimeoutError:
                # 超时处理：终止进程
                self.logger.warning(f"⏱️ 执行超时 ({timeout}秒)，正在终止进程...")
                try:
                    process.terminate()
                    # 等待进程终止，最多等待5秒
                    try:
                        await asyncio.wait_for(process.wait(), timeout=5.0)
                    except asyncio.TimeoutError:
                        # 强制杀死进程
                        process.kill()
                        await process.wait()
                except Exception as kill_error:
                    self.logger.error(f"终止进程时出错: {kill_error}")
                
                return {
                    "success": False,
                    "return_code": -1,
                    "error": f"执行超时 (超过{timeout}秒)",
                    "timeout": True,
                    "stdout": "",
                    "stderr": ""
                }
            
            # 解码输出（处理编码问题）
            try:
                stdout_text = stdout.decode("utf-8", errors="replace") if stdout else ""
                stderr_text = stderr.decode("utf-8", errors="replace") if stderr else ""
            except Exception as decode_error:
                self.logger.warning(f"解码输出时出错: {decode_error}")
                stdout_text = str(stdout) if stdout else ""
                stderr_text = str(stderr) if stderr else ""
            
            self.logger.info(f"   命令执行完成，退出码: {return_code}")
            
            # 记录输出信息（用于调试）
            if stdout_text:
                self.logger.debug(f"   stdout: {stdout_text[:500]}...")
            if stderr_text:
                self.logger.debug(f"   stderr: {stderr_text[:500]}...")
            
            if return_code == 0:
                self.logger.info(f"✅ 修复成功")
                return {
                    "success": True,
                    "return_code": return_code,
                    "stdout": stdout_text,
                    "stderr": stderr_text
                }
            else:
                error_msg = f"修复失败 (返回码: {return_code})"
                if stderr_text:
                    error_msg += f"\n错误信息: {stderr_text[:200]}"
                
                self.logger.error(f"❌ {error_msg}")
                return {
                    "success": False,
                    "return_code": return_code,
                    "error": error_msg,
                    "stdout": stdout_text,
                    "stderr": stderr_text
                }
                
        except Exception as e:
            error_msg = f"执行修复命令时出错: {str(e)}"
            self.logger.error(f"❌ {error_msg}", exc_info=True)
            return {
                "success": False,
                "error": error_msg,
                "exception": str(e),
                "stdout": "",
                "stderr": ""
            }
    
    async def _process_single_issue(
        self,
        issue: Dict[str, Any],
        issue_index: int,
        total_issues: int,
        project_root: str
    ) -> Dict[str, Any]:
        """处理单个问题的辅助方法"""
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"🔧 [{issue_index}/{total_issues}] 正在处理问题")
        
        # 从 issue 中获取信息
        issue_message = issue.get("message", "")
        issue_file = issue.get("file_path") or issue.get("file", "")
        
        # 从 original_task 中获取 task, problem_file, project_root
        original_task = issue.get("original_task", {})
        task = original_task.get("task", issue_message)
        problem_file = original_task.get("problem_file", issue_file)
        issue_project_root = original_task.get("project_root", project_root)
        
        # 路径解析
        problem_file = self._resolve_temp_extract_path(problem_file)
        issue_project_root = self._resolve_temp_extract_path(issue_project_root)
        
        if not os.path.isabs(problem_file):
            problem_file = os.path.normpath(
                os.path.join(issue_project_root, problem_file.lstrip('./').lstrip('../'))
            )
        else:
            problem_file = os.path.normpath(problem_file)
        
        if not os.path.isabs(issue_project_root):
            issue_project_root = os.path.normpath(
                os.path.join(project_root, issue_project_root.lstrip('./').lstrip('../'))
            )
        else:
            issue_project_root = os.path.normpath(issue_project_root)
        
        issue_project_root = os.path.abspath(issue_project_root)
        problem_file = os.path.abspath(problem_file)
        
        self.logger.info(f"   任务: {task[:100]}...")
        self.logger.info(f"   问题文件: {problem_file}")
        self.logger.info(f"   项目根目录: {issue_project_root}")
        
        # 调用改进后的修复方法
        result = await self._run_fixcodeagent(
            task=task,
            problem_file=problem_file,
            project_root=issue_project_root
        )
        
        if result.get("success"):
            self.logger.info(f"✅ 问题 {issue_index} 修复成功")
        else:
            error_msg = result.get("error", "未知错误")
            self.logger.error(f"❌ 问题 {issue_index} 修复失败: {error_msg}")
        
        return {
            "issue_index": issue_index,
            "issue": issue,
            "task": task,
            "problem_file": problem_file,
            "project_root": issue_project_root,
            "result": result
        }
    
    async def process_task(self, task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理修复任务，逐个解决问题 - 改进版本"""
        self.logger.info("=" * 60)
        self.logger.info(f"🔧 修复Agent开始处理任务: {task_id}")
        
        # 从 task_data 获取项目路径和问题列表
        project_path = task_data.get("project_path") or task_data.get("file_path", "")
        issues: List[Dict[str, Any]] = task_data.get("issues", []) or []
        
        self.logger.info(f"   项目路径: {project_path}")
        self.logger.info(f"   问题数量: {len(issues)}")
        
        if not project_path:
            return {
                "success": False,
                "task_id": task_id,
                "message": "未提供项目路径",
                "errors": ["未提供项目路径"]
            }
        
        if not issues:
            return {
                "success": True,
                "task_id": task_id,
                "message": "没有问题需要修复",
                "fixed_issues": 0,
                "total_issues": 0
            }
        
        # 解析项目根目录
        project_path = self._resolve_temp_extract_path(project_path)
        project_path = os.path.normpath(project_path)
        
        if os.path.isdir(project_path):
            project_root = project_path
        else:
            project_root = os.path.dirname(project_path) if project_path else os.getcwd()
        
        project_root = os.path.abspath(project_root)
        
        # 逐个处理问题
        fix_results: List[Dict[str, Any]] = []
        fixed_count = 0
        failed_count = 0
        errors: List[str] = []
        
        self.logger.info(f"   项目根目录: {project_root}")
        self.logger.info(f"   开始逐个修复问题...")
        self.logger.info("=" * 60)
        
        # 改进：支持并发处理（可选）
        max_concurrent = self.max_concurrent_fixes
        
        if max_concurrent > 1 and len(issues) > 1:
            # 并发处理模式
            self.logger.info(f"   使用并发模式，最大并发数: {max_concurrent}")
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def process_single_issue_with_semaphore(issue, index):
                async with semaphore:
                    return await self._process_single_issue(issue, index, len(issues), project_root)
            
            tasks = [
                process_single_issue_with_semaphore(issue, idx) 
                for idx, issue in enumerate(issues, 1)
            ]
            fix_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 处理异常结果
            processed_results = []
            for idx, result in enumerate(fix_results, 1):
                if isinstance(result, Exception):
                    self.logger.error(f"❌ 问题 {idx} 处理时发生异常: {result}")
                    errors.append(f"问题 {idx}: {str(result)}")
                    failed_count += 1
                    processed_results.append({
                        "issue_index": idx,
                        "error": str(result),
                        "result": {"success": False}
                    })
                else:
                    processed_results.append(result)
                    if result.get("result", {}).get("success"):
                        fixed_count += 1
                    else:
                        failed_count += 1
                        error_msg = result.get("result", {}).get("error", "未知错误")
                        errors.append(f"问题 {result['issue_index']}: {error_msg}")
            
            fix_results = processed_results
        else:
            # 串行处理模式（原逻辑）
            for issue_index, issue in enumerate(issues, 1):
                result = await self._process_single_issue(
                    issue, issue_index, len(issues), project_root
                )
                fix_results.append(result)
                
                if result.get("result", {}).get("success"):
                    fixed_count += 1
                else:
                    failed_count += 1
                    error_msg = result.get("result", {}).get("error", "未知错误")
                    errors.append(f"问题 {issue_index}: {error_msg}")
        
        # 汇总结果
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"🎉 修复任务完成！")
        self.logger.info(f"   任务ID: {task_id}")
        self.logger.info(f"   总问题数: {len(issues)}")
        self.logger.info(f"   成功修复: {fixed_count}")
        self.logger.info(f"   修复失败: {failed_count}")
        self.logger.info(f"{'='*60}\n")
        
        return {
            "success": failed_count == 0,
            "task_id": task_id,
            "total_issues": len(issues),
            "fixed_issues": fixed_count,
            "failed_issues": failed_count,
            "fix_results": fix_results,
            "errors": errors,
            "message": f"修复完成: {fixed_count}/{len(issues)} 个问题 (失败: {failed_count})"
        }

