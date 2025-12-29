# Allowlist Guide - Override Restrictions

## Overview

The sandbox now supports **allowlists** that override restrictions. If something is in the allowed list, it will be permitted even if it's normally restricted.

## How It Works

**Priority Order:**
1. ✅ **Allowed list** (highest priority - overrides everything)
2. ❌ **Restricted list** (blocked unless in allowed list)
3. ✅ **Default allowed** (if not in restricted list)

## Examples

### Example 1: Allow Restricted Import

**Default behavior - os is blocked:**
```bash
python sandbox_runner.py test_restricted_import.py
```
Result: `os` import is blocked

**Allow os even though it's restricted:**
```bash
python sandbox_runner.py test_restricted_import.py --allowed-imports os
```
Result: `os` import is **allowed** ✅

### Example 2: Programmatic Usage

```python
from sandbox_runner import run_sandboxed_code, SandboxConfig

code = """
import os
print(f"Current directory: {os.getcwd()}")
"""

# Allow os even though it's in restricted list
config = SandboxConfig(
    allowed_imports=['os']  # This overrides the restriction!
)

result = run_sandboxed_code(code, config)
print(result['stdout'])  # Will work!
```

### Example 3: Allow Multiple Imports

```bash
python sandbox_runner.py script.py --allowed-imports os subprocess socket
```

### Example 4: Allow Specific File Path

```python
from sandbox_runner import run_sandboxed_code, SandboxConfig

code = """
with open('allowed_file.txt', 'w') as f:
    f.write("This works!")
"""

config = SandboxConfig(
    allowed_file_paths=['allowed_file.txt']  # Allow this specific file
)

result = run_sandboxed_code(code, config)
```

### Example 5: Command Line - Allow File Path

```bash
python sandbox_runner.py script.py --allowed-file-paths data/output.txt temp/log.txt
```

### Example 6: Allow Network Address

```python
from sandbox_runner import run_sandboxed_code, SandboxConfig

code = """
import socket
s = socket.socket()
s.connect(('localhost', 8080))
"""

config = SandboxConfig(
    allowed_network_addresses=['localhost', '127.0.0.1']  # Allow localhost
)

result = run_sandboxed_code(code, config)
```

## Command Line Options

### Allow Imports
```bash
--allowed-imports MODULE1 MODULE2 ...
```
Example:
```bash
python sandbox_runner.py script.py --allowed-imports os sys
```

### Allow File Paths
```bash
--allowed-file-paths PATH1 PATH2 ...
```
Example:
```bash
python sandbox_runner.py script.py --allowed-file-paths data/input.txt output.txt
```

### Allow Network Addresses
```bash
--allowed-network-addresses ADDRESS1 ADDRESS2 ...
```
Example:
```bash
python sandbox_runner.py script.py --allowed-network-addresses localhost 127.0.0.1
```

## Complete Example

```python
from sandbox_runner import run_sandboxed_code, SandboxConfig

code = """
import os
import subprocess

# File operation
with open('output.txt', 'w') as f:
    f.write("test")

# Network operation  
import socket
s = socket.socket()
s.connect(('localhost', 8080))
"""

config = SandboxConfig(
    # Allow these imports even though they're restricted
    allowed_imports=['os', 'subprocess', 'socket'],
    
    # Allow this specific file even if file writes are disabled
    allowed_file_paths=['output.txt'],
    
    # Allow localhost connections even if network is disabled
    allowed_network_addresses=['localhost', '127.0.0.1']
)

result = run_sandboxed_code(code, config)
```

## Key Points

1. **Allowed list takes priority** - If something is in both allowed and restricted lists, it's allowed
2. **Specific overrides general** - Allowed file paths override general file restrictions
3. **All activities are still logged** - Even allowed operations are logged in the report
4. **Use with caution** - Only allow what you trust!

## Testing

Run the test script:
```bash
python test_allowlist.py
```

This demonstrates:
- Default blocking behavior
- Allowing restricted imports
- Allowing specific file paths
- Allowing multiple imports

