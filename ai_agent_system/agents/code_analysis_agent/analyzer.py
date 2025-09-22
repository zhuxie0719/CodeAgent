"""
代码分析器模块
"""

import os
import ast
import json
from typing import Dict, List, Any, Optional
from pathlib import Path


class ProjectAnalyzer:
    """项目结构分析器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    async def analyze_structure(self, project_path: str) -> Dict[str, Any]:
        """分析项目结构"""
        structure = {
            'files': [],
            'directories': [],
            'file_types': {},
            'total_lines': 0
        }
        
        for root, dirs, files in os.walk(project_path):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, project_path)
                
                # 获取文件信息
                file_info = {
                    'path': relative_path,
                    'size': os.path.getsize(file_path),
                    'extension': os.path.splitext(file)[1]
                }
                
                # 计算代码行数
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = len(f.readlines())
                        file_info['lines'] = lines
                        structure['total_lines'] += lines
                except:
                    file_info['lines'] = 0
                
                structure['files'].append(file_info)
                
                # 统计文件类型
                ext = file_info['extension']
                structure['file_types'][ext] = structure['file_types'].get(ext, 0) + 1
        
        return structure


class CodeAnalyzer:
    """代码质量分析器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    async def analyze_quality(self, project_path: str) -> Dict[str, Any]:
        """分析代码质量"""
        quality_metrics = {
            'complexity': {},
            'maintainability': {},
            'duplication': {},
            'issues': []
        }
        
        # 分析Python文件
        for root, dirs, files in os.walk(project_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    await self._analyze_python_file(file_path, quality_metrics)
        
        return quality_metrics
    
    async def _analyze_python_file(self, file_path: str, metrics: Dict[str, Any]):
        """分析Python文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析AST
            tree = ast.parse(content)
            
            # 计算复杂度
            complexity = self._calculate_complexity(tree)
            metrics['complexity'][file_path] = complexity
            
        except Exception as e:
            metrics['issues'].append({
                'file': file_path,
                'type': 'parse_error',
                'message': str(e)
            })
    
    def _calculate_complexity(self, tree: ast.AST) -> int:
        """计算代码复杂度"""
        complexity = 1  # 基础复杂度
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
        
        return complexity


class DependencyAnalyzer:
    """依赖关系分析器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    async def analyze_dependencies(self, project_path: str) -> Dict[str, Any]:
        """分析项目依赖"""
        dependencies = {
            'python_packages': [],
            'node_modules': [],
            'imports': {},
            'circular_dependencies': []
        }
        
        # 分析requirements.txt
        req_file = os.path.join(project_path, 'requirements.txt')
        if os.path.exists(req_file):
            with open(req_file, 'r') as f:
                dependencies['python_packages'] = [line.strip() for line in f if line.strip()]
        
        # 分析package.json
        package_file = os.path.join(project_path, 'package.json')
        if os.path.exists(package_file):
            with open(package_file, 'r') as f:
                package_data = json.load(f)
                dependencies['node_modules'] = list(package_data.get('dependencies', {}).keys())
        
        return dependencies
