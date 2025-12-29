#!/usr/bin/env python3
"""
Test script that attempts file operations - should be blocked by default
"""

print("Attempting file operations...")

try:
    # Try to read a file
    with open('test.txt', 'r') as f:
        content = f.read()
    print("ERROR: File read succeeded (should be blocked)")
except PermissionError as e:
    print(f"SUCCESS: File read blocked - {e}")
except Exception as e:
    print(f"File read failed: {e}")

try:
    # Try to write a file
    with open('output.txt', 'w') as f:
        f.write("test content")
    print("ERROR: File write succeeded (should be blocked)")
except PermissionError as e:
    print(f"SUCCESS: File write blocked - {e}")
except Exception as e:
    print(f"File write failed: {e}")

print("File operations test completed!")

