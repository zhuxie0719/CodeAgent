"""
Ruff工具封装
现代化的快速Python静态分析工具，集成了flake8/isort/pyupgrade等功能
"""

import subprocess
import json
import os
from typing import Dict, List, Any, Optional


class RuffTool:
    """Ruff静态分析工具"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get('enabled', True)
        self.ruff_args = config.get('ruff_args', ['--output-format=json'])
        # 确保select_rules和ignore_rules是列表类型
        select_rules = config.get('select', [])
        ignore_rules = config.get('ignore', [])
        self.select_rules = select_rules if isinstance(select_rules, list) else (list(select_rules) if select_rules else [])
        self.ignore_rules = ignore_rules if isinstance(ignore_rules, list) else (list(ignore_rules) if ignore_rules else [])
        
    async def analyze(self, file_path: str) -> Dict[str, Any]:
        """执行Ruff分析单个文件"""
        try:
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': f'文件不存在: {file_path}',
                    'issues': []
                }
            
            # 构建命令
            cmd = ['ruff', 'check']
            
            # 添加输出格式
            if '--output-format=json' not in self.ruff_args:
                cmd.append('--output-format=json')
            
            # 添加规则选择
            if self.select_rules:
                cmd.extend(['--select', ','.join(self.select_rules)])
            
            # 添加规则忽略
            if self.ignore_rules:
                cmd.extend(['--ignore', ','.join(self.ignore_rules)])
            
            # 添加额外参数
            for arg in self.ruff_args:
                if arg not in cmd:
                    cmd.append(arg)
            
            # 添加文件路径
            cmd.append(file_path)
            
            # 设置环境变量，确保UTF-8编码
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            if os.name == 'nt':
                env['PYTHONUTF8'] = '1'
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',  # 遇到编码错误时替换而不是失败
                timeout=30,
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            issues = []
            
            # Ruff的JSON输出格式
            if result.stdout:
                try:
                    ruff_output = json.loads(result.stdout)
                    if isinstance(ruff_output, list):
                        for issue in ruff_output:
                            code_info = issue.get('code', {})
                            severity = 'warning'
                            rule_code = ''
                            rule_name = ''
                            if isinstance(code_info, dict):
                                severity = code_info.get('severity', 'WARNING').lower()
                                rule_code = code_info.get('code', '')
                                rule_name = code_info.get('name', '')
                            else:
                                # Ruff >=0.14 将 code 直接作为字符串返回
                                rule_code = str(code_info)
                            
                            issues.append({
                                'type': 'ruff',
                                'severity': severity,
                                'message': issue.get('message', ''),
                                'file': issue.get('filename', file_path),
                                'line': issue.get('location', {}).get('row', 0),
                                'column': issue.get('location', {}).get('column', 0),
                                'end_line': issue.get('end_location', {}).get('row', 0),
                                'end_column': issue.get('end_location', {}).get('column', 0),
                                'rule_code': rule_code,
                                'rule_name': rule_name
                            })
                except json.JSONDecodeError as e:
                    # JSON解析失败，尝试文本输出
                    import logging
                    logging.debug(f"Ruff JSON解析失败: {e}, stdout: {result.stdout[:200] if result.stdout else 'None'}")
                    if result.stdout and result.stdout.strip():
                        lines = result.stdout.strip().split('\n')
                        for line in lines:
                            if ':' in line:
                                parts = line.split(':', 3)
                                if len(parts) >= 4:
                                    issues.append({
                                        'type': 'ruff',
                                        'severity': 'warning',
                                        'message': parts[3].strip(),
                                        'file': parts[0],
                                        'line': int(parts[1]) if parts[1].isdigit() else 0,
                                        'column': int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0,
                                        'rule_code': 'unknown'
                                    })
            
            # Ruff返回码：0=无问题，非0=有问题
            return {
                'success': True,
                'issues': issues,
                'total_issues': len(issues),
                'stdout': result.stdout[:500] if result.stdout else '',
                'stderr': result.stderr[:500] if result.stderr else '',
                'return_code': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Ruff执行超时',
                'issues': []
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'issues': []
            }
    
    async def analyze_directory(self, directory_path: str) -> Dict[str, Any]:
        """执行Ruff分析整个目录（更高效）"""
        try:
            if not os.path.isdir(directory_path):
                return {
                    'success': False,
                    'error': f'目录不存在: {directory_path}',
                    'issues': []
                }
            
            # 构建命令
            cmd = ['ruff', 'check']
            
            # 添加输出格式
            if '--output-format=json' not in self.ruff_args:
                cmd.append('--output-format=json')
            
            # 添加规则选择
            if self.select_rules:
                cmd.extend(['--select', ','.join(self.select_rules)])
            
            # 添加规则忽略
            if self.ignore_rules:
                cmd.extend(['--ignore', ','.join(self.ignore_rules)])
            
            # 添加额外参数
            for arg in self.ruff_args:
                if arg not in cmd and not arg.startswith('--output-format'):
                    cmd.append(arg)
            
            # 添加目录路径
            cmd.append(directory_path)
            
            # 设置环境变量，确保UTF-8编码和JSON输出格式
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            if os.name == 'nt':
                env['PYTHONUTF8'] = '1'
            # 尝试使用环境变量设置JSON输出格式（某些Ruff版本可能需要）
            env['RUFF_OUTPUT_FORMAT'] = 'json'
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',  # 遇到编码错误时替换而不是失败
                timeout=300,  # 增加到5分钟（300秒），给大项目足够时间
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            issues = []
            
            # 解析JSON输出
            if result.stdout and result.stdout.strip():
                try:
                    ruff_output = json.loads(result.stdout)
                    if isinstance(ruff_output, list):
                        for issue in ruff_output:
                            issues.append({
                                'type': 'ruff',
                                'severity': issue.get('code', {}).get('severity', 'WARNING').lower(),
                                'message': issue.get('message', ''),
                                'file': issue.get('filename', ''),
                                'line': issue.get('location', {}).get('row', 0),
                                'column': issue.get('location', {}).get('column', 0),
                                'end_line': issue.get('end_location', {}).get('row', 0),
                                'end_column': issue.get('end_location', {}).get('column', 0),
                                'rule_code': issue.get('code', {}).get('code', ''),
                                'rule_name': issue.get('code', {}).get('name', '')
                            })
                except json.JSONDecodeError as e:
                    # JSON解析失败，检查是否是字符串类型错误
                    if isinstance(result.stdout, str):
                        # 尝试解析JSON字符串
                        try:
                            # 如果stdout是字符串但包含JSON，尝试直接解析
                            if result.stdout.strip().startswith('[') or result.stdout.strip().startswith('{'):
                                ruff_output = json.loads(result.stdout)
                                if isinstance(ruff_output, list):
                                    for issue in ruff_output:
                                        if isinstance(issue, dict):
                                            issues.append({
                                                'type': 'ruff',
                                                'severity': issue.get('code', {}).get('severity', 'WARNING').lower() if isinstance(issue.get('code'), dict) else 'warning',
                                                'message': issue.get('message', '') if isinstance(issue.get('message'), str) else str(issue.get('message', '')),
                                                'file': issue.get('filename', ''),
                                                'line': issue.get('location', {}).get('row', 0) if isinstance(issue.get('location'), dict) else 0,
                                                'column': issue.get('location', {}).get('column', 0) if isinstance(issue.get('location'), dict) else 0,
                                                'end_line': issue.get('end_location', {}).get('row', 0) if isinstance(issue.get('end_location'), dict) else 0,
                                                'end_column': issue.get('end_location', {}).get('column', 0) if isinstance(issue.get('end_location'), dict) else 0,
                                                'rule_code': issue.get('code', {}).get('code', '') if isinstance(issue.get('code'), dict) else '',
                                                'rule_name': issue.get('code', {}).get('name', '') if isinstance(issue.get('code'), dict) else ''
                                            })
                        except (json.JSONDecodeError, AttributeError, TypeError) as parse_error:
                            # JSON解析仍然失败，尝试文本格式
                            pass
                    
                    # 尝试解析文本格式输出（fallback）
                    stdout_preview = result.stdout[:200] if result.stdout else 'None'
                    if not result.stdout.strip():
                        # 空输出，可能是没有发现问题
                        return {
                            'success': True,
                            'issues': [],
                            'total_issues': 0,
                            'return_code': result.returncode,
                            'message': 'Ruff执行成功，未发现问题'
                        }
                    else:
                        # 非空但非JSON，尝试解析文本格式
                        # Ruff文本格式示例: "F401 [*] `os` imported but unused"
                        # 或者: "path/to/file.py:3:8: F401 `os` imported but unused"
                        try:
                            lines = result.stdout.strip().split('\n')
                            for line in lines:
                                line = line.strip()
                                if not line:
                                    continue
                                
                                # 尝试解析格式: "file.py:line:col: CODE message"
                                if ':' in line and any(char.isdigit() for char in line):
                                    # 解析文件路径和行号
                                    parts = line.split(':', 3)
                                    if len(parts) >= 4:
                                        file_path = parts[0]
                                        try:
                                            line_num = int(parts[1]) if parts[1].isdigit() else 0
                                            col_num = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
                                            message_part = parts[3].strip()
                                            
                                            # 提取规则代码（如F401）
                                            rule_code = 'unknown'
                                            message = message_part
                                            if message_part:
                                                # 格式可能是: "F401 `os` imported but unused"
                                                msg_parts = message_part.split(' ', 1)
                                                if msg_parts and (msg_parts[0].startswith('F') or msg_parts[0].startswith('E')):
                                                    rule_code = msg_parts[0]
                                                    message = msg_parts[1] if len(msg_parts) > 1 else message_part
                                            
                                            issues.append({
                                                'type': 'ruff',
                                                'severity': 'warning',
                                                'message': message,
                                                'file': file_path,
                                                'line': line_num,
                                                'column': col_num,
                                                'rule_code': rule_code
                                            })
                                        except (ValueError, IndexError):
                                            # 如果解析失败，尝试其他格式
                                            # 格式可能是: "F401 [*] `os` imported but unused"
                                            if ' ' in line:
                                                msg_parts = line.split(' ', 2)
                                                if len(msg_parts) >= 3 and (msg_parts[0].startswith('F') or msg_parts[0].startswith('E')):
                                                    issues.append({
                                                        'type': 'ruff',
                                                        'severity': 'warning',
                                                        'message': msg_parts[2] if len(msg_parts) > 2 else line,
                                                        'file': directory_path,  # 使用目录路径作为默认
                                                        'line': 0,
                                                        'column': 0,
                                                        'rule_code': msg_parts[0]
                                                    })
                            # 如果成功解析了问题，返回成功
                            if issues:
                                return {
                                    'success': True,
                                    'issues': issues,
                                    'total_issues': len(issues),
                                    'return_code': result.returncode,
                                    'message': 'Ruff执行成功（使用文本格式解析）'
                                }
                        except Exception as parse_error:
                            pass  # 如果文本解析也失败，继续返回错误
                        
                        # 如果文本解析也失败，返回错误
                        return {
                            'success': False,
                            'error': f'Ruff JSON解析失败: {e}。输出预览: {stdout_preview}',
                            'issues': [],
                            'stdout_preview': stdout_preview
                        }
            elif not result.stdout or not result.stdout.strip():
                # 空输出，可能是没有发现问题（Ruff返回码0表示无问题）
                return {
                    'success': True,
                    'issues': [],
                    'total_issues': 0,
                    'return_code': result.returncode,
                    'message': 'Ruff执行成功，未发现问题'
                }
            
            return {
                'success': True,
                'issues': issues,
                'total_issues': len(issues),
                'return_code': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Ruff执行超时',
                'issues': []
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'issues': []
            }
