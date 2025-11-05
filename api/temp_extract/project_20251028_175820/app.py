"""
Flask 2.0.0 Bug Test Application
Based on Flask version selection and Issue strategy.md 32 bug checklist test cases
"""
from flask import Flask, g, jsonify, send_file, send_from_directory, Blueprint, request, session
import decimal
import functools
from typing import NamedTuple

app = Flask(__name__)

# Bug Test: Static Type Related
# Bug #1: Top-level export name type check visibility
# Bug #2: g type hint as namespace object
@app.route('/bug1_g_type')
def bug1_g_type():
    """Test g object type hint issue"""
    g.user_id = 123  # Type checker cannot recognize in 2.0.0
    g.data = {"key": "value"}
    return f"g.user_id: {g.user_id}, g.data: {g.data}"

# Bug #4, #6: send_file/send_from_directory type improvement
@app.route('/bug4_send_file_type')
def bug4_send_file_type():
    """Test send_file type issue"""
    # In 2.0.0, send_file has incomplete type hints
    return send_file('static/test.txt', mimetype='text/plain')

@app.route('/bug6_send_from_directory_type')
def bug6_send_from_directory_type():
    """Test send_from_directory type issue"""
    # Type hints missing for send_from_directory
    return send_from_directory('static', 'test.txt')

# Bug #7: Blueprint prefix merging issue
# Bug #8: Blueprint naming constraint
blueprint1 = Blueprint('test1', __name__, url_prefix='/api')
blueprint2 = Blueprint('test2', __name__, url_prefix='/api')  # Same prefix issue

@blueprint1.route('/users')
def users():
    return jsonify({"users": []})

@blueprint2.route('/posts')
def posts():
    return jsonify({"posts": []})

app.register_blueprint(blueprint1)
app.register_blueprint(blueprint2)  # Bug #7: Prefix merging

# Bug #9: send_from_directory path traversal
@app.route('/bug9_path_traversal')
def bug9_path_traversal():
    """Test path traversal vulnerability"""
    filename = request.args.get('file', 'test.txt')
    # Bug: No path validation in 2.0.0
    return send_from_directory('static', filename)

# Bug #11: Decorator type issue
def custom_decorator(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function

@app.route('/bug11_decorator_type')
@custom_decorator
def bug11_decorator_type():
    """Test decorator type issue"""
    return "Decorator test"

# Bug #14-17: Various decorator type issues
def auth_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('user_id'):
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @functools.wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('is_admin'):
            return jsonify({"error": "Admin required"}), 403
        return f(*args, **kwargs)
    return decorated

@app.route('/bug14_auth_decorator')
@auth_required
def bug14_auth_decorator():
    """Test auth decorator type"""
    return jsonify({"user": session.get('user_id')})

@app.route('/bug15_admin_decorator')
@admin_required
def bug15_admin_decorator():
    """Test admin decorator type"""
    return jsonify({"admin": True})

@app.route('/bug16_multiple_decorators')
@auth_required
@admin_required
def bug16_multiple_decorators():
    """Test multiple decorators type"""
    return jsonify({"message": "Admin access granted"})

@app.route('/bug17_nested_decorators')
@custom_decorator
@auth_required
def bug17_nested_decorators():
    """Test nested decorators type"""
    return jsonify({"message": "Nested decorators"})

# Bug #18: Blueprint duplicate registration
blueprint_duplicate = Blueprint('duplicate', __name__)

@blueprint_duplicate.route('/duplicate')
def duplicate_route():
    return "Duplicate blueprint"

# This will cause issues in 2.0.0
app.register_blueprint(blueprint_duplicate)
# app.register_blueprint(blueprint_duplicate)  # Bug #18: Duplicate registration

# Bug #20: jsonify Decimal serialization
@app.route('/bug20_jsonify_decimal')
def bug20_jsonify_decimal():
    """Test jsonify Decimal serialization issue"""
    # Bug: Decimal not properly serialized in 2.0.0
    price = decimal.Decimal('19.99')
    return jsonify({"price": price})

# Bug #21: Request context type issues
@app.route('/bug21_request_context')
def bug21_request_context():
    """Test request context type issues"""
    # Bug: Request context type hints incomplete
    user_agent = request.headers.get('User-Agent')
    remote_addr = request.remote_addr
    return jsonify({
        "user_agent": user_agent,
        "remote_addr": remote_addr
    })

# Bug #22: Session type issues
@app.route('/bug22_session_type')
def bug22_session_type():
    """Test session type issues"""
    # Bug: Session type hints incomplete
    session['user_id'] = 123
    session['username'] = 'testuser'
    return jsonify({"session": dict(session)})

# Bug #23: Blueprint before_request type
@blueprint1.before_request
def before_request():
    """Test blueprint before_request type"""
    g.request_start_time = 1234567890

# Bug #24: Blueprint after_request type
@blueprint1.after_request
def after_request(response):
    """Test blueprint after_request type"""
    response.headers['X-Custom'] = 'test'
    return response

# Bug #25: Blueprint teardown_request type
@blueprint1.teardown_request
def teardown_request(exception):
    """Test blueprint teardown_request type"""
    pass

# Bug #26: App context type issues
@app.route('/bug26_app_context')
def bug26_app_context():
    """Test app context type issues"""
    # Bug: App context type hints incomplete
    with app.app_context():
        return jsonify({"context": "app"})

# Bug #27: Request context type issues
@app.route('/bug27_request_context')
def bug27_request_context():
    """Test request context type issues"""
    # Bug: Request context type hints incomplete
    with app.test_request_context():
        return jsonify({"context": "request"})

# Bug #28: Test client type issues
@app.route('/bug28_test_client')
def bug28_test_client():
    """Test test client type issues"""
    # Bug: Test client type hints incomplete
    client = app.test_client()
    response = client.get('/bug1_g_type')
    return jsonify({"status": response.status_code})

# Bug #29: Config type issues
@app.route('/bug29_config_type')
def bug29_config_type():
    """Test config type issues"""
    # Bug: Config type hints incomplete
    debug_mode = app.config.get('DEBUG', False)
    secret_key = app.config.get('SECRET_KEY', 'default')
    return jsonify({
        "debug": debug_mode,
        "has_secret": bool(secret_key)
    })

# Bug #30: URL building type issues
@app.route('/bug30_url_building')
def bug30_url_building():
    """Test URL building type issues"""
    # Bug: URL building type hints incomplete
    from flask import url_for
    user_url = url_for('bug1_g_type')
    return jsonify({"url": user_url})

# Bug #31: Error handler type issues
@app.errorhandler(404)
def bug31_error_handler(error):
    """Test error handler type issues"""
    # Bug: Error handler type hints incomplete
    return jsonify({"error": "Not found"}), 404

# Bug #32: Template rendering type issues
@app.route('/bug32_template_type')
def bug32_template_type():
    """Test template rendering type issues"""
    # Bug: Template rendering type hints incomplete
    from flask import render_template_string
    template = "<h1>Hello {{ name }}</h1>"
    return render_template_string(template, name="World")

# Additional NamedTuple test for type checking
class UserData(NamedTuple):
    user_id: int
    username: str
    email: str

@app.route('/bug_namedtuple_type')
def bug_namedtuple_type():
    """Test NamedTuple type with Flask"""
    user = UserData(1, "testuser", "test@example.com")
    return jsonify({
        "user_id": user.user_id,
        "username": user.username,
        "email": user.email
    })

# Main route for testing
@app.route('/')
def index():
    """Main test route"""
    return jsonify({
        "message": "Flask 2.0.0 Bug Test Application",
        "bugs_tested": 32,
        "version": "2.0.0"
    })

# Health check route
@app.route('/health')
def health():
    """Health check route"""
    return jsonify({"status": "healthy", "version": "2.0.0"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)