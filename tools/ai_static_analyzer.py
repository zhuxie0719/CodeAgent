"""
AI多语言静态缺陷检测器
支持Java、C++、JavaScript、Go、Rust等语言的AI分析
"""

import os
import re
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import httpx
from api.deepseek_config import deepseek_config

class LanguageType(Enum):
    """支持的语言类型"""
    PYTHON = "python"
    JAVA = "java"
    CPP = "cpp"
    C = "c"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    GO = "go"
    RUST = "rust"
    CSHARP = "csharp"
    PHP = "php"
    RUBY = "ruby"
    SWIFT = "swift"
    KOTLIN = "kotlin"

@dataclass
class CodeIssue:
    """代码问题数据结构"""
    file_path: str
    line_number: int
    column: int
    severity: str  # error, warning, info
    category: str   # security, performance, style, logic, best_practice
    message: str
    suggestion: str
    language: str
    confidence: float

@dataclass
class AnalysisResult:
    """分析结果数据结构"""
    language: str
    files_analyzed: int
    issues_found: int
    issues: List[CodeIssue]
    metrics: Dict[str, Any]
    summary: str

class AIMultiLanguageAnalyzer:
    """AI多语言静态分析器"""
    
    def __init__(self):
        self.config = deepseek_config
        self.supported_extensions = {
            '.java': LanguageType.JAVA,
            '.cpp': LanguageType.CPP,
            '.cc': LanguageType.CPP,
            '.cxx': LanguageType.CPP,
            '.c': LanguageType.C,
            '.h': LanguageType.C,
            '.hpp': LanguageType.CPP,
            '.js': LanguageType.JAVASCRIPT,
            '.ts': LanguageType.TYPESCRIPT,
            '.go': LanguageType.GO,
            '.rs': LanguageType.RUST,
            '.cs': LanguageType.CSHARP,
            '.php': LanguageType.PHP,
            '.rb': LanguageType.RUBY,
            '.swift': LanguageType.SWIFT,
            '.kt': LanguageType.KOTLIN,
            '.kts': LanguageType.KOTLIN
        }
        
        # 语言特定的检测规则
        self.language_rules = {
            LanguageType.JAVA: self._get_java_rules(),
            LanguageType.CPP: self._get_cpp_rules(),
            LanguageType.C: self._get_c_rules(),
            LanguageType.JAVASCRIPT: self._get_javascript_rules(),
            LanguageType.GO: self._get_go_rules(),
            LanguageType.RUST: self._get_rust_rules()
        }
    
    def _get_java_rules(self) -> Dict[str, Any]:
        """Java特定检测规则"""
        return {
            "security_patterns": [
                r"System\.out\.print",  # 调试输出
                r"printStackTrace",      # 异常堆栈打印
                r"Runtime\.getRuntime\(\)\.exec",  # 命令执行
                r"ProcessBuilder",       # 进程构建
                r"Class\.forName",        # 动态类加载
                r"URLClassLoader",        # URL类加载器
                r"Serializable",         # 序列化风险
                r"ObjectInputStream",    # 反序列化
                r"SQLException",         # SQL注入风险
                r"PreparedStatement",    # SQL预处理
            ],
            "performance_patterns": [
                r"String\s*\+\s*String",  # 字符串拼接
                r"new\s+String\s*\(",     # 不必要的字符串创建
                r"System\.gc\(\)",        # 手动垃圾回收
                r"Thread\.sleep",         # 线程睡眠
                r"while\s*\(\s*true\s*\)", # 无限循环
            ],
            "style_patterns": [
                r"public\s+class\s+\w*[a-z]",  # 类名不符合规范
                r"public\s+void\s+\w*[A-Z]",    # 方法名不符合规范
                r"import\s+\*",                  # 通配符导入
                r"@SuppressWarnings",            # 抑制警告
            ],
            "best_practices": [
                r"catch\s*\(\s*Exception\s*\)",  # 捕获通用异常
                r"null\s*==\s*",                 # 空值检查顺序
                r"equals\s*\(\s*\"",             # 字符串比较
            ]
        }
    
    def _get_cpp_rules(self) -> Dict[str, Any]:
        """C++特定检测规则"""
        return {
            "security_patterns": [
                r"strcpy\s*\(",          # 不安全的字符串复制
                r"strcat\s*\(",          # 不安全的字符串连接
                r"sprintf\s*\(",        # 不安全的格式化
                r"gets\s*\(",            # 不安全的输入
                r"scanf\s*\(",           # 格式化字符串风险
                r"system\s*\(",          # 系统命令执行
                r"malloc\s*\(",          # 内存分配
                r"free\s*\(",            # 内存释放
                r"delete\s+",            # 内存删除
                r"new\s+",               # 动态分配
            ],
            "performance_patterns": [
                r"std::endl",            # 频繁换行
                r"std::cout",             # 控制台输出
                r"#include\s*<iostream>", # 不必要的头文件
                r"using\s+namespace\s+std", # 使用命名空间
            ],
            "style_patterns": [
                r"goto\s+",             # goto语句
                r"#define\s+",           # 宏定义
                r"#ifdef\s+",            # 条件编译
                r"int\s+main\s*\(",      # main函数
            ],
            "best_practices": [
                r"std::auto_ptr",        # 已废弃的智能指针
                r"std::shared_ptr",      # 智能指针使用
                r"const\s+",             # const使用
                r"explicit\s+",           # 显式构造函数
            ]
        }
    
    def _get_c_rules(self) -> Dict[str, Any]:
        """C特定检测规则"""
        return {
            "security_patterns": [
                r"strcpy\s*\(",          # 不安全的字符串复制
                r"strcat\s*\(",          # 不安全的字符串连接
                r"sprintf\s*\(",        # 不安全的格式化
                r"gets\s*\(",            # 不安全的输入
                r"scanf\s*\(",           # 格式化字符串风险
                r"system\s*\(",          # 系统命令执行
                r"malloc\s*\(",          # 内存分配
                r"free\s*\(",            # 内存释放
            ],
            "performance_patterns": [
                r"printf\s*\(",          # 格式化输出
                r"#include\s*<stdio\.h>", # 标准输入输出
                r"#include\s*<stdlib\.h>", # 标准库
            ],
            "style_patterns": [
                r"goto\s+",             # goto语句
                r"#define\s+",           # 宏定义
                r"#ifdef\s+",            # 条件编译
                r"int\s+main\s*\(",      # main函数
            ],
            "best_practices": [
                r"void\s*\*",           # 空指针使用
                r"NULL\s*==\s*",         # 空值检查
                r"sizeof\s*\(",          # sizeof使用
            ]
        }
    
    def _get_javascript_rules(self) -> Dict[str, Any]:
        """JavaScript特定检测规则"""
        return {
            "security_patterns": [
                r"eval\s*\(",            # eval函数
                r"innerHTML\s*=",        # innerHTML赋值
                r"document\.write",       # document.write
                r"setTimeout\s*\(",      # setTimeout
                r"setInterval\s*\(",     # setInterval
                r"Function\s*\(",         # Function构造函数
                r"window\.open",         # 窗口打开
                r"location\.href",       # 位置跳转
            ],
            "performance_patterns": [
                r"for\s*\(\s*var\s+",    # var声明
                r"==\s*",                 # 宽松相等
                r"!=\s*",                 # 宽松不等
                r"typeof\s+",             # typeof使用
            ],
            "style_patterns": [
                r"var\s+",               # var声明
                r"function\s+\w*\s*\(",   # 函数声明
                r"console\.log",          # 控制台输出
                r"alert\s*\(",            # 警告框
            ],
            "best_practices": [
                r"===\s*",               # 严格相等
                r"!==\s*",                # 严格不等
                r"let\s+",                # let声明
                r"const\s+",              # const声明
            ]
        }
    
    def _get_go_rules(self) -> Dict[str, Any]:
        """Go特定检测规则"""
        return {
            "security_patterns": [
                r"os\.Getenv",           # 环境变量获取
                r"exec\.Command",        # 命令执行
                r"http\.Get",             # HTTP请求
                r"net\.Dial",             # 网络连接
                r"ioutil\.ReadFile",      # 文件读取
                r"os\.Open",              # 文件打开
            ],
            "performance_patterns": [
                r"make\s*\(\s*map",      # map创建
                r"make\s*\(\s*slice",    # slice创建
                r"append\s*\(",          # slice追加
                r"range\s+",              # range使用
            ],
            "style_patterns": [
                r"func\s+\w*\s*\(",      # 函数声明
                r"type\s+\w*\s+struct",  # 结构体定义
                r"interface\s*{",          # 接口定义
                r"package\s+\w+",         # 包声明
            ],
            "best_practices": [
                r"defer\s+",             # defer使用
                r"go\s+",                # goroutine
                r"chan\s+",              # 通道
                r"sync\.",               # 同步包
            ]
        }
    
    def _get_rust_rules(self) -> Dict[str, Any]:
        """Rust特定检测规则"""
        return {
            "security_patterns": [
                r"unsafe\s*{",           # unsafe块
                r"std::ptr::",            # 原始指针
                r"std::mem::",            # 内存操作
                r"std::process::",        # 进程操作
                r"std::fs::",             # 文件系统
            ],
            "performance_patterns": [
                r"clone\s*\(",            # clone调用
                r"to_string\s*\(",        # 字符串转换
                r"collect\s*\(",          # 集合收集
                r"unwrap\s*\(",           # unwrap调用
            ],
            "style_patterns": [
                r"fn\s+\w*\s*\(",        # 函数声明
                r"struct\s+\w*",          # 结构体定义
                r"enum\s+\w*",            # 枚举定义
                r"impl\s+\w*",            # 实现块
            ],
            "best_practices": [
                r"match\s+",              # match表达式
                r"if\s+let\s+",           # if let
                r"while\s+let\s+",         # while let
                r"Option::",               # Option使用
                r"Result::",               # Result使用
            ]
        }
    
    def detect_language(self, file_path: str) -> Optional[LanguageType]:
        """检测文件语言类型"""
        ext = os.path.splitext(file_path)[1].lower()
        return self.supported_extensions.get(ext)
    
    def is_supported_file(self, file_path: str) -> bool:
        """检查文件是否支持"""
        return self.detect_language(file_path) is not None
    
    async def analyze_file(self, file_path: str, project_path: str) -> Optional[AnalysisResult]:
        """分析单个文件"""
        try:
            language = self.detect_language(file_path)
            if not language:
                return None
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if not content.strip():
                return None
            
            # 执行AI分析
            ai_result = await self._analyze_with_ai(content, file_path, language)
            
            # 执行规则匹配
            rule_issues = self._analyze_with_rules(content, file_path, language)
            
            # 合并结果
            all_issues = ai_result.get('issues', []) + rule_issues
            
            # 计算指标
            metrics = self._calculate_metrics(content, all_issues, language)
            
            # 生成摘要
            summary = await self._generate_summary(content, all_issues, language)
            
            return AnalysisResult(
                language=language.value,
                files_analyzed=1,
                issues_found=len(all_issues),
                issues=all_issues,
                metrics=metrics,
                summary=summary
            )
            
        except Exception as e:
            print(f"分析文件失败 {file_path}: {e}")
            return None
    
    async def _analyze_with_ai(self, content: str, file_path: str, language: LanguageType) -> Dict[str, Any]:
        """使用AI分析代码"""
        try:
            if not self.config.is_configured():
                return {'issues': []}
            
            # 构建分析提示词
            prompt = self._build_analysis_prompt(content, file_path, language)
            
            # 限制文件大小，避免过长的API请求
            if len(content) > 50 * 1024:  # 50KB
                return {'issues': []}
            
            # 调用AI API
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.config.base_url}/chat/completions",
                    headers=self.config.get_headers(),
                    json={
                        "model": self.config.model,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": 1000,
                        "temperature": 0.2
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    ai_content = result["choices"][0]["message"]["content"]
                    
                    # 调试信息
                    print(f"🤖 AI响应长度: {len(ai_content)} 字符")
                    print(f"🤖 AI响应预览: {ai_content[:100]}...")
                    
                    # 解析AI响应
                    return self._parse_ai_response(ai_content, file_path, language)
                else:
                    print(f"AI API调用失败: {response.status_code}")
                    return {'issues': []}
                    
        except Exception as e:
            print(f"AI分析失败: {e}")
            return {'issues': []}
    
    def _build_analysis_prompt(self, content: str, file_path: str, language: LanguageType) -> str:
        """构建AI分析提示词"""
        # 限制内容长度，提高效率
        content_preview = content[:1000] + "..." if len(content) > 1000 else content
        
        prompt = f"""快速分析{language.value.upper()}代码，只检测严重错误：

**文件**: {file_path}
**代码**:
```{language.value}
{content_preview}
```

**任务**: 检测代码问题，根据严重程度判断级别：
1. **error级别**: 严重安全漏洞、会导致崩溃的错误、严重性能问题
2. **warning级别**: 潜在问题、性能警告、代码质量问题
3. **info级别**: 代码风格问题、建议改进

重点关注：
- **安全漏洞**: 缓冲区溢出、SQL注入、XSS攻击、内存泄漏
- **严重性能问题**: 死循环、内存溢出、资源泄露
- **严重逻辑错误**: 空指针异常、数组越界、除零错误
- **严重语法错误**: 编译错误、运行时崩溃

**输出格式** (严格JSON数组):
```json
[
    {{
        "line_number": 行号,
        "severity": "error|warning|info",
        "category": "security|performance|logic|syntax",
        "message": "问题描述",
        "suggestion": "修复建议",
        "confidence": 0.9
    }}
]
```

**严格要求**:
1. 根据问题严重程度准确判断severity级别
2. 必须提供准确的行号
3. 只输出JSON数组，不要包含其他任何内容
4. 如果没有问题，返回空数组: []
5. 不要添加解释文字、markdown格式或其他内容
6. 确保JSON格式正确，可以正常解析"""
        
        return prompt
    
    def _parse_ai_response(self, ai_content: str, file_path: str, language: LanguageType) -> Dict[str, Any]:
        """解析AI响应"""
        try:
            import json
            
            # 尝试多种JSON提取方式
            json_patterns = [
                r'```json\s*(\{.*?\})\s*```',  # 对象格式
                r'```json\s*(\[.*?\])\s*```',  # 数组格式
                r'(\{.*?\})',  # 直接对象
                r'(\[.*?\])',  # 直接数组
            ]
            
            json_content = None
            for pattern in json_patterns:
                match = re.search(pattern, ai_content, re.DOTALL)
                if match:
                    json_content = match.group(1)
                    break
            
            if json_content:
                try:
                    result = json.loads(json_content)
                    
                    # 处理不同的响应格式
                    if isinstance(result, dict):
                        # 对象格式: {"issues": [...], "summary": "..."}
                        issues_data = result.get('issues', [])
                        summary = result.get('summary', '')
                    elif isinstance(result, list):
                        # 数组格式: [{"line_number": 1, "message": "..."}, ...]
                        issues_data = result
                        summary = f"发现 {len(result)} 个问题"
                    else:
                        print(f"⚠️ 未知的AI响应格式: {type(result)}")
                        return {'issues': []}
                    
                    # 转换问题格式，处理所有级别
                    issues = []
                    for issue in issues_data:
                        if isinstance(issue, dict):
                            severity = issue.get('severity', 'info')
                            # 处理所有级别的问题
                            issues.append(CodeIssue(
                                file_path=file_path,
                                line_number=issue.get('line_number', 0),
                                column=issue.get('column', 0),
                                severity=severity,  # 使用原始severity
                                category=issue.get('category', 'logic'),
                                message=issue.get('message', ''),
                                suggestion=issue.get('suggestion', ''),
                                language=language.value,
                                confidence=issue.get('confidence', 0.9)
                            ))
                    
                    return {
                        'issues': issues,
                        'summary': summary
                    }
                    
                except json.JSONDecodeError as e:
                    print(f"⚠️ JSON解析失败: {e}")
                    print(f"原始内容: {json_content[:200]}...")
                    return {'issues': []}
            else:
                # 如果没有JSON格式，尝试直接解析整个响应
                try:
                    result = json.loads(ai_content.strip())
                    if isinstance(result, list):
                        issues_data = result
                        summary = f"发现 {len(result)} 个问题"
                    elif isinstance(result, dict):
                        issues_data = result.get('issues', [])
                        summary = result.get('summary', '')
                    else:
                        return self._parse_text_response(ai_content, file_path, language)
                    
                    # 转换问题格式，处理所有级别
                    issues = []
                    for issue in issues_data:
                        if isinstance(issue, dict):
                            severity = issue.get('severity', 'info')
                            # 处理所有级别的问题
                            issues.append(CodeIssue(
                                file_path=file_path,
                                line_number=issue.get('line_number', 0),
                                column=issue.get('column', 0),
                                severity=severity,  # 使用原始severity
                                category=issue.get('category', 'logic'),
                                message=issue.get('message', ''),
                                suggestion=issue.get('suggestion', ''),
                                language=language.value,
                                confidence=issue.get('confidence', 0.9)
                            ))
                    
                    return {
                        'issues': issues,
                        'summary': summary
                    }
                except json.JSONDecodeError:
                    # 如果直接解析也失败，尝试解析文本
                    return self._parse_text_response(ai_content, file_path, language)
                
        except Exception as e:
            print(f"解析AI响应失败: {e}")
            print(f"AI响应内容: {ai_content[:300]}...")
            return {'issues': []}
    
    def _parse_text_response(self, content: str, file_path: str, language: LanguageType) -> Dict[str, Any]:
        """解析文本格式的AI响应"""
        issues = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 尝试匹配问题描述
            if any(keyword in line.lower() for keyword in ['error', 'warning', 'issue', 'problem', 'bug']):
                issues.append(CodeIssue(
                    file_path=file_path,
                    line_number=0,
                    column=0,
                    severity='info',
                    category='style',
                    message=line,
                    suggestion='请参考代码审查建议',
                    language=language.value,
                    confidence=0.6
                ))
        
        return {
            'issues': issues,
            'summary': content[:200] + "..." if len(content) > 200 else content
        }
    
    def _analyze_with_rules(self, content: str, file_path: str, language: LanguageType) -> List[CodeIssue]:
        """使用规则分析代码"""
        issues = []
        rules = self.language_rules.get(language, {})
        
        if not rules:
            return issues
        
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for category, patterns in rules.items():
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        severity = self._get_severity_by_category(category)
                        message = self._get_message_by_pattern(pattern, category)
                        suggestion = self._get_suggestion_by_pattern(pattern, category)
                        
                        issues.append(CodeIssue(
                            file_path=file_path,
                            line_number=line_num,
                            column=0,
                            severity=severity,
                            category=category,
                            message=message,
                            suggestion=suggestion,
                            language=language.value,
                            confidence=0.9
                        ))
        
        return issues
    
    def _get_severity_by_category(self, category: str) -> str:
        """根据类别获取严重程度"""
        severity_map = {
            'security_patterns': 'error',
            'performance_patterns': 'warning',
            'style_patterns': 'info',
            'best_practices': 'warning'
        }
        return severity_map.get(category, 'info')
    
    def _get_message_by_pattern(self, pattern: str, category: str) -> str:
        """根据模式获取消息"""
        messages = {
            'security_patterns': f'发现潜在安全问题: {pattern}',
            'performance_patterns': f'发现性能问题: {pattern}',
            'style_patterns': f'发现代码风格问题: {pattern}',
            'best_practices': f'发现最佳实践问题: {pattern}'
        }
        return messages.get(category, f'发现代码问题: {pattern}')
    
    def _get_suggestion_by_pattern(self, pattern: str, category: str) -> str:
        """根据模式获取建议"""
        suggestions = {
            'security_patterns': '建议使用更安全的替代方案',
            'performance_patterns': '建议优化性能实现',
            'style_patterns': '建议遵循代码风格规范',
            'best_practices': '建议采用最佳实践'
        }
        return suggestions.get(category, '建议改进代码实现')
    
    def _calculate_metrics(self, content: str, issues: List[CodeIssue], language: LanguageType) -> Dict[str, Any]:
        """计算代码指标"""
        lines = content.split('\n')
        total_lines = len(lines)
        code_lines = len([line for line in lines if line.strip() and not line.strip().startswith('#')])
        
        # 统计问题
        issues_by_severity = {}
        issues_by_category = {}
        
        for issue in issues:
            severity = issue.severity
            category = issue.category
            
            issues_by_severity[severity] = issues_by_severity.get(severity, 0) + 1
            issues_by_category[category] = issues_by_category.get(category, 0) + 1
        
        # 计算复杂度（简单估算）
        complexity = self._calculate_complexity(content, language)
        
        # 计算可维护性评分
        maintainability_score = self._calculate_maintainability_score(issues, total_lines)
        
        return {
            'total_lines': total_lines,
            'code_lines': code_lines,
            'complexity': complexity,
            'maintainability_score': maintainability_score,
            'issues_by_severity': issues_by_severity,
            'issues_by_category': issues_by_category,
            'language': language.value
        }
    
    def _calculate_complexity(self, content: str, language: LanguageType) -> int:
        """计算代码复杂度"""
        complexity_keywords = {
            LanguageType.JAVA: ['if', 'else', 'while', 'for', 'switch', 'case', 'catch', 'try'],
            LanguageType.CPP: ['if', 'else', 'while', 'for', 'switch', 'case', 'catch', 'try'],
            LanguageType.C: ['if', 'else', 'while', 'for', 'switch', 'case'],
            LanguageType.JAVASCRIPT: ['if', 'else', 'while', 'for', 'switch', 'case', 'catch', 'try'],
            LanguageType.GO: ['if', 'else', 'for', 'switch', 'case', 'select'],
            LanguageType.RUST: ['if', 'else', 'while', 'for', 'match', 'loop']
        }
        
        keywords = complexity_keywords.get(language, ['if', 'else', 'while', 'for'])
        complexity = 1  # 基础复杂度
        
        for keyword in keywords:
            complexity += len(re.findall(rf'\b{keyword}\b', content, re.IGNORECASE))
        
        return complexity
    
    def _calculate_maintainability_score(self, issues: List[CodeIssue], total_lines: int) -> float:
        """计算可维护性评分"""
        base_score = 100.0
        
        # 根据问题数量扣分
        for issue in issues:
            if issue.severity == 'error':
                base_score -= 5.0
            elif issue.severity == 'warning':
                base_score -= 2.0
            else:
                base_score -= 0.5
        
        # 根据代码行数调整
        if total_lines > 1000:
            base_score -= (total_lines - 1000) * 0.01
        
        return max(0.0, min(100.0, base_score))
    
    async def _generate_summary(self, content: str, issues: List[CodeIssue], language: LanguageType) -> str:
        """生成分析摘要"""
        total_issues = len(issues)
        error_count = len([i for i in issues if i.severity == 'error'])
        warning_count = len([i for i in issues if i.severity == 'warning'])
        info_count = len([i for i in issues if i.severity == 'info'])
        
        summary = f"{language.value.upper()}代码分析完成。"
        summary += f"共发现{total_issues}个问题："
        summary += f"严重问题{error_count}个，"
        summary += f"警告问题{warning_count}个，"
        summary += f"信息问题{info_count}个。"
        
        if error_count > 0:
            summary += "建议优先修复严重问题。"
        elif warning_count > 0:
            summary += "建议及时处理警告问题。"
        else:
            summary += "代码质量良好。"
        
        return summary
    
    async def analyze_project(self, project_path: str) -> Dict[str, Any]:
        """分析整个项目"""
        results = {}
        total_files = 0
        total_issues = 0
        all_issues = []
        
        # 遍历项目文件
        for root, dirs, files in os.walk(project_path):
            # 跳过不需要的目录
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules', '.venv', 'venv'}]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                if self.is_supported_file(file_path):
                    total_files += 1
                    result = await self.analyze_file(file_path, project_path)
                    
                    if result:
                        language = result.language
                        if language not in results:
                            results[language] = {
                                'files_analyzed': 0,
                                'issues_found': 0,
                                'issues': [],
                                'metrics': {},
                                'summary': ''
                            }
                        
                        results[language]['files_analyzed'] += result.files_analyzed
                        results[language]['issues_found'] += result.issues_found
                        results[language]['issues'].extend(result.issues)
                        results[language]['metrics'].update(result.metrics)
                        
                        total_issues += result.issues_found
                        all_issues.extend(result.issues)
        
        # 生成总体摘要
        overall_summary = f"多语言项目分析完成。共分析{total_files}个文件，发现{total_issues}个问题。"
        
        return {
            'total_files': total_files,
            'total_issues': total_issues,
            'results_by_language': results,
            'all_issues': all_issues,
            'overall_summary': overall_summary
        }
