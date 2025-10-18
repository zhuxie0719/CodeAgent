#!/usr/bin/env python3
"""
无Flask动态测试 - 完全不依赖Flask的动态测试
专注于代码分析和质量检查，作为最终回退方案
"""

import sys
import os
import json
import time
import traceback
import ast
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

class NoFlaskDynamicTest:
    """无Flask动态测试类"""
    
    def __init__(self):
        self.test_results = {
            "timestamp": time.time(),
            "test_type": "no_flask_dynamic",
            "tests": {},
            "summary": {
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "skipped_tests": 0,
                "success_rate": 0.0,
                "overall_status": "unknown"
            }
        }
    
    def run_no_flask_tests(self, target_path: str = ".") -> Dict[str, Any]:
        """运行无Flask动态测试"""
        print("🔧 运行无Flask动态测试...")
        print(f"🎯 目标路径: {target_path}")
        
        try:
            # 测试1: Python环境检查
            self._test_python_environment()
            
            # 测试2: 项目结构分析
            self._test_project_structure(target_path)
            
            # 测试3: 代码质量检查
            self._test_code_quality(target_path)
            
            # 测试4: 依赖分析
            self._test_dependencies(target_path)
            
            # 测试5: 配置检查
            self._test_configuration(target_path)
            
            # 测试6: 安全扫描
            self._test_security_scan(target_path)
            
            # 测试7: 性能分析
            self._test_performance_analysis(target_path)
            
            # 计算总结
            self._calculate_summary()
            
            print(f"✅ 无Flask动态测试完成")
            print(f"📊 成功率: {self.test_results['summary']['success_rate']:.1f}%")
            
            return self.test_results
            
        except Exception as e:
            print(f"❌ 无Flask动态测试失败: {e}")
            traceback.print_exc()
            return {
                "error": str(e),
                "timestamp": time.time(),
                "test_type": "no_flask_dynamic"
            }
    
    def _test_python_environment(self):
        """测试Python环境"""
        test_name = "python_environment"
        print(f"  🐍 测试Python环境...")
        
        try:
            # 检查Python版本
            python_version = sys.version_info
            version_str = f"{python_version.major}.{python_version.minor}.{python_version.micro}"
            
            # 检查关键模块
            modules = ['os', 'sys', 'json', 'pathlib', 'time', 'ast', 'subprocess']
            available_modules = []
            missing_modules = []
            
            for module in modules:
                try:
                    __import__(module)
                    available_modules.append(module)
                except ImportError:
                    missing_modules.append(module)
            
            # 检查pip
            pip_available = False
            try:
                subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                             capture_output=True, check=True)
                pip_available = True
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass
            
            self.test_results["tests"][test_name] = {
                "status": "passed",
                "details": {
                    "python_version": version_str,
                    "available_modules": available_modules,
                    "missing_modules": missing_modules,
                    "pip_available": pip_available,
                    "platform": sys.platform,
                    "executable": sys.executable
                }
            }
            print(f"    ✅ Python环境正常")
            
        except Exception as e:
            self.test_results["tests"][test_name] = {
                "status": "failed",
                "error": str(e)
            }
            print(f"    ❌ Python环境测试失败: {e}")
    
    def _test_project_structure(self, target_path: str):
        """测试项目结构"""
        test_name = "project_structure"
        print(f"  📁 测试项目结构...")
        
        try:
            path = Path(target_path)
            structure_info = {
                "root_path": str(path),
                "is_file": path.is_file(),
                "is_dir": path.is_dir(),
                "files": [],
                "directories": [],
                "python_files": [],
                "config_files": [],
                "documentation_files": []
            }
            
            if path.is_dir():
                # 扫描项目结构
                for item in path.rglob('*'):
                    if item.is_file():
                        structure_info["files"].append(str(item.relative_to(path)))
                        
                        # 分类文件
                        if item.suffix == '.py':
                            structure_info["python_files"].append(str(item.relative_to(path)))
                        elif item.name in ['requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile']:
                            structure_info["config_files"].append(str(item.relative_to(path)))
                        elif item.suffix in ['.md', '.txt', '.rst']:
                            structure_info["documentation_files"].append(str(item.relative_to(path)))
                    
                    elif item.is_dir():
                        structure_info["directories"].append(str(item.relative_to(path)))
            
            # 分析项目类型
            project_type = "unknown"
            if any('flask' in f.lower() for f in structure_info["config_files"]):
                project_type = "flask"
            elif any('django' in f.lower() for f in structure_info["config_files"]):
                project_type = "django"
            elif structure_info["python_files"]:
                project_type = "python"
            
            structure_info["project_type"] = project_type
            
            self.test_results["tests"][test_name] = {
                "status": "passed",
                "details": structure_info
            }
            print(f"    ✅ 项目结构分析完成")
            
        except Exception as e:
            self.test_results["tests"][test_name] = {
                "status": "failed",
                "error": str(e)
            }
            print(f"    ❌ 项目结构测试失败: {e}")
    
    def _test_code_quality(self, target_path: str):
        """测试代码质量"""
        test_name = "code_quality"
        print(f"  🔍 测试代码质量...")
        
        try:
            path = Path(target_path)
            quality_issues = []
            quality_metrics = {
                "total_files": 0,
                "total_lines": 0,
                "total_functions": 0,
                "total_classes": 0,
                "complexity_issues": [],
                "style_issues": []
            }
            
            # 查找Python文件
            python_files = []
            if path.is_file() and path.suffix == '.py':
                python_files = [path]
            elif path.is_dir():
                python_files = list(path.rglob('*.py'))
            
            quality_metrics["total_files"] = len(python_files)
            
            # 分析每个Python文件
            for py_file in python_files[:20]:  # 限制分析文件数量
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    lines = content.split('\n')
                    quality_metrics["total_lines"] += len(lines)
                    
                    # 解析AST
                    try:
                        tree = ast.parse(content)
                        
                        # 统计函数和类
                        for node in ast.walk(tree):
                            if isinstance(node, ast.FunctionDef):
                                quality_metrics["total_functions"] += 1
                                
                                # 检查函数复杂度
                                if len(node.body) > 20:
                                    quality_metrics["complexity_issues"].append({
                                        "file": str(py_file),
                                        "function": node.name,
                                        "issue": "函数过长",
                                        "lines": len(node.body)
                                    })
                                
                            elif isinstance(node, ast.ClassDef):
                                quality_metrics["total_classes"] += 1
                                
                                # 检查类复杂度
                                if len(node.body) > 50:
                                    quality_metrics["complexity_issues"].append({
                                        "file": str(py_file),
                                        "class": node.name,
                                        "issue": "类过长",
                                        "lines": len(node.body)
                                    })
                        
                        # 检查代码风格
                        for i, line in enumerate(lines):
                            line_num = i + 1
                            
                            # 检查行长度
                            if len(line) > 120:
                                quality_metrics["style_issues"].append({
                                    "file": str(py_file),
                                    "line": line_num,
                                    "issue": "行过长",
                                    "length": len(line)
                                })
                            
                            # 检查缩进
                            if line.strip() and not line.startswith((' ', '\t')):
                                if any(keyword in line for keyword in ['def ', 'class ', 'if ', 'for ', 'while ', 'try:', 'except', 'with ']):
                                    quality_metrics["style_issues"].append({
                                        "file": str(py_file),
                                        "line": line_num,
                                        "issue": "缩进问题"
                                    })
                    
                    except SyntaxError as e:
                        quality_issues.append({
                            "file": str(py_file),
                            "error": f"语法错误: {e}",
                            "line": e.lineno
                        })
                
                except Exception as e:
                    quality_issues.append({
                        "file": str(py_file),
                        "error": str(e)
                    })
            
            # 计算质量分数
            total_issues = len(quality_issues) + len(quality_metrics["complexity_issues"]) + len(quality_metrics["style_issues"])
            quality_score = max(0, 100 - total_issues * 2)
            
            self.test_results["tests"][test_name] = {
                "status": "passed" if quality_score >= 70 else "failed",
                "details": {
                    "quality_score": quality_score,
                    "quality_issues": quality_issues,
                    "metrics": quality_metrics
                }
            }
            
            if quality_score >= 70:
                print(f"    ✅ 代码质量良好 (分数: {quality_score})")
            else:
                print(f"    ⚠️ 代码质量需要改进 (分数: {quality_score})")
            
        except Exception as e:
            self.test_results["tests"][test_name] = {
                "status": "failed",
                "error": str(e)
            }
            print(f"    ❌ 代码质量测试失败: {e}")
    
    def _test_dependencies(self, target_path: str):
        """测试依赖分析"""
        test_name = "dependencies"
        print(f"  📦 测试依赖分析...")
        
        try:
            path = Path(target_path)
            dependency_info = {
                "requirements_files": [],
                "dependencies": [],
                "missing_dependencies": [],
                "version_conflicts": []
            }
            
            # 查找依赖文件
            req_files = []
            if path.is_dir():
                req_files = list(path.glob('requirements*.txt')) + list(path.glob('Pipfile')) + list(path.glob('pyproject.toml'))
            elif path.is_file() and path.name in ['requirements.txt', 'Pipfile', 'pyproject.toml']:
                req_files = [path]
            
            dependency_info["requirements_files"] = [str(f) for f in req_files]
            
            # 解析依赖
            for req_file in req_files:
                try:
                    with open(req_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if req_file.name == 'requirements.txt':
                        # 解析requirements.txt
                        for line in content.split('\n'):
                            line = line.strip()
                            if line and not line.startswith('#'):
                                if '==' in line:
                                    name, version = line.split('==', 1)
                                    dependency_info["dependencies"].append({
                                        "name": name.strip(),
                                        "version": version.strip(),
                                        "file": str(req_file)
                                    })
                                else:
                                    dependency_info["dependencies"].append({
                                        "name": line,
                                        "version": "未指定",
                                        "file": str(req_file)
                                    })
                    
                except Exception as e:
                    dependency_info["missing_dependencies"].append({
                        "file": str(req_file),
                        "error": str(e)
                    })
            
            # 检查关键依赖
            critical_deps = ['flask', 'django', 'requests', 'numpy', 'pandas']
            for dep in critical_deps:
                found = any(dep.lower() in d["name"].lower() for d in dependency_info["dependencies"])
                if not found:
                    dependency_info["missing_dependencies"].append({
                        "dependency": dep,
                        "reason": "未在依赖文件中找到"
                    })
            
            self.test_results["tests"][test_name] = {
                "status": "passed",
                "details": dependency_info
            }
            print(f"    ✅ 依赖分析完成")
            
        except Exception as e:
            self.test_results["tests"][test_name] = {
                "status": "failed",
                "error": str(e)
            }
            print(f"    ❌ 依赖分析测试失败: {e}")
    
    def _test_configuration(self, target_path: str):
        """测试配置检查"""
        test_name = "configuration"
        print(f"  ⚙️ 测试配置检查...")
        
        try:
            path = Path(target_path)
            config_info = {
                "config_files": [],
                "environment_files": [],
                "config_issues": []
            }
            
            # 查找配置文件
            config_patterns = ['*.conf', '*.ini', '*.yaml', '*.yml', '*.json', '*.toml']
            env_patterns = ['.env', '.env.local', '.env.production', '.env.development']
            
            if path.is_dir():
                for pattern in config_patterns:
                    config_files = list(path.rglob(pattern))
                    config_info["config_files"].extend([str(f) for f in config_files])
                
                for pattern in env_patterns:
                    env_files = list(path.rglob(pattern))
                    config_info["environment_files"].extend([str(f) for f in env_files])
            
            # 检查配置问题
            for config_file in config_info["config_files"][:5]:  # 限制检查文件数量
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 检查敏感信息
                    sensitive_patterns = ['password', 'secret', 'key', 'token', 'api_key']
                    for pattern in sensitive_patterns:
                        if pattern.lower() in content.lower():
                            config_info["config_issues"].append({
                                "file": config_file,
                                "issue": f"可能包含敏感信息: {pattern}",
                                "severity": "warning"
                            })
                
                except Exception as e:
                    config_info["config_issues"].append({
                        "file": config_file,
                        "issue": f"读取失败: {e}",
                        "severity": "error"
                    })
            
            self.test_results["tests"][test_name] = {
                "status": "passed",
                "details": config_info
            }
            print(f"    ✅ 配置检查完成")
            
        except Exception as e:
            self.test_results["tests"][test_name] = {
                "status": "failed",
                "error": str(e)
            }
            print(f"    ❌ 配置检查测试失败: {e}")
    
    def _test_security_scan(self, target_path: str):
        """测试安全扫描"""
        test_name = "security_scan"
        print(f"  🔒 测试安全扫描...")
        
        try:
            path = Path(target_path)
            security_issues = []
            
            # 查找Python文件
            python_files = []
            if path.is_file() and path.suffix == '.py':
                python_files = [path]
            elif path.is_dir():
                python_files = list(path.rglob('*.py'))
            
            # 安全扫描
            for py_file in python_files[:10]:  # 限制扫描文件数量
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    lines = content.split('\n')
                    
                    # 检查危险函数
                    dangerous_functions = [
                        'eval(', 'exec(', 'compile(',
                        'os.system(', 'subprocess.call(',
                        'pickle.loads(', 'marshal.loads(',
                        'sqlite3.connect('
                    ]
                    
                    for i, line in enumerate(lines):
                        line_num = i + 1
                        for func in dangerous_functions:
                            if func in line:
                                security_issues.append({
                                    "file": str(py_file),
                                    "line": line_num,
                                    "issue": f"使用危险函数: {func}",
                                    "severity": "high"
                                })
                    
                    # 检查硬编码密码
                    if 'password' in content.lower() and '=' in content:
                        security_issues.append({
                            "file": str(py_file),
                            "issue": "可能包含硬编码密码",
                            "severity": "medium"
                        })
                    
                    # 检查SQL注入风险
                    if any(keyword in content.lower() for keyword in ['select', 'insert', 'update', 'delete']):
                        if 'format(' in content or '%' in content:
                            security_issues.append({
                                "file": str(py_file),
                                "issue": "可能存在SQL注入风险",
                                "severity": "high"
                            })
                
                except Exception as e:
                    security_issues.append({
                        "file": str(py_file),
                        "error": str(e)
                    })
            
            self.test_results["tests"][test_name] = {
                "status": "passed" if not security_issues else "failed",
                "details": {
                    "security_issues": security_issues,
                    "high_severity_count": sum(1 for issue in security_issues if issue.get("severity") == "high"),
                    "medium_severity_count": sum(1 for issue in security_issues if issue.get("severity") == "medium"),
                    "low_severity_count": sum(1 for issue in security_issues if issue.get("severity") == "low")
                }
            }
            
            if security_issues:
                print(f"    ⚠️ 发现 {len(security_issues)} 个安全问题")
            else:
                print(f"    ✅ 安全扫描通过")
            
        except Exception as e:
            self.test_results["tests"][test_name] = {
                "status": "failed",
                "error": str(e)
            }
            print(f"    ❌ 安全扫描测试失败: {e}")
    
    def _test_performance_analysis(self, target_path: str):
        """测试性能分析"""
        test_name = "performance_analysis"
        print(f"  ⚡ 测试性能分析...")
        
        try:
            path = Path(target_path)
            performance_issues = []
            
            # 查找Python文件
            python_files = []
            if path.is_file() and path.suffix == '.py':
                python_files = [path]
            elif path.is_dir():
                python_files = list(path.rglob('*.py'))
            
            # 性能分析
            for py_file in python_files[:10]:  # 限制分析文件数量
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    lines = content.split('\n')
                    
                    # 检查性能问题
                    for i, line in enumerate(lines):
                        line_num = i + 1
                        
                        # 检查循环中的数据库查询
                        if any(keyword in line.lower() for keyword in ['for ', 'while ']):
                            # 检查后续几行是否有数据库查询
                            for j in range(i + 1, min(i + 10, len(lines))):
                                if any(keyword in lines[j].lower() for keyword in ['select', 'insert', 'update', 'delete']):
                                    performance_issues.append({
                                        "file": str(py_file),
                                        "line": line_num,
                                        "issue": "循环中可能存在数据库查询",
                                        "severity": "medium"
                                    })
                                    break
                        
                        # 检查大量数据加载
                        if 'load' in line.lower() and any(keyword in line.lower() for keyword in ['all', 'entire', 'whole']):
                            performance_issues.append({
                                "file": str(py_file),
                                "line": line_num,
                                "issue": "可能加载大量数据",
                                "severity": "low"
                            })
                        
                        # 检查同步操作
                        if any(keyword in line.lower() for keyword in ['time.sleep', 'input(', 'raw_input']):
                            performance_issues.append({
                                "file": str(py_file),
                                "line": line_num,
                                "issue": "同步阻塞操作",
                                "severity": "low"
                            })
                
                except Exception as e:
                    performance_issues.append({
                        "file": str(py_file),
                        "error": str(e)
                    })
            
            self.test_results["tests"][test_name] = {
                "status": "passed" if not performance_issues else "failed",
                "details": {
                    "performance_issues": performance_issues,
                    "total_issues": len(performance_issues)
                }
            }
            
            if performance_issues:
                print(f"    ⚠️ 发现 {len(performance_issues)} 个性能问题")
            else:
                print(f"    ✅ 性能分析通过")
            
        except Exception as e:
            self.test_results["tests"][test_name] = {
                "status": "failed",
                "error": str(e)
            }
            print(f"    ❌ 性能分析测试失败: {e}")
    
    def _calculate_summary(self):
        """计算测试总结"""
        tests = self.test_results["tests"]
        total = len(tests)
        passed = sum(1 for test in tests.values() if test["status"] == "passed")
        failed = sum(1 for test in tests.values() if test["status"] == "failed")
        skipped = sum(1 for test in tests.values() if test["status"] == "skipped")
        
        success_rate = (passed / total * 100) if total > 0 else 0
        
        if success_rate >= 80:
            overall_status = "excellent"
        elif success_rate >= 60:
            overall_status = "good"
        elif success_rate >= 40:
            overall_status = "fair"
        else:
            overall_status = "poor"
        
        self.test_results["summary"].update({
            "total_tests": total,
            "passed_tests": passed,
            "failed_tests": failed,
            "skipped_tests": skipped,
            "success_rate": success_rate,
            "overall_status": overall_status
        })
    
    def save_results(self, results: Dict[str, Any], output_file: str):
        """保存测试结果"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"📄 测试结果已保存到: {output_file}")
        except Exception as e:
            print(f"❌ 保存结果失败: {e}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='无Flask动态测试')
    parser.add_argument('--target', type=str, default='.', 
                       help='目标文件或目录路径')
    parser.add_argument('--output', type=str, 
                       help='输出文件路径（可选）')
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("无Flask动态测试")
    print("=" * 50)
    
    tester = NoFlaskDynamicTest()
    results = tester.run_no_flask_tests(args.target)
    
    if args.output:
        tester.save_results(results, args.output)
    
    return results


if __name__ == "__main__":
    main()
