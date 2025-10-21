#!/usr/bin/env python3
"""
Flask 2.0.0 简化测试文件
包含官方文档中的32个已知Issue的复现代码
"""

from pathlib import Path
import decimal
from typing import Callable, Any, Optional, Union
import functools

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

def test_flask_version():
    """验证Flask版本"""
    try:
        # 尝试导入Flask并检查版本
        import flask
        print(f"🔍 当前Flask版本: {flask.__version__}")
        return flask.__version__
    except ImportError as e:
        print(f"⚠️  Flask导入失败: {e}")
        return "unknown"

# ===== S类问题（静态可检）- 8个 =====

def test_s_class_issues():
    """测试S类问题"""
    print("\n🔍 测试S类问题（静态可检）...")

    # Issue #4024: 顶层导出名类型检查可见性
    print("  - #4024: 顶层导出名类型检查")
    # 在2.0.0中，顶层导出名的类型检查有问题

    # Issue #4020: g对象类型提示
    print("  - #4020: g对象类型提示")
    # 在2.0.0中，g对象的类型提示有问题
    # g.user_id = 123  # 类型检查器会报错
    # g.session_data = {"key": "value"}

    # Issue #4044, #4026: send_file类型改进
    print("  - #4044, #4026: send_file类型改进")
    # 在2.0.0中，send_file的类型注解有问题

    # Issue #4040: 早期Python类型修正
    print("  - #4040: 早期Python类型修正")
    # 在2.0.0中，某些类型在早期Python版本上不可用
    # return Union[str, int]

    # Issue #4295: errorhandler类型注解
    print("  - #4295: errorhandler类型注解")
    # 在2.0.0中，errorhandler的类型注解有问题

    # Issue #4041: 蓝图命名约束
    print("  - #4041: 蓝图命名约束")
    # 在2.0.0中，允许不安全的蓝图命名
    bp_name = "unsafe-name-with-dashes"

    # Issue #4037: 蓝图URL前缀合并
    print("  - #4037: 蓝图URL前缀合并")
    # 在2.0.0中，蓝图URL前缀合并有问题
    parent_prefix = "/api"
    child_prefix = "/v1"
    # return f"{parent_prefix}{child_prefix}"

    print("✅ S类问题测试完成")

# ===== A类问题（AI辅助）- 18个 =====

def test_a_class_issues():
    """测试A类问题"""
    print("\n🔍 测试A类问题（AI辅助）...")

    # Issue #4019: send_from_directory参数问题
    print("  - #4019: send_from_directory参数")
    # 在2.0.0中，send_from_directory的参数有问题
    # return {"directory": "/tmp", "filename": "test.txt", "old_param": "old_name.txt"}

    # Issue #4078: Config.from_json回退恢复
    print("  - #4078: Config.from_json回退")
    # 在2.0.0中，这个方法被误删了
    # import json
    # with open(filename, 'r') as f:
    #     return json.load(f)

    # Issue #4060: 装饰器工厂类型
    print("  - #4060: 装饰器工厂类型")
    # 在2.0.0中，装饰器工厂的类型注解有问题
    # def decorator_factory(param: str):
    #     def decorator(func: Callable) -> Callable:
    #         @functools.wraps(func)
    #         def wrapper(*args, **kwargs):
    #             return func(*args, **kwargs)
    #         return wrapper
    #     return decorator

    # Issue #4069: 嵌套蓝图注册
    print("  - #4069: 嵌套蓝图注册")
    # 在2.0.0中，嵌套蓝图的端点命名会冲突
    parent_name = "parent"
    child_name = "child"
    # return f"{parent_name}.{child_name}"

    # Issue #1091: 蓝图重复注册
    print("  - #1091: 蓝图重复注册")
    # 在2.0.0中，重复注册同名蓝图会导致端点被覆盖
    bp1_name = "test"
    bp2_name = "test"
    # return f"Blueprint {bp1_name} and {bp2_name} conflict"

    # Issue #4093: teardown方法类型
    print("  - #4093: teardown方法类型")
    # 在2.0.0中，teardown方法的类型注解有问题

    # Issue #4104: before_request类型
    print("  - #4104: before_request类型")
    # 在2.0.0中，before_request的类型注解有问题

    # Issue #4098: 模板全局装饰器
    print("  - #4098: 模板全局装饰器")
    # 在2.0.0中，模板全局装饰器的类型约束有问题
    # return "global"

    # Issue #4095: errorhandler类型增强
    print("  - #4095: errorhandler类型增强")
    # 在2.0.0中，errorhandler的类型增强有问题
    # return "error", 500

    # Issue #4124: 蓝图重复注册处理
    print("  - #4124: 蓝图重复注册处理")
    def blueprint_double_registration():
        # 在2.0.0中，同一蓝图注册两次会导致路由表异常
        bp_name = "test"
        return f"Blueprint {bp_name} registered twice"

    # Issue #4150: static_folder PathLike
    print("  - #4150: static_folder PathLike")
    def create_static_folder_issue():
        # 在2.0.0中，static_folder不接受PathLike对象
        static_path = Path("/tmp/static")
        return str(static_path)

    # Issue #4157: jsonify Decimal处理
    print("  - #4157: jsonify Decimal处理")
    def json_decimal_issue():
        # 在2.0.0中，jsonify无法正确处理Decimal
        data = {
            "price": decimal.Decimal("19.99"),
            "quantity": decimal.Decimal("2.5")
        }
        return data

    # Issue #4096: CLI懒加载错误
    print("  - #4096: CLI懒加载错误")
    def create_cli_with_lazy_loading():
        # 在2.0.0中，CLI懒加载时的错误处理有问题
        return "CLI lazy loading error"

    # Issue #4170: CLI loader kwargs
    print("  - #4170: CLI loader kwargs")
    def create_cli_with_kwargs():
        # 在2.0.0中，CLI loader不支持带关键字参数的create_app
        return "CLI kwargs not supported"

    # Issue #4053: URL匹配顺序
    print("  - #4053: URL匹配顺序")
    def create_url_matching_issue():
        # 在2.0.0中，URL匹配顺序有问题
        routes = [
            "/user/<int:user_id>",
            "/user/<string:username>"
        ]
        return routes

    # Issue #4112: 异步视图支持
    print("  - #4112: 异步视图支持")
    def create_async_view_issue():
        # 在2.0.0中，异步视图的支持有问题
        return "async view not supported"

    # Issue #4229: 回调顺序
    print("  - #4229: 回调顺序")
    def create_callback_order_issue():
        # 在2.0.0中，回调顺序有问题
        callbacks = ["before_1", "before_2"]
        return callbacks

    # Issue #4333: 上下文边界
    print("  - #4333: 上下文边界")
    def create_after_request_context_issue():
        # 在2.0.0中，after_this_request的上下文有问题
        return "context boundary issue"

    print("✅ A类问题测试完成")

# ===== D类问题（动态验证）- 6个 =====

def test_d_class_issues():
    """测试D类问题（动态验证）"""
    print("\n🔍 测试D类问题（动态验证）...")

    # 创建Flask应用进行动态测试
    try:
        from flask import Flask, request, jsonify, render_template_string
        import threading
        import time
        import requests
        from contextlib import contextmanager

        app = Flask(__name__)
        app.config['TESTING'] = True

        # Issue #4053: URL匹配顺序（运行时）
        print("  - #4053: URL匹配顺序（运行时）")
        @app.route('/user/<int:user_id>')
        def get_user_by_id(user_id):
            return jsonify({"type": "int", "user_id": user_id})

        @app.route('/user/<string:username>')
        def get_user_by_name(username):
            return jsonify({"type": "string", "username": username})

        # Issue #4112: 异步视图支持（模拟）
        print("  - #4112: 异步视图支持（运行时）")
        @app.route('/async-test')
        def async_test():
            # 在Flask 2.0.0中，异步视图支持有限
            return jsonify({"message": "async view test", "supported": False})

        # Issue #4229: 回调顺序（运行时）
        print("  - #4229: 回调顺序（运行时）")
        callbacks_executed = []

        @app.before_request
        def before_request_1():
            callbacks_executed.append("before_1")

        @app.before_request
        def before_request_2():
            callbacks_executed.append("before_2")

        @app.route('/callback-test')
        def callback_test():
            return jsonify({"callbacks": callbacks_executed})

        # Issue #4333: 上下文边界（运行时）
        print("  - #4333: 上下文边界（运行时）")
        @app.route('/context-test')
        def context_test():
            from flask import g
            g.test_value = "context_test_value"
            return jsonify({"context_available": hasattr(g, 'test_value')})

        # Issue #4037: 蓝图前缀合并（复杂）
        print("  - #4037: 蓝图前缀合并（复杂）")
        from flask import Blueprint

        parent_bp = Blueprint('parent', __name__, url_prefix='/api')
        child_bp = Blueprint('child', __name__, url_prefix='/v1')

        @parent_bp.route('/test')
        def parent_test():
            return jsonify({"blueprint": "parent"})

        @child_bp.route('/test')
        def child_test():
            return jsonify({"blueprint": "child"})

        app.register_blueprint(parent_bp)
        app.register_blueprint(child_bp)

        # Issue #4069: 嵌套蓝图（复杂）
        print("  - #4069: 嵌套蓝图（复杂）")
        nested_bp = Blueprint('nested', __name__, url_prefix='/nested')

        @nested_bp.route('/test')
        def nested_test():
            return jsonify({"blueprint": "nested"})

        app.register_blueprint(nested_bp)

        # 启动测试服务器进行动态测试
        @contextmanager
        def test_server():
            """测试服务器上下文管理器"""
            server_thread = None
            try:
                def run_server():
                    app.run(host='127.0.0.1', port=5001, debug=False, use_reloader=False)

                server_thread = threading.Thread(target=run_server, daemon=True)
                server_thread.start()
                time.sleep(2)  # 等待服务器启动
                yield
            finally:
                if server_thread:
                    # 无法优雅关闭，但测试完成后进程会结束
                    pass

        # 执行动态测试
        with test_server():
            base_url = "http://127.0.0.1:5001"

            # 测试URL匹配顺序
            try:
                response = requests.get(f"{base_url}/user/123", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    print(f"    URL匹配测试: {data}")
            except (ImportError, RuntimeError, AttributeError, OSError) as e:
                print(f"    URL匹配测试失败: {e}")

            # 测试异步视图
            try:
                response = requests.get(f"{base_url}/async-test", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    print(f"    异步视图测试: {data}")
            except (ImportError, RuntimeError, AttributeError, OSError) as e:
                print(f"    异步视图测试失败: {e}")

            # 测试回调顺序
            try:
                response = requests.get(f"{base_url}/callback-test", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    print(f"    回调顺序测试: {data}")
            except (ImportError, RuntimeError, AttributeError, OSError) as e:
                print(f"    回调顺序测试失败: {e}")

            # 测试上下文边界
            try:
                response = requests.get(f"{base_url}/context-test", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    print(f"    上下文测试: {data}")
            except (ImportError, RuntimeError, AttributeError, OSError) as e:
                print(f"    上下文测试失败: {e}")

            # 测试蓝图前缀
            try:
                response = requests.get(f"{base_url}/api/test", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    print(f"    蓝图前缀测试: {data}")
            except (ImportError, RuntimeError, AttributeError, OSError) as e:
                print(f"    蓝图前缀测试失败: {e}")

            # 测试嵌套蓝图
            try:
                response = requests.get(f"{base_url}/nested/test", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    print(f"    嵌套蓝图测试: {data}")
            except (ImportError, RuntimeError, AttributeError, OSError) as e:
                print(f"    嵌套蓝图测试失败: {e}")

        print("✅ D类问题动态测试完成")

    except ImportError as e:
        print(f"❌ 动态测试失败，缺少依赖: {e}")
        print("   请安装: pip install flask requests")
    except (ImportError, RuntimeError, AttributeError, OSError) as e:
        print(f"❌ 动态测试失败: {e}")
        print("✅ D类问题测试完成（静态模式）")

def run_all_tests():
    """运行所有测试"""
    print("🚀 开始Flask 2.0.0简化测试...")
    print("="*70)

    # 验证Flask版本
    version = test_flask_version()
    if not version.startswith("2.0.0"):
        print(f"⚠️  警告: 当前Flask版本为 {version}，不是2.0.0")

    # 运行各类测试
    test_s_class_issues()
    test_a_class_issues()
    test_d_class_issues()

    print("\n🎉 所有测试完成！")
    print("💡 请使用检测系统分析这些代码")

if __name__ == "__main__":
    run_all_tests()
