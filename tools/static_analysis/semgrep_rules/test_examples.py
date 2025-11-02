"""
Flask 2.0.0 问题示例代码
用于测试 Semgrep 规则是否正确检测
"""

from flask import Flask, Blueprint, jsonify, send_from_directory
from decimal import Decimal
from pathlib import Path

app = Flask(__name__)

# ============================================
# 问题1: 嵌套蓝图缺少显式命名 (#4069)
# ============================================
# 应被检测：flask-blueprint-nested-naming
parent_bp = Blueprint("parent", __name__)
child_bp = Blueprint("child", __name__)
parent_bp.register_blueprint(child_bp)  # 缺少 name 参数
app.register_blueprint(parent_bp)

# 正确做法（不应被检测）：
# parent_bp.register_blueprint(child_bp, name="parent.child")

# ============================================
# 问题2: 蓝图重复注册 (#1091, #4124)
# ============================================
# 应被检测：flask-blueprint-duplicate-registration
test_bp = Blueprint("test", __name__)
app.register_blueprint(test_bp)
# ... 其他代码 ...
app.register_blueprint(test_bp)  # 重复注册

# ============================================
# 问题3: 不安全的蓝图命名 (#4041)
# ============================================
# 应被检测：flask-blueprint-unsafe-naming
bad_bp1 = Blueprint("", __name__)  # 空字符串
bad_bp2 = Blueprint(None, __name__)  # None
bad_bp3 = Blueprint(".invalid", __name__)  # 以点开头
bad_bp4 = Blueprint("invalid/name", __name__)  # 包含斜杠

# ============================================
# 问题4: URL前缀嵌套 (#4037)
# ============================================
# 应被检测：flask-blueprint-url-prefix-nesting
api_bp = Blueprint("api", __name__, url_prefix="/api")
v1_bp = Blueprint("v1", __name__, url_prefix="/v1")
api_bp.register_blueprint(v1_bp)
app.register_blueprint(api_bp, url_prefix="/app")  # 多层前缀嵌套

# ============================================
# 问题5: send_from_directory 使用旧参数 (#4019)
# ============================================
# 应被检测：flask-send-from-directory-filename-param
@app.route("/file")
def send_file_old():
    return send_from_directory("/path/to/dir", filename="file.txt")  # 应使用 path=

# ============================================
# 问题6: Config.from_json 使用 (#4078)
# ============================================
# 应被检测：flask-config-from-json-missing
# 注意：这个规则主要是提示性检测
class MyConfig:
    pass

config = MyConfig()
# config.from_json(...)  # 如果在Flask 2.0.0中使用会报错

# ============================================
# 问题7: jsonify Decimal 编码 (#4157)
# ============================================
# 应被检测：flask-jsonify-decimal-encoding
@app.route("/decimal")
def return_decimal():
    data = {"price": Decimal("99.99")}
    return jsonify(data)  # Flask 2.0.0中无法正确处理

# ============================================
# 问题8: static_folder PathLike (#4150)
# ============================================
# 应被检测：flask-static-folder-pathlike
static_path = Path("static")
app_bad = Flask(__name__, static_folder=static_path)  # 应使用 str(static_path)
bp_bad = Blueprint("bp", __name__, static_folder=Path("static"))  # 应使用字符串

# ============================================
# 问题9: CLI loader kwargs (#4170)
# ============================================
# 应被检测：flask-cli-loader-kwargs
def create_app(env, **kwargs):  # Flask 2.0.0不支持
    app = Flask(__name__)
    return app

# ============================================
# 问题10: errorhandler 装饰器 (#4295)
# ============================================
# 应被检测：flask-errorhandler-decorator-type (INFO级别)
@app.errorhandler(404)
def handle_404(e):
    return "Not found", 404

# ============================================
# 问题11: before_request 装饰器 (#4104)
# ============================================
# 应被检测：flask-before-request-decorator-type (INFO级别)
@app.before_request
def before_request():
    pass
