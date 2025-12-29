#!/usr/bin/env python3
"""Show detailed report information"""

import json
import sys

if len(sys.argv) < 2:
    print("Usage: python show_report.py <report.json>")
    sys.exit(1)

report_file = sys.argv[1]

with open(report_file, 'r') as f:
    data = json.load(f)

print("=" * 60)
print("DETAILED SANDBOX ACTIVITY REPORT")
print("=" * 60)

# Execution summary
summary = data['execution_summary']
print(f"\nExecution Summary:")
print(f"  Duration: {summary['duration_seconds']:.3f} seconds")
print(f"  Start: {summary['start_time']}")
print(f"  End: {summary['end_time']}")
print(f"  Total Activities: {summary['total_activities']}")

# Imports
imports = data['imports']
print(f"\nImports ({imports['total']} total):")
print(f"  Allowed: {imports['allowed']}")
print(f"  Blocked: {imports['blocked']}")
if imports['details']:
    print("\n  Details:")
    for imp in imports['details']:
        status = "✓ ALLOWED" if imp['details']['allowed'] else "✗ BLOCKED"
        print(f"    {status}: {imp['details']['module']}")
        if not imp['details']['allowed']:
            print(f"      Reason: {imp['details']['reason']}")

# File operations
file_ops = data['file_operations']
print(f"\nFile Operations ({file_ops['total']} total):")
print(f"  Allowed: {file_ops['allowed']}")
print(f"  Blocked: {file_ops['blocked']}")
if file_ops['details']:
    print("\n  Details:")
    for op in file_ops['details']:
        status = "✓ ALLOWED" if op['details']['allowed'] else "✗ BLOCKED"
        print(f"    {status}: {op['details']['operation']} on {op['details']['path']}")
        if not op['details']['allowed']:
            print(f"      Reason: {op['details']['reason']}")

# Network operations
net_ops = data['network_operations']
print(f"\nNetwork Operations ({net_ops['total']} total):")
print(f"  Allowed: {net_ops['allowed']}")
print(f"  Blocked: {net_ops['blocked']}")
if net_ops['details']:
    print("\n  Details:")
    for op in net_ops['details']:
        status = "✓ ALLOWED" if op['details']['allowed'] else "✗ BLOCKED"
        print(f"    {status}: {op['details']['operation']} to {op['details'].get('address', 'unknown')}")
        if not op['details']['allowed']:
            print(f"      Reason: {op['details']['reason']}")

# Exceptions
exceptions = data['exceptions']
print(f"\nExceptions ({exceptions['total']} total):")
if exceptions['details']:
    for exc in exceptions['details']:
        print(f"  {exc['details']['exception_type']}: {exc['details']['message']}")

print("\n" + "=" * 60)

