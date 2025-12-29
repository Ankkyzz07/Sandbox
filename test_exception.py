#!/usr/bin/env python3
"""
Test script that raises exceptions - should be logged
"""
sleep(10)
print("Testing exception handling...")

try:
    # Raise a custom exception
    raise ValueError("This is a test exception")
except ValueError as e:
    print(f"Caught exception: {e}")

# Cause a division by zero
try:
    result = 1 / 0
except ZeroDivisionError as e:
    print(f"Caught division by zero: {e}")

# Cause an attribute error
try:
    obj = None
    obj.some_method()
except AttributeError as e:
    print(f"Caught attribute error: {e}")

print("Exception test completed!")

