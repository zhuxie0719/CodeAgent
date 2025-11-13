"""
通用Bug检测模块
检测各种类型的通用bug，包括：
1. 用户输入与外部数据交互点
2. 资源管理与状态依赖
3. 并发与异步操作
4. 边界条件与异常处理
5. 环境依赖与配置
6. 动态代码执行
"""

import os
import re
import ast
import json
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path


class GenericBugDetector:
    """通用Bug检测器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.detected_issues = []
    
    def detect_all_issues(self, project_path: str) -> Dict[str, Any]:
        """检测所有类型的bug"""
        self.detected_issues = []
        
        try:
            # 获取所有Python文件
            python_files = list(Path(project_path).rglob("*.py"))
            
            # 跳过虚拟环境、缓存目录及常见第三方依赖目录
            skip_dirs = {
                'venv', '__pycache__', '.git', 'node_modules',
                '.pytest_cache', '.mypy_cache', 'env', '.env',
                'site-packages', 'dist-packages', '.eggs'
            }
            skip_keywords = {
                'tests' + os.sep, os.sep + 'tests',
                'examples' + os.sep, os.sep + 'examples',
                'sample' + os.sep, os.sep + 'sample',
                'demo' + os.sep, os.sep + 'demo',
                'flask-', 'django-', 'werkzeug', 'sqlalchemy'
            }
            python_files = [
                f for f in python_files
                if not any(skip_dir in str(f) for skip_dir in skip_dirs)
                and not any(keyword in str(f).lower() for keyword in skip_keywords)
            ]
            
            # 限制扫描文件数量，避免对大量依赖库造成噪声
            max_files = 200
            if len(python_files) > max_files:
                self.logger.info(f"文件数量 {len(python_files)} 超过上限 {max_files}，仅分析前 {max_files} 个文件")
                python_files = python_files[:max_files]
            
            self.logger.info(f"开始检测 {len(python_files)} 个Python文件")
            
            # 1. 用户输入与外部数据交互点
            input_issues = self._detect_input_interaction_issues(python_files)
            self.detected_issues.extend(input_issues)
            
            # 2. 资源管理与状态依赖
            resource_issues = self._detect_resource_management_issues(python_files)
            self.detected_issues.extend(resource_issues)
            
            # 3. 并发与异步操作
            concurrency_issues = self._detect_concurrency_issues(python_files)
            self.detected_issues.extend(concurrency_issues)
            
            # 4. 边界条件与异常处理
            boundary_issues = self._detect_boundary_condition_issues(python_files)
            self.detected_issues.extend(boundary_issues)
            
            # 5. 环境依赖与配置
            env_issues = self._detect_environment_dependency_issues(python_files)
            self.detected_issues.extend(env_issues)
            
            # 6. 动态代码执行
            dynamic_code_issues = self._detect_dynamic_code_execution_issues(python_files)
            self.detected_issues.extend(dynamic_code_issues)
            
            return {
                "status": "completed",
                "total_issues": len(self.detected_issues),
                "issues_by_category": self._categorize_issues(),
                "issues": self.detected_issues,
                "files_scanned": len(python_files)
            }
            
        except Exception as e:
            self.logger.error(f"通用bug检测失败: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "issues": []
            }
    
    def _detect_input_interaction_issues(self, python_files: List[Path]) -> List[Dict[str, Any]]:
        """检测用户输入与外部数据交互点问题"""
        issues = []
        
        # 检测模式
        patterns = {
            "unsafe_request_params": [
                r"request\.(args|form|json|data|values)\[",
                r"request\.(args|form|json|data|values)\.get\(",
                r"flask\.request\.(args|form|json|data|values)",
            ],
            "unsafe_headers": [
                r"request\.headers\[",
                r"request\.headers\.get\(",
                r"request\.headers\[['\"]",
            ],
            "unsafe_cookies": [
                r"request\.cookies\[",
                r"request\.cookies\.get\(",
                r"cookies\[",
            ],
            "unsafe_file_upload": [
                r"request\.files\[",
                r"request\.files\.get\(",
                r"\.save\(",
                r"open\(.*request",
            ],
            "unsafe_file_read": [
                r"open\(.*request",
                r"open\(.*input",
                r"open\(.*user",
            ],
            "unsafe_api_response": [
                r"requests\.(get|post|put|delete)\(.*\)\.(text|content|json)",
                r"urllib\.request\.urlopen\(.*\)\.read",
                r"httpx\.(get|post)\(.*\)\.(text|content|json)",
            ],
            "unsafe_third_party_data": [
                r"\.json\(\)",
                r"\.text",
                r"\.content",
            ],
        }
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                for category, pattern_list in patterns.items():
                    for pattern in pattern_list:
                        for line_num, line in enumerate(lines, 1):
                            if re.search(pattern, line, re.IGNORECASE):
                                # 检查是否有验证或清理
                                if not self._has_validation_or_sanitization(line, lines, line_num):
                                    issues.append({
                                        "type": "input_interaction",
                                        "category": category,
                                        "severity": self._get_severity(category),
                                        "file": str(file_path),
                                        "line": line_num,
                                        "code": line.strip(),
                                        "description": self._get_input_issue_description(category),
                                        "recommendation": self._get_input_recommendation(category)
                                    })
            except Exception as e:
                self.logger.warning(f"检测文件 {file_path} 失败: {e}")
        
        return issues
    
    def _detect_resource_management_issues(self, python_files: List[Path]) -> List[Dict[str, Any]]:
        """检测资源管理与状态依赖问题"""
        issues = []
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                # 检测文件操作
                file_issues = self._detect_file_resource_issues(file_path, lines)
                issues.extend(file_issues)
                
                # 检测数据库连接
                db_issues = self._detect_database_connection_issues(file_path, lines)
                issues.extend(db_issues)
                
                # 检测网络套接字
                socket_issues = self._detect_socket_resource_issues(file_path, lines)
                issues.extend(socket_issues)
                
                # 检测锁资源
                lock_issues = self._detect_lock_resource_issues(file_path, lines)
                issues.extend(lock_issues)
                
            except Exception as e:
                self.logger.warning(f"检测文件 {file_path} 失败: {e}")
        
        return issues
    
    def _detect_file_resource_issues(self, file_path: Path, lines: List[str]) -> List[Dict[str, Any]]:
        """检测文件资源问题"""
        issues = []
        open_calls = []
        
        for line_num, line in enumerate(lines, 1):
            # 查找open()调用
            if re.search(r'\bopen\s*\(', line):
                open_calls.append((line_num, line))
                # 检查是否有对应的close()
                if not self._has_matching_close(lines, line_num, 'file'):
                    issues.append({
                        "type": "resource_management",
                        "category": "file_not_closed",
                        "severity": "high",
                        "file": str(file_path),
                        "line": line_num,
                        "code": line.strip(),
                        "description": "文件打开后可能未正确关闭",
                        "recommendation": "使用with语句或确保在finally块中关闭文件"
                    })
        
        return issues
    
    def _detect_database_connection_issues(self, file_path: Path, lines: List[str]) -> List[Dict[str, Any]]:
        """检测数据库连接问题"""
        issues = []
        connection_patterns = [
            r'sqlite3\.connect\(',
            r'psycopg2\.connect\(',
            r'mysql\.connector\.connect\(',
            r'pymongo\.MongoClient\(',
            r'sqlalchemy\.create_engine\(',
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern in connection_patterns:
                if re.search(pattern, line):
                    # 检查是否有连接池或上下文管理
                    if not self._has_connection_management(line, lines, line_num):
                        issues.append({
                            "type": "resource_management",
                            "category": "database_connection",
                            "severity": "high",
                            "file": str(file_path),
                            "line": line_num,
                            "code": line.strip(),
                            "description": "数据库连接可能未正确管理",
                            "recommendation": "使用连接池或确保连接在使用后正确关闭"
                        })
        
        return issues
    
    def _detect_socket_resource_issues(self, file_path: Path, lines: List[str]) -> List[Dict[str, Any]]:
        """检测网络套接字资源问题"""
        issues = []
        socket_patterns = [
            r'socket\.socket\(',
            r'socket\.create_connection\(',
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern in socket_patterns:
                if re.search(pattern, line):
                    if not self._has_socket_management(line, lines, line_num):
                        issues.append({
                            "type": "resource_management",
                            "category": "socket_not_closed",
                            "severity": "medium",
                            "file": str(file_path),
                            "line": line_num,
                            "code": line.strip(),
                            "description": "套接字可能未正确关闭",
                            "recommendation": "使用with语句或确保在finally块中关闭套接字"
                        })
        
        return issues
    
    def _detect_lock_resource_issues(self, file_path: Path, lines: List[str]) -> List[Dict[str, Any]]:
        """检测锁资源问题"""
        issues = []
        lock_patterns = [
            r'threading\.Lock\(',
            r'threading\.RLock\(',
            r'multiprocessing\.Lock\(',
            r'\.acquire\(',
        ]
        
        lock_acquired = False
        for line_num, line in enumerate(lines, 1):
            for pattern in lock_patterns:
                if re.search(r'\.acquire\(', line):
                    lock_acquired = True
                    # 检查后续是否有release
                    if not self._has_matching_release(lines, line_num):
                        issues.append({
                            "type": "resource_management",
                            "category": "lock_not_released",
                            "severity": "high",
                            "file": str(file_path),
                            "line": line_num,
                            "code": line.strip(),
                            "description": "锁获取后可能未正确释放",
                            "recommendation": "使用with语句或确保在finally块中释放锁"
                        })
        
        return issues
    
    def _detect_concurrency_issues(self, python_files: List[Path]) -> List[Dict[str, Any]]:
        """检测并发与异步操作问题"""
        issues = []
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                # 检测多线程问题
                threading_issues = self._detect_threading_issues(file_path, lines)
                issues.extend(threading_issues)
                
                # 检测多进程问题
                multiprocessing_issues = self._detect_multiprocessing_issues(file_path, lines)
                issues.extend(multiprocessing_issues)
                
                # 检测异步操作问题
                async_issues = self._detect_async_issues(file_path, lines)
                issues.extend(async_issues)
                
            except Exception as e:
                self.logger.warning(f"检测文件 {file_path} 失败: {e}")
        
        return issues
    
    def _detect_threading_issues(self, file_path: Path, lines: List[str]) -> List[Dict[str, Any]]:
        """检测多线程问题"""
        issues = []
        
        for line_num, line in enumerate(lines, 1):
            # 检测共享变量访问
            if re.search(r'threading\.Thread\(', line):
                # 检查是否有锁保护
                if not self._has_lock_protection(lines, line_num):
                    issues.append({
                        "type": "concurrency",
                        "category": "threading_race_condition",
                        "severity": "high",
                        "file": str(file_path),
                        "line": line_num,
                        "code": line.strip(),
                        "description": "多线程访问共享资源可能产生竞态条件",
                        "recommendation": "使用锁或其他同步机制保护共享资源"
                    })
        
        return issues
    
    def _detect_multiprocessing_issues(self, file_path: Path, lines: List[str]) -> List[Dict[str, Any]]:
        """检测多进程问题"""
        issues = []
        
        for line_num, line in enumerate(lines, 1):
            if re.search(r'multiprocessing\.(Process|Pool)\(', line):
                issues.append({
                    "type": "concurrency",
                    "category": "multiprocessing",
                    "severity": "medium",
                    "file": str(file_path),
                    "line": line_num,
                    "code": line.strip(),
                    "description": "多进程操作需要确保进程间通信和资源管理",
                    "recommendation": "确保进程间数据同步和资源正确释放"
                })
        
        return issues
    
    def _detect_async_issues(self, file_path: Path, lines: List[str]) -> List[Dict[str, Any]]:
        """检测异步操作问题"""
        issues = []
        
        async_functions = []
        for line_num, line in enumerate(lines, 1):
            if re.search(r'async\s+def\s+', line):
                async_functions.append((line_num, line))
        
        for line_num, line in enumerate(lines, 1):
            # 检测await缺失
            if re.search(r'async\s+def\s+', line):
                # 检查函数体内是否有await
                func_body = self._get_function_body(lines, line_num)
                if func_body and not re.search(r'\bawait\s+', func_body):
                    issues.append({
                        "type": "concurrency",
                        "category": "async_missing_await",
                        "severity": "medium",
                        "file": str(file_path),
                        "line": line_num,
                        "code": line.strip(),
                        "description": "异步函数中可能缺少await关键字",
                        "recommendation": "确保异步操作使用await关键字"
                    })
        
        return issues
    
    def _detect_boundary_condition_issues(self, python_files: List[Path]) -> List[Dict[str, Any]]:
        """检测边界条件与异常处理问题"""
        issues = []
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                # 检测循环边界
                loop_issues = self._detect_loop_boundary_issues(file_path, lines)
                issues.extend(loop_issues)
                
                # 检测数值计算
                numeric_issues = self._detect_numeric_calculation_issues(file_path, lines)
                issues.extend(numeric_issues)
                
                # 检测递归调用
                recursion_issues = self._detect_recursion_issues(file_path, lines)
                issues.extend(recursion_issues)
                
                # 检测异常处理
                exception_issues = self._detect_exception_handling_issues(file_path, lines)
                issues.extend(exception_issues)
                
            except Exception as e:
                self.logger.warning(f"检测文件 {file_path} 失败: {e}")
        
        return issues
    
    def _detect_loop_boundary_issues(self, file_path: Path, lines: List[str]) -> List[Dict[str, Any]]:
        """检测循环边界问题"""
        issues = []
        
        for line_num, line in enumerate(lines, 1):
            # 检测可能的越界访问
            if re.search(r'for\s+\w+\s+in\s+range\(', line):
                # 检查是否有边界检查
                if not self._has_boundary_check(lines, line_num):
                    issues.append({
                        "type": "boundary_condition",
                        "category": "loop_boundary",
                        "severity": "medium",
                        "file": str(file_path),
                        "line": line_num,
                        "code": line.strip(),
                        "description": "循环可能访问越界",
                        "recommendation": "确保循环边界检查正确"
                    })
        
        return issues
    
    def _detect_numeric_calculation_issues(self, file_path: Path, lines: List[str]) -> List[Dict[str, Any]]:
        """检测数值计算问题"""
        issues = []
        
        for line_num, line in enumerate(lines, 1):
            # 检测除零
            if re.search(r'/\s*0\b|/\s*\w+\s*$', line):
                issues.append({
                    "type": "boundary_condition",
                    "category": "division_by_zero",
                    "severity": "high",
                    "file": str(file_path),
                    "line": line_num,
                    "code": line.strip(),
                    "description": "可能存在除零错误",
                    "recommendation": "添加除零检查"
                })
            
            # 检测整数溢出
            if re.search(r'\*\s*\d{6,}', line):
                issues.append({
                    "type": "boundary_condition",
                    "category": "integer_overflow",
                    "severity": "medium",
                    "file": str(file_path),
                    "line": line_num,
                    "code": line.strip(),
                    "description": "可能存在整数溢出",
                    "recommendation": "检查数值范围"
                })
        
        return issues
    
    def _detect_recursion_issues(self, file_path: Path, lines: List[str]) -> List[Dict[str, Any]]:
        """检测递归调用问题"""
        issues = []
        
        recursion_functions = []
        for line_num, line in enumerate(lines, 1):
            if re.search(r'def\s+\w+.*\(.*\):', line):
                func_name = re.search(r'def\s+(\w+)', line)
                if func_name:
                    recursion_functions.append((line_num, func_name.group(1)))
        
        for line_num, line in enumerate(lines, 1):
            for func_line, func_name in recursion_functions:
                if re.search(rf'\b{func_name}\s*\(', line) and line_num != func_line:
                    # 检查是否有递归终止条件
                    if not self._has_recursion_base_case(lines, func_line):
                        issues.append({
                            "type": "boundary_condition",
                            "category": "recursion_no_base_case",
                            "severity": "high",
                            "file": str(file_path),
                            "line": func_line,
                            "code": lines[func_line - 1].strip(),
                            "description": "递归函数可能缺少终止条件",
                            "recommendation": "确保递归函数有明确的终止条件"
                        })
        
        return issues
    
    def _detect_exception_handling_issues(self, file_path: Path, lines: List[str]) -> List[Dict[str, Any]]:
        """检测异常处理问题"""
        issues = []
        
        for line_num, line in enumerate(lines, 1):
            # 检测过于宽泛的异常捕获
            if re.search(r'except\s*:', line) or re.search(r'except\s+Exception\s*:', line):
                issues.append({
                    "type": "boundary_condition",
                    "category": "broad_exception",
                    "severity": "medium",
                    "file": str(file_path),
                    "line": line_num,
                    "code": line.strip(),
                    "description": "异常捕获过于宽泛，可能隐藏错误",
                    "recommendation": "捕获具体的异常类型"
                })
            
            # 检测空的except块
            if re.search(r'except.*:\s*$', line) or (re.search(r'except', line) and 
                line_num < len(lines) and lines[line_num].strip() in ['pass', '...']):
                issues.append({
                    "type": "boundary_condition",
                    "category": "empty_except",
                    "severity": "medium",
                    "file": str(file_path),
                    "line": line_num,
                    "code": line.strip(),
                    "description": "空的异常处理块可能隐藏错误",
                    "recommendation": "至少记录异常信息"
                })
        
        return issues
    
    def _detect_environment_dependency_issues(self, python_files: List[Path]) -> List[Dict[str, Any]]:
        """检测环境依赖与配置问题"""
        issues = []
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    # 检测环境变量访问
                    if re.search(r'os\.environ\[', line) or re.search(r'os\.getenv\(', line):
                        if not self._has_default_value(line):
                            issues.append({
                                "type": "environment_dependency",
                                "category": "missing_env_default",
                                "severity": "medium",
                                "file": str(file_path),
                                "line": line_num,
                                "code": line.strip(),
                                "description": "环境变量可能未设置，缺少默认值",
                                "recommendation": "为环境变量提供默认值"
                            })
                    
                    # 检测配置文件读取
                    if re.search(r'config\[|config\.get\(|\.ini|\.yaml|\.yml|\.json', line):
                        if not self._has_config_validation(line, lines, line_num):
                            issues.append({
                                "type": "environment_dependency",
                                "category": "config_validation",
                                "severity": "low",
                                "file": str(file_path),
                                "line": line_num,
                                "code": line.strip(),
                                "description": "配置文件读取可能缺少验证",
                                "recommendation": "验证配置文件的完整性和有效性"
                            })
                    
                    # 检测时区处理
                    if re.search(r'datetime\.(now|utcnow)\(', line):
                        issues.append({
                            "type": "environment_dependency",
                            "category": "timezone_handling",
                            "severity": "low",
                            "file": str(file_path),
                            "line": line_num,
                            "code": line.strip(),
                            "description": "时间处理可能未考虑时区",
                            "recommendation": "明确指定时区或使用timezone-aware datetime"
                        })
            
            except Exception as e:
                self.logger.warning(f"检测文件 {file_path} 失败: {e}")
        
        return issues
    
    def _detect_dynamic_code_execution_issues(self, python_files: List[Path]) -> List[Dict[str, Any]]:
        """检测动态代码执行问题"""
        issues = []
        
        dangerous_patterns = {
            "eval": r'\beval\s*\(',
            "exec": r'\bexec\s*\(',
            "compile": r'\bcompile\s*\(',
            "pickle": r'pickle\.(load|loads)\(',
            "yaml_load": r'yaml\.(load|safe_load)\(',
            "json_loads": r'json\.loads\(',
            "xml_parse": r'xml\.(etree\.ElementTree\.parse|sax\.parse)',
            "reflection": r'getattr\(|setattr\(|__getattribute__',
        }
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    for category, pattern in dangerous_patterns.items():
                        if re.search(pattern, line, re.IGNORECASE):
                            # 检查是否有输入验证
                            if not self._has_input_validation(line, lines, line_num):
                                issues.append({
                                    "type": "dynamic_code_execution",
                                    "category": category,
                                    "severity": self._get_dynamic_code_severity(category),
                                    "file": str(file_path),
                                    "line": line_num,
                                    "code": line.strip(),
                                    "description": self._get_dynamic_code_description(category),
                                    "recommendation": self._get_dynamic_code_recommendation(category)
                                })
            
            except Exception as e:
                self.logger.warning(f"检测文件 {file_path} 失败: {e}")
        
        return issues
    
    # 辅助方法
    def _has_validation_or_sanitization(self, line: str, lines: List[str], line_num: int) -> bool:
        """检查是否有验证或清理"""
        validation_keywords = ['validate', 'sanitize', 'escape', 'clean', 'check', 'verify']
        # 检查前后几行
        context_lines = lines[max(0, line_num-3):min(len(lines), line_num+3)]
        context = ' '.join(context_lines)
        return any(keyword in context.lower() for keyword in validation_keywords)
    
    def _has_matching_close(self, lines: List[str], open_line: int, resource_type: str) -> bool:
        """检查是否有匹配的关闭操作"""
        # 简化检查：查找with语句
        for i in range(max(0, open_line-5), min(len(lines), open_line+20)):
            if 'with ' in lines[i] and 'open(' in lines[i]:
                return True
        return False
    
    def _has_connection_management(self, line: str, lines: List[str], line_num: int) -> bool:
        """检查是否有连接管理"""
        context = ' '.join(lines[max(0, line_num-5):min(len(lines), line_num+10)])
        return 'with ' in context or 'pool' in context.lower() or 'close()' in context
    
    def _has_socket_management(self, line: str, lines: List[str], line_num: int) -> bool:
        """检查是否有套接字管理"""
        context = ' '.join(lines[max(0, line_num-5):min(len(lines), line_num+10)])
        return 'with ' in context or 'close()' in context
    
    def _has_matching_release(self, lines: List[str], acquire_line: int) -> bool:
        """检查是否有匹配的释放操作"""
        for i in range(acquire_line, min(len(lines), acquire_line+50)):
            if '.release()' in lines[i]:
                return True
        return False
    
    def _has_lock_protection(self, lines: List[str], line_num: int) -> bool:
        """检查是否有锁保护"""
        context = ' '.join(lines[max(0, line_num-10):min(len(lines), line_num+10)])
        return 'Lock' in context or 'RLock' in context or 'with ' in context
    
    def _get_function_body(self, lines: List[str], func_line: int) -> str:
        """获取函数体"""
        body_lines = []
        indent = len(lines[func_line]) - len(lines[func_line].lstrip())
        for i in range(func_line + 1, min(len(lines), func_line + 50)):
            if lines[i].strip() and len(lines[i]) - len(lines[i].lstrip()) > indent:
                body_lines.append(lines[i])
            else:
                break
        return ' '.join(body_lines)
    
    def _has_boundary_check(self, lines: List[str], line_num: int) -> bool:
        """检查是否有边界检查"""
        context = ' '.join(lines[max(0, line_num-3):min(len(lines), line_num+10)])
        return 'len(' in context or 'if ' in context or 'range(' in context
    
    def _has_recursion_base_case(self, lines: List[str], func_line: int) -> bool:
        """检查递归函数是否有终止条件"""
        func_body = self._get_function_body(lines, func_line)
        return 'if ' in func_body and ('return' in func_body or 'break' in func_body)
    
    def _has_default_value(self, line: str) -> bool:
        """检查是否有默认值"""
        return 'default' in line.lower() or 'or ' in line or 'if ' in line
    
    def _has_config_validation(self, line: str, lines: List[str], line_num: int) -> bool:
        """检查是否有配置验证"""
        context = ' '.join(lines[max(0, line_num-5):min(len(lines), line_num+5)])
        return 'validate' in context.lower() or 'check' in context.lower()
    
    def _has_input_validation(self, line: str, lines: List[str], line_num: int) -> bool:
        """检查是否有输入验证"""
        context = ' '.join(lines[max(0, line_num-5):min(len(lines), line_num+5)])
        validation_keywords = ['validate', 'check', 'verify', 'sanitize', 'whitelist']
        return any(keyword in context.lower() for keyword in validation_keywords)
    
    def _get_severity(self, category: str) -> str:
        """获取严重程度"""
        severity_map = {
            "unsafe_request_params": "high",
            "unsafe_file_upload": "high",
            "unsafe_file_read": "high",
            "unsafe_api_response": "medium",
            "unsafe_headers": "medium",
            "unsafe_cookies": "medium",
            "unsafe_third_party_data": "medium",
        }
        return severity_map.get(category, "medium")
    
    def _get_input_issue_description(self, category: str) -> str:
        """获取输入问题描述"""
        descriptions = {
            "unsafe_request_params": "HTTP请求参数未经验证直接使用",
            "unsafe_headers": "HTTP头部未经验证直接使用",
            "unsafe_cookies": "Cookie未经验证直接使用",
            "unsafe_file_upload": "文件上传未经验证",
            "unsafe_file_read": "文件读取使用用户输入，可能存在路径遍历风险",
            "unsafe_api_response": "API响应未经验证直接使用",
            "unsafe_third_party_data": "第三方服务返回数据未经验证",
        }
        return descriptions.get(category, "用户输入未经验证")
    
    def _get_input_recommendation(self, category: str) -> str:
        """获取输入问题建议"""
        recommendations = {
            "unsafe_request_params": "验证和清理所有用户输入，使用白名单验证",
            "unsafe_headers": "验证HTTP头部，防止头部注入攻击",
            "unsafe_cookies": "验证Cookie值，防止Cookie篡改",
            "unsafe_file_upload": "验证文件类型、大小和内容",
            "unsafe_file_read": "验证文件路径，防止路径遍历攻击",
            "unsafe_api_response": "验证API响应格式和内容",
            "unsafe_third_party_data": "验证第三方数据格式和内容",
        }
        return recommendations.get(category, "添加输入验证和清理机制")
    
    def _get_dynamic_code_severity(self, category: str) -> str:
        """获取动态代码执行严重程度"""
        severity_map = {
            "eval": "critical",
            "exec": "critical",
            "compile": "high",
            "pickle": "high",
            "yaml_load": "high",
            "json_loads": "medium",
            "xml_parse": "medium",
            "reflection": "low",
        }
        return severity_map.get(category, "medium")
    
    def _get_dynamic_code_description(self, category: str) -> str:
        """获取动态代码执行描述"""
        descriptions = {
            "eval": "使用eval()执行用户输入可能导致代码注入",
            "exec": "使用exec()执行用户输入可能导致代码注入",
            "compile": "动态编译代码可能存在安全风险",
            "pickle": "pickle反序列化可能执行恶意代码",
            "yaml_load": "YAML加载可能执行任意代码",
            "json_loads": "JSON反序列化需要验证输入",
            "xml_parse": "XML解析可能受到XXE攻击",
            "reflection": "反射操作需要验证输入",
        }
        return descriptions.get(category, "动态代码执行存在安全风险")
    
    def _get_dynamic_code_recommendation(self, category: str) -> str:
        """获取动态代码执行建议"""
        recommendations = {
            "eval": "避免使用eval()，使用安全的替代方案",
            "exec": "避免使用exec()，使用安全的替代方案",
            "compile": "验证编译的代码来源",
            "pickle": "使用pickle.loads()时验证数据来源，或使用更安全的序列化格式",
            "yaml_load": "使用yaml.safe_load()替代yaml.load()",
            "json_loads": "验证JSON输入格式和内容",
            "xml_parse": "禁用外部实体解析，使用安全的XML解析器",
            "reflection": "验证反射操作的输入参数",
        }
        return recommendations.get(category, "添加输入验证和安全检查")
    
    def _categorize_issues(self) -> Dict[str, int]:
        """按类别统计问题"""
        categories = {}
        for issue in self.detected_issues:
            issue_type = issue.get("type", "unknown")
            if issue_type not in categories:
                categories[issue_type] = 0
            categories[issue_type] += 1
        return categories


