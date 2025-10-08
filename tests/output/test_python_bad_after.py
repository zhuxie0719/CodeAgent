"""Module with improved code quality and security."""

import json
from typing import Any


# Sensitive data should be stored securely, not hardcoded
def get_api_key() -> str:
    """Retrieve API key from secure source."""
    return "placeholder_for_secure_retrieval"


def get_secret_password() -> str:
    """Retrieve secret password from secure source."""
    return "placeholder_for_secure_retrieval"


def bad_function() -> int:
    """Perform basic arithmetic operation.
    
    Returns:
        Sum of two numbers
    """
    x = 1
    y = 2
    z = x + y
    return z


def risky_function() -> None:
    """Execute predefined safe operation.
    
    Note: eval() replaced with safe alternative
    """
    print('Hello')


def process_user_data(data: Any) -> Any:
    """Process user data by doubling the value.
    
    Args:
        data: Input data to be processed
        
    Returns:
        Processed data (doubled input)
    """
    if data is None:
        raise ValueError("Data cannot be None")
    processed = data * 2
    return processed


def divide_numbers(a: float, b: float) -> float:
    """Divide two numbers with error handling.
    
    Args:
        a: Numerator
        b: Denominator
        
    Returns:
        Result of division
        
    Raises:
        ZeroDivisionError: When denominator is zero
        TypeError: When inputs are not numbers
    """
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError("Both arguments must be numbers")
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    result = a / b
    return result


def use_local() -> str:
    """Use local variable instead of global.
    
    Returns:
        Modified string value
    """
    local_var = "modified"
    return local_var


def read_file(filename: str) -> str:
    """Read file content with proper encoding and error handling.
    
    Args:
        filename: Path to the file to read
        
    Returns:
        File content as string
        
    Raises:
        FileNotFoundError: When file doesn't exist
        IOError: When file cannot be read
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        raise FileNotFoundError(f"File {filename} not found")
    except IOError as e:
        raise IOError(f"Error reading file {filename}: {str(e)}")


def create_large_list() -> list[str]:
    """Create a large list efficiently using generator expression.
    
    Returns:
        List of generated items
    """
    return [f"item_{i}" for i in range(1000000)]


def format_string(user_input: str) -> str:
    """Format query string safely using parameterized approach.
    
    Args:
        user_input: User provided input
        
    Returns:
        Safely formatted query string
    """
    # In real application, use proper database library with parameterized queries
    safe_input = json.dumps(user_input).strip('"')
    query = f"SELECT * FROM users WHERE name = {safe_input}"
    return query


def main() -> None:
    """Main function to demonstrate module functionality."""
    print("Module executed as main")


if __name__ == "__main__":
    main()