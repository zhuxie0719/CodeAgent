"""
Pylint工具封装
支持单文件和目录分析
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
        """执行Pylint分析单个文件"""
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
                    # JSON解析失败，尝试解析文本输出
                    if result.stdout.strip():
                        lines = result.stdout.strip().split('\n')
                        for line in lines:
                            if ':' in line and any(char.isdigit() for char in line):
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
            # 其他 = 有问题（但不算失败）
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
    
    async def analyze_directory(self, directory_path: str, file_pattern: Optional[str] = None) -> Dict[str, Any]:
        """
        执行Pylint分析整个目录（更高效，一次性分析多个文件）
        
        Args:
            directory_path: 要分析的目录路径
            file_pattern: 文件匹配模式（如 '*.py'），默认None表示所有Python文件
        """
        try:
            if not os.path.isdir(directory_path):
                return {
                    'success': False,
                    'error': f'目录不存在: {directory_path}',
                    'issues': []
                }
            
            # 构建命令
            cmd = ['python', '-m', 'pylint', '--output-format=json'] + self.pylint_args
            
            # 设置环境变量
            env = os.environ.copy()
            env['PAGER'] = ''
            env['LESS'] = ''
            env['PYTHONUNBUFFERED'] = '1'
            env['TERM'] = 'dumb'
            
            # Windows上添加参数
            if os.name == 'nt' and '--disable=C0114' not in cmd:
                cmd.extend(['--disable=C0114'])
            
            # 添加目录或文件模式
            if file_pattern:
                # 使用find或glob模式（需要根据系统调整）
                import glob
                pattern = os.path.join(directory_path, '**', file_pattern)
                files = glob.glob(pattern, recursive=True)
                if not files:
                    return {
                        'success': True,
                        'issues': [],
                        'total_issues': 0,
                        'message': f'未找到匹配 {file_pattern} 的文件'
                    }
                cmd.extend(files)
            else:
                # 直接分析目录（Pylint支持）
                cmd.append(directory_path)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 目录分析可能需要更长时间
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
                except json.JSONDecodeError:
                    # JSON解析失败，返回空结果
                    pass
            
            # 即使有很多问题，也不认为是失败（除非是致命错误）
            success = result.returncode != 1
            
            return {
                'success': success,
                'issues': issues,
                'total_issues': len(issues),
                'return_code': result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Pylint目录分析超时',
                'issues': []
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'issues': []
            }
    
    async def fix_issues(self, issues: List[Dict[str, Any]], project_path: str) -> Dict[str, Any]:
        """尝试自动修复Pylint问题"""
        return {
            'success': False,
            'message': 'Pylint自动修复功能待实现',
            'fixed_issues': []
        }
