#!/usr/bin/env python3
"""
Test script that runs for a long time - should timeout
"""

import time

print("Starting long-running operation...")
print("This should timeout after a few seconds")

# Infinite loop that should be killed by timeout
counter = 0
while True:
    counter += 1
    if counter % 1000000 == 0:
        print(f"Still running... counter: {counter}")
    # Small delay to prevent CPU spinning
    time.sleep(0.001)

print("This should never be reached")

