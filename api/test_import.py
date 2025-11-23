import sys
sys.path.insert(0, r"C:\Users\86138\Desktop\thisisfinal\CodeAgent\api\temp_extract\project_20251119_134538_571467_1f92395f\flask-2.0.0\src")
try:
    from flask.cli import cli
    print("SUCCESS: Flask CLI imported successfully")
    print("SUCCESS: _app_ctx_stack import is at top level")
except ImportError as e:
    print(f"ERROR: {e}")
except Exception as e:
    print(f"OTHER ERROR: {e}")
