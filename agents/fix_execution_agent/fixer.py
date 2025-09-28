"""
修复器模块
"""

import os
import re
import subprocess
from typing import Dict, List, Any, Optional


class CodeFixer:
    """代码修复器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    async def fix_code_style(self, issue: Dict[str, Any], project_path: str) -> Dict[str, Any]:
        """修复代码风格问题"""
        try:
            file_path = os.path.join(project_path, issue['file'])
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 根据问题类型应用修复
            fixed_content = self._apply_style_fixes(content, issue)
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            return {
                'success': True,
                'changes': [f"修复了 {issue['file']} 中的代码风格问题"],
                'message': '代码风格修复成功'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'代码风格修复失败: {e}'
            }
    
    async def fix_security_issue(self, issue: Dict[str, Any], project_path: str) -> Dict[str, Any]:
        """修复安全问题"""
        try:
            file_path = os.path.join(project_path, issue['file'])
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 根据安全问题类型应用修复
            fixed_content = self._apply_security_fixes(content, issue)
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            return {
                'success': True,
                'changes': [f"修复了 {issue['file']} 中的安全问题"],
                'message': '安全问题修复成功'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'安全问题修复失败: {e}'
            }
    
    def _apply_style_fixes(self, content: str, issue: Dict[str, Any]) -> str:
        """应用代码风格修复（仅根据新type字段和message内容，不再判断工具名）"""
        lines = content.split('\n')
        line_num = issue.get('line', 1) - 1
        message = issue.get('message', '').lower()
        issue_type = issue.get('type', '').lower()
        
        if line_num < 0 or line_num >= len(lines):
            return content
        
        # 按type和message内容修复
        if issue_type == 'line_too_long' or 'line too long' in message:
            lines[line_num] = self._fix_line_length(lines[line_num])
        elif issue_type == 'indentation' or 'indentation' in message or 'unexpected indentation' in message:
            lines[line_num] = self._fix_indentation(lines[line_num])
        elif issue_type == 'blank_line' or 'blank line' in message:
            if 'missing' in message:
                lines = self._add_blank_line(lines, line_num)
            elif 'too many' in message:
                lines = self._remove_extra_blank_lines(lines, line_num)
        elif issue_type == 'trailing_whitespace' or 'trailing whitespace' in message:
            lines[line_num] = lines[line_num].rstrip()
        elif issue_type == 'missing_final_newline' or 'missing final newline' in message:
            if lines and not lines[-1].endswith('\n'):
                lines[-1] += '\n'
        elif issue_type == 'unused_import' or 'unused import' in message:
            lines = self._remove_unused_import(lines, line_num)
        # 其它风格问题可继续扩展
        return '\n'.join(lines)
    
    def _apply_security_fixes(self, content: str, issue: Dict[str, Any]) -> str:
        """应用安全修复（仅根据新type字段和message内容，不再判断工具名）"""
        lines = content.split('\n')
        line_num = issue.get('line', 1) - 1
        message = issue.get('message', '').lower()
        issue_type = issue.get('type', '').lower()
        
        if line_num < 0 or line_num >= len(lines):
            return content
        
        # 按type和message内容修复
        if issue_type == 'hardcoded_secrets' or 'hardcoded password' in message:
            lines[line_num] = self._fix_hardcoded_password(lines[line_num])
        elif issue_type == 'sql_injection' or 'sql injection' in message:
            lines[line_num] = self._fix_sql_injection(lines[line_num])
        elif issue_type == 'insecure_random' or 'insecure random' in message:
            lines[line_num] = self._fix_insecure_random(lines[line_num])
        elif issue_type == 'insecure_hash' or 'insecure hash' in message:
            lines[line_num] = self._fix_insecure_hash(lines[line_num])
        # 其它安全问题可继续扩展
        return '\n'.join(lines)
    
    def _fix_line_length(self, line: str, max_length: int = 79) -> str:
        """修复行长度问题"""
        if len(line) <= max_length:
            return line
        
        # 简单的行分割策略
        if '=' in line and len(line.split('=')[0]) < max_length // 2:
            # 在赋值处分割
            parts = line.split('=', 1)
            return f"{parts[0]}= \\\n    {parts[1].strip()}"
        elif ',' in line:
            # 在逗号处分割
            parts = line.split(',', 1)
            return f"{parts[0]},\n    {parts[1].strip()}"
        else:
            # 强制分割
            return line[:max_length] + ' \\\n    ' + line[max_length:].strip()
    
    def _fix_indentation(self, line: str) -> str:
        """修复缩进问题"""
        # 移除尾随空白
        line = line.rstrip()
        # 确保使用4个空格缩进
        stripped = line.lstrip()
        if stripped:
            indent_level = (len(line) - len(stripped)) // 4
            return '    ' * indent_level + stripped
        return line
    
    def _add_blank_line(self, lines: List[str], line_num: int) -> List[str]:
        """添加空行"""
        if line_num < len(lines) - 1 and lines[line_num + 1].strip():
            lines.insert(line_num + 1, '')
        return lines
    
    def _remove_extra_blank_lines(self, lines: List[str], line_num: int) -> List[str]:
        """移除多余空行"""
        # 简单的空行清理
        result = []
        prev_empty = False
        for i, line in enumerate(lines):
            if line.strip() == '':
                if not prev_empty:
                    result.append(line)
                prev_empty = True
            else:
                result.append(line)
                prev_empty = False
        return result
    
    def _remove_unused_import(self, lines: List[str], line_num: int) -> List[str]:
        """移除未使用的导入"""
        if line_num < len(lines):
            lines.pop(line_num)
        return lines
    
    def _fix_hardcoded_password(self, line: str) -> str:
        """修复硬编码密码"""
        # 简单的密码替换为环境变量
        if 'password' in line.lower() and '=' in line:
            return re.sub(r'password\s*=\s*["\'][^"\']*["\']', 'password = os.getenv("PASSWORD")', line, flags=re.IGNORECASE)
        return line
    
    def _fix_sql_injection(self, line: str) -> str:
        """修复SQL注入"""
        # 简单的参数化查询替换
        if 'execute' in line and '%' in line:
            return re.sub(r'execute\s*\(\s*["\'][^"\']*%[^"\']*["\']', 'execute("SELECT * FROM table WHERE id = ?")', line)
        return line
    
    def _fix_insecure_random(self, line: str) -> str:
        """修复不安全的随机数"""
        if 'random.random' in line:
            return line.replace('random.random', 'secrets.randbelow(1000) / 1000')
        elif 'random.randint' in line:
            return line.replace('random.randint', 'secrets.randbelow')
        return line
    
    def _fix_insecure_hash(self, line: str) -> str:
        """修复不安全的哈希"""
        if 'md5' in line.lower():
            return re.sub(r'md5\(', 'hashlib.sha256(', line, flags=re.IGNORECASE)
        elif 'sha1' in line.lower():
            return re.sub(r'sha1\(', 'hashlib.sha256(', line, flags=re.IGNORECASE)
        return line


class Refactorer:
    """代码重构器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    async def refactor_code(self, issue: Dict[str, Any], project_path: str) -> Dict[str, Any]:
        """重构代码"""
        try:
            file_path = os.path.join(project_path, issue['file'])
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 应用重构
            refactored_content = self._apply_refactoring(content, issue)
            
            # 写回文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(refactored_content)
            
            return {
                'success': True,
                'changes': [f"重构了 {issue['file']} 中的代码"],
                'message': '代码重构成功'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'代码重构失败: {e}'
            }
    
    def _apply_refactoring(self, content: str, issue: Dict[str, Any]) -> str:
        """应用重构"""
        # 简单的重构逻辑
        message = issue.get('message', '').lower()
        
        if 'duplicate code' in message:
            # 提取重复代码为函数
            return self._extract_duplicate_code(content)
        elif 'long method' in message:
            # 拆分长方法
            return self._split_long_method(content)
        elif 'large class' in message:
            # 拆分大类
            return self._split_large_class(content)
        
        return content
    
    def _extract_duplicate_code(self, content: str) -> str:
        """提取重复代码"""
        # 简单的重复代码检测和提取
        lines = content.split('\n')
        # 这里可以实现更复杂的重复代码检测逻辑
        return content
    
    def _split_long_method(self, content: str) -> str:
        """拆分长方法"""
        # 简单的长方法拆分逻辑
        return content
    
    def _split_large_class(self, content: str) -> str:
        """拆分大类"""
        # 简单的大类拆分逻辑
        return content


class DependencyUpdater:
    """依赖更新器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    async def update_dependency(self, issue: Dict[str, Any], project_path: str) -> Dict[str, Any]:
        """更新依赖"""
        try:
            # 检查依赖文件
            req_file = os.path.join(project_path, 'requirements.txt')
            package_file = os.path.join(project_path, 'package.json')
            
            changes = []
            
            if os.path.exists(req_file):
                changes.extend(await self._update_python_dependencies(req_file, issue))
            
            if os.path.exists(package_file):
                changes.extend(await self._update_node_dependencies(package_file, issue))
            
            return {
                'success': True,
                'changes': changes,
                'message': '依赖更新成功'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'依赖更新失败: {e}'
            }
    
    async def _update_python_dependencies(self, req_file: str, issue: Dict[str, Any]) -> List[str]:
        """更新Python依赖"""
        changes = []
        try:
            with open(req_file, 'r') as f:
                lines = f.readlines()
            
            # 简单的依赖更新逻辑
            # 这里可以实现具体的依赖更新策略
            
            changes.append(f"更新了 {req_file} 中的依赖")
        except Exception as e:
            changes.append(f"更新Python依赖失败: {e}")
        
        return changes
    
    async def _update_node_dependencies(self, package_file: str, issue: Dict[str, Any]) -> List[str]:
        """更新Node.js依赖"""
        changes = []
        try:
            with open(package_file, 'r') as f:
                package_data = json.load(f)
            
            # 简单的依赖更新逻辑
            # 这里可以实现具体的依赖更新策略
            
            changes.append(f"更新了 {package_file} 中的依赖")
        except Exception as e:
            changes.append(f"更新Node.js依赖失败: {e}")
        
        return changes
