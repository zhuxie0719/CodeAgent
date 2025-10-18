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

static_agent = BugDetectionAgent({
    "enable_ai_analysis": True,
    "analysis_depth": "comprehensive"
})

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
                           enable_server_testing: bool = True) -> Dict[str, Any]:
        """执行综合检测"""
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
                "enable_server_testing": enable_server_testing
            }
        }
        
        try:
            # 检查文件大小
            file_size = os.path.getsize(zip_file_path)
            max_size = 50 * 1024 * 1024  # 50MB限制
            
            if file_size > max_size:
                results["error"] = f"文件过大 ({file_size // (1024*1024)}MB > {max_size // (1024*1024)}MB)"
                return results
            
            # 解压项目
            import zipfile
            import tempfile
            import shutil
            
            extract_dir = tempfile.mkdtemp()
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
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
            
            # 等待所有任务完成
            if tasks:
                task_results = await asyncio.gather(*tasks, return_exceptions=True)
                
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
            
            # 清理临时目录
            shutil.rmtree(extract_dir, ignore_errors=True)
            
            return results
            
        except Exception as e:
            results["error"] = str(e)
            # 即使出现错误也要生成summary
            results["summary"] = self._generate_summary(results)
            return results
    
    def _list_files(self, project_path: str) -> List[str]:
        """列出项目文件"""
        files = []
        for root, dirs, filenames in os.walk(project_path):
            for filename in filenames:
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
                return analysis_result.get("detection_results", {})
            else:
                return {
                    "error": analysis_result.get("error", "静态分析失败"),
                    "issues": []
                }
        except Exception as e:
            return {"error": str(e), "issues": []}
    
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
        if not results.get("runtime_analysis", {}).get("execution_successful", True):
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
    
    prompt += "\n## 运行时分析结果\n"
    if "runtime_analysis" in results:
        runtime = results["runtime_analysis"]
        prompt += f"- 主文件: {runtime.get('main_file', 'N/A')}\n"
        prompt += f"- 执行状态: {'成功' if runtime.get('execution_successful', False) else '失败'}\n"
        if runtime.get("error"):
            prompt += f"- 错误信息: {runtime.get('error')}\n"
    
    prompt += "\n## 动态检测结果\n"
    if "dynamic_detection" in results:
        dynamic_detection = results["dynamic_detection"]
        prompt += f"- 状态: {dynamic_detection.get('status', 'unknown')}\n"
        prompt += f"- 是Flask项目: {dynamic_detection.get('is_flask_project', False)}\n"
        prompt += f"- 测试完成: {dynamic_detection.get('tests_completed', False)}\n"
        prompt += f"- 成功率: {dynamic_detection.get('success_rate', 0)}%\n"
    
    prompt += """
请生成一份详细的自然语言分析报告，包括：
1. 项目概述
2. 问题分析
3. 风险评估
4. 改进建议
5. 总结

报告应该专业、详细且易于理解。"""
    
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
                    enable_server_testing=enable_server_testing
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
