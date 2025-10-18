#!/usr/bin/env python3
"""
不依赖Flask的动态测试，专注于代码分析
"""

import sys
import os
import time
import json
import ast
import subprocess
from pathlib import Path
from typing import Dict, Any, List

class NoFlaskDynamicTest:
    """不依赖Flask的动态测试类"""

    def __init__(self):
        self.test_results = {}

    def run_no_flask_tests(self) -> Dict[str, Any]:
        """运行不依赖Flask的动态测试"""
        print("开始无Flask动态测试...")
        print("="*50)

        results = {
            "test_type": "no_flask_dynamic_test",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "tests": {}
        }

        try:
            # 测试1: Python环境检查
            print("\n测试1: Python环境检查")
            results["tests"]["python_environment"] = self._test_python_environment()

            # 测试2: 代码语法检查
            print("\n测试2: 代码语法检查")
            results["tests"]["syntax_check"] = self._test_syntax_check()

            # 测试3: 导入检查
            print("\n测试3: 导入检查")
            results["tests"]["import_check"] = self._test_import_check()

            # 测试4: 项目结构分析
            print("\n测试4: 项目结构分析")
            results["tests"]["project_structure"] = self._test_project_structure()

            # 测试5: 代码质量检查
            print("\n测试5: 代码质量检查")
            results["tests"]["code_quality"] = self._test_code_quality()

            # 生成测试摘要
            results["summary"] = self._generate_test_summary(results)

            print("\n无Flask动态测试完成！")
            return results

        except (ImportError, RuntimeError, AttributeError, OSError) as e:
            print(f"\n无Flask动态测试失败: {e}")
            results["error"] = str(e)
            results["summary"] = self._generate_test_summary(results)
            return results

    def _test_python_environment(self) -> Dict[str, Any]:
        """测试Python环境"""
        try:
            import sys
            import platform

            result = {
                "status": "success",
                "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "platform": platform.system(),
                "architecture": platform.architecture()[0],
                "executable": sys.executable,
                "path": sys.path[:3]  # 只显示前3个路径
            }

            print("  ✅ Python环境检查成功")
            print(f"  - Python版本: {result['python_version']}")
            print(f"  - 平台: {result['platform']}")

            return result

        except (ImportError, RuntimeError, AttributeError, OSError) as e:
            print(f"  ❌ Python环境检查失败: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

    def _test_syntax_check(self) -> Dict[str, Any]:
        """测试代码语法"""
        try:
            current_dir = Path(__file__).parent
            python_files = list(current_dir.glob("*.py"))

            syntax_errors = []
            valid_files = 0

            for py_file in python_files:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 使用ast检查语法
                    ast.parse(content)
                    valid_files += 1

                except SyntaxError as e:
                    syntax_errors.append({
                        "file": py_file.name,
                        "line": e.lineno,
                        "message": str(e)
                    })
                except (ImportError, RuntimeError, AttributeError, OSError) as e:
                    syntax_errors.append({
                        "file": py_file.name,
                        "line": 0,
                        "message": str(e)
                    })

            result = {
                "status": "success" if not syntax_errors else "partial",
                "total_files": len(python_files),
                "valid_files": valid_files,
                "syntax_errors": syntax_errors,
                "error_count": len(syntax_errors)
            }

            print("  ✅ 代码语法检查完成")
            print(f"  - 检查文件: {len(python_files)}个")
            print(f"  - 有效文件: {valid_files}个")
            print(f"  - 语法错误: {len(syntax_errors)}个")

            return result

        except (ImportError, RuntimeError, AttributeError, OSError) as e:
            print(f"  ❌ 代码语法检查失败: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

    def _test_import_check(self) -> Dict[str, Any]:
        """测试导入检查"""
        try:
            current_dir = Path(__file__).parent
            python_files = list(current_dir.glob("*.py"))

            import_issues = []
            successful_imports = 0

            for py_file in python_files:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # 解析AST
                    tree = ast.parse(content)

                    # 查找导入语句
                    imports = []
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                imports.append(alias.name)
                        elif isinstance(node, ast.ImportFrom):
                            module = node.module or ""
                            for alias in node.names:
                                imports.append(f"{module}.{alias.name}")

                    # 检查导入是否可用
                    for import_name in imports:
                        try:
                            if '.' in import_name:
                                module_name = import_name.split('.')[0]
                                __import__(module_name)
                            else:
                                __import__(import_name)
                            successful_imports += 1
                        except ImportError as e:
                            import_issues.append({
                                "file": py_file.name,
                                "import": import_name,
                                "error": str(e)
                            })

                except (ImportError, RuntimeError, AttributeError, OSError) as e:
                    import_issues.append({
                        "file": py_file.name,
                        "import": "unknown",
                        "error": str(e)
                    })

            result = {
                "status": "success" if not import_issues else "partial",
                "total_imports": successful_imports + len(import_issues),
                "successful_imports": successful_imports,
                "import_issues": import_issues,
                "issue_count": len(import_issues)
            }

            print("  ✅ 导入检查完成")
            print(f"  - 总导入数: {result['total_imports']}")
            print(f"  - 成功导入: {successful_imports}")
            print(f"  - 导入问题: {len(import_issues)}")

            return result

        except (ImportError, RuntimeError, AttributeError, OSError) as e:
            print(f"  ❌ 导入检查失败: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

    def _test_project_structure(self) -> Dict[str, Any]:
        """测试项目结构"""
        try:
            current_dir = Path(__file__).parent
            parent_dir = current_dir.parent

            # 分析项目结构
            structure = {
                "files": [],
                "directories": [],
                "python_files": 0,
                "total_lines": 0,
                "file_sizes": []
            }

            for item in parent_dir.rglob("*"):
                if item.is_file():
                    rel_path = item.relative_to(parent_dir)
                    structure["files"].append(str(rel_path))

                    if item.suffix == '.py':
                        structure["python_files"] += 1

                        try:
                            with open(item, 'r', encoding='utf-8') as f:
                                lines = len(f.readlines())
                                structure["total_lines"] += lines
                        except:
                            pass

                    try:
                        size = item.stat().st_size
                        structure["file_sizes"].append(size)
                    except:
                        pass

                elif item.is_dir() and not any(part.startswith('.') for part in item.parts):
                    rel_path = item.relative_to(parent_dir)
                    structure["directories"].append(str(rel_path))

            # 计算统计信息
            avg_file_size = sum(structure["file_sizes"]) / len(structure["file_sizes"]) if structure["file_sizes"] else 0

            result = {
                "status": "success",
                "total_files": len(structure["files"]),
                "total_directories": len(structure["directories"]),
                "python_files": structure["python_files"],
                "total_lines": structure["total_lines"],
                "average_file_size": round(avg_file_size, 2),
                "project_scale": "small" if len(structure["files"]) < 50 else "medium" if len(structure["files"]) < 200 else "large"
            }

            print("  ✅ 项目结构分析完成")
            print(f"  - 总文件数: {len(structure['files'])}")
            print(f"  - Python文件: {structure['python_files']}")
            print(f"  - 总代码行数: {structure['total_lines']}")
            print(f"  - 项目规模: {result['project_scale']}")

            return result

        except (ImportError, RuntimeError, AttributeError, OSError) as e:
            print(f"  ❌ 项目结构分析失败: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

    def _test_code_quality(self) -> Dict[str, Any]:
        """测试代码质量"""
        try:
            current_dir = Path(__file__).parent
            python_files = list(current_dir.glob("*.py"))

            quality_issues = []
            total_functions = 0
            total_classes = 0

            for py_file in python_files:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    tree = ast.parse(content)

                    # 统计函数和类
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            total_functions += 1

                            # 检查函数长度
                            if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                                func_length = node.end_lineno - node.lineno
                                if func_length > 50:
                                    quality_issues.append({
                                        "file": py_file.name,
                                        "type": "long_function",
                                        "function": node.name,
                                        "line": node.lineno,
                                        "length": func_length
                                    })

                        elif isinstance(node, ast.ClassDef):
                            total_classes += 1

                            # 检查类长度
                            if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                                class_length = node.end_lineno - node.lineno
                                if class_length > 100:
                                    quality_issues.append({
                                        "file": py_file.name,
                                        "type": "long_class",
                                        "class": node.name,
                                        "line": node.lineno,
                                        "length": class_length
                                    })

                    # 检查代码复杂度（简单的嵌套深度检查）
                    max_depth = 0
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.For, ast.While, ast.If, ast.Try)):
                            depth = self._get_nesting_depth(node)
                            max_depth = max(max_depth, depth)

                    if max_depth > 5:
                        quality_issues.append({
                            "file": py_file.name,
                            "type": "high_complexity",
                            "line": 0,
                            "max_depth": max_depth
                        })

                except (ImportError, RuntimeError, AttributeError, OSError) as e:
                    quality_issues.append({
                        "file": py_file.name,
                        "type": "analysis_error",
                        "line": 0,
                        "error": str(e)
                    })

            result = {
                "status": "success" if len(quality_issues) < 5 else "partial",
                "total_functions": total_functions,
                "total_classes": total_classes,
                "quality_issues": quality_issues,
                "issue_count": len(quality_issues),
                "code_quality_score": max(0, 100 - len(quality_issues) * 10)
            }

            print("  ✅ 代码质量检查完成")
            print(f"  - 函数数量: {total_functions}")
            print(f"  - 类数量: {total_classes}")
            print(f"  - 质量问题: {len(quality_issues)}")
            print(f"  - 质量评分: {result['code_quality_score']}")

            return result

        except (ImportError, RuntimeError, AttributeError, OSError) as e:
            print(f"  ❌ 代码质量检查失败: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

    def _get_nesting_depth(self, node, current_depth=0):
        """获取嵌套深度"""
        max_depth = current_depth
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.For, ast.While, ast.If, ast.Try)):
                depth = self._get_nesting_depth(child, current_depth + 1)
                max_depth = max(max_depth, depth)
        return max_depth

    def _generate_test_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """生成测试摘要"""
        tests = results.get("tests", {})

        # 统计测试结果
        total_tests = len(tests)
        successful_tests = 0
        failed_tests = 0
        partial_tests = 0

        for test_name, test_result in tests.items():
            status = test_result.get("status", "unknown")
            if status == "success":
                successful_tests += 1
            elif status == "failed":
                failed_tests += 1
            elif status == "partial":
                partial_tests += 1

        # 计算成功率
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0

        # 确定整体状态
        if failed_tests == 0:
            overall_status = "success"
        elif successful_tests > failed_tests:
            overall_status = "partial"
        else:
            overall_status = "failed"

        return {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "partial_tests": partial_tests,
            "success_rate": round(success_rate, 2),
            "overall_status": overall_status
        }

def main():
    """主函数"""
    print("无Flask动态测试运行器")
    print("="*30)

    # 创建测试实例
    tester = NoFlaskDynamicTest()

    # 运行测试
    results = tester.run_no_flask_tests()

    # 显示测试摘要
    summary = results.get("summary", {})
    print("\n" + "="*30)
    print("测试摘要")
    print("="*30)
    print(f"总测试数: {summary.get('total_tests', 0)}")
    print(f"成功测试: {summary.get('successful_tests', 0)}")
    print(f"失败测试: {summary.get('failed_tests', 0)}")
    print(f"部分成功: {summary.get('partial_tests', 0)}")
    print(f"成功率: {summary.get('success_rate', 0)}%")
    print(f"整体状态: {summary.get('overall_status', 'unknown')}")

    # 保存结果
    try:
        results_file = f"no_flask_dynamic_test_results_{int(time.time())}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n测试结果已保存到: {results_file}")
    except (ImportError, RuntimeError, AttributeError, OSError) as e:
        print(f"\n保存结果失败: {e}")

if __name__ == "__main__":
    main()
