#!/usr/bin/env python3
"""
Test script demonstrating allowlist functionality
Shows how to allow specific operations even if they're restricted
"""

from sandbox_runner import run_sandboxed_code, SandboxConfig

print("=" * 60)
print("TEST 1: Default behavior - os is blocked")
print("=" * 60)

code1 = """
try:
    import os
    print(f"[OK] os imported: {os.getcwd()}")
except ImportError as e:
    print(f"[BLOCKED] os import failed: {e}")
"""

result1 = run_sandboxed_code(code1)
print(result1['stdout'])
print(f"Imports blocked: {result1['report']['imports']['blocked']}")
print()

print("=" * 60)
print("TEST 2: Allow os even though it's restricted")
print("=" * 60)

config2 = SandboxConfig(
    allowed_imports=['os']  # This overrides the restriction!
)

result2 = run_sandboxed_code(code1, config2)
print(result2['stdout'])
print(f"Imports allowed: {result2['report']['imports']['allowed']}")
print(f"Imports blocked: {result2['report']['imports']['blocked']}")
print()

print("=" * 60)
print("TEST 3: Allow specific file path even if file writes are disabled")
print("=" * 60)

code3 = """
try:
    with open('allowed_file.txt', 'w') as f:
        f.write("This should work!")
    print("[OK] File write succeeded")
except PermissionError as e:
    print(f"[BLOCKED] File write failed: {e}")
"""

config3 = SandboxConfig(
    allowed_file_paths=['allowed_file.txt']  # Allow this specific file
)

result3 = run_sandboxed_code(code3, config3)
print(result3['stdout'])
print(f"File operations allowed: {result3['report']['file_operations']['allowed']}")
print(f"File operations blocked: {result3['report']['file_operations']['blocked']}")
print()

print("=" * 60)
print("TEST 4: Allow multiple imports")
print("=" * 60)

code4 = """
imports_to_test = ['os', 'subprocess', 'socket', 'math']
for mod in imports_to_test:
    try:
        exec(f"import {mod}")
        print(f"[OK] {mod} imported")
    except ImportError as e:
        print(f"[BLOCKED] {mod} failed: {e}")
"""

config4 = SandboxConfig(
    allowed_imports=['os', 'subprocess']  # Allow these two
)

result4 = run_sandboxed_code(code4, config4)
print(result4['stdout'])
print()

print("=" * 60)
print("Summary: Allowlist overrides restrictions!")
print("=" * 60)
print("If a module/file/network address is in the allowed list,")
print("it will be permitted even if it's in the restricted list.")

