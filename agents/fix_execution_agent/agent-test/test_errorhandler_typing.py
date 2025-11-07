"""Test script to reproduce the errorhandler typing issue."""
from flask import Flask
from typing import Tuple

# Create a custom exception for testing
class ExpiredTokenException(Exception):
    def __init__(self, description: str = None):
        self.description = description
        super().__init__(description)

app = Flask(__name__)

# This should work with proper typing but currently requires casting
@app.errorhandler(ExpiredTokenException)
def expired_token(error: ExpiredTokenException) -> Tuple[str, int]:
    """Handle the expired token error."""
    return error.description or "Expired token", 498

if __name__ == "__main__":
    print("Testing errorhandler typing...")
    # Check if the handler is registered correctly
    handler = app.error_handler_spec[None][None].get(ExpiredTokenException)
    if handler:
        print(f"Handler registered: {handler}")
        # Test the handler with our custom exception
        test_error = ExpiredTokenException("Token expired")
        result = handler(test_error)
        print(f"Handler result: {result}")
    else:
        print("Handler not found in error_handler_spec")
