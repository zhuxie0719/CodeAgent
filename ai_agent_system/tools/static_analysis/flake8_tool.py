"""
Flake8工具封装
"""

import subprocess
from typing import Dict, List, Any, Optional


class Flake8Tool:
    """Flake8代码风格检查工具"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.flake8_args = config.get('flake8_args', [])
    
    async def analyze(self, project_path: str) -> Dict[str, Any]:
        """执行Flake8分析"""
        try:
            cmd = ['flake8', project_path] + self.flake8_args
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=project_path
            )
            
            issues = []
            for line in result.stdout.split('\n'):
                if line.strip():
                    parts = line.split(':', 3)
                    if len(parts) >= 4:
                        issues.append({
                            'type': 'flake8',
                            'severity': 'warning',
                            'message': parts[3].strip(),
                            'file': parts[0],
                            'line': int(parts[1]),
                            'column': int(parts[2])
                        })
            
            return {
                'success': result.returncode == 0,
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
