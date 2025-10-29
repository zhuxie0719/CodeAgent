#!/usr/bin/env python3
"""
Test edge cases for blueprint name validation.
"""
from flask import Flask, Blueprint

def test_multiple_dots():
    """Test blueprint name with multiple dots."""
    try:
        bp = Blueprint("my.blueprint.name", __name__)
        print("ERROR: Blueprint with multiple dots was created without error")
        return False
    except ValueError as e:
        print(f"SUCCESS: Correctly raised ValueError for multiple dots: {e}")
        return True

def test_dot_at_start():
    """Test blueprint name starting with a dot."""
    try:
        bp = Blueprint(".myblueprint", __name__)
        print("ERROR: Blueprint starting with dot was created without error")
        return False
    except ValueError as e:
        print(f"SUCCESS: Correctly raised ValueError for dot at start: {e}")
        return True

def test_dot_at_end():
    """Test blueprint name ending with a dot."""
    try:
        bp = Blueprint("myblueprint.", __name__)
        print("ERROR: Blueprint ending with dot was created without error")
        return False
    except ValueError as e:
        print(f"SUCCESS: Correctly raised ValueError for dot at end: {e}")
        return True

def test_valid_names():
    """Test various valid blueprint names."""
    valid_names = [
        "myblueprint",
        "my_blueprint",
        "my-blueprint",
        "MyBlueprint",
        "myBlueprint123",
        "blueprint_name_with_underscores"
    ]
    
    all_passed = True
    for name in valid_names:
        try:
            bp = Blueprint(name, __name__)
            print(f"SUCCESS: Valid blueprint name '{name}' was created normally")
        except Exception as e:
            print(f"ERROR: Unexpected exception for valid name '{name}': {e}")
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    print("Testing edge cases for blueprint name validation...")
    test1 = test_multiple_dots()
    test2 = test_dot_at_start()
    test3 = test_dot_at_end()
    test4 = test_valid_names()
    
    if test1 and test2 and test3 and test4:
        print("\nAll edge case tests passed!")
    else:
        print("\nSome edge case tests failed!")
