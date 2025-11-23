import sys
import os
sys.path.insert(0, r"C:\Users\86138\Desktop\thisisfinal\CodeAgent\api\temp_extract\project_20251119_134538_571467_1f92395f\flask-2.0.0\src")
from flask import Flask, flash

app = Flask(__name__)
app.secret_key = 'test'

with app.app_context():
    flash("Test message", "info")
    print("Flash function executed successfully")
