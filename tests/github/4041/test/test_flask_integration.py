#!/usr/bin/env python3
"""
Test that the blueprint fix integrates properly with Flask.
"""
from flask import Flask, Blueprint

def test_flask_integration():
    """Test that Flask can register blueprints normally after the fix."""
    app = Flask(__name__)
    
    # Create a valid blueprint
    bp = Blueprint("valid_bp", __name__)
    
    @bp.route('/')
    def index():
        return "Hello from blueprint"
    
    # Register the blueprint
    app.register_blueprint(bp, url_prefix='/blueprint')
    
    # Test that the app works
    with app.test_client() as client:
        response = client.get('/blueprint/')
        if response.status_code == 200 and b"Hello from blueprint" in response.data:
            print("SUCCESS: Flask integration test passed")
            return True
        else:
            print("ERROR: Flask integration test failed")
            return False

if __name__ == "__main__":
    print("Testing Flask integration...")
    if test_flask_integration():
        print("Flask integration test completed successfully!")
    else:
        print("Flask integration test failed!")
