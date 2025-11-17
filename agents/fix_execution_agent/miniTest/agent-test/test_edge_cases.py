# Test edge cases for the fixed average function
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)

# Test cases
test_cases = [
    [85, 90, 78, 92],  # Original test case
    [100, 100, 100],   # All same numbers
    [0, 0, 0],         # All zeros
    [1, 2, 3, 4, 5],   # Sequential numbers
    [10],              # Single number
    [-5, 0, 5]         # Negative and positive numbers
]

print("Testing edge cases:")
for i, test_case in enumerate(test_cases, 1):
    result = calculate_average(test_case)
    print(f"Test {i}: {test_case} -> Average: {result}")

# Test with empty list (should raise ZeroDivisionError)
try:
    calculate_average([])
    print("Empty list test: No error (unexpected)")
except ZeroDivisionError:
    print("Empty list test: Correctly raised ZeroDivisionError")
