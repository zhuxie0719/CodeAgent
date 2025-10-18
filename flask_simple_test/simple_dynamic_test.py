#!/usr/bin/env python3
"""
简化的动态测试，避免Flask版本兼容性问题
"""

import sys
import os
import time
import json
from pathlib import Path
from typing import Dict, Any, List

# 应用Werkzeug兼容性补丁
try:
    import werkzeug.urls
    from urllib.parse import quote as url_quote, urlparse as url_parse
    patches_applied = []
    
    if not hasattr(werkzeug.urls, 'url_quote'):
        werkzeug.urls.url_quote = url_quote
        patches_applied.append("url_quote")
        
    if not hasattr(werkzeug.urls, 'url_parse'):
        werkzeug.urls.url_parse = url_parse
        patches_applied.append("url_parse")
        
    if patches_applied:
        print(f"🔧 已应用Werkzeug兼容性补丁: {', '.join(patches_applied)}")
except ImportError:
    print("⚠️ 无法应用Werkzeug兼容性补丁")

class SimpleDynamicTest:
    """简化的动态测试类"""

    def __init__(self):
        self.test_results = {}

    def run_simple_tests(self) -> Dict[str, Any]:
        """运行简化的动态测试"""
        print("开始简化动态测试...")
        print("="*50)

        results = {
            "test_type": "simple_dynamic_test",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "tests": {}
        }

        try:
            # 测试1: Python环境检查
            print("\n测试1: Python环境检查")
            results["tests"]["python_environment"] = self._test_python_environment()

            # 测试2: Flask导入检查
            print("\n测试2: Flask导入检查")
            results["tests"]["flask_import"] = self._test_flask_import()

            # 测试3: 基础Flask功能
            print("\n测试3: 基础Flask功能")
            results["tests"]["basic_flask"] = self._test_basic_flask()

            # 测试4: 项目文件检查
            print("\n测试4: 项目文件检查")
            results["tests"]["project_files"] = self._test_project_files()

            # 生成测试摘要
            results["summary"] = self._generate_test_summary(results)

            print("\n简化动态测试完成！")
            return results

        except (ImportError, RuntimeError, AttributeError, OSError) as e:
            print(f"\n简化动态测试失败: {e}")
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
                "executable": sys.executable
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

    def _test_flask_import(self) -> Dict[str, Any]:
        """测试Flask导入"""
        try:
            import flask
            flask_version = flask.__version__

            # 检查关键模块
            modules_to_check = [
                'flask.Flask',
                'flask.request',
                'flask.jsonify',
                'flask.Blueprint'
            ]

            available_modules = []
            for module in modules_to_check:
                try:
                    exec(f"from {module} import *")
                    available_modules.append(module)
                except:
                    pass

            result = {
                "status": "success",
                "flask_version": flask_version,
                "available_modules": available_modules,
                "module_count": len(available_modules)
            }

            print("  ✅ Flask导入检查成功")
            print(f"  - Flask版本: {flask_version}")
            print(f"  - 可用模块: {len(available_modules)}/{len(modules_to_check)}")

            return result

        except ImportError as e:
            print(f"  ❌ Flask导入失败: {e}")
            return {
                "status": "failed",
                "error": f"Flask未安装: {e}"
            }
        except (ImportError, RuntimeError, AttributeError, OSError) as e:
            print(f"  ❌ Flask导入检查失败: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

    def _test_basic_flask(self) -> Dict[str, Any]:
        """测试基础Flask功能"""
        try:
            from flask import Flask

            # 创建应用
            app = Flask(__name__)
            app.config['TESTING'] = True

            # 测试基本属性
            result = {
                "status": "success",
                "app_name": app.name,
                "debug_mode": app.debug,
                "testing_mode": app.testing,
                "config_keys": len(app.config),
                "url_rules": len(app.url_map._rules)
            }

            print("  ✅ 基础Flask功能测试成功")
            print(f"  - 应用名称: {app.name}")
            print(f"  - 配置项数量: {len(app.config)}")

            return result

        except (ImportError, RuntimeError, AttributeError, OSError) as e:
            print(f"  ❌ 基础Flask功能测试失败: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

    def _test_project_files(self) -> Dict[str, Any]:
        """测试项目文件"""
        try:
            current_dir = Path(__file__).parent
            project_files = []

            # 查找Python文件
            for py_file in current_dir.glob("*.py"):
                if py_file.name != __file__:
                    project_files.append(py_file.name)

            # 查找其他重要文件
            important_files = ['README.md', 'requirements.txt', 'setup.py']
            for file_name in important_files:
                file_path = current_dir / file_name
                if file_path.exists():
                    project_files.append(file_name)

            result = {
                "status": "success",
                "project_files": project_files,
                "file_count": len(project_files),
                "current_directory": str(current_dir)
            }

            print("  ✅ 项目文件检查成功")
            print(f"  - 发现文件: {len(project_files)}个")
            print(f"  - 文件列表: {', '.join(project_files[:5])}{'...' if len(project_files) > 5 else ''}")

            return result

        except (ImportError, RuntimeError, AttributeError, OSError) as e:
            print(f"  ❌ 项目文件检查失败: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

    def _generate_test_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """生成测试摘要"""
        tests = results.get("tests", {})

        # 统计测试结果
        total_tests = len(tests)
        successful_tests = 0
        failed_tests = 0

        for test_name, test_result in tests.items():
            status = test_result.get("status", "unknown")
            if status == "success":
                successful_tests += 1
            elif status == "failed":
                failed_tests += 1

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
            "success_rate": round(success_rate, 2),
            "overall_status": overall_status
        }

def main():
    """主函数"""
    print("简化动态测试运行器")
    print("="*30)

    # 创建测试实例
    tester = SimpleDynamicTest()

    # 运行测试
    results = tester.run_simple_tests()

    # 显示测试摘要
    summary = results.get("summary", {})
    print("\n" + "="*30)
    print("测试摘要")
    print("="*30)
    print(f"总测试数: {summary.get('total_tests', 0)}")
    print(f"成功测试: {summary.get('successful_tests', 0)}")
    print(f"失败测试: {summary.get('failed_tests', 0)}")
    print(f"成功率: {summary.get('success_rate', 0)}%")
    print(f"整体状态: {summary.get('overall_status', 'unknown')}")

    # 保存结果
    try:
        results_file = f"simple_dynamic_test_results_{int(time.time())}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n测试结果已保存到: {results_file}")
    except (ImportError, RuntimeError, AttributeError, OSError) as e:
        print(f"\n保存结果失败: {e}")

if __name__ == "__main__":
    main()
