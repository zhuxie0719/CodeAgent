"""
Flake8工具封装
"""

import subprocess
import os
import sys
from typing import Dict, List, Any, Optional


class Flake8Tool:
    """Flake8代码风格检查工具"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.flake8_args = config.get('flake8_args', [])
    
    async def analyze(self, file_path: str) -> Dict[str, Any]:
        """执行Flake8分析"""
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': f'文件不存在: {file_path}',
                    'issues': []
                }
            
            # 使用当前 Python 解释器（虚拟环境中的 Python）
            cmd = [sys.executable, '-m', 'flake8', file_path] + self.flake8_args
            
            # 设置环境变量避免pager问题
            env = os.environ.copy()
            env['PAGER'] = ''
            env['LESS'] = ''
            env['PYTHONUNBUFFERED'] = '1'
            env['TERM'] = 'dumb'
            
            print(f"执行Flake8命令: {' '.join(cmd)}")  # 调试信息
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
                stdin=subprocess.DEVNULL
            )
            
            print(f"Flake8返回码: {result.returncode}")  # 调试信息
            print(f"Flake8 stdout: {result.stdout[:200]}...")  # 调试信息
            print(f"Flake8 stderr: {result.stderr[:200]}...")  # 调试信息
            
            issues = []
            for line in result.stdout.split('\n'):
                if line.strip():
                    parts = line.split(':', 3)
                    if len(parts) >= 4:
                        try:
                            issues.append({
                                'type': 'flake8',
                                'severity': 'warning',
                                'message': parts[3].strip(),
                                'file': parts[0],
                                'line': int(parts[1]),
                                'column': int(parts[2])
                            })
                        except (ValueError, IndexError):
                            # 跳过无法解析的行
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
