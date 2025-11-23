import sys
import os
sys.path.insert(0, r"C:\Users\86138\Desktop\thisisfinal\CodeAgent\api\temp_extract\project_20251119_134538_571467_1f92395f\flask-2.0.0\src")

try:
    from flask import Flask
    from werkzeug.exceptions import HTTPException, BadRequest, NotFound
    
    app = Flask(__name__)
    
    @app.route('/')
    def index():
        return "Hello World"
    
    @app.route('/bad')
    def bad_route():
        raise BadRequest("This is a bad request")
    
    @app.route('/notfound')
    def notfound_route():
        raise NotFound("This resource was not found")
    
    # Test normal request
    with app.test_client() as client:
        response = client.get('/')
        print(f"Normal route status: {response.status_code}")
        assert response.status_code == 200
    
    # Test HTTPException handling
    with app.test_client() as client:
        response = client.get('/bad')
        print(f"BadRequest route status: {response.status_code}")
        assert response.status_code == 400
    
    # Test another HTTPException
    with app.test_client() as client:
        response = client.get('/notfound')
        print(f"NotFound route status: {response.status_code}")
        assert response.status_code == 404
    
    print("All tests passed! The fix works correctly.")
    
except Exception as e:
    print(f"Error during test: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
