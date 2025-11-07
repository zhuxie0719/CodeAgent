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

        # 将问题按文件聚合，并追踪被跳过的问题
        issues_by_file: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        skipped_issues: List[Dict[str, Any]] = []  # 追踪被跳过的问题及其原因
        
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
            if os.path.isabs(issue_file_path):
                # 已经是绝对路径
                file_name = os.path.normpath(issue_file_path)
                # 检查路径是否包含project_root（避免重复嵌套）
                # 如果路径已经包含项目根目录，直接使用
                if project_root in file_name:
                    # 路径已经包含项目路径，直接使用
                    pass
                else:
                    # 路径不包含项目路径，但已经是绝对路径，直接使用
                    # 这种情况可能发生在Docker环境下，路径映射不同
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
            # 例如：['temp_extract', 'project_xxx', 'temp_extract', 'project_xxx', 'file.py']
            # 应该变成：['temp_extract', 'project_xxx', 'file.py']
            if len(path_parts) > 2:
                # 从最大可能的模式长度开始检查（最多检查到路径长度的一半）
                max_pattern_len = min(len(path_parts) // 2, 10)  # 限制最大模式长度为10，避免性能问题
                found_duplicate = False
                
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
                        found_duplicate = True
                        break
                
                # 如果没找到重复模式，但路径看起来异常长，记录日志
                if not found_duplicate and len(path_parts) > 10:
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
                
            issues_by_file[file_name].append(issue)

        fix_results: List[Dict[str, Any]] = []
        errors: List[str] = []
        failed_issues_details: List[Dict[str, Any]] = []  # 追踪修复失败的问题详情
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
                    error_msg = f"文件未找到: {abs_path}"
                    errors.append(error_msg)
                    # 记录该文件的所有问题为失败
                    for issue in file_issues:
                        failed_issues_details.append({
                            "issue": issue,
                            "file": abs_path,
                            "reason": error_msg,
                            "status": "file_not_found"
                        })
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
                    error_trace = traceback.format_exc()
                    self.logger.error(f"   错误详情: {error_trace}")
                    error_msg = f"LLM修复失败: {str(e)}"
                    errors.append(error_msg)
                    # 记录该文件的所有问题为失败
                    for issue in file_issues:
                        failed_issues_details.append({
                            "issue": issue,
                            "file": abs_path,
                            "reason": error_msg,
                            "error_detail": error_trace,
                            "status": "llm_failed"
                        })
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
                error_msg = f"处理 {file_key} 失败: {e}"
                errors.append(error_msg)
                # 记录该文件的所有问题为失败
                for issue in file_issues:
                    failed_issues_details.append({
                        "issue": issue,
                        "file": file_key,
                        "reason": error_msg,
                        "status": "processing_failed"
                    })

        total_issues = len(issues)
        fixed_files = len(fix_results)
        total_fixed_issues = sum(r.get("issues_fixed", 0) for r in fix_results)
        skipped_count = len(skipped_issues)
        failed_count = len(failed_issues_details)
        
        # 生成修复结果摘要
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"🎉 修复任务完成！")
        self.logger.info(f"   任务ID: {task_id}")
        self.logger.info(f"   总问题数: {total_issues}")
        self.logger.info(f"   成功修复文件数: {fixed_files}/{total_files}")
        self.logger.info(f"   成功修复问题数: {total_fixed_issues}")
        self.logger.info(f"   跳过问题数: {skipped_count}")
        self.logger.info(f"   失败问题数: {failed_count}")
        self.logger.info(f"   输出目录: {output_dir}")
        
        if fix_results:
            self.logger.info(f"\n📁 修复结果文件位置:")
            for idx, result in enumerate(fix_results, 1):
                self.logger.info(f"   {idx}. {result.get('file_name', 'unknown')}")
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
            "total_files": total_files,
            "fixed_files": fixed_files,
            "fixed_issues": total_fixed_issues,
            "failed_issues": failed_count,
            "skipped_issues": skipped_count,
            "errors": errors,
            "skipped_issues_details": skipped_issues,  # 添加被跳过的问题详情
            "failed_issues_details": failed_issues_details,  # 添加失败问题的详情
            "output_dir": output_dir,
            "timestamp": asyncio.get_event_loop().time(),
            "message": f"修复完成: {fixed_files}/{total_files} 个文件, {total_fixed_issues}/{total_issues} 个问题 (跳过: {skipped_count}, 失败: {failed_count})" if not errors else f"修复完成但有错误: {fixed_files}/{total_files} 个文件, {total_fixed_issues}/{total_issues} 个问题 (跳过: {skipped_count}, 失败: {failed_count})",
        }
