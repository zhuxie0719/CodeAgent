import sys
sys.path.insert(0, r"C:\Users\86138\Desktop\thisisfinal\CodeAgent\api\temp_extract\project_20251119_134538_571467_1f92395f\flask-2.0.0\src")
try:
    import flask.helpers
    print("SUCCESS: Flask helpers module imported without pylint redefinition error")
except Exception as e:
    print(f"ERROR: {e}")
