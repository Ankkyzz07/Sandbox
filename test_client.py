#!/usr/bin/env python3
"""
Test client for the sandbox server
"""

import requests
import json

SERVER_URL = 'http://localhost:8000'

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f'{SERVER_URL}/health')
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_execute(code, **kwargs):
    """Test execute endpoint"""
    print(f"Executing code:\n{code}\n")
    print("-" * 60)
    
    payload = {
        'code': code,
        **kwargs
    }
    
    response = requests.post(
        f'{SERVER_URL}/execute',
        json=payload,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"Status: {response.status_code}")
    result = response.json()
    
    print(f"\nSTDOUT:\n{result.get('stdout', '')}")
    if result.get('stderr'):
        print(f"\nSTDERR:\n{result.get('stderr', '')}")
    
    print(f"\nSuccess: {result.get('success')}")
    print(f"Execution time: {result.get('execution_time', 0):.3f}s")
    
    report = result.get('report', {})
    summary = report.get('execution_summary', {})
    print(f"\nTotal activities: {summary.get('total_activities', 0)}")
    print(f"Imports: {report.get('imports', {}).get('total', 0)}")
    print(f"File operations: {report.get('file_operations', {}).get('total', 0)}")
    print(f"Network operations: {report.get('network_operations', {}).get('total', 0)}")
    print(f"Exceptions: {report.get('exceptions', {}).get('total', 0)}")
    print("=" * 60)
    print()

if __name__ == '__main__':
    print("Sandbox Runner API Test Client")
    print("=" * 60)
    print()
    
    # Test health
    try:
        test_health()
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to server. Make sure it's running:")
        print("  python sandbox_server.py")
        exit(1)
    
    # Test 1: Simple code
    test_execute("""
print("Hello from sandbox!")
result = sum(range(1, 11))
print(f"Sum: {result}")
""")
    
    # Test 2: Restricted import
    test_execute("""
try:
    import os
    print("os imported")
except ImportError as e:
    print(f"Import blocked: {e}")
""")
    
    # Test 3: File operation (blocked)
    test_execute("""
try:
    with open('test.txt', 'w') as f:
        f.write("test")
    print("File write succeeded")
except PermissionError as e:
    print(f"File write blocked: {e}")
""")
    
    # Test 4: With custom config
    test_execute("""
import math
print(f"Pi = {math.pi}")
""", timeout=5.0, allow_file_read=True)
    
    print("All tests completed!")

