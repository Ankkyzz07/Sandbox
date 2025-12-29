#!/usr/bin/env python3
"""
Test script to demonstrate warning mode (no blocking, just warnings)
"""

print("=== Testing Warning Mode (No Blocking) ===")
print()

print("1. Testing restricted imports (should show warnings but work):")
print("-" * 60)
try:
    import os
    print(f"   [OK] os imported successfully: {os.getcwd()}")
except Exception as e:
    print(f"   [FAILED] os import failed: {e}")

try:
    import subprocess
    print(f"   [OK] subprocess imported successfully")
except Exception as e:
    print(f"   [FAILED] subprocess import failed: {e}")

try:
    import socket
    print(f"   [OK] socket imported successfully")
except Exception as e:
    print(f"   [FAILED] socket import failed: {e}")

print()
print("2. Testing file operations (should show warnings but work):")
print("-" * 60)
try:
    with open('test_write.txt', 'w') as f:
        f.write("This file write should work with a warning")
    print("   [OK] File write succeeded")
except Exception as e:
    print(f"   [FAILED] File write failed: {e}")

try:
    with open('test_write.txt', 'r') as f:
        content = f.read()
    print(f"   [OK] File read succeeded: {content[:50]}...")
except Exception as e:
    print(f"   [FAILED] File read failed: {e}")

print()
print("3. Testing network operations (should show warnings but work):")
print("-" * 60)
try:
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("   [OK] Socket creation succeeded")
    s.close()
except Exception as e:
    print(f"   [FAILED] Socket creation failed: {e}")

print()
print("=== Test Complete ===")
print("All operations should have worked, but warnings should appear in stderr")

