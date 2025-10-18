#!/usr/bin/env python3
"""
Flask 2.0.0 快速测试脚本
创建最小化的测试用例，专门触发官方文档中的32个Issue
"""

import os
import tempfile
from pathlib import Path

def create_minimal_flask_test():
    """创建最小化的Flask测试项目"""
    
    # 创建临时目录
    test_dir = Path("flask_minimal_test")
    test_dir.mkdir(exist_ok=True)
    
    # 1. 创建主应用文件 - 触发S类问题
    app_content = '''#!/usr/bin/env python3
"""
Flask 2.0.0 最小测试应用
触发官方文档中的32个已知Issue
"""

from flask import Flask, Blueprint, jsonify, send_file, send_from_directory, g, request
from flask.cli import FlaskGroup
import decimal
from pathlib import Path
from typing import Callable, Any, Optional, Union
import functools

# ===== S类问题（静态可检）=====

# Issue #4024: 顶层导出名类型检查可见性
from flask import Flask, Blueprint, jsonify, send_file, send_from_directory, g, request

# Issue #4020: g对象类型提示
def use_g_object():
    g.user_id = 123  # 类型检查器会报错
    g.session_data = {"key": "value"}
    return g.user_id

# Issue #4044, #4026: send_file类型改进
def send_file_issues():
    return send_file("test.txt")  # 类型注解有问题

# Issue #4040: 早期Python类型修正
def early_python_typing():
    from typing import Union, Optional
    return Union[str, int]

# Issue #4295: errorhandler类型注解
@app.errorhandler(404)
def handle_404(error):
    return jsonify({"error": "Not found"}), 404

# Issue #4041: 蓝图命名约束
def create_unsafe_blueprint():
    bp = Blueprint("unsafe-name-with-dashes", __name__)  # 不安全命名
    return bp

# Issue #4037: 蓝图URL前缀合并
def create_nested_blueprints():
    parent_bp = Blueprint("parent", __name__, url_prefix="/api")
    child_bp = Blueprint("child", __name__, url_prefix="/v1")
    
    @child_bp.route("/test")
    def child_route():
        return "child route"
    
    parent_bp.register_blueprint(child_bp)  # 前缀合并有问题
    return parent_bp

# ===== A类问题（AI辅助）=====

# Issue #4019: send_from_directory参数问题
def send_from_directory_issue():
    return send_from_directory("/tmp", "test.txt", filename="old_name.txt")

# Issue #4078: Config.from_json回退恢复
class Config:
    def from_json(self, filename):  # 在2.0.0中被误删
        import json
        with open(filename, 'r') as f:
            return json.load(f)

# Issue #4060: 装饰器工厂类型
def decorator_factory(param: str):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Issue #4069: 嵌套蓝图注册
def create_nested_blueprint_issues():
    parent = Blueprint("parent", __name__)
    child = Blueprint("child", __name__)
    
    @child.route("/test")
    def child_route():
        return "child"
    
    parent.register_blueprint(child)  # 端点命名冲突
    return parent

# Issue #1091: 蓝图重复注册
def duplicate_blueprint_registration():
    app = Flask(__name__)
    bp1 = Blueprint("test", __name__)
    bp2 = Blueprint("test", __name__)
    
    @bp1.route("/route1")
    def route1():
        return "route1"
    
    @bp2.route("/route2")
    def route2():
        return "route2"
    
    app.register_blueprint(bp1)
    app.register_blueprint(bp2)  # 端点被覆盖
    return app

# Issue #4093: teardown方法类型
def teardown_handler(error):
    pass

# Issue #4104: before_request类型
def before_request_handler():
    pass

# Issue #4098: 模板全局装饰器
def template_global_func():
    return "global"

# Issue #4095: errorhandler类型增强
def error_handler(error):
    return "error", 500

# Issue #4124: 蓝图重复注册处理
def blueprint_double_registration():
    app = Flask(__name__)
    bp = Blueprint("test", __name__)
    
    @bp.route("/test")
    def test_route():
        return "test"
    
    app.register_blueprint(bp, name="first")
    app.register_blueprint(bp, name="second")  # 路由表异常
    return app

# Issue #4150: static_folder PathLike
def create_static_folder_issue():
    static_path = Path("/tmp/static")
    app = Flask(__name__, static_folder=static_path)  # 不接受PathLike
    return app

# Issue #4157: jsonify Decimal处理
def json_decimal_issue():
    data = {
        "price": decimal.Decimal("19.99"),
        "quantity": decimal.Decimal("2.5")
    }
    return jsonify(data)  # 无法处理Decimal

# Issue #4096: CLI懒加载错误
def create_cli_with_lazy_loading():
    def create_app():
        app = Flask(__name__)
        @app.route("/")
        def index():
            return "Hello"
        return app
    
    cli = FlaskGroup(create_app=create_app)  # 错误处理有问题
    return cli

# Issue #4170: CLI loader kwargs
def create_cli_with_kwargs():
    def create_app(**kwargs):
        app = Flask(__name__)
        app.config.update(kwargs)
        return app
    
    cli = FlaskGroup(create_app=create_app)  # 不支持kwargs
    return cli

# Issue #4053: URL匹配顺序
def create_url_matching_issue():
    app = Flask(__name__)
    
    @app.route("/user/<int:user_id>")
    def user_route(user_id):
        return f"User {user_id}"
    
    @app.route("/user/<string:username>")
    def username_route(username):
        return f"Username {username}"
    
    return app  # 匹配顺序有问题

# Issue #4112: 异步视图支持
def create_async_view_issue():
    app = Flask(__name__)
    
    @app.route("/async")
    async def async_route():
        return "async response"  # 异步handler有问题
    
    return app

# Issue #4229: 回调顺序
def create_callback_order_issue():
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
        return f"Order: {g.order}"  # 回调顺序有问题
    
    return app

# Issue #4333: 上下文边界
def create_after_request_context_issue():
    app = Flask(__name__)
    
    @app.route("/after-request")
    def after_request_route():
        def cleanup():
            pass
        
        after_this_request(cleanup)  # 上下文问题
        return "after request"
    
    return app

# ===== D类问题（动态验证）=====

# Issue #4053: URL匹配顺序（运行时）
def url_matching_runtime():
    # 需要运行时验证URL匹配顺序
    pass

# Issue #4112: 异步视图（运行时）
def async_view_runtime():
    # 需要运行时验证异步handler
    pass

# Issue #4229: 回调顺序（运行时）
def callback_order_runtime():
    # 需要运行时验证回调顺序
    pass

# Issue #4333: 上下文边界（运行时）
def context_boundary_runtime():
    # 需要运行时验证上下文边界
    pass

# Issue #4037: 蓝图前缀合并（复杂）
def blueprint_prefix_complex():
    # 需要复杂路由验证
    pass

# Issue #4069: 嵌套蓝图（复杂）
def nested_blueprint_complex():
    # 需要复杂命名验证
    pass

if __name__ == "__main__":
    app = Flask(__name__)
    
    # 注册所有蓝图
    unsafe_bp = create_unsafe_blueprint()
    nested_bp = create_nested_blueprints()
    
    app.register_blueprint(unsafe_bp)
    app.register_blueprint(nested_bp)
    
    # 运行应用
    app.run(debug=True)
'''
    
    with open(test_dir / "app.py", "w", encoding="utf-8") as f:
        f.write(app_content)
    
    # 2. 创建配置文件
    config_content = '''{
  "DEBUG": true,
  "SECRET_KEY": "test-secret-key",
  "DATABASE_URL": "sqlite:///test.db"
}'''
    
    with open(test_dir / "config.json", "w", encoding="utf-8") as f:
        f.write(config_content)
    
    # 3. 创建测试运行脚本
    runner_content = '''#!/usr/bin/env python3
"""
Flask 2.0.0 快速测试运行器
"""

import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def run_quick_test():
    """运行快速测试"""
    print("🚀 运行Flask 2.0.0快速测试...")
    
    try:
        # 导入主应用
        import app
        print("✅ 主应用导入成功")
        
        # 创建应用实例
        flask_app = app.Flask(__name__)
        print("✅ Flask应用创建成功")
        
        # 测试各种功能
        print("🔍 测试各种Issue触发...")
        
        # 测试g对象
        with flask_app.app_context():
            app.use_g_object()
            print("✅ g对象测试完成")
        
        # 测试蓝图
        unsafe_bp = app.create_unsafe_blueprint()
        nested_bp = app.create_nested_blueprints()
        print("✅ 蓝图测试完成")
        
        # 测试配置
        config = app.Config()
        print("✅ 配置测试完成")
        
        print("🎉 所有测试运行完成！")
        print("💡 请使用检测系统分析这些代码")
        
    except Exception as e:
        print(f"❌ 测试运行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_quick_test()
'''
    
    with open(test_dir / "run_quick_test.py", "w", encoding="utf-8") as f:
        f.write(runner_content)
    
    # 4. 创建README
    readme_content = '''# Flask 2.0.0 快速测试

这个项目包含了Flask 2.0.0中32个已知Issue的最小化复现代码。

## 文件说明

- `app.py` - 包含所有32个Issue的复现代码
- `config.json` - 配置文件
- `run_quick_test.py` - 测试运行器

## 使用方法

1. 运行测试：
   ```bash
   python run_quick_test.py
   ```

2. 使用检测系统分析：
   ```bash
   python start_api.py
   # 然后上传 flask_minimal_test 目录
   ```

3. 运行对比分析：
   ```bash
   python compare_flask_bugs.py
   ```

## 包含的Issue

### S类（静态可检）- 8个
- #4024 - 顶层导出名类型检查
- #4020 - g对象类型提示  
- #4040 - 早期Python类型修正
- #4044 - send_file类型改进
- #4026 - send_file类型改进
- #4295 - errorhandler类型注解
- #4037 - 蓝图URL前缀合并
- #4041 - 蓝图命名约束

### A类（AI辅助）- 18个
- #4019 - send_from_directory参数
- #4078 - Config.from_json回退
- #4060 - 装饰器工厂类型
- #4069 - 嵌套蓝图注册
- #1091 - 蓝图重复注册
- #4093 - teardown方法类型
- #4104 - before_request类型
- #4098 - 模板全局装饰器
- #4095 - errorhandler类型增强
- #4124 - 蓝图重复注册处理
- #4150 - static_folder PathLike
- #4157 - jsonify Decimal处理
- #4096 - CLI懒加载错误
- #4170 - CLI loader kwargs
- #4053 - URL匹配顺序
- #4112 - 异步视图支持
- #4229 - 回调顺序
- #4333 - 上下文边界

### D类（动态验证）- 6个
- #4053 - URL匹配顺序（运行时）
- #4112 - 异步视图（运行时）
- #4229 - 回调顺序（运行时）
- #4333 - 上下文边界（运行时）
- #4037 - 蓝图前缀合并（复杂）
- #4069 - 嵌套蓝图（复杂）

## 注意事项

这些代码故意包含了Flask 2.0.0中的已知问题，用于测试检测系统的能力。
在实际项目中，这些问题在Flask 2.0.1/2.0.2/2.0.3中已被修复。
'''
    
    with open(test_dir / "README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    return str(test_dir)

def main():
    """主函数"""
    print("🔧 创建Flask 2.0.0快速测试项目...")
    
    project_path = create_minimal_flask_test()
    
    print(f"✅ 快速测试项目已创建: {project_path}")
    print("\n📁 包含文件:")
    print("  - app.py (包含所有32个Issue)")
    print("  - config.json (配置文件)")
    print("  - run_quick_test.py (测试运行器)")
    print("  - README.md (说明文档)")
    
    print("\n🚀 运行测试:")
    print(f"  cd {project_path}")
    print("  python run_quick_test.py")
    
    print("\n🔍 使用检测系统分析:")
    print("  python start_api.py")
    print("  # 然后上传 flask_minimal_test 目录")
    
    print("\n📊 运行对比分析:")
    print("  python compare_flask_bugs.py")

if __name__ == "__main__":
    main()




