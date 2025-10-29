"""Comprehensive test for errorhandler typing fix."""
import sys
sys.path.insert(0, '/home/baiqinyu/Desktop/project/CodeAgent/tests/flask-2.0.0/src')

from flask import Flask
from typing import Tuple, Optional, Dict, Any
from werkzeug.exceptions import HTTPException, NotFound

# Test with custom exceptions
class ExpiredTokenException(Exception):
    def __init__(self, description: Optional[str] = None):
        self.description = description
        super().__init__(description)

class DatabaseConnectionError(Exception):
    pass

class ValidationError(Exception):
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")

app = Flask(__name__)

# Test 1: Custom exception with specific type
@app.errorhandler(ExpiredTokenException)
def expired_token(error: ExpiredTokenException) -> Tuple[str, int]:
    """Handle expired token error with proper typing."""
    return error.description or "Expired token", 498

# Test 2: Another custom exception
@app.errorhandler(DatabaseConnectionError)
def database_error(error: DatabaseConnectionError) -> Tuple[str, int]:
    """Handle database connection error."""
    return "Database connection failed", 500

# Test 3: HTTP exception (built-in)
@app.errorhandler(NotFound)
def not_found(error: NotFound) -> Tuple[str, int]:
    """Handle 404 errors."""
    return "Page not found", 404

# Test 4: Error code (integer)
@app.errorhandler(500)
def internal_error(error: Exception) -> Tuple[str, int]:
    """Handle 500 errors - this should still work with base Exception type."""
    return "Internal server error", 500

# Test 5: Complex custom exception
@app.errorhandler(ValidationError)
def validation_error(error: ValidationError) -> Dict[str, Any]:
    """Handle validation errors with complex response."""
    return {"error": "Validation failed", "field": error.field, "message": error.message}, 400

if __name__ == "__main__":
    print("Testing comprehensive errorhandler typing...")
    
    # Test that handlers are registered
    handlers = [
        (ExpiredTokenException, "expired_token"),
        (DatabaseConnectionError, "database_error"), 
        (NotFound, "not_found"),
        (500, "internal_error"),
        (ValidationError, "validation_error")
    ]
    
    for exc_type, handler_name in handlers:
        if isinstance(exc_type, int):
            # For error codes, check the default exception mapping
            from werkzeug.exceptions import default_exceptions
            exc_class = default_exceptions.get(exc_type)
            if exc_class:
                handler = app.error_handler_spec[None][exc_type].get(exc_class)
            else:
                handler = None
        else:
            handler = app.error_handler_spec[None][None].get(exc_type)
        
        if handler:
            print(f"✓ {handler_name} registered for {exc_type}")
        else:
            print(f"✗ {handler_name} NOT registered for {exc_type}")
    
    print("\nAll tests completed!")
