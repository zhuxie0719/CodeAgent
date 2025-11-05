# fibonacci.py
"""
A simple Fibonacci generator module.
"""

def generate_fibonacci(n):
    """Return a list with the first n Fibonacci numbers."""
    if n <= 0:
        return []
    if n == 1:
        return [0]
    
    fibs = [0, 1]
    for i in range(2, n):
        fibs.append(fibs[i-1] + fibs[i-2])
    
    return fibs
