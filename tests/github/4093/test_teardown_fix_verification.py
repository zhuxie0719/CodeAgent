from flask import Flask

def test_teardown_return_values_ignored():
    """Test that teardown functions can return any type and values are ignored."""
    app = Flask(__name__)
    results = []
    
    @app.teardown_appcontext
    def teardown_none(exc):
        results.append("teardown_none_called")
        return None
    
    @app.teardown_appcontext
    def teardown_string(exc):
        results.append("teardown_string_called") 
        return "This should be ignored"
    
    @app.teardown_appcontext
    def teardown_int(exc):
        results.append("teardown_int_called")
        return 42
    
    @app.teardown_appcontext
    def teardown_dict(exc):
        results.append("teardown_dict_called")
        return {"key": "value"}
    
    @app.teardown_appcontext
    def teardown_response(exc):
        results.append("teardown_response_called")
        from flask import Response
        return Response("response")
    
    # Create and pop app context - all teardown functions should be called
    with app.app_context():
        pass
    
    # Verify all teardown functions were called
    expected_calls = [
        "teardown_response_called",
        "teardown_dict_called", 
        "teardown_int_called",
        "teardown_string_called",
        "teardown_none_called"
    ]
    
    assert results == expected_calls, f"Expected {expected_calls}, got {results}"
    print("✓ All teardown functions were called regardless of return type")
    print("✓ Return values were properly ignored")
    
    return True

def test_teardown_with_exception():
    """Test teardown functions work correctly when an exception occurs."""
    app = Flask(__name__)
    exceptions_caught = []
    
    @app.teardown_appcontext
    def teardown_with_exc(exc):
        exceptions_caught.append(exc)
        return "Return value should be ignored"
    
    # Test with no exception
    with app.app_context():
        pass
    assert exceptions_caught == [None]
    
    # Test with exception
    exceptions_caught.clear()
    try:
        with app.app_context():
            raise ValueError("Test exception")
    except ValueError:
        pass
    
    assert len(exceptions_caught) == 1
    assert isinstance(exceptions_caught[0], ValueError)
    assert str(exceptions_caught[0]) == "Test exception"
    
    print("✓ Teardown functions correctly receive exception parameter")
    print("✓ Return values are ignored even with exceptions")
    
    return True

if __name__ == "__main__":
    print("Testing teardown function fix...")
    test_teardown_return_values_ignored()
    test_teardown_with_exception()
    print("\\n🎉 All tests passed! Teardown functions now correctly accept any return type.")
