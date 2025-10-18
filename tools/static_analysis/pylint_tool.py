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
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': f'文件不存在: {file_path}',
                    'issues': []
                }
            
            cmd = ['python', '-m', 'pylint', file_path, '--output-format=json'] + self.pylint_args
            
            # 设置环境变量避免pager问题
            env = os.environ.copy()
            env['PAGER'] = ''
            env['LESS'] = ''
            env['PYTHONUNBUFFERED'] = '1'
            env['TERM'] = 'dumb'
            
            # 在Windows上添加额外的参数来避免交互
            if os.name == 'nt' and '--disable=C0114' not in cmd:
                cmd.extend(['--disable=C0114'])  # 只禁用missing-module-docstring
            
            print(f"执行Pylint命令: {' '.join(cmd)}")  # 调试信息
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
                stdin=subprocess.DEVNULL
            )
            
            print(f"Pylint返回码: {result.returncode}")  # 调试信息
            print(f"Pylint stdout: {result.stdout[:200]}...")  # 调试信息
            print(f"Pylint stderr: {result.stderr[:200]}...")  # 调试信息
            
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
            
            # Pylint返回码说明：
            # 0 = 无问题
            # 1 = 致命错误
            # 2 = 错误
            # 4 = 警告
            # 8 = 重构建议
            # 16 = 约定问题
            # 32 = 使用错误
            # 28 = 4+8+16 (警告+重构建议+约定问题)
            # 只有致命错误(1)才认为失败
            success = result.returncode != 1
            
            return {
                'success': success,
                'issues': issues,
                'total_issues': len(issues),
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
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
