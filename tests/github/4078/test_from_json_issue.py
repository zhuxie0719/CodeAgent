#!/usr/bin/env python3
"""Test script to reproduce the from_json deprecation issue"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from flask import Flask

def test_from_json_method():
    app = Flask(__name__)
    
    # Test if from_json method exists
    if hasattr(app.config, 'from_json'):
        print("SUCCESS: from_json method exists")
        try:
            # Try to use it
            result = app.config.from_json('{"TEST": "value"}')
            print(f"from_json worked: {result}")
        except Exception as e:
            print(f"ERROR: from_json failed: {e}")
    else:
        print("ERROR: from_json method does not exist - this is the issue!")
        print("Available config methods:", [m for m in dir(app.config) if not m.startswith('_')])
    
    # Test the recommended alternative
    import json
    if hasattr(app.config, 'from_file'):
        print("\nTesting alternative method from_file with json.load:")
        try:
            # Create a temporary JSON file for testing
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                f.write('{"TEST_ALTERNATIVE": "value"}')
                temp_file = f.name
            
            result = app.config.from_file(temp_file, load=json.load)
            print(f"from_file with json.load worked: {result}")
            print(f"Config value: {app.config.get('TEST_ALTERNATIVE')}")
            
            # Clean up
            os.unlink(temp_file)
        except Exception as e:
            print(f"ERROR: from_file failed: {e}")

if __name__ == "__main__":
    test_from_json_method()
