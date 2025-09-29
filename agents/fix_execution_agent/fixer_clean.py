import os
import subprocess
from typing import Dict, Any

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
            
            # 应用安全修复
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
        """应用代码风格修复"""
        lines = content.split('\n')
        line_num = issue.get('line', 1) - 1  # 转换为0索引
        
        if line_num < 0 or line_num >= len(lines):
            return content
        
        # 根据问题类型应用不同的修复
        issue_type = issue.get('type', '').lower()
        message = issue.get('message', '').lower()
        
        if 'indentation' in message or 'unexpected indentation' in message:
            # 修复缩进问题
            lines[line_num] = self._fix_indentation(lines[line_num])
        elif 'trailing whitespace' in message:
            # 移除行尾空白
            lines[line_num] = lines[line_num].rstrip()
        elif 'line too long' in message:
            # 修复过长的行
            lines[line_num] = self._fix_long_line(lines[line_num])
        elif 'missing blank line' in message:
            # 添加空行
            if line_num > 0 and lines[line_num - 1].strip():
                lines.insert(line_num, '')
        elif 'too many blank lines' in message:
            # 移除多余空行
            lines[line_num] = ''
        elif 'unused import' in message or 'imported but unused' in message:
            # 移除未使用的导入
            lines[line_num] = ''
        elif 'missing final newline' in message:
            # 确保文件以换行符结尾
            if lines and not lines[-1].endswith('\n'):
                lines.append('')
        
        return '\n'.join(lines)
    
    def _fix_indentation(self, line: str) -> str:
        """修复缩进问题"""
        # 移除前导空白，重新添加正确的缩进
        stripped = line.lstrip()
        if stripped:
            # 根据上下文确定正确的缩进级别
            return '    ' + stripped  # 默认4空格缩进
        return line
    
    def _fix_long_line(self, line: str) -> str:
        """修复过长的行"""
        max_length = 88  # PEP 8 推荐长度
        if len(line) <= max_length:
            return line
        
        # 简单的换行策略
        if ' ' in line:
            words = line.split(' ')
            result = []
            current_line = ''
            
            for word in words:
                if len(current_line + ' ' + word) <= max_length:
                    if current_line:
                        current_line += ' ' + word
                    else:
                        current_line = word
                else:
                    if current_line:
                        result.append(current_line)
                    current_line = word
            
            if current_line:
                result.append(current_line)
            
            return '\n'.join(result)
        
        return line
    
    def _apply_security_fixes(self, content: str, issue: Dict[str, Any]) -> str:
        """应用安全修复"""
        lines = content.split('\n')
        line_num = issue.get('line', 1) - 1
        
        if line_num < 0 or line_num >= len(lines):
            return content
        
        message = issue.get('message', '').lower()
        
        if 'hardcoded password' in message or 'hardcoded secret' in message:
            # 替换硬编码密码
            lines[line_num] = self._replace_hardcoded_secrets(lines[line_num])
        elif 'sql injection' in message:
            # 修复SQL注入问题
            lines[line_num] = self._fix_sql_injection(lines[line_num])
        elif 'unsafe deserialization' in message:
            # 修复不安全的反序列化
            lines[line_num] = self._fix_unsafe_deserialization(lines[line_num])
        
        return '\n'.join(lines)
    
    def _replace_hardcoded_secrets(self, line: str) -> str:
        """替换硬编码的秘密"""
        import re
        
        # 替换常见的硬编码密码模式
        patterns = [
            (r'password\s*=\s*["\'][^"\']+["\']', 'password = os.getenv("PASSWORD")'),
            (r'secret\s*=\s*["\'][^"\']+["\']', 'secret = os.getenv("SECRET")'),
            (r'api_key\s*=\s*["\'][^"\']+["\']', 'api_key = os.getenv("API_KEY")'),
        ]
        
        for pattern, replacement in patterns:
            line = re.sub(pattern, replacement, line, flags=re.IGNORECASE)
        
        return line
    
    def _fix_sql_injection(self, line: str) -> str:
        """修复SQL注入问题"""
        import re
        
        # 简单的SQL注入修复示例
        if 'execute' in line.lower() and '%' in line:
            # 替换字符串格式化
            line = re.sub(r'execute\s*\(\s*["\'].*%s.*["\']', 'execute("SELECT * FROM table WHERE id = ?")', line)
        
        return line
    
    def _fix_unsafe_deserialization(self, line: str) -> str:
        """修复不安全的反序列化"""
        import re
        
        # 替换pickle.loads
        if 'pickle.loads' in line:
            line = re.sub(r'pickle\.loads\([^)]+\)', 'json.loads()', line)
        
        return line
    
    def _fix_hash_functions(self, line: str) -> str:
        """修复不安全的哈希函数"""
        import re
        
        if 'md5' in line.lower():
            return re.sub(r'md5\(', 'hashlib.sha256(', line, flags=re.IGNORECASE)
        elif 'sha1' in line.lower():
            return re.sub(r'sha1\(', 'hashlib.sha256(', line, flags=re.IGNORECASE)
        return line

    async def fix_python(self, file: str, project_path: str) -> Dict[str, Any]:
        """修复Python文件"""
        try:
            file_path = os.path.join(project_path, file)
            subprocess.run(["autoflake", "--in-place", "--remove-unused-variables", file_path], check=True)
            subprocess.run(["isort", file_path], check=True)
            subprocess.run(["black", file_path], check=True)
            return {"success": True, "changes": [f"Python文件已自动修复: {file_path}"], "message": "autoflake + isort + black 修复成功"}
        except Exception as e:
            return {"success": False, "changes": [], "message": f"Python修复失败: {e}"}

    async def fix_java(self, file: str, project_path: str) -> Dict[str, Any]:
        """修复Java文件"""
        try:
            file_path = os.path.join(project_path, file)
            subprocess.run(["google-java-format", "-i", file_path], check=True)
            return {"success": True, "changes": [f"Java文件已自动修复: {file_path}"], "message": "google-java-format 修复成功"}
        except Exception as e:
            return {"success": False, "changes": [], "message": f"Java修复失败: {e}"}

    async def fix_javascript(self, file: str, project_path: str) -> Dict[str, Any]:
        """修复JavaScript文件"""
        try:
            file_path = os.path.join(project_path, file)
            subprocess.run(["prettier", "--write", file_path], check=True)
            return {"success": True, "changes": [f"JavaScript文件已自动修复: {file_path}"], "message": "prettier 修复成功"}
        except Exception as e:
            return {"success": False, "changes": [], "message": f"JavaScript修复失败: {e}"}

    async def fix_go(self, file: str, project_path: str) -> Dict[str, Any]:
        """修复Go文件"""
        try:
            file_path = os.path.join(project_path, file)
            subprocess.run(["gofmt", "-w", file_path], check=True)
            subprocess.run(["goimports", "-w", file_path], check=True)
            return {"success": True, "changes": [f"Go文件已自动修复: {file_path}"], "message": "gofmt + goimports 修复成功"}
        except Exception as e:
            return {"success": False, "changes": [], "message": f"Go修复失败: {e}"}
