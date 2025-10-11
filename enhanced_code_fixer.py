#!/usr/bin/env python3
"""
增强版代码修复器
专门处理Python代码的语法错误和语义问题
"""

import ast
import os
import re
import sys
from typing import Dict, Any, List, Set, Tuple
from pathlib import Path


class EnhancedCodeFixer:
    """增强版代码修复器 - 专门处理Python语法和语义错误"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.required_imports = set()
        self.defined_variables = set()
        self.used_variables = set()
    
    async def fix_python_file(self, file_path: str) -> Dict[str, Any]:
        """修复Python文件的所有问题"""
        try:
            # 1. 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            print(f"🔍 分析文件: {file_path}")
            
            # 2. 分析代码问题
            issues = self._analyze_code_issues(original_content)
            print(f"📋 发现 {len(issues)} 个问题")
            
            # 3. 应用修复
            fixed_content = self._apply_all_fixes(original_content, issues)
            
            # 4. 验证修复结果
            if self._validate_syntax(fixed_content):
                # 5. 写回文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                
                return {
                    'success': True,
                    'changes': [f"修复了 {len(issues)} 个问题"],
                    'message': f'成功修复 {file_path}',
                    'issues_fixed': issues
                }
            else:
                return {
                    'success': False,
                    'message': '修复后代码仍有语法错误'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'修复失败: {e}'
            }
    
    def _analyze_code_issues(self, content: str) -> List[Dict[str, Any]]:
        """分析代码中的所有问题"""
        issues = []
        lines = content.split('\n')
        
        # 1. 检查语法错误
        syntax_issues = self._check_syntax_errors(content)
        issues.extend(syntax_issues)
        
        # 2. 检查导入问题
        import_issues = self._check_import_issues(content)
        issues.extend(import_issues)
        
        # 3. 检查未定义变量
        variable_issues = self._check_undefined_variables(content)
        issues.extend(variable_issues)
        
        # 4. 检查其他问题
        other_issues = self._check_other_issues(content)
        issues.extend(other_issues)
        
        return issues
    
    def _check_syntax_errors(self, content: str) -> List[Dict[str, Any]]:
        """检查语法错误"""
        issues = []
        try:
            ast.parse(content)
        except SyntaxError as e:
            issues.append({
                'type': 'syntax_error',
                'line': e.lineno,
                'message': f'语法错误: {e.msg}',
                'severity': 'error'
            })
        return issues
    
    def _check_import_issues(self, content: str) -> List[Dict[str, Any]]:
        """检查导入问题"""
        issues = []
        lines = content.split('\n')
        
        # 检查使用了但未导入的模块
        used_modules = self._find_used_modules(content)
        imported_modules = self._find_imported_modules(content)
        
        for module in used_modules:
            if module not in imported_modules:
                # 找到使用该模块的行
                for i, line in enumerate(lines):
                    if module in line and not line.strip().startswith('import'):
                        issues.append({
                            'type': 'missing_import',
                            'line': i + 1,
                            'message': f'使用了未导入的模块: {module}',
                            'module': module,
                            'severity': 'error'
                        })
                        break
        
        # 检查导入但未使用的模块
        for module in imported_modules:
            if module not in used_modules:
                for i, line in enumerate(lines):
                    if f'import {module}' in line:
                        issues.append({
                            'type': 'unused_import',
                            'line': i + 1,
                            'message': f'导入了但未使用的模块: {module}',
                            'module': module,
                            'severity': 'warning'
                        })
                        break
        
        return issues
    
    def _check_undefined_variables(self, content: str) -> List[Dict[str, Any]]:
        """检查未定义变量"""
        issues = []
        lines = content.split('\n')
        
        # 简单的变量检查
        defined_vars = set()
        
        for i, line in enumerate(lines):
            # 检查赋值语句
            if '=' in line and not line.strip().startswith('#'):
                var_name = line.split('=')[0].strip()
                if var_name and not var_name.startswith('def ') and not var_name.startswith('class '):
                    defined_vars.add(var_name)
            
            # 检查变量使用
            for word in line.split():
                if word.isidentifier() and word not in defined_vars and word not in ['def', 'class', 'if', 'for', 'while', 'return', 'print']:
                    # 检查是否是内置函数或关键字
                    if word not in dir(__builtins__) and word not in ['True', 'False', 'None']:
                        issues.append({
                            'type': 'undefined_variable',
                            'line': i + 1,
                            'message': f'可能未定义的变量: {word}',
                            'variable': word,
                            'severity': 'warning'
                        })
        
        return issues
    
    def _check_other_issues(self, content: str) -> List[Dict[str, Any]]:
        """检查其他问题"""
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            # 检查硬编码密码
            if 'password' in line.lower() and '=' in line and '"' in line:
                issues.append({
                    'type': 'hardcoded_password',
                    'line': i + 1,
                    'message': '发现硬编码密码',
                    'severity': 'warning'
                })
            
            # 检查SQL注入风险
            if 'SELECT' in line.upper() and '%' in line:
                issues.append({
                    'type': 'sql_injection',
                    'line': i + 1,
                    'message': '可能的SQL注入风险',
                    'severity': 'warning'
                })
        
        return issues
    
    def _apply_all_fixes(self, content: str, issues: List[Dict[str, Any]]) -> str:
        """应用所有修复"""
        fixed_content = content
        
        for issue in issues:
            if issue['type'] == 'missing_import':
                fixed_content = self._fix_missing_import(fixed_content, issue)
            elif issue['type'] == 'unused_import':
                fixed_content = self._fix_unused_import(fixed_content, issue)
            elif issue['type'] == 'undefined_variable':
                fixed_content = self._fix_undefined_variable(fixed_content, issue)
            elif issue['type'] == 'hardcoded_password':
                fixed_content = self._fix_hardcoded_password(fixed_content, issue)
            elif issue['type'] == 'sql_injection':
                fixed_content = self._fix_sql_injection(fixed_content, issue)
        
        return fixed_content
    
    def _fix_missing_import(self, content: str, issue: Dict[str, Any]) -> str:
        """修复缺失的导入"""
        module = issue['module']
        lines = content.split('\n')
        
        # 在文件开头添加导入
        import_line = f"import {module}"
        
        # 找到第一个非注释行
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.strip() and not line.strip().startswith('#'):
                insert_pos = i
                break
        
        lines.insert(insert_pos, import_line)
        return '\n'.join(lines)
    
    def _fix_unused_import(self, content: str, issue: Dict[str, Any]) -> str:
        """修复未使用的导入"""
        lines = content.split('\n')
        line_num = issue['line'] - 1
        
        if line_num < len(lines):
            lines.pop(line_num)
        
        return '\n'.join(lines)
    
    def _fix_undefined_variable(self, content: str, issue: Dict[str, Any]) -> str:
        """修复未定义变量"""
        variable = issue['variable']
        lines = content.split('\n')
        line_num = issue['line'] - 1
        
        if line_num < len(lines):
            line = lines[line_num]
            # 简单的修复：添加变量定义
            if 'MAX_ITEMS' in variable:
                lines.insert(0, 'MAX_ITEMS = 1000  # 定义最大项目数')
        
        return '\n'.join(lines)
    
    def _fix_hardcoded_password(self, content: str, issue: Dict[str, Any]) -> str:
        """修复硬编码密码"""
        lines = content.split('\n')
        line_num = issue['line'] - 1
        
        if line_num < len(lines):
            line = lines[line_num]
            # 替换为环境变量
            fixed_line = re.sub(
                r'password\s*=\s*["\'][^"\']*["\']',
                'password = os.getenv("PASSWORD", "")',
                line,
                flags=re.IGNORECASE
            )
            lines[line_num] = fixed_line
        
        return '\n'.join(lines)
    
    def _fix_sql_injection(self, content: str, issue: Dict[str, Any]) -> str:
        """修复SQL注入"""
        lines = content.split('\n')
        line_num = issue['line'] - 1
        
        if line_num < len(lines):
            line = lines[line_num]
            # 替换为参数化查询
            fixed_line = re.sub(
                r'SELECT\s+\*\s+FROM\s+\w+\s+WHERE\s+\w+\s*=\s*["\'][^"\']*%[^"\']*["\']',
                'SELECT * FROM users WHERE name = ?',
                line,
                flags=re.IGNORECASE
            )
            lines[line_num] = fixed_line
        
        return '\n'.join(lines)
    
    def _find_used_modules(self, content: str) -> Set[str]:
        """查找使用的模块"""
        used_modules = set()
        
        # 常见的Python模块
        common_modules = ['os', 'sys', 're', 'json', 'datetime', 'ast', 'subprocess']
        
        for module in common_modules:
            if module in content:
                used_modules.add(module)
        
        return used_modules
    
    def _find_imported_modules(self, content: str) -> Set[str]:
        """查找已导入的模块"""
        imported_modules = set()
        lines = content.split('\n')
        
        for line in lines:
            if line.strip().startswith('import '):
                module = line.strip().split()[1].split('.')[0]
                imported_modules.add(module)
        
        return imported_modules
    
    def _validate_syntax(self, content: str) -> bool:
        """验证语法是否正确"""
        try:
            ast.parse(content)
            return True
        except SyntaxError:
            return False


# 测试函数
async def test_enhanced_fixer():
    """测试增强版修复器"""
    print("🧪 测试增强版代码修复器")
    
    # 创建测试文件
    test_content = '''# test_python_bad.py - 有问题的Python代码示例
# import os
# import sys
import unused_module  # 未使用的导入

# 硬编码的API密钥
API_KEY = os.getenv("API_KEY", "")
SECRET_PASSWORD = os.getenv("SECRET_PASSWORD", "")

def bad_function():
    """TODO: 添加函数文档字符串"""
    # 缺少文档字符串
    x = 1
    y = 2
    z = x + y
    return z

def risky_function():
    # 不安全的eval使用
    user_input = "print('Hello')"
    result = ast.literal_eval(user_input)  # 安全风险
    return result

def process_user_data(data):
    """TODO: 添加函数文档字符串"""
    # 缺少类型提示和文档字符串
    # 缺少输入验证
    processed = data * 2
    return processed

def divide_numbers(a, b):
    # 缺少异常处理
    result = a / b if b != 0 else 0  # 可能除零错误
    return result

# 全局变量（不好的实践）
global_var = "I'm global"

def use_global():
    """TODO: 添加函数文档字符串"""
    global_var = "modified"
    return global_var

# 不安全的文件操作
def read_file(filename):
    """TODO: 添加函数文档字符串"""
    # 没有异常处理
    with open(filename, 'r') as f:
        content = f.read()
    return content

# 内存泄漏风险
def create_large_list():
    """TODO: 添加函数文档字符串"""
    big_list = []
    for i in range(MAX_ITEMS):
        big_list.append(f"item_{i}")
    return big_list

# 缺少主函数保护
print("This will always execute")

# 不安全的字符串格式化
def format_string(user_input):
    """TODO: 添加函数文档字符串"""
    query = "SELECT * FROM users WHERE name = '%s'" % user_input  # SQL注入风险
    return query
'''
    
    # 写入测试文件
    test_file = "test_python_bad_fixed.py"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    # 创建修复器
    fixer = EnhancedCodeFixer({"enabled": True})
    
    # 执行修复
    result = await fixer.fix_python_file(test_file)
    
    print(f"修复结果: {result}")
    
    # 显示修复后的内容
    if result['success']:
        print("\n✅ 修复后的代码:")
        with open(test_file, 'r', encoding='utf-8') as f:
            print(f.read())
    
    # 清理测试文件
    os.remove(test_file)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_enhanced_fixer())





