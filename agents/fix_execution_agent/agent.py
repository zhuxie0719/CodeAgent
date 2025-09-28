"""
修复执行AGENT主类
"""

import asyncio
import re
from typing import Dict, List, Any, Optional
from .fixer import CodeFixer, Refactorer, DependencyUpdater


class FixExecutionAgent:
    """修复执行AGENT"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.code_fixer = CodeFixer(config)
        self.refactorer = Refactorer(config)
        self.dependency_updater = DependencyUpdater(config)
        self.is_running = False
    
    async def start(self):
        """启动AGENT"""
        self.is_running = True
        print("修复执行AGENT已启动")
    
    async def stop(self):
        """停止AGENT"""
        self.is_running = False
        print("修复执行AGENT已停止")
    
    async def process_task(self, task_id: str, task_manager) -> Dict[str, Any]:
        """处理任务 - 核心方法，接收task_id"""
        try:
            # 1. 从TaskManager获取任务数据
            task = task_manager.get_task(task_id)
            if not task:
                return {'success': False, 'error': f'任务 {task_id} 不存在'}
            
            task_data = task['data']
            project_path = task_data.get('project_path', '')
            issues = task_data.get('issues', [])
            
            print(f"开始处理任务 {task_id}: {len(issues)} 个缺陷")
            
            # 2. 执行修复
            fix_result = await self.process_issues(issues, project_path)
            
            # 3. 更新任务状态
            task_manager.update_task_result(task_id, fix_result)
            
            return fix_result
            
        except Exception as e:
            error_result = {'success': False, 'error': str(e)}
            task_manager.update_task_result(task_id, error_result)
            return error_result
    
    async def process_issues(self, issues: List[Dict[str, Any]], project_path: str) -> Dict[str, Any]:
        """处理多个缺陷"""
        try:
            results = {
                'total_issues': len(issues),
                'fixed_issues': 0,
                'failed_issues': 0,
                'skipped_issues': 0,
                'changes': [],
                'errors': [],
                'timestamp': asyncio.get_event_loop().time()
            }
            
            print(f"开始处理 {len(issues)} 个缺陷...")
            
            for i, issue in enumerate(issues, 1):
                try:
                    # 判断缺陷复杂度
                    complexity = self._classify_issue_complexity(issue)
                    
                    if complexity == 'simple':
                        # 简单缺陷，直接修复
                        print(f"处理简单缺陷 {i}/{len(issues)}: {issue.get('message', '')[:50]}...")
                        result = await self.execute_fix(issue, project_path)
                        
                        if result['success']:
                            results['fixed_issues'] += 1
                            results['changes'].extend(result.get('changes', []))
                            print(f"✓ 修复成功: {issue.get('file', '')}")
                        else:
                            results['failed_issues'] += 1
                            results['errors'].append(f"修复失败: {result.get('message', '')}")
                            print(f"✗ 修复失败: {result.get('message', '')}")
                    
                    elif complexity == 'complex':
                        # 复杂缺陷，记录但不自动修复
                        results['skipped_issues'] += 1
                        results['changes'].append(f"跳过复杂缺陷: {issue.get('message', '')[:100]}")
                        print(f"⚠ 跳过复杂缺陷 {i}/{len(issues)}: {issue.get('message', '')[:50]}...")
                    
                    else:
                        # 未知类型缺陷
                        results['skipped_issues'] += 1
                        results['changes'].append(f"跳过未知类型缺陷: {issue.get('type', 'unknown')}")
                        print(f"? 跳过未知类型缺陷 {i}/{len(issues)}: {issue.get('type', 'unknown')}")
                
                except Exception as e:
                    results['failed_issues'] += 1
                    results['errors'].append(f"处理缺陷时出错: {str(e)}")
                    print(f"✗ 处理缺陷时出错: {e}")
            
            # 计算成功率
            if results['total_issues'] > 0:
                results['success_rate'] = results['fixed_issues'] / results['total_issues']
            else:
                results['success_rate'] = 0.0
            
            print(f"缺陷处理完成: 总计{results['total_issues']}, 修复{results['fixed_issues']}, 失败{results['failed_issues']}, 跳过{results['skipped_issues']}")
            
            return results
            
        except Exception as e:
            print(f"批量处理缺陷失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'total_issues': len(issues) if issues else 0,
                'fixed_issues': 0,
                'failed_issues': 0,
                'skipped_issues': 0,
                'changes': [],
                'errors': [str(e)]
            }
    
    async def execute_fix(self, issue: Dict[str, Any], project_path: str) -> Dict[str, Any]:
        """执行修复"""
        try:
            fix_result = {
                'success': False,
                'changes': [],
                'message': '',
                'timestamp': asyncio.get_event_loop().time()
            }
            
            # 根据问题类型选择修复策略
            issue_type = issue.get('type', '')
            
            if issue_type in ['pylint', 'flake8']:
                fix_result = await self.code_fixer.fix_code_style(issue, project_path)
            elif issue_type == 'bandit':
                fix_result = await self.code_fixer.fix_security_issue(issue, project_path)
            elif issue_type == 'refactor':
                fix_result = await self.refactorer.refactor_code(issue, project_path)
            elif issue_type == 'dependency':
                fix_result = await self.dependency_updater.update_dependency(issue, project_path)
            
            return fix_result
        except Exception as e:
            print(f"修复执行失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def _classify_issue_complexity(self, issue: Dict[str, Any]) -> str:
        """判断缺陷复杂度"""
        try:
            issue_type = issue.get('type', '').lower()
            severity = issue.get('severity', 'info').lower()
            message = issue.get('message', '').lower()
            
            # 简单缺陷：格式、风格问题
            if issue_type in ['pylint', 'flake8']:
                # 根据严重程度判断
                if severity in ['info', 'warning']:
                    # 进一步根据消息内容判断
                    simple_keywords = [
                        'indentation', 'blank line', 'whitespace', 'trailing whitespace',
                        'line too long', 'missing docstring', 'unused import',
                        'too many blank lines', 'line break before binary operator',
                        'missing final newline', 'unexpected indentation'
                    ]
                    
                    if any(keyword in message for keyword in simple_keywords):
                        return 'simple'
                    else:
                        return 'complex'
                else:
                    return 'complex'
            
            # 安全问题通常是复杂缺陷
            elif issue_type == 'bandit':
                return 'complex'
            
            # 重构和依赖更新通常是复杂缺陷
            elif issue_type in ['refactor', 'dependency']:
                return 'complex'
            
            # 根据消息内容进一步判断
            complex_keywords = [
                'security', 'vulnerability', 'injection', 'xss', 'csrf',
                'authentication', 'authorization', 'cryptography',
                'business logic', 'algorithm', 'performance', 'memory leak'
            ]
            
            if any(keyword in message for keyword in complex_keywords):
                return 'complex'
            
            # 默认根据严重程度判断
            if severity in ['error', 'critical']:
                return 'complex'
            elif severity in ['warning', 'info']:
                return 'simple'
            
            return 'unknown'
            
        except Exception as e:
            print(f"分类缺陷复杂度失败: {e}")
            return 'unknown'
    
    def _is_simple_style_issue(self, issue: Dict[str, Any]) -> bool:
        """判断是否为简单风格问题"""
        message = issue.get('message', '').lower()
        simple_patterns = [
            r'missing.*blank line',
            r'too many blank lines',
            r'trailing whitespace',
            r'line too long',
            r'unexpected indentation',
            r'missing final newline',
            r'unused import',
            r'import.*not.*used'
        ]
        
        return any(re.search(pattern, message) for pattern in simple_patterns)
    
    def _is_security_issue(self, issue: Dict[str, Any]) -> bool:
        """判断是否为安全问题"""
        issue_type = issue.get('type', '').lower()
        message = issue.get('message', '').lower()
        
        if issue_type == 'bandit':
            return True
        
        security_keywords = [
            'security', 'vulnerability', 'injection', 'xss', 'csrf',
            'authentication', 'authorization', 'cryptography', 'hash',
            'password', 'token', 'session', 'cookie'
        ]
        
        return any(keyword in message for keyword in security_keywords)
    
    async def get_fix_summary(self, results: Dict[str, Any]) -> str:
        """生成修复摘要"""
        try:
            summary = f"""
修复执行摘要:
==============
总缺陷数: {results.get('total_issues', 0)}
成功修复: {results.get('fixed_issues', 0)}
修复失败: {results.get('failed_issues', 0)}
跳过处理: {results.get('skipped_issues', 0)}
成功率: {results.get('success_rate', 0):.1%}

修复详情:
"""
            
            if results.get('changes'):
                summary += "\n修复内容:\n"
                for change in results['changes'][:10]:  # 只显示前10个
                    summary += f"- {change}\n"
                
                if len(results['changes']) > 10:
                    summary += f"... 还有 {len(results['changes']) - 10} 个修复\n"
            
            if results.get('errors'):
                summary += "\n错误信息:\n"
                for error in results['errors'][:5]:  # 只显示前5个错误
                    summary += f"- {error}\n"
                
                if len(results['errors']) > 5:
                    summary += f"... 还有 {len(results['errors']) - 5} 个错误\n"
            
            return summary.strip()
            
        except Exception as e:
            return f"生成摘要失败: {e}"
