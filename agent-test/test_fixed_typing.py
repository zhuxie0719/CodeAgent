#!/usr/bin/env python3
"""
Test script to verify the fixed typing for get_send_file_max_age
"""
import sys
import os
sys.path.insert(0, '/home/baiqinyu/Desktop/project/CodeAgent/tests/flask-2.0.0/src')

from flask import Flask
import typing as t

app = Flask(__name__)

def test_get_send_file_max_age_typing():
    print("Testing get_send_file_max_age with various inputs...")
    
    with app.app_context():
        # Test with string filename
        result1 = app.get_send_file_max_age("test.txt")
        print(f"Result with string 'test.txt': {result1}")
        
        # Test with None filename (should work now)
        result2 = app.get_send_file_max_age(None)
        print(f"Result with None: {result2}")
        
        # Test with empty string
        result3 = app.get_send_file_max_age("")
        print(f"Result with empty string: {result3}")
        
        # Test the typing annotations
        method = app.get_send_file_max_age
        print(f"Method signature: {method.__annotations__}")
        
        # Verify the function accepts Optional[str] and returns Optional[int]
        if 'filename' in method.__annotations__:
            filename_type = method.__annotations__['filename']
            print(f"Filename parameter type: {filename_type}")
        
        if 'return' in method.__annotations__:
            return_type = method.__annotations__['return']
            print(f"Return type: {return_type}")

if __name__ == "__main__":
    test_get_send_file_max_age_typing()
