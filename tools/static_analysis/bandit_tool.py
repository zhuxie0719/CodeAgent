"""
Bandit安全分析工具
"""

from typing import Dict, List, Any
import subprocess
import json
import os


class BanditTool:
    """Bandit安全分析工具"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    async def analyze(self, file_path: str) -> Dict[str, Any]:
        """使用Bandit分析单个文件"""
        try:
            # 设置环境变量，确保UTF-8编码
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            if os.name == 'nt':
                env['PYTHONUTF8'] = '1'
            
            # Bandit对于单个文件不使用-r参数，使用-f json直接指定文件
            result = subprocess.run(
                ['bandit', '-f', 'json', file_path],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=30,
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            issues = []
            
            if result.stdout:
                try:
                    bandit_results = json.loads(result.stdout)
                    for issue in bandit_results.get('results', []):
                        issues.append({
                            'type': 'bandit',
                            'severity': issue.get('issue_severity', 'medium').lower(),
                            'message': issue.get('issue_text', ''),
                            'file': issue.get('filename', ''),
                            'line': issue.get('line_number', 0),
                            'column': 0,
                            'rule': issue.get('test_id', 'unknown'),
                            'confidence': issue.get('issue_confidence', 'medium').lower()
                        })
                except json.JSONDecodeError:
                    # JSON解析失败，可能Bandit返回了错误信息
                    pass
            
            return {
                "success": True,
                "issues": issues,
                "tool": "bandit",
                "total_issues": len(issues)
            }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "issues": [],
                "tool": "bandit"
            }
    
    async def analyze_directory(self, directory_path: str) -> Dict[str, Any]:
        """使用Bandit分析整个目录（更高效）"""
        try:
            if not os.path.isdir(directory_path):
                return {
                    'success': False,
                    'error': f'目录不存在: {directory_path}',
                    'issues': []
                }
            
            # 设置环境变量，确保UTF-8编码
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            if os.name == 'nt':
                env['PYTHONUTF8'] = '1'
            
            result = subprocess.run(
                ['bandit', '-r', directory_path, '-f', 'json'],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=120,
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            issues = []
            
            if result.stdout:
                try:
                    bandit_results = json.loads(result.stdout)
                    for issue in bandit_results.get('results', []):
                        issues.append({
                            'type': 'bandit',
                            'severity': issue.get('issue_severity', 'medium').lower(),
                            'message': issue.get('issue_text', ''),
                            'file': issue.get('filename', ''),
                            'line': issue.get('line_number', 0),
                            'column': 0,
                            'rule': issue.get('test_id', 'unknown'),
                            'confidence': issue.get('issue_confidence', 'medium').lower()
                        })
                except json.JSONDecodeError:
                    pass
            
            return {
                "success": True,
                "issues": issues,
                "tool": "bandit",
                "total_issues": len(issues)
            }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Bandit执行超时",
                "issues": []
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "issues": [],
                "tool": "bandit"
            }



