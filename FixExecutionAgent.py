import asyncio
import os
import subprocess
import sys
from typing import Dict, List, Any, Optional

from agents.base_agent import BaseAgent


class FixExecutionAgent(BaseAgent):
    """修复执行Agent - 新版本"""
    
    def __init__(self, agent_id: str = "fix_execution_agent", config: Optional[Dict[str, Any]] = None):
        super().__init__(agent_id, config or {})
    
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
    
    async def _run_fixcodeagent(self, task: str, problem_file: str, project_root: str) -> Dict[str, Any]:
        """运行 fixcodeagent 命令修复单个问题 - 简单测试版本"""
        # 设置Windows环境下的编码
        if sys.platform == "win32":
            os.environ["PYTHONIOENCODING"] = "utf-8"
            os.environ["FIXCODE_SILENT_STARTUP"] = "1"
        
        # 构建完整的任务描述，包含 task, problem_file, project_root
        full_task = f"Task: {task}\n\nProblem File: {problem_file}\nProject Root: {project_root}"
        
        # 准备命令参数 - 简单版本，就像 newtest.py
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
        
        try:
            # 简单版本 - 使用 subprocess.Popen 就像 newtest.py
            process = subprocess.Popen(
                cmd,
                env=env
            )
            # 等待进程完成
            return_code = process.wait()
            
            self.logger.info(f"   命令执行完成，退出码: {return_code}")
            
            if return_code == 0:
                self.logger.info(f"✅ 修复成功")
                return {
                    "success": True,
                    "return_code": return_code
                }
            else:
                self.logger.error(f"❌ 修复失败 (返回码: {return_code})")
                return {
                    "success": False,
                    "return_code": return_code,
                    "error": f"修复失败 (返回码: {return_code})"
                }
                
        except Exception as e:
            error_msg = f"执行修复命令时出错: {str(e)}"
            self.logger.error(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "exception": str(e)
            }
    
    async def process_task(self, task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理修复任务，逐个解决问题"""
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
        
        for issue_index, issue in enumerate(issues, 1):
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"🔧 [{issue_index}/{len(issues)}] 正在处理问题")
            
            # 从 issue 中获取信息
            issue_message = issue.get("message", "")
            issue_file = issue.get("file_path") or issue.get("file", "")
            
            # 从 original_task 中获取 task, problem_file, project_root
            original_task = issue.get("original_task", {})
            task = original_task.get("task", issue_message)
            problem_file = original_task.get("problem_file", issue_file)
            issue_project_root = original_task.get("project_root", project_root)
            
            # 解析路径
            problem_file = self._resolve_temp_extract_path(problem_file)
            issue_project_root = self._resolve_temp_extract_path(issue_project_root)
            
            if not os.path.isabs(problem_file):
                problem_file = os.path.normpath(os.path.join(issue_project_root, problem_file.lstrip('./').lstrip('../')))
            else:
                problem_file = os.path.normpath(problem_file)
            
            if not os.path.isabs(issue_project_root):
                issue_project_root = os.path.normpath(os.path.join(project_root, issue_project_root.lstrip('./').lstrip('../')))
            else:
                issue_project_root = os.path.normpath(issue_project_root)
            
            issue_project_root = os.path.abspath(issue_project_root)
            problem_file = os.path.abspath(problem_file)
            
            self.logger.info(f"   任务: {task[:100]}...")
            self.logger.info(f"   问题文件: {problem_file}")
            self.logger.info(f"   项目根目录: {issue_project_root}")
            
            # 调用 fixcodeagent 修复问题
            result = await self._run_fixcodeagent(
                task=task,
                problem_file=problem_file,
                project_root=issue_project_root
            )
            
            if result.get("success"):
                fixed_count += 1
                self.logger.info(f"✅ 问题 {issue_index} 修复成功")
            else:
                failed_count += 1
                error_msg = result.get("error", "未知错误")
                errors.append(f"问题 {issue_index} ({problem_file}): {error_msg}")
                self.logger.error(f"❌ 问题 {issue_index} 修复失败: {error_msg}")
            
            fix_results.append({
                "issue_index": issue_index,
                "issue": issue,
                "task": task,
                "problem_file": problem_file,
                "project_root": issue_project_root,
                "result": result
            })
        
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