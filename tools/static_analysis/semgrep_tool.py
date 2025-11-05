"""
Semgrep工具封装
基于规则引擎的静态分析工具，用于检测Flask特定的问题模式
"""

import subprocess
import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path


class SemgrepTool:
    """Semgrep静态分析工具"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get('enabled', True)
        self.semgrep_args = config.get('semgrep_args', [])
        self.rules_configs = config.get('rules_configs', ['python', 'p/python'])  # 默认使用Python规则
        self.custom_rules = config.get('custom_rules', [])  # 自定义规则文件路径
        
    async def analyze(self, file_path: str) -> Dict[str, Any]:
        """执行Semgrep分析单个文件"""
        try:
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': f'文件不存在: {file_path}',
                    'issues': []
                }
            
            # 构建命令（Semgrep新版本需要使用scan子命令）
            # 注意：--quiet等参数从self.semgrep_args中读取，避免重复
            cmd = ['semgrep', 'scan', '--json']
            
            # 添加规则配置
            for rule_config in self.rules_configs:
                cmd.extend(['--config', rule_config])
            
            # 添加自定义规则（支持相对路径和绝对路径）
            for rule_file in self.custom_rules:
                # 处理相对路径
                if not os.path.isabs(rule_file):
                    # 尝试从项目根目录查找
                    base_dir = Path(__file__).parent.parent.parent  # 回到项目根目录
                    rule_path = base_dir / rule_file
                    if rule_path.exists():
                        rule_file = str(rule_path.resolve())
                    elif os.path.exists(rule_file):
                        rule_file = os.path.abspath(rule_file)
                
                if os.path.exists(rule_file):
                    cmd.extend(['--config', rule_file])
                else:
                    # 记录警告但继续执行
                    import logging
                    logging.warning(f"Semgrep规则文件不存在: {rule_file}")
            
            # 添加额外参数
            cmd.extend(self.semgrep_args)
            
            # 添加文件路径
            cmd.append(file_path)
            
            # 设置环境变量
            env = os.environ.copy()
            env['SEMGREP_SEND_METRICS'] = 'off'
            # 在Windows上强制使用UTF-8编码，避免读取规则文件时的编码错误
            if os.name == 'nt':
                env['PYTHONIOENCODING'] = 'utf-8'
                env['PYTHONUTF8'] = '1'
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',  # 明确指定编码
                errors='replace',  # 遇到编码错误时替换而不是失败
                timeout=60,  # Semgrep可能需要更长时间
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            issues = []
            
            # 解析JSON输出
            if result.stdout:
                try:
                    semgrep_output = json.loads(result.stdout)
                    results = semgrep_output.get('results', [])
                    
                    for match in results:
                        issues.append({
                            'type': 'semgrep',
                            'severity': match.get('extra', {}).get('severity', 'ERROR').lower(),
                            'message': match.get('message', ''),
                            'file': match.get('path', file_path),
                            'line': match.get('start', {}).get('line', 0),
                            'column': match.get('start', {}).get('col', 0),
                            'end_line': match.get('end', {}).get('line', 0),
                            'end_column': match.get('end', {}).get('col', 0),
                            'rule_id': match.get('check_id', ''),
                            'rule_name': match.get('extra', {}).get('metadata', {}).get('name', ''),
                            'confidence': match.get('extra', {}).get('metadata', {}).get('confidence', 'MEDIUM')
                        })
                except json.JSONDecodeError:
                    # JSON解析失败，尝试文本输出
                    if result.stdout.strip():
                        lines = result.stdout.strip().split('\n')
                        for line in lines:
                            if ':' in line:
                                parts = line.split(':', 3)
                                if len(parts) >= 4:
                                    issues.append({
                                        'type': 'semgrep',
                                        'severity': 'warning',
                                        'message': parts[3].strip(),
                                        'file': parts[0],
                                        'line': int(parts[1]) if parts[1].isdigit() else 0,
                                        'column': int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0,
                                        'rule_id': 'unknown'
                                    })
            
            return {
                'success': True,
                'issues': issues,
                'total_issues': len(issues),
                'stdout': result.stdout[:500] if result.stdout else '',  # 限制输出长度
                'stderr': result.stderr[:500] if result.stderr else ''
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Semgrep执行超时',
                'issues': []
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'issues': []
            }
    
    async def analyze_directory(self, directory_path: str) -> Dict[str, Any]:
        """执行Semgrep分析整个目录（更高效）"""
        try:
            if not os.path.isdir(directory_path):
                return {
                    'success': False,
                    'error': f'目录不存在: {directory_path}',
                    'issues': []
                }
            
            # 构建命令（Semgrep新版本需要使用scan子命令）
            # 注意：--quiet等参数从self.semgrep_args中读取，避免重复
            cmd = ['semgrep', 'scan', '--json']
            
            # 添加规则配置
            for rule_config in self.rules_configs:
                cmd.extend(['--config', rule_config])
            
            # 添加自定义规则（支持相对路径和绝对路径）
            for rule_file in self.custom_rules:
                # 处理相对路径
                if not os.path.isabs(rule_file):
                    # 尝试从项目根目录查找
                    base_dir = Path(__file__).parent.parent.parent  # 回到项目根目录
                    rule_path = base_dir / rule_file
                    if rule_path.exists():
                        rule_file = str(rule_path.resolve())
                    elif os.path.exists(rule_file):
                        rule_file = os.path.abspath(rule_file)
                
                if os.path.exists(rule_file):
                    cmd.extend(['--config', rule_file])
                else:
                    # 记录警告但继续执行
                    import logging
                    logging.warning(f"Semgrep规则文件不存在: {rule_file}")
            
            # 添加额外参数
            cmd.extend(self.semgrep_args)
            
            # 添加目录路径
            cmd.append(directory_path)
            
            # 设置环境变量
            env = os.environ.copy()
            env['SEMGREP_SEND_METRICS'] = 'off'
            # 在Windows上强制使用UTF-8编码，避免读取规则文件时的编码错误
            if os.name == 'nt':
                env['PYTHONIOENCODING'] = 'utf-8'
                env['PYTHONUTF8'] = '1'
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',  # 明确指定编码
                errors='replace',  # 遇到编码错误时替换而不是失败
                timeout=300,  # 目录扫描可能需要更长时间
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            issues = []
            
            # Semgrep返回码说明：
            # 0 = 成功，无问题
            # 1 = 成功，发现问题
            # 2 = 部分成功（如配置文件错误）或成功但无匹配
            # 其他 = 错误
            # 我们只要stdout有JSON输出就认为成功，返回码不影响
            if result.stdout:
                try:
                    semgrep_output = json.loads(result.stdout)
                    results = semgrep_output.get('results', [])
                    
                    for match in results:
                        issues.append({
                            'type': 'semgrep',
                            'severity': match.get('extra', {}).get('severity', 'ERROR').lower(),
                            'message': match.get('message', ''),
                            'file': match.get('path', ''),
                            'line': match.get('start', {}).get('line', 0),
                            'column': match.get('start', {}).get('col', 0),
                            'end_line': match.get('end', {}).get('line', 0),
                            'end_column': match.get('end', {}).get('col', 0),
                            'rule_id': match.get('check_id', ''),
                            'rule_name': match.get('extra', {}).get('metadata', {}).get('name', ''),
                            'confidence': match.get('extra', {}).get('metadata', {}).get('confidence', 'MEDIUM')
                        })
                except json.JSONDecodeError as e:
                    # JSON解析失败，记录错误但尝试从stderr获取信息
                    error_msg = f'Semgrep JSON解析失败: {e}'
                    if result.stderr:
                        error_msg += f'\nStderr: {result.stderr[:500]}'
                    return {
                        'success': False,
                        'error': error_msg,
                        'issues': [],
                        'stdout': result.stdout[:500] if result.stdout else '',
                        'returncode': result.returncode
                    }
            elif result.returncode != 0 and result.stderr:
                # 没有stdout但有错误，可能是配置文件错误或其他问题
                return {
                    'success': False,
                    'error': f'Semgrep执行失败 (返回码: {result.returncode}): {result.stderr[:500]}',
                    'issues': [],
                    'returncode': result.returncode
                }
            
            result_data = {
                'success': True,
                'issues': issues,
                'total_issues': len(issues),
            }
            
            # 添加调试信息
            if 'semgrep_output' in locals():
                result_data['files_scanned'] = semgrep_output.get('paths', {}).get('scanned', [])
                result_data['rules_loaded'] = len(semgrep_output.get('rules', []))
                # 记录返回码和是否有stderr
                result_data['returncode'] = result.returncode
                if result.stderr:
                    result_data['stderr'] = result.stderr[:500]  # 只记录前500字符
            
            return result_data
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Semgrep执行超时',
                'issues': []
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'issues': []
            }
