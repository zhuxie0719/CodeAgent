"""
代码质量检查器模块
专注于单文件分析
"""

import os
import ast
import re
import subprocess
import json
import asttokens
from typing import Dict, List, Any, Optional
from datetime import datetime
import requests


class StyleChecker:
    """代码风格检查器 - 专注单文件分析"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    async def analyze_single_file(self, file_path: str, file_content: str) -> List[Dict[str, Any]]:
        """分析单个文件的代码风格"""
        issues = []
        
        # 基础代码风格检查
        issues.extend(self._check_line_length(file_content))
        issues.extend(self._check_naming_conventions(file_content))
        issues.extend(self._check_indentation(file_content))
        issues.extend(self._check_comments(file_content))
        issues.extend(self._check_imports(file_content))
        
        return issues
    
    def _check_line_length(self, file_content: str) -> List[Dict[str, Any]]:
        """检查行长度"""
        issues = []
        max_line_length = self.config.get('max_line_length', 120)
        
        lines = file_content.split('\n')
        for i, line in enumerate(lines, 1):
            if len(line) > max_line_length:
                issues.append({
                    'type': 'line_length',
                    'severity': 'warning',
                    'line': i,
                    'message': f'行长度超过{max_line_length}字符限制',
                    'content': line[:50] + '...' if len(line) > 50 else line
                })
        
        return issues
    
    def _check_naming_conventions(self, file_content: str) -> List[Dict[str, Any]]:
        """检查命名规范"""
        issues = []
        
        try:
            tree = ast.parse(file_content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not re.match(r'^[a-z_][a-z0-9_]*$', node.name):
                        issues.append({
                            'type': 'naming',
                            'severity': 'warning',
                            'line': node.lineno,
                            'message': f'函数名"{node.name}"不符合小写下划线命名规范',
                            'suggestion': '建议使用小写字母和下划线，如：function_name'
                        })
                
                elif isinstance(node, ast.ClassDef):
                    if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                        issues.append({
                            'type': 'naming',
                            'severity': 'warning',
                            'line': node.lineno,
                            'message': f'类名"{node.name}"不符合大驼峰命名规范',
                            'suggestion': '建议使用大驼峰命名，如：ClassName'
                        })
                
                elif isinstance(node, ast.Name):
                    if isinstance(node.ctx, ast.Store):
                        if not re.match(r'^[a-z_][a-z0-9_]*$', node.id):
                            issues.append({
                                'type': 'naming',
                                'severity': 'warning',
                                'line': node.lineno,
                                'message': f'变量名"{node.id}"不符合小写下划线命名规范',
                                'suggestion': '建议使用小写字母和下划线，如：variable_name'
                            })
        
        except SyntaxError:
            # 如果不是Python文件，跳过语法检查
            pass
        
        return issues
    
    def _check_indentation(self, file_content: str) -> List[Dict[str, Any]]:
        """检查缩进一致性"""
        issues = []
        lines = file_content.split('\n')
        
        # 检测使用的缩进方式
        tabs_count = 0
        spaces_2_count = 0
        spaces_4_count = 0
        
        for line in lines:
            if line.startswith(' '):
                if line.startswith('  ') and not line.startswith('    '):
                    spaces_2_count += 1
                elif line.startswith('    '):
                    spaces_4_count += 1
            elif line.startswith('\t'):
                tabs_count += 1
        
        # 检查是否混合使用不同的缩进
        total_indented = tabs_count + spaces_2_count + spaces_4_count
        if total_indented > 0:
            dominant = max([(tabs_count, 'tab'), (spaces_2_count, 'space2'), (spaces_4_count, 'space4')])
            if tabs_count > 0 and spaces_2_count + spaces_4_count > 0:
                issues.append({
                    'type': 'indentation',
                    'severity': 'error',
                    'message': '混合使用制表符和空格进行缩进',
                    'suggestion': f'建议统一只使用{dominant[1]}缩进'
                })
        
        return issues
    
    def _check_comments(self, file_content: str) -> List[Dict[str, Any]]:
        """检查注释覆盖率"""
        issues = []
        
        lines = file_content.split('\n')
        code_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
        comment_lines = [line for line in lines if line.strip().startswith('#')]
        
        if len(code_lines) > 10:  # 只有足够长的文件才检查注释
            comment_ratio = len(comment_lines) / len(code_lines)
            if comment_ratio < 0.1:  # 注释覆盖率低于10%
                issues.append({
                    'type': 'documentation',
                    'severity': 'info',
                    'message': f'注释覆盖率较低({comment_ratio:.1%})，建议增加注释',
                    'suggestion': '建议为复杂函数和类添加文档字符串'
                })
        
        return issues
    
    def _check_imports(self, file_content: str) -> List[Dict[str, Any]]:
        """检查导入语句"""
        issues = []
        
        try:
            atok = asttokens.ASTTokens(file_content, parse=True)
            tree = atok.tree
            
            import_lines = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    import_lines.append(node)
            
            # 检查导入语句是否按照标准库、第三方库、本地库的顺序
            stdlib_after_other = False
            third_party_after_local = False
            
            for i, node in enumerate(import_lines):
                if isinstance(node, ast.ImportFrom):
                    module = node.module
                    if module and not module.startswith('.'):
                        # 检查是否是标准库
                        try:
                            __import__(module)
                            if i > 0 and not stdlib_after_other:
                                prev_node = import_lines[i-1]
                                if isinstance(prev_node, ast.ImportFrom) and prev_node.module:
                                    try:
                                        __import__(prev_node.module)
                                    except ModuleNotFoundError:
                                        stdlib_after_other = True
                        except ModuleNotFoundError:
                            # 第三方库
                            pass
            
            if stdlib_after_other:
                issues.append({
                    'type': 'import_order',
                    'severity': 'warning',
                    'message': '导入语句顺序不规范',
                    'suggestion': '建议按照标准库、第三方库、本地库的顺序排列导入语句'
                })
        
        except Exception:
            pass
        
        return issues


class QualityMetricsCalculator:
    """代码质量指标计算器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    async def calculate_metrics(self, file_path: str, file_content: str) -> Dict[str, Any]:
        """计算代码质量指标"""
        metrics = {
            'lines_of_code': 0,
            'comment_lines': 0,
            'blank_lines': 0,
            'complexity_score': 0.0,
            'maintainability_score': 0.0,
            'readability_score': 0.0,
            'function_count': 0,
            'class_count': 0,
            'average_function_length': 0,
            'duplicate_lines': 0,
            'cyclomatic_complexity': 0
        }
        
        try:
            # 基础统计
            lines = file_content.split('\n')
            metrics['lines_of_code'] = len([line for line in lines if line.strip()])
            metrics['comment_lines'] = len([line for line in lines if line.strip().startswith('#')])
            metrics['blank_lines'] = len([line for line in lines if not line.strip()])
            
            # Python AST分析
            if file_path.endswith('.py'):
                tree = ast.parse(file_content, file_path)
                
                # 计算函数和类数量
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        metrics['function_count'] += 1
                        metrics['cyclomatic_complexity'] += self._calculate_complexity(node)
                    elif isinstance(node, ast.ClassDef):
                        metrics['class_count'] += 1
                
                # 计算平均函数长度
                if metrics['function_count'] > 0:
                    function_lines = 0
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            function_lines += self._get_function_length(node, lines)
                    metrics['average_function_length'] = function_lines / metrics['function_count']
                
                # 计算复杂度分数 (1-10，分数越低越好)
                metrics['complexity_score'] = min(10.0, metrics['cyclomatic_complexity'] / max(1, metrics['function_count']) * 2)
                
                # 计算可维护性分数 (1-10，分数越高越好)
                readability_factors = [
                    metrics['lines_of_code'] < 500,  # 文件不能太长
                    metrics['comment_lines'] / max(1, metrics['lines_of_code']) > 0.1,  # 有足够的注释
                    metrics['cyclomatic_complexity'] / max(1, metrics['function_count']) < 5,  # 平均复杂度不高
                    metrics['average_function_length'] < 50  # 平均函数长度适中
                ]
                metrics['maintainability_score'] = sum(readability_factors) / len(readability_factors) * 10
                
                # 计算可读性分数
                metrics['readability_score'] = min(10.0, max(1.0, 10 - metrics['complexity_score'] + 
                                                          (metrics['comment_lines'] / max(1, metrics['lines_of_code'])) * 5))
            
        except Exception as e:
            print(f"计算指标时出错: {e}")
        
        return metrics
    
    def _calculate_complexity(self, node) -> int:
        """计算节点复杂度"""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
        return complexity
    
    def _get_function_length(self, func_node, lines) -> int:
        """获取函数行数"""
        return func_node.end_lineno - func_node.lineno + 1 if hasattr(func_node, 'end_lineno') else len(lines)


class AICodeQualityAnalyzer:
    """AI代码质量分析器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = config.get('ai_api_key')
        self.base_url = config.get('ai_base_url', 'https://api.deepseek.com/v1/chat/completions')
    
    async def generate_quality_report(self, file_path: str, file_content: str, 
                                    style_issues: List[Dict], metrics: Dict[str, Any]) -> Dict[str, Any]:
        """使用AI生成代码质量报告"""
        
        # 构造分析上下文
        context = self._build_analysis_context(file_path, file_content, style_issues, metrics)
        
        # 调用AI接口
        prompt = f"""
作为一名资深代码审查专家，请对以下代码文件进行全面的质量分析并提供详细的评分报告。

文件路径：{file_path}

代码内容：
```python
{file_content}
```

发现的风格问题：
{json.dumps(style_issues, ensure_ascii=False, indent=2)}

计算的质量指标：
{json.dumps(metrics, ensure_ascii=False, indent=2)}

请从以下几个方面给出详细的评分报告：
1. 代码风格 (15分) - 命名规范、格式一致性、注释质量
2. 代码结构 (20分) - 模块化、函数设计、类设计
3. 性能和效率 (15分) - 算法效率、资源使用
4. 安全性 (15分) - 输入验证、错误处理、潜在漏洞
5. 可维护性 (15分) - 代码复杂度、可读性
6. 可测试性 (10分) - 测试友好性、依赖管理
7. 文档和质量 (10分) - 注释完整性、文档质量

请按照以下JSON格式返回结果：
{{
    "overall_score": 85,
    "grade": "B",
    "detailed_scores": {{
        "style": 15,
        "structure": 18,
        "performance": 12,
        "security": 14,
        "maintainability": 13,
        "testability": 8,
        "documentation": 9
    }},
    "strengths": ["优势1", "优势2"],
    "weaknesses": ["问题1", "问题2"],
    "suggestions": ["建议1", "建议2"],
    "critical_issues": ["严重问题1"],
    "summary": "总体评价和建议的文字描述"
}}
        """
        
        try:
            response = await self._call_ai_api(prompt)
            return response
        except Exception as e:
            return {
                'error': f'AI分析失败: {str(e)}',
                'fallback_report': self._generate_fallback_report(style_issues, metrics)
            }
    
    def _build_analysis_context(self, file_path: str, file_content: str, 
                               style_issues: List[Dict], metrics: Dict[str, Any]) -> Dict[str, Any]:
        """构建分析上下文"""
        return {
            'file_info': {
                'path': file_path,
                'size': len(file_content),
                'language': self._detect_language(file_path)
            },
            'style_issues_count': len(style_issues),
            'critical_issues': [issue for issue in style_issues if issue.get('severity') == 'error'],
            'warnings': [issue for issue in style_issues if issue.get('severity') == 'warning'],
            'metrics': metrics
        }
    
    def _detect_language(self, file_path: str) -> str:
        """检测编程语言"""
        ext_mapping = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C',
            '.cs': 'C#'
        }
        
        ext = os.path.splitext(file_path)[1]
        return ext_mapping.get(ext, 'Unknown')
    
    async def _call_ai_api(self, prompt: str) -> Dict[str, Any]:
        """调用AI接口"""
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        
        data = {
            'model': 'deepseek-coder',
            'messages': [
                {
                    'role': 'system',
                    'content': '你是一个专业的代码质量分析专家，擅长提供详细、准确、实用的代码评分和改进建议。'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': 0.3,
            'max_tokens': 2000
        }
        
        response = requests.post(self.base_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        content = result['choices'][0]['message']['content']
        
        # 尝试解析JSON格式的回复
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # 尝试从Markdown代码块中提取JSON
            try:
                import re
                # 寻找```json ... ```格式的内容
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
                if json_match:
                    json_content = json_match.group(1)
                    return json.loads(json_content)
                else:
                    raise json.JSONDecodeError('No JSON found in markdown')
            except (json.JSONDecodeError, ValueError):
                return {
                    'error': 'AI返回格式错误',
                    'raw_response': content,
                    'fallback_report': self._generate_fallback_report([], {})
                }
    
    def _generate_fallback_report(self, style_issues: List[Dict], metrics: Dict[str, Any]) -> Dict[str, Any]:
        """生成备用报告"""
        # 基于已有的指标和问题生成备用报告
        issues_count = len(style_issues)
        critical_count = len([i for i in style_issues if i.get('severity') == 'error'])
        
        # 计算基本分数
        base_score = 80
        if critical_count > 0:
            base_score -= critical_count * 10
        if issues_count > 10:
            base_score -= (issues_count - 10) * 2
        
        # 确定等级
        if base_score >= 90:
            grade = 'A'
        elif base_score >= 80:
            grade = 'B'
        elif base_score >= 70:
            grade = 'C'
        elif base_score >= 60:
            grade = 'D'
        else:
            grade = 'F'
        
        return {
            'overall_score': max(0, base_score),
            'grade': grade,
            'detailed_scores': {
                'style': max(0, 15 - issues_count),
                'structure': metrics.get('maintainability_score', 5) * 1.5,
                'performance': 12,
                'security': 10 if critical_count == 0 else 5,
                'maintainability': metrics.get('maintainability_score', 8),
                'testability': 8,
                'documentation': 8
            },
            'strengths': ['代码基本结构清晰'] if base_score >= 60 else [],
            'weaknesses': ['存在代码质量问题'] if issues_count > 0 else [],
            'suggestions': ['建议参考详细报告进行改进'],
            'critical_issues': [issue for issue in style_issues if issue.get('severity') == 'error'],
            'summary': f'基于基础分析，代码质量为{grade}级(评分: {base_score}分)。'
        }


async def analyze_file_quality(file_path: str, file_content: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """分析单文件质量的入口函数"""
    try:
        # 初始化分析器
        style_checker = StyleChecker(config)
        metrics_calculator = QualityMetricsCalculator(config)
        ai_analyzer = AICodeQualityAnalyzer(config)
        
        # 执行风格检查
        style_issues = await style_checker.analyze_single_file(file_path, file_content)
        
        # 计算质量指标
        metrics = await metrics_calculator.calculate_metrics(file_path, file_content)
        
        # 生成AI质量报告
        ai_report = await ai_analyzer.generate_quality_report(file_path, file_content, style_issues, metrics)
        
        # 汇总结果
        return {
            'success': True,
            'file_path': file_path,
            'file_size': len(file_content),
            'analysis_time': datetime.now().isoformat(),
            'style_issues': style_issues,
            'metrics': metrics,
            'ai_report': ai_report,
            'summary': {
                'total_issues': len(style_issues),
                'critical_issues': len([i for i in style_issues if i.get('severity') == 'error']),
                'warnings': len([i for i in style_issues if i.get('severity') == 'warning']),
                'overall_score': ai_report.get('overall_score', 0),
                'grade': ai_report.get('grade', 'F')
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'file_path': file_path,
            'analysis_time': datetime.now().isoformat()
        }