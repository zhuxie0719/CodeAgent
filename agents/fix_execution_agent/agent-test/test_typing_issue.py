#!/usr/bin/env python3
"""
Test script to reproduce the typing issue with get_send_file_max_age
"""
import sys
import os
sys.path.insert(0, '/home/baiqinyu/Desktop/project/CodeAgent/tests/flask-2.0.0/src')

from flask import Flask

app = Flask(__name__)

# Test the current typing - this should show the issue
def test_get_send_file_max_age_typing():
    # The function should accept an optional string parameter
    # and return an optional int
    result = app.get_send_file_max_age("test.txt")
    print(f"Result with string: {result}")
    
    # This should work but currently the typing doesn't allow None
    try:
        result_none = app.get_send_file_max_age(None)
        print(f"Result with None: {result_none}")
    except Exception as e:
        print(f"Error with None: {e}")

if __name__ == "__main__":
    test_get_send_file_max_age_typing()
