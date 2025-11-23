# Test script to verify Flask json module parameter names
import sys
sys.path.insert(0, "C:\Users\86138\Desktop\thisisfinal\CodeAgent\api\temp_extract\project_20251119_134538_571467_1f92395f\flask-2.0.0\src")
from flask.json import htmlsafe_dump, htmlsafe_dumps, dump, dumps, load, loads

# Check function signatures
import inspect
functions = [htmlsafe_dump, htmlsafe_dumps, dump, dumps, load, loads]
for func in functions:
    sig = inspect.signature(func)
    print(f"{func.__name__}: {sig}")
    for param_name, param in sig.parameters.items():
        if param_name != param_name.lower() or "_" not in param_name:
            print(f"  WARNING: Parameter '{param_name}' may not follow snake_case")
