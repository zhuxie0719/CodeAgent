"""
Bandit安全分析工具
"""

from typing import Dict, List, Any
import subprocess
import json

class BanditTool:
    """Bandit安全分析工具"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    async def analyze(self, file_path: str) -> Dict[str, Any]:
        """使用Bandit分析文件"""
        try:
            result = subprocess.run(
                ['bandit', '-r', file_path, '-f', 'json'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.stdout:
                bandit_results = json.loads(result.stdout)
                issues = []
                
                for issue in bandit_results.get('results', []):
                    issues.append({
                        'type': 'bandit',
                        'severity': issue.get('issue_severity', 'medium'),
                        'message': issue.get('issue_text', ''),
                        'file': issue.get('filename', ''),
                        'line': issue.get('line_number', 0),
                        'column': 0,
                        'rule': issue.get('test_id', 'unknown')
                    })
                
                return {
                    "success": True,
                    "issues": issues,
                    "tool": "bandit"
                }
            else:
                return {
                    "success": True,
                    "issues": [],
                    "tool": "bandit"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "issues": [],
                "tool": "bandit"
            }
