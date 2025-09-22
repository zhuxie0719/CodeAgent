"""
简化的静态代码检测器
用于演示AI AGENT系统的缺陷检测功能
"""

import os
import ast
import re
import json
from typing import List, Dict, Any, Optional
from pathlib import Path


class StaticDetector:
    """静态代码检测器"""
    
    def __init__(self):
        self.issues = []
        self.rules = {
            'unused_imports': True,
            'hardcoded_secrets': True,
            'unsafe_eval': True,
            'missing_type_hints': True,
            'long_functions': True,
            'duplicate_code': True,
            'bad_exception_handling': True,
            'global_variables': True,
            'magic_numbers': True,
            'unsafe_file_operations': True,
            'missing_docstrings': True,
            'bad_naming': True,
            'unhandled_exceptions': True,
            'deep_nesting': True,
            'insecure_random': True,
            'memory_leaks': True,
            'missing_input_validation': True,
            'bad_formatting': True,
            'dead_code': True,
            'unused_variables': True
        }
    
    def detect_issues(self, file_path: str) -> List[Dict[str, Any]]:
        """检测文件中的问题
        
        Args:
            file_path: 文件路径
            
        Returns:
            List[Dict[str, Any]]: 问题列表
        """
        self.issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析AST
            tree = ast.parse(content)
            
            # 执行各种检测规则
            self._check_unused_imports(tree, content)
            self._check_hardcoded_secrets(content)
            self._check_unsafe_eval(content)
            self._check_missing_type_hints(tree, content)
            self._check_long_functions(tree)
            self._check_duplicate_code(content)
            self._check_bad_exception_handling(tree)
            self._check_global_variables(tree)
            self._check_magic_numbers(content)
            self._check_unsafe_file_operations(content)
            self._check_missing_docstrings(tree)
            self._check_bad_naming(tree)
            self._check_unhandled_exceptions(tree)
            self._check_deep_nesting(tree)
            self._check_insecure_random(content)
            self._check_memory_leaks(content)
            self._check_missing_input_validation(content)
            self._check_bad_formatting(content)
            self._check_dead_code(tree)
            self._check_unused_variables(tree, content)
            
        except Exception as e:
            self.issues.append({
                'type': 'parse_error',
                'severity': 'error',
                'message': f'文件解析失败: {e}',
                'line': 0,
                'file': file_path
            })
        
        return self.issues
    
    def _check_unused_imports(self, tree: ast.AST, content: str):
        """检查未使用的导入"""
        if not self.rules['unused_imports']:
            return
        
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        for import_name in imports:
            if import_name not in content.replace(f'import {import_name}', ''):
                self.issues.append({
                    'type': 'unused_import',
                    'severity': 'warning',
                    'message': f'未使用的导入: {import_name}',
                    'line': 0,
                    'file': ''
                })
    
    def _check_hardcoded_secrets(self, content: str):
        """检查硬编码的秘密信息"""
        if not self.rules['hardcoded_secrets']:
            return
        
        # 检查密码模式
        password_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']'
        ]
        
        for i, line in enumerate(content.split('\n'), 1):
            for pattern in password_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    self.issues.append({
                        'type': 'hardcoded_secret',
                        'severity': 'error',
                        'message': '发现硬编码的秘密信息',
                        'line': i,
                        'file': ''
                    })
    
    def _check_unsafe_eval(self, content: str):
        """检查不安全的eval使用"""
        if not self.rules['unsafe_eval']:
            return
        
        for i, line in enumerate(content.split('\n'), 1):
            if 'eval(' in line:
                self.issues.append({
                    'type': 'unsafe_eval',
                    'severity': 'error',
                    'message': '使用了不安全的eval函数',
                    'line': i,
                    'file': ''
                })
    
    def _check_missing_type_hints(self, tree: ast.AST, content: str):
        """检查缺少类型注解"""
        if not self.rules['missing_type_hints']:
            return
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 检查函数参数类型注解
                for arg in node.args.args:
                    if arg.annotation is None:
                        self.issues.append({
                            'type': 'missing_type_hint',
                            'severity': 'info',
                            'message': f'函数 {node.name} 的参数 {arg.arg} 缺少类型注解',
                            'line': node.lineno,
                            'file': ''
                        })
                
                # 检查函数返回类型注解
                if node.returns is None:
                    self.issues.append({
                        'type': 'missing_type_hint',
                        'severity': 'info',
                        'message': f'函数 {node.name} 缺少返回类型注解',
                        'line': node.lineno,
                        'file': ''
                    })
    
    def _check_long_functions(self, tree: ast.AST):
        """检查过长的函数"""
        if not self.rules['long_functions']:
            return
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # 计算函数行数
                lines = node.end_lineno - node.lineno + 1 if hasattr(node, 'end_lineno') else 0
                if lines > 50:  # 超过50行认为过长
                    self.issues.append({
                        'type': 'long_function',
                        'severity': 'warning',
                        'message': f'函数 {node.name} 过长 ({lines} 行)，建议拆分',
                        'line': node.lineno,
                        'file': ''
                    })
    
    def _check_duplicate_code(self, content: str):
        """检查重复代码"""
        if not self.rules['duplicate_code']:
            return
        
        lines = content.split('\n')
        function_blocks = []
        
        # 简单的重复代码检测
        for i, line in enumerate(lines):
            if line.strip().startswith('def '):
                # 找到函数定义
                func_lines = []
                j = i
                while j < len(lines) and (lines[j].startswith('    ') or lines[j].strip() == ''):
                    func_lines.append(lines[j])
                    j += 1
                
                if len(func_lines) > 5:  # 只检查较长的函数
                    function_blocks.append((i, func_lines))
        
        # 检查相似的函数
        for i, (line1, func1) in enumerate(function_blocks):
            for j, (line2, func2) in enumerate(function_blocks[i+1:], i+1):
                if len(func1) == len(func2):
                    # 简单的相似度检查
                    similar_lines = sum(1 for l1, l2 in zip(func1, func2) if l1.strip() == l2.strip())
                    if similar_lines > len(func1) * 0.8:  # 80%相似度
                        self.issues.append({
                            'type': 'duplicate_code',
                            'severity': 'warning',
                            'message': f'发现重复代码，行 {line1} 和行 {line2}',
                            'line': line1,
                            'file': ''
                        })
    
    def _check_bad_exception_handling(self, tree: ast.AST):
        """检查异常处理不当"""
        if not self.rules['bad_exception_handling']:
            return
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:  # 裸露的except
                    self.issues.append({
                        'type': 'bad_exception_handling',
                        'severity': 'warning',
                        'message': '使用了裸露的except语句，应该指定具体的异常类型',
                        'line': node.lineno,
                        'file': ''
                    })
    
    def _check_global_variables(self, tree: ast.AST):
        """检查全局变量使用"""
        if not self.rules['global_variables']:
            return
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Global):
                self.issues.append({
                    'type': 'global_variable',
                    'severity': 'warning',
                    'message': '使用了全局变量，建议避免',
                    'line': node.lineno,
                    'file': ''
                })
    
    def _check_magic_numbers(self, content: str):
        """检查魔法数字"""
        if not self.rules['magic_numbers']:
            return
        
        magic_number_patterns = [
            r'\b(18|65|100|1000|9999)\b'  # 常见的魔法数字
        ]
        
        for i, line in enumerate(content.split('\n'), 1):
            for pattern in magic_number_patterns:
                if re.search(pattern, line):
                    self.issues.append({
                        'type': 'magic_number',
                        'severity': 'info',
                        'message': '发现魔法数字，建议定义为常量',
                        'line': i,
                        'file': ''
                    })
    
    def _check_unsafe_file_operations(self, content: str):
        """检查不安全的文件操作"""
        if not self.rules['unsafe_file_operations']:
            return
        
        unsafe_patterns = [
            r'/tmp/',
            r'C:\\temp\\',
            r'C:\\Windows\\Temp\\'
        ]
        
        for i, line in enumerate(content.split('\n'), 1):
            for pattern in unsafe_patterns:
                if re.search(pattern, line):
                    self.issues.append({
                        'type': 'unsafe_file_operation',
                        'severity': 'warning',
                        'message': '使用了硬编码的临时文件路径',
                        'line': i,
                        'file': ''
                    })
    
    def _check_missing_docstrings(self, tree: ast.AST):
        """检查缺少文档字符串"""
        if not self.rules['missing_docstrings']:
            return
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and not node.name.startswith('_'):
                if not ast.get_docstring(node):
                    self.issues.append({
                        'type': 'missing_docstring',
                        'severity': 'info',
                        'message': f'函数 {node.name} 缺少文档字符串',
                        'line': node.lineno,
                        'file': ''
                    })
            elif isinstance(node, ast.ClassDef):
                if not ast.get_docstring(node):
                    self.issues.append({
                        'type': 'missing_docstring',
                        'severity': 'info',
                        'message': f'类 {node.name} 缺少文档字符串',
                        'line': node.lineno,
                        'file': ''
                    })
    
    def _check_bad_naming(self, tree: ast.AST):
        """检查命名不规范"""
        if not self.rules['bad_naming']:
            return
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not re.match(r'^[a-z_][a-z0-9_]*$', node.name):
                    self.issues.append({
                        'type': 'bad_naming',
                        'severity': 'warning',
                        'message': f'函数名 {node.name} 不符合命名规范',
                        'line': node.lineno,
                        'file': ''
                    })
    
    def _check_unhandled_exceptions(self, tree: ast.AST):
        """检查未处理的异常"""
        if not self.rules['unhandled_exceptions']:
            return
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Div):
                # 检查除法操作是否在try-except中
                parent = getattr(node, 'parent', None)
                if not self._is_in_try_except(node, tree):
                    self.issues.append({
                        'type': 'unhandled_exception',
                        'severity': 'warning',
                        'message': '除法操作可能抛出ZeroDivisionError，建议添加异常处理',
                        'line': node.lineno,
                        'file': ''
                    })
    
    def _check_deep_nesting(self, tree: ast.AST):
        """检查过深的嵌套"""
        if not self.rules['deep_nesting']:
            return
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                max_depth = self._calculate_nesting_depth(node)
                if max_depth > 4:  # 超过4层嵌套
                    self.issues.append({
                        'type': 'deep_nesting',
                        'severity': 'warning',
                        'message': f'函数 {node.name} 嵌套过深 ({max_depth} 层)',
                        'line': node.lineno,
                        'file': ''
                    })
    
    def _check_insecure_random(self, content: str):
        """检查不安全的随机数使用"""
        if not self.rules['insecure_random']:
            return
        
        for i, line in enumerate(content.split('\n'), 1):
            if 'random.randint' in line or 'random.choice' in line:
                self.issues.append({
                    'type': 'insecure_random',
                    'severity': 'warning',
                    'message': '使用了不安全的随机数生成，建议使用secrets模块',
                    'line': i,
                    'file': ''
                })
    
    def _check_memory_leaks(self, content: str):
        """检查内存泄漏风险"""
        if not self.rules['memory_leaks']:
            return
        
        for i, line in enumerate(content.split('\n'), 1):
            if 'range(1000000)' in line or 'range(100000)' in line:
                self.issues.append({
                    'type': 'memory_leak',
                    'severity': 'warning',
                    'message': '可能的内存泄漏风险，大对象没有及时清理',
                    'line': i,
                    'file': ''
                })
    
    def _check_missing_input_validation(self, content: str):
        """检查缺少输入验证"""
        if not self.rules['missing_input_validation']:
            return
        
        for i, line in enumerate(content.split('\n'), 1):
            if 'def process_user_input' in line or 'def handle_input' in line:
                # 检查函数是否包含验证逻辑
                func_content = self._extract_function_content(content, i)
                if not any(keyword in func_content for keyword in ['if', 'validate', 'check', 'strip()']):
                    self.issues.append({
                        'type': 'missing_input_validation',
                        'severity': 'warning',
                        'message': '用户输入处理函数缺少输入验证',
                        'line': i,
                        'file': ''
                    })
    
    def _check_bad_formatting(self, content: str):
        """检查代码格式问题"""
        if not self.rules['bad_formatting']:
            return
        
        for i, line in enumerate(content.split('\n'), 1):
            # 检查缩进问题
            if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                if 'def ' in line or 'class ' in line or 'if ' in line or 'for ' in line or 'while ' in line:
                    continue
            elif line.strip() and line.startswith(' '):
                # 检查缩进是否一致
                spaces = len(line) - len(line.lstrip())
                if spaces % 4 != 0:
                    self.issues.append({
                        'type': 'bad_formatting',
                        'severity': 'info',
                        'message': '缩进不一致，建议使用4个空格',
                        'line': i,
                        'file': ''
                    })
    
    def _check_dead_code(self, tree: ast.AST):
        """检查死代码"""
        if not self.rules['dead_code']:
            return
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith('unused_') or 'unused' in node.name.lower():
                    self.issues.append({
                        'type': 'dead_code',
                        'severity': 'info',
                        'message': f'函数 {node.name} 可能未被使用',
                        'line': node.lineno,
                        'file': ''
                    })
    
    def _check_unused_variables(self, tree: ast.AST, content: str):
        """检查未使用的变量"""
        if not self.rules['unused_variables']:
            return
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id
                        if var_name.startswith('unused_') or 'unused' in var_name.lower():
                            self.issues.append({
                                'type': 'unused_variable',
                                'severity': 'warning',
                                'message': f'变量 {var_name} 可能未被使用',
                                'line': node.lineno,
                                'file': ''
                            })
    
    def _is_in_try_except(self, node: ast.AST, tree: ast.AST) -> bool:
        """检查节点是否在try-except块中"""
        # 简化的实现，实际应该遍历AST树
        return False
    
    def _calculate_nesting_depth(self, node: ast.AST) -> int:
        """计算嵌套深度"""
        max_depth = 0
        current_depth = 0
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.With)):
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif isinstance(child, (ast.FunctionDef, ast.ClassDef)):
                # 重置深度，因为这是新的作用域
                current_depth = 0
        
        return max_depth
    
    def _extract_function_content(self, content: str, start_line: int) -> str:
        """提取函数内容"""
        lines = content.split('\n')
        func_lines = []
        
        i = start_line - 1
        indent_level = len(lines[i]) - len(lines[i].lstrip())
        
        i += 1
        while i < len(lines):
            line = lines[i]
            if line.strip() == '':
                func_lines.append(line)
                i += 1
                continue
            
            current_indent = len(line) - len(line.lstrip())
            if current_indent <= indent_level and line.strip():
                break
            
            func_lines.append(line)
            i += 1
        
        return '\n'.join(func_lines)
    
    def generate_report(self, issues: List[Dict[str, Any]]) -> str:
        """生成检测报告"""
        if not issues:
            return "✅ 未发现代码问题！"
        
        report = f"🔍 代码检测报告\n"
        report += f"发现 {len(issues)} 个问题\n\n"
        
        # 按严重程度分组
        severity_groups = {'error': [], 'warning': [], 'info': []}
        for issue in issues:
            severity_groups[issue['severity']].append(issue)
        
        for severity, issues_list in severity_groups.items():
            if issues_list:
                severity_emoji = {'error': '❌', 'warning': '⚠️', 'info': 'ℹ️'}
                report += f"{severity_emoji[severity]} {severity.upper()} ({len(issues_list)} 个)\n"
                
                for issue in issues_list:
                    report += f"  • 行 {issue['line']}: {issue['message']}\n"
                report += "\n"
        
        return report
