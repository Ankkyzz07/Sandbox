#!/usr/bin/env python3
"""
Comprehensive test that triggers multiple types of activities
"""

print("=== Starting Comprehensive Test ===")

# Test 1: Multiple imports (some allowed, some blocked)
print("\n1. Testing imports...")
try:
    import math
    print(f"   [OK] math imported: {math.pi}")
except Exception as e:
    print(f"   [FAIL] math failed: {e}")

try:
    import json
    print(f"   [OK] json imported")
except Exception as e:
    print(f"   [FAIL] json failed: {e}")

try:
    import os
    print(f"   [FAIL] os imported (should be blocked)")
except ImportError as e:
    print(f"   [OK] os blocked: {e}")

try:
    import subprocess
    print(f"   [FAIL] subprocess imported (should be blocked)")
except ImportError as e:
    print(f"   [OK] subprocess blocked: {e}")

# Test 2: File operations (should be blocked)
print("\n2. Testing file operations...")
try:
    with open('test_read.txt', 'r') as f:
        content = f.read()
    print(f"   [FAIL] File read succeeded (should be blocked)")
except PermissionError as e:
    print(f"   [OK] File read blocked: {e}")
except Exception as e:
    print(f"   File read error: {e}")

try:
    with open('test_write.txt', 'w') as f:
        f.write("test content")
    print(f"   [FAIL] File write succeeded (should be blocked)")
except PermissionError as e:
    print(f"   [OK] File write blocked: {e}")
except Exception as e:
    print(f"   File write error: {e}")

# Test 3: Network operations (should be blocked)
print("\n3. Testing network operations...")
try:
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f"   [FAIL] Socket created (should be blocked)")
except PermissionError as e:
    print(f"   [OK] Network operation blocked: {e}")
except ImportError as e:
    print(f"   [OK] Socket import blocked: {e}")
except Exception as e:
    print(f"   Network error: {e}")

# Test 4: Exceptions (should be logged)
print("\n4. Testing exception handling...")
try:
    result = 1 / 0
except ZeroDivisionError as e:
    print(f"   [OK] Caught ZeroDivisionError: {e}")

try:
    my_list = [1, 2, 3]
    value = my_list[10]
except IndexError as e:
    print(f"   [OK] Caught IndexError: {e}")

# Test 5: Normal operations (should work)
print("\n5. Testing normal operations...")
numbers = [x**2 for x in range(10)]
print(f"   [OK] List comprehension: {numbers}")

result = sum(range(1, 101))
print(f"   [OK] Sum calculation: {result}")

print("\n=== Test Completed ===")

