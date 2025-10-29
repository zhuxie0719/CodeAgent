#!/usr/bin/env python3
"""
Test edge cases for the fixed get_send_file_max_age typing
"""
import sys
import os
sys.path.insert(0, '/home/baiqinyu/Desktop/project/CodeAgent/tests/flask-2.0.0/src')

from flask import Flask
import typing as t

def test_edge_cases():
    app = Flask(__name__)
    
    # Test with different configurations
    test_cases = [
        # (config_value, expected_result_description)
        (None, "None (default)"),
        (3600, "integer seconds"),
        (60.5, "float seconds"),
    ]
    
    for config_val, desc in test_cases:
        print(f"\nTesting with config value: {desc}")
        app.config['SEND_FILE_MAX_AGE_DEFAULT'] = config_val
        
        with app.app_context():
            # Test various filename inputs
            inputs = ["file.txt", "", None, "path/to/file.jpg"]
            
            for filename in inputs:
                try:
                    result = app.get_send_file_max_age(filename)
                    print(f"  filename={repr(filename)} -> {result}")
                except Exception as e:
                    print(f"  filename={repr(filename)} -> ERROR: {e}")

if __name__ == "__main__":
    test_edge_cases()
