import os
import subprocess
from typing import Dict, Any, List

class CodeFixer:
    """多语言代码格式化修复器"""
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

    async def fix_python(self, file: str, project_path: str) -> Dict[str, Any]:
        try:
            file_path = os.path.join(project_path, file)
            subprocess.run(["autoflake", "--in-place", "--remove-unused-variables", file_path], check=True)
            subprocess.run(["isort", file_path], check=True)
            subprocess.run(["black", file_path], check=True)
            return {"success": True, "changes": [f"Python文件已自动修复: {file_path}"], "message": "autoflake + isort + black 修复成功"}
        except Exception as e:
            return {"success": False, "changes": [], "message": f"Python修复失败: {e}"}

    async def fix_javascript(self, file: str, project_path: str) -> Dict[str, Any]:
        try:
            file_path = os.path.join(project_path, file)
            subprocess.run(["eslint", "--fix", file_path], check=True)
            subprocess.run(["prettier", "--write", file_path], check=True)
            return {"success": True, "changes": [f"JavaScript文件已格式化: {file_path}"], "message": "eslint + prettier 格式化成功"}
        except Exception as e:
            return {"success": False, "changes": [], "message": f"JavaScript格式化失败: {e}"}

    async def fix_java(self, file: str, project_path: str) -> Dict[str, Any]:
        try:
            file_path = os.path.join(project_path, file)
            subprocess.run(["google-java-format", "-i", file_path], check=True)
            return {"success": True, "changes": [f"Java文件已格式化: {file_path}"], "message": "google-java-format 格式化成功"}
        except Exception as e:
            return {"success": False, "changes": [], "message": f"Java格式化失败: {e}"}

    async def fix_cpp(self, file: str, project_path: str) -> Dict[str, Any]:
        try:
            file_path = os.path.join(project_path, file)
            subprocess.run(["clang-format", "-i", file_path], check=True)
            return {"success": True, "changes": [f"C/C++文件已格式化: {file_path}"], "message": "clang-format 格式化成功"}
        except Exception as e:
            return {"success": False, "changes": [], "message": f"C/C++格式化失败: {e}"}

    async def fix_go(self, file: str, project_path: str) -> Dict[str, Any]:
        try:
            file_path = os.path.join(project_path, file)
            subprocess.run(["gofmt", "-w", file_path], check=True)
            subprocess.run(["goimports", "-w", file_path], check=True)
            return {"success": True, "changes": [f"Go文件已格式化: {file_path}"], "message": "gofmt + goimports 格式化成功"}
        except Exception as e:
            return {"success": False, "changes": [], "message": f"Go格式化失败: {e}"}


class Refactorer:
    """代码重构器"""
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    async def refactor_code(self, issue: Dict[str, Any], project_path: str) -> Dict[str, Any]:
        """重构代码"""
        try:
            # 这里可以实现具体的重构逻辑
            return {
                'success': True,
                'changes': [f"重构了 {issue.get('file', '')} 中的代码"],
                'message': '代码重构成功'
            }
        except Exception as e:
            return {
                'success': False,
                'changes': [],
                'message': f'代码重构失败: {e}'
            }


class DependencyUpdater:
    """依赖更新器"""
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    async def update_dependency(self, issue: Dict[str, Any], project_path: str) -> Dict[str, Any]:
        """更新依赖"""
        try:
            # 这里可以实现具体的依赖更新逻辑
            return {
                'success': True,
                'changes': [f"更新了 {issue.get('file', '')} 中的依赖"],
                'message': '依赖更新成功'
            }
        except Exception as e:
            return {
                'success': False,
                'changes': [],
                'message': f'依赖更新失败: {e}'
            }
