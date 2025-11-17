import sys
print("Python path:")
for path in sys.path:
    print(f"  {path}")

try:
    import flask
    print("Flask imported successfully")
except ImportError as e:
    print(f"Flask import error: {e}")

try:
    import conftest
    print("conftest imported successfully")
except ImportError as e:
    print(f"conftest import error: {e}")
