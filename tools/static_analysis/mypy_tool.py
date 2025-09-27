"""
MyPy类型检查工具
"""

from typing import Dict, List, Any
import subprocess
import json

class MypyTool:
    """MyPy类型检查工具"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    async def analyze(self, file_path: str) -> Dict[str, Any]:
        """使用MyPy分析文件"""
        try:
            result = subprocess.run(
                ['mypy', file_path, '--show-error-codes', '--no-error-summary'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            issues = []
            
            for line in result.stdout.split('\n'):
                if ':' in line and ('error:' in line or 'warning:' in line):
                    parts = line.split(':', 3)
                    if len(parts) >= 4:
                        issues.append({
                            'type': 'mypy',
                            'severity': 'error' if 'error:' in line else 'warning',
                            'message': parts[3].strip(),
                            'file': parts[0],
                            'line': int(parts[1]) if parts[1].isdigit() else 0,
                            'column': int(parts[2]) if parts[2].isdigit() else 0,
                            'rule': 'mypy'
                        })
            
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
