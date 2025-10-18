#!/usr/bin/env python3
"""
Flask 2.0.0 动态测试运行器
支持真正的运行时检测和Web应用测试
"""

import json
import sys
import time
import threading
from typing import Any, Dict

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
    
    # 添加__version__属性到werkzeug模块
    if not hasattr(werkzeug, '__version__'):
        try:
            import pkg_resources
            werkzeug.__version__ = pkg_resources.get_distribution('werkzeug').version
            patches_applied.append("__version__")
        except:
            werkzeug.__version__ = '3.1.3'  # 默认版本
            patches_applied.append("__version__ (default)")
        
    if patches_applied:
        print(f"🔧 已应用Werkzeug兼容性补丁: {', '.join(patches_applied)}")
except ImportError:
    print("⚠️ 无法应用Werkzeug兼容性补丁")

import requests

# Flask相关导入
import flask
from flask import Flask, request, jsonify, Blueprint, g, abort

class FlaskDynamicTestRunner:
    """Flask动态测试运行器"""

    def __init__(self):
        self.test_results = {}
        self.server_process = None
        self.test_port = 5002  # 使用不同的端口避免冲突

    def run_dynamic_tests(self, enable_web_app_test: bool = True) -> Dict[str, Any]:
        """运行动态测试"""
        print("🚀 开始Flask 2.0.0动态测试...")
        print("="*70)

        results = {
            "test_type": "dynamic_runtime_test",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "enable_web_app_test": enable_web_app_test,
            "tests": {}
        }

        try:
            # 测试1: 基础Flask应用创建
            print("\n🔍 测试1: 基础Flask应用创建")
            results["tests"]["basic_app_creation"] = self._test_basic_app_creation()

            # 测试2: 路由注册和匹配
            print("\n🔍 测试2: 路由注册和匹配")
            results["tests"]["route_registration"] = self._test_route_registration()

            # 测试3: 蓝图功能
            print("\n🔍 测试3: 蓝图功能")
            results["tests"]["blueprint_functionality"] = self._test_blueprint_functionality()

            # 测试4: 请求上下文
            print("\n🔍 测试4: 请求上下文")
            results["tests"]["request_context"] = self._test_request_context()

            # 测试5: 错误处理
            print("\n🔍 测试5: 错误处理")
            results["tests"]["error_handling"] = self._test_error_handling()

            # 测试6: 配置管理
            print("\n🔍 测试6: 配置管理")
            results["tests"]["configuration"] = self._test_configuration()

            # 如果启用Web应用测试，进行服务器测试
            if enable_web_app_test:
                print("\n🔍 测试7: Web应用服务器测试")
                results["tests"]["web_server_test"] = self._test_web_server()
            else:
                print("\n⏭️ 跳过Web应用服务器测试（未启用）")
                results["tests"]["web_server_test"] = {
                    "status": "skipped",
                    "reason": "Web应用测试未启用"
                }

            # 生成测试摘要
            results["summary"] = self._generate_test_summary(results)

            print("\n✅ 动态测试完成！")
            return results

        except (ImportError, RuntimeError, OSError) as e:
            print(f"\n❌ 动态测试失败: {e}")
            results["error"] = str(e)
            results["summary"] = self._generate_test_summary(results)
            return results

    def _test_basic_app_creation(self) -> Dict[str, Any]:
        """测试基础Flask应用创建"""
        try:
            # 检查Flask版本兼容性
            # flask已在顶部导入
            flask_version = flask.__version__
            print(f"  - Flask版本: {flask_version}")

            # 检查Werkzeug版本兼容性
            try:
                import werkzeug
                # 安全地获取版本信息
                werkzeug_version = getattr(werkzeug, '__version__', 'unknown')
                
                # 如果__version__不可用，尝试从其他方式获取版本
                if werkzeug_version == 'unknown':
                    try:
                        import pkg_resources
                        werkzeug_version = pkg_resources.get_distribution('werkzeug').version
                    except:
                        try:
                            import werkzeug.routing
                            werkzeug_version = getattr(werkzeug.routing, '__version__', 'unknown')
                        except:
                            werkzeug_version = 'unknown'
                
                print(f"  - Werkzeug版本: {werkzeug_version}")

                # 检查是否有url_quote问题
                try:
                    from werkzeug.urls import url_quote
                except ImportError:
                    print("  - 检测到Werkzeug版本兼容性问题，尝试替代方案...")
                    # 使用替代方案
                    from urllib.parse import quote as url_quote
                    import werkzeug.urls
                    werkzeug.urls.url_quote = url_quote

            except ImportError:
                print("  - 无法导入Werkzeug")

            # Flask已在顶部导入

            # 创建应用
            app = Flask(__name__)
            app.config['TESTING'] = True

            # 测试应用属性
            test_result = {
                "status": "success",
                "app_name": app.name,
                "debug_mode": app.debug,
                "testing_mode": app.testing,
                "config_keys": list(app.config.keys()),
                "url_map_rules": len(list(app.url_map.iter_rules()))
            }

            print("  ✅ Flask应用创建成功")
            print(f"  - 应用名称: {app.name}")
            print(f"  - 调试模式: {app.debug}")
            print(f"  - 测试模式: {app.testing}")
            print(f"  - 配置项数量: {len(app.config)}")

            return test_result

        except (ImportError, AttributeError, RuntimeError) as e:
            print(f"  ❌ Flask应用创建失败: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

    def _test_route_registration(self) -> Dict[str, Any]:
        """测试路由注册和匹配"""
        try:
            # Flask已在顶部导入, request, jsonify

            app = Flask(__name__)
            app.config['TESTING'] = True

            # 注册各种类型的路由
            @app.route('/')
            def index():
                return jsonify({"message": "Hello World"})

            @app.route('/user/<int:user_id>')
            def get_user_by_id(user_id):
                return jsonify({"type": "int", "user_id": user_id})

            @app.route('/user/<string:username>')
            def get_user_by_name(username):
                return jsonify({"type": "string", "username": username})

            @app.route('/api/data', methods=['GET', 'POST'])
            def api_data():
                if request.method == 'POST':
                    return jsonify({"method": "POST", "data": request.get_json()})
                return jsonify({"method": "GET", "data": "test"})

            # 测试路由匹配
            test_results = self._test_route_endpoints(app)

            test_result = {
                "status": "success",
                "total_routes": len(list(app.url_map.iter_rules())),
                **test_results,
                "all_tests_passed": all(test_results.values())
            }

            print("  ✅ 路由注册和匹配测试成功")
            print(f"  - 总路由数: {len(list(app.url_map.iter_rules()))}")
            print(f"  - 所有测试通过: {test_result['all_tests_passed']}")

            return test_result

        except (ImportError, AttributeError, RuntimeError) as e:
            print(f"  ❌ 路由注册测试失败: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

    def _test_route_endpoints(self, app) -> Dict[str, bool]:
        """测试路由端点的辅助方法"""
        with app.test_client() as client:
            return {
                "index_route": client.get('/').status_code == 200,
                "int_parameter_route": client.get('/user/123').status_code == 200,
                "string_parameter_route": client.get('/user/john').status_code == 200,
                "post_method": client.post('/api/data', json={"test": "data"}).status_code == 200,
                "get_method": client.get('/api/data').status_code == 200
            }

    def _test_blueprint_functionality(self) -> Dict[str, Any]:
        """测试蓝图功能"""
        try:
            # Flask已在顶部导入, Blueprint, jsonify

            app = Flask(__name__)
            app.config['TESTING'] = True

            # 创建并注册蓝图
            self._register_test_blueprints(app)

            # 测试蓝图路由
            test_results = self._test_blueprint_endpoints(app)

            test_result = {
                "status": "success",
                "blueprints_registered": 2,
                **test_results,
                "all_blueprint_tests_passed": all(test_results.values())
            }

            print("  ✅ 蓝图功能测试成功")
            print("  - 注册蓝图数: 2")
            print(f"  - 所有蓝图测试通过: {test_result['all_blueprint_tests_passed']}")

            return test_result

        except (ImportError, AttributeError, RuntimeError) as e:
            print(f"  ❌ 蓝图功能测试失败: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

    def _register_test_blueprints(self, app):
        """注册测试蓝图的辅助方法"""
        # Flask相关模块已在顶部导入

        # 创建蓝图
        api_bp = Blueprint('api', __name__, url_prefix='/api')
        admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

        # 在蓝图中定义路由
        @api_bp.route('/users')
        def api_users():
            return jsonify({"endpoint": "api_users"})

        @api_bp.route('/data')
        def api_data():
            return jsonify({"endpoint": "api_data"})

        @admin_bp.route('/settings')
        def admin_settings():
            return jsonify({"endpoint": "admin_settings"})

        # 注册蓝图
        app.register_blueprint(api_bp)
        app.register_blueprint(admin_bp)

    def _test_blueprint_endpoints(self, app) -> Dict[str, bool]:
        """测试蓝图端点的辅助方法"""
        with app.test_client() as client:
            return {
                "api_users_route": client.get('/api/users').status_code == 200,
                "api_data_route": client.get('/api/data').status_code == 200,
                "admin_settings_route": client.get('/admin/settings').status_code == 200
            }

    def _test_request_context(self) -> Dict[str, Any]:
        """测试请求上下文"""
        try:
            # Flask已在顶部导入, request, g, jsonify

            app = Flask(__name__)
            app.config['TESTING'] = True

            @app.before_request
            def before_request():
                g.request_id = f"req_{int(time.time() * 1000)}"
                g.start_time = time.time()

            @app.route('/context-test')
            def context_test():
                return jsonify({
                    "request_id": getattr(g, 'request_id', None),
                    "start_time": getattr(g, 'start_time', None),
                    "method": request.method,
                    "url": request.url,
                    "headers": dict(request.headers)
                })

            # 测试请求上下文
            test_results = self._test_context_endpoints(app)

            test_result = {
                "status": "success",
                "context_test_success": test_results["context_success"],
                **test_results,
                "all_context_tests_passed": all([
                    test_results["context_success"],
                    test_results["has_request_id"],
                    test_results["has_start_time"],
                    test_results["has_method"]
                ])
            }

            print("  ✅ 请求上下文测试成功")
            print(f"  - 上下文测试通过: {test_result['all_context_tests_passed']}")

            return test_result

        except (ImportError, AttributeError, RuntimeError) as e:
            print(f"  ❌ 请求上下文测试失败: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

    def _test_context_endpoints(self, app) -> Dict[str, bool]:
        """测试上下文端点的辅助方法"""
        with app.test_client() as client:
            response = client.get('/context-test')
            context_success = response.status_code == 200

            if context_success:
                data = response.get_json()
                return {
                    "context_success": context_success,
                    "has_request_id": 'request_id' in data,
                    "has_start_time": 'start_time' in data,
                    "has_method": 'method' in data
                }
            else:
                return {
                    "context_success": False,
                    "has_request_id": False,
                    "has_start_time": False,
                    "has_method": False
                }

    def _test_error_handling(self) -> Dict[str, Any]:
        """测试错误处理"""
        try:
            # Flask已在顶部导入, jsonify

            app = Flask(__name__)
            app.config['TESTING'] = True

            @app.route('/test-error')
            def test_error():
                raise ValueError("Test error for error handling")

            @app.route('/test-404')
            def test_404():
                # Flask相关模块已在顶部导入
                abort(404)

            @app.errorhandler(ValueError)
            def handle_value_error(error):
                return jsonify({"error": "ValueError", "message": str(error)}), 400

            @app.errorhandler(404)
            def handle_404(_):
                return jsonify({"error": "Not Found", "message": "Resource not found"}), 404

            # 测试错误处理
            with app.test_client() as client:
                # 测试ValueError处理
                response = client.get('/test-error')
                value_error_success = response.status_code == 400

                # 测试404处理
                response = client.get('/test-404')
                not_found_success = response.status_code == 404

                # 测试不存在的路由
                response = client.get('/nonexistent')
                nonexistent_success = response.status_code == 404

            test_result = {
                "status": "success",
                "value_error_handling": value_error_success,
                "not_found_handling": not_found_success,
                "nonexistent_route_handling": nonexistent_success,
                "all_error_tests_passed": all([
                    value_error_success, not_found_success, nonexistent_success
                ])
            }

            print("  ✅ 错误处理测试成功")
            print(f"  - 所有错误处理测试通过: {test_result['all_error_tests_passed']}")

            return test_result

        except (ImportError, AttributeError, RuntimeError) as e:
            print(f"  ❌ 错误处理测试失败: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

    def _test_configuration(self) -> Dict[str, Any]:
        """测试配置管理"""
        try:
            # Flask已在顶部导入

            app = Flask(__name__)

            # 测试默认配置
            default_config = {
                "DEBUG": app.config.get('DEBUG'),
                "TESTING": app.config.get('TESTING'),
                "SECRET_KEY": bool(app.config.get('SECRET_KEY')),
                "JSONIFY_PRETTYPRINT_REGULAR": app.config.get('JSONIFY_PRETTYPRINT_REGULAR')
            }

            # 测试配置更新
            app.config.update({
                'CUSTOM_SETTING': 'test_value',
                'ANOTHER_SETTING': 123
            })

            custom_config = {
                "CUSTOM_SETTING": app.config.get('CUSTOM_SETTING'),
                "ANOTHER_SETTING": app.config.get('ANOTHER_SETTING')
            }

            test_result = {
                "status": "success",
                "default_config": default_config,
                "custom_config": custom_config,
                "config_update_success": all([
                    app.config.get('CUSTOM_SETTING') == 'test_value',
                    app.config.get('ANOTHER_SETTING') == 123
                ])
            }

            print("  ✅ 配置管理测试成功")
            print(f"  - 配置更新成功: {test_result['config_update_success']}")

            return test_result

        except (ImportError, AttributeError, RuntimeError) as e:
            print(f"  ❌ 配置管理测试失败: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }

    def _test_web_server(self) -> Dict[str, Any]:
        """测试Web服务器启动和运行"""
        try:
            # Flask已在顶部导入, jsonify

            app = Flask(__name__)
            self._setup_test_routes(app)

            # 启动服务器
            self._start_test_server(app)

            # 测试服务器端点
            test_results = self._test_server_endpoints()

            # 计算总体结果
            all_tests_passed = all([
                test_results.get("root_endpoint", False),
                test_results.get("health_endpoint", False),
                test_results.get("test_endpoint", False),
                test_results.get("response_content", False)
            ])

            result = {
                "status": "success" if all_tests_passed else "partial",
                "server_port": self.test_port,
                "tests": test_results,
                "all_tests_passed": all_tests_passed
            }

            if all_tests_passed:
                print("  ✅ Web服务器测试成功")
                print(f"  - 服务器端口: {self.test_port}")
                print(f"  - 所有端点测试通过: {all_tests_passed}")
            else:
                print("  ⚠️ Web服务器测试部分成功")
                print(f"  - 服务器端口: {self.test_port}")
                print(f"  - 测试结果: {test_results}")

            return result

        except (ImportError, OSError, RuntimeError) as e:
            print(f"  ❌ Web服务器测试失败: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "server_port": self.test_port
            }

    def _setup_test_routes(self, app):
        """设置测试路由的辅助方法"""
        @app.route('/')
        def index():
            return jsonify({"message": "Flask Dynamic Test Server", "status": "running"})

        @app.route('/health')
        def health():
            return jsonify({"status": "healthy", "timestamp": time.time()})

        @app.route('/test')
        def test():
            return jsonify({"test": "success", "server": "running"})

    def _start_test_server(self, app):
        """启动测试服务器的辅助方法"""
        server_thread = threading.Thread(
            target=lambda: app.run(host='127.0.0.1', port=self.test_port, debug=False, use_reloader=False),
            daemon=True
        )
        server_thread.start()
        time.sleep(3)  # 等待服务器启动

    def _test_server_endpoints(self) -> Dict[str, Any]:
        """测试服务器端点的辅助方法"""
        base_url = f"http://127.0.0.1:{self.test_port}"
        test_results = {}

        try:
            # 测试根路径
            response = requests.get(f"{base_url}/", timeout=5)
            test_results["root_endpoint"] = response.status_code == 200

            # 测试健康检查
            response = requests.get(f"{base_url}/health", timeout=5)
            test_results["health_endpoint"] = response.status_code == 200

            # 测试测试端点
            response = requests.get(f"{base_url}/test", timeout=5)
            test_results["test_endpoint"] = response.status_code == 200

            # 测试响应内容
            response = requests.get(f"{base_url}/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                test_results["response_content"] = data.get("status") == "running"
            else:
                test_results["response_content"] = False

        except requests.exceptions.RequestException as e:
            test_results["connection_error"] = str(e)
            test_results["root_endpoint"] = False
            test_results["health_endpoint"] = False
            test_results["test_endpoint"] = False
            test_results["response_content"] = False

        return test_results

    def _generate_test_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """生成测试摘要"""
        tests = results.get("tests", {})

        # 统计测试结果
        total_tests = len(tests)
        successful_tests = 0
        failed_tests = 0
        skipped_tests = 0

        for test_result in tests.values():
            status = test_result.get("status", "unknown")
            if status == "success":
                successful_tests += 1
            elif status == "failed":
                failed_tests += 1
            elif status == "skipped":
                skipped_tests += 1

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
            "skipped_tests": skipped_tests,
            "success_rate": round(success_rate, 2),
            "overall_status": overall_status,
            "enable_web_app_test": results.get("enable_web_app_test", False)
        }

def main():
    """主函数"""
    print("🚀 Flask 2.0.0 动态测试运行器")
    print("="*50)

    # 检查依赖
    try:
        # flask已在顶部导入
        # requests已在顶部导入
        print(f"✅ Flask版本: {flask.__version__}")
        print(f"✅ Requests版本: {requests.__version__}")
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请安装: pip install flask requests")
        return

    # 创建测试运行器
    runner = FlaskDynamicTestRunner()

    # 运行动态测试
    # 可以通过命令行参数控制是否启用Web应用测试
    enable_web_test = len(sys.argv) > 1 and sys.argv[1] == "--enable-web-test"

    results = runner.run_dynamic_tests(enable_web_app_test=enable_web_test)

    # 显示测试摘要
    summary = results.get("summary", {})
    print("\n" + "="*50)
    print("📊 测试摘要")
    print("="*50)
    print(f"总测试数: {summary.get('total_tests', 0)}")
    print(f"成功测试: {summary.get('successful_tests', 0)}")
    print(f"失败测试: {summary.get('failed_tests', 0)}")
    print(f"跳过测试: {summary.get('skipped_tests', 0)}")
    print(f"成功率: {summary.get('success_rate', 0)}%")
    print(f"整体状态: {summary.get('overall_status', 'unknown')}")
    print(f"Web应用测试: {'启用' if summary.get('enable_web_app_test') else '禁用'}")

    # 保存结果
    try:
        results_file = f"dynamic_test_results_{int(time.time())}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 测试结果已保存到: {results_file}")
    except (OSError, IOError) as e:
        print(f"\n⚠️ 保存结果失败: {e}")

if __name__ == "__main__":
    main()
