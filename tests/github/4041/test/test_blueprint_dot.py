#!/usr/bin/env python3
"""
Test script to reproduce the blueprint name with dot issue.
"""
from flask import Flask, Blueprint

def test_blueprint_with_dot():
    """Test that creating a blueprint with a dot in the name raises an error."""
    try:
        # This should raise an error
        bp = Blueprint("my.blueprint", __name__)
        print("ERROR: Blueprint with dot in name was created without error")
        return False
    except ValueError as e:
        print(f"SUCCESS: Correctly raised ValueError: {e}")
        return True
    except Exception as e:
        print(f"ERROR: Unexpected exception: {e}")
        return False

def test_blueprint_without_dot():
    """Test that creating a blueprint without a dot in the name works normally."""
    try:
        bp = Blueprint("my_blueprint", __name__)
        print("SUCCESS: Blueprint without dot in name was created normally")
        return True
    except Exception as e:
        print(f"ERROR: Unexpected exception for valid blueprint name: {e}")
        return False

if __name__ == "__main__":
    print("Testing blueprint name validation...")
    test1 = test_blueprint_with_dot()
    test2 = test_blueprint_without_dot()
    
    if test1 and test2:
        print("\nAll tests passed!")
    else:
        print("\nSome tests failed!")
