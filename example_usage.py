#!/usr/bin/env python3
"""
Example usage of the sandbox runner
"""

from sandbox_runner import run_sandboxed_code, SandboxConfig
import json

# Example 1: Run safe code
print("=" * 60)
print("Example 1: Running safe code")
print("=" * 60)

safe_code = """
print("Hello from sandbox!")
result = sum(range(1, 11))
print(f"Sum: {result}")
"""

result = run_sandboxed_code(safe_code)
print("STDOUT:", result['stdout'])
print("STDERR:", result['stderr'])
print("Success:", result['success'])
print("\nReport Summary:")
report = result['report']
print(f"  Total activities: {report['execution_summary']['total_activities']}")
print(f"  Imports: {report['imports']['total']}")
print(f"  Exceptions: {report['exceptions']['total']}")

# Example 2: Run code with restricted imports
print("\n" + "=" * 60)
print("Example 2: Running code with restricted imports")
print("=" * 60)

restricted_code = """
try:
    import os
    print("os imported successfully")
except ImportError as e:
    print(f"Import blocked: {e}")
"""

result = run_sandboxed_code(restricted_code)
print("STDOUT:", result['stdout'])
print("STDERR:", result['stderr'])
print("\nImport activities:")
for activity in result['report']['imports']['details']:
    print(f"  - {activity['details']['module']}: allowed={activity['details']['allowed']}")

# Example 3: Run code with file operations (blocked)
print("\n" + "=" * 60)
print("Example 3: Running code with file operations (blocked)")
print("=" * 60)

file_code = """
try:
    with open('test.txt', 'w') as f:
        f.write("test")
    print("File write succeeded")
except PermissionError as e:
    print(f"File write blocked: {e}")
"""

result = run_sandboxed_code(file_code)
print("STDOUT:", result['stdout'])
print("\nFile operation activities:")
for activity in result['report']['file_operations']['details']:
    print(f"  - {activity['details']['operation']} on {activity['details']['path']}: allowed={activity['details']['allowed']}")

# Example 4: Custom configuration
print("\n" + "=" * 60)
print("Example 4: Running with custom configuration")
print("=" * 60)

config = SandboxConfig(
    timeout_seconds=5.0,
    memory_limit_mb=64,
    allow_file_read=True,
    restricted_imports=['os', 'sys', 'subprocess']
)

custom_code = """
import math
print(f"Pi = {math.pi}")
"""

result = run_sandboxed_code(custom_code, config)
print("STDOUT:", result['stdout'])
print("Execution time:", result['execution_time'], "seconds")

# Example 5: Generate full report
print("\n" + "=" * 60)
print("Example 5: Full activity report")
print("=" * 60)

test_code = """
import math
import random
print("Testing imports and operations")
result = math.sqrt(16)
print(f"Square root: {result}")
"""

result = run_sandboxed_code(test_code)
report_json = json.dumps(result['report'], indent=2)
print(report_json)

