#!/usr/bin/env python3
"""
简化动态测试 - 避免Flask版本兼容性问题
专注于基础功能测试，作为完整测试的回退方案
"""

import sys
import os
import json
import time
import traceback
from pathlib import Path
from typing import Dict, Any, List

class SimpleDynamicTest:
    """简化的动态测试类"""
    
    def __init__(self):
        self.test_results = {
            "timestamp": time.time(),
            "test_type": "simple_dynamic",
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
    
    def run_simple_tests(self, target_path: str = ".") -> Dict[str, Any]:
        """运行简化的动态测试"""
        print("🔧 运行简化动态测试...")
        print(f"🎯 目标路径: {target_path}")
        
        try:
            # 测试1: Python环境检查
            self._test_python_environment()
            
            # 测试2: 文件系统检查
            self._test_file_system(target_path)
            
            # 测试3: 代码语法检查
            self._test_code_syntax(target_path)
            
            # 测试4: 导入检查
            self._test_imports(target_path)
            
            # 测试5: 基础Flask检测
            self._test_flask_detection(target_path)
            
            # 计算总结
            self._calculate_summary()
            
            print(f"✅ 简化动态测试完成")
            print(f"📊 成功率: {self.test_results['summary']['success_rate']:.1f}%")
            
            return self.test_results
            
        except Exception as e:
            print(f"❌ 简化动态测试失败: {e}")
            traceback.print_exc()
            return {
                "error": str(e),
                "timestamp": time.time(),
                "test_type": "simple_dynamic"
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
            modules = ['os', 'sys', 'json', 'pathlib', 'time']
            available_modules = []
            
            for module in modules:
                try:
                    __import__(module)
                    available_modules.append(module)
                except ImportError:
                    pass
            
            self.test_results["tests"][test_name] = {
                "status": "passed",
                "details": {
                    "python_version": version_str,
                    "available_modules": available_modules,
                    "platform": sys.platform
                }
            }
            print(f"    ✅ Python环境正常")
            
        except Exception as e:
            self.test_results["tests"][test_name] = {
                "status": "failed",
                "error": str(e)
            }
            print(f"    ❌ Python环境测试失败: {e}")
    
    def _test_file_system(self, target_path: str):
        """测试文件系统"""
        test_name = "file_system"
        print(f"  📁 测试文件系统...")
        
        try:
            path = Path(target_path)
            
            # 检查路径是否存在
            exists = path.exists()
            is_file = path.is_file() if exists else False
            is_dir = path.is_dir() if exists else False
            
            # 如果是目录，检查内容
            contents = []
            if is_dir:
                try:
                    contents = [str(item) for item in path.iterdir()]
                except PermissionError:
                    contents = ["权限不足"]
            
            self.test_results["tests"][test_name] = {
                "status": "passed",
                "details": {
                    "path": str(path),
                    "exists": exists,
                    "is_file": is_file,
                    "is_dir": is_dir,
                    "contents_count": len(contents) if is_dir else 0
                }
            }
            print(f"    ✅ 文件系统访问正常")
            
        except Exception as e:
            self.test_results["tests"][test_name] = {
                "status": "failed",
                "error": str(e)
            }
            print(f"    ❌ 文件系统测试失败: {e}")
    
    def _test_code_syntax(self, target_path: str):
        """测试代码语法"""
        test_name = "code_syntax"
        print(f"  🔍 测试代码语法...")
        
        try:
            path = Path(target_path)
            python_files = []
            syntax_errors = []
            
            if path.is_file() and path.suffix == '.py':
                python_files = [str(path)]
            elif path.is_dir():
                python_files = [str(f) for f in path.rglob('*.py')]
            
            # 检查每个Python文件的语法
            for py_file in python_files[:10]:  # 限制检查文件数量
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 尝试编译代码
                    compile(content, py_file, 'exec')
                    
                except SyntaxError as e:
                    syntax_errors.append({
                        "file": py_file,
                        "error": str(e),
                        "line": e.lineno
                    })
                except Exception as e:
                    syntax_errors.append({
                        "file": py_file,
                        "error": str(e)
                    })
            
            self.test_results["tests"][test_name] = {
                "status": "passed" if not syntax_errors else "failed",
                "details": {
                    "python_files_found": len(python_files),
                    "files_checked": min(len(python_files), 10),
                    "syntax_errors": syntax_errors
                }
            }
            
            if syntax_errors:
                print(f"    ⚠️ 发现 {len(syntax_errors)} 个语法错误")
            else:
                print(f"    ✅ 代码语法检查通过")
            
        except Exception as e:
            self.test_results["tests"][test_name] = {
                "status": "failed",
                "error": str(e)
            }
            print(f"    ❌ 代码语法测试失败: {e}")
    
    def _test_imports(self, target_path: str):
        """测试导入"""
        test_name = "imports"
        print(f"  📦 测试导入...")
        
        try:
            path = Path(target_path)
            import_errors = []
            
            # 查找Python文件
            python_files = []
            if path.is_file() and path.suffix == '.py':
                python_files = [path]
            elif path.is_dir():
                python_files = list(path.rglob('*.py'))
            
            # 检查导入
            for py_file in python_files[:5]:  # 限制检查文件数量
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 简单的导入检查
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        line = line.strip()
                        if line.startswith('import ') or line.startswith('from '):
                            try:
                                # 尝试解析导入语句
                                if 'import' in line:
                                    parts = line.split('import')
                                    if len(parts) == 2:
                                        module = parts[1].strip().split(',')[0].strip()
                                        # 跳过相对导入
                                        if not module.startswith('.'):
                                            try:
                                                __import__(module)
                                            except ImportError:
                                                import_errors.append({
                                                    "file": str(py_file),
                                                    "line": i + 1,
                                                    "module": module,
                                                    "error": "模块未找到"
                                                })
                            except Exception as e:
                                import_errors.append({
                                    "file": str(py_file),
                                    "line": i + 1,
                                    "error": str(e)
                                })
                
                except Exception as e:
                    import_errors.append({
                        "file": str(py_file),
                        "error": str(e)
                    })
            
            self.test_results["tests"][test_name] = {
                "status": "passed" if not import_errors else "failed",
                "details": {
                    "python_files_checked": len(python_files),
                    "import_errors": import_errors
                }
            }
            
            if import_errors:
                print(f"    ⚠️ 发现 {len(import_errors)} 个导入问题")
            else:
                print(f"    ✅ 导入检查通过")
            
        except Exception as e:
            self.test_results["tests"][test_name] = {
                "status": "failed",
                "error": str(e)
            }
            print(f"    ❌ 导入测试失败: {e}")
    
    def _test_flask_detection(self, target_path: str):
        """测试Flask检测"""
        test_name = "flask_detection"
        print(f"  🌐 测试Flask检测...")
        
        try:
            path = Path(target_path)
            flask_indicators = []
            
            # 查找Flask相关文件
            if path.is_file():
                files_to_check = [path]
            else:
                files_to_check = list(path.rglob('*.py'))
            
            # 检查Flask相关代码
            for py_file in files_to_check[:10]:  # 限制检查文件数量
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 检查Flask相关关键词
                    flask_keywords = [
                        'from flask import',
                        'import flask',
                        'Flask(',
                        '@app.route',
                        'app.run(',
                        'render_template',
                        'request',
                        'jsonify'
                    ]
                    
                    for keyword in flask_keywords:
                        if keyword in content:
                            flask_indicators.append({
                                "file": str(py_file),
                                "indicator": keyword
                            })
                            break
                
                except Exception as e:
                    pass
            
            # 检查requirements.txt
            req_file = path / 'requirements.txt' if path.is_dir() else path.parent / 'requirements.txt'
            if req_file.exists():
                try:
                    with open(req_file, 'r', encoding='utf-8') as f:
                        req_content = f.read()
                    if 'flask' in req_content.lower():
                        flask_indicators.append({
                            "file": str(req_file),
                            "indicator": "requirements.txt中的flask依赖"
                        })
                except Exception:
                    pass
            
            is_flask_project = len(flask_indicators) > 0
            
            self.test_results["tests"][test_name] = {
                "status": "passed",
                "details": {
                    "is_flask_project": is_flask_project,
                    "flask_indicators": flask_indicators,
                    "indicators_count": len(flask_indicators)
                }
            }
            
            if is_flask_project:
                print(f"    ✅ 检测到Flask项目 ({len(flask_indicators)} 个指标)")
            else:
                print(f"    ℹ️ 未检测到Flask项目")
            
        except Exception as e:
            self.test_results["tests"][test_name] = {
                "status": "failed",
                "error": str(e)
            }
            print(f"    ❌ Flask检测测试失败: {e}")
    
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
    
    parser = argparse.ArgumentParser(description='简化动态测试')
    parser.add_argument('--target', type=str, default='.', 
                       help='目标文件或目录路径')
    parser.add_argument('--output', type=str, 
                       help='输出文件路径（可选）')
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("简化动态测试")
    print("=" * 50)
    
    tester = SimpleDynamicTest()
    results = tester.run_simple_tests(args.target)
    
    if args.output:
        tester.save_results(results, args.output)
    
    return results


if __name__ == "__main__":
    main()
