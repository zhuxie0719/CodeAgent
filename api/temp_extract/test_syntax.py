# Simple syntax check for the modified file
import ast
try:
    with open(r"C:\Users\86138\Desktop\thisisfinal\CodeAgent\api\temp_extract\project_20251117_091003_926095_72074f0a\flask-2.0.0\src\flask\helpers.py", "r") as f:
        source = f.read()
    ast.parse(source)
    print("SUCCESS: Python syntax is valid")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
