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
        self.select_rules = config.get('select', [])  # 选择特定规则组
        self.ignore_rules = config.get('ignore', [])  # 忽略特定规则
        
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
                            issues.append({
                                'type': 'ruff',
                                'severity': issue.get('code', {}).get('severity', 'WARNING').lower(),
                                'message': issue.get('message', ''),
                                'file': issue.get('filename', file_path),
                                'line': issue.get('location', {}).get('row', 0),
                                'column': issue.get('location', {}).get('column', 0),
                                'end_line': issue.get('end_location', {}).get('row', 0),
                                'end_column': issue.get('end_location', {}).get('column', 0),
                                'rule_code': issue.get('code', {}).get('code', ''),
                                'rule_name': issue.get('code', {}).get('name', '')
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
                timeout=120,
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            issues = []
            
            # 解析JSON输出
            if result.stdout:
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
                    return {
                        'success': False,
                        'error': f'Ruff JSON解析失败: {e}',
                        'issues': []
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
