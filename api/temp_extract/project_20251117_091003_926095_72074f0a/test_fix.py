import sys
sys.path.insert(0, r"C:\Users\86138\Desktop\thisisfinal\CodeAgent\api\temp_extract\project_20251117_091003_926095_72074f0a\flask-2.0.0\src")
try:
    from flask import Flask
    print("SUCCESS: Flask app.py syntax is valid - no bare raise error")
except SyntaxError as e:
    print(f"FAILED: Syntax error - {e}")
except Exception as e:
    print(f"OTHER ERROR: {e}")
