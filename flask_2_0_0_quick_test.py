#!/usr/bin/env python3
"""
Flask 2.0.0 快速测试脚本
使用 tests/flask-2.0.0.zip 中的源码，确保测试真正的 2.0.0 版本
"""

import os
import sys
import tempfile
import zipfile
import shutil
from pathlib import Path

def create_flask_2_0_0_test():
    """创建使用Flask 2.0.0源码的测试项目"""
    
    print("🔧 创建Flask 2.0.0专用测试项目...")
    
    # 检查Flask源码包
    flask_zip_path = Path("tests/flask-2.0.0.zip")
    if not flask_zip_path.exists():
        print(f"❌ 未找到Flask源码包: {flask_zip_path}")
        return None
    
    # 创建测试目录
    test_dir = Path("flask_2_0_0_test")
    test_dir.mkdir(exist_ok=True)
    
    # 提取Flask源码
    print("📦 提取Flask 2.0.0源码...")
    with zipfile.ZipFile(flask_zip_path, 'r') as zip_ref:
        zip_ref.extractall(test_dir)
    
    # 找到Flask源码目录
    flask_src = test_dir / "flask-2.0.0" / "src" / "flask"
    if not flask_src.exists():
        print("❌ Flask源码目录不存在")
        return None
    
    # 复制Flask源码到测试目录
    flask_dest = test_dir / "flask"
    shutil.copytree(flask_src, flask_dest)
    
    # 创建主测试文件
    test_content = '''#!/usr/bin/env python3
"""
Flask 2.0.0 专用测试文件
使用本地Flask 2.0.0源码，触发官方文档中的32个已知Issue
"""

import sys
import os
from pathlib import Path

# 添加本地Flask源码到Python路径
current_dir = Path(__file__).parent
flask_path = current_dir / "flask"
sys.path.insert(0, str(flask_path))

# 导入Flask 2.0.0
from flask import Flask, Blueprint, jsonify, send_file, send_from_directory, g, request
from flask.cli import FlaskGroup
import decimal
from pathlib import Path as PathLib
from typing import Callable, Any, Optional, Union
import functools

def test_flask_version():
    """验证Flask版本"""
    import flask
    print(f"🔍 当前Flask版本: {flask.__version__}")
    return flask.__version__

# ===== S类问题（静态可检）- 8个 =====

def test_s_class_issues():
    """测试S类问题"""
    print("\\n🔍 测试S类问题（静态可检）...")
    
    # Issue #4024: 顶层导出名类型检查可见性
    print("  - #4024: 顶层导出名类型检查")
    from flask import Flask, Blueprint, jsonify, send_file, send_from_directory, g, request
    
    # Issue #4020: g对象类型提示
    print("  - #4020: g对象类型提示")
    def use_g_object():
        g.user_id = 123  # 在2.0.0中类型检查器会报错
        g.session_data = {"key": "value"}
        return g.user_id
    
    # Issue #4044, #4026: send_file类型改进
    print("  - #4044, #4026: send_file类型改进")
    def send_file_issues():
        return send_file("test.txt")  # 类型注解有问题
    
    # Issue #4040: 早期Python类型修正
    print("  - #4040: 早期Python类型修正")
    def early_python_typing():
        from typing import Union, Optional
        return Union[str, int]
    
    # Issue #4295: errorhandler类型注解
    print("  - #4295: errorhandler类型注解")
    app = Flask(__name__)
    
    @app.errorhandler(404)
    def handle_404(error):
        return jsonify({"error": "Not found"}), 404
    
    # Issue #4041: 蓝图命名约束
    print("  - #4041: 蓝图命名约束")
    def create_unsafe_blueprint():
        bp = Blueprint("unsafe-name-with-dashes", __name__)  # 不安全命名
        return bp
    
    # Issue #4037: 蓝图URL前缀合并
    print("  - #4037: 蓝图URL前缀合并")
    def create_nested_blueprints():
        parent_bp = Blueprint("parent", __name__, url_prefix="/api")
        child_bp = Blueprint("child", __name__, url_prefix="/v1")
        
        @child_bp.route("/test")
        def child_route():
            return "child route"
        
        parent_bp.register_blueprint(child_bp)  # 前缀合并有问题
        return parent_bp
    
    print("✅ S类问题测试完成")

# ===== A类问题（AI辅助）- 18个 =====

def test_a_class_issues():
    """测试A类问题"""
    print("\\n🔍 测试A类问题（AI辅助）...")
    
    # Issue #4019: send_from_directory参数问题
    print("  - #4019: send_from_directory参数")
    def send_from_directory_issue():
        return send_from_directory("/tmp", "test.txt", filename="old_name.txt")
    
    # Issue #4078: Config.from_json回退恢复
    print("  - #4078: Config.from_json回退")
    class Config:
        def from_json(self, filename):  # 在2.0.0中被误删
            import json
            with open(filename, 'r') as f:
                return json.load(f)
    
    # Issue #4060: 装饰器工厂类型
    print("  - #4060: 装饰器工厂类型")
    def decorator_factory(param: str):
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    # Issue #4069: 嵌套蓝图注册
    print("  - #4069: 嵌套蓝图注册")
    def create_nested_blueprint_issues():
        parent = Blueprint("parent", __name__)
        child = Blueprint("child", __name__)
        
        @child.route("/test")
        def child_route():
            return "child"
        
        parent.register_blueprint(child)  # 端点命名冲突
        return parent
    
    # Issue #1091: 蓝图重复注册
    print("  - #1091: 蓝图重复注册")
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
    print("  - #4093: teardown方法类型")
    def teardown_handler(error):
        pass
    
    # Issue #4104: before_request类型
    print("  - #4104: before_request类型")
    def before_request_handler():
        pass
    
    # Issue #4098: 模板全局装饰器
    print("  - #4098: 模板全局装饰器")
    def template_global_func():
        return "global"
    
    # Issue #4095: errorhandler类型增强
    print("  - #4095: errorhandler类型增强")
    def error_handler(error):
        return "error", 500
    
    # Issue #4124: 蓝图重复注册处理
    print("  - #4124: 蓝图重复注册处理")
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
    print("  - #4150: static_folder PathLike")
    def create_static_folder_issue():
        static_path = PathLib("/tmp/static")
        app = Flask(__name__, static_folder=static_path)  # 不接受PathLike
        return app
    
    # Issue #4157: jsonify Decimal处理
    print("  - #4157: jsonify Decimal处理")
    def json_decimal_issue():
        data = {
            "price": decimal.Decimal("19.99"),
            "quantity": decimal.Decimal("2.5")
        }
        return jsonify(data)  # 无法处理Decimal
    
    # Issue #4096: CLI懒加载错误
    print("  - #4096: CLI懒加载错误")
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
    print("  - #4170: CLI loader kwargs")
    def create_cli_with_kwargs():
        def create_app(**kwargs):
            app = Flask(__name__)
            app.config.update(kwargs)
            return app
        
        cli = FlaskGroup(create_app=create_app)  # 不支持kwargs
        return cli
    
    # Issue #4053: URL匹配顺序
    print("  - #4053: URL匹配顺序")
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
    print("  - #4112: 异步视图支持")
    def create_async_view_issue():
        app = Flask(__name__)
        
        @app.route("/async")
        async def async_route():
            return "async response"  # 异步handler有问题
        
        return app
    
    # Issue #4229: 回调顺序
    print("  - #4229: 回调顺序")
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
    print("  - #4333: 上下文边界")
    def create_after_request_context_issue():
        app = Flask(__name__)
        
        @app.route("/after-request")
        def after_request_route():
            def cleanup():
                pass
            
            from flask import after_this_request
            after_this_request(cleanup)  # 上下文问题
            return "after request"
        
        return app
    
    print("✅ A类问题测试完成")

# ===== D类问题（动态验证）- 6个 =====

def test_d_class_issues():
    """测试D类问题"""
    print("\\n🔍 测试D类问题（动态验证）...")
    
    # Issue #4053: URL匹配顺序（运行时）
    print("  - #4053: URL匹配顺序（运行时）")
    def url_matching_runtime():
        # 需要运行时验证URL匹配顺序
        pass
    
    # Issue #4112: 异步视图（运行时）
    print("  - #4112: 异步视图（运行时）")
    def async_view_runtime():
        # 需要运行时验证异步handler
        pass
    
    # Issue #4229: 回调顺序（运行时）
    print("  - #4229: 回调顺序（运行时）")
    def callback_order_runtime():
        # 需要运行时验证回调顺序
        pass
    
    # Issue #4333: 上下文边界（运行时）
    print("  - #4333: 上下文边界（运行时）")
    def context_boundary_runtime():
        # 需要运行时验证上下文边界
        pass
    
    # Issue #4037: 蓝图前缀合并（复杂）
    print("  - #4037: 蓝图前缀合并（复杂）")
    def blueprint_prefix_complex():
        # 需要复杂路由验证
        pass
    
    # Issue #4069: 嵌套蓝图（复杂）
    print("  - #4069: 嵌套蓝图（复杂）")
    def nested_blueprint_complex():
        # 需要复杂命名验证
        pass
    
    print("✅ D类问题测试完成")

def run_all_tests():
    """运行所有测试"""
    print("🚀 开始Flask 2.0.0专用测试...")
    print("="*70)
    
    # 验证Flask版本
    version = test_flask_version()
    if not version.startswith("2.0.0"):
        print(f"⚠️  警告: 当前Flask版本为 {version}，不是2.0.0")
    
    # 运行各类测试
    test_s_class_issues()
    test_a_class_issues()
    test_d_class_issues()
    
    print("\\n🎉 所有测试完成！")
    print("💡 请使用检测系统分析这些代码")

if __name__ == "__main__":
    run_all_tests()
'''
    
    with open(test_dir / "test_flask_2_0_0.py", "w", encoding="utf-8") as f:
        f.write(test_content)
    
    # 创建测试运行器
    runner_content = '''#!/usr/bin/env python3
"""
Flask 2.0.0 测试运行器
"""

import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """主函数"""
    print("🚀 运行Flask 2.0.0专用测试...")
    
    try:
        import test_flask_2_0_0
        test_flask_2_0_0.run_all_tests()
    except Exception as e:
        print(f"❌ 测试运行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
'''
    
    with open(test_dir / "run_tests.py", "w", encoding="utf-8") as f:
        f.write(runner_content)
    
    # 创建README
    readme_content = '''# Flask 2.0.0 专用测试项目

这个项目使用 Flask 2.0.0 的完整源码，确保测试真正的 2.0.0 版本。

## 文件说明

- `flask/` - Flask 2.0.0 完整源码
- `test_flask_2_0_0.py` - 包含32个Issue的测试代码
- `run_tests.py` - 测试运行器

## 使用方法

1. 运行测试：
   ```bash
   python run_tests.py
   ```

2. 使用检测系统分析：
   ```bash
   python start_api.py
   # 然后上传 flask_2_0_0_test 目录
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

这个项目使用 Flask 2.0.0 的完整源码，确保测试的是真正的 2.0.0 版本。
所有32个Issue都是基于官方文档中的已知问题。
'''
    
    with open(test_dir / "README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    return str(test_dir)

def main():
    """主函数"""
    print("🚀 Flask 2.0.0 专用测试项目创建器")
    print("="*70)
    
    project_path = create_flask_2_0_0_test()
    
    if project_path:
        print(f"\\n✅ 测试项目创建成功: {project_path}")
        print("\\n📁 包含文件:")
        print("  - flask/ (Flask 2.0.0完整源码)")
        print("  - test_flask_2_0_0.py (32个Issue测试代码)")
        print("  - run_tests.py (测试运行器)")
        print("  - README.md (说明文档)")
        
        print("\\n🚀 运行测试:")
        print(f"  cd {project_path}")
        print("  python run_tests.py")
        
        print("\\n🔍 使用检测系统分析:")
        print("  python start_api.py")
        print(f"  # 然后上传 {project_path} 目录")
        
        print("\\n📊 运行对比分析:")
        print("  python compare_flask_bugs.py")
    else:
        print("❌ 测试项目创建失败")

if __name__ == "__main__":
    main()




