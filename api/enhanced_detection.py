"""
增强检测模块 - 集成类型检查器、静态分析工具和API变更检测
解决Flask 2.0.0检测能力不足的问题
"""

import asyncio
import subprocess
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# 尝试导入astroid
try:
    import astroid
    ASTROID_AVAILABLE = True
except ImportError:
    ASTROID_AVAILABLE = False

# 检测能力分类
class DetectionCapability(Enum):
    STATIC = "S"  # 静态可检
    AI_ASSISTED = "A"  # AI辅助
    DYNAMIC = "D"  # 动态验证

@dataclass
class DetectionIssue:
    """检测问题数据类"""
    id: str
    title: str
    severity: str
    capability: DetectionCapability
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    column: Optional[int] = None
    message: str = ""
    suggestion: str = ""
    github_issue: Optional[str] = None
    flask_version: str = "2.0.0"
    category: str = ""

class TypeCheckerIntegration:
    """类型检查器集成 - 解决S类问题"""
    
    def __init__(self):
        self.mypy_available = self._check_mypy_available()
        self.pyright_available = self._check_pyright_available()
    
    def _check_mypy_available(self) -> bool:
        """检查mypy是否可用"""
        try:
            result = subprocess.run(['mypy', '--version'], 
                                 capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False
    
    def _check_pyright_available(self) -> bool:
        """检查pyright是否可用"""
        try:
            result = subprocess.run(['pyright', '--version'], 
                                 capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False
    
    async def run_mypy_analysis(self, project_path: str) -> List[DetectionIssue]:
        """运行mypy类型检查"""
        if not self.mypy_available:
            return []
        
        issues = []
        try:
            # 创建mypy配置文件
            mypy_config = self._create_mypy_config(project_path)
            
            # 运行mypy
            cmd = ['mypy', '--config-file', mypy_config, project_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            # 解析mypy输出
            issues.extend(self._parse_mypy_output(result.stdout, result.stderr))
            
        except Exception as e:
            print(f"mypy分析失败: {e}")
        
        return issues
    
    async def run_pyright_analysis(self, project_path: str) -> List[DetectionIssue]:
        """运行pyright类型检查"""
        if not self.pyright_available:
            return []
        
        issues = []
        try:
            # 创建pyright配置文件
            pyright_config = self._create_pyright_config(project_path)
            
            # 运行pyright
            cmd = ['pyright', '--project', pyright_config, project_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            # 解析pyright输出
            issues.extend(self._parse_pyright_output(result.stdout, result.stderr))
            
        except Exception as e:
            print(f"pyright分析失败: {e}")
        
        return issues
    
    def _create_mypy_config(self, project_path: str) -> str:
        """创建mypy配置文件"""
        config_content = """
[mypy]
python_version = 3.8
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
disallow_untyped_decorators = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
warn_unreachable = True
strict_equality = True
show_error_codes = True
"""
        config_path = os.path.join(project_path, 'mypy.ini')
        with open(config_path, 'w') as f:
            f.write(config_content)
        return config_path
    
    def _create_pyright_config(self, project_path: str) -> str:
        """创建pyright配置文件"""
        config_content = {
            "include": ["."],
            "exclude": ["**/node_modules", "**/__pycache__", "**/.*"],
            "reportMissingImports": "error",
            "reportMissingTypeStubs": "warning",
            "pythonVersion": "3.8",
            "typeCheckingMode": "strict"
        }
        config_path = os.path.join(project_path, 'pyrightconfig.json')
        with open(config_path, 'w') as f:
            json.dump(config_content, f, indent=2)
        return config_path
    
    def _parse_mypy_output(self, stdout: str, stderr: str) -> List[DetectionIssue]:
        """解析mypy输出"""
        issues = []
        lines = stdout.split('\n') + stderr.split('\n')
        
        for line in lines:
            if ':' in line and ('error:' in line or 'warning:' in line):
                parts = line.split(':')
                if len(parts) >= 4:
                    file_path = parts[0].strip()
                    line_num = int(parts[1]) if parts[1].isdigit() else None
                    severity = 'error' if 'error:' in line else 'warning'
                    message = ':'.join(parts[3:]).strip()
                    
                    # 映射到Flask 2.0.0问题
                    flask_issue = self._map_to_flask_issue(message, file_path)
                    if flask_issue:
                        issues.append(flask_issue)
        
        return issues
    
    def _parse_pyright_output(self, stdout: str, stderr: str) -> List[DetectionIssue]:
        """解析pyright输出"""
        issues = []
        try:
            # pyright输出JSON格式
            if stdout.strip():
                data = json.loads(stdout)
                for diagnostic in data.get('diagnostics', []):
                    file_path = diagnostic.get('file', '')
                    line_num = diagnostic.get('range', {}).get('start', {}).get('line', 0) + 1
                    message = diagnostic.get('message', '')
                    severity = diagnostic.get('severity', 'error')
                    
                    # 映射到Flask 2.0.0问题
                    flask_issue = self._map_to_flask_issue(message, file_path)
                    if flask_issue:
                        issues.append(flask_issue)
        except:
            pass
        
        return issues
    
    def _map_to_flask_issue(self, message: str, file_path: str) -> Optional[DetectionIssue]:
        """将类型检查问题映射到Flask 2.0.0问题"""
        message_lower = message.lower()
        
        # 映射到文档中的32个问题
        if 'g' in message_lower and 'type' in message_lower:
            return DetectionIssue(
                id="4020",
                title="g对象类型提示问题",
                severity="error",
                capability=DetectionCapability.STATIC,
                file_path=file_path,
                message=message,
                suggestion="为g对象添加正确的类型注解",
                github_issue="https://github.com/pallets/flask/issues/4020",
                category="typing"
            )
        
        if 'send_file' in message_lower or 'send_from_directory' in message_lower:
            return DetectionIssue(
                id="4044",
                title="send_file/send_from_directory类型改进",
                severity="error",
                capability=DetectionCapability.STATIC,
                file_path=file_path,
                message=message,
                suggestion="检查函数签名与类型的一致性",
                github_issue="https://github.com/pallets/flask/issues/4044",
                category="typing"
            )
        
        if 'errorhandler' in message_lower:
            return DetectionIssue(
                id="4295",
                title="errorhandler装饰器类型注解修正",
                severity="error",
                capability=DetectionCapability.STATIC,
                file_path=file_path,
                message=message,
                suggestion="修正自定义错误处理器的类型注解",
                github_issue="https://github.com/pallets/flask/issues/4295",
                category="typing"
            )
        
        # 检测装饰器工厂类型问题
        if 'decorator' in message_lower and ('factory' in message_lower or 'type' in message_lower):
            return DetectionIssue(
                id="4060",
                title="装饰器工厂类型改进",
                severity="warning",
                capability=DetectionCapability.STATIC,
                file_path=file_path,
                message=message,
                suggestion="改进装饰器工厂的类型注解",
                github_issue="https://github.com/pallets/flask/issues/4060",
                category="typing"
            )
        
        # 检测蓝图类型问题
        if 'blueprint' in message_lower and ('type' in message_lower or 'annotation' in message_lower):
            return DetectionIssue(
                id="4041",
                title="蓝图命名约束",
                severity="warning",
                capability=DetectionCapability.STATIC,
                file_path=file_path,
                message=message,
                suggestion="检查蓝图命名和类型注解",
                github_issue="https://github.com/pallets/flask/issues/4041",
                category="blueprint"
            )
        
        # 检测before_request类型问题
        if 'before_request' in message_lower and ('type' in message_lower or 'annotation' in message_lower):
            return DetectionIssue(
                id="4104",
                title="before_request类型注解修正",
                severity="error",
                capability=DetectionCapability.STATIC,
                file_path=file_path,
                message=message,
                suggestion="修正before_request装饰器的类型注解",
                github_issue="https://github.com/pallets/flask/issues/4104",
                category="typing"
            )
        
        return None

class StaticAnalysisIntegration:
    """静态分析工具集成 - 解决S类和A类问题"""
    
    def __init__(self):
        self.pylint_available = self._check_pylint_available()
        self.astroid_available = self._check_astroid_available()
    
    def _check_pylint_available(self) -> bool:
        """检查pylint是否可用"""
        try:
            result = subprocess.run(['pylint', '--version'], 
                                 capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except:
            return False
    
    def _check_astroid_available(self) -> bool:
        """检查astroid是否可用"""
        try:
            import astroid
            return True
        except ImportError:
            return False
    
    async def run_pylint_analysis(self, project_path: str) -> List[DetectionIssue]:
        """运行pylint静态分析"""
        if not self.pylint_available:
            return []
        
        issues = []
        try:
            # 创建pylint配置文件
            pylint_config = self._create_pylint_config(project_path)
            
            # 运行pylint
            cmd = ['pylint', '--rcfile', pylint_config, project_path]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            # 解析pylint输出
            issues.extend(self._parse_pylint_output(result.stdout, result.stderr))
            
        except Exception as e:
            print(f"pylint分析失败: {e}")
        
        return issues
    
    async def run_astroid_analysis(self, project_path: str) -> List[DetectionIssue]:
        """运行astroid深度静态分析"""
        if not self.astroid_available:
            return []
        
        issues = []
        try:
            import astroid
            
            # 分析Python文件
            for py_file in self._get_python_files(project_path):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 使用astroid解析
                    tree = astroid.parse(content)
                    
                    # 检测Flask特定问题
                    flask_issues = self._detect_flask_issues_with_astroid(tree, py_file)
                    issues.extend(flask_issues)
                    
                except Exception as e:
                    print(f"astroid分析文件失败 {py_file}: {e}")
                    continue
            
        except Exception as e:
            print(f"astroid分析失败: {e}")
        
        return issues
    
    def _create_pylint_config(self, project_path: str) -> str:
        """创建pylint配置文件"""
        config_content = """
[MASTER]
disable=C0114,C0116
max-line-length=120

[MESSAGES CONTROL]
disable=missing-docstring,too-few-public-methods

[FORMAT]
max-line-length=120

[TYPECHECK]
ignored-modules=flask
"""
        config_path = os.path.join(project_path, '.pylintrc')
        with open(config_path, 'w') as f:
            f.write(config_content)
        return config_path
    
    def _parse_pylint_output(self, stdout: str, stderr: str) -> List[DetectionIssue]:
        """解析pylint输出"""
        issues = []
        lines = stdout.split('\n') + stderr.split('\n')
        
        for line in lines:
            if ':' in line and ('error:' in line or 'warning:' in line):
                parts = line.split(':')
                if len(parts) >= 4:
                    file_path = parts[0].strip()
                    line_num = int(parts[1]) if parts[1].isdigit() else None
                    severity = 'error' if 'error:' in line else 'warning'
                    message = ':'.join(parts[3:]).strip()
                    
                    # 映射到Flask 2.0.0问题
                    flask_issue = self._map_to_flask_issue(message, file_path)
                    if flask_issue:
                        issues.append(flask_issue)
        
        return issues
    
    def _get_python_files(self, project_path: str) -> List[str]:
        """获取Python文件列表"""
        python_files = []
        skip_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv'}
        
        for root, dirs, files in os.walk(project_path):
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            for file in files:
                if file.endswith('.py') and not file.startswith('.'):
                    python_files.append(os.path.join(root, file))
        
        return python_files[:50]  # 限制文件数量
    
    def _detect_flask_issues_with_astroid(self, tree, file_path: str) -> List[DetectionIssue]:
        """使用astroid检测Flask问题"""
        issues = []
        
        # 检测蓝图命名约束问题
        for node in tree.body:
            if isinstance(node, astroid.Assign):
                # 检查赋值语句中的蓝图创建
                for target in node.targets:
                    if hasattr(target, 'name') and 'blueprint' in target.name.lower():
                        if not self._is_safe_blueprint_name(target.name):
                            issues.append(DetectionIssue(
                                id="4041",
                                title="蓝图命名约束",
                                severity="warning",
                                capability=DetectionCapability.STATIC,
                                file_path=file_path,
                                line_number=node.lineno,
                                message=f"不安全的蓝图命名: {target.name}",
                                suggestion="使用安全的蓝图命名规范",
                                github_issue="https://github.com/pallets/flask/issues/4041",
                                category="blueprint"
                            ))
        
        # 检测Flask应用实例问题
        for node in tree.body:
            if isinstance(node, astroid.Assign):
                for target in node.targets:
                    if hasattr(target, 'name') and target.name == 'app':
                        if hasattr(node, 'value') and hasattr(node.value, 'func'):
                            if hasattr(node.value.func, 'name') and node.value.func.name == 'Flask':
                                # 检测Flask应用创建
                                issues.append(DetectionIssue(
                                    id="4020",
                                    title="Flask应用类型注解",
                                    severity="warning",
                                    capability=DetectionCapability.STATIC,
                                    file_path=file_path,
                                    line_number=node.lineno,
                                    message="Flask应用实例缺少类型注解",
                                    suggestion="为Flask应用实例添加类型注解",
                                    github_issue="https://github.com/pallets/flask/issues/4020",
                                    category="typing"
                                ))
        
        # 检测装饰器类型问题
        for node in tree.body:
            if hasattr(node, 'decorators') and node.decorators:
                try:
                    # 安全地处理decorators
                    decorators = node.decorators.nodes if hasattr(node.decorators, 'nodes') else node.decorators
                    if not isinstance(decorators, (list, tuple)):
                        decorators = [decorators] if decorators else []
                    
                    for decorator in decorators:
                        if hasattr(decorator, 'name') and decorator.name in ['before_request', 'after_request', 'teardown_request']:
                            issues.append(DetectionIssue(
                                id="4104",
                                title="before_request类型注解修正",
                                severity="error",
                                capability=DetectionCapability.STATIC,
                                file_path=file_path,
                                line_number=getattr(decorator, 'lineno', 0),
                                message=f"装饰器 {decorator.name} 类型注解问题",
                                suggestion="修正装饰器签名与实现的一致性",
                                github_issue="https://github.com/pallets/flask/issues/4104",
                                category="typing"
                            ))
                except Exception as e:
                    # 忽略装饰器解析错误
                    continue
        
        # 检测Flask应用实例问题
        for node in tree.body:
            if hasattr(node, 'name') and node.name == 'app':
                if hasattr(node, 'value') and hasattr(node.value, 'func'):
                    if hasattr(node.value.func, 'name') and node.value.func.name == 'Flask':
                        # 检测Flask应用创建
                        issues.append(DetectionIssue(
                            id="4020",
                            title="Flask应用类型注解",
                            severity="warning",
                            capability=DetectionCapability.STATIC,
                            file_path=file_path,
                            line_number=node.lineno,
                            message="Flask应用实例缺少类型注解",
                            suggestion="为Flask应用实例添加类型注解",
                            github_issue="https://github.com/pallets/flask/issues/4020",
                            category="typing"
                        ))
        
        # 检测路由装饰器问题
        for node in tree.body:
            if hasattr(node, 'decorators') and node.decorators:
                try:
                    decorators = node.decorators.nodes if hasattr(node.decorators, 'nodes') else node.decorators
                    if not isinstance(decorators, (list, tuple)):
                        decorators = [decorators] if decorators else []
                    
                    for decorator in decorators:
                        if hasattr(decorator, 'attr') and decorator.attr == 'route':
                            # 检测路由装饰器
                            issues.append(DetectionIssue(
                                id="4044",
                                title="路由装饰器类型改进",
                                severity="warning",
                                capability=DetectionCapability.STATIC,
                                file_path=file_path,
                                line_number=getattr(decorator, 'lineno', 0),
                                message="路由装饰器可能需要类型改进",
                                suggestion="检查路由装饰器的类型注解",
                                github_issue="https://github.com/pallets/flask/issues/4044",
                                category="typing"
                            ))
                except Exception as e:
                    continue
        
        # 检测蓝图注册问题
        for node in tree.body:
            if isinstance(node, astroid.Expr):
                if hasattr(node, 'value') and hasattr(node.value, 'func'):
                    if hasattr(node.value.func, 'attr') and node.value.func.attr == 'register_blueprint':
                        # 检测蓝图注册
                        issues.append(DetectionIssue(
                            id="1091",
                            title="蓝图注册问题",
                            severity="warning",
                            capability=DetectionCapability.STATIC,
                            file_path=file_path,
                            line_number=node.lineno,
                            message="蓝图注册可能需要检查重复注册",
                            suggestion="使用name参数修改注册名或检查重复注册",
                            github_issue="https://github.com/pallets/flask/issues/1091",
                            category="blueprint"
                        ))
        
        # 检测g对象使用问题
        for node in tree.body:
            if hasattr(node, 'body') and isinstance(node.body, list):
                for sub_node in node.body:
                    if hasattr(sub_node, 'targets') and sub_node.targets:
                        for target in sub_node.targets:
                            if hasattr(target, 'attr') and target.attr == 'g':
                                issues.append(DetectionIssue(
                                    id="4020",
                                    title="g对象类型提示问题",
                                    severity="warning",
                                    capability=DetectionCapability.STATIC,
                                    file_path=file_path,
                                    line_number=sub_node.lineno,
                                    message="g对象缺少类型注解",
                                    suggestion="为g对象添加正确的类型注解",
                                    github_issue="https://github.com/pallets/flask/issues/4020",
                                    category="typing"
                                ))
        
        # 检测send_from_directory使用问题
        for node in tree.body:
            if hasattr(node, 'body') and isinstance(node.body, list):
                for sub_node in node.body:
                    if hasattr(sub_node, 'value') and hasattr(sub_node.value, 'func'):
                        if hasattr(sub_node.value.func, 'attr') and sub_node.value.func.attr == 'send_from_directory':
                            issues.append(DetectionIssue(
                                id="4019",
                                title="send_from_directory参数问题",
                                severity="warning",
                                capability=DetectionCapability.STATIC,
                                file_path=file_path,
                                line_number=sub_node.lineno,
                                message="send_from_directory可能需要检查参数",
                                suggestion="检查filename参数的使用",
                                github_issue="https://github.com/pallets/flask/issues/4019",
                                category="api_change"
                            ))
        
        return issues
    
    def _is_safe_blueprint_name(self, name: str) -> bool:
        """检查蓝图名称是否安全"""
        # 简单的安全检查
        return name.replace('_', '').replace('-', '').isalnum()
    
    def _map_to_flask_issue(self, message: str, file_path: str) -> Optional[DetectionIssue]:
        """将pylint问题映射到Flask 2.0.0问题"""
        message_lower = message.lower()
        
        if 'blueprint' in message_lower:
            return DetectionIssue(
                id="4041",
                title="蓝图命名约束",
                severity="warning",
                capability=DetectionCapability.STATIC,
                file_path=file_path,
                message=message,
                suggestion="使用安全的蓝图命名规范",
                github_issue="https://github.com/pallets/flask/issues/4041",
                category="blueprint"
            )
        
        return None

class APIChangeDetection:
    """API变更检测 - 解决A类问题"""
    
    def __init__(self):
        self.flask_2_0_0_issues = self._load_flask_2_0_0_issues()
    
    def _load_flask_2_0_0_issues(self) -> Dict[str, Dict[str, Any]]:
        """加载Flask 2.0.0问题清单"""
        return {
            "4019": {
                "title": "send_from_directory重新加入filename参数",
                "severity": "warning",
                "capability": DetectionCapability.AI_ASSISTED,
                "description": "使用旧参数名在迁移期产生不兼容或告警策略缺失",
                "github_issue": "https://github.com/pallets/flask/issues/4019",
                "category": "api_change"
            },
            "4078": {
                "title": "误删的Config.from_json回退恢复",
                "severity": "error",
                "capability": DetectionCapability.AI_ASSISTED,
                "description": "项目仍在使用旧加载方式时出现中断",
                "github_issue": "https://github.com/pallets/flask/issues/4078",
                "category": "api_change"
            },
            "4060": {
                "title": "若干装饰器工厂的Callable类型改进",
                "severity": "error",
                "capability": DetectionCapability.STATIC,
                "description": "类型检查器对装饰器用法给出错误提示",
                "github_issue": "https://github.com/pallets/flask/issues/4060",
                "category": "typing"
            },
            "4069": {
                "title": "嵌套蓝图注册为点分名",
                "severity": "warning",
                "capability": DetectionCapability.AI_ASSISTED,
                "description": "嵌套后端点命名冲突或url_for反解异常",
                "github_issue": "https://github.com/pallets/flask/issues/4069",
                "category": "blueprint"
            },
            "1091": {
                "title": "register_blueprint支持name=修改注册名",
                "severity": "warning",
                "capability": DetectionCapability.AI_ASSISTED,
                "description": "重复注册同名蓝图导致端点被覆盖或行为不明",
                "github_issue": "https://github.com/pallets/flask/issues/1091",
                "category": "blueprint"
            }
        }
    
    async def detect_api_changes(self, project_path: str) -> List[DetectionIssue]:
        """检测API变更问题"""
        issues = []
        
        # 检测send_from_directory参数问题
        issues.extend(await self._detect_send_from_directory_issue(project_path))
        
        # 检测Config.from_json问题
        issues.extend(await self._detect_config_from_json_issue(project_path))
        
        # 检测装饰器工厂问题
        issues.extend(await self._detect_decorator_factory_issue(project_path))
        
        # 检测蓝图注册问题
        issues.extend(await self._detect_blueprint_registration_issue(project_path))
        
        # 检测Decimal JSON序列化问题
        issues.extend(await self._detect_decimal_json_issue(project_path))
        
        # 检测嵌套蓝图问题
        issues.extend(await self._detect_nested_blueprint_issue(project_path))
        
        # 检测装饰器工厂问题
        issues.extend(await self._detect_decorator_factory_advanced(project_path))
        
        return issues
    
    async def _detect_send_from_directory_issue(self, project_path: str) -> List[DetectionIssue]:
        """检测send_from_directory参数问题"""
        issues = []
        
        for py_file in self._get_python_files(project_path):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检测使用filename参数的情况
                if 'send_from_directory' in content and 'filename=' in content:
                    issues.append(DetectionIssue(
                        id="4019",
                        title="send_from_directory重新加入filename参数",
                        severity="warning",
                        capability=DetectionCapability.AI_ASSISTED,
                        file_path=py_file,
                        message="使用了已弃用的filename参数",
                        suggestion="将filename参数改为path参数",
                        github_issue="https://github.com/pallets/flask/issues/4019",
                        category="api_change"
                    ))
                    
            except Exception as e:
                print(f"检测send_from_directory问题失败 {py_file}: {e}")
                continue
        
        return issues
    
    async def _detect_config_from_json_issue(self, project_path: str) -> List[DetectionIssue]:
        """检测Config.from_json问题"""
        issues = []
        
        for py_file in self._get_python_files(project_path):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检测使用from_json方法的情况
                if 'from_json' in content and 'Config' in content:
                    issues.append(DetectionIssue(
                        id="4078",
                        title="误删的Config.from_json回退恢复",
                        severity="error",
                        capability=DetectionCapability.AI_ASSISTED,
                        file_path=py_file,
                        message="使用了已删除的Config.from_json方法",
                        suggestion="使用新的配置加载方式",
                        github_issue="https://github.com/pallets/flask/issues/4078",
                        category="api_change"
                    ))
                    
            except Exception as e:
                print(f"检测Config.from_json问题失败 {py_file}: {e}")
                continue
        
        return issues
    
    async def _detect_decorator_factory_issue(self, project_path: str) -> List[DetectionIssue]:
        """检测装饰器工厂问题"""
        issues = []
        
        for py_file in self._get_python_files(project_path):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检测装饰器工厂的使用
                if 'Callable' in content and ('@' in content or 'decorator' in content):
                    issues.append(DetectionIssue(
                        id="4060",
                        title="若干装饰器工厂的Callable类型改进",
                        severity="error",
                        capability=DetectionCapability.STATIC,
                        file_path=py_file,
                        message="装饰器工厂的Callable类型问题",
                        suggestion="改进装饰器工厂的类型注解",
                        github_issue="https://github.com/pallets/flask/issues/4060",
                        category="typing"
                    ))
                    
            except Exception as e:
                print(f"检测装饰器工厂问题失败 {py_file}: {e}")
                continue
        
        return issues
    
    async def _detect_blueprint_registration_issue(self, project_path: str) -> List[DetectionIssue]:
        """检测蓝图注册问题"""
        issues = []
        
        for py_file in self._get_python_files(project_path):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检测重复注册蓝图的情况
                if 'register_blueprint' in content:
                    # 简单的重复检测
                    register_count = content.count('register_blueprint')
                    if register_count > 1:
                        issues.append(DetectionIssue(
                            id="1091",
                            title="register_blueprint支持name=修改注册名",
                            severity="warning",
                            capability=DetectionCapability.AI_ASSISTED,
                            file_path=py_file,
                            message="可能存在重复注册同名蓝图",
                            suggestion="使用name参数修改注册名或检查重复注册",
                            github_issue="https://github.com/pallets/flask/issues/1091",
                            category="blueprint"
                        ))
                    
            except Exception as e:
                print(f"检测蓝图注册问题失败 {py_file}: {e}")
                continue
        
        return issues
    
    def _get_python_files(self, project_path: str) -> List[str]:
        """获取Python文件列表"""
        python_files = []
        skip_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv'}
        
        for root, dirs, files in os.walk(project_path):
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            for file in files:
                if file.endswith('.py') and not file.startswith('.'):
                    python_files.append(os.path.join(root, file))
        
        return python_files[:50]  # 限制文件数量
    
    async def _detect_decimal_json_issue(self, project_path: str) -> List[DetectionIssue]:
        """检测Decimal JSON序列化问题"""
        issues = []
        
        for py_file in self._get_python_files(project_path):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检测Decimal和jsonify的使用
                if 'decimal' in content and 'jsonify' in content:
                    issues.append(DetectionIssue(
                        id="4157",
                        title="Decimal JSON序列化问题",
                        severity="error",
                        capability=DetectionCapability.AI_ASSISTED,
                        file_path=py_file,
                        message="Decimal类型在Flask 2.0.0中JSON序列化可能失败",
                        suggestion="使用自定义JSON编码器处理Decimal类型",
                        github_issue="https://github.com/pallets/flask/issues/4157",
                        category="serialization"
                    ))
                    
            except Exception as e:
                print(f"检测Decimal JSON问题失败 {py_file}: {e}")
                continue
        
        return issues
    
    async def _detect_nested_blueprint_issue(self, project_path: str) -> List[DetectionIssue]:
        """检测嵌套蓝图问题"""
        issues = []
        
        for py_file in self._get_python_files(project_path):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检测嵌套蓝图注册
                if 'Blueprint' in content and 'register_blueprint' in content:
                    # 检查是否有嵌套的蓝图注册
                    lines = content.split('\n')
                    blueprint_names = []
                    for line in lines:
                        if 'Blueprint(' in line:
                            # 提取蓝图名称
                            if 'name=' in line:
                                start = line.find('name=') + 5
                                end = line.find(',', start)
                                if end == -1:
                                    end = line.find(')', start)
                                name = line[start:end].strip().strip('"\'')
                                blueprint_names.append(name)
                    
                    # 检查是否有重复的蓝图名称
                    if len(blueprint_names) != len(set(blueprint_names)):
                        issues.append(DetectionIssue(
                            id="4069",
                            title="嵌套蓝图注册为点分名",
                            severity="warning",
                            capability=DetectionCapability.AI_ASSISTED,
                            file_path=py_file,
                            message="嵌套蓝图可能导致端点命名冲突",
                            suggestion="使用点分命名避免冲突",
                            github_issue="https://github.com/pallets/flask/issues/4069",
                            category="blueprint"
                        ))
                    
            except Exception as e:
                print(f"检测嵌套蓝图问题失败 {py_file}: {e}")
                continue
        
        return issues
    
    async def _detect_decorator_factory_advanced(self, project_path: str) -> List[DetectionIssue]:
        """检测装饰器工厂问题（高级版本）"""
        issues = []
        
        for py_file in self._get_python_files(project_path):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检测装饰器工厂模式
                if 'def ' in content and '@' in content:
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        # 检测装饰器工厂函数
                        if 'def ' in line and ('decorator' in line.lower() or 'wrapper' in line.lower()):
                            # 检查是否有类型注解
                            if 'Callable' not in content and 'typing' not in content:
                                issues.append(DetectionIssue(
                                    id="4060",
                                    title="装饰器工厂类型改进",
                                    severity="warning",
                                    capability=DetectionCapability.STATIC,
                                    file_path=py_file,
                                    line_number=i + 1,
                                    message="装饰器工厂缺少类型注解",
                                    suggestion="为装饰器工厂添加Callable类型注解",
                                    github_issue="https://github.com/pallets/flask/issues/4060",
                                    category="typing"
                                ))
                    
            except Exception as e:
                print(f"检测装饰器工厂问题失败 {py_file}: {e}")
                continue
        
        return issues

class EnhancedFlaskDetector:
    """增强的Flask检测器 - 集成所有检测能力"""
    
    def __init__(self):
        self.type_checker = TypeCheckerIntegration()
        self.static_analyzer = StaticAnalysisIntegration()
        self.api_detector = APIChangeDetection()
    
    async def detect_flask_2_0_0_issues(self, project_path: str) -> Dict[str, Any]:
        """检测Flask 2.0.0问题"""
        print("开始增强Flask 2.0.0问题检测...")
        
        all_issues = []
        
        # 类型检查器检测 (S类问题)
        print("运行类型检查器...")
        mypy_issues = await self.type_checker.run_mypy_analysis(project_path)
        pyright_issues = await self.type_checker.run_pyright_analysis(project_path)
        all_issues.extend(mypy_issues)
        all_issues.extend(pyright_issues)
        
        # 静态分析工具检测 (S类和A类问题)
        print("运行静态分析工具...")
        pylint_issues = await self.static_analyzer.run_pylint_analysis(project_path)
        astroid_issues = await self.static_analyzer.run_astroid_analysis(project_path)
        all_issues.extend(pylint_issues)
        all_issues.extend(astroid_issues)
        
        # API变更检测 (A类问题)
        print("运行API变更检测...")
        api_issues = await self.api_detector.detect_api_changes(project_path)
        all_issues.extend(api_issues)
        
        # 按能力分类统计
        issues_by_capability = {
            DetectionCapability.STATIC.value: [],
            DetectionCapability.AI_ASSISTED.value: [],
            DetectionCapability.DYNAMIC.value: []
        }
        
        for issue in all_issues:
            issues_by_capability[issue.capability.value].append(issue)
        
        # 按严重程度统计
        issues_by_severity = {}
        for issue in all_issues:
            severity = issue.severity
            issues_by_severity[severity] = issues_by_severity.get(severity, 0) + 1
        
        return {
            "detection_type": "enhanced_flask_2_0_0",
            "total_issues": len(all_issues),
            "issues": all_issues,
            "issues_by_capability": {
                capability: len(issues) for capability, issues in issues_by_capability.items()
            },
            "issues_by_severity": issues_by_severity,
            "capability_breakdown": {
                "static_detectable": len(issues_by_capability[DetectionCapability.STATIC.value]),
                "ai_assisted": len(issues_by_capability[DetectionCapability.AI_ASSISTED.value]),
                "dynamic_verification": len(issues_by_capability[DetectionCapability.DYNAMIC.value])
            },
            "detection_tools": {
                "mypy_available": self.type_checker.mypy_available,
                "pyright_available": self.type_checker.pyright_available,
                "pylint_available": self.static_analyzer.pylint_available,
                "astroid_available": self.static_analyzer.astroid_available
            }
        }
