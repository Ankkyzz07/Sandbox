#!/usr/bin/env python3
"""
Test script that attempts network operations - should be blocked by default
"""

print("Attempting network operations...")

try:
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("ERROR: Socket creation succeeded (should be blocked)")
except PermissionError as e:
    print(f"SUCCESS: Network operation blocked - {e}")
except ImportError as e:
    print(f"SUCCESS: Socket import blocked - {e}")
except Exception as e:
    print(f"Network operation failed: {e}")

print("Network operations test completed!")

