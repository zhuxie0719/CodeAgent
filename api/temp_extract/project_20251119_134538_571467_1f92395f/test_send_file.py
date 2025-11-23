import sys
sys.path.insert(0, r"C:\Users\86138\Desktop\thisisfinal\CodeAgent\api\temp_extract\project_20251119_134538_571467_1f92395f\flask-2.0.0\src")
from flask import Flask, helpers
import tempfile
import os

# Test that the function can be imported and called
app = Flask(__name__)

with app.test_request_context():
    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as f:
        f.write(b"Test content")
        temp_path = f.name
    
    try:
        # Test calling send_file with various parameters using kwargs
        response = helpers.send_file(
            temp_path,
            mimetype='text/plain',
            as_attachment=True,
            download_name='test.txt',
            conditional=True,
            etag=True,
            last_modified=None,
            max_age=3600
        )
        print("SUCCESS: send_file works with kwargs")
        print(f"Response status: {response.status_code}")
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.unlink(temp_path)
