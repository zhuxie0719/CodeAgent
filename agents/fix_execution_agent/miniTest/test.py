from fibbo import generate_fibonacci

def test_fibonacci_length():
    result = generate_fibonacci(5)
    if len(result) != 5:
        print(f"❌ Test failed: expected 5 numbers, got {len(result)} -> {result}")
    else:
        print("✅ Test passed")
