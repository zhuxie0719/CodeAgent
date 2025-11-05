"""
MyPy类型检查工具
增强配置以检测Flask 2.0.0的类型问题
"""

from typing import Dict, List, Any
import subprocess
import json
import os
import re

class MypyTool:
    """MyPy类型检查工具（增强严格模式）"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        # 启用严格模式配置（针对Flask类型问题）
        self.strict_mode = config.get('strict_mode', True)
        self.mypy_args = config.get('mypy_args', [])
    
    async def analyze(self, file_path: str) -> Dict[str, Any]:
        """使用MyPy分析文件（增强严格模式）"""
        try:
            # 构建命令
            cmd = ['mypy']
            
            # 基本参数
            cmd.extend(['--show-error-codes', '--no-error-summary', '--pretty'])
            
            # 严格模式配置（仅在启用时添加，且不与mypy_args冲突）
            if self.strict_mode:
                strict_options = [
                    '--disallow-untyped-calls',      # 不允许未注解的调用
                    '--disallow-untyped-defs',        # 不允许未注解的函数定义
                    '--disallow-incomplete-defs',     # 不允许不完整的定义
                    '--no-implicit-reexport',         # 针对#4024: 顶层导出类型检查
                    '--warn-return-any',              # 警告返回Any类型
                    '--warn-unreachable',             # 警告不可达代码
                    '--warn-redundant-casts',          # 警告冗余类型转换
                    '--warn-unused-ignores',           # 警告未使用的ignore
                    '--strict-optional',               # 严格可选类型检查
                    '--strict-equality',               # 严格相等性检查
                ]
                # 只添加不在mypy_args中的严格选项（避免冲突）
                existing_args = set(self.mypy_args)
                for opt in strict_options:
                    opt_name = opt.lstrip('-').split('=')[0]
                    # 检查是否有冲突的选项
                    conflict = False
                    for existing in existing_args:
                        existing_name = existing.lstrip('-').split('=')[0]
                        # 检查是否是相反选项（如--allow-untyped-calls vs --disallow-untyped-calls）
                        if opt_name.replace('disallow', 'allow') == existing_name or \
                           opt_name.replace('allow', 'disallow') == existing_name:
                            conflict = True
                            break
                    if not conflict:
                        cmd.append(opt)
            
            # 添加用户自定义参数
            cmd.extend(self.mypy_args)
            
            # 添加文件路径
            cmd.append(file_path)
            
            # 设置环境变量
            env = os.environ.copy()
            env['MYPY_FORCE_COLOR'] = '0'  # 禁用颜色输出
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',  # 遇到编码错误时替换
                timeout=60,  # 严格模式可能需要更长时间
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            issues = []
            
            # Mypy输出可能在stdout或stderr中，合并两者
            output_lines = result.stdout.split('\n') + result.stderr.split('\n')
            
            for line in output_lines:
                line = line.strip()
                if not line:
                    continue
                
                # Mypy输出格式: file:line:column: severity: message [error-code]
                # 例如: test.py:5:12: error: Incompatible types in assignment (expression has type "int", variable has type "str")  [assignment]
                if ':' in line and ('error:' in line or 'warning:' in line or 'note:' in line):
                    # 匹配格式: file:line:column: severity: message
                    # 例如: file.py:10:5: error: message here
                    pattern = r'^([^:]+):(\d+):(\d+):\s*(error|warning|note):\s*(.+)$'
                    match = re.match(pattern, line)
                    
                    if match:
                        file_path, line_str, col_str, severity, message = match.groups()
                        try:
                            line_num = int(line_str)
                            col_num = int(col_str)
                            
                            # 只处理error和warning，忽略note
                            if severity in ['error', 'warning']:
                                issues.append({
                                    'type': 'mypy',
                                    'severity': severity,
                                    'message': message.strip(),
                                    'file': file_path,
                                    'line': line_num,
                                    'column': col_num,
                                    'rule': 'mypy'
                                })
                        except ValueError:
                            # 如果行号或列号不是数字，跳过
                            continue
                    else:
                        # 尝试备用解析方法（可能没有列号）
                        # 格式: file:line: severity: message
                        pattern2 = r'^([^:]+):(\d+):\s*(error|warning|note):\s*(.+)$'
                        match2 = re.match(pattern2, line)
                        if match2:
                            file_path, line_str, severity, message = match2.groups()
                            try:
                                line_num = int(line_str)
                                if severity in ['error', 'warning']:
                                    issues.append({
                                        'type': 'mypy',
                                        'severity': severity,
                                        'message': message.strip(),
                                        'file': file_path,
                                        'line': line_num,
                                        'column': 0,
                                        'rule': 'mypy'
                                    })
                            except ValueError:
                                continue
            
            return {
                "success": True,
                "issues": issues,
                "tool": "mypy"
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "issues": [],
                "tool": "mypy"
            }
