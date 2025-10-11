"""
Pylint工具封装
"""

import subprocess
import json
import os
from typing import Dict, List, Any, Optional


class PylintTool:
    """Pylint静态分析工具"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.pylint_args = config.get('pylint_args', [])
    
    async def analyze(self, file_path: str) -> Dict[str, Any]:
        """执行Pylint分析"""
        try:
            cmd = ['python', '-m', 'pylint', file_path, '--output-format=json'] + self.pylint_args
            
            # 设置环境变量避免pager问题
            env = os.environ.copy()
            env['PAGER'] = ''
            env['LESS'] = ''
            env['PYTHONUNBUFFERED'] = '1'
            env['TERM'] = 'dumb'
            
            # 在Windows上添加额外的参数来避免交互
            if os.name == 'nt':
                cmd.extend(['--disable=C0114'])  # 只禁用missing-module-docstring
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
                stdin=subprocess.DEVNULL
            )
            
            issues = []
            
            # 处理JSON输出
            if result.stdout:
                try:
                    pylint_results = json.loads(result.stdout)
                    if isinstance(pylint_results, list):
                        for issue in pylint_results:
                            issues.append({
                                'type': 'pylint',
                                'severity': issue.get('type', 'info'),
                                'message': issue.get('message', ''),
                                'file': issue.get('path', ''),
                                'line': issue.get('line', 0),
                                'column': issue.get('column', 0),
                                'symbol': issue.get('symbol', ''),
                                'module': issue.get('module', '')
                            })
                except json.JSONDecodeError as e:
                    print(f"JSON解析错误: {e}")
                    print(f"原始输出: {result.stdout}")
            
            # 如果JSON解析失败，尝试解析文本输出
            if not issues and result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if ':' in line and any(char.isdigit() for char in line):
                        # 尝试解析pylint的文本输出格式
                        parts = line.split(':', 4)
                        if len(parts) >= 4:
                            try:
                                issues.append({
                                    'type': 'pylint',
                                    'severity': 'warning',
                                    'message': parts[-1].strip(),
                                    'file': parts[0],
                                    'line': int(parts[1]),
                                    'column': int(parts[2]) if parts[2].isdigit() else 0,
                                    'symbol': parts[3].strip() if len(parts) > 3 else '',
                                    'module': ''
                                })
                            except (ValueError, IndexError):
                                continue
            
            return {
                'success': result.returncode in [0, 1],  # 0=无问题, 1=发现问题
                'issues': issues,
                'total_issues': len(issues),
                'stdout': result.stdout,
                'stderr': result.stderr
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'issues': []
            }
    
    async def fix_issues(self, issues: List[Dict[str, Any]], project_path: str) -> Dict[str, Any]:
        """尝试自动修复Pylint问题"""
        # 实现自动修复逻辑
        return {
            'success': False,
            'message': 'Pylint自动修复功能待实现',
            'fixed_issues': []
        }
