#!/usr/bin/env python3
"""
Werkzeug兼容性补丁
解决Flask与Werkzeug版本兼容性问题
"""

def apply_werkzeug_compatibility_patch():
    """应用Werkzeug兼容性补丁"""
    try:
        import werkzeug.urls
        from urllib.parse import quote as url_quote, urlparse as url_parse
        
        # 检查是否需要补丁
        patches_applied = []
        
        if not hasattr(werkzeug.urls, 'url_quote'):
            print("🔧 应用url_quote补丁...")
            werkzeug.urls.url_quote = url_quote
            patches_applied.append("url_quote")
            
        if not hasattr(werkzeug.urls, 'url_parse'):
            print("🔧 应用url_parse补丁...")
            werkzeug.urls.url_parse = url_parse
            patches_applied.append("url_parse")
            
        if patches_applied:
            print(f"✅ Werkzeug兼容性补丁应用成功: {', '.join(patches_applied)}")
            return True
        else:
            print("✅ Werkzeug版本兼容，无需补丁")
            return True
            
    except ImportError as e:
        print(f"⚠️ 无法应用Werkzeug兼容性补丁: {e}")
        return False

def check_flask_werkzeug_compatibility():
    """检查Flask和Werkzeug版本兼容性"""
    try:
        import flask
        import werkzeug
        
        flask_version = getattr(flask, '__version__', 'unknown')
        werkzeug_version = getattr(werkzeug, '__version__', 'unknown')
        
        print(f"📦 Flask版本: {flask_version}")
        print(f"📦 Werkzeug版本: {werkzeug_version}")
        
        # 检查关键兼容性问题
        compatibility_issues = []
        
        try:
            from werkzeug.urls import url_quote
        except ImportError:
            compatibility_issues.append("url_quote函数不可用")
        
        if compatibility_issues:
            print("⚠️ 检测到兼容性问题:")
            for issue in compatibility_issues:
                print(f"   - {issue}")
            return False
        else:
            print("✅ Flask和Werkzeug版本兼容")
            return True
            
    except ImportError as e:
        print(f"❌ 无法检查版本兼容性: {e}")
        return False

if __name__ == "__main__":
    print("🔍 检查Flask和Werkzeug兼容性...")
    if not check_flask_werkzeug_compatibility():
        print("\n🔧 尝试应用兼容性补丁...")
        apply_werkzeug_compatibility_patch()
