#!/usr/bin/env python3
"""
Flask 2.0.0 框架问题检测测试
专门用于检测文档中定义的S类和A类问题
"""

import sys
import os
from pathlib import Path
import decimal
from typing import Callable, Any, Optional, Union, List, Dict
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
        import flask
        print(f"🔍 当前Flask版本: {flask.__version__}")
        return flask.__version__
    except ImportError as e:
        print(f"⚠️  Flask导入失败: {e}")
        return "unknown"

# ===== S类问题（静态可检）- 8个 =====
# 这些是Flask框架本身的类型注解和API设计问题

def test_s_class_framework_issues():
    """测试S类问题 - Flask框架类型注解问题"""
    print("\n🔍 测试S类问题（Flask框架类型注解问题）...")
    
    try:
        from flask import Flask, Blueprint, jsonify, send_file, send_from_directory, g, request
        from flask.cli import FlaskGroup
        from flask.helpers import get_send_file_max_age
        from flask.typing import ResponseReturnValue
        
        # Issue #4024: 顶层导出名类型检查可见性
        print("  - #4024: 顶层导出名类型检查可见性")
        # 在Flask 2.0.0中，顶层导出名的类型检查有问题
        # 类型检查器无法正确识别这些导出
        flask_exports = [
            Flask, Blueprint, jsonify, send_file, send_from_directory, 
            g, request, FlaskGroup, get_send_file_max_age
        ]
        print(f"    Flask导出数量: {len(flask_exports)}")
        
        # Issue #4020: g对象类型提示
        print("  - #4020: g对象类型提示")
        # 在Flask 2.0.0中，g对象的类型提示有问题
        # 类型检查器无法识别g对象的属性访问
        def test_g_object_typing():
            # 这些操作在2.0.0中类型检查会报错
            g.user_id = 123  # 类型检查器会报错
            g.session_data = {"key": "value"}  # 类型检查器会报错
            g.request_id = "req_123"  # 类型检查器会报错
            return g.user_id, g.session_data, g.request_id
        
        # Issue #4044, #4026: send_file类型改进
        print("  - #4044, #4026: send_file类型改进")
        # 在Flask 2.0.0中，send_file的类型注解有问题
        def test_send_file_typing():
            # 这些调用在2.0.0中类型检查会报错
            return send_file("test.txt")  # 类型注解有问题
            # return send_file("test.txt", mimetype="text/plain")  # 类型注解有问题
            # return send_file("test.txt", as_attachment=True)  # 类型注解有问题
        
        # Issue #4040: 早期Python类型修正
        print("  - #4040: 早期Python类型修正")
        # 在Flask 2.0.0中，某些类型在早期Python版本上不可用
        def test_early_python_typing():
            # 这些类型在早期Python版本上可能不可用
            return Union[str, int]  # 可能有问题
            # return Optional[Dict[str, Any]]  # 可能有问题
            # return List[Callable]  # 可能有问题
        
        # Issue #4295: errorhandler类型注解
        print("  - #4295: errorhandler类型注解")
        # 在Flask 2.0.0中，errorhandler的类型注解有问题
        def test_errorhandler_typing():
            app = Flask(__name__)
            
            @app.errorhandler(404)
            def handle_404(error):  # 类型注解有问题
                return jsonify({"error": "Not found"}), 404
            
            @app.errorhandler(500)
            def handle_500(error):  # 类型注解有问题
                return jsonify({"error": "Internal error"}), 500
            
            return app
        
        # Issue #4041: 蓝图命名约束
        print("  - #4041: 蓝图命名约束")
        # 在Flask 2.0.0中，允许不安全的蓝图命名
        def test_blueprint_naming_constraints():
            # 这些命名在2.0.0中是允许的，但应该被禁止
            unsafe_names = [
                "unsafe-name-with-dashes",
                "name.with.dots",
                "name with spaces",
                "name@with@special@chars"
            ]
            
            blueprints = []
            for name in unsafe_names:
                try:
                    bp = Blueprint(name, __name__)
                    blueprints.append(bp)
                except Exception as e:
                    print(f"    蓝图命名 '{name}' 创建失败: {e}")
            
            return blueprints
        
        # Issue #4037: 蓝图URL前缀合并
        print("  - #4037: 蓝图URL前缀合并")
        # 在Flask 2.0.0中，蓝图URL前缀合并有问题
        def test_blueprint_url_prefix_merging():
            # 创建嵌套蓝图，测试前缀合并
            parent_bp = Blueprint("parent", __name__, url_prefix="/api")
            child_bp = Blueprint("child", __name__, url_prefix="/v1")
            
            @child_bp.route("/test")
            def child_route():
                return "child route"
            
            # 在2.0.0中，前缀合并有问题
            parent_bp.register_blueprint(child_bp)
            
            return parent_bp
        
        # Issue #4026: send_file类型改进（补充）
        print("  - #4026: send_file类型改进（补充）")
        # 在Flask 2.0.0中，send_file的类型注解有问题
        def test_send_file_additional_typing():
            # 这些调用在2.0.0中类型检查会报错
            return send_file("test.txt", download_name="download.txt")  # 类型注解有问题
            # return send_file("test.txt", mimetype="application/octet-stream")  # 类型注解有问题
        
        print("✅ S类问题测试完成")
        
    except ImportError as e:
        print(f"❌ S类问题测试失败，缺少Flask: {e}")
        print("   请安装: pip install flask")

# ===== A类问题（AI辅助）- 18个 =====
# 这些是Flask框架的功能行为问题

def test_a_class_framework_issues():
    """测试A类问题 - Flask框架功能行为问题"""
    print("\n🔍 测试A类问题（Flask框架功能行为问题）...")
    
    try:
        from flask import Flask, Blueprint, jsonify, send_file, send_from_directory, g, request
        from flask.cli import FlaskGroup
        from flask.config import Config
        from flask.helpers import get_send_file_max_age
        from flask.typing import ResponseReturnValue
        
        # Issue #4019: send_from_directory参数问题
        print("  - #4019: send_from_directory参数问题")
        # 在Flask 2.0.0中，send_from_directory的参数有问题
        def test_send_from_directory_params():
            # 在2.0.0中，filename参数被重命名为path，但旧参数名仍可用
            # 这会导致API不一致
            return send_from_directory("/tmp", "test.txt", filename="old_name.txt")  # 参数问题
        
        # Issue #4078: Config.from_json回退恢复
        print("  - #4078: Config.from_json回退恢复")
        # 在Flask 2.0.0中，Config.from_json方法被误删
        def test_config_from_json():
            config = Config()
            # 在2.0.0中，这个方法不存在，但应该存在
            try:
                result = config.from_json("config.json")
                return result
            except AttributeError:
                print("    Config.from_json方法不存在（2.0.0问题）")
                return None
        
        # Issue #4060: 装饰器工厂类型
        print("  - #4060: 装饰器工厂类型")
        # 在Flask 2.0.0中，装饰器工厂的类型有问题
        def test_decorator_factory_typing():
            def decorator_factory(param: str):
                def decorator(func: Callable) -> Callable:
                    @functools.wraps(func)
                    def wrapper(*args, **kwargs):
                        return func(*args, **kwargs)
                    return wrapper
                return decorator
            
            # 在2.0.0中，装饰器工厂的类型检查有问题
            @decorator_factory("test")
            def test_function():
                return "test"
            
            return test_function
        
        # Issue #4069: 嵌套蓝图注册
        print("  - #4069: 嵌套蓝图注册")
        # 在Flask 2.0.0中，嵌套蓝图的注册有问题
        def test_nested_blueprint_registration():
            app = Flask(__name__)
            parent = Blueprint("parent", __name__)
            child = Blueprint("child", __name__)
            
            @child.route("/test")
            def child_route():
                return "child"
            
            # 在2.0.0中，嵌套注册会导致端点命名冲突
            parent.register_blueprint(child)
            app.register_blueprint(parent)
            
            return app
        
        # Issue #1091: 蓝图重复注册
        print("  - #1091: 蓝图重复注册")
        # 在Flask 2.0.0中，重复注册同名蓝图会导致端点被覆盖
        def test_duplicate_blueprint_registration():
            app = Flask(__name__)
            bp1 = Blueprint("test", __name__)
            bp2 = Blueprint("test", __name__)
            
            @bp1.route("/route1")
            def route1():
                return "route1"
            
            @bp2.route("/route2")
            def route2():
                return "route2"
            
            # 在2.0.0中，重复注册会导致端点被覆盖
            app.register_blueprint(bp1)
            app.register_blueprint(bp2)
            
            return app
        
        # Issue #4093: teardown方法类型
        print("  - #4093: teardown方法类型")
        # 在Flask 2.0.0中，teardown方法的类型注解有问题
        def test_teardown_method_typing():
            app = Flask(__name__)
            
            @app.teardown_appcontext
            def teardown_handler(error):  # 类型注解有问题
                pass
            
            @app.teardown_request
            def teardown_request_handler(error):  # 类型注解有问题
                pass
            
            return app
        
        # Issue #4104: before_request类型
        print("  - #4104: before_request类型")
        # 在Flask 2.0.0中，before_request的类型注解有问题
        def test_before_request_typing():
            app = Flask(__name__)
            
            @app.before_request
            def before_request_handler():  # 类型注解有问题
                pass
            
            @app.before_app_request
            def before_app_request_handler():  # 类型注解有问题
                pass
            
            return app
        
        # Issue #4098: 模板全局装饰器
        print("  - #4098: 模板全局装饰器")
        # 在Flask 2.0.0中，模板全局装饰器的类型约束有问题
        def test_template_global_decorator():
            app = Flask(__name__)
            
            @app.template_global()
            def template_global_func():  # 类型约束有问题
                return "global"
            
            @app.template_global()
            def template_global_func_with_params(param):  # 类型约束有问题
                return f"global with {param}"
            
            return app
        
        # Issue #4095: errorhandler类型增强
        print("  - #4095: errorhandler类型增强")
        # 在Flask 2.0.0中，errorhandler的类型增强有问题
        def test_errorhandler_type_enhancement():
            app = Flask(__name__)
            
            @app.errorhandler(404)
            def handle_404(error):  # 类型增强有问题
                return "Not found", 404
            
            @app.errorhandler(500)
            def handle_500(error):  # 类型增强有问题
                return "Internal error", 500
            
            return app
        
        # Issue #4124: 蓝图重复注册处理
        print("  - #4124: 蓝图重复注册处理")
        # 在Flask 2.0.0中，同一蓝图注册两次会导致路由表异常
        def test_blueprint_double_registration():
            app = Flask(__name__)
            bp = Blueprint("test", __name__)
            
            @bp.route("/test")
            def test_route():
                return "test"
            
            # 在2.0.0中，同一蓝图注册两次会导致路由表异常
            app.register_blueprint(bp, name="first")
            app.register_blueprint(bp, name="second")
            
            return app
        
        # Issue #4150: static_folder PathLike
        print("  - #4150: static_folder PathLike")
        # 在Flask 2.0.0中，static_folder不接受PathLike对象
        def test_static_folder_pathlike():
            static_path = Path("/tmp/static")
            # 在2.0.0中，static_folder不接受PathLike对象
            app = Flask(__name__, static_folder=static_path)
            return app
        
        # Issue #4157: jsonify Decimal处理
        print("  - #4157: jsonify Decimal处理")
        # 在Flask 2.0.0中，jsonify无法正确处理Decimal
        def test_jsonify_decimal_handling():
            data = {
                "price": decimal.Decimal("19.99"),
                "quantity": decimal.Decimal("2.5"),
                "total": decimal.Decimal("49.975")
            }
            # 在2.0.0中，jsonify无法正确处理Decimal
            return jsonify(data)
        
        # Issue #4096: CLI懒加载错误
        print("  - #4096: CLI懒加载错误")
        # 在Flask 2.0.0中，CLI懒加载时的错误处理有问题
        def test_cli_lazy_loading_error():
            def create_app():
                app = Flask(__name__)
                @app.route("/")
                def index():
                    return "Hello"
                return app
            
            # 在2.0.0中，CLI懒加载时的错误处理有问题
            cli = FlaskGroup(create_app=create_app)
            return cli
        
        # Issue #4170: CLI loader kwargs
        print("  - #4170: CLI loader kwargs")
        # 在Flask 2.0.0中，CLI loader不支持带关键字参数的create_app
        def test_cli_loader_kwargs():
            def create_app(**kwargs):
                app = Flask(__name__)
                app.config.update(kwargs)
                return app
            
            # 在2.0.0中，CLI loader不支持带关键字参数的create_app
            cli = FlaskGroup(create_app=create_app)
            return cli
        
        # Issue #4053: URL匹配顺序
        print("  - #4053: URL匹配顺序")
        # 在Flask 2.0.0中，URL匹配顺序有问题
        def test_url_matching_order():
            app = Flask(__name__)
            
            @app.route("/user/<int:user_id>")
            def get_user_by_id(user_id):
                return f"User ID: {user_id}"
            
            @app.route("/user/<string:username>")
            def get_user_by_name(username):
                return f"Username: {username}"
            
            # 在2.0.0中，URL匹配顺序有问题
            return app
        
        # Issue #4112: 异步视图支持
        print("  - #4112: 异步视图支持")
        # 在Flask 2.0.0中，异步视图的支持有问题
        def test_async_view_support():
            app = Flask(__name__)
            
            @app.route("/async")
            async def async_route():  # 在2.0.0中，异步视图支持有问题
                return "async response"
            
            return app
        
        # Issue #4229: 回调顺序
        print("  - #4229: 回调顺序")
        # 在Flask 2.0.0中，回调顺序有问题
        def test_callback_order():
            app = Flask(__name__)
            
            @app.before_request
            def before_request_1():
                g.order = []
                g.order.append("before_1")
            
            @app.before_request
            def before_request_2():
                g.order.append("before_2")
            
            @app.route("/callback-order")
            def callback_order_route():
                return f"Order: {g.order}"
            
            # 在2.0.0中，回调顺序有问题
            return app
        
        # Issue #4333: 上下文边界
        print("  - #4333: 上下文边界")
        # 在Flask 2.0.0中，after_this_request的上下文有问题
        def test_after_request_context():
            app = Flask(__name__)
            
            @app.route("/after-request")
            def after_request_route():
                from flask import after_this_request
                
                def cleanup():
                    pass
                
                # 在2.0.0中，after_this_request的上下文有问题
                after_this_request(cleanup)
                return "after request"
            
            return app
        
        print("✅ A类问题测试完成")
        
    except ImportError as e:
        print(f"❌ A类问题测试失败，缺少Flask: {e}")
        print("   请安装: pip install flask")

def run_framework_issue_tests():
    """运行Flask框架问题测试"""
    print("🚀 开始Flask 2.0.0框架问题检测测试...")
    print("="*70)
    
    # 验证Flask版本
    version = test_flask_version()
    if not version.startswith("2.0.0"):
        print(f"⚠️  警告: 当前Flask版本为 {version}，不是2.0.0")
    
    # 运行框架问题测试
    test_s_class_framework_issues()
    test_a_class_framework_issues()
    
    print("\n🎉 Flask框架问题测试完成！")
    print("💡 这些代码专门用于检测Flask框架本身的S类和A类问题")
    print("💡 请使用类型检查器（mypy/pyright）和静态分析工具检测")

if __name__ == "__main__":
    run_framework_issue_tests()


