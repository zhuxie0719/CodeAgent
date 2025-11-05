"""
综合检测API
统一的检测入口，集成静态检测和动态检测功能
"""

import asyncio
import tempfile
import os
import json
import sys
import httpx
import shutil
import zipfile
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

from fastapi import APIRouter, File, UploadFile, HTTPException, BackgroundTasks, Form
from pydantic import BaseModel, Field

# 导入检测组件
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from agents.dynamic_detection_agent.agent import DynamicDetectionAgent
from agents.bug_detection_agent.agent import BugDetectionAgent
from api.deepseek_config import deepseek_config

# 数据模型
class BaseResponse(BaseModel):
    """基础响应模型"""
    success: bool = Field(True, description="是否成功")
    message: str = Field("", description="响应消息")
    data: Optional[Dict[str, Any]] = Field(None, description="响应数据")
    error: Optional[str] = Field(None, description="错误信息")

class DetectionRequest(BaseModel):
    """检测请求模型"""
    static_analysis: bool = Field(True, description="是否进行静态分析")
    dynamic_monitoring: bool = Field(True, description="是否进行动态监控")
    runtime_analysis: bool = Field(True, description="是否进行运行时分析")

# 创建APIRouter
router = APIRouter()

# 全局检测器
dynamic_agent = DynamicDetectionAgent({
    "monitor_interval": 5,
    "alert_thresholds": {
        "cpu_threshold": 80,
        "memory_threshold": 85,
        "disk_threshold": 90,
        "network_threshold": 80
    },
    "enable_web_app_test": False,
    "enable_dynamic_detection": True,
    "enable_flask_specific_tests": True,
    "enable_server_testing": True
})

# 检查是否启用Docker支持（通过环境变量，默认禁用）
use_docker = os.getenv("USE_DOCKER", "false").lower() == "true"

static_agent = BugDetectionAgent({
    "enable_ai_analysis": True,
    "analysis_depth": "comprehensive",
    "use_docker": use_docker
})

# 注意：动态检测不使用Docker，它直接使用本地虚拟环境

class ComprehensiveDetector:
    """综合检测器，集成静态检测和动态检测功能"""
    
    def __init__(self, static_agent, dynamic_agent):
        self.static_agent = static_agent
        self.dynamic_agent = dynamic_agent
        self.enable_web_app_test = False
        self.enable_dynamic_detection = True
        self.enable_flask_specific_tests = True
        self.enable_server_testing = True
    
    async def detect_defects(self, zip_file_path: str, 
                           static_analysis: bool = True,
                           dynamic_monitoring: bool = True,
                           runtime_analysis: bool = True,
                           enable_dynamic_detection: bool = True,
                           enable_flask_specific_tests: bool = True,
                           enable_server_testing: bool = True,
                           enable_web_app_test: bool = False) -> Dict[str, Any]:
        """执行综合检测"""
        # 设置enable_web_app_test属性，并同步到dynamic_agent
        self.enable_web_app_test = enable_web_app_test
        if hasattr(self.dynamic_agent, 'enable_web_app_test'):
            self.dynamic_agent.enable_web_app_test = enable_web_app_test
        
        results = {
            "detection_type": "comprehensive",
            "timestamp": datetime.now().isoformat(),
            "zip_file": zip_file_path,
            "analysis_options": {
                "static_analysis": static_analysis,
                "dynamic_monitoring": dynamic_monitoring,
                "runtime_analysis": runtime_analysis,
                "enable_dynamic_detection": enable_dynamic_detection,
                "enable_flask_specific_tests": enable_flask_specific_tests,
                "enable_server_testing": enable_server_testing,
                "enable_web_app_test": enable_web_app_test
            }
        }
        
        try:
            # 检查文件大小
            file_size = os.path.getsize(zip_file_path)
            max_size = 50 * 1024 * 1024  # 50MB限制
            
            if file_size > max_size:
                results["error"] = f"文件过大 ({file_size // (1024*1024)}MB > {max_size // (1024*1024)}MB)"
                return results
            
            # 使用BugDetectionAgent的extract_project方法来解压项目并创建虚拟环境
            print(f"🔧 开始解压项目并创建虚拟环境: {zip_file_path}")
            try:
                # 设置较长的超时时间，给虚拟环境创建足够时间
                extract_dir = await asyncio.wait_for(
                    self.static_agent.extract_project(zip_file_path),
                    timeout=120.0  # 增加到120秒
                )
                print(f"✅ 项目解压完成，虚拟环境已创建: {extract_dir}")
            except asyncio.TimeoutError:
                print("⚠️ 虚拟环境创建超时（120秒），使用简单解压模式")
                extract_dir = await self._simple_extract_project(zip_file_path)
                results["warning"] = "虚拟环境创建超时，使用简单解压模式"
            except KeyboardInterrupt:
                print("⚠️ 虚拟环境创建被中断，使用简单解压模式")
                extract_dir = await self._simple_extract_project(zip_file_path)
                results["warning"] = "虚拟环境创建被中断，使用简单解压模式"
            except Exception as e:
                print(f"❌ 项目解压失败: {e}")
                # 如果虚拟环境创建失败，尝试简单的文件解压
                extract_dir = await self._simple_extract_project(zip_file_path)
                    
                # 设置警告信息
                results["warning"] = f"虚拟环境创建失败，使用简单解压模式: {e}"
            
            results["extracted_path"] = extract_dir
            results["files"] = self._list_files(extract_dir)
            
            # 限制文件数量，避免处理过多文件
            if len(results["files"]) > 1000:
                results["warning"] = f"文件数量过多 ({len(results['files'])} > 1000)，将进行采样分析"
                results["files"] = results["files"][:1000]  # 只取前1000个文件
            
            # 并行执行静态分析和动态检测
            tasks = []
            
            # 静态分析
            if static_analysis:
                tasks.append(self._perform_static_analysis_async(extract_dir))
            
            # 动态监控
            if dynamic_monitoring:
                tasks.append(self._perform_dynamic_monitoring_async())
            
            # 运行时分析
            if runtime_analysis:
                tasks.append(self._perform_runtime_analysis_async(extract_dir))
            
            # 动态缺陷检测
            if enable_dynamic_detection:
                tasks.append(self._perform_dynamic_detection_async(extract_dir, enable_flask_specific_tests, enable_server_testing))
            
            # 等待所有任务完成（添加超时机制）
            if tasks:
                try:
                    # 设置120秒超时，给检测更多时间
                    task_results = await asyncio.wait_for(
                        asyncio.gather(*tasks, return_exceptions=True),
                        timeout=120.0
                    )
                except asyncio.TimeoutError:
                    print("⚠️ 检测任务超时（120秒），使用默认结果")
                    results["warning"] = "检测任务超时，部分功能可能未完成"
                    # 创建默认的失败结果
                    task_results = []
                    for i, task in enumerate(tasks):
                        if i == 0 and static_analysis:
                            task_results.append({"error": "检测超时", "issues": []})
                        elif i == 1 and dynamic_monitoring:
                            task_results.append({"error": "检测超时", "alerts": []})
                        elif i == 2 and runtime_analysis:
                            task_results.append({"error": "检测超时", "execution_successful": False})
                        elif i == 3 and enable_dynamic_detection:
                            task_results.append({"error": "检测超时", "tests_completed": False})
                
                # 处理结果
                task_index = 0
                if static_analysis:
                    if isinstance(task_results[task_index], Exception):
                        results["static_analysis"] = {"error": str(task_results[task_index]), "issues": []}
                    else:
                        results["static_analysis"] = task_results[task_index]
                    task_index += 1
                
                if dynamic_monitoring:
                    if isinstance(task_results[task_index], Exception):
                        results["dynamic_monitoring"] = {"error": str(task_results[task_index]), "alerts": []}
                    else:
                        results["dynamic_monitoring"] = task_results[task_index]
                    task_index += 1
                
                if runtime_analysis:
                    if isinstance(task_results[task_index], Exception):
                        results["runtime_analysis"] = {"error": str(task_results[task_index]), "execution_successful": False}
                    else:
                        results["runtime_analysis"] = task_results[task_index]
                    task_index += 1
                
                if enable_dynamic_detection:
                    if isinstance(task_results[task_index], Exception):
                        results["dynamic_detection"] = {"error": str(task_results[task_index]), "tests_completed": False}
                    else:
                        results["dynamic_detection"] = task_results[task_index]
            
            # 生成综合摘要
            results["summary"] = self._generate_summary(results)
            
            # 清理临时目录和虚拟环境
            try:
                await self.static_agent.cleanup_project_environment(extract_dir)
                print(f"✅ 项目环境清理完成: {extract_dir}")
            except Exception as cleanup_error:
                print(f"⚠️ 环境清理失败: {cleanup_error}")
                # 回退到手动清理
                shutil.rmtree(extract_dir, ignore_errors=True)
            
            return results
            
        except Exception as e:
            results["error"] = str(e)
            # 即使出现错误也要生成summary
            results["summary"] = self._generate_summary(results)
            return results
    
    async def _simple_extract_project(self, zip_file_path: str) -> str:
        """简单的项目解压方法（不创建虚拟环境）"""
        try:
            import zipfile
            import tempfile
            
            # 创建临时解压目录
            temp_dir = tempfile.mkdtemp(prefix="comprehensive_extract_")
            
            # 解压ZIP文件
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            print(f"⚠️ 使用简单解压模式: {temp_dir}")
            return temp_dir
            
        except Exception as e:
            print(f"❌ 简单解压也失败: {e}")
            raise e
    
    def _list_files(self, project_path: str) -> List[str]:
        """列出项目文件（排除虚拟环境和缓存文件）"""
        files = []
        skip_dirs = {'venv', '__pycache__', '.git', 'node_modules', '.pytest_cache', '.mypy_cache'}
        
        for root, dirs, filenames in os.walk(project_path):
            # 跳过不需要的目录
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for filename in filenames:
                # 跳过隐藏文件和缓存文件
                if filename.startswith('.') or filename.endswith(('.pyc', '.pyo', '.pyd')):
                    continue
                    
                file_path = os.path.relpath(os.path.join(root, filename), project_path)
                files.append(file_path)
        return files
    
    async def _perform_static_analysis_async(self, project_path: str) -> Dict[str, Any]:
        """异步执行静态分析"""
        try:
            # 调用静态检测agent
            analysis_result = await self.static_agent.analyze_project(project_path, {
                "enable_static": True,
                "enable_pylint": True,
                "enable_flake8": True,
                "enable_bandit": True,
                "enable_mypy": True,
                "enable_ai_analysis": True
            })
            
            if analysis_result.get("success", False):
                detection_results = analysis_result.get("detection_results", {})
                
                # 提取基础数据
                files_analyzed = detection_results.get("files_analyzed", 0)
                project_structure = detection_results.get("project_structure", {})
                code_quality = detection_results.get("code_quality", {})
                
                # 确保有statistics字段，如果没有则从其他字段构建
                statistics = detection_results.get("statistics", {})
                if not statistics or not isinstance(statistics, dict) or len(statistics) == 0:
                    # 从detection_results中提取统计信息
                    statistics = {
                        "total_files": project_structure.get("total_files") if project_structure else files_analyzed,
                        "total_lines": project_structure.get("total_lines", 0) if project_structure else 0,
                        "average_complexity": code_quality.get("average_complexity", 0) if code_quality else 0,
                        "maintainability_score": code_quality.get("maintainability_score", 0) if code_quality else 0,
                        "issues_by_severity": {},
                        "issues_by_type": {},
                        "issues_by_tool": {}
                    }
                    detection_results["statistics"] = statistics
                else:
                    # 如果statistics存在，但缺少某些字段，则从project_structure和code_quality补充
                    if "total_files" not in statistics or statistics["total_files"] == 0:
                        statistics["total_files"] = project_structure.get("total_files", files_analyzed) if project_structure else files_analyzed
                    if "total_lines" not in statistics:
                        statistics["total_lines"] = project_structure.get("total_lines", 0) if project_structure else 0
                    if "average_complexity" not in statistics:
                        statistics["average_complexity"] = code_quality.get("average_complexity", 0) if code_quality else 0
                    if "maintainability_score" not in statistics:
                        statistics["maintainability_score"] = code_quality.get("maintainability_score", 0) if code_quality else 0
                
                # 统计问题的严重程度和类型（确保总是有这些字段）
                if "issues_by_severity" not in statistics:
                    statistics["issues_by_severity"] = {}
                if "issues_by_type" not in statistics:
                    statistics["issues_by_type"] = {}
                if "issues_by_tool" not in statistics:
                    statistics["issues_by_tool"] = {}
                
                issues = detection_results.get("issues", [])
                for issue in issues:
                    severity = issue.get("severity", "info")
                    issue_type = issue.get("type", "unknown")
                    tool = issue.get("tool", "unknown")
                    
                    statistics["issues_by_severity"][severity] = \
                        statistics["issues_by_severity"].get(severity, 0) + 1
                    statistics["issues_by_type"][issue_type] = \
                        statistics["issues_by_type"].get(issue_type, 0) + 1
                    statistics["issues_by_tool"][tool] = \
                        statistics["issues_by_tool"].get(tool, 0) + 1
                
                # 如果没有问题，但仍然记录使用的工具（基于analysis_type）
                if len(issues) == 0 and not statistics.get("issues_by_tool"):
                    # 根据分析配置，记录使用的工具
                    statistics["issues_by_tool"] = {
                        "pylint": 0,
                        "flake8": 0,
                        "bandit": 0,
                        "mypy": 0,
                        "ai_analysis": 0
                    }
                
                # 确保有files_analyzed字段
                if "files_analyzed" not in detection_results or detection_results.get("files_analyzed", 0) == 0:
                    detection_results["files_analyzed"] = statistics.get("total_files", 0)
                
                # 确保有analysis_type字段
                if "analysis_type" not in detection_results:
                    detection_results["analysis_type"] = "enhanced_static_analysis"
                
                # 确保project_structure和code_quality字段被正确传递（即使statistics已经包含）
                # 这样前端可以直接访问这些详细信息
                if not project_structure or not isinstance(project_structure, dict) or len(project_structure) == 0:
                    # 从statistics中构建project_structure
                    detection_results["project_structure"] = {
                        "total_files": statistics.get("total_files", files_analyzed),
                        "total_lines": statistics.get("total_lines", 0)
                    }
                
                if not code_quality or not isinstance(code_quality, dict) or len(code_quality) == 0:
                    # 从statistics中构建code_quality
                    detection_results["code_quality"] = {
                        "average_complexity": statistics.get("average_complexity", 0),
                        "maintainability_score": statistics.get("maintainability_score", 0)
                    }
                
                # 确保issues字段存在（即使为空列表）
                if "issues" not in detection_results:
                    detection_results["issues"] = []
                
                # 确保问题数据格式正确，添加缺失的工具字段
                for issue in detection_results.get("issues", []):
                    if "tool" not in issue:
                        # 从detection_tool或其他字段推断工具
                        issue["tool"] = issue.get("detection_tool", issue.get("tool", "unknown"))
                    if "severity" not in issue:
                        # 根据类型推断严重程度
                        issue["severity"] = "warning"  # 默认值
                
                return detection_results
            else:
                return {
                    "error": analysis_result.get("error", "静态分析失败"),
                    "issues": [],
                    "statistics": {
                        "total_files": 0,
                        "total_lines": 0,
                        "average_complexity": 0,
                        "maintainability_score": 0
                    },
                    "files_analyzed": 0
                }
        except Exception as e:
            return {
                "error": str(e), 
                "issues": [],
                "statistics": {
                    "total_files": 0,
                    "total_lines": 0,
                    "average_complexity": 0,
                    "maintainability_score": 0
                },
                "files_analyzed": 0
            }
    
    async def _perform_dynamic_monitoring_async(self) -> Dict[str, Any]:
        """异步执行动态监控"""
        try:
            return await self.dynamic_agent.start_monitoring(duration=60)
        except Exception as e:
            return {"error": str(e), "alerts": []}
    
    async def _perform_runtime_analysis_async(self, project_path: str) -> Dict[str, Any]:
        """异步执行运行时分析"""
        try:
            return await self.dynamic_agent.perform_runtime_analysis(project_path)
        except Exception as e:
            return {"error": str(e), "execution_successful": False}
    
    async def _perform_dynamic_detection_async(self, project_path: str, enable_flask_tests: bool = True, enable_server_tests: bool = True) -> Dict[str, Any]:
        """异步执行动态缺陷检测"""
        try:
            return await self.dynamic_agent.perform_dynamic_detection(project_path, enable_flask_tests, enable_server_tests)
        except Exception as e:
            return {"error": str(e), "tests_completed": False}
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """生成综合摘要"""
        summary = {
            "total_files": len(results.get("files", [])),
            "analysis_completed": not bool(results.get("error")),
            "issues_summary": {}
        }
        
        # 统计问题数量
        total_issues = 0
        critical_issues = 0
        warning_issues = 0
        info_issues = 0
        
        # 统计静态分析问题
        if "static_analysis" in results:
            static = results["static_analysis"]
            issues = static.get("issues", [])
            statistics = static.get("statistics", {})
            
            summary["issues_summary"]["static"] = {
                "analysis_type": static.get("analysis_type", "unknown"),
                "files_analyzed": static.get("files_analyzed", 0),
                "issues_found": len(issues),
                "total_files": statistics.get("total_files", 0),
                "total_lines": statistics.get("total_lines", 0),
                "average_complexity": statistics.get("average_complexity", 0),
                "maintainability_score": statistics.get("maintainability_score", 0),
                "issues_by_severity": statistics.get("issues_by_severity", {}),
                "issues_by_type": statistics.get("issues_by_type", {}),
                "issues_by_tool": statistics.get("issues_by_tool", {})
            }
            
            # 统计问题严重程度
            for issue in issues:
                total_issues += 1
                severity = issue.get("severity", "info").lower()
                if severity == "error" or severity == "critical":
                    critical_issues += 1
                elif severity == "warning":
                    warning_issues += 1
                else:
                    info_issues += 1
        
        # 统计动态监控结果
        if "dynamic_monitoring" in results:
            dynamic = results["dynamic_monitoring"]
            alerts = dynamic.get("alerts", [])
            summary["issues_summary"]["dynamic"] = {
                "monitoring_duration": dynamic.get("duration", 0),
                "alerts_generated": len(alerts)
            }
            
            # 统计告警数量
            for alert in alerts:
                total_issues += 1
                severity = alert.get("severity", "info").lower()
                if severity == "error" or severity == "critical":
                    critical_issues += 1
                elif severity == "warning":
                    warning_issues += 1
                else:
                    info_issues += 1
        
        # 统计运行时分析结果
        if "runtime_analysis" in results:
            runtime = results["runtime_analysis"]
            summary["issues_summary"]["runtime"] = {
                "execution_successful": runtime.get("execution_successful", False),
                "main_file": runtime.get("main_file", "unknown")
            }
            
            # 如果有运行时错误，计入问题
            if runtime.get("error"):
                total_issues += 1
                critical_issues += 1
        
        # 统计动态检测结果
        if "dynamic_detection" in results:
            dynamic_detection = results["dynamic_detection"]
            summary["issues_summary"]["dynamic_detection"] = {
                "status": dynamic_detection.get("status", "unknown"),
                "is_flask_project": dynamic_detection.get("is_flask_project", False),
                "tests_completed": dynamic_detection.get("tests_completed", False),
                "success_rate": dynamic_detection.get("success_rate", 0)
            }
            
            # 统计动态检测问题
            dynamic_issues = dynamic_detection.get("issues", [])
            for issue in dynamic_issues:
                total_issues += 1
                severity = issue.get("severity", "info").lower()
                if severity == "error" or severity == "critical":
                    critical_issues += 1
                elif severity == "warning":
                    warning_issues += 1
                else:
                    info_issues += 1
        
        # 设置整体状态
        if critical_issues > 0:
            overall_status = "error"
        elif warning_issues > 0:
            overall_status = "warning"
        elif info_issues > 0:
            overall_status = "info"
        else:
            overall_status = "good"
        
        # 生成建议
        recommendations = []
        if critical_issues > 0:
            recommendations.append("发现严重问题，建议立即修复")
        if warning_issues > 0:
            recommendations.append("发现警告问题，建议及时处理")
        
        # 检查运行时分析和动态检测的状态
        runtime_analysis = results.get("runtime_analysis", {})
        dynamic_detection = results.get("dynamic_detection", {})
        runtime_failed = not runtime_analysis.get("execution_successful", True)
        dynamic_success = dynamic_detection.get("tests_completed", False) and dynamic_detection.get("success_rate", 0) >= 100
        
        if runtime_failed:
            if dynamic_success:
                # 运行时分析失败但动态检测成功，说明项目需要Flask环境才能运行
                recommendations.append("运行时分析失败，但动态检测成功。这可能是因为项目需要Flask环境才能运行，属于正常情况")
            else:
                # 两者都失败，需要检查配置
                recommendations.append("运行时分析失败，检查项目配置和依赖")
        
        # 添加摘要字段
        summary.update({
            "total_issues": total_issues,
            "critical_issues": critical_issues,
            "warning_issues": warning_issues,
            "info_issues": info_issues,
            "overall_status": overall_status,
            "recommendations": recommendations
        })
        
        return summary
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """生成文本报告"""
        report_lines = [
            "# 综合检测报告",
            f"生成时间: {results.get('timestamp', 'unknown')}",
            f"检测类型: {results.get('detection_type', 'unknown')}",
            "",
            "## 检测摘要",
        ]
        
        summary = results.get("summary", {})
        report_lines.extend([
            f"- 总文件数: {summary.get('total_files', 0)}",
            f"- 分析完成: {summary.get('analysis_completed', False)}",
            ""
        ])
        
        # 添加问题摘要
        issues_summary = summary.get("issues_summary", {})
        if issues_summary:
            report_lines.append("## 问题统计")
            for analysis_type, stats in issues_summary.items():
                report_lines.append(f"### {analysis_type.upper()}")
                for key, value in stats.items():
                    report_lines.append(f"- {key}: {value}")
                report_lines.append("")
        
        return "\n".join(report_lines)
    
    def save_results(self, results: Dict[str, Any], file_path: str):
        """保存结果到文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"检测结果已保存到: {file_path}")
        except Exception as e:
            print(f"保存结果失败: {e}")
    
    def generate_severe_issues_report(self, results: Dict[str, Any], filename: str) -> str:
        """生成严重问题汇总文档"""
        report_lines = [
            "# 严重问题汇总报告",
            f"**项目名称**: {filename}",
            f"**生成时间**: {results.get('timestamp', 'unknown')}",
            f"**检测类型**: {results.get('detection_type', 'unknown')}",
            "",
            "## 概述",
            "本报告汇总了代码检测中发现的严重问题，排除了格式化和风格问题，重点关注可能影响功能和安全的关键问题。",
            ""
        ]
        
        # 收集所有严重问题
        severe_issues = []
        
        # 静态分析问题
        if "static_analysis" in results:
            static_issues = results["static_analysis"].get("issues", [])
            for issue in static_issues:
                if self._is_severe_issue(issue):
                    severe_issues.append({
                        "type": "静态分析",
                        "severity": issue.get("severity", "unknown"),
                        "file": issue.get("file", "unknown"),
                        "line": issue.get("line", "unknown"),
                        "message": issue.get("message", "unknown"),
                        "tool": issue.get("tool", "unknown"),
                        "issue_type": issue.get("type", "unknown")
                    })
        
        # 动态监控问题
        if "dynamic_monitoring" in results:
            dynamic_alerts = results["dynamic_monitoring"].get("alerts", [])
            for alert in dynamic_alerts:
                if self._is_severe_alert(alert):
                    severe_issues.append({
                        "type": "动态监控",
                        "severity": alert.get("severity", "unknown"),
                        "file": "系统监控",
                        "line": "N/A",
                        "message": alert.get("message", "unknown"),
                        "tool": "系统监控",
                        "issue_type": alert.get("type", "unknown")
                    })
        
        # 运行时分析问题
        if "runtime_analysis" in results:
            runtime = results["runtime_analysis"]
            if runtime.get("error"):
                severe_issues.append({
                    "type": "运行时分析",
                    "severity": "error",
                    "file": runtime.get("main_file", "unknown"),
                    "line": "N/A",
                    "message": runtime.get("error"),
                    "tool": "运行时分析",
                    "issue_type": "execution_error"
                })
        
        # 动态检测问题
        if "dynamic_detection" in results:
            dynamic_issues = results["dynamic_detection"].get("issues", [])
            for issue in dynamic_issues:
                if self._is_severe_dynamic_issue(issue):
                    severe_issues.append({
                        "type": "动态检测",
                        "severity": issue.get("severity", "unknown"),
                        "file": issue.get("file", "unknown"),
                        "line": issue.get("line", "N/A"),
                        "message": issue.get("message", "unknown"),
                        "tool": issue.get("test", "unknown"),
                        "issue_type": issue.get("type", "unknown")
                    })
        
        # 按严重程度和文件分组
        if severe_issues:
            # 按严重程度排序
            severity_order = {"error": 0, "critical": 0, "warning": 1, "info": 2}
            severe_issues.sort(key=lambda x: severity_order.get(x["severity"], 3))
            
            # 按文件分组
            issues_by_file = {}
            for issue in severe_issues:
                file_path = issue["file"]
                if file_path not in issues_by_file:
                    issues_by_file[file_path] = []
                issues_by_file[file_path].append(issue)
            
            # 生成报告内容
            report_lines.extend([
                f"**发现严重问题总数**: {len(severe_issues)}",
                "",
                "## 问题详情",
                ""
            ])
            
            # 按文件输出问题
            for file_path, file_issues in issues_by_file.items():
                report_lines.extend([
                    f"### 📁 {file_path}",
                    ""
                ])
                
                for issue in file_issues:
                    severity_emoji = {
                        "error": "❌",
                        "critical": "🚨",
                        "warning": "⚠️",
                        "info": "ℹ️"
                    }.get(issue["severity"], "❓")
                    
                    report_lines.extend([
                        f"**{severity_emoji} {issue['severity'].upper()}** - 第 {issue['line']} 行",
                        f"- **问题类型**: {issue['issue_type']}",
                        f"- **检测工具**: {issue['tool']}",
                        f"- **问题描述**: {issue['message']}",
                        ""
                    ])
            
            # 添加修复建议
            report_lines.extend([
                "## 修复建议",
                "",
                "### 优先级排序",
                "1. **立即修复**: 错误和严重问题",
                "2. **尽快修复**: 警告问题",
                "3. **计划修复**: 信息类问题",
                "",
                "### 修复步骤",
                "1. 按文件逐个处理问题",
                "2. 优先处理影响功能的关键问题",
                "3. 修复后重新运行检测验证",
                "4. 建立代码质量检查流程",
                ""
            ])
            
        else:
            report_lines.extend([
                "## 检测结果",
                "",
                "✅ **未发现严重问题**",
                "",
                "项目代码质量良好，未发现需要立即处理的严重问题。",
                "建议继续保持代码质量，定期进行代码审查。",
                ""
            ])
        
        # 添加统计信息
        summary = results.get("summary", {})
        report_lines.extend([
            "## 检测统计",
            "",
            f"- **总文件数**: {summary.get('total_files', 0)}",
            f"- **总问题数**: {summary.get('total_issues', 0)}",
            f"- **严重问题**: {summary.get('critical_issues', 0)}",
            f"- **警告问题**: {summary.get('warning_issues', 0)}",
            f"- **信息问题**: {summary.get('info_issues', 0)}",
            f"- **整体状态**: {summary.get('overall_status', 'unknown')}",
            "",
            "---",
            f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        ])
        
        return "\n".join(report_lines)
    
    def _is_severe_issue(self, issue: Dict[str, Any]) -> bool:
        """判断静态分析问题是否为严重问题"""
        # 排除格式化和风格问题
        excluded_types = {
            "import_style", "line_length", "trailing_whitespace", 
            "missing_whitespace", "extra_whitespace", "indentation",
            "blank_line", "spacing", "quotes", "docstring"
        }
        
        issue_type = issue.get("type", "").lower()
        severity = issue.get("severity", "").lower()
        
        # 如果是格式或风格问题，直接排除
        if issue_type in excluded_types:
            return False
        
        # 只保留错误和严重问题
        if severity in ["error", "critical"]:
            return True
        
        # 对于警告，只保留重要的类型
        if severity == "warning":
            important_warning_types = {
                "security", "performance", "logic_error", "unused_variable",
                "undefined_variable", "import_error", "syntax_error"
            }
            return issue_type in important_warning_types
        
        return False
    
    def _is_severe_alert(self, alert: Dict[str, Any]) -> bool:
        """判断动态监控告警是否为严重问题"""
        severity = alert.get("severity", "").lower()
        return severity in ["error", "critical", "warning"]
    
    def _is_severe_dynamic_issue(self, issue: Dict[str, Any]) -> bool:
        """判断动态检测问题是否为严重问题"""
        severity = issue.get("severity", "").lower()
        issue_type = issue.get("type", "").lower()
        
        # 只保留错误和严重问题
        if severity in ["error", "critical"]:
            return True
        
        # 对于警告，只保留重要的类型
        if severity == "warning":
            important_types = {
                "security", "performance", "functionality", "compatibility"
            }
            return issue_type in important_types
        
        return False

async def generate_ai_comprehensive_report(results: Dict[str, Any], filename: str) -> str:
    """生成AI综合检测报告"""
    try:
        if not deepseek_config.is_configured():
            print("⚠️ DeepSeek API未配置，使用基础报告")
            return generate_fallback_report(results, filename)
        
        prompt = build_comprehensive_analysis_prompt(results, filename)
        
        print("🤖 正在生成AI综合报告...")
        async with httpx.AsyncClient(timeout=180.0) as client:
            response = await client.post(
                f"{deepseek_config.base_url}/chat/completions",
                headers=deepseek_config.get_headers(),
                json={
                    "model": deepseek_config.model,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": deepseek_config.max_tokens,
                    "temperature": deepseek_config.temperature
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_content = result["choices"][0]["message"]["content"]
                print("✅ AI综合报告生成成功")
                return ai_content
            else:
                print(f"❌ AI API调用失败: {response.status_code}")
                return generate_fallback_report(results, filename)
                
    except httpx.TimeoutException:
        print("❌ AI API调用超时")
        return generate_fallback_report(results, filename)
    except httpx.RequestError as e:
        print(f"❌ AI API请求失败: {e}")
        return generate_fallback_report(results, filename)
    except Exception as e:
        print(f"❌ AI报告生成异常: {e}")
        return generate_fallback_report(results, filename)

def build_comprehensive_analysis_prompt(results: Dict[str, Any], filename: str) -> str:
    """构建综合分析提示词"""
    summary = results.get("summary", {})
    
    prompt = f"""请分析以下综合检测结果，生成一份详细的自然语言报告：

## 项目信息
- 文件名: {filename}
- 检测时间: {results.get('timestamp', 'unknown')}
- 检测类型: {results.get('detection_type', 'unknown')}
- 总文件数: {summary.get('total_files', 0)}

## 检测统计
- 总问题数: {summary.get('total_issues', 0)}
- 严重问题: {summary.get('critical_issues', 0)}
- 警告问题: {summary.get('warning_issues', 0)}
- 信息问题: {summary.get('info_issues', 0)}
- 整体状态: {summary.get('overall_status', 'unknown')}

## 静态分析结果
"""
    
    if "static_analysis" in results:
        static = results["static_analysis"]
        statistics = static.get("statistics", {})
        
        prompt += f"- 分析类型: {static.get('analysis_type', 'unknown')}\n"
        prompt += f"- 分析文件数: {static.get('files_analyzed', 0)}\n"
        prompt += f"- 总文件数: {statistics.get('total_files', 0)}\n"
        prompt += f"- 总代码行数: {statistics.get('total_lines', 0)}\n"
        prompt += f"- 平均复杂度: {statistics.get('average_complexity', 0)}\n"
        prompt += f"- 可维护性评分: {statistics.get('maintainability_score', 0)}\n"
        prompt += f"- 发现问题数: {len(static.get('issues', []))}\n"
        
        # 添加问题统计
        issues_by_severity = statistics.get("issues_by_severity", {})
        issues_by_tool = statistics.get("issues_by_tool", {})
        
        if issues_by_severity:
            prompt += "\n### 问题严重程度分布:\n"
            for severity, count in issues_by_severity.items():
                prompt += f"- {severity}: {count}个\n"
        
        if issues_by_tool:
            prompt += "\n### 分析工具统计:\n"
            for tool, count in issues_by_tool.items():
                prompt += f"- {tool}: {count}个问题\n"
    
    prompt += "\n## 动态监控结果\n"
    if "dynamic_monitoring" in results:
        dynamic = results["dynamic_monitoring"]
        prompt += f"- 监控时长: {dynamic.get('duration', 0)}秒\n"
        prompt += f"- 告警数量: {len(dynamic.get('alerts', []))}\n"
    
    prompt += "\n## 运行时分析结果（独立检测模块）\n"
    prompt += "注意：运行时分析仅用于检查项目主文件能否直接执行，与动态检测的测试成功率是独立的。\n"
    if "runtime_analysis" in results:
        runtime = results["runtime_analysis"]
        prompt += f"- 主文件: {runtime.get('main_file', 'N/A')}\n"
        prompt += f"- 执行状态: {'成功' if runtime.get('execution_successful', False) else '失败'}\n"
        if runtime.get("error"):
            prompt += f"- 错误信息: {runtime.get('error')}\n"
    
    prompt += "\n## 动态检测结果（Flask功能测试）\n"
    prompt += "注意：动态检测通过实际运行Flask应用并执行功能测试来检测缺陷，与运行时分析是独立的检测模块。\n"
    if "dynamic_detection" in results:
        dynamic_detection = results["dynamic_detection"]
        prompt += f"- 状态: {dynamic_detection.get('status', 'unknown')}\n"
        prompt += f"- 是Flask项目: {dynamic_detection.get('is_flask_project', False)}\n"
        prompt += f"- 测试完成: {dynamic_detection.get('tests_completed', False)}\n"
        prompt += f"- 测试成功率: {dynamic_detection.get('success_rate', 0)}%\n"
        prompt += f"- 发现问题数: {len(dynamic_detection.get('issues', []))}\n"
        prompt += "重要说明：\n"
        prompt += "- 如果测试完成且成功率为100%，说明动态检测测试执行成功\n"
        prompt += "- 运行时分析失败不影响动态检测的成功（两者检测方式不同）\n"
        prompt += "- 动态检测的成功率反映的是功能测试的通过率，而不是检测本身的失败\n"
    
    prompt += """
请生成一份详细的自然语言分析报告，包括：
1. 项目概述
2. 问题分析（请明确区分运行时分析失败和动态检测失败，它们是不同的检测模块）
3. 风险评估
4. 改进建议
5. 总结

报告应该专业、详细且易于理解。
特别注意：
- 如果动态检测显示"测试完成: True, 成功率: 100%"，说明动态检测本身是成功的
- 运行时分析失败只表示主文件无法直接执行，不代表动态检测失败
- 请在报告中明确说明这两个检测模块的区别和各自的检测结果"""
    
    return prompt

def generate_fallback_report(results: Dict[str, Any], filename: str) -> str:
    """生成基础报告（当AI API不可用时）"""
    summary = results.get("summary", {})
    
    report = f"""# 综合检测报告

## 项目概述
- **项目名称**: {filename}
- **检测时间**: {results.get('timestamp', 'unknown')}
- **检测类型**: {results.get('detection_type', 'unknown')}
- **总文件数**: {summary.get('total_files', 0)}

## 检测结果摘要
- **总问题数**: {summary.get('total_issues', 0)}
- **严重问题**: {summary.get('critical_issues', 0)}
- **警告问题**: {summary.get('warning_issues', 0)}
- **信息问题**: {summary.get('info_issues', 0)}
- **整体状态**: {summary.get('overall_status', 'unknown')}

## 问题分析
"""
    
    if summary.get('critical_issues', 0) > 0:
        report += "⚠️ **发现严重问题**，需要立即处理\n"
    if summary.get('warning_issues', 0) > 0:
        report += "⚠️ **发现警告问题**，建议及时处理\n"
    if summary.get('info_issues', 0) > 0:
        report += "ℹ️ **发现信息问题**，可选择性处理\n"
    
    if summary.get('total_issues', 0) == 0:
        report += "✅ **未发现明显问题**\n"
    
    # 添加建议
    recommendations = summary.get('recommendations', [])
    if recommendations:
        report += "\n## 改进建议\n"
        for i, rec in enumerate(recommendations, 1):
            report += f"{i}. {rec}\n"
    
    report += "\n## 总结\n"
    if summary.get('overall_status') == 'good':
        report += "项目整体质量良好，未发现严重问题。建议继续保持代码质量，定期进行代码审查。"
    elif summary.get('overall_status') == 'warning':
        report += "项目存在一些警告问题，建议及时处理。重点关注代码质量和可维护性。"
    elif summary.get('overall_status') == 'error':
        report += "项目存在严重问题，需要立即修复。建议优先处理严重问题，然后逐步改进代码质量。"
    else:
        report += "请根据具体问题情况进行相应处理。建议定期进行代码质量检查。"
    
    return report

# API端点
@router.get("/")
async def root():
    """根路径"""
    return {
        "message": "综合检测API运行中",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/health")
async def health():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "comprehensive_detection"
    }

@router.post("/detect", response_model=BaseResponse)
async def comprehensive_detect(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(None),
    files: List[UploadFile] = File(None),
    static_analysis: str = Form("true"),
    dynamic_monitoring: str = Form("true"),
    runtime_analysis: str = Form("true"),
    enable_web_app_test: str = Form("false"),
    enable_dynamic_detection: str = Form("true"),
    enable_flask_specific_tests: str = Form("true"),
    enable_server_testing: str = Form("true"),
    upload_type: str = Form("file")
):
    """综合检测 - 并行执行静态检测和动态检测"""
    
    # 确保所有布尔参数都是布尔值
    def convert_to_bool(value, param_name):
        if isinstance(value, str):
            result = value.lower() in ('true', '1', 'yes', 'on')
            return result
        elif isinstance(value, bool):
            return value
        else:
            return bool(value)
    
    static_analysis = convert_to_bool(static_analysis, 'static_analysis')
    dynamic_monitoring = convert_to_bool(dynamic_monitoring, 'dynamic_monitoring')
    runtime_analysis = convert_to_bool(runtime_analysis, 'runtime_analysis')
    enable_web_app_test = convert_to_bool(enable_web_app_test, 'enable_web_app_test')
    enable_dynamic_detection = convert_to_bool(enable_dynamic_detection, 'enable_dynamic_detection')
    enable_flask_specific_tests = convert_to_bool(enable_flask_specific_tests, 'enable_flask_specific_tests')
    enable_server_testing = convert_to_bool(enable_server_testing, 'enable_server_testing')
    
    # 验证输入
    if not file and not files:
        raise HTTPException(status_code=400, detail="请提供文件或文件列表")
    
    if file and files:
        raise HTTPException(status_code=400, detail="请选择单文件上传或目录上传，不能同时使用")
    
    # 处理单文件上传（压缩包）
    if file:
        if not file.filename.endswith('.zip'):
            raise HTTPException(status_code=400, detail="只支持ZIP格式的压缩包")
        upload_files = [file]
        filename = file.filename
    else:
        # 处理多文件上传（目录）
        if not files or len(files) == 0:
            raise HTTPException(status_code=400, detail="目录上传需要至少一个文件")
        upload_files = files
        filename = f"directory_{len(files)}_files"
    
    temp_file_path = None
    temp_dir = None
    
    try:
        print(f"开始处理上传文件: {filename}")
        
        if upload_type == "file":
            # 单文件上传（压缩包）
            file = upload_files[0]
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
                content = await file.read()
                tmp_file.write(content)
                temp_file_path = tmp_file.name
            print(f"压缩包已保存到临时位置: {temp_file_path}")
        else:
            # 目录上传（多文件）
            temp_dir = tempfile.mkdtemp(prefix="comprehensive_detection_")
            print(f"创建临时目录: {temp_dir}")
            
            # 保存所有文件到临时目录
            for file in upload_files:
                if file.filename:
                    # 处理文件路径结构
                    if '/' in file.filename or '\\' in file.filename:
                        file_path = os.path.join(temp_dir, file.filename)
                    else:
                        file_path = os.path.join(temp_dir, file.filename)
                    
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    
                    with open(file_path, "wb") as f:
                        content = await file.read()
                        f.write(content)
                    print(f"保存文件: {file.filename} -> {file_path}")
            
            # 创建ZIP文件
            temp_file_path = os.path.join(temp_dir, "project.zip")
            with zipfile.ZipFile(temp_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if file != "project.zip":  # 避免包含自己
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, temp_dir)
                            zipf.write(file_path, arcname)
            
            print(f"目录已打包为ZIP: {temp_file_path}")
        
        # 为每个请求创建独立的检测器实例
        detector = ComprehensiveDetector(static_agent, dynamic_agent)
        detector.enable_web_app_test = enable_web_app_test
        detector.enable_dynamic_detection = enable_dynamic_detection
        detector.enable_flask_specific_tests = enable_flask_specific_tests
        detector.enable_server_testing = enable_server_testing
        
        # 执行检测（添加超时处理）
        print("开始执行综合检测...")
        if enable_web_app_test or enable_server_testing:
            print("⚠️ 已启用Web应用测试，检测时间可能较长...")
        
        try:
            results = await asyncio.wait_for(
                detector.detect_defects(
                    zip_file_path=temp_file_path,
                    static_analysis=static_analysis,
                    dynamic_monitoring=dynamic_monitoring,
                    runtime_analysis=runtime_analysis,
                    enable_dynamic_detection=enable_dynamic_detection,
                    enable_flask_specific_tests=enable_flask_specific_tests,
                    enable_server_testing=enable_server_testing,
                    enable_web_app_test=enable_web_app_test
                ),
                timeout=600  # 10分钟超时
            )
        except asyncio.TimeoutError:
            return BaseResponse(
                success=False,
                error="检测超时（10分钟）",
                message="检测过程超时，请尝试上传较小的项目"
            )
        
        print("检测完成，生成报告...")
        
        # 生成文本报告
        report = detector.generate_report(results)
        
        # 生成AI报告
        try:
            ai_report = await generate_ai_comprehensive_report(results, file.filename)
            print("✅ AI报告生成成功")
        except Exception as e:
            print(f"⚠️ AI报告生成失败: {e}")
            ai_report = {
                "success": False,
                "error": str(e),
                "summary": "AI报告生成失败，请查看详细检测结果"
            }
        
        # 保存结果到文件
        try:
            results_file = f"comprehensive_detection_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            results_dir = Path("comprehensive_detection_results")
            results_dir.mkdir(exist_ok=True)
            results_path = results_dir / results_file
            detector.save_results(results, str(results_path))
            print(f"✅ 结果已保存到: {results_path}")
        except Exception as e:
            print(f"⚠️ 保存结果文件失败: {e}")
            results_file = None
        
        # 返回结果
        return BaseResponse(
            success=True,
            message="综合检测完成",
            data={
                "results": results,
                "report": report,
                "ai_report": ai_report,
                "results_file": results_file,
                "filename": file.filename,
                "detection_time": datetime.now().isoformat()
            }
        )
    
    finally:
        # 清理临时文件
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
                print(f"已清理临时文件: {temp_file_path}")
            except Exception as e:
                print(f"清理临时文件失败: {e}")
        
        # 清理临时目录
        if temp_dir and os.path.exists(temp_dir):
            try:
                import shutil
                shutil.rmtree(temp_dir)
                print(f"已清理临时目录: {temp_dir}")
            except Exception as e:
                print(f"清理临时目录失败: {e}")

@router.get("/status")
async def get_detection_status():
    """获取检测状态"""
    return {
        "status": "ready",
        "timestamp": datetime.now().isoformat(),
        "supported_formats": [".zip"],
        "features": {
            "static_analysis": True,
            "dynamic_monitoring": True,
            "runtime_analysis": True,
            "comprehensive_detection": True
        }
    }

@router.post("/generate-severe-issues-report")
async def generate_severe_issues_report(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(None),
    files: List[UploadFile] = File(None),
    static_analysis: str = Form("true"),
    dynamic_monitoring: str = Form("true"),
    runtime_analysis: str = Form("true"),
    enable_web_app_test: str = Form("false"),
    enable_dynamic_detection: str = Form("true"),
    enable_flask_specific_tests: str = Form("true"),
    enable_server_testing: str = Form("true"),
    upload_type: str = Form("file")
):
    """生成严重问题汇总文档"""
    
    # 确保所有布尔参数都是布尔值
    def convert_to_bool(value, param_name):
        if isinstance(value, str):
            result = value.lower() in ('true', '1', 'yes', 'on')
            return result
        elif isinstance(value, bool):
            return value
        else:
            return bool(value)
    
    static_analysis = convert_to_bool(static_analysis, 'static_analysis')
    dynamic_monitoring = convert_to_bool(dynamic_monitoring, 'dynamic_monitoring')
    runtime_analysis = convert_to_bool(runtime_analysis, 'runtime_analysis')
    enable_web_app_test = convert_to_bool(enable_web_app_test, 'enable_web_app_test')
    enable_dynamic_detection = convert_to_bool(enable_dynamic_detection, 'enable_dynamic_detection')
    enable_flask_specific_tests = convert_to_bool(enable_flask_specific_tests, 'enable_flask_specific_tests')
    enable_server_testing = convert_to_bool(enable_server_testing, 'enable_server_testing')
    
    # 验证输入
    if not file and not files:
        raise HTTPException(status_code=400, detail="请提供文件或文件列表")
    
    if file and files:
        raise HTTPException(status_code=400, detail="请选择单文件上传或目录上传，不能同时使用")
    
    # 处理单文件上传（压缩包）
    if file:
        if not file.filename.endswith('.zip'):
            raise HTTPException(status_code=400, detail="只支持ZIP格式的压缩包")
        upload_files = [file]
        filename = file.filename
    else:
        # 处理多文件上传（目录）
        if not files or len(files) == 0:
            raise HTTPException(status_code=400, detail="目录上传需要至少一个文件")
        upload_files = files
        filename = f"directory_{len(files)}_files"
    
    temp_file_path = None
    temp_dir = None
    
    try:
        print(f"开始处理上传文件: {filename}")
        
        if upload_type == "file":
            # 单文件上传（压缩包）
            file = upload_files[0]
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
                content = await file.read()
                tmp_file.write(content)
                temp_file_path = tmp_file.name
            print(f"压缩包已保存到临时位置: {temp_file_path}")
        else:
            # 目录上传（多文件）
            temp_dir = tempfile.mkdtemp(prefix="comprehensive_detection_")
            print(f"创建临时目录: {temp_dir}")
            
            # 保存所有文件到临时目录
            for file in upload_files:
                if file.filename:
                    # 处理文件路径结构
                    if '/' in file.filename or '\\' in file.filename:
                        file_path = os.path.join(temp_dir, file.filename)
                    else:
                        file_path = os.path.join(temp_dir, file.filename)
                    
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    
                    with open(file_path, "wb") as f:
                        content = await file.read()
                        f.write(content)
                    print(f"保存文件: {file.filename} -> {file_path}")
            
            # 创建ZIP文件
            temp_file_path = os.path.join(temp_dir, "project.zip")
            with zipfile.ZipFile(temp_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if file != "project.zip":  # 避免包含自己
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, temp_dir)
                            zipf.write(file_path, arcname)
            
            print(f"目录已打包为ZIP: {temp_file_path}")
        
        # 为每个请求创建独立的检测器实例
        detector = ComprehensiveDetector(static_agent, dynamic_agent)
        detector.enable_web_app_test = enable_web_app_test
        detector.enable_dynamic_detection = enable_dynamic_detection
        detector.enable_flask_specific_tests = enable_flask_specific_tests
        detector.enable_server_testing = enable_server_testing
        
        # 执行检测
        print("开始执行综合检测...")
        try:
            results = await asyncio.wait_for(
                detector.detect_defects(
                    zip_file_path=temp_file_path,
                    static_analysis=static_analysis,
                    dynamic_monitoring=dynamic_monitoring,
                    runtime_analysis=runtime_analysis,
                    enable_dynamic_detection=enable_dynamic_detection,
                    enable_flask_specific_tests=enable_flask_specific_tests,
                    enable_server_testing=enable_server_testing,
                    enable_web_app_test=enable_web_app_test
                ),
                timeout=600  # 10分钟超时
            )
        except asyncio.TimeoutError:
            return BaseResponse(
                success=False,
                error="检测超时（10分钟）",
                message="检测过程超时，请尝试上传较小的项目"
            )
        
        print("检测完成，生成严重问题汇总文档...")
        
        # 生成严重问题汇总文档
        severe_issues_report = detector.generate_severe_issues_report(results, filename)
        
        # 保存文档到result文件夹
        try:
            report_filename = f"severe_issues_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            result_dir = Path("result")
            result_dir.mkdir(exist_ok=True)
            report_path = result_dir / report_filename
            
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(severe_issues_report)
            
            print(f"✅ 严重问题汇总文档已保存到: {report_path}")
        except Exception as e:
            print(f"⚠️ 保存文档文件失败: {e}")
            report_filename = None
        
        # 返回结果
        return BaseResponse(
            success=True,
            message="严重问题汇总文档生成完成",
            data={
                "severe_issues_report": severe_issues_report,
                "report_filename": report_filename,
                "report_path": str(report_path) if report_filename else None,
                "filename": filename,
                "generation_time": datetime.now().isoformat(),
                "summary": results.get("summary", {})
            }
        )
    
    finally:
        # 清理临时文件
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
                print(f"已清理临时文件: {temp_file_path}")
            except Exception as e:
                print(f"清理临时文件失败: {e}")
        
        # 清理临时目录
        if temp_dir and os.path.exists(temp_dir):
            try:
                import shutil
                shutil.rmtree(temp_dir)
                print(f"已清理临时目录: {temp_dir}")
            except Exception as e:
                print(f"清理临时目录失败: {e}")
