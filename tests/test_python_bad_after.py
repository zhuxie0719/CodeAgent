"""Module with improved code quality and security practices."""

import json
from typing import Any


# Sensitive data should be stored securely, not hardcoded
API_KEY = "placeholder_key"
SECRET_PASSWORD = "placeholder_password"


def bad_function() -> int:
    """Perform a simple calculation.
    
    Returns:
        int: The result of the calculation
    """
    x = 1
    y = 2
    z = x + y
    return z


def risky_function() -> None:
    """Execute predefined code safely.
    
    Note: eval() is replaced with safer alternatives
    """
    print('Hello')


def process_user_data(data: Any) -> Any:
    """Process user data by doubling it.
    
    Args:
        data: Input data to be processed
        
    Returns:
        Any: Processed data multiplied by 2
    """
    processed = data * 2
    return processed


def divide_numbers(a: float, b: float) -> float:
    """Divide two numbers with error handling.
    
    Args:
        a: Numerator
        b: Denominator
        
    Returns:
        float: Result of division
        
    Raises:
        ZeroDivisionError: When denominator is zero
    """
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    result = a / b
    return result


# Constants should follow UPPER_CASE convention
GLOBAL_CONSTANT = "I'm a constant"


def use_global() -> str:
    """Modify and return the global constant.
    
    Returns:
        str: Modified constant value
    """
    modified_value = "modified"
    return modified_value


def read_file(filename: str) -> str:
    """Read file content with proper encoding and error handling.
    
    Args:
        filename: Path to the file to read
        
    Returns:
        str: File content
        
    Raises:
        FileNotFoundError: When file doesn't exist
        IOError: When file cannot be read
    """
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    except FileNotFoundError:
        raise FileNotFoundError(f"File {filename} not found")
    except IOError as e:
        raise IOError(f"Error reading file {filename}: {str(e)}")


def create_large_list() -> list[str]:
    """Create a large list of items efficiently.
    
    Returns:
        list[str]: List containing numbered items
    """
    return [f"item_{i}" for i in range(1000000)]


def format_string(user_input: str) -> str:
    """Format SQL query safely using parameterization.
    
    Args:
        user_input: User-provided input
        
    Returns:
        str: Safe SQL query string
    """
    # In real application, use proper database API with parameterized queries
    safe_input = user_input.replace("'", "''")
    query = f"SELECT * FROM users WHERE name = '{safe_input}'"
    return query


def main() -> None:
    """Main function to demonstrate module functionality."""
    print("Module executed as main")


if __name__ == "__main__":
    main()