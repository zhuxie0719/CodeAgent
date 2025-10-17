#!/usr/bin/env python3
"""
Flask简单静态测试
基于Flask 2.0.0的已知问题进行检测
"""

import os
import sys
import json
import ast
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
import importlib.util

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class StaticTestRunner:
    """静态测试运行器"""
    
    def __init__(self):
        self.results = {
            "flask_issues": [],
            "code_quality": [],
            "security_issues": [],
            "performance_issues": []
        }
        
        # Flask 2.0.0 已知问题列表
        self.flask_issues = [
            {
                "id": "FLASK-001",
                "title": "url_for() 在某些情况下返回错误的URL",
                "description": "url_for()函数在处理复杂路由时可能返回错误的URL",
                "pattern": r"url_for\s*\(",
                "severity": "high"
            },
            {
                "id": "FLASK-002", 
                "title": "模板渲染性能问题",
                "description": "大型模板渲染时性能较差",
                "pattern": r"render_template\s*\(",
                "severity": "medium"
            },
            {
                "id": "FLASK-003",
                "title": "JSON响应编码问题",
                "description": "某些Unicode字符在JSON响应中编码不正确",
                "pattern": r"jsonify\s*\(",
                "severity": "medium"
            },
            {
                "id": "FLASK-004",
                "title": "会话管理安全问题",
                "description": "会话cookie在某些情况下不够安全",
                "pattern": r"session\s*\[",
                "severity": "high"
            },
            {
                "id": "FLASK-005",
                "title": "请求上下文问题",
                "description": "在某些异步操作中请求上下文可能丢失",
                "pattern": r"request\.",
                "severity": "high"
            }
        ]
    
    def run_analysis(self, target_path: str) -> Dict[str, Any]:
        """运行静态分析"""
        print(f"🎯 分析目标: {target_path}")
        
        target_path = Path(target_path)
        
        if target_path.is_file():
            self._analyze_file(target_path)
        elif target_path.is_dir():
            self._analyze_directory(target_path)
        else:
            raise ValueError(f"无效的目标路径: {target_path}")
        
        # 生成总结
        summary = self._generate_summary()
        
        return {
            "summary": summary,
            "details": self.results,
            "timestamp": self._get_timestamp()
        }
    
    def _analyze_file(self, file_path: Path):
        """分析单个文件"""
        if file_path.suffix != '.py':
            return
        
        print(f"📄 分析文件: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析AST
            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                self.results["code_quality"].append({
                    "file": str(file_path),
                    "issue": "语法错误",
                    "description": f"Python语法错误: {e}",
                    "line": e.lineno,
                    "severity": "high"
                })
                return
            
            # 检查Flask相关问题
            self._check_flask_issues(content, file_path)
            
            # 检查代码质量
            self._check_code_quality(tree, file_path)
            
            # 检查安全问题
            self._check_security_issues(content, file_path)
            
            # 检查性能问题
            self._check_performance_issues(content, file_path)
            
        except Exception as e:
            self.results["code_quality"].append({
                "file": str(file_path),
                "issue": "文件读取错误",
                "description": f"无法读取文件: {e}",
                "severity": "medium"
            })
    
    def _analyze_directory(self, dir_path: Path):
        """分析目录中的所有Python文件"""
        print(f"📁 分析目录: {dir_path}")
        
        python_files = list(dir_path.rglob("*.py"))
        
        for file_path in python_files:
            # 跳过__pycache__目录
            if "__pycache__" in str(file_path):
                continue
            
            self._analyze_file(file_path)
    
    def _check_flask_issues(self, content: str, file_path: Path):
        """检查Flask相关问题"""
        lines = content.split('\n')
        
        for issue in self.flask_issues:
            pattern = issue["pattern"]
            matches = re.finditer(pattern, content, re.IGNORECASE)
            
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                line_content = lines[line_num - 1].strip()
                
                self.results["flask_issues"].append({
                    "file": str(file_path),
                    "issue_id": issue["id"],
                    "title": issue["title"],
                    "description": issue["description"],
                    "line": line_num,
                    "line_content": line_content,
                    "severity": issue["severity"]
                })
    
    def _check_code_quality(self, tree: ast.AST, file_path: Path):
        """检查代码质量问题"""
        issues = []
        
        for node in ast.walk(tree):
            # 检查过长的函数
            if isinstance(node, ast.FunctionDef):
                if len(node.body) > 50:
                    issues.append({
                        "file": str(file_path),
                        "issue": "函数过长",
                        "description": f"函数 '{node.name}' 有 {len(node.body)} 行，建议拆分",
                        "line": node.lineno,
                        "severity": "medium"
                    })
            
            # 检查复杂的条件语句
            elif isinstance(node, ast.If):
                if self._count_conditions(node.test) > 3:
                    issues.append({
                        "file": str(file_path),
                        "issue": "条件语句过于复杂",
                        "description": f"第 {node.lineno} 行的条件语句过于复杂",
                        "line": node.lineno,
                        "severity": "low"
                    })
            
            # 检查未使用的导入
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if not self._is_import_used(tree, alias.name):
                        issues.append({
                            "file": str(file_path),
                            "issue": "未使用的导入",
                            "description": f"导入的模块 '{alias.name}' 未被使用",
                            "line": node.lineno,
                            "severity": "low"
                        })
        
        self.results["code_quality"].extend(issues)
    
    def _check_security_issues(self, content: str, file_path: Path):
        """检查安全问题"""
        security_patterns = [
            {
                "pattern": r"eval\s*\(",
                "issue": "使用eval()函数",
                "description": "eval()函数存在安全风险，建议避免使用",
                "severity": "high"
            },
            {
                "pattern": r"exec\s*\(",
                "issue": "使用exec()函数", 
                "description": "exec()函数存在安全风险，建议避免使用",
                "severity": "high"
            },
            {
                "pattern": r"os\.system\s*\(",
                "issue": "使用os.system()",
                "description": "os.system()存在命令注入风险",
                "severity": "high"
            },
            {
                "pattern": r"subprocess\.call\s*\(",
                "issue": "使用subprocess.call()",
                "description": "subprocess.call()可能存在安全风险，建议使用subprocess.run()",
                "severity": "medium"
            }
        ]
        
        lines = content.split('\n')
        
        for pattern_info in security_patterns:
            pattern = pattern_info["pattern"]
            matches = re.finditer(pattern, content, re.IGNORECASE)
            
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                line_content = lines[line_num - 1].strip()
                
                self.results["security_issues"].append({
                    "file": str(file_path),
                    "issue": pattern_info["issue"],
                    "description": pattern_info["description"],
                    "line": line_num,
                    "line_content": line_content,
                    "severity": pattern_info["severity"]
                })
    
    def _check_performance_issues(self, content: str, file_path: Path):
        """检查性能问题"""
        performance_patterns = [
            {
                "pattern": r"for\s+\w+\s+in\s+range\s*\(\s*len\s*\(",
                "issue": "低效的循环",
                "description": "使用range(len())遍历列表效率较低，建议使用enumerate()",
                "severity": "low"
            },
            {
                "pattern": r"\.append\s*\(\s*\[\s*\]\s*\)",
                "issue": "频繁的列表操作",
                "description": "频繁的列表append操作可能影响性能",
                "severity": "low"
            },
            {
                "pattern": r"import\s+\*",
                "issue": "通配符导入",
                "description": "通配符导入可能影响性能，建议明确导入需要的模块",
                "severity": "low"
            }
        ]
        
        lines = content.split('\n')
        
        for pattern_info in performance_patterns:
            pattern = pattern_info["pattern"]
            matches = re.finditer(pattern, content, re.IGNORECASE)
            
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                line_content = lines[line_num - 1].strip()
                
                self.results["performance_issues"].append({
                    "file": str(file_path),
                    "issue": pattern_info["issue"],
                    "description": pattern_info["description"],
                    "line": line_num,
                    "line_content": line_content,
                    "severity": pattern_info["severity"]
                })
    
    def _count_conditions(self, node: ast.AST) -> int:
        """计算条件语句的复杂度"""
        if isinstance(node, ast.BoolOp):
            return len(node.values)
        elif isinstance(node, ast.Compare):
            return len(node.comparators) + 1
        else:
            return 1
    
    def _is_import_used(self, tree: ast.AST, module_name: str) -> bool:
        """检查导入的模块是否被使用"""
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                if node.id == module_name:
                    return True
            elif isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name) and node.value.id == module_name:
                    return True
        return False
    
    def _generate_summary(self) -> Dict[str, Any]:
        """生成分析总结"""
        total_issues = (
            len(self.results["flask_issues"]) +
            len(self.results["code_quality"]) +
            len(self.results["security_issues"]) +
            len(self.results["performance_issues"])
        )
        
        high_severity = sum(1 for issue in self.results["flask_issues"] if issue["severity"] == "high")
        high_severity += sum(1 for issue in self.results["security_issues"] if issue["severity"] == "high")
        
        return {
            "total_issues": total_issues,
            "high_severity_issues": high_severity,
            "flask_issues_count": len(self.results["flask_issues"]),
            "code_quality_issues_count": len(self.results["code_quality"]),
            "security_issues_count": len(self.results["security_issues"]),
            "performance_issues_count": len(self.results["performance_issues"])
        }
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳"""
        import datetime
        return datetime.datetime.now().isoformat()
    
    def save_results(self, results: Dict[str, Any], output_path: str):
        """保存检测结果"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"💾 结果已保存到: {output_path}")
        except Exception as e:
            print(f"❌ 保存结果失败: {e}")


if __name__ == "__main__":
    runner = StaticTestRunner()
    results = runner.run_analysis(".")
    print("\n" + "="*60)
    print("静态检测结果:")
    print("="*60)
    print(json.dumps(results, ensure_ascii=False, indent=2))
