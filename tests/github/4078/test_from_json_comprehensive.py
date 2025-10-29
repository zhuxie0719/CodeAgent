#!/usr/bin/env python3
"""Comprehensive test for the deprecated from_json method"""

import sys
import os
import tempfile
import json
import warnings

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from flask import Flask

def test_from_json_with_file():
    """Test from_json with actual JSON file"""
    app = Flask(__name__)
    
    # Create a temporary JSON file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"TEST_KEY": "test_value", "ANOTHER_KEY": 123}, f)
        temp_file = f.name
    
    try:
        # Capture deprecation warning
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = app.config.from_json(temp_file)
            
            # Check if deprecation warning was raised
            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "Config.from_json is deprecated" in str(w[0].message)
            print("✓ Deprecation warning correctly raised")
        
        # Check if config was loaded
        assert result == True
        assert app.config['TEST_KEY'] == 'test_value'
        assert app.config['ANOTHER_KEY'] == 123
        print("✓ Config values correctly loaded from JSON file")
        
    finally:
        # Clean up
        os.unlink(temp_file)

def test_from_json_silent():
    """Test from_json with silent=True for missing file"""
    app = Flask(__name__)
    
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = app.config.from_json("nonexistent_file.json", silent=True)
        
        # Should return False for missing file with silent=True
        assert result == False
        assert len(w) == 1  # Still should show deprecation warning
        print("✓ Silent mode works correctly for missing files")

def test_from_json_not_silent():
    """Test from_json raises error for missing file when not silent"""
    app = Flask(__name__)
    
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        try:
            result = app.config.from_json("nonexistent_file.json", silent=False)
            assert False, "Should have raised an exception"
        except OSError:
            assert len(w) == 1  # Should still show deprecation warning
            print("✓ Correctly raises error for missing files when not silent")

def test_alternative_method():
    """Test the recommended alternative method"""
    app = Flask(__name__)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({"ALTERNATIVE_KEY": "alternative_value"}, f)
        temp_file = f.name
    
    try:
        result = app.config.from_file(temp_file, load=json.load)
        assert result == True
        assert app.config['ALTERNATIVE_KEY'] == 'alternative_value'
        print("✓ Alternative method (from_file with json.load) works correctly")
        
    finally:
        os.unlink(temp_file)

if __name__ == "__main__":
    print("Running comprehensive from_json tests...")
    test_from_json_with_file()
    test_from_json_silent()
    test_from_json_not_silent()
    test_alternative_method()
    print("\\nAll tests passed! The from_json method is properly deprecated.")
