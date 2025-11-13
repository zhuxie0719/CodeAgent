"""
静态缺陷检测AGENT
负责主动发现代码中的潜在缺陷和问题
集成静态代码检测功能，支持多语言分析
"""

import asyncio
import logging
import json
import os
import mimetypes
import zipfile
import tarfile
import shutil
import tempfile
import subprocess
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime
from pathlib import Path
import sys

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from ..base_agent import BaseAgent, TaskStatus
from tools.static_analysis.pylint_tool import PylintTool
from tools.static_analysis.bandit_tool import BanditTool
from tools.static_analysis.mypy_tool import MypyTool
from tools.static_analysis.semgrep_tool import SemgrepTool
from tools.static_analysis.ruff_tool import RuffTool

# 简化的设置类
class Settings:
    AGENTS = {"bug_detection_agent": {"enabled": True}}
    TOOLS = {
        "pylint": {"enabled": True, "pylint_args": ["--disable=C0114"]},
        "bandit": {"enabled": True},
        "mypy": {"enabled": True}
    }

settings = Settings()


class BugDetectionAgent(BaseAgent):
    """静态缺陷检测AGENT - 支持多语言和大型项目分析"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("bug_detection_agent", config)
        self.pylint_tool = None
        self.bandit_tool = None
        self.mypy_tool = None
        self.semgrep_tool = None
        self.ruff_tool = None
        self.ai_analyzer = None
        self.detection_rules = {}
        self.tasks = {}  # 任务管理
        self.tasks_file = Path("api/tasks_state.json")  # 任务状态持久化文件
        self._tools_initialized = False  # 标记工具是否已初始化
        
        # Docker支持配置
        self.use_docker = config.get("use_docker", False)  # 默认不启用Docker
        self.docker_runner = None
        if self.use_docker:
            try:
                import sys
                sys.path.append(str(Path(__file__).parent.parent.parent))
                from utils.docker_runner import get_docker_runner
                import subprocess
                
                # 首先检查Docker是否可用
                try:
                    docker_check = subprocess.run(
                        ["docker", "info"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if docker_check.returncode != 0:
                        raise Exception("Docker服务未运行或不可用")
                except FileNotFoundError:
                    raise Exception("Docker未安装或不在PATH中")
                except subprocess.TimeoutExpired:
                    raise Exception("Docker服务响应超时")
                
                # 初始化Docker运行器
                self.docker_runner = get_docker_runner()
                print("✅ Docker支持已启用 - BugDetectionAgent")
                self.logger.info("Docker支持已启用")
            except Exception as e:
                print(f"⚠️  无法初始化Docker运行器: {e}，将回退到虚拟环境")
                self.logger.warning(f"无法初始化Docker运行器: {e}，将回退到虚拟环境")
                self.use_docker = False
                self.docker_runner = None
        
        # 缺陷严重性级别
        self.severity_levels = {
            "error": {"level": 1, "name": "错误", "color": "#ff4444"},
            "warning": {"level": 2, "name": "警告", "color": "#ff8800"},
            "info": {"level": 3, "name": "信息", "color": "#4488ff"},
            "hint": {"level": 4, "name": "提示", "color": "#888888"}
        }
        
        # 支持的语言和文件扩展名
        self.supported_languages = {
            "python": {
                "extensions": [".py", ".pyw", ".pyi"],
                "tools": ["pylint", "ruff", "mypy", "semgrep", "static_detector"],
                "ai_analysis": True
            },
            "java": {
                "extensions": [".java"],
                "tools": ["spotbugs", "pmd", "checkstyle"],
                "ai_analysis": True
            },
            "c": {
                "extensions": [".c", ".h"],
                "tools": ["cppcheck", "clang-static-analyzer"],
                "ai_analysis": True
            },
            "cpp": {
                "extensions": [".cpp", ".cc", ".cxx", ".hpp", ".hxx"],
                "tools": ["cppcheck", "clang-static-analyzer"],
                "ai_analysis": True
            },
            "javascript": {
                "extensions": [".js", ".jsx", ".ts", ".tsx"],
                "tools": ["eslint", "jshint"],
                "ai_analysis": True
            },
            "go": {
                "extensions": [".go"],
                "tools": ["golangci-lint", "go vet"],
                "ai_analysis": True
            }
        }
        
        # 项目分析配置
        self.project_config = {
            "max_file_size": 2 * 1024 * 1024,  # 2MB - 减少单个文件大小限制
            "max_files_per_project": 200,  # 减少最大文件数
            "max_project_size": 50 * 1024 * 1024,  # 50MB - 减少项目大小限制
            "parallel_analysis": True,
            "max_workers": 2,  # 减少并发数
            "skip_dirs": [".git", "__pycache__", "node_modules", ".venv", "venv", "doc", "docs", "tests", ".github", "ci", "asv_bench", "conda.recipe", "web", "LICENSES"],
            "skip_files": ["*.pyc", "*.pyo", "*.pyd", "*.so", "*.dll", "*.rst", "*.md", "*.txt", "*.yml", "*.yaml", "*.json", "*.xml", "*.bat", "*.sh"],
            "timeout": 120,  # 2分钟超时
            "sample_ratio": 0.2  # 只分析20%的文件
        }
    
    async def initialize(self) -> bool:
        """初始化缺陷检测AGENT"""
        try:
            self.logger.info("初始化缺陷检测AGENT...")
            
            # 加载任务状态
            self._load_tasks_state()
            
            # 初始化检测工具
            await self._initialize_detection_tools()
            
            # 加载检测规则
            await self._load_detection_rules()
            
            self.logger.info("缺陷检测AGENT初始化完成")
            self._tools_initialized = True  # 标记工具已初始化
            return True
            
        except Exception as e:
            self.logger.error(f"缺陷检测AGENT初始化失败: {e}")
            import traceback
            self.logger.error(f"初始化错误详情: {traceback.format_exc()}")
            self._tools_initialized = False
            return False
    
    async def start(self):
        """启动AGENT"""
        await self.initialize()
        self.logger.info("BugDetectionAgent 启动成功")
    
    async def stop(self):
        """停止AGENT"""
        self.logger.info("BugDetectionAgent 已停止")
    
    def get_status(self):
        """获取AGENT状态"""
        return {"status": "running"}
    
    async def process_task(self, task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理缺陷检测任务"""
        try:
            self.logger.info(f"开始处理缺陷检测任务: {task_id}")
            
            # 获取任务参数
            file_path = task_data.get("file_path")
            project_path = task_data.get("project_path")
            analysis_type = task_data.get("analysis_type", "file")
            options = task_data.get("options", {})
            
            if not file_path and not project_path:
                raise ValueError("缺少文件路径或项目路径")
            
            # 执行缺陷检测
            # 如果提供了 file_path 且是 zip/tar 文件，需要先解压
            # 如果提供了 project_path（已解压的目录），直接使用
            if analysis_type == "project":
                if file_path and os.path.isfile(file_path) and any(file_path.endswith(ext) for ext in ['.zip', '.tar', '.tar.gz']):
                    # file_path 是压缩文件，需要解压
                    self.logger.info(f"检测到压缩文件，开始解压: {file_path}")
                    project_path = await self.extract_project(file_path)
                elif not project_path:
                    # 只有 file_path 但不是压缩文件，当作项目路径使用
                    project_path = file_path
                
                # 现在 project_path 应该是已解压的目录
                if not project_path or not os.path.exists(project_path):
                    raise ValueError(f"项目路径无效: {project_path}")
                
                self.logger.info(f"开始分析项目: {project_path}")
                project_result = await self.analyze_project(project_path, options)
                if project_result.get("success"):
                    detection_results = project_result.get("detection_results", {})
                else:
                    detection_results = {
                        "project_path": project_path,
                        "total_issues": 0,
                        "issues": [],
                        "error": project_result.get("error", "项目分析失败"),
                        "summary": {"error_count": 0, "warning_count": 0, "info_count": 0}
                    }
            elif file_path:
                # 单文件分析
                detection_results = await self._detect_file_bugs(file_path, options)
            else:
                detection_results = await self._detect_project_bugs(project_path, options)
            
            # 生成检测报告
            report = await self._generate_report(detection_results)
            
            self.logger.info(f"缺陷检测任务完成: {task_id}")
            result = {
                "success": True,
                "task_id": task_id,
                "detection_results": detection_results,
                "report": report,
                "timestamp": datetime.now().isoformat()
            }
            
            # 在返回结果前，先记录需要清理的信息（但不阻塞返回）
            cleanup_needed = False
            cleanup_path = None
            if analysis_type == "project" and 'project_path' in locals() and project_path:
                if "temp_extract" in str(project_path) and os.path.exists(project_path):
                    if file_path and os.path.isfile(file_path):
                        cleanup_needed = True
                        cleanup_path = project_path
            
            # 立即返回结果，让Coordinator能够快速收到完成通知
            # 清理操作在后台异步执行，不阻塞任务完成通知
            if cleanup_needed:
                # 在后台任务中执行清理，不阻塞主流程
                import asyncio
                asyncio.create_task(self._cleanup_project_environment_async(cleanup_path))
            
            # 添加日志，确保任务完成状态已更新
            self.logger.info(f"✅ 任务结果已准备，即将返回: {task_id}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"处理缺陷检测任务失败: {e}")
            return {
                "success": False,
                "task_id": task_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def submit_task(self, task_id: str, task_data: Dict[str, Any]) -> str:
        """提交任务"""
        try:
            # 存储任务信息
            self.tasks[task_id] = {
                "task_id": task_id,
                "status": "running",
                "created_at": datetime.now().isoformat(),
                "started_at": datetime.now().isoformat(),
                "result": None,
                "error": None
            }
            
            # 保存任务状态
            self._save_tasks_state()
            
            # 异步处理任务
            asyncio.create_task(self._process_task_async(task_id, task_data))
            
            return task_id
            
        except Exception as e:
            self.logger.error(f"提交任务失败: {e}")
            raise
    
    async def _process_task_async(self, task_id: str, task_data: Dict[str, Any]):
        """异步处理任务"""
        try:
            result = await self.process_task(task_id, task_data)
            
            # 更新任务状态
            self.tasks[task_id].update({
                "status": "completed",
                "completed_at": datetime.now().isoformat(),
                "result": result
            })
            
            # 保存任务状态
            self._save_tasks_state()
            
        except Exception as e:
            # 更新任务状态为失败
            self.tasks[task_id].update({
                "status": "failed",
                "completed_at": datetime.now().isoformat(),
                "error": str(e)
            })
            
            # 保存任务状态
            self._save_tasks_state()
    
    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """获取任务状态"""
        task = self.tasks.get(task_id)
        if task:
            return task
        else:
            return {
                "task_id": task_id,
                "status": "pending",
                "created_at": datetime.now().isoformat(),
                "started_at": None,
                "completed_at": None,
                "result": None,
                "error": None
            }
    
    def get_capabilities(self) -> List[str]:
        """获取AGENT能力列表"""
        return [
            "static_analysis",
            "bug_detection", 
            "code_quality_check",
            "security_scan",
            "file_analysis",
            "project_analysis"
        ]
    
    async def _initialize_detection_tools(self):
        """初始化检测工具"""
        try:
            self.logger.info(f"开始初始化检测工具，配置: {settings.TOOLS}")
            
            # 初始化Pylint工具
            if settings.TOOLS.get("pylint", {}).get("enabled", True):
                try:
                    self.logger.info("正在初始化Pylint工具...")
                    self.pylint_tool = PylintTool(settings.TOOLS["pylint"])
                    self.logger.info("✅ Pylint工具初始化成功")
                except Exception as e:
                    self.logger.error(f"❌ Pylint工具初始化失败: {e}")
                    import traceback
                    self.logger.error(f"Pylint错误详情: {traceback.format_exc()}")
            
            # 初始化Bandit工具
            if settings.TOOLS.get("bandit", {}).get("enabled", True):
                try:
                    self.logger.info("正在初始化Bandit工具...")
                    self.bandit_tool = BanditTool(settings.TOOLS["bandit"])
                    self.logger.info("✅ Bandit工具初始化成功")
                except Exception as e:
                    self.logger.error(f"❌ Bandit工具初始化失败: {e}")
                    import traceback
                    self.logger.error(f"Bandit错误详情: {traceback.format_exc()}")
            
            # 初始化Mypy工具（增强严格模式）
            if settings.TOOLS.get("mypy", {}).get("enabled", True):
                try:
                    self.logger.info("正在初始化Mypy工具（严格模式）...")
                    # 确保启用严格模式
                    mypy_config = settings.TOOLS.get("mypy", {})
                    mypy_config.setdefault("strict_mode", True)
                    self.mypy_tool = MypyTool(mypy_config)
                    self.logger.info("✅ Mypy工具初始化成功（严格模式已启用）")
                except Exception as e:
                    self.logger.error(f"❌ Mypy工具初始化失败: {e}")
                    import traceback
                    self.logger.error(f"Mypy错误详情: {traceback.format_exc()}")
            
            # 初始化Semgrep工具（方案B必需）- 添加超时保护
            if settings.TOOLS.get("semgrep", {}).get("enabled", True):
                try:
                    self.logger.info("正在初始化Semgrep工具...")
                    # 在后台线程中初始化，避免阻塞
                    import concurrent.futures
                    loop = asyncio.get_event_loop()
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(SemgrepTool, settings.TOOLS.get("semgrep", {}))
                        try:
                            self.semgrep_tool = await asyncio.wait_for(
                                loop.run_in_executor(None, lambda: future.result()),
                                timeout=10.0  # 10秒超时
                            )
                            self.logger.info("✅ Semgrep工具初始化成功")
                        except asyncio.TimeoutError:
                            self.logger.warning("⚠️ Semgrep工具初始化超时，跳过")
                            self.semgrep_tool = None
                except Exception as e:
                    self.logger.warning(f"⚠️ Semgrep工具初始化失败（可能未安装）: {e}")
                    self.semgrep_tool = None
            
            # 初始化Ruff工具（方案B推荐，替代flake8，更快且功能更强）
            if settings.TOOLS.get("ruff", {}).get("enabled", True):
                try:
                    self.logger.info("正在初始化Ruff工具...")
                    self.ruff_tool = RuffTool(settings.TOOLS.get("ruff", {}))
                    self.logger.info("✅ Ruff工具初始化成功")
                except Exception as e:
                    self.logger.warning(f"⚠️ Ruff工具初始化失败（可能未安装）: {e}")
                    self.ruff_tool = None
            
            # 初始化AI多语言分析器
            try:
                from tools.ai_static_analyzer import AIMultiLanguageAnalyzer
                self.ai_analyzer = AIMultiLanguageAnalyzer()
                self.logger.info("✅ AI多语言分析器初始化成功")
            except Exception as e:
                self.logger.warning(f"⚠️ AI多语言分析器初始化失败: {e}")
                self.ai_analyzer = None
            
            # 输出工具初始化状态
            tools_status = []
            if self.pylint_tool:
                tools_status.append("pylint")
            if self.bandit_tool:
                tools_status.append("bandit")
            if self.mypy_tool:
                tools_status.append("mypy(strict)")
            if self.semgrep_tool:
                tools_status.append("semgrep")
            if self.ruff_tool:
                tools_status.append("ruff")
            if self.ai_analyzer:
                tools_status.append("ai_analyzer")
            
            self.logger.info(f"检测工具初始化完成（方案B标准配置），可用工具: {', '.join(tools_status) if tools_status else '无'}")
            
        except Exception as e:
            self.logger.error(f"初始化检测工具失败: {e}")
            import traceback
            self.logger.error(f"工具初始化错误详情: {traceback.format_exc()}")
            # 不抛出异常，允许在没有工具的情况下继续运行
    
    async def _load_detection_rules(self):
        """加载检测规则"""
        try:
            # 初始化默认检测规则
            self.detection_rules = {
                "unused_imports": True,
                "hardcoded_secrets": True,
                "unsafe_eval": True,
                "missing_type_hints": True,
                "long_functions": True,
                "duplicate_code": True,
                "bad_exception_handling": True,
                "global_variables": True,
                "magic_numbers": True,
                "unsafe_file_operations": True,
                "missing_docstrings": True,
                "bad_naming": True,
                "unhandled_exceptions": True,
                "deep_nesting": True,
                "insecure_random": True,
                "memory_leaks": True,
                "missing_input_validation": True,
                "bad_formatting": True,
                "dead_code": True,
                "unused_variables": True
            }
            
            self.logger.info(f"加载了 {len(self.detection_rules)} 个检测规则")
            
        except Exception as e:
            self.logger.error(f"加载检测规则失败: {e}")
            # 不抛出异常，使用默认规则
    
    async def _analyze_file_content(self, file_path: str, content: str, language: str, options: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分析文件内容，检测缺陷"""
        issues = []
        lines = content.split('\n')
        filename = Path(file_path).name
        
        if language == "python":
            issues.extend(await self._analyze_python_content(file_path, content, lines, filename, options))
        elif language == "java":
            issues.extend(await self._analyze_java_content(file_path, content, lines, filename, options))
        elif language in ["c", "cpp"]:
            issues.extend(await self._analyze_c_content(file_path, content, lines, filename, options))
        elif language == "javascript":
            issues.extend(await self._analyze_javascript_content(file_path, content, lines, filename, options))
        elif language == "go":
            issues.extend(await self._analyze_go_content(file_path, content, lines, filename, options))
        else:
            issues.extend(await self._analyze_generic_content(file_path, content, lines, filename, options))
        
        return issues
    
    async def _analyze_python_content(self, file_path: str, content: str, lines: List[str], filename: str, options: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分析Python文件内容"""
        issues = []
        
        # 检测未使用的导入
        if options.get("enable_static", True):
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if line.startswith('import ') or line.startswith('from '):
                    # 检测可能未使用的导入
                    if 'import' in line:
                        import_name = line.split('import')[-1].strip().split('.')[0].split(',')[0].strip()
                    else:
                        import_name = line.split('from')[-1].strip().split('.')[0].strip()
                    
                    # 检查导入是否在代码中使用
                    content_without_import = content.replace(line, '')
                    if import_name and import_name not in content_without_import:
                        issues.append({
                            "type": "unused_import",
                            "severity": "warning",
                            "message": f"可能未使用的导入: {import_name}",
                            "line": i,
                            "file": filename,
                            "language": "python"
                        })
        
        # 强制检测一些明显的问题
        for i, line in enumerate(lines, 1):
            # 检测硬编码密钥
            if 'API_KEY' in line or 'SECRET' in line or 'PASSWORD' in line:
                issues.append({
                    "type": "hardcoded_secrets",
                    "severity": "error",
                    "message": "发现硬编码的密钥或密码",
                    "line": i,
                    "file": filename,
                    "language": "python"
                })
            
            # 检测不安全的eval使用
            if 'eval(' in line:
                issues.append({
                    "type": "unsafe_eval",
                    "severity": "error",
                    "message": "不安全的eval使用",
                    "line": i,
                    "file": filename,
                    "language": "python"
                })
            
            # 检测除零风险
            if '/' in line and ('/' in line.split('=')[-1] if '=' in line else True):
                if 'if' not in line and 'for' not in line and 'while' not in line:
                    issues.append({
                        "type": "division_by_zero_risk",
                        "severity": "warning",
                        "message": "可能存在除零风险",
                        "line": i,
                        "file": filename,
                        "language": "python"
                    })
            
            # 检测未处理的异常
            if 'open(' in line and 'with' not in line:
                issues.append({
                    "type": "unhandled_exception",
                    "severity": "warning",
                    "message": "文件操作未使用with语句，可能导致资源泄漏",
                    "line": i,
                    "file": filename,
                    "language": "python"
                })
            
            # 检测JSON解析未处理异常
            if 'json.loads(' in line and 'try' not in content[max(0, i-10):i]:
                issues.append({
                    "type": "unhandled_exception",
                    "severity": "warning",
                    "message": "JSON解析未处理异常",
                    "line": i,
                    "file": filename,
                    "language": "python"
                })
            
            # 检测类型转换未处理异常
            if 'int(' in line and 'try' not in content[max(0, i-10):i]:
                issues.append({
                    "type": "unhandled_exception",
                    "severity": "warning",
                    "message": "类型转换未处理异常",
                    "line": i,
                    "file": filename,
                    "language": "python"
                })
            
            # 检测空列表处理
            if 'sum(' in line and 'if' not in line and 'len(' in line:
                issues.append({
                    "type": "empty_list_handling",
                    "severity": "warning",
                    "message": "未处理空列表情况",
                    "line": i,
                    "file": filename,
                    "language": "python"
                })
            
            # 检测参数验证缺失
            if 'def ' in line and ':' in line and 'if' not in line:
                func_name = line.split('def ')[1].split('(')[0].strip()
                if func_name not in ['__init__', '__str__', '__repr__']:
                    issues.append({
                        "type": "missing_parameter_validation",
                        "severity": "info",
                        "message": f"函数 {func_name} 缺少参数验证",
                        "line": i,
                        "file": filename,
                        "language": "python"
                    })
            
            # 检测不安全的exec使用
            if 'exec(' in line:
                issues.append({
                    "type": "unsafe_exec",
                    "severity": "error",
                    "message": "不安全的exec使用",
                    "line": i,
                    "file": filename,
                    "language": "python"
                })
            
            # 检测全局变量使用
            if 'global ' in line:
                issues.append({
                    "type": "global_variables",
                    "severity": "warning",
                    "message": "使用全局变量",
                    "line": i,
                    "file": filename,
                    "language": "python"
                })
            
            # 检测裸露的except
            if line.strip() == 'except:':
                issues.append({
                    "type": "bare_except",
                    "severity": "warning",
                    "message": "裸露的except语句",
                    "line": i,
                    "file": filename,
                    "language": "python"
                })
        
        # 检测硬编码密钥
        secret_patterns = ['API_KEY', 'SECRET', 'PASSWORD', 'TOKEN', 'PRIVATE_KEY', 'DATABASE_URL']
        for pattern in secret_patterns:
            if pattern in content:
                for i, line in enumerate(lines, 1):
                    if '=' in line and pattern in line:
                        issues.append({
                            "type": "hardcoded_secrets",
                            "severity": "error",
                            "message": f"发现硬编码的{pattern}",
                            "line": i,
                            "file": filename,
                            "language": "python"
                        })
        
        # 检测不安全的eval使用
        if 'eval(' in content:
            for i, line in enumerate(lines, 1):
                if 'eval(' in line:
                    issues.append({
                        "type": "unsafe_eval",
                        "severity": "error",
                        "message": "不安全的eval使用",
                        "line": i,
                        "file": filename,
                        "language": "python"
                    })
        
        # 检测exec使用
        if 'exec(' in content:
            for i, line in enumerate(lines, 1):
                if 'exec(' in line:
                    issues.append({
                        "type": "unsafe_exec",
                        "severity": "error",
                        "message": "不安全的exec使用",
                        "line": i,
                        "file": filename,
                        "language": "python"
                    })
        
        # 检测缺少文档字符串的函数
        in_function = False
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('def ') and not in_function:
                in_function = True
                # 检查下一行是否有文档字符串
                if i < len(lines) and not lines[i].strip().startswith('"""') and not lines[i].strip().startswith("'''"):
                    issues.append({
                        "type": "missing_docstring",
                        "severity": "info",
                        "message": "函数缺少文档字符串",
                        "line": i,
                        "file": filename,
                        "language": "python"
                    })
            elif line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                in_function = False
        
        # 检测过长的函数
        function_lines = 0
        in_function = False
        function_start = 0
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('def '):
                if in_function and function_lines > 50:  # 函数超过50行
                    issues.append({
                        "type": "long_function",
                        "severity": "warning",
                        "message": f"函数过长 ({function_lines} 行)",
                        "line": function_start,
                        "file": filename,
                        "language": "python"
                    })
                in_function = True
                function_start = i
                function_lines = 0
            elif in_function:
                if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                    in_function = False
                    if function_lines > 50:
                        issues.append({
                            "type": "long_function",
                            "severity": "warning",
                            "message": f"函数过长 ({function_lines} 行)",
                            "line": function_start,
                            "file": filename,
                            "language": "python"
                        })
                else:
                    function_lines += 1
        
        # 检测魔法数字
        for i, line in enumerate(lines, 1):
            # 检测硬编码的数字（排除0, 1, -1等常见数字）
            import re
            numbers = re.findall(r'\b\d{2,}\b', line)
            for num in numbers:
                if int(num) not in [0, 1, -1, 2, 10, 100, 1000]:  # 排除常见数字
                    issues.append({
                        "type": "magic_number",
                        "severity": "info",
                        "message": f"魔法数字: {num}",
                        "line": i,
                        "file": filename,
                        "language": "python"
                    })
        
        # 检测全局变量使用
        for i, line in enumerate(lines, 1):
            if 'global ' in line:
                issues.append({
                    "type": "global_variables",
                    "severity": "warning",
                    "message": "使用全局变量",
                    "line": i,
                    "file": filename,
                    "language": "python"
                })
        
        # 检测裸露的except
        for i, line in enumerate(lines, 1):
            if line.strip() == 'except:':
                issues.append({
                    "type": "bare_except",
                    "severity": "warning",
                    "message": "裸露的except语句",
                    "line": i,
                    "file": filename,
                    "language": "python"
                })
        
        # 检测除零错误
        for i, line in enumerate(lines, 1):
            if '/' in line and 'len(' in line:
                issues.append({
                    "type": "potential_division_by_zero",
                    "severity": "warning",
                    "message": "可能存在除零错误",
                    "line": i,
                    "file": filename,
                    "language": "python"
                })
        
        # 检测未处理的异常
        for i, line in enumerate(lines, 1):
            if 'open(' in line and 'try:' not in content:
                issues.append({
                    "type": "unhandled_exception",
                    "severity": "warning",
                    "message": "文件操作未处理异常",
                    "line": i,
                    "file": filename,
                    "language": "python"
                })
        
        # 检测类型转换未处理异常
        for i, line in enumerate(lines, 1):
            if 'int(' in line and 'try:' not in content:
                issues.append({
                    "type": "unhandled_type_conversion",
                    "severity": "warning",
                    "message": "类型转换未处理异常",
                    "line": i,
                    "file": filename,
                    "language": "python"
                })
        
        # 检测JSON解析未处理异常
        for i, line in enumerate(lines, 1):
            if 'json.loads(' in line and 'try:' not in content:
                issues.append({
                    "type": "unhandled_json_parse",
                    "severity": "warning",
                    "message": "JSON解析未处理异常",
                    "line": i,
                    "file": filename,
                    "language": "python"
                })
        
        # 检测空列表处理
        for i, line in enumerate(lines, 1):
            if 'sum(' in line and 'if' not in line:
                issues.append({
                    "type": "empty_list_handling",
                    "severity": "warning",
                    "message": "未处理空列表情况",
                    "line": i,
                    "file": filename,
                    "language": "python"
                })
        
        # 检测参数验证
        function_defs = []
        for i, line in enumerate(lines, 1):
            if 'def ' in line:
                function_defs.append(i)
        
        # 如果函数定义存在但没有参数验证
        if function_defs and 'if' not in content:
            for line_num in function_defs:
                issues.append({
                    "type": "missing_parameter_validation",
                    "severity": "info",
                    "message": "缺少参数验证",
                    "line": line_num,
                    "file": filename,
                    "language": "python"
                })
        
        # 检测函数参数过多
        for i, line in enumerate(lines, 1):
            if 'def ' in line and '(' in line and ')' in line:
                # 计算参数数量
                params_part = line.split('(')[1].split(')')[0]
                if params_part.strip():
                    param_count = len([p.strip() for p in params_part.split(',') if p.strip()])
                    if param_count > 5:  # 超过5个参数
                        issues.append({
                            "type": "too_many_parameters",
                            "severity": "warning",
                            "message": f"函数参数过多 ({param_count} 个)",
                            "line": i,
                            "file": filename,
                            "language": "python"
                        })
        
        # 检测长函数
        function_start = None
        function_line_count = 0
        for i, line in enumerate(lines, 1):
            if line.strip().startswith('def '):
                if function_start and function_line_count > 20:  # 函数超过20行
                    issues.append({
                        "type": "long_function",
                        "severity": "warning",
                        "message": f"函数过长 ({function_line_count} 行)",
                        "line": function_start,
                        "file": filename,
                        "language": "python"
                    })
                function_start = i
                function_line_count = 0
            elif function_start is not None:
                if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                    # 函数结束
                    if function_line_count > 20:
                        issues.append({
                            "type": "long_function",
                            "severity": "warning",
                            "message": f"函数过长 ({function_line_count} 行)",
                            "line": function_start,
                            "file": filename,
                            "language": "python"
                        })
                    function_start = None
                    function_line_count = 0
                else:
                    function_line_count += 1
        
        # 检测语法错误
        try:
            compile(content, file_path, 'exec')
        except SyntaxError as e:
            issues.append({
                "type": "syntax_error",
                "severity": "error",
                "message": f"语法错误: {e.msg}",
                "line": e.lineno or 1,
                "file": filename,
                "language": "python"
            })
        
        return issues
    
    async def _analyze_java_content(self, file_path: str, content: str, lines: List[str], filename: str, options: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分析Java文件内容"""
        issues = []
        
        # 检测空指针解引用
        if 'null' in content and ('==' in content or '!=' in content):
            for i, line in enumerate(lines, 1):
                if 'null' in line and ('==' in line or '!=' in line):
                    issues.append({
                        "type": "null_pointer_dereference",
                        "severity": "error",
                        "message": "潜在的空指针解引用",
                        "line": i,
                        "file": filename,
                        "language": "java"
                    })
        
        # 检测内存泄漏
        if 'new ' in content and 'close()' not in content:
            for i, line in enumerate(lines, 1):
                if 'new ' in line and 'close()' not in content:
                    issues.append({
                        "type": "memory_leak",
                        "severity": "warning",
                        "message": "可能存在内存泄漏",
                        "line": i,
                        "file": filename,
                        "language": "java"
                    })
        
        return issues
    
    async def _analyze_c_content(self, file_path: str, content: str, lines: List[str], filename: str, options: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分析C/C++文件内容"""
        issues = []
        
        # 检测缓冲区溢出
        if 'strcpy' in content or 'strcat' in content:
            for i, line in enumerate(lines, 1):
                if 'strcpy' in line or 'strcat' in line:
                    issues.append({
                        "type": "buffer_overflow",
                        "severity": "error",
                        "message": "缓冲区溢出风险",
                        "line": i,
                        "file": filename,
                        "language": "c"
                    })
        
        # 检测内存泄漏
        if 'malloc' in content and 'free' not in content:
            for i, line in enumerate(lines, 1):
                if 'malloc' in line:
                    issues.append({
                        "type": "memory_leak",
                        "severity": "warning",
                        "message": "内存泄漏",
                        "line": i,
                        "file": filename,
                        "language": "c"
                    })
        
        return issues
    
    async def _analyze_javascript_content(self, file_path: str, content: str, lines: List[str], filename: str, options: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分析JavaScript文件内容"""
        issues = []
        
        # 检测XSS漏洞
        if 'innerHTML' in content or 'document.write' in content:
            for i, line in enumerate(lines, 1):
                if 'innerHTML' in line or 'document.write' in line:
                    issues.append({
                        "type": "xss_vulnerability",
                        "severity": "error",
                        "message": "XSS漏洞风险",
                        "line": i,
                        "file": filename,
                        "language": "javascript"
                    })
        
        return issues
    
    async def _analyze_go_content(self, file_path: str, content: str, lines: List[str], filename: str, options: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分析Go文件内容"""
        issues = []
        
        # 检测未使用的导入
        if 'import ' in content:
            for i, line in enumerate(lines, 1):
                if 'import ' in line and 'fmt' in line and 'fmt.' not in content:
                    issues.append({
                        "type": "unused_import",
                        "severity": "warning",
                        "message": "未使用的导入",
                        "line": i,
                        "file": filename,
                        "language": "go"
                    })
        
        return issues
    
    async def _analyze_generic_content(self, file_path: str, content: str, lines: List[str], filename: str, options: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分析通用文件内容"""
        issues = []
        
        # 检测空文件
        if not content.strip():
            issues.append({
                "type": "empty_file",
                "severity": "info",
                "message": "空文件",
                "line": 1,
                "file": filename,
                "language": "unknown"
            })
        
        return issues
    
    async def _detect_file_bugs(self, file_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """检测单个文件的缺陷 - 支持多语言"""
        try:
            # 检测文件语言
            language = self.detect_language(file_path)
            self.logger.info(f"检测文件 {file_path}，语言: {language}")
            
            all_issues = []
            detection_tools = []
            analysis_time = 0
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 根据语言选择检测工具
            if language == "python":
                # Python文件检测
                if options.get("enable_static", True):
                    start_time = datetime.now()
                    issues = await self._analyze_file_content(file_path, content, language, options)
                    end_time = datetime.now()
                    
                    for issue in issues:
                        issue["file"] = Path(file_path).name
                        issue["language"] = language
                        issue["detection_tool"] = "custom_analyzer"
                        if "column" not in issue:
                            issue["column"] = 0
                    
                    all_issues.extend(issues)
                    detection_tools.append("custom_analyzer")
                    analysis_time += (end_time - start_time).total_seconds()
                
                # Pylint检测
                if options.get("enable_pylint", True) and self.pylint_tool:
                    self.logger.info("开始Pylint检测...")
                    start_time = datetime.now()
                    try:
                        pylint_result = await self.pylint_tool.analyze(file_path)
                        end_time = datetime.now()
                        
                        self.logger.info(f"Pylint检测完成，结果: {pylint_result}")
                        
                        # 注意：pylint 发现问题时通常返回非零退出码，这里以 issues 是否非空为准
                        if pylint_result.get("issues"):
                            for issue in pylint_result["issues"]:
                                issue["language"] = language
                                issue["file"] = Path(file_path).name
                                issue["detection_tool"] = "pylint"
                            all_issues.extend(pylint_result["issues"])
                            detection_tools.append("pylint")
                            self.logger.info(f"Pylint检测到 {len(pylint_result['issues'])} 个问题")
                        else:
                            self.logger.info("Pylint没有检测到问题")
                        
                        analysis_time += (end_time - start_time).total_seconds()
                    except Exception as e:
                        self.logger.error(f"Pylint检测失败: {e}")
                        import traceback
                        self.logger.error(f"Pylint错误详情: {traceback.format_exc()}")
                elif options.get("enable_pylint", True):
                    self.logger.warning("Pylint工具未初始化，跳过Pylint检测")
                
                # Bandit安全检测
                if options.get("enable_bandit", True) and self.bandit_tool:
                    start_time = datetime.now()
                    bandit_result = await self.bandit_tool.analyze(file_path)
                    end_time = datetime.now()
                    
                    if bandit_result["success"]:
                        for issue in bandit_result["issues"]:
                            issue["language"] = language
                            issue["file"] = Path(file_path).name
                            issue["detection_tool"] = "bandit"
                        all_issues.extend(bandit_result["issues"])
                        detection_tools.append("bandit")
                    
                    analysis_time += (end_time - start_time).total_seconds()
                
                # Mypy类型检查
                if options.get("enable_mypy", True) and self.mypy_tool:
                    start_time = datetime.now()
                    mypy_result = await self.mypy_tool.analyze(file_path)
                    end_time = datetime.now()
                    
                    if mypy_result["success"]:
                        for issue in mypy_result["issues"]:
                            issue["language"] = language
                            issue["file"] = Path(file_path).name
                            issue["detection_tool"] = "mypy"
                        all_issues.extend(mypy_result["issues"])
                        detection_tools.append("mypy")
                    
                    analysis_time += (end_time - start_time).total_seconds()
            
            elif language in ["java", "c", "cpp", "javascript", "go"]:
                # 其他语言使用自定义分析 + AI分析
                if options.get("enable_static", True):
                    start_time = datetime.now()
                    issues = await self._analyze_file_content(file_path, content, language, options)
                    end_time = datetime.now()
                    
                    for issue in issues:
                        issue["detection_tool"] = "custom_analyzer"
                    all_issues.extend(issues)
                    detection_tools.append("custom_analyzer")
                    analysis_time += (end_time - start_time).total_seconds()
                
                # AI分析
                if options.get("enable_ai_analysis", True):
                    start_time = datetime.now()
                    ai_issues = await self._ai_analyze_file(file_path, language)
                    end_time = datetime.now()
                    
                    for issue in ai_issues:
                        issue["detection_tool"] = "ai_analyzer"
                    all_issues.extend(ai_issues)
                    detection_tools.append("ai_analyzer")
                    analysis_time += (end_time - start_time).total_seconds()
            
            # 动态检测
            if options.get("enable_dynamic", False):
                self.logger.info("开始动态检测...")
                start_time = datetime.now()
                try:
                    dynamic_issues = await self._dynamic_analyze_file(file_path, language)
                    end_time = datetime.now()
                    
                    for issue in dynamic_issues:
                        issue["file"] = Path(file_path).name
                        issue["language"] = language
                        issue["detection_tool"] = "dynamic_analyzer"
                        if "column" not in issue:
                            issue["column"] = 0
                    
                    all_issues.extend(dynamic_issues)
                    detection_tools.append("dynamic_analyzer")
                    analysis_time += (end_time - start_time).total_seconds()
                    self.logger.info(f"动态检测完成，发现 {len(dynamic_issues)} 个问题")
                except Exception as e:
                    self.logger.error(f"动态检测失败: {e}")
                    import traceback
                    self.logger.error(f"动态检测错误详情: {traceback.format_exc()}")
            
            # 应用过滤条件
            if options.get("severity_filter"):
                all_issues = [issue for issue in all_issues 
                             if issue.get("severity") in options["severity_filter"]]
            
            if options.get("custom_rules"):
                all_issues = [issue for issue in all_issues 
                             if issue.get("type") in options["custom_rules"]]
            
            # 基础检测结果
            basic_results = {
                "file_path": file_path,
                "language": language,
                "total_issues": len(all_issues),
                "issues": all_issues,
                "detection_tools": detection_tools,
                "analysis_time": analysis_time,
                "summary": {
                    "error_count": sum(1 for issue in all_issues if issue.get("severity") == "error"),
                    "warning_count": sum(1 for issue in all_issues if issue.get("severity") == "warning"),
                    "info_count": sum(1 for issue in all_issues if issue.get("severity") == "info")
                }
            }
            
            # 增强检测结果
            enhanced_results = await self._enhance_detection_results(basic_results, file_path)
            
            return enhanced_results
            
        except Exception as e:
            self.logger.error(f"文件检测失败 {file_path}: {e}")
            return {
                "file_path": file_path,
                "language": "unknown",
                "total_issues": 0,
                "issues": [],
                "error": str(e)
            }
    
    async def _ai_analyze_file(self, file_path: str, language: str) -> List[Dict[str, Any]]:
        """使用AI分析非Python文件"""
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 限制文件大小
            if len(content) > 50000:  # 50KB
                content = content[:50000] + "\n... (文件过大，已截断)"
            
            # 构建AI分析提示词
            prompt = f"""
请分析以下{language}代码文件，检测潜在的缺陷和问题：

文件路径: {file_path}
文件内容:
```
{content}
```

请检测以下类型的缺陷：
1. 语法错误和编译问题
2. 逻辑错误和算法问题
3. 内存泄漏和资源管理问题
4. 安全漏洞和输入验证问题
5. 性能问题和优化建议
6. 代码规范和最佳实践问题

请以JSON格式返回检测结果，格式如下：
{{
    "issues": [
        {{
            "type": "缺陷类型",
            "severity": "error/warning/info",
            "line": 行号,
            "column": 列号,
            "message": "详细描述",
            "rule": "规则ID",
            "language": "{language}"
        }}
    ]
}}
"""
            
            # 调用AI分析
            try:
                from api.deepseek_config import deepseek_config
                import aiohttp
            except ImportError:
                self.logger.warning("AI分析功能不可用，跳过AI分析")
                return []
            
            request_data = {
                "model": deepseek_config.model,
                "messages": [
                    {
                        "role": "system",
                        "content": f"你是一个专业的{language}代码分析专家，擅长检测代码缺陷和问题。请以JSON格式返回分析结果。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 2000,
                "temperature": 0.3
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{deepseek_config.base_url}/chat/completions",
                    headers=deepseek_config.get_headers(),
                    json=request_data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        ai_response = result["choices"][0]["message"]["content"]
                        
                        # 解析AI返回的JSON
                        try:
                            import json
                            ai_result = json.loads(ai_response)
                            issues = ai_result.get("issues", [])
                            
                            # 添加文件信息
                            for issue in issues:
                                issue["file"] = Path(file_path).name
                                issue["language"] = language
                            
                            return issues
                        except json.JSONDecodeError:
                            self.logger.warning(f"AI返回格式错误: {ai_response}")
                            return []
                    else:
                        self.logger.warning(f"AI分析失败: {response.status}")
                        return []
        
        except Exception as e:
            self.logger.error(f"AI分析文件失败 {file_path}: {e}")
            return []
    
    async def _dynamic_analyze_file(self, file_path: str, language: str) -> List[Dict[str, Any]]:
        """动态分析文件 - 检测运行时问题"""
        try:
            issues = []
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 动态检测规则
            if language == "python":
                # 检测潜在的运行时问题
                lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    line = line.strip()
                    
                    # 检测未处理的异常
                    if 'except:' in line and 'Exception' not in line:
                        issues.append({
                            'type': 'dynamic',
                            'severity': 'warning',
                            'message': '使用了裸露的except语句，可能隐藏重要异常',
                            'line': i,
                            'column': line.find('except:') + 1
                        })
                    
                    # 检测可能的无限循环
                    if 'while True:' in line and 'break' not in content[content.find(line):content.find(line) + 200]:
                        issues.append({
                            'type': 'dynamic',
                            'severity': 'warning',
                            'message': '可能存在无限循环，缺少break语句',
                            'line': i,
                            'column': line.find('while True:') + 1
                        })
                    
                    # 检测资源未释放
                    if 'open(' in line and 'with' not in line:
                        issues.append({
                            'type': 'dynamic',
                            'severity': 'info',
                            'message': '文件操作未使用with语句，可能导致资源泄漏',
                            'line': i,
                            'column': line.find('open(') + 1
                        })
                    
                    # 检测可能的竞态条件
                    if 'threading' in line and 'lock' not in content.lower():
                        issues.append({
                            'type': 'dynamic',
                            'severity': 'warning',
                            'message': '使用多线程但未发现锁机制，可能存在竞态条件',
                            'line': i,
                            'column': line.find('threading') + 1
                        })
                    
                    # 检测内存泄漏风险
                    if 'global' in line and 'del' not in content:
                        issues.append({
                            'type': 'dynamic',
                            'severity': 'info',
                            'message': '使用全局变量但未发现清理机制，可能存在内存泄漏风险',
                            'line': i,
                            'column': line.find('global') + 1
                        })
            
            return issues
            
        except Exception as e:
            self.logger.error(f"动态分析文件失败 {file_path}: {e}")
            return []
    
    async def _detect_project_bugs(self, project_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """检测整个项目的缺陷"""
        # 这里可以实现项目级别的检测逻辑
        # 遍历项目中的所有Python文件
        project_issues = []
        files_analyzed = []
        
        for py_file in Path(project_path).rglob("*.py"):
            try:
                file_result = await self._detect_file_bugs(str(py_file), options)
                project_issues.extend(file_result["issues"])
                files_analyzed.append(str(py_file))
            except Exception as e:
                self.logger.warning(f"检测文件失败 {py_file}: {e}")
        
        return {
            "project_path": project_path,
            "total_issues": len(project_issues),
            "issues": project_issues,
            "files_analyzed": files_analyzed,
            "summary": {
                "error_count": sum(1 for issue in project_issues if issue.get("severity") == "error"),
                "warning_count": sum(1 for issue in project_issues if issue.get("severity") == "warning"),
                "info_count": sum(1 for issue in project_issues if issue.get("severity") == "info")
            }
        }
    
    async def _generate_report(self, detection_results: Dict[str, Any]) -> Dict[str, Any]:
        """生成检测报告"""
        issues = detection_results.get("issues", [])
        
        # 按类型分组
        issues_by_type = {}
        for issue in issues:
            issue_type = issue.get("type", "unknown")
            issues_by_type[issue_type] = issues_by_type.get(issue_type, 0) + 1
        
        # 按严重程度分组
        issues_by_severity = {"error": 0, "warning": 0, "info": 0}
        for issue in issues:
            severity = issue.get("severity", "info")
            if severity in issues_by_severity:
                issues_by_severity[severity] += 1
        
        # 生成建议
        recommendations = []
        if issues_by_severity["error"] > 0:
            recommendations.append("发现严重错误，建议优先修复")
        if issues_by_severity["warning"] > 10:
            recommendations.append("警告数量较多，建议进行代码审查")
        if "unused_imports" in issues_by_type:
            recommendations.append("存在未使用的导入，建议清理")
        
        return {
            "summary": detection_results.get("summary", {}),
            "issues_by_type": issues_by_type,
            "issues_by_severity": issues_by_severity,
            "recommendations": recommendations,
            "priority_issues": [issue for issue in issues if issue.get("severity") == "error"][:5]
        }
    
    async def get_detection_rules(self) -> Dict[str, Any]:
        """获取检测规则信息"""
        rules = []
        
        for rule_id, enabled in self.detection_rules.items():
            rule_info = {
                "id": rule_id,
                "name": self._get_rule_name(rule_id),
                "description": self._get_rule_description(rule_id),
                "severity": self._get_rule_severity(rule_id),
                "enabled": enabled,
                "category": self._get_rule_category(rule_id)
            }
            rules.append(rule_info)
        
        return {
            "rules": rules,
            "total_rules": len(rules)
        }
    
    def _get_rule_name(self, rule_id: str) -> str:
        """获取规则名称"""
        rule_names = {
            "unused_imports": "未使用的导入",
            "hardcoded_secrets": "硬编码秘密信息",
            "unsafe_eval": "不安全的eval使用",
            "missing_type_hints": "缺少类型注解",
            "long_functions": "过长的函数",
            "duplicate_code": "重复代码",
            "bad_exception_handling": "异常处理不当",
            "global_variables": "全局变量使用",
            "magic_numbers": "魔法数字",
            "unsafe_file_operations": "不安全的文件操作",
            "missing_docstrings": "缺少文档字符串",
            "bad_naming": "命名不规范",
            "unhandled_exceptions": "未处理的异常",
            "deep_nesting": "过深的嵌套",
            "insecure_random": "不安全的随机数",
            "memory_leaks": "内存泄漏风险",
            "missing_input_validation": "缺少输入验证",
            "bad_formatting": "代码格式问题",
            "dead_code": "死代码",
            "unused_variables": "未使用的变量"
        }
        return rule_names.get(rule_id, rule_id)
    
    def _get_rule_description(self, rule_id: str) -> str:
        """获取规则描述"""
        rule_descriptions = {
            "unused_imports": "检测导入但未使用的模块",
            "hardcoded_secrets": "检测硬编码的密码、API密钥等",
            "unsafe_eval": "检测使用eval函数的安全风险",
            "missing_type_hints": "检测函数参数和返回值缺少类型注解",
            "long_functions": "检测超过50行的函数",
            "duplicate_code": "检测相似的代码块",
            "bad_exception_handling": "检测裸露的except语句",
            "global_variables": "检测全局变量的使用",
            "magic_numbers": "检测硬编码的数字常量",
            "unsafe_file_operations": "检测硬编码的文件路径",
            "missing_docstrings": "检测函数和类缺少文档",
            "bad_naming": "检测不符合Python命名规范的标识符",
            "unhandled_exceptions": "检测可能抛出异常但未处理的代码",
            "deep_nesting": "检测超过4层的代码嵌套",
            "insecure_random": "检测使用不安全的随机数生成",
            "memory_leaks": "检测可能的内存泄漏",
            "missing_input_validation": "检测用户输入处理缺少验证",
            "bad_formatting": "检测缩进和格式问题",
            "dead_code": "检测可能未被使用的代码",
            "unused_variables": "检测定义但未使用的变量"
        }
        return rule_descriptions.get(rule_id, "自定义检测规则")
    
    def _get_rule_severity(self, rule_id: str) -> str:
        """获取规则严重程度"""
        severity_map = {
            "hardcoded_secrets": "error",
            "unsafe_eval": "error",
            "unused_imports": "warning",
            "long_functions": "warning",
            "duplicate_code": "warning",
            "bad_exception_handling": "warning",
            "global_variables": "warning",
            "magic_numbers": "info",
            "unsafe_file_operations": "warning",
            "missing_docstrings": "info",
            "bad_naming": "warning",
            "unhandled_exceptions": "warning",
            "deep_nesting": "warning",
            "insecure_random": "warning",
            "memory_leaks": "warning",
            "missing_input_validation": "warning",
            "bad_formatting": "info",
            "dead_code": "info",
            "unused_variables": "warning",
            "missing_type_hints": "info"
        }
        return severity_map.get(rule_id, "info")
    
    def _get_rule_category(self, rule_id: str) -> str:
        """获取规则分类"""
        category_map = {
            "unused_imports": "代码质量",
            "hardcoded_secrets": "安全",
            "unsafe_eval": "安全",
            "missing_type_hints": "代码质量",
            "long_functions": "代码质量",
            "duplicate_code": "代码质量",
            "bad_exception_handling": "代码质量",
            "global_variables": "代码质量",
            "magic_numbers": "代码质量",
            "unsafe_file_operations": "安全",
            "missing_docstrings": "文档",
            "bad_naming": "代码规范",
            "unhandled_exceptions": "代码质量",
            "deep_nesting": "代码质量",
            "insecure_random": "安全",
            "memory_leaks": "性能",
            "missing_input_validation": "安全",
            "bad_formatting": "代码规范",
            "dead_code": "代码质量",
            "unused_variables": "代码质量"
        }
        return category_map.get(rule_id, "其他")
    
    def detect_language(self, file_path: str) -> str:
        """检测文件编程语言"""
        try:
            file_path = Path(file_path)
            extension = file_path.suffix.lower()
            
            # 根据文件扩展名检测语言
            for language, config in self.supported_languages.items():
                if extension in config["extensions"]:
                    return language
            
            # 如果无法通过扩展名检测，尝试读取文件内容
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(1024)  # 只读取前1KB
                    
                    # 基于文件内容的启发式检测
                    if "package " in content and "import " in content:
                        return "java"
                    elif "#include" in content and ("int main" in content or "void main" in content):
                        return "c"
                    elif "#include" in content and ("std::" in content or "using namespace" in content):
                        return "cpp"
                    elif "def " in content or "import " in content or "from " in content:
                        return "python"
                    elif "function " in content or "var " in content or "let " in content:
                        return "javascript"
                    elif "package " in content and "func " in content:
                        return "go"
            except:
                pass
            
            return "unknown"
            
        except Exception as e:
            self.logger.error(f"语言检测失败: {e}")
            return "unknown"
    
    def is_project_upload(self, file_path: str) -> bool:
        """判断是否为项目上传（压缩文件或目录）"""
        try:
            file_path = Path(file_path)
            
            # 检查是否为压缩文件
            archive_extensions = ['.zip', '.tar', '.tar.gz', '.rar', '.7z']
            if file_path.suffix.lower() in archive_extensions:
                return True
            
            # 检查是否为目录
            if file_path.is_dir():
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"项目检测失败: {e}")
            return False
    
    async def extract_project(self, file_path: str) -> str:
        """解压项目文件并创建虚拟环境

        对已知的演示/测试项目（如 flask_simple_test）跳过解压后立即创建项目内虚拟环境，
        避免被热重载器监控而导致 Windows 下文件占用或卡死。此类项目的运行时会由动态检测模块
        使用预置缓存虚拟环境运行。
        """
        try:
            file_path = Path(file_path)
            # 使用更精确的时间戳（包含微秒）和UUID，避免目录冲突
            import uuid
            import time
            max_retries = 5
            extract_dir = None
            
            for attempt in range(max_retries):
                try:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
                    unique_id = uuid.uuid4().hex[:8]
                    extract_dir = Path("temp_extract") / f"project_{timestamp}_{unique_id}"
                    
                    # 如果目录已存在，强制删除它
                    if extract_dir.exists():
                        self.logger.warning(f"临时目录已存在，删除旧目录: {extract_dir}")
                        # 尝试多次删除，确保成功
                        for delete_attempt in range(3):
                            try:
                                shutil.rmtree(extract_dir, ignore_errors=False)
                                break
                            except Exception as e:
                                if delete_attempt < 2:
                                    time.sleep(0.5)  # 等待0.5秒后重试
                                    continue
                                else:
                                    self.logger.warning(f"无法删除旧目录，尝试使用新路径: {e}")
                                    # 如果删除失败，使用新的UUID
                                    unique_id = uuid.uuid4().hex[:8]
                                    extract_dir = Path("temp_extract") / f"project_{timestamp}_{unique_id}"
                    
                    # 创建新目录
                    extract_dir.mkdir(parents=True, exist_ok=False)  # 使用exist_ok=False确保目录不存在
                    break  # 成功创建，退出重试循环
                    
                except FileExistsError:
                    # 目录仍然存在（可能是并发创建），重试
                    if attempt < max_retries - 1:
                        self.logger.warning(f"目录创建冲突，重试 {attempt + 1}/{max_retries}")
                        time.sleep(0.1 * (attempt + 1))  # 递增等待时间
                        continue
                    else:
                        raise Exception(f"无法创建临时目录，已重试{max_retries}次")
                except Exception as e:
                    if attempt < max_retries - 1:
                        self.logger.warning(f"创建临时目录失败，重试 {attempt + 1}/{max_retries}: {e}")
                        time.sleep(0.1 * (attempt + 1))
                        continue
                    else:
                        raise
            
            if extract_dir is None or not extract_dir.exists():
                raise Exception("无法创建临时解压目录")
            
            if file_path.suffix.lower() == '.zip':
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
            elif file_path.suffix.lower() in ['.tar', '.tar.gz']:
                with tarfile.open(file_path, 'r:*') as tar_ref:
                    tar_ref.extractall(extract_dir)
            else:
                # 如果是目录，直接复制
                shutil.copytree(file_path, extract_dir)
            
            self.logger.info(f"项目解压到: {extract_dir}")

            # 常规项目：创建虚拟环境并安装依赖
            # 如果启用了Docker，优先使用Docker
            print(f"🔍 Docker配置检查: use_docker={self.use_docker}, docker_runner={'存在' if self.docker_runner else 'None'}")
            self.logger.info(f"Docker配置检查: use_docker={self.use_docker}, docker_runner={'存在' if self.docker_runner else 'None'}")
            
            # 特判：识别 flask_simple_test，如果未启用Docker则跳过项目内 venv 创建
            try:
                flask_app = Path(extract_dir) / "flask_simple_test" / "app.py"
                req = Path(extract_dir) / "requirements.txt"
                is_flask_simple = False
                if flask_app.exists():
                    is_flask_simple = True
                elif req.exists():
                    try:
                        content = req.read_text(encoding="utf-8", errors="ignore").lower()
                        if "flask==2.0.0" in content:
                            is_flask_simple = True
                    except Exception:
                        pass

                # 如果检测到 flask_simple_test 且未启用 Docker，则跳过虚拟环境创建
                if is_flask_simple and not (self.use_docker and self.docker_runner):
                    print("✅ 检测到 flask_simple_test 项目，跳过项目内虚拟环境创建")
                    self.logger.info("检测到 flask_simple_test 项目，且Docker未启用，跳过项目内虚拟环境创建，改由运行时使用预置缓存 venv。")
                    return str(extract_dir)
            except Exception:
                # 安全降级到常规逻辑
                pass
            
            # 添加进度提示
            if not (self.use_docker and self.docker_runner):
                print("⏳ 开始创建虚拟环境（这可能需要1-3分钟）...")
                self.logger.info("开始创建虚拟环境")
            
            if self.use_docker and self.docker_runner:
                try:
                    print("🐳 尝试使用Docker方式安装依赖...")
                    self.logger.info("使用Docker方式安装依赖")
                    # Docker方式：直接安装依赖，不需要创建本地虚拟环境
                    success = await self._install_dependencies_docker(extract_dir)
                    if success:
                        print("✅ Docker方式依赖安装成功")
                        return str(extract_dir)
                    else:
                        print("⚠️ Docker安装依赖失败，回退到虚拟环境方式")
                        self.logger.warning("Docker安装依赖失败，回退到虚拟环境方式")
                        # 回退到虚拟环境方式
                        venv_path = await self._create_virtual_environment(extract_dir)
                        await self._install_dependencies(extract_dir, venv_path)
                except Exception as e:
                    print(f"⚠️ Docker安装依赖异常: {e}，回退到虚拟环境方式")
                    self.logger.warning(f"Docker安装依赖异常: {e}，回退到虚拟环境方式")
                    import traceback
                    self.logger.warning(f"异常详情: {traceback.format_exc()}")
                    # 回退到虚拟环境方式
                    venv_path = await self._create_virtual_environment(extract_dir)
                    await self._install_dependencies(extract_dir, venv_path)
            else:
                # 传统虚拟环境方式
                if not self.use_docker:
                    print("⚠️ Docker未启用，使用本地虚拟环境")
                    self.logger.info("Docker未启用，使用本地虚拟环境")
                elif not self.docker_runner:
                    print("⚠️ Docker运行器未初始化，使用本地虚拟环境")
                    self.logger.warning("Docker运行器未初始化，使用本地虚拟环境")
                
                print("📦 步骤1/2: 创建虚拟环境...")
                venv_path = await self._create_virtual_environment(extract_dir)
                print("✅ 虚拟环境创建完成")
                
                print("📦 步骤2/2: 安装项目依赖（这可能需要几分钟）...")
                await self._install_dependencies(extract_dir, venv_path)
                print("✅ 依赖安装完成")

            return str(extract_dir)
            
        except Exception as e:
            self.logger.error(f"项目解压失败: {e}")
            raise
    
    async def _create_virtual_environment(self, project_path: Path) -> Path:
        """为项目创建虚拟环境"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                venv_path = project_path / "venv"
                
                # 检查是否已存在虚拟环境
                if venv_path.exists():
                    self.logger.info(f"虚拟环境已存在: {venv_path}")
                    # 验证现有虚拟环境是否可用
                    python_path = venv_path / ("Scripts" if os.name == 'nt' else "bin") / ("python.exe" if os.name == 'nt' else "python")
                    if python_path.exists():
                        # 验证虚拟环境是否正常工作
                        test_result = subprocess.run([
                            str(python_path), "-c", "import sys; print(sys.version)"
                        ], capture_output=True, text=True, timeout=30)
                        
                        if test_result.returncode == 0:
                            self.logger.info("现有虚拟环境验证成功")
                            return venv_path
                        else:
                            self.logger.warning("现有虚拟环境损坏，重新创建")
                            shutil.rmtree(venv_path, ignore_errors=True)
                
                self.logger.info(f"创建虚拟环境 (尝试 {retry_count + 1}/{max_retries}): {venv_path}")
                
                # 创建虚拟环境目录
                venv_path.mkdir(parents=True, exist_ok=True)
                
                # 使用更稳定的虚拟环境创建方式
                try:
                    # 方法1: 使用--without-pip创建，然后手动安装pip
                    result = subprocess.run([
                        sys.executable, "-m", "venv", "--without-pip", str(venv_path)
                    ], capture_output=True, text=True, timeout=180, 
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0)
                    
                    if result.returncode != 0:
                        self.logger.warning(f"方法1失败，尝试方法2: {result.stderr}")
                        # 方法2: 使用默认方式创建
                        result = subprocess.run([
                            sys.executable, "-m", "venv", str(venv_path)
                        ], capture_output=True, text=True, timeout=180,
                        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0)
                        
                        if result.returncode != 0:
                            raise Exception(f"虚拟环境创建失败: {result.stderr}")
                    
                    # 获取虚拟环境中的Python路径
                    python_path = venv_path / ("Scripts" if os.name == 'nt' else "bin") / ("python.exe" if os.name == 'nt' else "python")
                    
                    if not python_path.exists():
                        raise Exception(f"虚拟环境Python不存在: {python_path}")
                    
                    # 等待文件系统稳定
                    import time
                    time.sleep(3)
                    
                    # 验证Python是否可用
                    test_result = subprocess.run([
                        str(python_path), "-c", "import sys; print('Python OK')"
                    ], capture_output=True, text=True, timeout=30)
                    
                    if test_result.returncode != 0:
                        raise Exception(f"虚拟环境Python不可用: {test_result.stderr}")
                    
                    # 安装pip（如果需要）
                    pip_path = venv_path / ("Scripts" if os.name == 'nt' else "bin") / ("pip.exe" if os.name == 'nt' else "pip")
                    
                    if not pip_path.exists():
                        self.logger.info("安装pip到虚拟环境...")
                        pip_install_result = subprocess.run([
                            str(python_path), "-m", "ensurepip", "--upgrade"
                        ], capture_output=True, text=True, timeout=120,
                        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0)
                        
                        if pip_install_result.returncode != 0:
                            self.logger.warning(f"ensurepip失败: {pip_install_result.stderr}")
                            # 尝试使用get-pip.py
                            try:
                                import urllib.request
                                get_pip_url = "https://bootstrap.pypa.io/get-pip.py"
                                get_pip_path = venv_path / "get-pip.py"
                                urllib.request.urlretrieve(get_pip_url, get_pip_path)
                                
                                pip_result = subprocess.run([
                                    str(python_path), str(get_pip_path)
                                ], capture_output=True, text=True, timeout=120,
                                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0)
                                
                                if pip_result.returncode == 0:
                                    self.logger.info("get-pip.py安装pip成功")
                                else:
                                    self.logger.warning(f"get-pip.py失败: {pip_result.stderr}")
                            except Exception as e:
                                self.logger.warning(f"get-pip.py异常: {e}")
                    
                    # 验证pip是否可用
                    pip_test_result = subprocess.run([
                        str(python_path), "-m", "pip", "--version"
                    ], capture_output=True, text=True, timeout=30)
                    
                    if pip_test_result.returncode == 0:
                        self.logger.info(f"pip验证成功: {pip_test_result.stdout.strip()}")
                    else:
                        self.logger.warning(f"pip验证失败: {pip_test_result.stderr}")
                    
                    self.logger.info("虚拟环境创建完成")
                    return venv_path
                    
                except subprocess.TimeoutExpired:
                    self.logger.error(f"虚拟环境创建超时 (尝试 {retry_count + 1})")
                    if retry_count == max_retries - 1:
                        raise Exception("虚拟环境创建超时，请检查系统环境")
                except KeyboardInterrupt:
                    self.logger.error("虚拟环境创建被用户中断")
                    raise Exception("虚拟环境创建被中断")
                except Exception as e:
                    self.logger.error(f"虚拟环境创建异常 (尝试 {retry_count + 1}): {e}")
                    if retry_count == max_retries - 1:
                        raise
                
                # 清理失败的虚拟环境
                if venv_path.exists():
                    shutil.rmtree(venv_path, ignore_errors=True)
                
                retry_count += 1
                if retry_count < max_retries:
                    self.logger.info(f"等待5秒后重试...")
                    time.sleep(5)
            
            except Exception as e:
                self.logger.error(f"创建虚拟环境失败 (尝试 {retry_count + 1}): {e}")
                if retry_count == max_retries - 1:
                    raise
                retry_count += 1
                time.sleep(5)
        
        raise Exception("虚拟环境创建失败，已达到最大重试次数")
    
    def _fix_file_encoding(self, file_path: Path) -> bool:
        """修复文件编码问题，确保文件可以被正确读取"""
        try:
            # 尝试多种编码方式读取文件
            encodings = ['utf-8', 'gbk', 'gb2312', 'cp936', 'latin-1', 'iso-8859-1']
            content = None
            used_encoding = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    used_encoding = encoding
                    self.logger.info(f"成功使用 {encoding} 编码读取文件: {file_path}")
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                self.logger.error(f"无法使用任何编码读取文件: {file_path}")
                return False
            
            # 如果使用的不是UTF-8，则转换为UTF-8
            if used_encoding != 'utf-8':
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    self.logger.info(f"已将文件从 {used_encoding} 转换为 UTF-8: {file_path}")
                    return True
                except Exception as e:
                    self.logger.error(f"转换文件编码失败: {file_path}, 错误: {e}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"处理文件编码时发生异常: {file_path}, 错误: {e}")
            return False

    async def _install_dependencies(self, project_path: Path, venv_path: Path) -> bool:
        """在虚拟环境中安装项目依赖"""
        try:
            # 获取虚拟环境中的Python和pip路径
            if os.name == 'nt':  # Windows
                python_path = venv_path / "Scripts" / "python.exe"
                pip_path = venv_path / "Scripts" / "pip.exe"
            else:  # Unix/Linux
                python_path = venv_path / "bin" / "python"
                pip_path = venv_path / "bin" / "pip"
            
            if not python_path.exists():
                raise Exception(f"虚拟环境Python不存在: {python_path}")
            
            # 检查pip是否存在，如果不存在则使用python -m pip
            pip_cmd = [str(python_path), "-m", "pip"]
            if pip_path.exists():
                pip_cmd = [str(pip_path)]
            
            # 查找依赖文件
            requirements_files = [
                project_path / "requirements.txt",
                project_path / "requirements-dev.txt",
                project_path / "requirements-test.txt",
                project_path / "pyproject.toml",
                project_path / "setup.py"
            ]
            
            installed_any = False
            
            # 安装requirements.txt
            for req_file in requirements_files[:3]:  # requirements*.txt
                if req_file.exists():
                    print(f"📦 正在安装依赖文件: {req_file.name}")
                    self.logger.info(f"安装依赖文件: {req_file}")
                    
                    # 修复文件编码问题
                    if not self._fix_file_encoding(req_file):
                        self.logger.error(f"无法修复文件编码，跳过: {req_file}")
                        continue
                    
                    # 读取requirements.txt内容，检查是否有Flask
                    try:
                        with open(req_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 如果包含Flask，强制安装指定版本
                        if 'flask' in content.lower():
                            self.logger.info("检测到Flask依赖，强制安装Flask 2.0.0")
                            
                            # 先卸载现有Flask版本
                            uninstall_result = subprocess.run(
                                pip_cmd + ["uninstall", "flask", "werkzeug", "-y"],
                                capture_output=True, text=True, timeout=60,
                                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
                            )
                            
                            # 强制安装Flask 2.0.0和兼容的Werkzeug
                            flask_result = subprocess.run(
                                pip_cmd + ["install", "Flask==2.0.0", "Werkzeug==2.0.0", "--force-reinstall"],
                                capture_output=True, text=True, timeout=180,
                                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
                            )
                            
                            if flask_result.returncode == 0:
                                self.logger.info("Flask 2.0.0安装成功")
                                installed_any = True
                                
                                # 验证Flask版本
                                verify_result = subprocess.run([
                                    str(python_path), "-c", "import flask; print(f'Flask版本: {flask.__version__}')"
                                ], capture_output=True, text=True, timeout=30)
                                
                                if verify_result.returncode == 0:
                                    self.logger.info(f"Flask版本验证: {verify_result.stdout.strip()}")
                                else:
                                    self.logger.warning(f"Flask版本验证失败: {verify_result.stderr}")
                            else:
                                self.logger.warning(f"Flask 2.0.0安装失败: {flask_result.stderr}")
                        
                        # 安装其他依赖
                        print(f"⏳ 正在安装依赖（最多5分钟）...")
                        result = subprocess.run(
                            pip_cmd + ["install", "-r", str(req_file)],
                            capture_output=True, text=True, timeout=300,
                            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
                        )
                        
                        if result.returncode == 0:
                            print(f"✅ 依赖安装成功: {req_file.name}")
                            self.logger.info(f"依赖安装成功: {req_file}")
                            installed_any = True
                        else:
                            print(f"⚠️ 依赖安装失败: {req_file.name}")
                            self.logger.warning(f"依赖安装失败: {req_file}, 错误: {result.stderr}")
                            # 尝试使用--user参数
                            try:
                                self.logger.info(f"尝试使用--user参数安装: {req_file}")
                                result2 = subprocess.run(
                                    pip_cmd + ["install", "-r", str(req_file), "--user"],
                                    capture_output=True, text=True, timeout=300,
                                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
                                )
                                
                                if result2.returncode == 0:
                                    self.logger.info(f"使用--user参数安装成功: {req_file}")
                                    installed_any = True
                                else:
                                    self.logger.warning(f"使用--user参数安装也失败: {result2.stderr}")
                            except Exception as e:
                                self.logger.warning(f"使用--user参数安装异常: {e}")
                    
                    except Exception as e:
                        self.logger.warning(f"处理requirements文件异常: {e}")
                        continue
            
            # 安装pyproject.toml
            pyproject_file = project_path / "pyproject.toml"
            if pyproject_file.exists():
                self.logger.info(f"安装pyproject.toml依赖: {pyproject_file}")
                
                result = subprocess.run(
                    pip_cmd + ["install", "-e", str(project_path)],
                    capture_output=True, text=True, timeout=300,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
                )
                
                if result.returncode == 0:
                    self.logger.info("pyproject.toml依赖安装成功")
                    installed_any = True
                else:
                    self.logger.warning(f"pyproject.toml依赖安装失败: {result.stderr}")
            
            # 安装setup.py
            setup_file = project_path / "setup.py"
            if setup_file.exists():
                self.logger.info(f"安装setup.py依赖: {setup_file}")
                
                result = subprocess.run(
                    pip_cmd + ["install", "-e", str(project_path)],
                    capture_output=True, text=True, timeout=300,
                    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
                )
                
                if result.returncode == 0:
                    self.logger.info("setup.py依赖安装成功")
                    installed_any = True
                else:
                    self.logger.warning(f"setup.py依赖安装失败: {result.stderr}")
            
            # 如果没有找到任何依赖文件，尝试安装常见的Python包
            if not installed_any:
                self.logger.info("未找到依赖文件，安装常见Python包")
                common_packages = [
                    "flask==2.0.0", "werkzeug==2.0.0", "django", "fastapi", "requests", 
                    "numpy", "pandas", "matplotlib", "pytest", "unittest"
                ]
                
                for package in common_packages:
                    try:
                        result = subprocess.run(
                            pip_cmd + ["install", package],
                            capture_output=True, text=True, timeout=300,
                            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
                        )
                        
                        if result.returncode == 0:
                            self.logger.info(f"安装成功: {package}")
                            installed_any = True
                        else:
                            self.logger.debug(f"安装失败: {package}")
                    except:
                        continue
            
            # 保存虚拟环境路径到项目目录，供动态检测使用
            venv_info_file = project_path / ".venv_info"
            with open(venv_info_file, 'w') as f:
                f.write(str(python_path))
            
            self.logger.info("依赖安装完成")
            return True
            
        except Exception as e:
            self.logger.error(f"依赖安装失败: {e}")
            return False
    
    async def _install_dependencies_docker(self, project_path: Path) -> bool:
        """使用Docker容器安装项目依赖"""
        try:
            if not self.docker_runner:
                raise Exception("Docker运行器未初始化")
            
            self.logger.info("使用Docker方式安装依赖")
            
            # 查找requirements.txt
            requirements_file = project_path / "requirements.txt"
            if not requirements_file.exists():
                # 检查子目录中是否有requirements.txt
                for subdir in project_path.iterdir():
                    if subdir.is_dir():
                        sub_req = subdir / "requirements.txt"
                        if sub_req.exists():
                            requirements_file = sub_req
                            break
            
            # 安装依赖
            result = await self.docker_runner.install_dependencies(
                project_path=project_path,
                requirements_file=requirements_file if requirements_file.exists() else None
            )
            
            if result.get("success", False):
                self.logger.info("Docker方式依赖安装成功")
                if result.get("stdout"):
                    self.logger.info(f"安装输出: {result['stdout'][:500]}")
                return True
            else:
                error_msg = result.get("error")
                stderr = result.get("stderr", "")
                stdout = result.get("stdout", "")
                returncode = result.get("returncode", -1)
                
                # 构建详细的错误信息
                full_error_parts = []
                if error_msg:
                    full_error_parts.append(error_msg)
                
                # 优先使用stderr，如果没有则使用stdout（某些命令可能将错误输出到stdout）
                error_output = stderr if stderr else stdout
                if error_output:
                    # 显示完整的错误输出（限制长度）
                    full_error_parts.append(f"错误输出: {error_output[:1000]}")
                
                if not full_error_parts:
                    full_error_parts.append(f"命令执行失败（返回码: {returncode}），无错误详情")
                
                full_error = "\n".join(full_error_parts)
                
                self.logger.warning(f"Docker依赖安装失败: {full_error}")
                
                # 额外记录详细信息
                if stdout:
                    self.logger.debug(f"Docker stdout: {stdout[:500]}")
                if stderr:
                    self.logger.debug(f"Docker stderr: {stderr[:500]}")
                
                return False
            
        except Exception as e:
            self.logger.error(f"Docker方式安装依赖失败: {e}")
            import traceback
            self.logger.error(f"Docker安装依赖错误详情: {traceback.format_exc()}")
            return False
    
    async def _cleanup_project_environment_async(self, project_path: str):
        """后台异步清理项目环境（不阻塞主流程）"""
        try:
            self.logger.info(f"🧹 开始后台清理项目环境: {project_path}")
            await self.cleanup_project_environment(project_path)
            self.logger.info(f"✅ 后台清理完成: {project_path}")
        except Exception as e:
            self.logger.warning(f"⚠️ 后台清理失败: {project_path}, 错误: {e}")
    
    async def cleanup_project_environment(self, project_path: str) -> bool:
        """清理项目环境（删除临时文件和虚拟环境）"""
        try:
            # 检查project_path是否为None或空
            if not project_path:
                self.logger.warning("cleanup_project_environment: project_path为空，跳过清理")
                return False
            
            project_path = Path(project_path)
            
            # 检查路径是否存在
            if not project_path.exists():
                self.logger.warning(f"cleanup_project_environment: 路径不存在，跳过清理: {project_path}")
                return False
            
            # 删除虚拟环境
            venv_path = project_path / "venv"
            if venv_path.exists():
                self.logger.info(f"清理虚拟环境: {venv_path}")
                shutil.rmtree(venv_path, ignore_errors=True)
            
            # 删除.venv_info文件
            venv_info_file = project_path / ".venv_info"
            if venv_info_file.exists():
                venv_info_file.unlink()
            
            # 删除__pycache__目录
            for pycache_dir in project_path.rglob("__pycache__"):
                if pycache_dir.is_dir():
                    shutil.rmtree(pycache_dir, ignore_errors=True)
            
            # 删除.pyc文件
            for pyc_file in project_path.rglob("*.pyc"):
                if pyc_file.is_file():
                    pyc_file.unlink()
            
            self.logger.info("项目环境清理完成")
            return True
            
        except Exception as e:
            self.logger.error(f"项目环境清理失败: {e}")
            return False
    
    async def cleanup_temp_extract(self) -> bool:
        """清理临时解压目录"""
        try:
            temp_extract_dir = Path("temp_extract")
            if temp_extract_dir.exists():
                self.logger.info(f"清理临时解压目录: {temp_extract_dir}")
                shutil.rmtree(temp_extract_dir, ignore_errors=True)
                return True
            return True
            
        except Exception as e:
            self.logger.error(f"清理临时解压目录失败: {e}")
            return False
    
    def scan_project_files(self, project_path: str) -> Dict[str, List[str]]:
        """扫描项目中的代码文件"""
        try:
            project_path = Path(project_path)
            files_by_language = {}
            
            for language, config in self.supported_languages.items():
                files_by_language[language] = []
                
                for extension in config["extensions"]:
                    # 递归查找所有匹配的文件
                    for file_path in project_path.rglob(f"*{extension}"):
                        # 检查文件大小
                        if file_path.stat().st_size <= self.project_config["max_file_size"]:
                            files_by_language[language].append(str(file_path))
            
            # 过滤掉空的语言
            files_by_language = {k: v for k, v in files_by_language.items() if v}
            
            self.logger.info(f"扫描到文件: {sum(len(files) for files in files_by_language.values())} 个")
            for language, files in files_by_language.items():
                self.logger.info(f"  {language}: {len(files)} 个文件")
            
            return files_by_language
            
        except Exception as e:
            self.logger.error(f"项目文件扫描失败: {e}")
            return {}
    
    async def _filter_project_files(self, project_path: str) -> Dict[str, Any]:
        """
        过滤项目文件，排除第三方库、环境文件等，只保留核心源代码文件
        
        Args:
            project_path: 项目路径
            
        Returns:
            {
                "core_files": List[str],  # 核心文件列表（相对路径）
                "excluded_files": List[str],  # 被排除的文件列表（相对路径）
                "statistics": Dict[str, Any]  # 统计信息
            }
        """
        # 使用缓存避免重复过滤（基于项目路径）
        cache_key = f"_filter_cache_{project_path}"
        if hasattr(self, cache_key):
            cached_result = getattr(self, cache_key)
            self.logger.info(f"使用缓存的文件过滤结果（项目路径: {project_path}）")
            print(f"📂 [BugDetectionAgent] 使用缓存的文件过滤结果")
            return cached_result
        
        try:
            from tools.github_project_filter import github_filter
            
            # 使用GitHub项目过滤器进行文件过滤
            # 在后台线程中执行，避免阻塞
            import concurrent.futures
            loop = asyncio.get_event_loop()
            print(f"📂 [BugDetectionAgent] 开始执行文件过滤（GitHub过滤器）...")
            filter_result = await loop.run_in_executor(
                None,
                lambda: github_filter.filter_project_files(project_path)
            )
            print(f"📂 [BugDetectionAgent] GitHub过滤器执行完成")
            
            core_files = filter_result.get('analyze_files', [])
            excluded_files = filter_result.get('skip_files', [])
            statistics = filter_result.get('statistics', {})
            
            # 额外过滤：排除常见的第三方库目录
            additional_exclude_patterns = [
                # Python第三方库常见位置
                r'site-packages',
                r'lib/python\d+',
                r'Lib/site-packages',
                # Node.js第三方库
                r'node_modules',
                r'bower_components',
                # Java第三方库
                r'lib[\\/].*\.jar',
                # 通用第三方库目录
                r'vendor',
                r'third_party',
                r'third-party',
                r'external',
                r'dependencies',
                r'deps',
                # 测试生成的目录
                r'\.pytest_cache',
                r'\.coverage',
                r'htmlcov',
                # 构建产物
                r'build[\\/]lib',
                r'dist[\\/].*\.egg',
            ]
            
            import re
            final_core_files = []
            additional_excluded = []
            
            for file_path in core_files:
                # 检查是否匹配排除模式
                should_exclude = False
                for pattern in additional_exclude_patterns:
                    if re.search(pattern, file_path, re.IGNORECASE):
                        should_exclude = True
                        break
                
                if should_exclude:
                    additional_excluded.append(file_path)
                else:
                    final_core_files.append(file_path)
            
            # 更新统计信息
            statistics['additional_excluded'] = len(additional_excluded)
            statistics['final_core_files'] = len(final_core_files)
            statistics['filter_ratio'] = len(final_core_files) / (len(final_core_files) + len(excluded_files) + len(additional_excluded)) if (len(final_core_files) + len(excluded_files) + len(additional_excluded)) > 0 else 0
            
            self.logger.info(f"文件过滤统计: 核心文件 {len(final_core_files)}, 排除 {len(excluded_files) + len(additional_excluded)}, 过滤比例 {statistics['filter_ratio']:.2%}")
            
            result = {
                "core_files": final_core_files,
                "excluded_files": excluded_files + additional_excluded,
                "statistics": statistics
            }
            
            # 缓存结果，避免重复过滤
            setattr(self, cache_key, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"文件过滤失败: {e}")
            import traceback
            traceback.print_exc()
            # 如果过滤失败，返回所有文件作为核心文件
            all_files = []
            for root, dirs, files in os.walk(project_path):
                dirs[:] = [d for d in dirs if d not in self.project_config["skip_dirs"]]
                for file in files:
                    if not any(file.endswith(ext) for ext in ['.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe']):
                        rel_path = os.path.relpath(os.path.join(root, file), project_path)
                        all_files.append(rel_path)
            
            return {
                "core_files": all_files,
                "excluded_files": [],
                "statistics": {
                    "error": str(e),
                    "fallback_mode": True
                }
            }
    
    def _filter_and_sample_files(self, files_by_language: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """过滤和采样文件，提高分析效率"""
        try:
            filtered_files = {}
            
            for language, files in files_by_language.items():
                filtered_language_files = []
                
                for file_path in files:
                    file_path_obj = Path(file_path)
                    
                    # 跳过指定目录
                    skip_file = False
                    for skip_dir in self.project_config["skip_dirs"]:
                        if skip_dir in str(file_path_obj):
                            skip_file = True
                            break
                    
                    if skip_file:
                        continue
                    
                    # 跳过指定文件类型
                    skip_file = False
                    for skip_pattern in self.project_config["skip_files"]:
                        if file_path_obj.match(skip_pattern):
                            skip_file = True
                            break
                    
                    if skip_file:
                        continue
                    
                    # 检查文件大小
                    try:
                        file_size = file_path_obj.stat().st_size
                        if file_size > self.project_config["max_file_size"]:
                            continue
                    except:
                        continue
                    
                    filtered_language_files.append(file_path)
                
                # 应用采样比例
                if filtered_language_files:
                    sample_size = max(1, int(len(filtered_language_files) * self.project_config["sample_ratio"]))
                    filtered_language_files = filtered_language_files[:sample_size]
                    filtered_files[language] = filtered_language_files
            
            self.logger.info(f"过滤后文件: {sum(len(files) for files in filtered_files.values())} 个")
            for language, files in filtered_files.items():
                self.logger.info(f"  {language}: {len(files)} 个文件")
            
            return filtered_files
            
        except Exception as e:
            self.logger.error(f"文件过滤失败: {e}")
            return files_by_language
    
    async def analyze_project(self, project_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """分析整个项目 - 增强版静态分析"""
        try:
            self.logger.info(f"开始分析项目: {project_path}")
            print(f"📋 [BugDetectionAgent] 开始分析项目: {project_path}")
            
            # 执行增强的静态分析
            print(f"🔍 [BugDetectionAgent] 开始执行增强静态分析...")
            analysis_result = await self._perform_enhanced_static_analysis(project_path, options)
            print(f"✅ [BugDetectionAgent] 增强静态分析完成")
            
            if analysis_result.get("success", False):
                return {
                    "success": True,
                    "detection_results": analysis_result
                }
            else:
                # 回退到基础分析
                self.logger.warning("增强分析失败，回退到基础分析")
                return await self._perform_basic_project_analysis(project_path, options)
            
        except Exception as e:
            self.logger.error(f"项目分析失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "detection_results": {
                    "project_path": project_path,
                    "total_issues": 0,
                    "issues": [],
                    "summary": {"error_count": 0, "warning_count": 0, "info_count": 0}
                }
            }
    
    async def _perform_enhanced_static_analysis(self, project_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """执行增强的静态分析（已移除代码分析，仅执行缺陷检测）"""
        try:
            # 简化的项目结构分析，避免复杂的agent初始化
            self.logger.info("开始简化项目结构分析...")
            project_structure = await self._simple_project_structure_analysis(project_path)
            
            # 简化的代码质量分析
            self.logger.info("开始简化代码质量分析...")
            code_quality = await self._simple_code_quality_analysis(project_path)
            
            # 简化的依赖分析
            self.logger.info("开始简化依赖关系分析...")
            dependencies = await self._simple_dependency_analysis(project_path)
            # 获取初步分析结果（如果已由综合检测器执行）
            preliminary_analysis = options.get("preliminary_analysis")
            if preliminary_analysis and preliminary_analysis.get("success"):
                project_structure = preliminary_analysis.get("project_structure", {})
                code_quality = preliminary_analysis.get("code_quality", {})
                dependencies = preliminary_analysis.get("dependencies", {})
                self.logger.info("使用初步分析结果（来自综合检测器）")
            else:
                # 如果没有初步分析结果，使用空字典
                project_structure = {}
                code_quality = {}
                dependencies = {}
                self.logger.info("未找到初步分析结果，使用默认值")
            
            # ========== 步骤1: 文件过滤（排除第三方库等）==========
            self.logger.info("开始过滤项目文件，排除第三方库...")
            print(f"📁 [BugDetectionAgent] 开始过滤项目文件...")
            filtered_files_info = await self._filter_project_files(project_path)
            print(f"✅ [BugDetectionAgent] 文件过滤完成")
            
            core_files = filtered_files_info.get("core_files", [])
            excluded_files = filtered_files_info.get("excluded_files", [])
            filter_statistics = filtered_files_info.get("statistics", {})
            
            self.logger.info(f"文件过滤完成: 核心文件 {len(core_files)} 个, 排除文件 {len(excluded_files)} 个")
            
            # 将相对路径转换为绝对路径（用于后续分析）
            python_files = []
            other_language_files = []
            
            for rel_file in core_files:
                abs_file_path = os.path.join(project_path, rel_file)
                if not os.path.exists(abs_file_path):
                    continue
                
                try:
                    # 文件大小限制
                    if os.path.getsize(abs_file_path) <= 2 * 1024 * 1024:  # 2MB限制
                        if rel_file.endswith('.py'):
                            python_files.append(abs_file_path)
                        elif self.ai_analyzer and self.ai_analyzer.is_supported_file(abs_file_path):
                            other_language_files.append(abs_file_path)
                except:
                    continue
            
            # ========== 步骤2: 执行静态分析（方案B标准工具集）==========
            # 使用并行处理提高效率
            import asyncio
            
            pylint_issues = []
            mypy_issues = []
            semgrep_issues = []
            ruff_issues = []
            bandit_issues = []
            
            self.logger.info(f"开始静态分析 {len(python_files)} 个核心Python文件（已过滤，方案B标准工具集）...")
            
            # 文件已通过过滤机制筛选，只保留核心文件，无需再限制数量
            # 如果需要，可以设置一个合理的上限以避免超大项目性能问题（如100个文件）
            max_files_for_detailed_analysis = options.get("max_files_for_analysis", 100)
            
            # Pylint性能优化：如果文件数量较多，使用目录模式而不是逐个文件分析
            pylint_dir_mode_option = options.get("pylint_directory_mode", True)
            use_pylint_directory_mode = pylint_dir_mode_option and len(python_files) > 10
            
            self.logger.info(f"Pylint目录模式配置: option={pylint_dir_mode_option}, use_directory_mode={use_pylint_directory_mode}, python_files_count={len(python_files)}")
            
            if len(python_files) > max_files_for_detailed_analysis:
                self.logger.info(f"核心文件数 ({len(python_files)}) 超过上限 ({max_files_for_detailed_analysis})，仅分析前 {max_files_for_detailed_analysis} 个文件")
                analysis_files = python_files[:max_files_for_detailed_analysis]
            else:
                analysis_files = python_files  # 分析所有过滤后的核心文件
            
            self.logger.info(f"实际分析文件数: {len(analysis_files)}")
            
            # Pylint：优先使用目录模式（更高效）
            if options.get("enable_pylint", True) and self.pylint_tool:
                if use_pylint_directory_mode and hasattr(self.pylint_tool, 'analyze_directory'):
                    self.logger.info(f"使用Pylint目录模式分析（更高效，文件数: {len(analysis_files)}）...")
                    try:
                        # 只分析包含核心文件的目录
                        # 获取所有需要分析的文件的共同父目录
                        if analysis_files:
                            common_path = os.path.commonpath(analysis_files)
                            pylint_result = await self.pylint_tool.analyze_directory(common_path, '*.py')
                            
                            if pylint_result.get('success') and pylint_result.get('issues'):
                                # 只保留核心文件的问题
                                # 构建文件路径映射（支持多种路径格式）
                                core_file_basenames = {os.path.basename(os.path.normpath(f)) for f in analysis_files}
                                core_file_relpaths = {os.path.normpath(os.path.relpath(cf, project_path)) for cf in analysis_files}
                                
                                for issue in pylint_result['issues']:
                                    issue_path = issue.get('file', '')
                                    if not issue_path:
                                        continue
                                    
                                    issue_path_norm = os.path.normpath(issue_path)
                                    issue_basename = os.path.basename(issue_path_norm)
                                    
                                    # 检查是否在核心文件列表中（多种匹配方式）
                                    is_core_file = False
                                    # 方式1: 完全匹配绝对路径
                                    if issue_path_norm in {os.path.normpath(f) for f in analysis_files}:
                                        is_core_file = True
                                    # 方式2: 匹配相对路径
                                    elif any(issue_path_norm.endswith(rel_path) or issue_path_norm == rel_path 
                                             for rel_path in core_file_relpaths):
                                        is_core_file = True
                                    # 方式3: 匹配文件名（防止路径格式差异）
                                    elif issue_basename in core_file_basenames:
                                        is_core_file = True
                                    
                                    if is_core_file:
                                        # 转换为相对路径
                                        try:
                                            if os.path.isabs(issue_path):
                                                issue['file'] = os.path.relpath(issue_path, project_path)
                                            else:
                                                issue['file'] = issue_path
                                        except:
                                            issue['file'] = issue_path
                                        issue['tool'] = 'pylint'
                                        pylint_issues.append(issue)
                                
                                self.logger.info(f"Pylint目录模式检测到 {len(pylint_issues)} 个问题（已过滤为核心文件，原始问题数: {len(pylint_result['issues'])})")
                    except Exception as e:
                        self.logger.warning(f"Pylint目录模式分析失败，回退到单文件模式: {e}")
                        use_pylint_directory_mode = False  # 回退到单文件模式
            
            # 如果目录模式失败或禁用，使用单文件并行模式
            self.logger.info(f"use_pylint_directory_mode={use_pylint_directory_mode}, 将使用{'目录模式' if use_pylint_directory_mode else '单文件模式'}")
            if not use_pylint_directory_mode:
                # 并行执行单个文件分析工具（Pylint、Mypy）
                async def analyze_file_tools(file_path: str):
                    """并行分析单个文件"""
                    file_issues = {
                        'pylint': [],
                        'mypy': []
                    }
                    rel_path = os.path.relpath(file_path, project_path)
                    
                    try:
                        # 并行执行Pylint、Mypy（根据选项启用/禁用）
                        tasks = []
                        
                        if options.get("enable_pylint", True) and self.pylint_tool:
                            tasks.append(('pylint', self.pylint_tool.analyze(file_path)))
                        if options.get("enable_mypy", True) and self.mypy_tool:
                            tasks.append(('mypy', self.mypy_tool.analyze(file_path)))
                        
                        # 并行执行所有工具
                        if tasks:
                            results = await asyncio.gather(*[task[1] for task in tasks], return_exceptions=True)
                            
                            for (tool_name, _), result in zip(tasks, results):
                                if isinstance(result, Exception):
                                    self.logger.warning(f"{tool_name}分析失败 {file_path}: {result}")
                                    continue
                                
                                if result.get('success') and result.get('issues'):
                                    for issue in result['issues']:
                                        issue['file'] = rel_path
                                        issue['tool'] = tool_name
                                        file_issues[tool_name].append(issue)
                    
                    except Exception as e:
                        self.logger.warning(f"文件工具分析失败 {file_path}: {e}")
                    
                    return file_issues
                
                # 批量并行处理文件（限制并发数以避免资源耗尽）
                if analysis_files:
                    max_workers = options.get("max_parallel_files", 10)  # 默认最多10个文件并行
                    
                    # 分批处理
                    for i in range(0, len(analysis_files), max_workers):
                        batch = analysis_files[i:i + max_workers]
                        self.logger.info(f"并行分析文件批次 {i//max_workers + 1}/{(len(analysis_files) + max_workers - 1)//max_workers} ({len(batch)} 个文件)...")
                        
                        file_results = await asyncio.gather(*[analyze_file_tools(f) for f in batch], return_exceptions=True)
                        
                        batch_pylint_count = 0
                        batch_mypy_count = 0
                        for result in file_results:
                            if isinstance(result, Exception):
                                self.logger.warning(f"文件分析异常: {result}")
                                continue
                            pylint_batch = result.get('pylint', [])
                            mypy_batch = result.get('mypy', [])
                            batch_pylint_count += len(pylint_batch)
                            batch_mypy_count += len(mypy_batch)
                            pylint_issues.extend(pylint_batch)
                            mypy_issues.extend(mypy_batch)
                        
                        self.logger.info(f"批次 {i//max_workers + 1} 完成: Pylint={batch_pylint_count}个问题, Mypy={batch_mypy_count}个问题")
            
            # Mypy仍然使用单文件模式（因为Mypy需要类型检查，目录模式可能不够精确）
            # 注意：如果使用了Pylint目录模式，Mypy需要单独执行
            if options.get("enable_mypy", True) and self.mypy_tool:
                if use_pylint_directory_mode:
                    # 如果使用了Pylint目录模式，需要单独执行Mypy
                    self.logger.info("使用Mypy单文件模式分析（Pylint已使用目录模式）...")
                    async def analyze_mypy_file(file_path: str):
                        """分析单个文件的Mypy"""
                        rel_path = os.path.relpath(file_path, project_path)
                        try:
                            result = await self.mypy_tool.analyze(file_path)
                            issues = []
                            if result.get('success') and result.get('issues'):
                                for issue in result['issues']:
                                    issue['file'] = rel_path
                                    issue['tool'] = 'mypy'
                                    issues.append(issue)
                            return issues
                        except Exception as e:
                            self.logger.warning(f"Mypy分析失败 {file_path}: {e}")
                            return []
                    
                    # 批量并行处理Mypy
                    max_workers = options.get("max_parallel_files", 10)
                    for i in range(0, len(analysis_files), max_workers):
                        batch = analysis_files[i:i + max_workers]
                        mypy_results = await asyncio.gather(*[analyze_mypy_file(f) for f in batch], return_exceptions=True)
                        for result in mypy_results:
                            if isinstance(result, Exception):
                                continue
                            mypy_issues.extend(result)
                # else: Mypy的分析已经在单文件模式中处理了（在analyze_file_tools中）
            
            # Bandit：对整个目录进行安全检测（优先使用目录模式，更高效）
            if options.get("enable_bandit", True) and self.bandit_tool:
                self.logger.info("开始Bandit安全检测...")
                try:
                    # Bandit优先使用目录模式，更高效
                    # 添加超时保护（最多5分钟）
                    if hasattr(self.bandit_tool, 'analyze_directory'):
                        try:
                            bandit_result = await asyncio.wait_for(
                                self.bandit_tool.analyze_directory(project_path),
                                timeout=300.0  # 5分钟超时
                            )
                        except asyncio.TimeoutError:
                            self.logger.warning("Bandit目录分析超时（5分钟），跳过Bandit检测")
                            bandit_result = {
                                'success': False,
                                'error': 'Bandit执行超时（5分钟）',
                                'issues': []
                            }
                        except Exception as e:
                            # 捕获其他异常（包括subprocess.TimeoutExpired）
                            error_msg = str(e)
                            if 'timeout' in error_msg.lower() or 'TimeoutExpired' in str(type(e)):
                                self.logger.warning(f"Bandit目录分析超时: {e}")
                                bandit_result = {
                                    'success': False,
                                    'error': f'Bandit执行超时: {error_msg}',
                                    'issues': []
                                }
                            else:
                                # 其他异常，重新抛出或记录
                                self.logger.warning(f"Bandit目录分析异常: {e}")
                                bandit_result = {
                                    'success': False,
                                    'error': f'Bandit执行异常: {error_msg}',
                                    'issues': []
                                }
                        
                        if bandit_result.get('success') and bandit_result.get('issues'):
                            # 只保留核心文件的问题
                            # 构建多种路径格式用于匹配（绝对路径、相对路径、文件名）
                            core_file_norms = {os.path.normpath(f) for f in analysis_files}
                            core_file_rels = {os.path.normpath(os.path.relpath(cf, project_path)) for cf in analysis_files}
                            core_file_basenames = {os.path.basename(os.path.normpath(f)) for f in analysis_files}
                            
                            for issue in bandit_result['issues']:
                                issue_path = issue.get('file', '')
                                if not issue_path:
                                    continue
                                
                                issue_path_norm = os.path.normpath(issue_path)
                                issue_basename = os.path.basename(issue_path_norm)
                                
                                # 多种匹配方式
                                is_core_file = False
                                # 方式1: 完全匹配绝对路径
                                if issue_path_norm in core_file_norms:
                                    is_core_file = True
                                # 方式2: 匹配相对路径（issue_path可能包含相对路径）
                                elif any(issue_path_norm.endswith(rel_path) or issue_path_norm == rel_path 
                                         for rel_path in core_file_rels):
                                    is_core_file = True
                                # 方式3: 匹配文件名（防止路径格式差异）
                                elif issue_basename in core_file_basenames:
                                    # 进一步验证：检查是否在项目目录下
                                    if os.path.isabs(issue_path):
                                        if any(issue_path_norm.startswith(os.path.dirname(cf)) for cf in analysis_files):
                                            is_core_file = True
                                    else:
                                        # 相对路径，检查是否匹配任何核心文件的相对路径
                                        if any(issue_path_norm in rel_path or rel_path.endswith(issue_path_norm) 
                                               for rel_path in core_file_rels):
                                            is_core_file = True
                                    # 额外匹配：中文/路径编码差异时，仅依据文件名允许匹配
                                    if not is_core_file:
                                        is_core_file = True
                                
                                if is_core_file:
                                    # 转换为相对路径
                                    try:
                                        if os.path.isabs(issue_path):
                                            issue['file'] = os.path.relpath(issue_path, project_path)
                                        else:
                                            issue['file'] = issue_path
                                    except:
                                        issue['file'] = issue_path
                                    issue['tool'] = 'bandit'
                                    bandit_issues.append(issue)
                            
                            self.logger.info(f"Bandit目录模式检测到 {len(bandit_issues)} 个安全问题（已过滤为核心文件）")
                        elif not bandit_result.get('success'):
                            self.logger.warning(f"Bandit目录分析失败: {bandit_result.get('error', '未知错误')}")
                    else:
                        # 如果没有目录模式，使用单文件模式
                        self.logger.info("Bandit使用单文件模式分析...")
                        async def analyze_bandit_file(file_path: str):
                            """分析单个文件的Bandit"""
                            rel_path = os.path.relpath(file_path, project_path)
                            try:
                                result = await self.bandit_tool.analyze(file_path)
                                issues = []
                                if result.get('success') and result.get('issues'):
                                    for issue in result['issues']:
                                        issue['file'] = rel_path
                                        issue['tool'] = 'bandit'
                                        issues.append(issue)
                                return issues
                            except Exception as e:
                                self.logger.warning(f"Bandit分析失败 {file_path}: {e}")
                                return []
                        
                        # 批量并行处理Bandit
                        max_workers = options.get("max_parallel_files", 10)
                        for i in range(0, len(analysis_files), max_workers):
                            batch = analysis_files[i:i + max_workers]
                            bandit_results = await asyncio.gather(*[analyze_bandit_file(f) for f in batch], return_exceptions=True)
                            for result in bandit_results:
                                if isinstance(result, Exception):
                                    continue
                                bandit_issues.extend(result)
                    
                    if len(bandit_issues) > 0:
                        self.logger.info(f"Bandit检测到 {len(bandit_issues)} 个安全问题")
                    else:
                        self.logger.info("Bandit未检测到安全问题")
                except Exception as e:
                    self.logger.warning(f"Bandit分析失败: {e}")
                    import traceback
                    self.logger.debug(traceback.format_exc())
            
            # Semgrep：对整个目录进行分析（更高效，方案B推荐方式）
            if options.get("enable_semgrep", True):
                if self.semgrep_tool:
                    self.logger.info("开始Semgrep目录分析（规则引擎检测Flask特定问题）...")
                    try:
                        semgrep_result = await self.semgrep_tool.analyze_directory(project_path)
                        if semgrep_result.get('success'):
                            issues_found = semgrep_result.get('issues', [])
                            if issues_found:
                                for issue in issues_found:
                                    # 转换为相对路径
                                    if 'file' in issue:
                                        issue['file'] = os.path.relpath(issue['file'], project_path) if os.path.isabs(issue['file']) else issue['file']
                                    issue['tool'] = 'semgrep'
                                    semgrep_issues.append(issue)
                                self.logger.info(f"Semgrep检测到 {len(semgrep_issues)} 个问题")
                            else:
                                self.logger.info(f"Semgrep执行成功但未检测到问题（可能Flask代码符合规则）")
                        else:
                            error_msg = semgrep_result.get('error', '未知错误')
                            self.logger.warning(f"Semgrep分析失败: {error_msg}")
                            # 记录更多调试信息
                            if 'stdout' in semgrep_result:
                                self.logger.debug(f"Semgrep stdout: {semgrep_result.get('stdout', '')[:500]}")
                            if 'stderr' in semgrep_result:
                                self.logger.debug(f"Semgrep stderr: {semgrep_result.get('stderr', '')[:500]}")
                    except Exception as e:
                        self.logger.warning(f"Semgrep分析失败: {e}")
                        import traceback
                        self.logger.debug(traceback.format_exc())
                else:
                    self.logger.warning("Semgrep工具未初始化，跳过Semgrep检测（可能未安装）")
            
            # Ruff：对整个目录进行分析（替代flake8，更快且功能更强）
            if options.get("enable_ruff", True):
                if self.ruff_tool:
                    self.logger.info("开始Ruff目录分析（快速代码质量检查）...")
                    try:
                        # 添加超时保护（最多5分钟）
                        try:
                            ruff_result = await asyncio.wait_for(
                                self.ruff_tool.analyze_directory(project_path),
                                timeout=300.0  # 5分钟超时
                            )
                        except asyncio.TimeoutError:
                            self.logger.warning("Ruff目录分析超时（5分钟），跳过Ruff检测")
                            ruff_result = {
                                'success': False,
                                'error': 'Ruff执行超时（5分钟）',
                                'issues': []
                            }
                        # 检查ruff_result是否为字典类型
                        if not isinstance(ruff_result, dict):
                            # 如果返回的是字符串，尝试解析为JSON
                            if isinstance(ruff_result, str):
                                try:
                                    import json
                                    ruff_result = json.loads(ruff_result)
                                    if not isinstance(ruff_result, dict):
                                        raise ValueError("解析后仍不是字典")
                                except (json.JSONDecodeError, ValueError):
                                    self.logger.warning(f"Ruff分析失败: 返回结果类型错误，期望dict，实际为{type(ruff_result).__name__}: {str(ruff_result)[:200]}")
                                    ruff_result = {
                                        'success': False,
                                        'error': f'返回结果类型错误: {type(ruff_result).__name__}',
                                        'issues': []
                                    }
                            else:
                                self.logger.warning(f"Ruff分析失败: 返回结果类型错误，期望dict，实际为{type(ruff_result).__name__}: {str(ruff_result)[:200]}")
                            ruff_result = {
                                'success': False,
                                'error': f'返回结果类型错误: {type(ruff_result).__name__}',
                                'issues': []
                            }
                        
                        if ruff_result.get('success') and ruff_result.get('issues'):
                            for issue in ruff_result['issues']:
                                # 转换为相对路径
                                if 'file' in issue:
                                    issue['file'] = os.path.relpath(issue['file'], project_path) if os.path.isabs(issue['file']) else issue['file']
                                issue['tool'] = 'ruff'
                                ruff_issues.append(issue)
                            self.logger.info(f"Ruff检测到 {len(ruff_issues)} 个问题")
                        elif not ruff_result.get('success'):
                            error_msg = ruff_result.get('error', '未知错误') if isinstance(ruff_result, dict) else str(ruff_result)
                            self.logger.warning(f"Ruff分析失败: {error_msg}")
                    except Exception as e:
                        self.logger.warning(f"Ruff分析失败: {e}")
                        import traceback
                        self.logger.debug(traceback.format_exc())
                else:
                    self.logger.warning("Ruff工具未初始化，跳过Ruff检测（可能未安装）")
            
            # 执行AI多语言分析
            ai_issues = []
            if other_language_files and self.ai_analyzer:
                # AI分析可能需要更长时间，设置合理的上限
                max_ai_files = options.get("max_files_for_ai_analysis", 20)
                ai_files_to_analyze = other_language_files[:max_ai_files] if len(other_language_files) > max_ai_files else other_language_files
                self.logger.info(f"开始AI分析 {len(ai_files_to_analyze)} 个其他语言文件（共 {len(other_language_files)} 个，已过滤核心文件）...")
                for other_file in ai_files_to_analyze:
                    try:
                        # other_file 已经是绝对路径
                        rel_path = os.path.relpath(other_file, project_path)
                        result = await self.ai_analyzer.analyze_file(other_file, project_path)
                        
                        if result and result.issues:
                            for issue in result.issues:
                                ai_issues.append({
                                    'file': rel_path,
                                    'line': issue.line_number,
                                    'column': issue.column,
                                    'type': issue.category,
                                    'severity': issue.severity,
                                    'message': issue.message,
                                    'suggestion': issue.suggestion,
                                    'tool': 'ai_analyzer',
                                    'language': issue.language,
                                    'confidence': issue.confidence
                                })
                                
                    except Exception as e:
                        self.logger.warning(f"AI分析文件失败 {other_file}: {e}")
                        continue
            
            # 合并所有问题（方案B标准工具集，Ruff替代Flake8）
            all_issues = pylint_issues + mypy_issues + semgrep_issues + ruff_issues + bandit_issues + ai_issues
            
            # 可选：如果项目包含 tests/test 目录，则运行项目测试并将失败作为缺陷输出
            try:
                test_issues = await self._maybe_run_project_tests(project_path)
                if test_issues:
                    self.logger.info(f"项目测试发现 {len(test_issues)} 个失败用例，纳入缺陷列表")
                    all_issues.extend(test_issues)
            except Exception as e:
                self.logger.warning(f"运行项目测试时发生异常，跳过测试集成: {e}")
            
            self.logger.info(f"=== 静态分析完成统计 ===")
            self.logger.info(f"Pylint: {len(pylint_issues)} 个问题")
            self.logger.info(f"Mypy: {len(mypy_issues)} 个问题")
            self.logger.info(f"Semgrep: {len(semgrep_issues)} 个问题")
            self.logger.info(f"Ruff: {len(ruff_issues)} 个问题")
            self.logger.info(f"Bandit: {len(bandit_issues)} 个问题")
            self.logger.info(f"AI分析: {len(ai_issues)} 个问题")
            self.logger.info(f"总计: {len(all_issues)} 个问题")
            
            # ========== 步骤3: LLM智能误报过滤 ==========
            # 记录过滤前的原始问题数量（包括所有工具检测到的问题）
            original_issue_count_before_filter = len(all_issues)
            
            if options.get("enable_llm_filter", True):
                try:
                    from tools.llm_filter import get_false_positive_filter
                    
                    # 尝试导入配置，优先使用项目配置
                    try:
                        from config.settings import settings as project_settings
                        filter_config = getattr(project_settings, 'LLM_FILTER', {})
                    except ImportError:
                        # 如果导入失败，使用默认配置
                        self.logger.warning("无法导入config.settings，使用默认LLM过滤配置")
                        filter_config = {
                            "enabled": True,
                            "confidence_threshold": 0.7,
                            "batch_size": 20,
                            "model": "deepseek-chat",
                            "cache_enabled": True,
                            "max_issues_to_filter": 100
                        }
                    
                    # 检查是否启用LLM过滤
                    if filter_config.get("enabled", True):
                        self.logger.info(f"开始LLM智能误报过滤（原始问题数: {original_issue_count_before_filter}）...")
                        
                        # 初始化过滤器
                        llm_filter = get_false_positive_filter(filter_config)
                        
                        # 限制过滤的问题数量（控制成本）
                        max_issues_to_filter = filter_config.get("max_issues_to_filter", 100)
                        issues_to_filter = all_issues[:max_issues_to_filter] if len(all_issues) > max_issues_to_filter else all_issues
                        issues_not_filtered = all_issues[max_issues_to_filter:] if len(all_issues) > max_issues_to_filter else []
                        
                        if issues_to_filter:
                            # 创建源码提供函数
                            def get_source_code(file_path: str) -> str:
                                """获取文件的源码"""
                                try:
                                    # file_path可能是相对路径，需要转换为绝对路径
                                    abs_path = os.path.join(project_path, file_path) if not os.path.isabs(file_path) else file_path
                                    if os.path.exists(abs_path):
                                        with open(abs_path, 'r', encoding='utf-8', errors='ignore') as f:
                                            # 读取文件并提取相关行号附近的代码
                                            lines = f.readlines()
                                            # 对于每个问题，提取前后各10行作为上下文
                                            relevant_lines = []
                                            for issue in issues_to_filter:
                                                if issue.get('file') == file_path:
                                                    line_num = issue.get('line', 1)
                                                    start = max(0, line_num - 10)
                                                    end = min(len(lines), line_num + 10)
                                                    relevant_lines.extend(range(start, end))
                                            
                                            # 去重并排序
                                            relevant_lines = sorted(set(relevant_lines))
                                            
                                            # 如果相关行太多，只返回文件的前500行
                                            if len(relevant_lines) > 500:
                                                return ''.join(lines[:500])
                                            else:
                                                return ''.join([lines[i] if i < len(lines) else '' for i in relevant_lines])
                                    return ""
                                except Exception as e:
                                    self.logger.warning(f"读取源码失败 {file_path}: {e}")
                                    return ""
                            
                            # 执行批量过滤
                            filtered_issues = await llm_filter.filter_issues_batch(
                                issues_to_filter,
                                get_source_code
                            )
                            
                            # 合并过滤后的问题和未过滤的问题
                            all_issues = filtered_issues + issues_not_filtered
                            
                            filtered_count = len(issues_to_filter) - len(filtered_issues)
                            self.logger.info(f"LLM误报过滤完成: 原始问题 {len(issues_to_filter)} 个, "
                                           f"过滤后保留 {len(filtered_issues)} 个, "
                                           f"过滤掉 {filtered_count} 个误报")
                        else:
                            self.logger.info("无需过滤的问题")
                    else:
                        self.logger.info("LLM误报过滤已禁用（配置中disabled）")
                        
                except ImportError as e:
                    self.logger.warning(f"LLM过滤器导入失败，跳过误报过滤: {e}")
                except Exception as e:
                    self.logger.warning(f"LLM误报过滤失败，保留所有原始问题: {e}")
                    import traceback
                    self.logger.debug(traceback.format_exc())
            else:
                self.logger.info("LLM误报过滤已禁用（options中enable_llm_filter=False）")
            
            # 代码质量分析功能已移除，不再添加代码质量分析中的问题
            code_quality_issues = []
            
            # 生成AI分析摘要（如果有初步分析结果且启用AI分析）
            ai_summary = None
            if options.get("enable_ai_analysis", True) and preliminary_analysis:
                try:
                    from agents.code_analysis_agent.agent import CodeAnalysisAgent
                    code_analysis_agent = CodeAnalysisAgent({
                        "enable_ai_analysis": True,
                        "analysis_depth": "comprehensive"
                    })
                    ai_summary = await code_analysis_agent.ai_service.generate_project_summary({
                        'project_structure': project_structure,
                        'code_quality': code_quality,
                        'dependencies': dependencies
                    })
                except Exception as e:
                    self.logger.warning(f"AI分析失败: {e}")
                    ai_summary = {
                        'success': False,
                        'error': str(e),
                        'summary': 'AI分析服务暂时不可用'
                    }
            
            # 计算统计信息
            issues_by_severity = {}
            issues_by_type = {}
            issues_by_tool = {}
            
            # 计算过滤后的统计（排除代码质量分析的问题，因为它们是在过滤后添加的）
            filtered_issue_count = len(all_issues) - len(code_quality_issues)
            original_issue_count_after_code_quality = original_issue_count_before_filter
            
            llm_filter_stats = {
                "enabled": False,
                "original_count": original_issue_count_before_filter,
                "filtered_count": filtered_issue_count,  # 只统计过滤后的问题（不包括代码质量分析）
                "removed_count": 0,
                "code_quality_issues_count": len(code_quality_issues)  # 代码质量分析问题数量
            }
            
            for issue in all_issues:
                severity = issue.get('severity', 'info')
                issue_type = issue.get('type', 'unknown')
                tool = issue.get('tool', 'unknown')
                
                issues_by_severity[severity] = issues_by_severity.get(severity, 0) + 1
                issues_by_type[issue_type] = issues_by_type.get(issue_type, 0) + 1
                issues_by_tool[tool] = issues_by_tool.get(tool, 0) + 1
            
            # 更新LLM过滤统计（只考虑过滤前后的工具检测问题，不包括代码质量分析问题）
            if original_issue_count_before_filter > filtered_issue_count:
                llm_filter_stats["enabled"] = True
                llm_filter_stats["removed_count"] = original_issue_count_before_filter - filtered_issue_count
            
            # 可配置的问题数量限制（用于性能优化，避免返回过多数据）
            max_issues_to_return = options.get("max_issues_to_return", 1000)  # 默认1000，可根据需要调整
            
            return {
                "success": True,
                "analysis_type": "enhanced_static_analysis",
                "project_path": project_path,
                "files_analyzed": len(python_files) + len(other_language_files),
                "python_files_analyzed": len(python_files),
                "other_language_files_analyzed": len(other_language_files),
                "issues_found": len(all_issues),
                "issues": all_issues[:max_issues_to_return] if len(all_issues) > max_issues_to_return else all_issues,
                "issues_truncated": len(all_issues) > max_issues_to_return,  # 标记是否截断
                "total_issues_count": len(all_issues),  # 实际总问题数
                "project_structure": project_structure,  # 来自初步分析
                "code_quality": code_quality,  # 来自初步分析
                "dependencies": dependencies,  # 来自初步分析
                "ai_summary": ai_summary,
                "file_filtering": {
                    "core_files_count": len(core_files),
                    "excluded_files_count": len(excluded_files),
                    "filter_statistics": filter_statistics
                },
                "multi_language_analysis": {
                    "python_issues": len(pylint_issues) + len(mypy_issues),
                    "semgrep_issues": len(semgrep_issues),
                    "ruff_issues": len(ruff_issues),
                    "ai_issues": len(ai_issues),
                    "supported_languages": sorted(list(set([issue.get('language', 'unknown') for issue in ai_issues])))  # 转换为list并排序
                },
                "tool_coverage": {
                    "pylint": len(pylint_issues),
                    "mypy": len(mypy_issues),
                    "semgrep": len(semgrep_issues),
                    "ruff": len(ruff_issues),
                    "bandit": len(bandit_issues),
                    "ai_analyzer": len(ai_issues)
                },
                "statistics": {
                    "issues_by_severity": issues_by_severity,
                    "issues_by_type": issues_by_type,
                    "issues_by_tool": issues_by_tool,
                    "total_files": project_structure.get('total_files', 0) if project_structure else 0,
                    "total_lines": project_structure.get('total_lines', 0) if project_structure else 0,
                    "average_complexity": code_quality.get('average_complexity', 0) if code_quality else 0,
                    "maintainability_score": code_quality.get('maintainability_score', 0) if code_quality else 0
                },
                "summary": {
                    "error_count": issues_by_severity.get('error', 0),
                    "warning_count": issues_by_severity.get('warning', 0),
                    "info_count": issues_by_severity.get('info', 0)
                },
                "llm_filter": llm_filter_stats
            }
            
        except Exception as e:
            self.logger.error(f"增强静态分析失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _perform_basic_project_analysis(self, project_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """执行基础项目分析（回退方案）"""
        try:
            # 扫描项目文件（应用过滤规则）
            files_by_language = self.scan_project_files(project_path)
            
            if not files_by_language:
                return {
                    "success": False,
                    "error": "未找到支持的代码文件",
                    "project_path": project_path,
                    "total_issues": 0,
                    "issues": [],
                    "summary": {"error_count": 0, "warning_count": 0, "info_count": 0}
                }
            
            # 应用文件过滤和采样
            filtered_files = self._filter_and_sample_files(files_by_language)
            
            # 并行分析不同语言的文件
            all_results = []
            total_files = sum(len(files) for files in filtered_files.values())
            
            if total_files > self.project_config["max_files_per_project"]:
                return {
                    "success": False,
                    "error": f"项目文件过多 ({total_files} > {self.project_config['max_files_per_project']})",
                    "project_path": project_path,
                    "total_issues": 0,
                    "issues": [],
                    "summary": {"error_count": 0, "warning_count": 0, "info_count": 0}
                }
            
            # 按语言分组分析
            for language, files in filtered_files.items():
                self.logger.info(f"分析 {language} 文件: {len(files)} 个")
                
                # 限制每个语言的文件数量
                files_to_analyze = files[:30]  # 每个语言最多分析30个文件
                
                for file_path in files_to_analyze:
                    try:
                        # 分析单个文件
                        file_result = await self._detect_file_bugs(file_path, options)
                        if file_result:
                            all_results.append(file_result)
                    except Exception as e:
                        self.logger.warning(f"分析文件失败 {file_path}: {e}")
            
            # 合并所有结果
            combined_result = self._combine_project_results(all_results, project_path)
            
            self.logger.info(f"基础项目分析完成，共分析 {len(all_results)} 个文件")
            return {
                "success": True,
                "analysis_type": "basic_static_analysis",
                **combined_result
            }
            
        except Exception as e:
            self.logger.error(f"基础项目分析失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "project_path": project_path,
                "total_issues": 0,
                "issues": [],
                "summary": {"error_count": 0, "warning_count": 0, "info_count": 0}
            }
    
    def _combine_project_results(self, results: List[Dict[str, Any]], project_path: str) -> Dict[str, Any]:
        """合并项目分析结果"""
        try:
            all_issues = []
            total_files = len(results)
            analysis_time = 0
            detection_tools = set()
            
            for result in results:
                if result and "issues" in result:
                    all_issues.extend(result["issues"])
                    analysis_time += result.get("analysis_time", 0)
                    detection_tools.update(result.get("detection_tools", []))
            
            # 按严重性排序
            all_issues.sort(key=lambda x: self.severity_levels.get(x.get("severity", "info"), {}).get("level", 3))
            
            combined_result = {
                "project_path": project_path,
                "total_files": total_files,
                "total_issues": len(all_issues),
                "issues": all_issues,
                "detection_tools": list(detection_tools),
                "analysis_time": analysis_time,
                "summary": {
                    "error_count": sum(1 for issue in all_issues if issue.get("severity") == "error"),
                    "warning_count": sum(1 for issue in all_issues if issue.get("severity") == "warning"),
                    "info_count": sum(1 for issue in all_issues if issue.get("severity") == "info")
                },
                "languages_detected": list(set(issue.get("language", "unknown") for issue in all_issues))
            }
            
            return combined_result
            
        except Exception as e:
            self.logger.error(f"合并项目结果失败: {e}")
            return {
                "project_path": project_path,
                "total_files": 0,
                "total_issues": 0,
                "issues": [],
                "error": str(e)
            }
    
    async def _maybe_run_project_tests(self, project_path: str) -> List[Dict[str, Any]]:
        """如果项目包含 tests/test 目录，则尝试运行测试并将失败转换为缺陷"""
        try:
            root = Path(project_path)
            candidates = [root / "tests", root / "test"]
            test_files: List[Path] = []
            
            for d in candidates:
                if d.exists() and d.is_dir():
                    for py in d.rglob("*.py"):
                        name = py.name
                        if name.startswith("test_") or name.endswith("_test.py"):
                            test_files.append(py)
            
            if not test_files:
                return []
            
            # 优先在Docker中运行测试，避免本地环境差异
            stdout = ""
            stderr = ""
            success = False
            if getattr(self, "use_docker", False) and getattr(self, "docker_runner", None):
                try:
                    await self.docker_runner.ensure_image_exists()
                    result = await self.docker_runner.run_tests(Path(project_path))
                    success = bool(result.get("success")) and int(result.get("returncode", result.get("code", 1) or 1)) == 0
                    stdout = result.get("stdout", "") or ""
                    stderr = result.get("stderr", "") or ""
                except Exception as e:
                    self.logger.warning(f"Docker测试运行失败，回退到本地运行: {e}")
            
            if not success and (not getattr(self, "use_docker", False) or not getattr(self, "docker_runner", None)):
                try:
                    proc = await asyncio.create_subprocess_shell(
                        "python -m pytest -v",
                        cwd=project_path,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    out, err = await proc.communicate()
                    stdout = out.decode(errors="ignore") if out else ""
                    stderr = err.decode(errors="ignore") if err else ""
                    success = (proc.returncode == 0)
                except Exception as e:
                    stderr = f"本地运行pytest失败: {e}"
                    success = False
            
            if success:
                return []
            
            # 解析失败摘要（尽量抓取关键信息）
            lines = (stdout or "").splitlines() + (stderr or "").splitlines()
            summaries: List[str] = []
            for ln in lines:
                s = ln.strip()
                if s.startswith("FAILED") or s.startswith("ERROR") or s.startswith("E   ") or s.startswith("F   "):
                    summaries.append(s)
            # 限制信息长度
            if summaries:
                message_block = "\n".join(summaries[:50])
            else:
                clip_src = stdout if stdout else stderr
                message_block = (clip_src[-2000:] if clip_src else "测试失败但没有可用输出")
            
            # 输出为一个聚合的“测试失败”缺陷；前端像普通缺陷一样展示
            return [{
                "file": "tests/",
                "line": 1,
                "column": 0,
                "type": "test_failure",
                "severity": "error",
                "message": "项目单元测试失败",
                "details": message_block,
                "tool": "pytest"
            }]
        
        except Exception as e:
            self.logger.warning(f"测试检测与执行失败: {e}")
            return []
    
    async def _enhance_detection_results(self, detection_results: Dict[str, Any], file_path: str) -> Dict[str, Any]:
        """增强检测结果，添加代码片段和详细说明"""
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
            file_lines = file_content.split('\n')
            
            enhanced_issues = []
            for issue in detection_results.get("issues", []):
                enhanced_issue = await self._enhance_single_issue(issue, file_lines, file_path)
                enhanced_issues.append(enhanced_issue)
            
            # 按严重性排序
            enhanced_issues.sort(key=lambda x: self.severity_levels.get(x.get("severity", "info"), {}).get("level", 3))
            
            # 更新检测结果
            detection_results["issues"] = enhanced_issues
            detection_results["enhanced"] = True
            
            return detection_results
            
        except Exception as e:
            self.logger.error(f"增强检测结果失败: {e}")
            return detection_results
    
    async def _enhance_single_issue(self, issue: Dict[str, Any], file_lines: List[str], file_path: str) -> Dict[str, Any]:
        """增强单个缺陷信息"""
        try:
            line_number = issue.get("line", 1)
            column = issue.get("column", 0)
            issue_type = issue.get("type", "unknown")
            severity = issue.get("severity", "info")
            
            # 获取代码片段（前后各3行）
            start_line = max(1, line_number - 3)
            end_line = min(len(file_lines), line_number + 3)
            
            code_snippet = []
            for i in range(start_line - 1, end_line):
                line_content = file_lines[i] if i < len(file_lines) else ""
                code_snippet.append({
                    "line_number": i + 1,
                    "content": line_content,
                    "is_issue_line": i + 1 == line_number
                })
            
            # 获取详细说明
            detailed_description = await self._get_detailed_description(issue_type, issue)
            
            # 获取修复建议
            fix_suggestions = await self._get_fix_suggestions(issue_type, issue)
            
            # 增强的缺陷信息
            enhanced_issue = {
                **issue,
                "code_snippet": code_snippet,
                "detailed_description": detailed_description,
                "fix_suggestions": fix_suggestions,
                "severity_info": self.severity_levels.get(severity, {}),
                "file_path": file_path,
                "enhanced": True
            }
            
            return enhanced_issue
            
        except Exception as e:
            self.logger.error(f"增强单个缺陷信息失败: {e}")
            return issue
    
    async def _get_detailed_description(self, issue_type: str, issue: Dict[str, Any]) -> str:
        """获取详细的缺陷说明"""
        descriptions = {
            "unused_import": "未使用的导入语句会占用内存空间并可能影响代码的可读性。建议删除未使用的导入。",
            "hardcoded_secrets": "硬编码的密钥、密码或API密钥存在安全风险，可能被恶意用户获取。建议使用环境变量或配置文件。",
            "unsafe_eval": "使用eval()函数执行用户输入存在代码注入风险，可能导致系统被攻击。建议使用更安全的方法。",
            "missing_type_hints": "缺少类型提示会影响代码的可读性和IDE的智能提示功能。建议添加类型注解。",
            "long_functions": "函数过长会降低代码的可读性和可维护性。建议将长函数拆分为多个小函数。",
            "duplicate_code": "重复的代码会增加维护成本，容易产生不一致的bug。建议提取公共函数。",
            "bad_exception_handling": "不当的异常处理可能隐藏错误或导致程序崩溃。建议使用具体的异常类型。",
            "global_variables": "全局变量会增加代码的复杂性和测试难度。建议使用函数参数或类属性。",
            "magic_numbers": "魔法数字会降低代码的可读性。建议使用有意义的常量名称。",
            "unsafe_file_operations": "不安全的文件操作可能导致路径遍历攻击。建议验证文件路径。",
            "missing_docstrings": "缺少文档字符串会影响代码的可读性。建议为函数和类添加文档字符串。",
            "bad_naming": "不规范的命名会降低代码的可读性。建议使用有意义的变量和函数名。",
            "unhandled_exceptions": "未处理的异常可能导致程序崩溃。建议添加适当的异常处理。",
            "deep_nesting": "过深的嵌套会降低代码的可读性。建议使用早期返回或提取函数。",
            "insecure_random": "不安全的随机数生成可能导致安全漏洞。建议使用cryptographically secure random。",
            "memory_leaks": "内存泄漏会导致程序占用过多内存。建议及时释放不再使用的资源。",
            "missing_input_validation": "缺少输入验证可能导致安全漏洞。建议验证所有用户输入。",
            "bad_formatting": "代码格式不规范会影响可读性。建议使用代码格式化工具。",
            "dead_code": "死代码会增加维护成本。建议删除未使用的代码。",
            "unused_variables": "未使用的变量会占用内存空间。建议删除未使用的变量。"
        }
        
        return descriptions.get(issue_type, "这是一个代码质量问题，建议进行相应的修复。")
    
    async def _get_fix_suggestions(self, issue_type: str, issue: Dict[str, Any]) -> List[str]:
        """获取修复建议"""
        suggestions = {
            "unused_import": [
                "删除未使用的导入语句",
                "检查是否有其他文件需要这个导入",
                "使用IDE的自动清理功能"
            ],
            "hardcoded_secrets": [
                "使用环境变量存储敏感信息",
                "使用配置文件（不提交到版本控制）",
                "使用密钥管理服务"
            ],
            "unsafe_eval": [
                "使用ast.literal_eval()替代eval()",
                "使用json.loads()解析JSON数据",
                "使用专门的解析库"
            ],
            "missing_type_hints": [
                "为函数参数添加类型注解",
                "为返回值添加类型注解",
                "使用typing模块的类型提示"
            ],
            "long_functions": [
                "将函数拆分为多个小函数",
                "提取公共逻辑到单独的函数",
                "使用类来组织相关功能"
            ],
            "duplicate_code": [
                "提取公共函数",
                "使用继承或组合",
                "创建工具函数库"
            ],
            "bad_exception_handling": [
                "使用具体的异常类型",
                "添加适当的错误日志",
                "提供有意义的错误信息"
            ],
            "global_variables": [
                "使用函数参数传递数据",
                "使用类属性",
                "使用单例模式"
            ],
            "magic_numbers": [
                "定义有意义的常量",
                "使用枚举类型",
                "添加注释说明"
            ],
            "unsafe_file_operations": [
                "验证文件路径",
                "使用pathlib.Path",
                "检查文件权限"
            ],
            "missing_docstrings": [
                "为函数添加文档字符串",
                "为类添加文档字符串",
                "使用docstring格式规范"
            ],
            "bad_naming": [
                "使用有意义的变量名",
                "遵循命名约定",
                "避免缩写和单字母变量"
            ],
            "unhandled_exceptions": [
                "添加try-except块",
                "使用finally块清理资源",
                "记录异常信息"
            ],
            "deep_nesting": [
                "使用早期返回",
                "提取嵌套逻辑到函数",
                "使用guard clauses"
            ],
            "insecure_random": [
                "使用secrets模块",
                "使用random.SystemRandom()",
                "使用cryptographically secure random"
            ],
            "memory_leaks": [
                "及时关闭文件句柄",
                "使用with语句",
                "清理不再使用的对象"
            ],
            "missing_input_validation": [
                "验证输入类型",
                "检查输入范围",
                "使用验证库"
            ],
            "bad_formatting": [
                "使用black格式化工具",
                "使用autopep8",
                "配置IDE自动格式化"
            ],
            "dead_code": [
                "删除未使用的代码",
                "使用代码分析工具",
                "定期代码审查"
            ],
            "unused_variables": [
                "删除未使用的变量",
                "使用下划线前缀",
                "检查变量作用域"
            ]
        }
        
        return suggestions.get(issue_type, ["建议根据具体情况进行修复"])
    
    async def generate_downloadable_report(self, detection_results: Dict[str, Any], file_path: str) -> str:
        """生成可下载的检测报告"""
        try:
            # 创建报告目录
            report_dir = Path("reports")
            report_dir.mkdir(exist_ok=True)
            
            # 生成报告文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"bug_detection_report_{timestamp}.json"
            report_path = report_dir / filename
            
            # 生成报告内容
            report_data = {
                "report_info": {
                    "generated_at": datetime.now().isoformat(),
                    "file_path": file_path,
                    "total_issues": detection_results.get("total_issues", 0),
                    "summary": detection_results.get("summary", {}),
                    "detection_tools": detection_results.get("detection_tools", [])
                },
                "issues": detection_results.get("issues", []),
                "statistics": {
                    "by_severity": self._get_issues_by_severity(detection_results.get("issues", [])),
                    "by_type": self._get_issues_by_type(detection_results.get("issues", [])),
                    "by_category": self._get_issues_by_category(detection_results.get("issues", []))
                }
            }
            
            # 保存报告
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"检测报告已生成: {report_path}")
            return str(report_path)
            
        except Exception as e:
            self.logger.error(f"生成检测报告失败: {e}")
            return None
    
    def _get_issues_by_severity(self, issues: List[Dict[str, Any]]) -> Dict[str, int]:
        """按严重性统计问题"""
        severity_count = {}
        for issue in issues:
            severity = issue.get("severity", "info")
            severity_count[severity] = severity_count.get(severity, 0) + 1
        return severity_count
    
    def _get_issues_by_type(self, issues: List[Dict[str, Any]]) -> Dict[str, int]:
        """按类型统计问题"""
        type_count = {}
        for issue in issues:
            issue_type = issue.get("type", "unknown")
            type_count[issue_type] = type_count.get(issue_type, 0) + 1
        return type_count
    
    def _get_issues_by_category(self, issues: List[Dict[str, Any]]) -> Dict[str, int]:
        """按类别统计问题"""
        category_count = {}
        for issue in issues:
            rule_id = issue.get("rule", "unknown")
            category = self._get_rule_category(rule_id)
            category_count[category] = category_count.get(category, 0) + 1
        return category_count
    
    def _load_tasks_state(self):
        """加载任务状态"""
        try:
            if self.tasks_file.exists():
                with open(self.tasks_file, 'r', encoding='utf-8') as f:
                    self.tasks = json.load(f)
                self.logger.info(f"加载了 {len(self.tasks)} 个任务状态")
            else:
                self.tasks = {}
                self.logger.info("没有找到任务状态文件，初始化为空")
        except Exception as e:
            self.logger.error(f"加载任务状态失败: {e}")
            self.tasks = {}
    
    def _save_tasks_state(self):
        """保存任务状态"""
        try:
            # 确保目录存在
            self.tasks_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 将任务数据中的set对象转换为list，确保JSON可序列化
            serializable_tasks = self._make_json_serializable(self.tasks)
            
            with open(self.tasks_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_tasks, f, ensure_ascii=False, indent=2)
            self.logger.debug(f"保存了 {len(self.tasks)} 个任务状态")
        except Exception as e:
            self.logger.error(f"保存任务状态失败: {e}")
            import traceback
            self.logger.debug(traceback.format_exc())
    
    def _make_json_serializable(self, obj: Any) -> Any:
        """递归地将对象中的set转换为list，确保JSON可序列化"""
        if isinstance(obj, dict):
            return {key: self._make_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        elif isinstance(obj, set):
            return sorted(list(obj))  # 转换为list并排序
        elif isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        else:
            # 对于其他类型，尝试转换为字符串
            try:
                return str(obj)
            except:
                return None
    
    async def generate_ai_report(self, detection_results: Dict[str, Any], filename: str) -> str:
        """生成AI静态检测报告"""
        try:
            from api.deepseek_config import deepseek_config
            import aiohttp
            
            if not deepseek_config.is_configured():
                self.logger.warning("DeepSeek API未配置，使用基础报告")
                return self._generate_fallback_report(detection_results, filename)
            
            prompt = self._build_static_analysis_prompt(detection_results, filename)
            
            self.logger.info("🤖 正在生成AI静态检测报告...")
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=180.0)) as client:
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
                
                if response.status == 200:
                    result = await response.json()
                    ai_content = result["choices"][0]["message"]["content"]
                    self.logger.info("✅ AI静态检测报告生成成功")
                    return ai_content
                else:
                    self.logger.warning(f"❌ AI API调用失败: {response.status}")
                    return self._generate_fallback_report(detection_results, filename)
                    
        except Exception as e:
            self.logger.error(f"❌ AI报告生成异常: {e}")
            return self._generate_fallback_report(detection_results, filename)
    
    def _build_static_analysis_prompt(self, detection_results: Dict[str, Any], filename: str) -> str:
        """构建静态分析提示词"""
        summary = detection_results.get("summary", {})
        statistics = detection_results.get("statistics", {})
        
        prompt = f"""请分析以下静态检测结果，生成一份详细的自然语言报告：

## 项目信息
- 文件名: {filename}
- 检测时间: {datetime.now().isoformat()}
- 分析类型: {detection_results.get('analysis_type', 'unknown')}
- 分析文件数: {detection_results.get('files_analyzed', 0)}

## 检测统计
- 总问题数: {summary.get('total_issues', 0)}
- 严重问题: {summary.get('error_count', 0)}
- 警告问题: {summary.get('warning_count', 0)}
- 信息问题: {summary.get('info_count', 0)}

## 详细统计
- 总文件数: {statistics.get('total_files', 0)}
- 总代码行数: {statistics.get('total_lines', 0)}
- 平均复杂度: {statistics.get('average_complexity', 0)}
- 可维护性评分: {statistics.get('maintainability_score', 0)}

## 问题分布
"""
        
        # 添加问题严重程度分布
        issues_by_severity = statistics.get("issues_by_severity", {})
        if issues_by_severity:
            prompt += "\n### 问题严重程度分布:\n"
            for severity, count in issues_by_severity.items():
                prompt += f"- {severity}: {count}个\n"
        
        # 添加分析工具统计
        issues_by_tool = statistics.get("issues_by_tool", {})
        if issues_by_tool:
            prompt += "\n### 分析工具统计:\n"
            for tool, count in issues_by_tool.items():
                prompt += f"- {tool}: {count}个问题\n"
        
        # 添加主要问题
        issues = detection_results.get("issues", [])
        if issues:
            prompt += "\n### 主要问题:\n"
            for i, issue in enumerate(issues[:10], 1):  # 只显示前10个问题
                tool = issue.get('tool', 'unknown')
                prompt += f"{i}. [{tool}] {issue.get('file', 'N/A')}: {issue.get('message', 'N/A')} [{issue.get('severity', 'info')}]\n"
        
        # 添加项目结构信息
        project_structure = detection_results.get("project_structure", {})
        if project_structure:
            prompt += f"\n### 项目结构:\n"
            prompt += f"- 项目类型: {project_structure.get('project_type', 'unknown')}\n"
            prompt += f"- 主要语言: {project_structure.get('primary_language', 'unknown')}\n"
            prompt += f"- 框架: {project_structure.get('framework', 'unknown')}\n"
        
        # 添加多语言分析信息
        multi_lang = detection_results.get("multi_language_analysis", {})
        if multi_lang:
            prompt += f"\n### 多语言分析:\n"
            prompt += f"- Python文件分析: {detection_results.get('python_files_analyzed', 0)}个\n"
            prompt += f"- 其他语言文件分析: {detection_results.get('other_language_files_analyzed', 0)}个\n"
            prompt += f"- Python问题: {multi_lang.get('python_issues', 0)}个\n"
            prompt += f"- AI分析问题: {multi_lang.get('ai_issues', 0)}个\n"
            supported_langs = multi_lang.get('supported_languages', [])
            if supported_langs:
                prompt += f"- 支持的语言: {', '.join(supported_langs)}\n"
        
        # 添加AI分析摘要
        ai_summary = detection_results.get("ai_summary", {})
        if ai_summary and ai_summary.get('success'):
            prompt += f"\n### AI分析摘要:\n{ai_summary.get('summary', 'N/A')[:500]}...\n"
        
        prompt += """
请生成一份详细的自然语言分析报告，包括：
1. 项目概述
2. 问题分析
3. 风险评估
4. 改进建议
5. 总结

报告应该专业、详细且易于理解。"""
        
        return prompt
    
    def _generate_fallback_report(self, detection_results: Dict[str, Any], filename: str) -> str:
        """生成基础报告（当AI API不可用时）"""
        summary = detection_results.get("summary", {})
        statistics = detection_results.get("statistics", {})
        
        report = f"""# 静态检测报告

## 项目概述
- **项目名称**: {filename}
- **检测时间**: {datetime.now().isoformat()}
- **分析类型**: {detection_results.get('analysis_type', 'unknown')}
- **分析文件数**: {detection_results.get('files_analyzed', 0)}

## 检测结果摘要
- **总问题数**: {summary.get('total_issues', 0)}
- **严重问题**: {summary.get('error_count', 0)}
- **警告问题**: {summary.get('warning_count', 0)}
- **信息问题**: {summary.get('info_count', 0)}

## 详细统计
- **总文件数**: {statistics.get('total_files', 0)}
- **总代码行数**: {statistics.get('total_lines', 0)}
- **平均复杂度**: {statistics.get('average_complexity', 0)}
- **可维护性评分**: {statistics.get('maintainability_score', 0)}

## 问题分析
"""
        
        if summary.get('error_count', 0) > 0:
            report += "⚠️ **发现严重问题**，需要立即处理\n"
        if summary.get('warning_count', 0) > 0:
            report += "⚠️ **发现警告问题**，建议及时处理\n"
        if summary.get('info_count', 0) > 0:
            report += "ℹ️ **发现信息问题**，可选择性处理\n"
        
        if summary.get('total_issues', 0) == 0:
            report += "✅ **未发现明显问题**\n"
        
        # 添加技术建议
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
        if 'ruff' in issues_by_tool and issues_by_tool['ruff'] > 0:
            report += "- 🚀 **Ruff发现问题**，建议改进代码风格和规范\n"
        
        report += "\n## 总结\n"
        if summary.get('error_count', 0) > 0:
            report += "项目存在严重问题，需要立即修复。建议优先处理严重问题，然后逐步改进代码质量。"
        elif summary.get('warning_count', 0) > 0:
            report += "项目存在一些警告问题，建议及时处理。重点关注代码质量和可维护性。"
        else:
            report += "项目整体质量良好，未发现严重问题。建议继续保持代码质量，定期进行代码审查。"
        
        return report
    
    async def _simple_project_structure_analysis(self, project_path: str) -> Dict[str, Any]:
        """简化的项目结构分析"""
        try:
            structure = {
                "project_type": "unknown",
                "main_files": [],
                "config_files": [],
                "test_files": [],
                "total_files": 0
            }
            
            # 扫描项目文件
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    structure["total_files"] += 1
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, project_path)
                    
                    # 识别主要文件
                    if file in ['app.py', 'main.py', 'application.py', 'server.py']:
                        structure["main_files"].append(rel_path)
                        if 'flask' in file.lower() or 'app' in file.lower():
                            structure["project_type"] = "flask"
                    
                    # 识别配置文件
                    if file.endswith(('.json', '.yaml', '.yml', '.ini', '.cfg', '.conf')):
                        structure["config_files"].append(rel_path)
                    
                    # 识别测试文件
                    if 'test' in file.lower() or file.startswith('test_'):
                        structure["test_files"].append(rel_path)
            
            return structure
        except Exception as e:
            return {"error": str(e)}
    
    async def _simple_code_quality_analysis(self, project_path: str) -> Dict[str, Any]:
        """简化的代码质量分析"""
        try:
            quality = {
                "total_files": 0,
                "total_lines": 0,
                "python_files": 0,
                "issues": []
            }
            
            # 扫描Python文件
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    if file.endswith('.py'):
                        quality["python_files"] += 1
                        file_path = os.path.join(root, file)
                        
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                lines = f.readlines()
                                quality["total_lines"] += len(lines)
                                
                                # 简单的代码质量检查
                                for i, line in enumerate(lines, 1):
                                    line = line.strip()
                                    if len(line) > 120:
                                        quality["issues"].append({
                                            "file": os.path.relpath(file_path, project_path),
                                            "line": i,
                                            "type": "line_too_long",
                                            "severity": "warning",
                                            "message": "行长度超过120字符"
                                        })
                                    elif line and not line.startswith('#') and '  ' in line and not line.startswith('    '):
                                        quality["issues"].append({
                                            "file": os.path.relpath(file_path, project_path),
                                            "line": i,
                                            "type": "indentation",
                                            "severity": "warning",
                                            "message": "缩进不一致"
                                        })
                        except Exception as e:
                            continue
            
            quality["total_files"] = quality["python_files"]
            return quality
        except Exception as e:
            return {"error": str(e)}
    
    async def _simple_dependency_analysis(self, project_path: str) -> Dict[str, Any]:
        """简化的依赖分析"""
        try:
            dependencies = {
                "requirements_files": [],
                "imports": [],
                "external_packages": []
            }
            
            # 查找requirements文件
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    if file in ['requirements.txt', 'requirements-dev.txt', 'setup.py', 'pyproject.toml']:
                        dependencies["requirements_files"].append(os.path.relpath(os.path.join(root, file), project_path))
            
            # 扫描import语句
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                lines = content.split('\n')
                                
                                for line in lines:
                                    line = line.strip()
                                    if line.startswith(('import ', 'from ')):
                                        dependencies["imports"].append(line)
                                        # 提取外部包名
                                        if 'from ' in line and ' import' in line:
                                            package = line.split('from ')[1].split(' import')[0].split('.')[0]
                                            if package not in ['os', 'sys', 'json', 'time', 'datetime', 'pathlib']:
                                                dependencies["external_packages"].append(package)
                        except Exception as e:
                            continue
            
            # 去重
            dependencies["external_packages"] = list(set(dependencies["external_packages"]))
            return dependencies
        except Exception as e:
            return {"error": str(e)}
    
    # ========== 依赖库源码 Bug 检测通用方法 ==========
    
    async def detect_library_source_bugs(
        self,
        project_path: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        通用方法：检测依赖库源码中的 Bug
        
        核心思路：
        1. 检测阶段：对测试代码进行静态分析（mypy、pylint、AI分析）
        2. 识别阶段：判断问题是否来自依赖库（当错误涉及 import 的第三方库API时）
        3. 定位阶段：在Docker容器中定位依赖库源码位置（site-packages）
        4. 分析阶段：对依赖库源码进行静态分析（mypy、pylint）
        5. 关联阶段：将测试代码中的问题与依赖库源码中的bug关联起来
        
        适用于任何依赖库（Flask、Django、requests 等），不限于 Flask。
        
        Args:
            project_path: 项目路径（包含测试代码）
            options: 检测选项
            
        Returns:
            包含检测结果的字典
        """
        if options is None:
            options = {}
        
        try:
            self.logger.info(f"开始检测依赖库源码 Bug: {project_path}")
            
            # 检查Docker是否可用
            if not self.use_docker or not self.docker_runner:
                return {
                    "success": False,
                    "error": "Docker未启用，无法检测依赖库源码。请启用Docker支持。",
                    "detection_results": {}
                }
            
            project_path_obj = Path(project_path)
            if not project_path_obj.exists():
                return {
                    "success": False,
                    "error": f"项目路径不存在: {project_path}",
                    "detection_results": {}
                }
            
            # 阶段1：检测阶段 - 对测试代码进行静态分析
            self.logger.info("阶段1: 检测测试代码中的问题...")
            test_code_issues = await self._detect_test_code_issues(project_path_obj, options)
            
            # 阶段2：识别阶段 - 判断问题是否来自依赖库
            self.logger.info("阶段2: 识别来自依赖库的问题...")
            library_related_issues = await self._identify_library_related_issues(
                test_code_issues,
                project_path_obj
            )
            
            if not library_related_issues:
                self.logger.info("未发现与依赖库相关的问题")
                return {
                    "success": True,
                    "detection_results": {
                        "test_code_issues": test_code_issues,
                        "library_related_issues": [],
                        "library_source_issues": [],
                        "correlations": []
                    },
                    "summary": {
                        "total_test_issues": len(test_code_issues),
                        "library_related_count": 0,
                        "library_source_issues_count": 0
                    }
                }
            
            # 阶段3：定位阶段 - 在Docker容器中定位依赖库源码位置
            self.logger.info("阶段3: 定位依赖库源码位置...")
            library_locations = await self._locate_library_sources(
                library_related_issues,
                project_path_obj
            )
            
            if not library_locations:
                self.logger.warning("无法定位依赖库源码位置")
                return {
                    "success": True,
                    "detection_results": {
                        "test_code_issues": test_code_issues,
                        "library_related_issues": library_related_issues,
                        "library_source_issues": [],
                        "correlations": []
                    },
                    "summary": {
                        "total_test_issues": len(test_code_issues),
                        "library_related_count": len(library_related_issues),
                        "library_source_issues_count": 0
                    }
                }
            
            # 阶段4：分析阶段 - 对依赖库源码进行静态分析
            self.logger.info("阶段4: 分析依赖库源码...")
            library_source_issues = await self._analyze_library_sources(
                library_locations,
                options
            )
            
            # 阶段5：关联阶段 - 将测试代码中的问题与依赖库源码中的bug关联起来
            self.logger.info("阶段5: 关联测试代码问题与依赖库源码bug...")
            correlations = await self._correlate_issues(
                library_related_issues,
                library_source_issues,
                library_locations
            )
            
            # 生成报告
            result = {
                "success": True,
                "detection_results": {
                    "test_code_issues": test_code_issues,
                    "library_related_issues": library_related_issues,
                    "library_source_issues": library_source_issues,
                    "library_locations": library_locations,
                    "correlations": correlations
                },
                "summary": {
                    "total_test_issues": len(test_code_issues),
                    "library_related_count": len(library_related_issues),
                    "library_source_issues_count": len(library_source_issues),
                    "correlations_count": len(correlations)
                },
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"依赖库源码 Bug 检测完成: {result['summary']}")
            return result
            
        except Exception as e:
            self.logger.error(f"检测依赖库源码 Bug 失败: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return {
                "success": False,
                "error": str(e),
                "detection_results": {}
            }
    
    async def _detect_test_code_issues(
        self,
        project_path: Path,
        options: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        阶段1：检测阶段 - 对测试代码进行静态分析
        
        使用 mypy、pylint 等工具对测试代码进行静态分析
        """
        issues = []
        
        try:
            # 查找所有 Python 文件
            py_files = list(project_path.rglob("*.py"))
            
            # 排除测试目录（如果存在）
            test_dirs = ["tests", "test", "__pycache__", ".venv", "venv"]
            py_files = [
                f for f in py_files
                if not any(test_dir in str(f) for test_dir in test_dirs)
            ]
            
            self.logger.info(f"找到 {len(py_files)} 个 Python 文件进行分析")
            
            # 使用 mypy 进行类型检查
            if self.mypy_tool and options.get("use_mypy", True):
                for py_file in py_files:
                    try:
                        mypy_result = await self.mypy_tool.analyze(str(py_file))
                        if mypy_result.get("success"):
                            for issue in mypy_result.get("issues", []):
                                issue["tool"] = "mypy"
                                issue["file"] = str(py_file)
                                issues.append(issue)
                    except Exception as e:
                        self.logger.warning(f"mypy 分析失败 {py_file}: {e}")
            
            # 使用 pylint 进行代码质量检查
            if self.pylint_tool and options.get("use_pylint", True):
                for py_file in py_files:
                    try:
                        pylint_result = await self.pylint_tool.analyze(str(py_file))
                        if pylint_result.get("success"):
                            for issue in pylint_result.get("issues", []):
                                issue["tool"] = "pylint"
                                issue["file"] = str(py_file)
                                issues.append(issue)
                    except Exception as e:
                        self.logger.warning(f"pylint 分析失败 {py_file}: {e}")
            
            # 使用 AI 分析（如果启用）
            if options.get("use_ai_analysis", False):
                for py_file in py_files:
                    try:
                        ai_issues = await self._ai_analyze_file(str(py_file))
                        issues.extend(ai_issues)
                    except Exception as e:
                        self.logger.warning(f"AI 分析失败 {py_file}: {e}")
            
            self.logger.info(f"检测到 {len(issues)} 个测试代码问题")
            
        except Exception as e:
            self.logger.error(f"检测测试代码问题失败: {e}")
        
        return issues
    
    async def _identify_library_related_issues(
        self,
        test_code_issues: List[Dict[str, Any]],
        project_path: Path
    ) -> List[Dict[str, Any]]:
        """
        阶段2：识别阶段 - 判断问题是否来自依赖库
        
        通过分析错误信息、文件路径、import 语句等，判断问题是否与依赖库相关
        """
        library_related = []
        
        try:
            # 提取项目中使用的第三方库
            third_party_libraries = await self._extract_third_party_libraries(project_path)
            
            self.logger.info(f"发现 {len(third_party_libraries)} 个第三方库: {third_party_libraries}")
            
            # 分析每个问题，判断是否与依赖库相关
            for issue in test_code_issues:
                # 检查错误消息中是否包含库名
                message = issue.get("message", "").lower()
                file_path = issue.get("file", "")
                
                # 检查错误是否涉及第三方库的 API
                for library in third_party_libraries:
                    library_lower = library.lower()
                    
                    # 方法1: 检查错误消息中是否包含库名
                    if library_lower in message:
                        issue["library"] = library
                        issue["relation_type"] = "error_message"
                        library_related.append(issue)
                        break
                    
                    # 方法2: 检查是否使用了库的 API（通过解析代码）
                    if await self._check_uses_library_api(file_path, library):
                        issue["library"] = library
                        issue["relation_type"] = "api_usage"
                        library_related.append(issue)
                        break
                    
                    # 方法3: 检查错误是否指向库的模块
                    if library_lower in file_path.lower():
                        issue["library"] = library
                        issue["relation_type"] = "file_path"
                        library_related.append(issue)
                        break
            
            self.logger.info(f"识别出 {len(library_related)} 个与依赖库相关的问题")
            
        except Exception as e:
            self.logger.error(f"识别依赖库相关问题失败: {e}")
        
        return library_related
    
    async def _extract_third_party_libraries(self, project_path: Path) -> List[str]:
        """提取项目中使用的第三方库"""
        libraries = set()
        
        try:
            # 扫描所有 Python 文件中的 import 语句
            for py_file in project_path.rglob("*.py"):
                try:
                    with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                        # 简单的 import 语句解析
                        import re
                        # 匹配 from package import ... 或 import package
                        import_pattern = r'(?:from\s+(\w+)|import\s+(\w+))'
                        matches = re.findall(import_pattern, content)
                        
                        for match in matches:
                            package = match[0] if match[0] else match[1]
                            if package:
                                # 排除标准库
                                if package not in [
                                    'os', 'sys', 'json', 'time', 'datetime', 'pathlib',
                                    'collections', 'itertools', 'functools', 'typing',
                                    'abc', 'enum', 'dataclasses', 'asyncio', 'threading',
                                    'multiprocessing', 'subprocess', 'logging', 'hashlib',
                                    'base64', 'urllib', 'http', 'email', 'html', 'xml',
                                    'sqlite3', 'pickle', 'copy', 'math', 'random', 'string',
                                    're', 'struct', 'array', 'io', 'csv', 'configparser',
                                    'unittest', 'doctest', 'pdb', 'traceback', 'warnings',
                                    'ctypes', 'mmap', 'socket', 'select', 'ssl', 'gzip',
                                    'zipfile', 'tarfile', 'shutil', 'tempfile', 'glob',
                                    'fnmatch', 'linecache', 'codecs', 'locale', 'gettext'
                                ]:
                                    libraries.add(package)
                
                except Exception as e:
                    continue
            
        except Exception as e:
            self.logger.error(f"提取第三方库失败: {e}")
        
        return list(libraries)
    
    async def _check_uses_library_api(self, file_path: str, library: str) -> bool:
        """检查文件是否使用了指定库的 API"""
        try:
            if not Path(file_path).exists():
                return False
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 检查是否导入了该库
            import_patterns = [
                f'from {library}',
                f'import {library}',
                f'{library}.'
            ]
            
            for pattern in import_patterns:
                if pattern in content:
                    return True
            
            return False
            
        except Exception:
            return False
    
    async def _locate_library_sources(
        self,
        library_related_issues: List[Dict[str, Any]],
        project_path: Path
    ) -> Dict[str, str]:
        """
        阶段3：定位阶段 - 在Docker容器中定位依赖库源码位置
        
        在 Docker 容器的 site-packages 中查找依赖库的源码位置
        """
        library_locations = {}
        
        try:
            # 提取所有涉及的库
            libraries = set()
            for issue in library_related_issues:
                library = issue.get("library")
                if library:
                    libraries.add(library)
            
            self.logger.info(f"需要定位 {len(libraries)} 个依赖库的源码位置")
            
            # 在 Docker 容器中定位每个库的源码位置
            for library in libraries:
                try:
                    location = await self._find_library_source_in_docker(
                        project_path,
                        library
                    )
                    if location:
                        library_locations[library] = location
                        self.logger.info(f"定位到 {library} 源码位置: {location}")
                    else:
                        self.logger.warning(f"无法定位 {library} 源码位置")
                
                except Exception as e:
                    self.logger.warning(f"定位 {library} 源码位置失败: {e}")
            
        except Exception as e:
            self.logger.error(f"定位依赖库源码位置失败: {e}")
        
        return library_locations
    
    async def _find_library_source_in_docker(
        self,
        project_path: Path,
        library_name: str
    ) -> Optional[str]:
        """在 Docker 容器中查找依赖库源码位置"""
        
        try:
            # 方法1: 使用 Python 代码查找
            find_cmd = [
                "python", "-c",
                f"import {library_name}; import os; print(os.path.dirname({library_name}.__file__))"
            ]
            
            result = await self.docker_runner.run_command(
                project_path=project_path,
                command=find_cmd,
                timeout=60
            )
            
            if result.get("success") and result.get("stdout"):
                library_path = result["stdout"].strip()
                if library_path and "site-packages" in library_path:
                    return library_path
            
            # 方法2: 使用 pip show
            pip_cmd = ["pip", "show", library_name]
            result = await self.docker_runner.run_command(
                project_path=project_path,
                command=pip_cmd,
                timeout=60
            )
            
            if result.get("success") and result.get("stdout"):
                for line in result["stdout"].split('\n'):
                    if line.startswith('Location:'):
                        location = line.split(':', 1)[1].strip()
                        library_path = f"{location}/{library_name}"
                        return library_path
            
            # 方法3: 使用 sysconfig
            sysconfig_cmd = [
                "python", "-c",
                f"import sysconfig; import {library_name}; import os; "
                f"site_packages = sysconfig.get_path('purelib'); "
                f"print(os.path.join(site_packages, '{library_name}'))"
            ]
            
            result = await self.docker_runner.run_command(
                project_path=project_path,
                command=sysconfig_cmd,
                timeout=60
            )
            
            if result.get("success") and result.get("stdout"):
                library_path = result["stdout"].strip()
                if library_path:
                    return library_path
            
        except Exception as e:
            self.logger.error(f"在 Docker 中查找 {library_name} 源码位置失败: {e}")
        
        return None
    
    async def _analyze_library_sources(
        self,
        library_locations: Dict[str, str],
        options: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        阶段4：分析阶段 - 对依赖库源码进行静态分析
        
        使用 mypy、pylint 等工具对依赖库源码进行静态分析
        """
        all_issues = []
        
        try:
            for library_name, library_path in library_locations.items():
                self.logger.info(f"分析 {library_name} 源码: {library_path}")
                
                # 注意：library_path 是容器内的路径，我们需要在容器中运行分析
                library_issues = await self._analyze_library_source_in_docker(
                    library_name,
                    library_path,
                    options
                )
                
                for issue in library_issues:
                    issue["library"] = library_name
                    issue["library_source_path"] = library_path
                    all_issues.append(issue)
            
            self.logger.info(f"在依赖库源码中发现 {len(all_issues)} 个问题")
            
        except Exception as e:
            self.logger.error(f"分析依赖库源码失败: {e}")
        
        return all_issues
    
    async def _analyze_library_source_in_docker(
        self,
        library_name: str,
        library_path: str,
        options: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """在 Docker 容器中分析依赖库源码"""
        issues = []
        
        try:
            # 创建一个临时的项目目录来挂载（实际上我们只需要在容器中运行命令）
            # 使用一个空的项目路径作为挂载点
            temp_project = Path("temp_docker_analysis")
            temp_project.mkdir(exist_ok=True)
            
            try:
                # 方法1: 使用 mypy 分析库源码
                if options.get("use_mypy", True):
                    mypy_cmd = [
                        "sh", "-c",
                        f"cd /usr/local/lib/python*/site-packages && "
                        f"python -m mypy {library_name} --no-error-summary --show-error-codes 2>&1 || true"
                    ]
                    
                    result = await self.docker_runner.run_command(
                        project_path=temp_project,
                        command=mypy_cmd,
                        timeout=300
                    )
                    
                    if result.get("success") or result.get("stdout"):
                        # 解析 mypy 输出
                        mypy_issues = self._parse_mypy_output(
                            result.get("stdout", ""),
                            library_name,
                            library_path
                        )
                        issues.extend(mypy_issues)
                
                # 方法2: 使用 pylint 分析库源码
                if options.get("use_pylint", True):
                    pylint_cmd = [
                        "sh", "-c",
                        f"cd /usr/local/lib/python*/site-packages && "
                        f"python -m pylint {library_name} --disable=all --enable=E,F 2>&1 || true"
                    ]
                    
                    result = await self.docker_runner.run_command(
                        project_path=temp_project,
                        command=pylint_cmd,
                        timeout=300
                    )
                    
                    if result.get("success") or result.get("stdout"):
                        # 解析 pylint 输出
                        pylint_issues = self._parse_pylint_output(
                            result.get("stdout", ""),
                            library_name,
                            library_path
                        )
                        issues.extend(pylint_issues)
            
            finally:
                # 清理临时目录
                if temp_project.exists():
                    try:
                        shutil.rmtree(temp_project)
                    except Exception:
                        pass
        
        except Exception as e:
            self.logger.error(f"在 Docker 中分析 {library_name} 源码失败: {e}")
        
        return issues
    
    def _parse_mypy_output(
        self,
        output: str,
        library_name: str,
        library_path: str
    ) -> List[Dict[str, Any]]:
        """解析 mypy 输出"""
        issues = []
        
        try:
            for line in output.split('\n'):
                line = line.strip()
                if not line or 'error:' not in line:
                    continue
                
                # 解析 mypy 输出格式: file:line: error: message [error_code]
                parts = line.split(':', 3)
                if len(parts) >= 4:
                    file_path = parts[0]
                    line_num = parts[1]
                    error_msg = parts[3].strip()
                    
                    # 提取错误代码
                    error_code = ""
                    if '[' in error_msg and ']' in error_msg:
                        code_start = error_msg.rfind('[')
                        code_end = error_msg.rfind(']')
                        error_code = error_msg[code_start+1:code_end]
                        error_msg = error_msg[:code_start].strip()
                    
                    issues.append({
                        "type": "mypy",
                        "severity": "error",
                        "message": error_msg,
                        "file": file_path,
                        "line": int(line_num) if line_num.isdigit() else 0,
                        "column": 0,
                        "error_code": error_code,
                        "library": library_name,
                        "library_source_path": library_path
                    })
        
        except Exception as e:
            self.logger.warning(f"解析 mypy 输出失败: {e}")
        
        return issues
    
    def _parse_pylint_output(
        self,
        output: str,
        library_name: str,
        library_path: str
    ) -> List[Dict[str, Any]]:
        """解析 pylint 输出"""
        issues = []
        
        try:
            for line in output.split('\n'):
                line = line.strip()
                if not line or ':' not in line:
                    continue
                
                # 解析 pylint 输出格式: file:line:column: message (code)
                parts = line.split(':', 3)
                if len(parts) >= 4:
                    file_path = parts[0]
                    line_num = parts[1]
                    col_num = parts[2]
                    msg_part = parts[3].strip()
                    
                    # 提取消息和代码
                    message = msg_part
                    code = ""
                    if '(' in msg_part and ')' in msg_part:
                        code_start = msg_part.rfind('(')
                        code_end = msg_part.rfind(')')
                        code = msg_part[code_start+1:code_end]
                        message = msg_part[:code_start].strip()
                    
                    # 确定严重程度
                    severity = "warning"
                    if code.startswith('E'):
                        severity = "error"
                    elif code.startswith('F'):
                        severity = "error"
                    
                    issues.append({
                        "type": "pylint",
                        "severity": severity,
                        "message": message,
                        "file": file_path,
                        "line": int(line_num) if line_num.isdigit() else 0,
                        "column": int(col_num) if col_num.isdigit() else 0,
                        "error_code": code,
                        "library": library_name,
                        "library_source_path": library_path
                    })
        
        except Exception as e:
            self.logger.warning(f"解析 pylint 输出失败: {e}")
        
        return issues
    
    async def _correlate_issues(
        self,
        library_related_issues: List[Dict[str, Any]],
        library_source_issues: List[Dict[str, Any]],
        library_locations: Dict[str, str]
    ) -> List[Dict[str, Any]]:
        """
        阶段5：关联阶段 - 将测试代码中的问题与依赖库源码中的bug关联起来
        
        通过分析错误类型、API 使用、文件路径等，建立测试代码问题与依赖库源码bug的关联
        """
        correlations = []
        
        try:
            # 按库分组
            library_issues_map = {}
            for issue in library_related_issues:
                library = issue.get("library")
                if library:
                    if library not in library_issues_map:
                        library_issues_map[library] = []
                    library_issues_map[library].append(issue)
            
            library_source_issues_map = {}
            for issue in library_source_issues:
                library = issue.get("library")
                if library:
                    if library not in library_source_issues_map:
                        library_source_issues_map[library] = []
                    library_source_issues_map[library].append(issue)
            
            # 为每个库建立关联
            for library in library_issues_map.keys():
                test_issues = library_issues_map.get(library, [])
                source_issues = library_source_issues_map.get(library, [])
                
                if not test_issues or not source_issues:
                    continue
                
                # 尝试关联每个测试代码问题
                for test_issue in test_issues:
                    # 查找相关的源码问题
                    related_source_issues = []
                    
                    # 方法1: 通过错误类型匹配
                    test_message = test_issue.get("message", "").lower()
                    for source_issue in source_issues:
                        source_message = source_issue.get("message", "").lower()
                        # 检查是否有共同的关键词
                        common_keywords = self._extract_keywords(test_message) & self._extract_keywords(source_message)
                        if common_keywords:
                            related_source_issues.append(source_issue)
                    
                    # 方法2: 通过 API 使用匹配
                    # 如果测试代码使用了特定的 API，查找该 API 相关的源码问题
                    test_file = test_issue.get("file", "")
                    api_usage = await self._extract_api_usage(test_file, library)
                    if api_usage:
                        for source_issue in source_issues:
                            source_file = source_issue.get("file", "")
                            if any(api in source_file for api in api_usage):
                                if source_issue not in related_source_issues:
                                    related_source_issues.append(source_issue)
                    
                    # 如果找到相关源码问题，建立关联
                    if related_source_issues:
                        correlations.append({
                            "test_issue": test_issue,
                            "library": library,
                            "related_source_issues": related_source_issues,
                            "correlation_type": "error_type_match",
                            "confidence": "medium"
                        })
            
            self.logger.info(f"建立了 {len(correlations)} 个关联关系")
            
        except Exception as e:
            self.logger.error(f"关联问题失败: {e}")
        
        return correlations
    
    def _extract_keywords(self, text: str) -> Set[str]:
        """从文本中提取关键词"""
        import re
        # 提取单词（排除常见停用词）
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use'}
        keywords = {w for w in words if w not in stop_words and len(w) > 3}
        return keywords
    
    async def _extract_api_usage(self, file_path: str, library: str) -> List[str]:
        """从文件中提取对指定库的 API 使用"""
        apis = []
        
        try:
            if not Path(file_path).exists():
                return apis
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # 提取 library.xxx 或 from library import xxx 中的 xxx
            import re
            patterns = [
                rf'{library}\.(\w+)',  # library.xxx
                rf'from {library} import (\w+)',  # from library import xxx
                rf'from {library}\.(\w+) import'  # from library.xxx import
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content)
                apis.extend(matches)
            
            return list(set(apis))
            
        except Exception:
            return apis
    
    async def _ai_analyze_file(self, file_path: str) -> List[Dict[str, Any]]:
        """使用 AI 分析文件（如果启用）"""
        # 这里可以集成 AI 分析功能
        # 目前返回空列表
        return []