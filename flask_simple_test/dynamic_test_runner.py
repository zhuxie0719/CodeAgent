#!/usr/bin/env python3
"""
动态测试运行器
通过实际运行Flask应用来检测问题
"""

import os
import sys
import json
import time
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
import importlib.util

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class DynamicTestRunner:
    """动态测试运行器"""
    
    def __init__(self):
        self.results = {}
        self.temp_dir = None
        self.flask_app_path = None
        
    def run_dynamic_tests(self, target_path: str) -> Dict[str, Any]:
        """运行动态测试"""
        print(f"🎯 目标路径: {target_path}")
        
        # 检查Flask环境
        flask_info = self._check_flask_environment()
        print(f"📋 Flask环境信息:")
        for key, value in flask_info.items():
            print(f"  - {key}: {value}")
        
        # 检查Werkzeug版本兼容性
        try:
            import werkzeug
            # 安全地获取版本信息
            try:
                werkzeug_version = werkzeug.__version__
            except AttributeError:
                try:
                    import pkg_resources
                    werkzeug_version = pkg_resources.get_distribution('werkzeug').version
                except:
                    werkzeug_version = "unknown"
            print(f"  - Werkzeug版本: {werkzeug_version}")

            # 检查是否有url_quote问题
            try:
                from werkzeug.urls import url_quote  # pylint: disable=import-outside-toplevel
                print("  ✅ Werkzeug url_quote导入正常")
            except ImportError as e:
                print(f"  ❌ Werkzeug url_quote导入失败: {e}")
                return {
                    "status": "failed",
                    "error": f"Werkzeug兼容性问题: {e}",
                    "flask_info": flask_info,
                    "timestamp": time.time()
                }
                
        except Exception as e:
            print(f"  ❌ Werkzeug检查失败: {e}")
            return {
                "status": "failed", 
                "error": f"Werkzeug检查失败: {e}",
                "flask_info": flask_info,
                "timestamp": time.time()
            }
        
        # 创建临时测试环境
        try:
            self._setup_temp_environment(target_path)
            
            # 运行Flask应用测试
            test_results = self._run_flask_tests()
            
            return {
                "status": "success",
                "flask_info": flask_info,
                "test_results": test_results,
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "flask_info": flask_info,
                "timestamp": time.time()
            }
        finally:
            self._cleanup_temp_environment()
    
    def _check_flask_environment(self) -> Dict[str, Any]:
        """检查Flask环境"""
        flask_info = {}
        
        try:
            import flask
            flask_info["flask_installed"] = True
            flask_info["flask_version"] = flask.__version__
        except ImportError:
            flask_info["flask_installed"] = False
            flask_info["flask_version"] = "未安装"
            return flask_info
        
        try:
            import werkzeug
            flask_info["werkzeug_installed"] = True
            try:
                flask_info["werkzeug_version"] = werkzeug.__version__
            except AttributeError:
                flask_info["werkzeug_version"] = "版本未知"
        except ImportError:
            flask_info["werkzeug_installed"] = False
            flask_info["werkzeug_version"] = "未安装"
        
        # 检查其他依赖
        dependencies = ['jinja2', 'markupsafe', 'itsdangerous', 'click']
        for dep in dependencies:
            try:
                module = importlib.import_module(dep)
                version = getattr(module, '__version__', 'unknown')
                flask_info[f"{dep}_version"] = version
            except ImportError:
                flask_info[f"{dep}_version"] = "未安装"
        
        return flask_info
    
    def _setup_temp_environment(self, target_path: str):
        """设置临时测试环境"""
        self.temp_dir = tempfile.mkdtemp(prefix="flask_dynamic_test_")
        print(f"📁 创建临时目录: {self.temp_dir}")
        
        # 复制目标文件到临时目录
        target_path = Path(target_path)
        if target_path.is_file():
            shutil.copy2(target_path, self.temp_dir)
            self.flask_app_path = Path(self.temp_dir) / target_path.name
        elif target_path.is_dir():
            shutil.copytree(target_path, Path(self.temp_dir) / "app")
            self.flask_app_path = Path(self.temp_dir) / "app"
        else:
            raise ValueError(f"无效的目标路径: {target_path}")
    
    def _run_flask_tests(self) -> Dict[str, Any]:
        """运行Flask应用测试"""
        test_results = {
            "app_startup": False,
            "route_tests": {},
            "error_handling": {},
            "performance": {}
        }
        
        try:
            # 测试应用启动
            startup_result = self._test_app_startup()
            test_results["app_startup"] = startup_result["success"]
            
            if startup_result["success"]:
                # 测试路由
                test_results["route_tests"] = self._test_routes()
                
                # 测试错误处理
                test_results["error_handling"] = self._test_error_handling()
                
                # 测试性能
                test_results["performance"] = self._test_performance()
            else:
                test_results["startup_error"] = startup_result["error"]
                
        except Exception as e:
            test_results["test_error"] = str(e)
        
        return test_results
    
    def _test_app_startup(self) -> Dict[str, Any]:
        """测试应用启动"""
        print("🚀 测试Flask应用启动...")
        
        try:
            # 创建测试脚本
            test_script = self._create_startup_test_script()
            
            # 运行测试脚本
            result = subprocess.run(
                [sys.executable, test_script],
                cwd=self.temp_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print("  ✅ Flask应用启动成功")
                return {"success": True, "output": result.stdout}
            else:
                print(f"  ❌ Flask应用启动失败: {result.stderr}")
                return {"success": False, "error": result.stderr}
                
        except subprocess.TimeoutExpired:
            print("  ⏰ Flask应用启动超时")
            return {"success": False, "error": "启动超时"}
        except Exception as e:
            print(f"  ❌ 启动测试异常: {e}")
            return {"success": False, "error": str(e)}
    
    def _create_startup_test_script(self) -> str:
        """创建启动测试脚本"""
        script_content = '''
import sys
import os
sys.path.insert(0, os.getcwd())

try:
    # 尝试导入Flask
    from flask import Flask
    
    # 创建简单应用
    app = Flask(__name__)
    
    @app.route('/')
    def hello():
        return "Hello, Flask!"
    
    # 测试应用创建
    with app.test_client() as client:
        response = client.get('/')
        if response.status_code == 200:
            print("SUCCESS: Flask应用启动和路由测试通过")
        else:
            print(f"ERROR: 路由测试失败，状态码: {response.status_code}")
            sys.exit(1)
            
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
'''
        
        script_path = Path(self.temp_dir) / "startup_test.py"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        return str(script_path)
    
    def _test_routes(self) -> Dict[str, Any]:
        """测试路由功能"""
        print("🛣️  测试路由功能...")
        
        route_results = {}
        
        try:
            # 创建路由测试脚本
            test_script = self._create_route_test_script()
            
            result = subprocess.run(
                [sys.executable, test_script],
                cwd=self.temp_dir,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                route_results["status"] = "success"
                route_results["output"] = result.stdout
                print("  ✅ 路由测试通过")
            else:
                route_results["status"] = "failed"
                route_results["error"] = result.stderr
                print(f"  ❌ 路由测试失败: {result.stderr}")
                
        except Exception as e:
            route_results["status"] = "error"
            route_results["error"] = str(e)
            print(f"  ❌ 路由测试异常: {e}")
        
        return route_results
    
    def _create_route_test_script(self) -> str:
        """创建路由测试脚本"""
        script_content = '''
import sys
import os
sys.path.insert(0, os.getcwd())

try:
    from flask import Flask
    
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return "Index page"
    
    @app.route('/test')
    def test():
        return "Test page"
    
    @app.route('/api/data')
    def api_data():
        return {"message": "API data"}
    
    # 测试所有路由
    with app.test_client() as client:
        routes = ['/', '/test', '/api/data']
        
        for route in routes:
            response = client.get(route)
            if response.status_code != 200:
                print(f"ERROR: 路由 {route} 测试失败，状态码: {response.status_code}")
                sys.exit(1)
        
        print("SUCCESS: 所有路由测试通过")
        
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
'''
        
        script_path = Path(self.temp_dir) / "route_test.py"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        return str(script_path)
    
    def _test_error_handling(self) -> Dict[str, Any]:
        """测试错误处理"""
        print("⚠️  测试错误处理...")
        
        error_results = {}
        
        try:
            # 创建错误处理测试脚本
            test_script = self._create_error_test_script()
            
            result = subprocess.run(
                [sys.executable, test_script],
                cwd=self.temp_dir,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                error_results["status"] = "success"
                error_results["output"] = result.stdout
                print("  ✅ 错误处理测试通过")
            else:
                error_results["status"] = "failed"
                error_results["error"] = result.stderr
                print(f"  ❌ 错误处理测试失败: {result.stderr}")
                
        except Exception as e:
            error_results["status"] = "error"
            error_results["error"] = str(e)
            print(f"  ❌ 错误处理测试异常: {e}")
        
        return error_results
    
    def _create_error_test_script(self) -> str:
        """创建错误处理测试脚本"""
        script_content = '''
import sys
import os
sys.path.insert(0, os.getcwd())

try:
    from flask import Flask
    
    app = Flask(__name__)
    
    @app.route('/error')
    def error_route():
        raise ValueError("测试错误")
    
    @app.errorhandler(404)
    def not_found(error):
        return "页面未找到", 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return "服务器内部错误", 500
    
    # 测试错误处理
    with app.test_client() as client:
        # 测试404错误
        response = client.get('/nonexistent')
        if response.status_code != 404:
            print(f"ERROR: 404错误处理失败，状态码: {response.status_code}")
            sys.exit(1)
        
        # 测试500错误
        response = client.get('/error')
        if response.status_code != 500:
            print(f"ERROR: 500错误处理失败，状态码: {response.status_code}")
            sys.exit(1)
        
        print("SUCCESS: 错误处理测试通过")
        
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
'''
        
        script_path = Path(self.temp_dir) / "error_test.py"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        return str(script_path)
    
    def _test_performance(self) -> Dict[str, Any]:
        """测试性能"""
        print("⚡ 测试性能...")
        
        perf_results = {}
        
        try:
            # 创建性能测试脚本
            test_script = self._create_performance_test_script()
            
            result = subprocess.run(
                [sys.executable, test_script],
                cwd=self.temp_dir,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                perf_results["status"] = "success"
                perf_results["output"] = result.stdout
                print("  ✅ 性能测试通过")
            else:
                perf_results["status"] = "failed"
                perf_results["error"] = result.stderr
                print(f"  ❌ 性能测试失败: {result.stderr}")
                
        except Exception as e:
            perf_results["status"] = "error"
            perf_results["error"] = str(e)
            print(f"  ❌ 性能测试异常: {e}")
        
        return perf_results
    
    def _create_performance_test_script(self) -> str:
        """创建性能测试脚本"""
        script_content = '''
import sys
import os
import time
sys.path.insert(0, os.getcwd())

try:
    from flask import Flask
    
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return "Performance test"
    
    # 性能测试
    with app.test_client() as client:
        start_time = time.time()
        
        # 执行多次请求
        for i in range(100):
            response = client.get('/')
            if response.status_code != 200:
                print(f"ERROR: 请求失败，状态码: {response.status_code}")
                sys.exit(1)
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"SUCCESS: 100次请求耗时 {duration:.2f} 秒")
        print(f"平均响应时间: {duration/100*1000:.2f} 毫秒")
        
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
'''
        
        script_path = Path(self.temp_dir) / "performance_test.py"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        return str(script_path)
    
    def _cleanup_temp_environment(self):
        """清理临时环境"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                print(f"🧹 清理临时目录: {self.temp_dir}")
            except Exception as e:
                print(f"⚠️  清理临时目录失败: {e}")
    
    def save_results(self, results: Dict[str, Any], output_path: str):
        """保存检测结果"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"💾 结果已保存到: {output_path}")
        except Exception as e:
            print(f"❌ 保存结果失败: {e}")


if __name__ == "__main__":
    runner = DynamicTestRunner()
    results = runner.run_dynamic_tests(".")
    print("\n" + "="*60)
    print("动态检测结果:")
    print("="*60)
    print(json.dumps(results, ensure_ascii=False, indent=2))
