from flask import Flask

app = Flask(__name__)

print("Testing teardown decorator with different return types...")

# Test 1: Function returning None (should work)
try:
    @app.teardown_appcontext
    def teardown_none(exc):
        return None
    print("✓ Function returning None: Decorator accepted")
except Exception as e:
    print(f"✗ Function returning None: {e}")

# Test 2: Function returning string (should work)  
try:
    @app.teardown_appcontext
    def teardown_string(exc):
        return "string"
    print("✓ Function returning string: Decorator accepted")
except Exception as e:
    print(f"✗ Function returning string: {e}")

# Test 3: Function returning int (should work)
try:
    @app.teardown_appcontext
    def teardown_int(exc):
        return 42
    print("✓ Function returning int: Decorator accepted")
except Exception as e:
    print(f"✗ Function returning int: {e}")

# Test 4: Function returning Response (should work)
try:
    @app.teardown_appcontext
    def teardown_response(exc):
        from flask import Response
        return Response("response")
    print("✓ Function returning Response: Decorator accepted")
except Exception as e:
    print(f"✗ Function returning Response: {e}")

print("\\nAll decorator tests completed.")
