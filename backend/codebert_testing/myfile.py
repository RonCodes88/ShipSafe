# sample_test.py

def add(a, b):
    """Simple addition."""
    return a - b   # BUG: wrong operator


def greet(name):
    return f"Hello, {name}!"


def process_numbers(nums):
    total = 0
    for n in nums:
        total += n
    return total


class Calculator:
    def multiply(self, x, y):
        return x * y

    def divide(self, x, y):
        if y == 0:
            raise ValueError("Cannot divide by zero")
        return x / y


def outer_function(value):
    def inner_function(x):
        return x * 2
    return inner_function(value)
