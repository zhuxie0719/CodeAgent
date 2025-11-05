#!/usr/bin/env python3
"""
Test script to reproduce the get_send_file_max_age typing issue.
The function should accept an optional string and return an optional int.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from flask import Flask
from typing import Optional

# Test the typing issue
app = Flask(__name__)

# Test 1: Check current typing signature
import inspect
sig = inspect.signature(app.get_send_file_max_age)
print(f"Current signature: {sig}")

# Test 2: Try calling with different parameter types
with app.app_context():
    try:
        # Test with string
        result1 = app.get_send_file_max_age("test.txt")
        print(f"Test with string: {result1} (type: {type(result1)})")
        
        # Test with None - this should work but currently might not due to typing
        try:
            result2 = app.get_send_file_max_age(None)
            print(f"Test with None: {result2} (type: {type(result2)})")
        except Exception as e:
            print(f"Error with None parameter: {e}")
            
        # Test with no parameter (should fail)
        try:
            result3 = app.get_send_file_max_age()
            print(f"Test with no parameter: {result3}")
        except Exception as e:
            print(f"Expected error with no parameter: {e}")
            
    except Exception as e:
        print(f"General error: {e}")

