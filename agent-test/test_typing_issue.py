"""Test to show the typing issue with errorhandler decorator."""
import sys
sys.path.insert(0, '/home/baiqinyu/Desktop/project/CodeAgent/tests/flask-2.0.0/src')

from flask.typing import ErrorHandlerCallable
from typing import get_type_hints, Callable

# Show the current type definition
print("Current ErrorHandlerCallable type:")
print(f"ErrorHandlerCallable = {ErrorHandlerCallable}")

# Check what the type expects
hints = get_type_hints(ErrorHandlerCallable)
print(f"Type hints: {hints}")

# The issue is that ErrorHandlerCallable expects [Exception] as parameter
# but we want to use specific exception types like ExpiredTokenException
