from flask import Flask

app = Flask(__name__)

# This should work according to docs (returning None)
@app.teardown_appcontext
def teardown_none(exc):
    print("Teardown function returning None")
    return None

# This should work according to docs (returning string)
@app.teardown_appcontext  
def teardown_string(exc):
    print("Teardown function returning string")
    return "This return value should be ignored"

# This should work according to docs (returning int)
@app.teardown_appcontext
def teardown_int(exc):
    print("Teardown function returning int")
    return 42

# This should work (returning Response - current behavior)
@app.teardown_appcontext
def teardown_response(exc):
    print("Teardown function returning Response")
    from flask import Response
    return Response("Response")

if __name__ == "__main__":
    print("Testing teardown functions with different return types...")
    with app.app_context():
        print("App context created")
    print("App context destroyed - teardown functions should have been called")
