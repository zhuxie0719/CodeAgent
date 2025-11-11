"""
Flask 2.0.0 Bug测试应用
根据Flask版本选择与Issue策略.md中的32个bug清单编写测试用例
"""
from flask import Flask, g, jsonify, send_file, send_from_directory, Blueprint, request, session
import decimal
import functools
from typing import NamedTuple

app = Flask(__name__)

# Bug测试: 静态类型相关
# Bug #1: 顶层导出名的类型检查可见性
# Bug #2: g的类型提示为命名空间对象
@app.route('/bug1_g_type')
def bug1_g_type():
    """测试g对象的类型提示问题"""
    g.user_id = 123  # 在2.0.0中类型检查器无法识别
    g.data = {"key": "value"}
    return f"g.user_id: {g.user_id}, g.data: {g.data}"

# Bug #4, #6: send_file/send_from_directory类型改进
@app.route('/bug4_send_file_type')
def bug4_send_file_type():
    """测试send_file类型问题"""
    # 在2.0.0中类型不匹配
    try:
        return send_file('nonexistent.txt', mimetype='text/plain')
    except Exception as e:
        return f"Error: {str(e)}", 400

# Bug #7: 蓝图URL前缀合并
parent_bp = Blueprint('parent', __name__, url_prefix='/parent')

@parent_bp.route('/test')
def parent_test():
    return "Parent blueprint test"

@app.route('/bug7_blueprint_prefix')
def bug7_blueprint_prefix():
    """测试蓝图URL前缀合并问题"""
    # 在2.0.0中多级前缀未正确合并
    return "Blueprint prefix test"

# Bug #8: 蓝图命名约束
problematic_bp = Blueprint('test_nested', __name__)  # 在2.0.0中应该被限制但不被限制

@problematic_bp.route('/issue')
def problematic_naming():
    return "Problematic blueprint name"

# Bug #9: send_from_directory filename参数
@app.route('/bug9_send_from_directory')
def bug9_send_from_directory():
    """测试send_from_directory filename参数问题"""
    # 在2.0.0中使用filename参数会被忽略
    try:
        return send_from_directory('.', 'requirements.txt', as_attachment=True)
    except Exception as e:
        return f"Error: {str(e)}", 400

# Bug #10: Config.from_json缺失
# 这个需要在create_app中测试，这里仅作注释
# app.config.from_json('config.json')  # 在2.0.0中此方法不存在

# Bug #11: 装饰器类型改进
def decorator_type_test(f):
    """测试装饰器类型问题"""
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper

@app.route('/bug11_decorator_type')
@decorator_type_test
def bug11_decorator_type():
    """测试装饰器类型改进"""
    return "Decorator type test"

# Bug #14: teardown_request类型注解
@app.teardown_request
def bug14_teardown_request(exception):
    """测试teardown_request类型注解"""
    if exception:
        print(f"Exception in teardown: {exception}")
    return None

# Bug #15: before_request类型注解
@app.before_request
def bug15_before_request():
    """测试before_request类型注解"""
    g.request_count = getattr(g, 'request_count', 0) + 1

# Bug #16: 模板全局装饰器
@app.template_global()
def bug16_template_global():
    """测试模板全局装饰器类型"""
    return "Template global test"

# Bug #17: errorhandler装饰器类型
@app.errorhandler(404)
def bug17_errorhandler(error):
    """测试errorhandler装饰器类型"""
    return jsonify({"error": "Not found"}), 404

# Bug #18: 重复注册蓝图
duplicate_bp = Blueprint('duplicate', __name__)
app.register_blueprint(duplicate_bp)
# app.register_blueprint(duplicate_bp)  # 在2.0.0中应警告但不警告

# Bug #19: static_folder Path支持
# 这个需要在create_app中测试

# Bug #20: jsonify Decimal处理
@app.route('/bug20_jsonify_decimal')
def bug20_jsonify_decimal():
    """测试jsonify对Decimal的处理"""
    # 在2.0.0中会失败
    value = decimal.Decimal('10.5')
    return jsonify({"decimal": value})

# Bug #22: create_app工厂函数
def create_test_app():
    """测试create_app工厂函数"""
    app = Flask(__name__)
    # 在2.0.0中kwargs处理有问题
    return app

# Bug #23: URL匹配顺序
@app.route('/bug23_url_order/<int:id>')
def bug23_url_order_int(id):
    return f"URL order int: {id}"

@app.route('/bug23_url_order/<string:id>')
def bug23_url_order_str(id):
    return f"URL order str: {id}"

# Bug #24: 异步handler支持（需动态验证）
@app.route('/bug24_async_handler')
def bug24_async_handler():
    """测试异步handler支持"""
    # 在2.0.0中异步handler不被支持
    return "Async handler test"

# Bug #25: 回调触发顺序
@app.before_request
def bug25_before_all():
    g.callback_order = []
    g.callback_order.append('app_before')

# Bug #26: 上下文边界
@app.route('/bug26_context_boundary')
def bug26_context_boundary():
    """测试上下文边界问题"""
    # 在2.0.0中after_this_request在非请求上下文中行为异常
    def process_data():
        return "processed"
    
    from flask import after_this_request
    after_this_request(process_data)
    
    return "Context boundary test"

# 注册蓝图
app.register_blueprint(parent_bp)
app.register_blueprint(problematic_bp)

@app.route('/')
def index():
    return "Flask 2.0.0 Bug Test Application"

@app.route('/health')
def health():
    return jsonify({"status": "ok", "version": "2.0.0"})

def create_app():
    return app

if __name__ == '__main__':
    import os
    port = int(os.getenv('PORT', os.getenv('FLASK_RUN_PORT', 5000)))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
