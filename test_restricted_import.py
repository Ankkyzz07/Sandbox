#!/usr/bin/env python3
"""
Test script that attempts restricted imports - should be blocked
"""

print("Attempting to import restricted modules...")

try:
    import os
    print("ERROR: os import succeeded (should be blocked)")
except ImportError as e:
    print(f"SUCCESS: os import blocked - {e}")

try:
    import subprocess
    print("ERROR: subprocess import succeeded (should be blocked)")
except ImportError as e:
    print(f"SUCCESS: subprocess import blocked - {e}")

try:
    import socket
    print("ERROR: socket import succeeded (should be blocked)")
except ImportError as e:
    print(f"SUCCESS: socket import blocked - {e}")

print("Restricted import test completed!")

