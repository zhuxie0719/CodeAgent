"""
Flask D类问题检测器
专门检测Flask 2.0.0中的D类问题（需要动态验证的问题）
"""

import asyncio
import subprocess
import tempfile
import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import sys


class FlaskDClassDetector:
    """Flask D类问题检测器"""
    
    def __init__(self):
        self.d_class_issues = [
            {
                "id": 27,
                "title": "URL匹配顺序恢复为在session加载之后",
                "description": "依赖会话/上下文的URL转换器在复杂场景下行为异常",
                "github_link": "https://github.com/pallets/flask/issues/4053",
                "test_code": self._test_url_matching_order,
                "severity": "high"
            },
            {
                "id": 28,
                "title": "View/MethodView支持async处理器",
                "description": "异步handler的生命周期与上下文互动需要动态校验",
                "github_link": "https://github.com/pallets/flask/issues/4112",
                "test_code": self._test_async_view_support,
                "severity": "high"
            },
            {
                "id": 29,
                "title": "回调触发顺序：before_request从app到最近的嵌套蓝图",
                "description": "复杂多蓝图层级下的触发顺序需端到端验证",
                "github_link": "https://github.com/pallets/flask/issues/4229",
                "test_code": self._test_callback_order,
                "severity": "medium"
            },
            {
                "id": 30,
                "title": "after_this_request在非请求上下文下的报错信息改进",
                "description": "在复杂调用链/测试场景下触发，需运行时验证",
                "github_link": "https://github.com/pallets/flask/issues/4333",
                "test_code": self._test_after_request_context,
                "severity": "medium"
            },
            {
                "id": 31,
                "title": "嵌套蓝图合并URL前缀（复杂路由验证）",
                "description": "多级蓝图前缀未正确合并导致复杂路由树失配",
                "github_link": "https://github.com/pallets/flask/issues/4037",
                "test_code": self._test_nested_blueprint_url_prefix,
                "severity": "high"
            },
            {
                "id": 32,
                "title": "嵌套蓝图（复杂命名验证）",
                "description": "嵌套后端点命名冲突或url_for反解异常",
                "github_link": "https://github.com/pallets/flask/issues/4069",
                "test_code": self._test_nested_blueprint_naming,
                "severity": "high"
            }
        ]
    
    async def detect_d_class_issues(self, project_path: str) -> Dict[str, Any]:
        """检测Flask D类问题"""
        results = {
            "detection_type": "flask_d_class",
            "timestamp": datetime.now().isoformat(),
            "project_path": project_path,
            "issues_found": [],
            "tests_performed": [],
            "summary": {
                "total_issues": 0,
                "high_severity": 0,
                "medium_severity": 0,
                "low_severity": 0
            }
        }
        
        print("🔍 开始检测Flask D类问题...")
        
        for issue in self.d_class_issues:
            try:
                print(f"测试问题 {issue['id']}: {issue['title']}")
                
                # 创建测试文件
                test_file = await self._create_test_file(issue, project_path)
                
                # 执行测试
                test_result = await self._run_test(test_file, issue)
                
                if test_result["detected"]:
                    results["issues_found"].append({
                        "issue_id": issue["id"],
                        "title": issue["title"],
                        "description": issue["description"],
                        "github_link": issue["github_link"],
                        "severity": issue["severity"],
                        "test_result": test_result,
                        "detection_method": "dynamic_test"
                    })
                    
                    results["summary"]["total_issues"] += 1
                    if issue["severity"] == "high":
                        results["summary"]["high_severity"] += 1
                    elif issue["severity"] == "medium":
                        results["summary"]["medium_severity"] += 1
                    else:
                        results["summary"]["low_severity"] += 1
                
                results["tests_performed"].append({
                    "issue_id": issue["id"],
                    "test_result": test_result
                })
                
                # 清理测试文件
                if os.path.exists(test_file):
                    os.remove(test_file)
                    
            except Exception as e:
                print(f"测试问题 {issue['id']} 时出错: {e}")
                results["tests_performed"].append({
                    "issue_id": issue["id"],
                    "error": str(e)
                })
        
        print(f"✅ Flask D类问题检测完成，发现 {results['summary']['total_issues']} 个问题")
        return results
    
    async def _create_test_file(self, issue: Dict[str, Any], project_path: str) -> str:
        """创建测试文件"""
        test_code = issue["test_code"]()
        
        # 创建临时测试文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            return f.name
    
    async def _run_test(self, test_file: str, issue: Dict[str, Any]) -> Dict[str, Any]:
        """运行测试"""
        try:
            # 执行测试文件
            result = subprocess.run(
                [sys.executable, test_file],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return {
                "detected": result.returncode != 0,  # 非零退出码表示检测到问题
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "test_passed": result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            return {
                "detected": True,
                "error": "测试超时",
                "test_passed": False
            }
        except Exception as e:
            return {
                "detected": True,
                "error": str(e),
                "test_passed": False
            }
    
    def _test_url_matching_order(self) -> str:
        """测试URL匹配顺序问题"""
        return '''
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from flask import Flask, url_for, session
    from werkzeug.routing import Rule
    
    app = Flask(__name__)
    app.secret_key = 'test'
    
    # 创建自定义URL转换器
    class CustomConverter:
        def to_python(self, value):
            # 依赖session的转换器
            if 'user_id' not in session:
                raise ValueError("Session not available")
            return value
    
    # 注册转换器
    app.url_map.converters['custom'] = CustomConverter
    
    @app.route('/user/<custom:user_id>')
    def user_profile(user_id):
        return f"User: {user_id}"
    
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['user_id'] = '123'
        
        # 测试URL生成
        with app.test_request_context():
            url = url_for('user_profile', user_id='123')
            print(f"URL generated: {url}")
            
        # 测试URL匹配
        response = client.get('/user/123')
        if response.status_code != 200:
            print(f"ERROR: URL matching failed, status: {response.status_code}")
            sys.exit(1)
        else:
            print("SUCCESS: URL matching works correctly")
            sys.exit(0)
            
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
'''
    
    def _test_async_view_support(self) -> str:
        """测试异步视图支持"""
        return '''
import sys
import os
import asyncio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from flask import Flask
    
    app = Flask(__name__)
    
    # 测试异步视图
    @app.route('/async')
    async def async_view():
        await asyncio.sleep(0.1)
        return "Async response"
    
    # 测试同步视图
    @app.route('/sync')
    def sync_view():
        return "Sync response"
    
    with app.test_client() as client:
        # 测试同步视图
        response = client.get('/sync')
        if response.status_code != 200:
            print(f"ERROR: Sync view failed, status: {response.status_code}")
            sys.exit(1)
        
        # 测试异步视图（在Flask 2.0.0中可能不支持）
        try:
            response = client.get('/async')
            if response.status_code == 200:
                print("SUCCESS: Async view supported")
                sys.exit(0)
            else:
                print(f"ERROR: Async view failed, status: {response.status_code}")
                sys.exit(1)
        except Exception as e:
            print(f"ERROR: Async view not supported: {e}")
            sys.exit(1)
            
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
'''
    
    def _test_callback_order(self) -> str:
        """测试回调触发顺序"""
        return '''
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from flask import Flask, Blueprint
    
    app = Flask(__name__)
    
    # 创建嵌套蓝图
    parent_bp = Blueprint('parent', __name__, url_prefix='/parent')
    child_bp = Blueprint('child', __name__, url_prefix='/child')
    
    # 注册回调
    callbacks = []
    
    @app.before_request
    def app_before_request():
        callbacks.append('app_before_request')
    
    @parent_bp.before_request
    def parent_before_request():
        callbacks.append('parent_before_request')
    
    @child_bp.before_request
    def child_before_request():
        callbacks.append('child_before_request')
    
    @child_bp.route('/test')
    def test_route():
        return "Test"
    
    # 注册蓝图
    parent_bp.register_blueprint(child_bp)
    app.register_blueprint(parent_bp)
    
    with app.test_client() as client:
        response = client.get('/parent/child/test')
        
        # 检查回调顺序
        expected_order = ['app_before_request', 'parent_before_request', 'child_before_request']
        
        if callbacks == expected_order:
            print("SUCCESS: Callback order is correct")
            sys.exit(0)
        else:
            print(f"ERROR: Callback order incorrect. Expected: {expected_order}, Got: {callbacks}")
            sys.exit(1)
            
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
'''
    
    def _test_after_request_context(self) -> str:
        """测试after_this_request上下文问题"""
        return '''
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from flask import Flask, after_this_request
    
    app = Flask(__name__)
    
    @app.route('/test')
    def test_route():
        @after_this_request
        def after_request(response):
            response.headers['X-Test'] = 'test'
            return response
        return "Test"
    
    # 测试在请求上下文外使用after_this_request
    try:
        with app.app_context():
            @after_this_request
            def invalid_after_request(response):
                return response
        print("ERROR: after_this_request should fail outside request context")
        sys.exit(1)
    except RuntimeError as e:
        if "after_this_request" in str(e):
            print("SUCCESS: after_this_request properly validates context")
            sys.exit(0)
        else:
            print(f"ERROR: Unexpected error: {e}")
            sys.exit(1)
    except Exception as e:
        print(f"ERROR: Unexpected exception: {e}")
        sys.exit(1)
            
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
'''
    
    def _test_nested_blueprint_url_prefix(self) -> str:
        """测试嵌套蓝图URL前缀合并"""
        return '''
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from flask import Flask, Blueprint, url_for
    
    app = Flask(__name__)
    
    # 创建嵌套蓝图
    level1_bp = Blueprint('level1', __name__, url_prefix='/level1')
    level2_bp = Blueprint('level2', __name__, url_prefix='/level2')
    level3_bp = Blueprint('level3', __name__, url_prefix='/level3')
    
    @level3_bp.route('/test')
    def test_route():
        return "Test"
    
    # 注册嵌套蓝图
    level2_bp.register_blueprint(level3_bp)
    level1_bp.register_blueprint(level2_bp)
    app.register_blueprint(level1_bp)
    
    with app.test_client() as client:
        # 测试URL生成
        with app.test_request_context():
            url = url_for('level3.test_route')
            expected_url = '/level1/level2/level3/test'
            
            if url == expected_url:
                print("SUCCESS: Nested blueprint URL prefix merging works correctly")
                sys.exit(0)
            else:
                print(f"ERROR: URL prefix merging failed. Expected: {expected_url}, Got: {url}")
                sys.exit(1)
                
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
'''
    
    def _test_nested_blueprint_naming(self) -> str:
        """测试嵌套蓝图命名问题"""
        return '''
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from flask import Flask, Blueprint, url_for
    
    app = Flask(__name__)
    
    # 创建同名蓝图
    bp1 = Blueprint('test', __name__, url_prefix='/test1')
    bp2 = Blueprint('test', __name__, url_prefix='/test2')
    
    @bp1.route('/route1')
    def route1():
        return "Route 1"
    
    @bp2.route('/route2')
    def route2():
        return "Route 2"
    
    # 注册蓝图
    app.register_blueprint(bp1)
    app.register_blueprint(bp2)
    
    with app.test_client() as client:
        # 测试URL生成
        with app.test_request_context():
            try:
                url1 = url_for('test.route1')
                url2 = url_for('test.route2')
                
                # 检查是否只有一个路由可用（Flask 2.0.0的问题）
                if url1 == '/test1/route1' and url2 == '/test2/route2':
                    print("SUCCESS: Nested blueprint naming works correctly")
                    sys.exit(0)
                else:
                    print(f"ERROR: Blueprint naming conflict. URL1: {url1}, URL2: {url2}")
                    sys.exit(1)
            except Exception as e:
                print(f"ERROR: Blueprint naming conflict detected: {e}")
                sys.exit(1)
                
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
'''


# 测试函数
async def test_flask_d_class_detector():
    """测试Flask D类问题检测器"""
    detector = FlaskDClassDetector()
    
    # 使用当前目录作为项目路径
    project_path = os.getcwd()
    
    results = await detector.detect_d_class_issues(project_path)
    
    print("\\n" + "="*50)
    print("Flask D类问题检测结果")
    print("="*50)
    print(f"检测到的问题数量: {results['summary']['total_issues']}")
    print(f"高严重性问题: {results['summary']['high_severity']}")
    print(f"中严重性问题: {results['summary']['medium_severity']}")
    print(f"低严重性问题: {results['summary']['low_severity']}")
    
    if results['issues_found']:
        print("\\n发现的问题:")
        for issue in results['issues_found']:
            print(f"- [{issue['severity'].upper()}] {issue['title']}")
            print(f"  GitHub: {issue['github_link']}")
    
    return results


if __name__ == "__main__":
    asyncio.run(test_flask_d_class_detector())




