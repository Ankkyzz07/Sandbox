#!/usr/bin/env python3
"""
Safe test script - should execute successfully
"""

# Simple math operations
result = sum(range(1, 101))
print(f"Sum of 1 to 100: {result}")

# List comprehensions
squares = [x**2 for x in range(10)]
print(f"Squares: {squares}")

# String operations
message = "Hello, Sandbox!"
print(f"Message: {message}")

# Basic imports (should be allowed)
import math
print(f"Pi: {math.pi}")

import random
print(f"Random number: {random.randint(1, 100)}")

print("Safe script completed successfully!")

