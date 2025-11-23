import sys
import os
sys.path.insert(0, r"C:\Users\86138\Desktop\thisisfinal\CodeAgent\api\temp_extract\project_20251119_134538_571467_1f92395f\flask-2.0.0\src")
from flask import Flask, url_for
app = Flask(__name__)

# Try to trigger the handle_url_build_error method
try:
    with app.app_context():
        print(url_for('nonexistent_endpoint'))
except Exception as e:
    print(f"Error occurred: {e}")
