#!/usr/bin/env python3
"""
简单的Flask应用用于测试动态检测功能
"""

from pathlib import Path

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

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

def create_app():
    """创建Flask应用"""
    try:
        from flask import Flask, jsonify

        app = Flask(__name__)

        @app.route('/')
        def home():
            return jsonify({
                "message": "Flask应用运行正常",
                "version": "2.0.0",
                "status": "healthy"
            })

        @app.route('/health')
        def health():
            return jsonify({
                "status": "healthy",
                "service": "flask_simple_test"
            })

        @app.route('/api/status')
        def api_status():
            return jsonify({
                "api_version": "1.0.0",
                "endpoints": ["/", "/health", "/api/status"]
            })

        return app
    except ImportError as e:
        print(f"❌ Flask导入失败: {e}")
        print("请安装Flask: pip install flask")
        return None

def main():
    """主函数"""
    print("🚀 启动Flask应用...")

    app = create_app()
    if app is None:
        return

    # 获取端口配置
    port = int(os.environ.get('FLASK_PORT', os.environ.get('PORT', 5000)))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    print(f"📍 启动端口: {port}")
    print(f"🔧 调试模式: {debug}")
    print(f"🌐 访问地址: http://localhost:{port}")

    try:
        app.run(host='0.0.0.0', port=port, debug=debug)
    except (OSError, RuntimeError, ImportError) as e:
        print(f"❌ Flask应用启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
