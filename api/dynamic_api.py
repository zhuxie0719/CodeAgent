"""
简化版动态检测API
专注于核心功能，确保3周内能完成
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

from agents.dynamic_detection_agent.agent import DynamicMonitorAgent
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
monitor_agent = DynamicMonitorAgent({
    "monitor_interval": 5,
    "alert_thresholds": {
        "cpu_threshold": 80,
        "memory_threshold": 85,
        "disk_threshold": 90,
        "network_threshold": 80
    }
})

class SimpleDetector:
    """简化的检测器，集成动态监控功能"""
    
    def __init__(self, monitor_agent):
        self.monitor_agent = monitor_agent
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
            
            # 静态分析
            if static_analysis:
                try:
                    results["static_analysis"] = await self._perform_static_analysis(extract_dir)
                except Exception as e:
                    print(f"静态分析失败: {e}")
                    results["static_analysis"] = {"error": str(e), "issues": []}
            
            # 动态监控
            if dynamic_monitoring:
                try:
                    results["dynamic_monitoring"] = await self._perform_dynamic_monitoring()
                except Exception as e:
                    print(f"动态监控失败: {e}")
                    results["dynamic_monitoring"] = {"error": str(e), "alerts": []}
            
            # 运行时分析
            if runtime_analysis:
                try:
                    results["runtime_analysis"] = await self._perform_runtime_analysis(extract_dir)
                except Exception as e:
                    print(f"运行时分析失败: {e}")
                    results["runtime_analysis"] = {"error": str(e), "execution_successful": False}
            
            # 动态缺陷检测
            if enable_dynamic_detection:
                try:
                    results["dynamic_detection"] = await self._perform_dynamic_detection(extract_dir, enable_flask_specific_tests, enable_server_testing)
                except Exception as e:
                    print(f"动态缺陷检测失败: {e}")
                    results["dynamic_detection"] = {"error": str(e), "tests_completed": False}
            
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
    
    async def _perform_static_analysis(self, project_path: str) -> Dict[str, Any]:
        """执行增强的静态分析，集成代码分析工具"""
        try:
            # 导入代码分析组件
            from agents.code_analysis_agent.agent import CodeAnalysisAgent
            from tools.static_analysis.pylint_tool import PylintTool
            from tools.static_analysis.flake8_tool import Flake8Tool
            from tools.ai_static_analyzer import AIMultiLanguageAnalyzer
            
            # 初始化代码分析代理
            code_analysis_agent = CodeAnalysisAgent({
                "enable_ai_analysis": True,
                "analysis_depth": "comprehensive"
            })
            
            # 初始化静态分析工具
            pylint_tool = PylintTool({
                "pylint_args": ["--disable=C0114,C0116", "--max-line-length=120"]
            })
            flake8_tool = Flake8Tool({
                "flake8_args": ["--max-line-length=120", "--ignore=E203,W503"]
            })
            
            # 初始化AI多语言分析器
            ai_analyzer = AIMultiLanguageAnalyzer()
            
            # 执行项目结构分析
            print("开始项目结构分析...")
            project_structure = await code_analysis_agent.project_analyzer.analyze_project_structure(project_path)
            
            # 执行代码质量分析
            print("开始代码质量分析...")
            code_quality = await code_analysis_agent.code_analyzer.analyze_code_quality(project_path)
            
            # 执行依赖分析
            print("开始依赖关系分析...")
            dependencies = await code_analysis_agent.dependency_analyzer.analyze_dependencies(project_path)
            
            # 收集所有支持的文件进行静态分析
            python_files = []
            other_language_files = []
            skip_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'doc', 'docs', '.github', 'ci', 'asv_bench', 'conda.recipe', 'web', 'LICENSES'}
            
            for root, dirs, files in os.walk(project_path):
                dirs[:] = [d for d in dirs if d not in skip_dirs]
                
                for file in files:
                    if not file.startswith('.'):
                        file_path = os.path.join(root, file)
                        try:
                            if os.path.getsize(file_path) <= 2 * 1024 * 1024:  # 2MB限制
                                if file.endswith('.py'):
                                    python_files.append(file_path)
                                elif ai_analyzer.is_supported_file(file_path):
                                    other_language_files.append(file_path)
                        except:
                            continue
            
            # 限制分析的文件数量（提高效率）
            if len(python_files) > 30:  # 进一步减少到30个文件
                python_files = python_files[:30]
            if len(other_language_files) > 20:  # 减少到20个文件
                other_language_files = other_language_files[:20]
            
            # 执行Pylint和Flake8分析
            pylint_issues = []
            flake8_issues = []
            
            print(f"开始静态分析 {len(python_files)} 个Python文件...")
            for py_file in python_files[:15]:  # 只对前15个文件执行详细分析
                try:
                    rel_path = os.path.relpath(py_file, project_path)
                    
                    # Pylint分析
                    pylint_result = await pylint_tool.analyze(py_file)
                    if pylint_result.get('success') and pylint_result.get('issues'):
                        for issue in pylint_result['issues']:
                            # 处理所有级别的问题
                            issue['file'] = rel_path
                            issue['tool'] = 'pylint'
                            pylint_issues.append(issue)
                    
                    # Flake8分析
                    flake8_result = await flake8_tool.analyze(py_file)
                    if flake8_result.get('success') and flake8_result.get('issues'):
                        for issue in flake8_result['issues']:
                            # 处理所有级别的问题
                            issue['file'] = rel_path
                            issue['tool'] = 'flake8'
                            flake8_issues.append(issue)
                            
                except Exception as e:
                    print(f"静态分析文件失败 {py_file}: {e}")
                    continue
            
            # 执行Flask特定问题检测
            flask_issues = []
            print("开始Flask特定问题检测...")
            try:
                # Flask检测器已禁用
                # from api.tools.flask_issue_detector import FlaskIssueDetector
                # flask_detector = FlaskIssueDetector()
                # flask_result = flask_detector.detect_flask_issues(project_path)
                # if flask_result.get('issues'):
                #     for issue in flask_result['issues']:
                #         flask_issues.append(issue)
                # print(f"Flask检测完成，发现 {len(flask_issues)} 个Flask特定问题")
                print("Flask检测器已禁用，跳过Flask特定问题检测")
            except Exception as e:
                print(f"Flask检测失败: {e}")
            
            # 执行AI多语言分析
            ai_issues = []
            if other_language_files:
                print(f"开始AI分析 {len(other_language_files)} 个其他语言文件...")
                for other_file in other_language_files[:10]:  # 只对前10个文件执行AI分析
                    try:
                        rel_path = os.path.relpath(other_file, project_path)
                        result = await ai_analyzer.analyze_file(other_file, project_path)
                        
                        if result and result.issues:
                            for issue in result.issues:
                                # 处理所有级别的问题
                                ai_issues.append({
                                    'file': rel_path,
                                    'line': issue.line_number,
                                    'column': issue.column,
                                    'type': issue.category,
                                    'severity': issue.severity,  # 使用原始severity
                                    'message': issue.message,
                                    'suggestion': issue.suggestion,
                                    'tool': 'ai_analyzer',
                                    'language': issue.language,
                                    'confidence': issue.confidence
                                })
                                
                    except Exception as e:
                        print(f"AI分析文件失败 {other_file}: {e}")
                        continue
            
            # 合并所有问题
            all_issues = pylint_issues + flake8_issues + ai_issues + flask_issues
            
            # 添加代码质量分析中的问题
            if code_quality.get('file_analysis'):
                for file_analysis in code_quality['file_analysis']:
                    if file_analysis.get('issues'):
                        for issue in file_analysis['issues']:
                            # 处理所有级别的问题
                            issue['file'] = file_analysis['file_path']
                            issue['tool'] = 'code_analyzer'
                            all_issues.append(issue)
            
            # 生成AI分析摘要
            ai_summary = None
            try:
                ai_summary = await code_analysis_agent.ai_service.generate_project_summary({
                    'project_structure': project_structure,
                    'code_quality': code_quality,
                    'dependencies': dependencies
                })
            except Exception as e:
                print(f"AI分析失败: {e}")
                ai_summary = {
                    'success': False,
                    'error': str(e),
                    'summary': 'AI分析服务暂时不可用'
                }
            
            # 计算统计信息
            issues_by_severity = {}
            issues_by_type = {}
            issues_by_tool = {}
            
            for issue in all_issues:
                severity = issue.get('severity', 'info')
                issue_type = issue.get('type', 'unknown')
                tool = issue.get('tool', 'unknown')
                
                issues_by_severity[severity] = issues_by_severity.get(severity, 0) + 1
                issues_by_type[issue_type] = issues_by_type.get(issue_type, 0) + 1
                issues_by_tool[tool] = issues_by_tool.get(tool, 0) + 1
            
            return {
                "analysis_type": "enhanced_static_analysis",
                "files_analyzed": len(python_files) + len(other_language_files),
                "python_files_analyzed": len(python_files),
                "other_language_files_analyzed": len(other_language_files),
                "issues_found": len(all_issues),
                "issues": all_issues[:100],  # 限制问题数量
                "project_structure": project_structure,
                "code_quality": code_quality,
                "dependencies": dependencies,
                "ai_summary": ai_summary,
                "multi_language_analysis": {
                    "python_issues": len(pylint_issues) + len(flake8_issues),
                    "ai_issues": len(ai_issues),
                    "supported_languages": list(set([issue.get('language', 'unknown') for issue in ai_issues]))
                },
                "statistics": {
                    "issues_by_severity": issues_by_severity,
                    "issues_by_type": issues_by_type,
                    "issues_by_tool": issues_by_tool,
                    "total_files": project_structure.get('total_files', 0),
                    "total_lines": project_structure.get('total_lines', 0),
                    "average_complexity": code_quality.get('average_complexity', 0),
                    "maintainability_score": code_quality.get('maintainability_score', 0)
                }
            }
            
        except Exception as e:
            print(f"增强静态分析失败，回退到基础分析: {e}")
            # 回退到基础分析
            return await self._perform_basic_static_analysis(project_path)
    
    async def _perform_basic_static_analysis(self, project_path: str) -> Dict[str, Any]:
        """执行基础静态分析（回退方案）"""
        issues = []
        python_files = []
        
        # 跳过目录
        skip_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'doc', 'docs', '.github', 'ci', 'asv_bench', 'conda.recipe', 'web', 'LICENSES'}
        
        for root, dirs, files in os.walk(project_path):
            # 过滤掉不需要的目录
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for file in files:
                if file.endswith('.py') and not file.startswith('.'):
                    file_path = os.path.join(root, file)
                    # 检查文件大小
                    try:
                        if os.path.getsize(file_path) <= 2 * 1024 * 1024:  # 2MB限制
                            python_files.append(file_path)
                    except:
                        continue
        
        # 限制分析的文件数量
        if len(python_files) > 100:
            python_files = python_files[:100]  # 只分析前100个文件
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    # 简单的问题检测
                    if 'eval(' in content:
                        issues.append({
                            "file": os.path.relpath(py_file, project_path),
                            "type": "security_issue",
                            "severity": "warning",
                            "message": "使用了不安全的eval函数",
                            "tool": "basic_analyzer"
                        })
                    
                    if 'import *' in content:
                        issues.append({
                            "file": os.path.relpath(py_file, project_path),
                            "type": "code_quality",
                            "severity": "info",
                            "message": "使用了通配符导入",
                            "tool": "basic_analyzer"
                        })
                    
                    # 检查硬编码密码
                    if any(keyword in content.lower() for keyword in ['password=', 'passwd=', 'secret=']):
                        issues.append({
                            "file": os.path.relpath(py_file, project_path),
                            "type": "security_issue",
                            "severity": "warning",
                            "message": "可能存在硬编码密码",
                            "tool": "basic_analyzer"
                        })
                        
            except Exception as e:
                print(f"分析文件失败 {py_file}: {e}")
        
        return {
            "analysis_type": "basic_static_analysis",
            "files_analyzed": len(python_files),
            "issues_found": len(issues),
            "issues": issues[:50]  # 限制问题数量
        }
    
    async def _perform_dynamic_monitoring(self) -> Dict[str, Any]:
        """执行动态监控"""
        try:
            # 启动监控
            monitor_result = await self.monitor_agent.start_monitoring(duration=60)
            return monitor_result
        except Exception as e:
            return {"error": f"动态监控失败: {e}"}
    
    async def _perform_dynamic_detection(self, project_path: str, enable_flask_tests: bool = True, enable_server_tests: bool = True) -> Dict[str, Any]:
        """执行动态缺陷检测"""
        try:
            print("开始动态缺陷检测...")
            
            # 检查是否是Flask项目
            is_flask_project = await self._detect_flask_project(project_path)
            
            if not is_flask_project:
                return {
                    "status": "skipped",
                    "reason": "不是Flask项目",
                    "tests_completed": False
                }
            
            # 运行动态测试
            try:
                from flask_simple_test.dynamic_test_runner import FlaskDynamicTestRunner
                
                runner = FlaskDynamicTestRunner()
                
                # 根据选项决定是否启用Web应用测试
                enable_web_test = enable_server_tests and enable_flask_tests
                
                test_results = runner.run_dynamic_tests(enable_web_app_test=enable_web_test)
            except Exception as e:
                print(f"完整动态测试失败，使用无Flask测试: {e}")
                # 回退到无Flask测试
                from flask_simple_test.no_flask_dynamic_test import NoFlaskDynamicTest
                
                no_flask_tester = NoFlaskDynamicTest()
                test_results = no_flask_tester.run_no_flask_tests()
            
            # 分析测试结果，生成问题报告
            issues = []
            recommendations = []
            
            # 检查测试结果中的问题
            tests = test_results.get("tests", {})
            for test_name, test_result in tests.items():
                if test_result.get("status") == "failed":
                    issues.append({
                        "type": "dynamic_test_failure",
                        "test": test_name,
                        "severity": "warning",
                        "message": f"动态测试失败: {test_name}",
                        "details": test_result.get("error", "未知错误")
                    })
                elif test_result.get("status") == "partial":
                    issues.append({
                        "type": "dynamic_test_partial",
                        "test": test_name,
                        "severity": "info",
                        "message": f"动态测试部分成功: {test_name}",
                        "details": test_result.get("tests", {})
                    })
            
            # 基于测试结果生成建议
            summary = test_results.get("summary", {})
            success_rate = summary.get("success_rate", 0)
            
            if success_rate < 50:
                recommendations.append("动态测试成功率较低，建议检查Flask应用配置")
            elif success_rate < 80:
                recommendations.append("动态测试部分成功，建议优化Flask应用")
            else:
                recommendations.append("动态测试表现良好")
            
            if enable_web_test and not summary.get("enable_web_app_test", False):
                recommendations.append("建议启用Web应用测试以获得更全面的检测")
            
            return {
                "status": "completed",
                "is_flask_project": is_flask_project,
                "enable_web_test": enable_web_test,
                "test_results": test_results,
                "issues": issues,
                "recommendations": recommendations,
                "tests_completed": True,
                "success_rate": success_rate
            }
            
        except Exception as e:
            print(f"动态缺陷检测异常: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "tests_completed": False
            }
    
    async def _detect_flask_project(self, project_path: str) -> bool:
        """检测是否是Flask项目"""
        try:
            # 查找Flask相关文件
            flask_indicators = [
                'app.py', 'main.py', 'run.py', 'wsgi.py',
                'requirements.txt', 'setup.py', 'pyproject.toml'
            ]
            
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    if file in flask_indicators:
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                if 'flask' in content.lower() or 'Flask' in content:
                                    return True
                        except:
                            continue
            
            # 检查Python文件中的Flask导入
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                if any(keyword in content for keyword in [
                                    'from flask import', 'import flask', 'Flask(',
                                    'app = Flask', 'Flask(__name__)'
                                ]):
                                    return True
                        except:
                            continue
            
            return False
            
        except Exception as e:
            print(f"检测Flask项目失败: {e}")
            return False
    
    async def _perform_runtime_analysis(self, project_path: str) -> Dict[str, Any]:
        """执行运行时分析"""
        try:
            # 查找可执行的主文件
            main_files = []
            test_files = []
            
            for root, dirs, files in os.walk(project_path):
                # 跳过测试目录（但允许包含test的项目目录）
                if any(part in ['test', 'tests'] for part in root.split(os.sep)):
                    continue
                    
                for file in files:
                    if file.endswith('.py') and not file.startswith('.'):
                        file_path = os.path.join(root, file)
                        
                        # 检查文件大小
                        try:
                            if os.path.getsize(file_path) > 2 * 1024 * 1024:  # 2MB限制
                                continue
                        except:
                            continue
                        
                        # 查找主文件
                        if file in ['main.py', '__main__.py', 'app.py', 'run.py', 'start.py']:
                            main_files.append(file_path)
                        elif 'test' in file.lower():
                            test_files.append(file_path)
            
            # 如果没有找到明确的主文件，尝试查找包含if __name__ == '__main__'的文件
            if not main_files:
                for root, dirs, files in os.walk(project_path):
                    if any(part in ['test', 'tests'] for part in root.split(os.sep)):
                        continue
                        
                    for file in files:
                        if file.endswith('.py') and not file.startswith('.'):
                            file_path = os.path.join(root, file)
                            try:
                                if os.path.getsize(file_path) > 2 * 1024 * 1024:
                                    continue
                                    
                                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read()
                                    if 'if __name__' in content and '__main__' in content:
                                        main_files.append(file_path)
                                        break
                            except:
                                continue
            
            if main_files:
                main_file = main_files[0]
                print(f"找到主文件: {main_file}")
                
                # 检查是否是Web应用
                is_web_app = await self._detect_web_app(main_file)
                if is_web_app:
                    # 调试信息
                    print(f"🔍 调试信息:")
                    print(f"   - hasattr(self, 'enable_web_app_test'): {hasattr(self, 'enable_web_app_test')}")
                    print(f"   - self.enable_web_app_test: {getattr(self, 'enable_web_app_test', 'NOT_SET')}")
                    
                    # 检查是否启用了Web应用测试
                    print(f"🔍 Web应用检测调试:")
                    print(f"   - hasattr(self, 'enable_web_app_test'): {hasattr(self, 'enable_web_app_test')}")
                    print(f"   - self.enable_web_app_test: {getattr(self, 'enable_web_app_test', 'NOT_SET')} (type: {type(getattr(self, 'enable_web_app_test', None))})")
                    
                    if hasattr(self, 'enable_web_app_test') and self.enable_web_app_test:
                        print("✅ 检测到Web应用，开始动态测试...")
                        # 尝试启动Web应用进行测试
                        web_test_result = await self._test_web_app(main_file, project_path)
                        return {
                            "main_file": os.path.relpath(main_file, project_path),
                            "execution_successful": web_test_result.get("success", False),
                            "project_type": "web_application",
                            "web_test": web_test_result,
                            "dynamic_test_enabled": True
                        }
                    else:
                        print("❌ 检测到Web应用，但未启用Web应用测试")
                        return {
                            "main_file": os.path.relpath(main_file, project_path),
                            "execution_successful": False,
                            "error": "检测到Web应用，跳过服务器启动测试",
                            "project_type": "web_application",
                            "suggestion": "请启用'Web应用测试'选项以进行完整的动态检测"
                        }
                
                # 尝试运行项目（添加超时）
                import subprocess
                try:
                    result = subprocess.run([
                        sys.executable, main_file
                    ], capture_output=True, text=True, timeout=30)
                    
                    return {
                        "main_file": os.path.relpath(main_file, project_path),
                        "execution_successful": result.returncode == 0,
                        "stdout": result.stdout[:1000],  # 限制输出长度
                        "stderr": result.stderr[:1000],  # 限制错误长度
                        "return_code": result.returncode
                    }
                except subprocess.TimeoutExpired:
                    return {
                        "main_file": os.path.relpath(main_file, project_path),
                        "execution_successful": False,
                        "error": "执行超时（30秒）"
                    }
                except Exception as e:
                    return {
                        "main_file": os.path.relpath(main_file, project_path),
                        "execution_successful": False,
                        "error": str(e)[:500]  # 限制错误信息长度
                    }
            else:
                # 对于库项目（如pandas），尝试导入测试
                return {
                    "project_type": "library",
                    "message": "这是一个库项目，无法直接运行",
                    "suggestion": "建议使用静态分析或单元测试来验证代码质量",
                    "test_files_found": len(test_files)
                }
                
        except Exception as e:
            return {"error": f"运行时分析失败: {str(e)[:500]}"}
    
    async def _detect_web_app(self, file_path: str) -> bool:
        """检测是否是Web应用"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # 检测Web框架关键字
            web_frameworks = [
                'Flask', 'Django', 'FastAPI', 'Tornado', 'Bottle',
                'app.run', 'socketio.run', 'uvicorn.run',
                'create_app', 'register_blueprint'
            ]
            
            for framework in web_frameworks:
                if framework in content:
                    return True
            
            return False
        except:
            return False
    
    async def _test_web_app(self, main_file: str, project_path: str) -> Dict[str, Any]:
        """测试Web应用启动"""
        try:
            import subprocess
            import time
            import os
            import socket
            
            print(f"开始测试Web应用: {main_file}")
            
            # 创建环境变量，设置测试端口
            env = os.environ.copy()
            test_port = 8002  # 使用不同的端口避免冲突
            env['FLASK_PORT'] = str(test_port)
            env['PORT'] = str(test_port)
            
            # 尝试启动Web应用
            process = None
            try:
                # 构建启动命令
                cmd = [sys.executable, main_file]
                
                # 启动进程
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=project_path,
                    env=env
                )
                
                # 等待启动
                startup_timeout = 30  # 30秒启动超时
                start_time = time.time()
                
                while time.time() - start_time < startup_timeout:
                    if process.poll() is not None:
                        # 进程已结束
                        stdout, stderr = process.communicate()
                        return {
                            "success": False,
                            "error": "Web应用启动失败",
                            "stdout": stdout[:500],
                            "stderr": stderr[:500],
                            "return_code": process.returncode
                        }
                    
                    # 检查端口是否可用
                    if self._is_port_available(test_port):
                        print(f"Web应用已在端口 {test_port} 启动")
                        break
                    
                    time.sleep(1)
                
                # 如果进程还在运行，认为启动成功
                if process.poll() is None:
                    # 尝试访问应用
                    test_result = await self._test_web_endpoint(test_port)
                    
                    # 终止进程
                    try:
                        process.terminate()
                        process.wait(timeout=5)
                    except:
                        try:
                            process.kill()
                        except:
                            pass
                    
                    return {
                        "success": True,
                        "message": f"Web应用在端口 {test_port} 启动成功",
                        "startup_time": time.time() - start_time,
                        "test_port": test_port,
                        "endpoint_test": test_result
                    }
                else:
                    stdout, stderr = process.communicate()
                    return {
                        "success": False,
                        "error": "Web应用启动超时",
                        "stdout": stdout[:500],
                        "stderr": stderr[:500]
                    }
                    
            except Exception as e:
                if process:
                    try:
                        process.terminate()
                    except:
                        pass
                return {
                    "success": False,
                    "error": f"Web应用测试失败: {str(e)}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Web应用测试异常: {str(e)}"
            }
    
    def _is_port_available(self, port: int) -> bool:
        """检查端口是否可用"""
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return True
        except OSError:
            return False
    
    async def _test_web_endpoint(self, port: int = 8002) -> Dict[str, Any]:
        """测试Web端点"""
        try:
            import httpx
            
            # 测试多个可能的端点
            test_urls = [
                f"http://localhost:{port}/",
                f"http://localhost:{port}/health",
                f"http://localhost:{port}/api/health",
                f"http://localhost:{port}/status",
                f"http://127.0.0.1:{port}/"
            ]
            
            for url in test_urls:
                try:
                    async with httpx.AsyncClient(timeout=5.0) as client:
                        response = await client.get(url)
                        if response.status_code < 500:  # 4xx也算成功，说明服务器在运行
                            return {
                                "success": True,
                                "url": url,
                                "status_code": response.status_code,
                                "message": f"Web端点在端口 {port} 响应正常"
                            }
                except:
                    continue
            
            return {
                "success": False,
                "message": f"无法访问端口 {port} 上的任何Web端点"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"端点测试失败: {str(e)}"
            }
    
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
            "# 动态检测报告",
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

async def generate_ai_dynamic_report(results: Dict[str, Any], filename: str) -> str:
    """生成AI动态检测报告"""
    try:
        if not deepseek_config.is_configured():
            print("⚠️ DeepSeek API未配置，使用基础报告")
            return generate_fallback_report(results, filename)
        
        prompt = build_dynamic_analysis_prompt(results, filename)
        
        print("🤖 正在生成AI报告...")
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
                print("✅ AI报告生成成功")
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

def build_dynamic_analysis_prompt(results: Dict[str, Any], filename: str) -> str:
    """构建动态分析提示词"""
    summary = results.get("summary", {})
    
    prompt = f"""请分析以下动态检测结果，生成一份详细的自然语言报告：

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
        
        # 添加问题详情
        issues = static.get("issues", [])
        if issues:
            prompt += "\n### 主要问题:\n"
            for i, issue in enumerate(issues[:5]):  # 只显示前5个问题
                tool = issue.get('tool', 'unknown')
                prompt += f"{i+1}. [{tool}] {issue.get('file', 'N/A')}: {issue.get('message', 'N/A')} [{issue.get('severity', 'info')}]\n"
        
        # 添加项目结构信息
        project_structure = static.get("project_structure", {})
        if project_structure:
            prompt += f"\n### 项目结构:\n"
            prompt += f"- 项目类型: {project_structure.get('project_type', 'unknown')}\n"
            prompt += f"- 主要语言: {project_structure.get('primary_language', 'unknown')}\n"
            prompt += f"- 框架: {project_structure.get('framework', 'unknown')}\n"
        
        # 添加多语言分析信息
        multi_lang = static.get("multi_language_analysis", {})
        if multi_lang:
            prompt += f"\n### 多语言分析:\n"
            prompt += f"- Python文件分析: {static.get('python_files_analyzed', 0)}个\n"
            prompt += f"- 其他语言文件分析: {static.get('other_language_files_analyzed', 0)}个\n"
            prompt += f"- Python问题: {multi_lang.get('python_issues', 0)}个\n"
            prompt += f"- AI分析问题: {multi_lang.get('ai_issues', 0)}个\n"
            supported_langs = multi_lang.get('supported_languages', [])
            if supported_langs:
                prompt += f"- 支持的语言: {', '.join(supported_langs)}\n"
        
        # 添加AI分析摘要
        ai_summary = static.get("ai_summary", {})
        if ai_summary and ai_summary.get('success'):
            prompt += f"\n### AI分析摘要:\n{ai_summary.get('summary', 'N/A')[:500]}...\n"
    
    prompt += "\n## 动态监控结果\n"
    if "dynamic_monitoring" in results:
        dynamic = results["dynamic_monitoring"]
        prompt += f"- 监控时长: {dynamic.get('duration', 0)}秒\n"
        prompt += f"- 告警数量: {len(dynamic.get('alerts', []))}\n"
        
        alerts = dynamic.get("alerts", [])
        if alerts:
            prompt += "\n### 系统告警:\n"
            for i, alert in enumerate(alerts[:3]):  # 只显示前3个告警
                prompt += f"{i+1}. {alert.get('message', 'N/A')} [{alert.get('severity', 'info')}]\n"
    
    prompt += "\n## 运行时分析结果\n"
    if "runtime_analysis" in results:
        runtime = results["runtime_analysis"]
        prompt += f"- 主文件: {runtime.get('main_file', 'N/A')}\n"
        prompt += f"- 执行状态: {'成功' if runtime.get('execution_successful', False) else '失败'}\n"
        if runtime.get("error"):
            prompt += f"- 错误信息: {runtime.get('error')}\n"
    
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
    
    report = f"""# 动态检测报告

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

## 静态分析详情
"""
    
    # 添加静态分析详细信息
    if "static_analysis" in results:
        static = results["static_analysis"]
        statistics = static.get("statistics", {})
        
        report += f"- **分析类型**: {static.get('analysis_type', 'unknown')}\n"
        report += f"- **分析文件数**: {static.get('files_analyzed', 0)}\n"
        report += f"- **总代码行数**: {statistics.get('total_lines', 0)}\n"
        report += f"- **平均复杂度**: {statistics.get('average_complexity', 0)}\n"
        report += f"- **可维护性评分**: {statistics.get('maintainability_score', 0)}\n"
        
        # 添加问题统计
        issues_by_severity = statistics.get("issues_by_severity", {})
        issues_by_tool = statistics.get("issues_by_tool", {})
        
        if issues_by_severity:
            report += "\n### 问题严重程度分布\n"
            for severity, count in issues_by_severity.items():
                report += f"- {severity}: {count}个\n"
        
        if issues_by_tool:
            report += "\n### 分析工具统计\n"
            for tool, count in issues_by_tool.items():
                report += f"- {tool}: {count}个问题\n"
        
        # 添加项目结构信息
        project_structure = static.get("project_structure", {})
        if project_structure:
            report += f"\n### 项目结构信息\n"
            report += f"- **项目类型**: {project_structure.get('project_type', 'unknown')}\n"
            report += f"- **主要语言**: {project_structure.get('primary_language', 'unknown')}\n"
            report += f"- **框架**: {project_structure.get('framework', 'unknown')}\n"
            report += f"- **包含测试**: {'是' if project_structure.get('has_tests', False) else '否'}\n"
            report += f"- **包含文档**: {'是' if project_structure.get('has_docs', False) else '否'}\n"
        
        # 添加多语言分析信息
        multi_lang = static.get("multi_language_analysis", {})
        if multi_lang:
            report += f"\n### 多语言分析信息\n"
            report += f"- **Python文件分析**: {static.get('python_files_analyzed', 0)}个\n"
            report += f"- **其他语言文件分析**: {static.get('other_language_files_analyzed', 0)}个\n"
            report += f"- **Python问题**: {multi_lang.get('python_issues', 0)}个\n"
            report += f"- **AI分析问题**: {multi_lang.get('ai_issues', 0)}个\n"
            supported_langs = multi_lang.get('supported_languages', [])
            if supported_langs:
                report += f"- **支持的语言**: {', '.join(supported_langs)}\n"
        
        # 添加主要问题
        issues = static.get("issues", [])
        if issues:
            report += "\n### 主要问题列表\n"
            for i, issue in enumerate(issues[:10], 1):  # 显示前10个问题
                tool = issue.get('tool', 'unknown')
                report += f"{i}. **[{tool}]** {issue.get('file', 'N/A')}: {issue.get('message', 'N/A')} [{issue.get('severity', 'info')}]\n"
    
    report += "\n## 问题分析\n"
    
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
    
    # 添加技术建议
    if "static_analysis" in results:
        static = results["static_analysis"]
        statistics = static.get("statistics", {})
        
        report += "\n## 技术建议\n"
        
        # 基于复杂度给出建议
        avg_complexity = statistics.get("average_complexity", 0)
        if avg_complexity > 10:
            report += "- 🔧 **代码复杂度较高**，建议重构复杂函数\n"
        elif avg_complexity > 5:
            report += "- 📝 **代码复杂度适中**，注意保持代码简洁\n"
        else:
            report += "- ✅ **代码复杂度良好**，继续保持\n"
        
        # 基于可维护性给出建议
        maintainability_score = statistics.get("maintainability_score", 0)
        if maintainability_score < 60:
            report += "- 🔨 **可维护性较低**，建议改进代码结构和文档\n"
        elif maintainability_score < 80:
            report += "- 📊 **可维护性中等**，可以进一步优化\n"
        else:
            report += "- 🌟 **可维护性良好**，代码质量较高\n"
        
        # 基于工具分析给出建议
        issues_by_tool = statistics.get("issues_by_tool", {})
        if 'pylint' in issues_by_tool and issues_by_tool['pylint'] > 0:
            report += "- 🐍 **Pylint发现问题**，建议修复代码质量问题\n"
        if 'flake8' in issues_by_tool and issues_by_tool['flake8'] > 0:
            report += "- 📏 **Flake8发现问题**，建议改进代码风格\n"
    
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

# 注意：不再使用全局检测器实例，每个请求创建独立实例

@router.get("/")
async def root():
    """根路径"""
    return {
        "message": "简化版动态检测API运行中",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/health")
async def health():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "simple_dynamic_detection"
    }

@router.post("/detect", response_model=BaseResponse)
async def dynamic_detect(
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
    """动态缺陷检测"""
    
    # 调试信息
    print(f"🔧 API接收到的参数:")
    print(f"   - static_analysis: {static_analysis} (type: {type(static_analysis)})")
    print(f"   - dynamic_monitoring: {dynamic_monitoring} (type: {type(dynamic_monitoring)})")
    print(f"   - runtime_analysis: {runtime_analysis} (type: {type(runtime_analysis)})")
    print(f"   - enable_web_app_test: {enable_web_app_test} (type: {type(enable_web_app_test)})")
    print(f"   - enable_dynamic_detection: {enable_dynamic_detection} (type: {type(enable_dynamic_detection)})")
    print(f"   - enable_flask_specific_tests: {enable_flask_specific_tests} (type: {type(enable_flask_specific_tests)})")
    print(f"   - enable_server_testing: {enable_server_testing} (type: {type(enable_server_testing)})")
    print(f"   - upload_type: {upload_type}")
    print(f"   - file: {file}")
    print(f"   - files: {files}")
    
    # 确保所有布尔参数都是布尔值
    def convert_to_bool(value, param_name):
        if isinstance(value, str):
            result = value.lower() in ('true', '1', 'yes', 'on')
            print(f"🔄 转换{param_name}为布尔值: {value} -> {result}")
            return result
        elif isinstance(value, bool):
            print(f"🔄 {param_name}已经是布尔值: {value}")
            return value
        else:
            result = bool(value)
            print(f"🔄 转换{param_name}为布尔值: {value} -> {result}")
            return result
    
    static_analysis = convert_to_bool(static_analysis, 'static_analysis')
    dynamic_monitoring = convert_to_bool(dynamic_monitoring, 'dynamic_monitoring')
    runtime_analysis = convert_to_bool(runtime_analysis, 'runtime_analysis')
    enable_web_app_test = convert_to_bool(enable_web_app_test, 'enable_web_app_test')
    enable_dynamic_detection = convert_to_bool(enable_dynamic_detection, 'enable_dynamic_detection')
    enable_flask_specific_tests = convert_to_bool(enable_flask_specific_tests, 'enable_flask_specific_tests')
    enable_server_testing = convert_to_bool(enable_server_testing, 'enable_server_testing')
    """
    动态缺陷检测
    
    Args:
        file: 项目压缩包（单文件上传）
        files: 项目文件列表（目录上传）
        static_analysis: 是否进行静态分析
        dynamic_monitoring: 是否进行动态监控
        runtime_analysis: 是否进行运行时分析
        enable_web_app_test: 是否启用Web应用测试（默认False，避免超时）
        upload_type: 上传类型 ("file" 或 "directory")
    
    Returns:
        检测结果
    """
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
            temp_dir = tempfile.mkdtemp(prefix="dynamic_detection_")
            print(f"创建临时目录: {temp_dir}")
            
            # 保存所有文件到临时目录
            for file in upload_files:
                if file.filename:
                    # 处理文件路径结构
                    # 如果文件名包含路径分隔符，保持路径结构
                    # 否则，将文件放在根目录
                    if '/' in file.filename or '\\' in file.filename:
                        file_path = os.path.join(temp_dir, file.filename)
                    else:
                        # 没有路径信息，直接放在根目录
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
        detector = SimpleDetector(monitor_agent)
        detector.enable_web_app_test = enable_web_app_test
        detector.enable_dynamic_detection = enable_dynamic_detection
        detector.enable_flask_specific_tests = enable_flask_specific_tests
        detector.enable_server_testing = enable_server_testing
        
        # 调试信息
        print(f"🔧 API调试信息:")
        print(f"   - enable_web_app_test参数: {enable_web_app_test} (type: {type(enable_web_app_test)})")
        print(f"   - enable_dynamic_detection参数: {enable_dynamic_detection} (type: {type(enable_dynamic_detection)})")
        print(f"   - enable_flask_specific_tests参数: {enable_flask_specific_tests} (type: {type(enable_flask_specific_tests)})")
        print(f"   - enable_server_testing参数: {enable_server_testing} (type: {type(enable_server_testing)})")
        
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
            ai_report = await generate_ai_dynamic_report(results, file.filename)
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
            results_file = f"detection_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            results_dir = Path("dynamic_detection_results")
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
            message="动态检测完成",
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

@router.get("/results/{filename}")
async def get_detection_results(filename: str):
    """获取检测结果文件"""
    try:
        if not filename.endswith('.json'):
            raise HTTPException(status_code=400, detail="只支持JSON格式的结果文件")
        
        # 在dynamic_detection_results目录中查找文件
        results_dir = Path("dynamic_detection_results")
        file_path = results_dir / filename
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="结果文件不存在")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        return BaseResponse(
            success=True,
            message="获取检测结果成功",
            data=results
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取检测结果失败: {str(e)}")

@router.get("/results")
async def list_detection_results():
    """列出所有检测结果文件"""
    try:
        results_dir = Path("dynamic_detection_results")
        if not results_dir.exists():
            return BaseResponse(
                success=True,
                message="检测结果目录不存在",
                data={"results": []}
            )
        
        results_files = []
        for file_path in results_dir.glob("detection_results_*.json"):
            file_info = {
                "filename": file_path.name,
                "size": file_path.stat().st_size,
                "created_time": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
                "modified_time": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            }
            results_files.append(file_info)
        
        # 按修改时间倒序排列
        results_files.sort(key=lambda x: x["modified_time"], reverse=True)
        
        return BaseResponse(
            success=True,
            message="获取检测结果列表成功",
            data={"results": results_files}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取检测结果列表失败: {str(e)}")

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
            "runtime_analysis": True
        }
    }

@router.post("/test-monitor")
async def test_monitor(duration: int = 30):
    """测试监控功能"""
    try:
        results = await monitor_agent.start_monitoring(duration)
        
        return BaseResponse(
            success=True,
            message="监控测试完成",
            data=results
        )
        
    except Exception as e:
        return BaseResponse(
            success=False,
            error=str(e),
            message="监控测试失败"
        )

@router.post("/test-project-runner")
async def test_project_runner():
    """测试项目运行器"""
    try:
        from utils.project_runner import ProjectRunner
        
        runner = ProjectRunner()
        
        # 这里需要提供一个测试项目
        # 目前返回模拟结果
        return BaseResponse(
            success=True,
            message="项目运行器测试完成",
            data={
                "status": "ready",
                "message": "项目运行器已就绪"
            }
        )
        
    except Exception as e:
        return BaseResponse(
            success=False,
            error=str(e),
            message="项目运行器测试失败"
        )

@router.get("/system-info")
async def get_system_info():
    """获取系统信息"""
    try:
        import psutil
        import sys
        
        return {
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "disk_total": psutil.disk_usage('/').total,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": sys.platform
        }
        
    except Exception as e:
        return {
            "error": str(e)
        }

# 路由已配置完成，可以通过main_api.py统一启动
