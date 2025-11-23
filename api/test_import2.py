import sys
sys.path.insert(0, r"C:\Users\86138\Desktop\thisisfinal\CodeAgent\api\temp_extract\project_20251119_134538_571467_1f92395f\flask-2.0.0\src")
try:
    # Just test the import of _app_ctx_stack from cli module
    import flask.cli
    print("SUCCESS: Flask CLI module imported")
    # Check if _app_ctx_stack is imported at top level
    if hasattr(flask.cli, '_app_ctx_stack'):
        print("SUCCESS: _app_ctx_stack is available at module level")
    else:
        # Check the import in the source
        import inspect
        source = inspect.getsource(flask.cli)
        if 'from .globals import _app_ctx_stack' in source:
            print("SUCCESS: _app_ctx_stack import found at top level in source")
        else:
            print("ERROR: _app_ctx_stack import not found at top level")
except Exception as e:
    print(f"ERROR: {e}")
