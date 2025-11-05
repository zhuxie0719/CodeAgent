from fibbo import generate_fibonacci

# Test various cases
test_cases = [0, 1, 2, 5, 10]
for n in test_cases:
    result = generate_fibonacci(n)
    print(f"generate_fibonacci({n}) returns {len(result)} elements: {result}")
    assert len(result) == n, f"Expected {n} elements, got {len(result)}"

print("All tests passed!")