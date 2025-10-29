from flask import Flask
import inspect
from flask.typing import TeardownCallable

app = Flask(__name__)

def check_teardown_type(f):
    """Check if a function matches the TeardownCallable type"""
    sig = inspect.signature(f)
    return_annotation = sig.return_annotation
    
    print(f"Function: {f.__name__}")
    print(f"  Signature: {sig}")
    print(f"  Return annotation: {return_annotation}")
    print(f"  Matches TeardownCallable: {isinstance(f, TeardownCallable)}")
    print()

# Test different teardown function signatures
def teardown_none(exc):
    return None

def teardown_string(exc):
    return "string"

def teardown_int(exc):
    return 42

def teardown_response(exc):
    from flask import Response
    return Response("response")

print("Checking teardown function types:")
check_teardown_type(teardown_none)
check_teardown_type(teardown_string)
check_teardown_type(teardown_int)
check_teardown_type(teardown_response)

print("\\nNow testing with decorator...")
try:
    @app.teardown_appcontext
    def decorated_none(exc):
        return None
    print("✓ Decorated function with None return works")
except Exception as e:
    print(f"✗ Decorated function with None return failed: {e}")

try:
    @app.teardown_appcontext
    def decorated_string(exc):
        return "string"
    print("✓ Decorated function with string return works")
except Exception as e:
    print(f"✗ Decorated function with string return failed: {e}")
