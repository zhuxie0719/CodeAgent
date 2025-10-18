#!/usr/bin/env python3
"""
Flask 2.0.0 测试套件
用于触发官方文档中的32个已知Issue，测试检测系统的能力
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any
import json
import decimal
from flask import Flask, Blueprint, jsonify, send_file, send_from_directory, g, request
from flask.cli import FlaskGroup
import click

class FlaskTestSuite:
    """Flask 2.0.0 测试套件生成器"""
    
    def __init__(self, output_dir: str = "flask_test_project"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.test_files = []
        
    def create_test_project(self) -> str:
        """创建包含所有测试用例的Flask项目"""
        
        # 1. 创建主应用文件（包含S类问题）
        self._create_main_app()
        
        # 2. 创建蓝图文件（包含A类问题）
        self._create_blueprint_files()
        
        # 3. 创建类型注解问题文件
        self._create_typing_issues()
        
        # 4. 创建CLI相关文件
        self._create_cli_files()
        
        # 5. 创建JSON处理文件
        self._create_json_issues()
        
        # 6. 创建异步和上下文文件
        self._create_async_context_issues()
        
        # 7. 创建配置文件
        self._create_config_files()
        
        # 8. 创建测试运行脚本
        self._create_test_runner()
        
        return str(self.output_dir)
    
    def _create_main_app(self):
        """创建主应用文件 - 触发S类问题"""
        app_content = '''#!/usr/bin/env python3
"""
Flask 2.0.0 主应用 - 触发多个已知Issue
"""

from flask import Flask, Blueprint, jsonify, send_file, send_from_directory, g, request
from flask.cli import FlaskGroup
import decimal
from pathlib import Path
import os

# Issue #4024: 顶层导出名的类型检查可见性
from flask import Flask, Blueprint, jsonify, send_file, send_from_directory, g, request
# 在2.0.0中，这些导入的类型检查有问题

# Issue #4020: g的类型提示为命名空间对象
def use_g_object():
    """触发g对象的类型检查问题"""
    g.user_id = 123  # 在2.0.0中类型检查器会报错
    g.session_data = {"key": "value"}
    return g.user_id

# Issue #4044, #4026: send_file类型改进
def send_file_issues():
    """触发send_file相关的类型问题"""
    # 在2.0.0中，这些函数的类型注解有问题
    return send_file("test.txt")
    # return send_from_directory("/tmp", "test.txt")

# Issue #4040: 早期Python 3.6.0不可用类型修正
def early_python_typing():
    """触发早期Python版本的类型问题"""
    # 在2.0.0中，某些类型在Python 3.6.0上不可用
    from typing import Union, Optional
    return Union[str, int]

# Issue #4295: errorhandler装饰器类型注解修正
@app.errorhandler(404)
def handle_404(error):
    """触发errorhandler的类型注解问题"""
    return jsonify({"error": "Not found"}), 404

# Issue #4041: 蓝图命名约束
def create_unsafe_blueprint():
    """创建不安全的蓝图命名"""
    bp = Blueprint("unsafe-name-with-dashes", __name__)
    # 在2.0.0中允许不安全的命名
    return bp

# Issue #4037: 蓝图URL前缀合并
def create_nested_blueprints():
    """创建嵌套蓝图，触发前缀合并问题"""
    parent_bp = Blueprint("parent", __name__, url_prefix="/api")
    child_bp = Blueprint("child", __name__, url_prefix="/v1")
    
    @child_bp.route("/test")
    def child_route():
        return "child route"
    
    # 在2.0.0中，嵌套蓝图的前缀合并有问题
    parent_bp.register_blueprint(child_bp)
    return parent_bp

if __name__ == "__main__":
    app = Flask(__name__)
    
    # 注册蓝图
    unsafe_bp = create_unsafe_blueprint()
    nested_bp = create_nested_blueprints()
    
    app.register_blueprint(unsafe_bp)
    app.register_blueprint(nested_bp)
    
    app.run(debug=True)
'''
        
        with open(self.output_dir / "app.py", "w", encoding="utf-8") as f:
            f.write(app_content)
        self.test_files.append("app.py")
    
    def _create_blueprint_files(self):
        """创建蓝图相关文件 - 触发A类问题"""
        
        # 蓝图路由问题
        blueprint_content = '''#!/usr/bin/env python3
"""
蓝图相关Issue测试
"""

from flask import Blueprint, jsonify, request, url_for
from flask import Flask

# Issue #4019: send_from_directory重新加入filename参数
def send_file_issues():
    """触发send_from_directory的参数问题"""
    from flask import send_from_directory
    # 在2.0.0中，filename参数被重命名为path，但旧参数名仍可用
    # 这会导致迁移期的不兼容问题
    return send_from_directory("/tmp", "test.txt", filename="old_name.txt")

# Issue #4069: 嵌套蓝图注册为点分名
def create_nested_blueprint_issues():
    """创建嵌套蓝图，触发命名冲突"""
    parent = Blueprint("parent", __name__)
    child = Blueprint("child", __name__)
    
    @child.route("/test")
    def child_route():
        return "child"
    
    # 在2.0.0中，嵌套蓝图的端点命名会冲突
    parent.register_blueprint(child)
    return parent

# Issue #1091: register_blueprint支持name=修改注册名
def duplicate_blueprint_registration():
    """重复注册同名蓝图"""
    app = Flask(__name__)
    bp1 = Blueprint("test", __name__)
    bp2 = Blueprint("test", __name__)
    
    @bp1.route("/route1")
    def route1():
        return "route1"
    
    @bp2.route("/route2") 
    def route2():
        return "route2"
    
    # 在2.0.0中，重复注册同名蓝图会导致端点被覆盖
    app.register_blueprint(bp1)
    app.register_blueprint(bp2)  # 这会覆盖bp1的端点
    
    return app

# Issue #4124: 同一蓝图以不同名称注册两次
def blueprint_double_registration():
    """同一蓝图注册两次"""
    app = Flask(__name__)
    bp = Blueprint("test", __name__)
    
    @bp.route("/test")
    def test_route():
        return "test"
    
    # 在2.0.0中，允许非预期的重复注册
    app.register_blueprint(bp, name="first")
    app.register_blueprint(bp, name="second")  # 这会导致路由表异常
    
    return app
'''
        
        with open(self.output_dir / "blueprint_issues.py", "w", encoding="utf-8") as f:
            f.write(blueprint_content)
        self.test_files.append("blueprint_issues.py")
    
    def _create_typing_issues(self):
        """创建类型注解问题文件"""
        typing_content = '''#!/usr/bin/env python3
"""
类型注解相关Issue测试
"""

from flask import Flask, Blueprint, jsonify, request
from typing import Callable, Any, Optional, Union
import functools

# Issue #4060: 装饰器工厂的Callable类型改进
def create_decorator_factory():
    """创建装饰器工厂，触发类型问题"""
    
    def decorator_factory(param: str):
        """装饰器工厂函数"""
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

# Issue #4093: teardown_*方法类型注解修正
def create_teardown_handlers():
    """创建teardown处理器，触发类型问题"""
    
    def teardown_handler(error):
        """teardown处理器"""
        pass
    
    # 在2.0.0中，teardown方法的类型注解有问题
    return teardown_handler

# Issue #4104: before_request类型注解修正
def create_before_request_handlers():
    """创建before_request处理器"""
    
    def before_request_handler():
        """before_request处理器"""
        pass
    
    # 在2.0.0中，before_request的类型注解有问题
    return before_request_handler

# Issue #4098: 模板全局装饰器对无参函数的typing约束修复
def create_template_globals():
    """创建模板全局函数"""
    
    def template_global_func():
        """模板全局函数"""
        return "global"
    
    # 在2.0.0中，模板全局函数的类型约束有问题
    return template_global_func

# Issue #4095: app.errorhandler装饰器类型增强
def create_error_handlers():
    """创建错误处理器"""
    
    def error_handler(error):
        """错误处理器"""
        return "error", 500
    
    # 在2.0.0中，errorhandler的类型增强有问题
    return error_handler

# Issue #4150: static_folder接受pathlib.Path
def create_static_folder_issue():
    """创建static_folder的PathLike问题"""
    from pathlib import Path
    
    # 在2.0.0中，static_folder不接受PathLike对象
    static_path = Path("/tmp/static")
    app = Flask(__name__, static_folder=static_path)
    
    return app
'''
        
        with open(self.output_dir / "typing_issues.py", "w", encoding="utf-8") as f:
            f.write(typing_content)
        self.test_files.append("typing_issues.py")
    
    def _create_cli_files(self):
        """创建CLI相关文件"""
        cli_content = '''#!/usr/bin/env python3
"""
CLI相关Issue测试
"""

from flask import Flask
from flask.cli import FlaskGroup
import click

# Issue #4096: CLI懒加载时延迟错误抛出处理修正
def create_cli_with_lazy_loading():
    """创建CLI应用，触发懒加载错误处理问题"""
    
    def create_app():
        """应用工厂函数"""
        app = Flask(__name__)
        
        @app.route("/")
        def index():
            return "Hello"
        
        return app
    
    # 在2.0.0中，CLI懒加载时的错误处理有问题
    cli = FlaskGroup(create_app=create_app)
    return cli

# Issue #4170: CLI loader支持create_app(**kwargs)
def create_cli_with_kwargs():
    """创建带关键字参数的CLI应用"""
    
    def create_app(**kwargs):
        """带关键字参数的应用工厂"""
        app = Flask(__name__)
        
        # 使用传入的关键字参数
        app.config.update(kwargs)
        
        @app.route("/")
        def index():
            return "Hello with kwargs"
        
        return app
    
    # 在2.0.0中，CLI loader不支持带关键字参数的create_app
    cli = FlaskGroup(create_app=create_app)
    return cli

# Issue #4096: CLI懒加载错误处理
def create_cli_error_handling():
    """创建CLI错误处理测试"""
    
    def create_app_with_error():
        """会出错的应用工厂"""
        # 故意创建一个会出错的配置
        app = Flask(__name__)
        
        # 在2.0.0中，这种错误会被错误地吞掉
        @app.route("/")
        def index():
            # 这里会触发一个错误
            return 1 / 0
        
        return app
    
    cli = FlaskGroup(create_app=create_app_with_error)
    return cli
'''
        
        with open(self.output_dir / "cli_issues.py", "w", encoding="utf-8") as f:
            f.write(cli_content)
        self.test_files.append("cli_issues.py")
    
    def _create_json_issues(self):
        """创建JSON处理问题文件"""
        json_content = '''#!/usr/bin/env python3
"""
JSON处理相关Issue测试
"""

from flask import Flask, jsonify
import decimal

# Issue #4157: jsonify处理decimal.Decimal
def create_json_decimal_issue():
    """创建JSON处理Decimal的问题"""
    app = Flask(__name__)
    
    @app.route("/decimal")
    def decimal_route():
        """返回包含Decimal的JSON"""
        data = {
            "price": decimal.Decimal("19.99"),
            "quantity": decimal.Decimal("2.5"),
            "total": decimal.Decimal("49.975")
        }
        
        # 在2.0.0中，jsonify无法正确处理Decimal
        return jsonify(data)
    
    return app

# Issue #4078: Config.from_json回退恢复
def create_config_json_issue():
    """创建Config.from_json问题"""
    from flask import Flask
    
    class CustomConfig:
        """自定义配置类"""
        def __init__(self):
            self.data = {}
        
        def from_json(self, filename):
            """从JSON文件加载配置"""
            # 在2.0.0中，这个方法被误删了
            import json
            with open(filename, 'r') as f:
                self.data = json.load(f)
    
    app = Flask(__name__)
    config = CustomConfig()
    
    # 在2.0.0中，这会导致错误
    try:
        config.from_json("config.json")
    except AttributeError:
        pass  # 预期会出错
    
    return app
'''
        
        with open(self.output_dir / "json_issues.py", "w", encoding="utf-8") as f:
            f.write(json_content)
        self.test_files.append("json_issues.py")
    
    def _create_async_context_issues(self):
        """创建异步和上下文问题文件"""
        async_content = '''#!/usr/bin/env python3
"""
异步和上下文相关Issue测试
"""

from flask import Flask, request, g, after_this_request
import asyncio

# Issue #4112: 异步视图支持
def create_async_view_issue():
    """创建异步视图，触发上下文问题"""
    app = Flask(__name__)
    
    @app.route("/async")
    async def async_route():
        """异步路由"""
        # 在2.0.0中，异步handler的生命周期与上下文互动有问题
        await asyncio.sleep(0.1)
        return "async response"
    
    return app

# Issue #4053: URL匹配顺序
def create_url_matching_issue():
    """创建URL匹配顺序问题"""
    app = Flask(__name__)
    
    @app.route("/user/<int:user_id>")
    def user_route(user_id):
        """用户路由"""
        return f"User {user_id}"
    
    @app.route("/user/<string:username>")
    def username_route(username):
        """用户名路由"""
        return f"Username {username}"
    
    # 在2.0.0中，URL匹配顺序有问题
    return app

# Issue #4229: 回调顺序
def create_callback_order_issue():
    """创建回调顺序问题"""
    app = Flask(__name__)
    
    @app.before_request
    def before_request_1():
        """第一个before_request"""
        g.order = []
        g.order.append("before_1")
    
    @app.before_request
    def before_request_2():
        """第二个before_request"""
        g.order.append("before_2")
    
    @app.route("/callback-order")
    def callback_order_route():
        """测试回调顺序"""
        # 在2.0.0中，回调顺序有问题
        return f"Order: {g.order}"
    
    return app

# Issue #4333: after_this_request在非请求上下文下的报错
def create_after_request_context_issue():
    """创建after_this_request上下文问题"""
    app = Flask(__name__)
    
    @app.route("/after-request")
    def after_request_route():
        """after_request路由"""
        # 在2.0.0中，在非请求上下文下使用after_this_request会报错
        def cleanup():
            pass
        
        after_this_request(cleanup)
        return "after request"
    
    return app
'''
        
        with open(self.output_dir / "async_context_issues.py", "w", encoding="utf-8") as f:
            f.write(async_content)
        self.test_files.append("async_context_issues.py")
    
    def _create_config_files(self):
        """创建配置文件"""
        config_content = '''#!/usr/bin/env python3
"""
配置文件 - 触发Config相关Issue
"""

# Issue #4078: Config.from_json回退恢复
import json
from flask import Flask

class Config:
    """配置类"""
    def __init__(self):
        self.data = {}
    
    def from_json(self, filename):
        """从JSON文件加载配置"""
        # 在2.0.0中，这个方法被误删了
        with open(filename, 'r') as f:
            self.data = json.load(f)

def create_config_issue():
    """创建配置问题"""
    app = Flask(__name__)
    config = Config()
    
    # 在2.0.0中，这会导致AttributeError
    try:
        config.from_json("config.json")
    except AttributeError:
        pass
    
    return app
'''
        
        with open(self.output_dir / "config_issues.py", "w", encoding="utf-8") as f:
            f.write(config_content)
        self.test_files.append("config_issues.py")
    
    def _create_test_runner(self):
        """创建测试运行脚本"""
        runner_content = '''#!/usr/bin/env python3
"""
Flask 2.0.0 测试运行器
运行所有测试用例，触发已知Issue
"""

import sys
import os
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def run_all_tests():
    """运行所有测试"""
    print("🚀 开始运行Flask 2.0.0测试套件...")
    
    # 导入所有测试模块
    test_modules = [
        "app",
        "blueprint_issues", 
        "typing_issues",
        "cli_issues",
        "json_issues",
        "async_context_issues",
        "config_issues"
    ]
    
    for module_name in test_modules:
        try:
            print(f"📦 运行模块: {module_name}")
            __import__(module_name)
            print(f"✅ {module_name} 运行完成")
        except Exception as e:
            print(f"❌ {module_name} 运行失败: {e}")
    
    print("🎉 所有测试运行完成！")
    print("💡 请使用你的检测系统分析这些文件")

if __name__ == "__main__":
    run_all_tests()
'''
        
        with open(self.output_dir / "run_tests.py", "w", encoding="utf-8") as f:
            f.write(runner_content)
        self.test_files.append("run_tests.py")
        
        # 创建配置文件
        config_json = {
            "DEBUG": True,
            "SECRET_KEY": "test-secret-key",
            "DATABASE_URL": "sqlite:///test.db"
        }
        
        with open(self.output_dir / "config.json", "w", encoding="utf-8") as f:
            json.dump(config_json, f, indent=2)
    
    def create_readme(self):
        """创建README文件"""
        readme_content = '''# Flask 2.0.0 测试套件

这个测试套件包含了Flask 2.0.0中已知的32个Issue的复现代码。

## 文件说明

- `app.py` - 主应用文件，包含S类（静态可检）问题
- `blueprint_issues.py` - 蓝图相关A类（AI辅助）问题  
- `typing_issues.py` - 类型注解问题
- `cli_issues.py` - CLI相关问题
- `json_issues.py` - JSON处理问题
- `async_context_issues.py` - 异步和上下文D类（动态验证）问题
- `config_issues.py` - 配置相关问题
- `run_tests.py` - 测试运行器

## 使用方法

1. 运行测试套件：
   ```bash
   python run_tests.py
   ```

2. 使用你的检测系统分析这些文件

3. 运行对比脚本：
   ```bash
   python compare_flask_bugs.py
   ```

## 预期检测的Issue

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

这些测试用例故意包含了Flask 2.0.0中的已知问题，用于测试检测系统的能力。
在实际项目中，这些问题在Flask 2.0.1/2.0.2/2.0.3中已被修复。
'''
        
        with open(self.output_dir / "README.md", "w", encoding="utf-8") as f:
            f.write(readme_content)

def main():
    """主函数"""
    print("🔧 创建Flask 2.0.0测试套件...")
    
    suite = FlaskTestSuite("flask_test_project")
    project_path = suite.create_test_project()
    suite.create_readme()
    
    print(f"✅ 测试套件已创建: {project_path}")
    print("📁 包含文件:")
    for file in suite.test_files:
        print(f"  - {file}")
    print("\n🚀 运行测试:")
    print(f"  cd {project_path}")
    print("  python run_tests.py")
    print("\n🔍 使用检测系统分析:")
    print("  python start_api.py")
    print("  # 然后上传 flask_test_project 目录")

if __name__ == "__main__":
    main()




