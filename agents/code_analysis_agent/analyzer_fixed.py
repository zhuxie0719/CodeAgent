import os
import json
import ast
import re
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
import networkx as nx
from api.deepseek_config import DeepSeekConfig

@dataclass
class CodeComplexityMetrics:
    """代码复杂度指标"""
    cyclomatic_complexity: int = 0
    cognitive_complexity: int = 0
    lines_of_code: int = 0
    function_count: int = 0
    class_count: int = 0
    nested_depth: int = 0
    parameter_count: int = 0

@dataclass
class ProjectIntent:
    """项目意图信息"""
    project_type: str
    main_purpose: str
    key_features: List[str]
    architecture_pattern: str
    technology_stack: List[str]
    complexity_level: str
    maintainability_score: float
    confidence: float

class AIAnalysisService:
    """AI分析服务"""
    
    def __init__(self):
        self.config = DeepSeekConfig()
    
    async def analyze_code_intent(self, code_content: str, file_path: str, 
                                 complexity_metrics: Dict = None, issues: List = None) -> Dict[str, Any]:
        """使用AI分析代码意图"""
        try:
            # 构建代码分析上下文
            context_info = self._build_code_context(file_path, code_content, complexity_metrics, issues)
            
            prompt = f"""
            作为资深代码审查专家,请对以下代码进行深度分析:

            ## 文件信息
            {context_info['file_info']}

            ## 代码内容
            {context_info['code_content']}

            ## 静态分析结果
            {context_info['static_analysis']}

            请生成一份专业的代码分析报告,包含以下部分:

            1. **代码功能分析** - 主要功能,核心逻辑,设计意图
            2. **代码质量评估** - 可读性,可维护性,健壮性
            3. **设计模式识别** - 使用的设计模式,架构模式
            4. **复杂度分析** - 圈复杂度,认知复杂度评估
            5. **潜在问题识别** - 性能问题,安全问题,逻辑问题
            6. **代码规范检查** - PEP8规范,最佳实践
            7. **改进建议** - 具体的重构和优化建议
            8. **测试建议** - 单元测试,集成测试建议

            请以Markdown格式输出详细的分析报告,每个部分都要有具体的分析和建议。
            """
            
            response = await self.config.generate_response(prompt)
            
            return {
                'success': True,
                'analysis': response,
                'file_path': file_path,
                'context': context_info
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path
            }
    
    def _build_code_context(self, file_path: str, code_content: str, 
                           complexity_metrics: Dict = None, issues: List = None) -> Dict[str, str]:
        """构建代码分析上下文"""
        file_info = f"文件路径: {file_path}\n文件大小: {len(code_content)} 字符"
        
        # 代码内容预览（前500字符）
        code_preview = code_content[:500] + "..." if len(code_content) > 500 else code_content
        
        # 静态分析结果
        static_analysis = ""
        if complexity_metrics:
            static_analysis += f"复杂度指标:\n"
            for key, value in complexity_metrics.items():
                static_analysis += f"  - {key}: {value}\n"
        
        if issues:
            static_analysis += f"\n发现的问题:\n"
            for issue in issues:
                static_analysis += f"  - {issue}\n"
        
        return {
            'file_info': file_info,
            'code_content': code_preview,
            'static_analysis': static_analysis
        }
    
    async def generate_project_summary(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """生成项目总结报告"""
        try:
            # 构建分析摘要
            summary = self._build_analysis_summary(analysis_data)
            
            prompt = f"""
            作为资深软件架构师,请基于以下项目分析数据生成一份详细的项目分析报告:

            {summary}

            请生成一份专业的项目分析报告,包含以下部分:

            1. **项目概览** - 项目类型,主要功能,技术栈
            2. **代码质量评估** - 整体代码质量,可维护性,可读性
            3. **架构分析** - 架构模式,模块设计,依赖关系
            4. **复杂度分析** - 项目复杂度,技术债务评估
            5. **依赖关系评估** - 依赖管理,循环依赖,版本控制
            6. **关键问题识别** - 主要问题,风险点,改进点
            7. **改进建议** - 具体的优化和重构建议
            8. **最佳实践建议** - 开发规范,测试策略,部署建议

            请以Markdown格式输出详细的分析报告,每个部分都要有具体的分析和建议。
            """
            
            response = await self.config.generate_response(prompt)
            
            return {
                'success': True,
                'summary': response,
                'analysis_data': analysis_data
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'analysis_data': analysis_data
            }
    
    def _build_analysis_summary(self, analysis_data: Dict[str, Any]) -> str:
        """构建分析摘要"""
        summary = "## 项目分析数据摘要\n\n"
        
        # 项目信息
        if 'project_info' in analysis_data:
            project_info = analysis_data['project_info']
            summary += f"**项目信息:**\n"
            summary += f"- 项目路径: {project_info.get('path', 'N/A')}\n"
            summary += f"- 文件总数: {project_info.get('total_files', 0)}\n"
            summary += f"- 代码行数: {project_info.get('total_lines', 0)}\n"
            summary += f"- 项目类型: {project_info.get('project_type', 'N/A')}\n"
            summary += f"- 主要语言: {project_info.get('primary_language', 'N/A')}\n\n"
        
        # 代码质量
        if 'code_quality' in analysis_data:
            quality = analysis_data['code_quality']
            summary += f"**代码质量:**\n"
            summary += f"- 平均复杂度: {quality.get('average_complexity', 0)}\n"
            summary += f"- 问题总数: {quality.get('total_issues', 0)}\n"
            summary += f"- 可维护性评分: {quality.get('maintainability_score', 0)}\n\n"
        
        # 依赖信息
        if 'dependencies' in analysis_data:
            deps = analysis_data['dependencies']
            summary += f"**依赖信息:**\n"
            summary += f"- Python包: {len(deps.get('python_packages', []))}\n"
            summary += f"- Node模块: {len(deps.get('node_modules', []))}\n"
            summary += f"- 循环依赖: {deps.get('circular_dependencies', [])}\n\n"
        
        # 项目意图
        if 'project_intent' in analysis_data:
            intent = analysis_data['project_intent']
            summary += f"**项目意图:**\n"
            summary += f"- 项目类型: {intent.get('project_type', 'N/A')}\n"
            summary += f"- 主要目的: {intent.get('main_purpose', 'N/A')}\n"
            summary += f"- 复杂度等级: {intent.get('complexity_level', 'N/A')}\n"
            summary += f"- 置信度: {intent.get('confidence', 0)}\n\n"
        
        return summary

class ProjectAnalyzer:
    """项目结构分析器"""
    
    def __init__(self):
        self.ignored_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'env', '.env'}
        self.ignored_extensions = {'.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe'}
    
    async def analyze_project_structure(self, project_path: str) -> Dict[str, Any]:
        """分析项目结构"""
        if not os.path.exists(project_path):
            return {'error': f'项目路径不存在: {project_path}'}
        
        structure = {
            'path': project_path,
            'total_files': 0,
            'total_lines': 0,
            'file_types': defaultdict(int),
            'directories': [],
            'files': [],
            'project_type': 'unknown',
            'framework': 'unknown',
            'primary_language': 'unknown',
            'has_tests': False,
            'has_docs': False,
            'has_config': False
        }
        
        # 遍历项目目录
        for root, dirs, files in os.walk(project_path):
            # 过滤忽略的目录
            dirs[:] = [d for d in dirs if d not in self.ignored_dirs]
            
            # 分析目录
            rel_root = os.path.relpath(root, project_path)
            if rel_root != '.':
                structure['directories'].append(rel_root)
            
            # 分析文件
            for file in files:
                if any(file.endswith(ext) for ext in self.ignored_extensions):
                    continue
                
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, project_path)
                
                # 获取文件信息
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        lines = len(content.splitlines())
                except:
                    lines = 0
                
                # 文件类型统计
                ext = os.path.splitext(file)[1].lower()
                structure['file_types'][ext] += 1
                
                structure['files'].append({
                    'path': rel_path,
                    'lines': lines,
                    'size': os.path.getsize(file_path)
                })
                
                structure['total_files'] += 1
                structure['total_lines'] += lines
        
        # 推断项目类型
        structure['project_type'] = self._infer_project_type(structure)
        structure['framework'] = self._infer_framework(structure)
        structure['primary_language'] = self._infer_primary_language(structure)
        structure['has_tests'] = self._has_tests(structure)
        structure['has_docs'] = self._has_docs(structure)
        structure['has_config'] = self._has_config(structure)
        
        return structure
    
    def _infer_project_type(self, structure: Dict[str, Any]) -> str:
        """推断项目类型"""
        files = [f['path'] for f in structure['files']]
        
        if any('requirements.txt' in f for f in files):
            return 'python'
        elif any('package.json' in f for f in files):
            return 'nodejs'
        elif any('pom.xml' in f for f in files):
            return 'java'
        elif any('Cargo.toml' in f for f in files):
            return 'rust'
        elif any('go.mod' in f for f in files):
            return 'go'
        else:
            return 'unknown'
    
    def _infer_framework(self, structure: Dict[str, Any]) -> str:
        """推断框架"""
        files = [f['path'] for f in structure['files']]
        
        if any('django' in f.lower() for f in files):
            return 'django'
        elif any('flask' in f.lower() for f in files):
            return 'flask'
        elif any('fastapi' in f.lower() for f in files):
            return 'fastapi'
        elif any('react' in f.lower() for f in files):
            return 'react'
        elif any('vue' in f.lower() for f in files):
            return 'vue'
        else:
            return 'unknown'
    
    def _infer_primary_language(self, structure: Dict[str, Any]) -> str:
        """推断主要语言"""
        file_types = structure['file_types']
        
        if file_types['.py'] > 0:
            return 'python'
        elif file_types['.js'] > 0 or file_types['.ts'] > 0:
            return 'javascript'
        elif file_types['.java'] > 0:
            return 'java'
        elif file_types['.rs'] > 0:
            return 'rust'
        elif file_types['.go'] > 0:
            return 'go'
        else:
            return 'unknown'
    
    def _has_tests(self, structure: Dict[str, Any]) -> bool:
        """检查是否有测试文件"""
        files = [f['path'] for f in structure['files']]
        return any('test' in f.lower() or 'spec' in f.lower() for f in files)
    
    def _has_docs(self, structure: Dict[str, Any]) -> bool:
        """检查是否有文档"""
        files = [f['path'] for f in structure['files']]
        return any('readme' in f.lower() or 'doc' in f.lower() for f in files)
    
    def _has_config(self, structure: Dict[str, Any]) -> bool:
        """检查是否有配置文件"""
        files = [f['path'] for f in structure['files']]
        config_files = ['config', 'settings', 'conf', 'ini', 'yaml', 'yml', 'json']
        return any(any(cf in f.lower() for cf in config_files) for f in files)

class CodeAnalyzer:
    """代码质量分析器"""
    
    def __init__(self, ai_service: AIAnalysisService):
        self.ai_service = ai_service
        self.supported_extensions = {'.py', '.js', '.ts', '.java', '.c', '.cpp', '.h', '.hpp'}
    
    async def analyze_code_quality(self, project_path: str) -> Dict[str, Any]:
        """分析代码质量"""
        quality_metrics = {
            'total_files': 0,
            'analyzed_files': 0,
            'total_lines': 0,
            'total_functions': 0,
            'total_classes': 0,
            'average_complexity': 0,
            'max_complexity': 0,
            'total_issues': 0,
            'issues_by_type': defaultdict(int),
            'complexity_distribution': defaultdict(int),
            'maintainability_score': 0,
            'file_analysis': [],
            'ai_analysis': []
        }
        
        # 分析所有代码文件
        for root, dirs, files in os.walk(project_path):
            for file in files:
                if any(file.endswith(ext) for ext in self.supported_extensions):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, project_path)
                    
                    # 分析单个文件
                    file_analysis = await self._analyze_code_file(file_path, rel_path)
                    quality_metrics['file_analysis'].append(file_analysis)
                    
                    # 更新统计信息
                    quality_metrics['total_files'] += 1
                    quality_metrics['analyzed_files'] += 1
                    quality_metrics['total_lines'] += file_analysis['lines_of_code']
                    quality_metrics['total_functions'] += file_analysis['function_count']
                    quality_metrics['total_classes'] += file_analysis['class_count']
                    quality_metrics['total_issues'] += len(file_analysis['issues'])
                    
                    # 复杂度统计
                    complexity = file_analysis['complexity_metrics']['cyclomatic_complexity']
                    quality_metrics['max_complexity'] = max(quality_metrics['max_complexity'], complexity)
                    quality_metrics['complexity_distribution'][complexity] += 1
                    
                    # 问题类型统计
                    for issue in file_analysis['issues']:
                        issue_type = issue.get('type', 'unknown')
                        quality_metrics['issues_by_type'][issue_type] += 1
        
        # 计算平均复杂度
        if quality_metrics['analyzed_files'] > 0:
            quality_metrics['average_complexity'] = sum(
                f['complexity_metrics']['cyclomatic_complexity'] 
                for f in quality_metrics['file_analysis']
            ) / quality_metrics['analyzed_files']
        
        # 计算可维护性评分
        quality_metrics['maintainability_score'] = self._calculate_maintainability_score(quality_metrics)
        
        return quality_metrics
    
    async def _analyze_code_file(self, file_path: str, rel_path: str) -> Dict[str, Any]:
        """分析单个代码文件"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except:
            return {
                'file_path': rel_path,
                'error': '无法读取文件',
                'lines_of_code': 0,
                'function_count': 0,
                'class_count': 0,
                'complexity_metrics': CodeComplexityMetrics().__dict__,
                'issues': []
            }
        
        # 根据文件扩展名选择分析方法
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.py':
            return await self._analyze_python_file(file_path, rel_path, content)
        elif ext in {'.js', '.ts'}:
            return await self._analyze_javascript_file(file_path, rel_path, content)
        elif ext == '.java':
            return await self._analyze_java_file(file_path, rel_path, content)
        else:
            return await self._analyze_generic_file(file_path, rel_path, content)
    
    async def _analyze_python_file(self, file_path: str, rel_path: str, content: str) -> Dict[str, Any]:
        """分析Python文件"""
        try:
            tree = ast.parse(content)
        except:
            return {
                'file_path': rel_path,
                'error': '语法错误',
                'lines_of_code': len(content.splitlines()),
                'function_count': 0,
                'class_count': 0,
                'complexity_metrics': CodeComplexityMetrics().__dict__,
                'issues': [{'type': 'syntax_error', 'message': '文件包含语法错误'}]
            }
        
        # 计算复杂度指标
        complexity_metrics = self._calculate_python_complexity(tree)
        
        # 检测问题
        issues = self._detect_python_issues(tree, content)
        
        # AI分析
        ai_analysis = await self.ai_service.analyze_code_intent(
            content, rel_path, complexity_metrics.__dict__, issues
        )
        
        return {
            'file_path': rel_path,
            'lines_of_code': len(content.splitlines()),
            'function_count': len([node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]),
            'class_count': len([node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]),
            'complexity_metrics': complexity_metrics.__dict__,
            'issues': issues,
            'ai_analysis': ai_analysis
        }
    
    def _calculate_python_complexity(self, tree: ast.AST) -> CodeComplexityMetrics:
        """计算Python代码复杂度"""
        metrics = CodeComplexityMetrics()
        
        for node in ast.walk(tree):
            # 圈复杂度
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor, ast.ExceptHandler, ast.With, ast.AsyncWith)):
                metrics.cyclomatic_complexity += 1
            elif isinstance(node, ast.BoolOp):
                metrics.cyclomatic_complexity += len(node.values) - 1
            
            # 函数和类计数
            if isinstance(node, ast.FunctionDef):
                metrics.function_count += 1
                metrics.parameter_count += len(node.args.args)
            elif isinstance(node, ast.ClassDef):
                metrics.class_count += 1
            
            # 嵌套深度
            if hasattr(node, 'lineno'):
                depth = self._calculate_nested_depth(node)
                metrics.nested_depth = max(metrics.nested_depth, depth)
        
        return metrics
    
    def _calculate_nested_depth(self, node: ast.AST) -> int:
        """计算嵌套深度"""
        depth = 0
        current = node
        while hasattr(current, 'parent'):
            current = current.parent
            depth += 1
        return depth
    
    def _detect_python_issues(self, tree: ast.AST, content: str) -> List[Dict[str, str]]:
        """检测Python代码问题"""
        issues = []
        
        # 检测长函数
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.end_lineno and node.lineno:
                    lines = node.end_lineno - node.lineno
                    if lines > 50:
                        issues.append({
                            'type': 'long_function',
                            'message': f'函数 {node.name} 过长 ({lines} 行)',
                            'line': node.lineno
                        })
        
        # 检测长类
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if node.end_lineno and node.lineno:
                    lines = node.end_lineno - node.lineno
                    if lines > 200:
                        issues.append({
                            'type': 'long_class',
                            'message': f'类 {node.name} 过长 ({lines} 行)',
                            'line': node.lineno
                        })
        
        # 检测导入风格
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and '.' in node.module:
                    issues.append({
                        'type': 'import_style',
                        'message': f'建议使用相对导入: {node.module}',
                        'line': node.lineno
                    })
        
        return issues
    
    async def _analyze_javascript_file(self, file_path: str, rel_path: str, content: str) -> Dict[str, Any]:
        """分析JavaScript文件"""
        lines = content.splitlines()
        function_count = len(re.findall(r'function\s+\w+', content))
        class_count = len(re.findall(r'class\s+\w+', content))
        
        # 简单的复杂度计算
        complexity = len(re.findall(r'\b(if|while|for|switch|catch)\b', content))
        
        metrics = CodeComplexityMetrics(
            cyclomatic_complexity=complexity,
            lines_of_code=len(lines),
            function_count=function_count,
            class_count=class_count
        )
        
        return {
            'file_path': rel_path,
            'lines_of_code': len(lines),
            'function_count': function_count,
            'class_count': class_count,
            'complexity_metrics': metrics.__dict__,
            'issues': []
        }
    
    async def _analyze_java_file(self, file_path: str, rel_path: str, content: str) -> Dict[str, Any]:
        """分析Java文件"""
        lines = content.splitlines()
        function_count = len(re.findall(r'public\s+\w+\s+\w+\s*\(', content))
        class_count = len(re.findall(r'class\s+\w+', content))
        
        # 简单的复杂度计算
        complexity = len(re.findall(r'\b(if|while|for|switch|catch)\b', content))
        
        metrics = CodeComplexityMetrics(
            cyclomatic_complexity=complexity,
            lines_of_code=len(lines),
            function_count=function_count,
            class_count=class_count
        )
        
        return {
            'file_path': rel_path,
            'lines_of_code': len(lines),
            'function_count': function_count,
            'class_count': class_count,
            'complexity_metrics': metrics.__dict__,
            'issues': []
        }
    
    async def _analyze_generic_file(self, file_path: str, rel_path: str, content: str) -> Dict[str, Any]:
        """分析通用代码文件"""
        lines = content.splitlines()
        
        metrics = CodeComplexityMetrics(
            lines_of_code=len(lines)
        )
        
        return {
            'file_path': rel_path,
            'lines_of_code': len(lines),
            'function_count': 0,
            'class_count': 0,
            'complexity_metrics': metrics.__dict__,
            'issues': []
        }
    
    def _calculate_maintainability_score(self, quality_metrics: Dict[str, Any]) -> float:
        """计算可维护性评分"""
        score = 100.0
        
        # 基于复杂度扣分
        avg_complexity = quality_metrics['average_complexity']
        if avg_complexity > 10:
            score -= (avg_complexity - 10) * 2
        
        # 基于问题数量扣分
        total_issues = quality_metrics['total_issues']
        score -= total_issues * 0.5
        
        # 基于文件数量扣分（文件过多可能表示结构复杂）
        total_files = quality_metrics['total_files']
        if total_files > 100:
            score -= (total_files - 100) * 0.1
        
        return max(0, min(100, score))

class DependencyAnalyzer:
    """依赖关系分析器"""
    
    def __init__(self):
        self.dependency_graph = nx.DiGraph()
    
    async def analyze_dependencies(self, project_path: str) -> Dict[str, Any]:
        """分析项目依赖"""
        dependencies = {
            'python_packages': [],
            'node_modules': [],
            'rust_crates': [],
            'java_dependencies': [],
            'go_modules': [],
            'import_dependencies': {},
            'circular_dependencies': [],
            'dependency_metrics': {}
        }
        
        # 分析包管理器依赖
        await self._analyze_package_dependencies(project_path, dependencies)
        
        # 分析代码导入依赖
        await self._analyze_code_imports(project_path, dependencies)
        
        # 检测循环依赖
        dependencies['circular_dependencies'] = self._detect_circular_dependencies()
        
        # 计算依赖指标
        dependencies['dependency_metrics'] = self._calculate_dependency_metrics(dependencies)
        
        return dependencies
    
    async def _analyze_package_dependencies(self, project_path: str, dependencies: Dict[str, Any]):
        """分析包管理器依赖"""
        # 分析requirements.txt
        req_file = os.path.join(project_path, 'requirements.txt')
        if os.path.exists(req_file):
            with open(req_file, 'r', encoding='utf-8') as f:
                packages = []
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # 解析包名和版本
                        if '==' in line:
                            name, version = line.split('==', 1)
                            packages.append({'name': name, 'version': version, 'constraint': '=='})
                        elif '>=' in line:
                            name, version = line.split('>=', 1)
                            packages.append({'name': name, 'version': version, 'constraint': '>='})
                        elif '~=' in line:
                            name, version = line.split('~=', 1)
                            packages.append({'name': name, 'version': version, 'constraint': '~='})
                        else:
                            packages.append({'name': line, 'version': None, 'constraint': None})
                dependencies['python_packages'] = packages
        
        # 分析package.json
        package_file = os.path.join(project_path, 'package.json')
        if os.path.exists(package_file):
            try:
                with open(package_file, 'r', encoding='utf-8') as f:
                    package_data = json.load(f)
                    dependencies['node_modules'] = list(package_data.get('dependencies', {}).keys())
                    dependencies['dev_dependencies'] = list(package_data.get('devDependencies', {}).keys())
            except json.JSONDecodeError:
                dependencies['node_modules'] = []
        
        # 分析其他包管理器文件
        await self._analyze_other_package_managers(project_path, dependencies)
    
    async def _analyze_other_package_managers(self, project_path: str, dependencies: Dict[str, Any]):
        """分析其他包管理器"""
        # 分析Cargo.toml (Rust)
        cargo_file = os.path.join(project_path, 'Cargo.toml')
        if os.path.exists(cargo_file):
            dependencies['rust_crates'] = await self._parse_cargo_toml(cargo_file)
        
        # 分析pom.xml (Java)
        pom_file = os.path.join(project_path, 'pom.xml')
        if os.path.exists(pom_file):
            dependencies['java_dependencies'] = await self._parse_pom_xml(pom_file)
        
        # 分析go.mod (Go)
        go_mod_file = os.path.join(project_path, 'go.mod')
        if os.path.exists(go_mod_file):
            dependencies['go_modules'] = await self._parse_go_mod(go_mod_file)
    
    async def _parse_cargo_toml(self, file_path: str) -> List[str]:
        """解析Cargo.toml文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                dependencies = []
                for line in content.split('\n'):
                    line = line.strip()
                    if line.startswith('[') and 'dependencies' in line:
                        # 开始解析依赖块
                        continue
                    elif line and not line.startswith('[') and not line.startswith('#'):
                        # 提取依赖包名
                        if '=' in line:
                            dep_name = line.split('=')[0].strip()
                            dependencies.append(dep_name)
                return dependencies
        except Exception:
            return []
    
    async def _parse_pom_xml(self, file_path: str) -> List[str]:
        """解析pom.xml文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                dependencies = []
                # 简单的XML解析，提取dependency标签
                import re
                matches = re.findall(r'<dependency>.*?<artifactId>(.*?)</artifactId>', content, re.DOTALL)
                dependencies.extend(matches)
                return dependencies
        except Exception:
            return []
    
    async def _parse_go_mod(self, file_path: str) -> List[str]:
        """解析go.mod文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                dependencies = []
                for line in content.split('\n'):
                    line = line.strip()
                    if line.startswith('require ') and '(' in line:
                        # 解析require块
                        continue
                    elif line and not line.startswith('module ') and not line.startswith('go ') and not line.startswith('//'):
                        # 提取依赖包名
                        if ' ' in line:
                            dep_name = line.split()[0]
                            dependencies.append(dep_name)
                return dependencies
        except Exception:
            return []
    
    async def _analyze_code_imports(self, project_path: str, dependencies: Dict[str, Any]):
        """分析代码导入依赖"""
        imports = defaultdict(set)
        internal_modules = set()
        
        # 遍历Python文件
        for root, dirs, files in os.walk(project_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, project_path)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 解析导入语句
                        tree = ast.parse(content)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.Import):
                                for alias in node.names:
                                    imports[rel_path].add(alias.name)
                            elif isinstance(node, ast.ImportFrom):
                                if node.module:
                                    imports[rel_path].add(node.module)
                    except:
                        continue
        
        # 构建依赖图
        for file_path, imported_modules in imports.items():
            self.dependency_graph.add_node(file_path)
            for module in imported_modules:
                # 检查是否为内部模块
                if any(module.startswith(prefix) for prefix in ['agents', 'api', 'config', 'coordinator', 'tools']):
                    internal_modules.add(module)
                    self.dependency_graph.add_edge(file_path, module)
        
        dependencies['import_dependencies'] = dict(imports)
        dependencies['internal_modules'] = list(internal_modules)
    
    def _detect_circular_dependencies(self) -> List[List[str]]:
        """检测循环依赖"""
        try:
            cycles = list(nx.simple_cycles(self.dependency_graph))
            return cycles
        except:
            return []
    
    def _calculate_dependency_metrics(self, dependencies: Dict[str, Any]) -> Dict[str, Any]:
        """计算依赖指标"""
        metrics = {
            'total_packages': 0,
            'total_imports': 0,
            'circular_dependency_count': 0,
            'dependency_depth': 0,
            'coupling_score': 0
        }
        
        # 统计包数量
        for key in ['python_packages', 'node_modules', 'rust_crates', 'java_dependencies', 'go_modules']:
            metrics['total_packages'] += len(dependencies.get(key, []))
        
        # 统计导入数量
        metrics['total_imports'] = sum(len(imports) for imports in dependencies.get('import_dependencies', {}).values())
        
        # 循环依赖数量
        metrics['circular_dependency_count'] = len(dependencies.get('circular_dependencies', []))
        
        # 计算耦合度
        if self.dependency_graph.number_of_nodes() > 0:
            metrics['coupling_score'] = self.dependency_graph.number_of_edges() / self.dependency_graph.number_of_nodes()
        
        return metrics
