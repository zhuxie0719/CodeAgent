"""
缺陷检测AGENT
负责主动发现代码中的潜在缺陷和问题
集成静态代码检测功能
"""

import asyncio
import logging
import json
import os
import mimetypes
import magic
from typing import Dict, Any, List, Optional, Tuple, Set
from datetime import datetime
from pathlib import Path
import sys
import subprocess
import tempfile
import shutil

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from ..base_agent import BaseAgent, TaskStatus
# from demo.static_detector import StaticDetector  # 暂时注释，模块不存在
from tools.static_analysis.pylint_tool import PylintTool
from tools.static_analysis.flake8_tool import Flake8Tool
from config.settings import settings


class BugDetectionAgent(BaseAgent):
    """缺陷检测AGENT - 支持多语言和大型项目分析"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__("bug_detection_agent", config)
        self.static_detector = None
        self.pylint_tool = None
        self.flake8_tool = None
        self.detection_rules = {}
        
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
                "tools": ["pylint", "flake8", "static_detector"],
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
            "max_file_size": 10 * 1024 * 1024,  # 10MB
            "max_files_per_project": 1000,
            "max_project_size": 100 * 1024 * 1024,  # 100MB
            "parallel_analysis": True,
            "max_workers": 4
        }
    
    async def initialize(self) -> bool:
        """初始化缺陷检测AGENT"""
        try:
            self.logger.info("初始化缺陷检测AGENT...")
            
            # 初始化检测工具
            await self._initialize_detection_tools()
            
            # 加载检测规则
            await self._load_detection_rules()
            
            self.logger.info("缺陷检测AGENT初始化完成")
            return True
            
        except Exception as e:
            self.logger.error(f"缺陷检测AGENT初始化失败: {e}")
            return False
    
    async def process_task(self, task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理缺陷检测任务"""
        try:
            self.logger.info(f"开始处理缺陷检测任务: {task_id}")
            
            # 获取任务参数
            file_path = task_data.get("file_path")
            project_path = task_data.get("project_path")
            options = task_data.get("options", {})
            
            if not file_path and not project_path:
                raise ValueError("缺少文件路径或项目路径")
            
            # 执行缺陷检测
            if file_path:
                detection_results = await self._detect_file_bugs(file_path, options)
            else:
                detection_results = await self._detect_project_bugs(project_path, options)
            
            # 生成检测报告
            report = await self._generate_report(detection_results)
            
            self.logger.info(f"缺陷检测任务完成: {task_id}")
            return {
                "success": True,
                "task_id": task_id,
                "detection_results": detection_results,
                "report": report,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"处理缺陷检测任务失败: {e}")
            return {
                "success": False,
                "task_id": task_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
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
            # 初始化自定义静态检测器
            self.static_detector = StaticDetector()
            
            # 初始化Pylint工具
            if settings.TOOLS.get("pylint", {}).get("enabled", True):
                self.pylint_tool = PylintTool(settings.TOOLS["pylint"])
            
            # 初始化Flake8工具
            if settings.TOOLS.get("flake8", {}).get("enabled", True):
                self.flake8_tool = Flake8Tool(settings.TOOLS["flake8"])
            
            self.logger.info("检测工具初始化完成")
            
        except Exception as e:
            self.logger.error(f"初始化检测工具失败: {e}")
            raise
    
    async def _load_detection_rules(self):
        """加载检测规则"""
        try:
            # 从静态检测器获取规则
            if self.static_detector:
                self.detection_rules = self.static_detector.rules.copy()
            
            self.logger.info(f"加载了 {len(self.detection_rules)} 个检测规则")
            
        except Exception as e:
            self.logger.error(f"加载检测规则失败: {e}")
            raise
    
    async def _detect_file_bugs(self, file_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """检测单个文件的缺陷 - 支持多语言"""
        try:
            # 检测文件语言
            language = self.detect_language(file_path)
            self.logger.info(f"检测文件 {file_path}，语言: {language}")
            
            all_issues = []
            detection_tools = []
            analysis_time = 0
            
            # 根据语言选择检测工具
            if language == "python":
                # Python文件检测
                if options.get("enable_static", True) and self.static_detector:
                    start_time = datetime.now()
                    issues = self.static_detector.detect_issues(file_path)
                    end_time = datetime.now()
                    
                    for issue in issues:
                        issue["file"] = Path(file_path).name
                        issue["language"] = language
                        if "column" not in issue:
                            issue["column"] = 0
                    
                    all_issues.extend(issues)
                    detection_tools.append("static_detector")
                    analysis_time += (end_time - start_time).total_seconds()
                
                if options.get("enable_pylint", True) and self.pylint_tool:
                    start_time = datetime.now()
                    pylint_result = await self.pylint_tool.analyze(file_path)
                    end_time = datetime.now()
                    
                    if pylint_result["success"]:
                        for issue in pylint_result["issues"]:
                            issue["language"] = language
                        all_issues.extend(pylint_result["issues"])
                        detection_tools.append("pylint")
                    
                    analysis_time += (end_time - start_time).total_seconds()
                
                if options.get("enable_flake8", True) and self.flake8_tool:
                    start_time = datetime.now()
                    flake8_result = await self.flake8_tool.analyze(file_path)
                    end_time = datetime.now()
                    
                    if flake8_result["success"]:
                        for issue in flake8_result["issues"]:
                            issue["language"] = language
                        all_issues.extend(flake8_result["issues"])
                        detection_tools.append("flake8")
                    
                    analysis_time += (end_time - start_time).total_seconds()
            
            elif language in ["java", "c", "cpp", "javascript", "go"]:
                # 其他语言使用AI分析
                if options.get("enable_ai_analysis", True):
                    ai_issues = await self._ai_analyze_file(file_path, language)
                    all_issues.extend(ai_issues)
                    detection_tools.append("ai_analyzer")
            
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
            from api.deepseek_config import deepseek_config
            import aiohttp
            
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
        """解压项目文件"""
        try:
            file_path = Path(file_path)
            extract_dir = Path("temp_extract") / f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            extract_dir.mkdir(parents=True, exist_ok=True)
            
            if file_path.suffix.lower() == '.zip':
                import zipfile
                with zipfile.ZipFile(file_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
            elif file_path.suffix.lower() in ['.tar', '.tar.gz']:
                import tarfile
                with tarfile.open(file_path, 'r:*') as tar_ref:
                    tar_ref.extractall(extract_dir)
            else:
                # 如果是目录，直接复制
                shutil.copytree(file_path, extract_dir)
            
            self.logger.info(f"项目解压到: {extract_dir}")
            return str(extract_dir)
            
        except Exception as e:
            self.logger.error(f"项目解压失败: {e}")
            raise
    
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
    
    async def analyze_project(self, project_path: str, options: Dict[str, Any]) -> Dict[str, Any]:
        """分析整个项目"""
        try:
            self.logger.info(f"开始分析项目: {project_path}")
            
            # 扫描项目文件
            files_by_language = self.scan_project_files(project_path)
            
            if not files_by_language:
                return {
                    "success": False,
                    "error": "未找到支持的代码文件",
                    "files_analyzed": 0
                }
            
            # 并行分析不同语言的文件
            all_results = []
            total_files = sum(len(files) for files in files_by_language.values())
            
            if total_files > self.project_config["max_files_per_project"]:
                return {
                    "success": False,
                    "error": f"项目文件过多 ({total_files} > {self.project_config['max_files_per_project']})",
                    "files_analyzed": 0
                }
            
            # 按语言分组分析
            for language, files in files_by_language.items():
                self.logger.info(f"分析 {language} 文件: {len(files)} 个")
                
                # 限制每个语言的文件数量
                files_to_analyze = files[:50]  # 每个语言最多分析50个文件
                
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
            
            self.logger.info(f"项目分析完成，共分析 {len(all_results)} 个文件")
            return combined_result
            
        except Exception as e:
            self.logger.error(f"项目分析失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "files_analyzed": 0
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