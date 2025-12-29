# Understanding the Sandbox Output

## What You're Seeing

When you run `python sandbox_runner.py test_simple.py`, you see:

```
============================================================
SANDBOX ACTIVITY REPORT
============================================================
Execution time: 0.09s
Total activities: 2
Imports: 2 (allowed: 1, blocked: 1)
File operations: 0 (allowed: 0, blocked: 0)
Network operations: 0 (allowed: 0, blocked: 0)
Exceptions: 0
============================================================
```

## What This Means

### Execution Summary
- **Execution time: 0.09s** - The code ran successfully in 0.09 seconds
- **Total activities: 2** - The sandbox logged 2 activities (imports in this case)

### Import Activity
- **Imports: 2 (allowed: 1, blocked: 1)**
  - The script tried to import 2 modules
  - 1 import was **allowed** (likely `math`)
  - 1 import was **blocked** (likely something that tried to import `os` or another restricted module)

### Other Activities
- **File operations: 0** - No file reads/writes attempted
- **Network operations: 0** - No network/socket operations attempted
- **Exceptions: 0** - No exceptions occurred

## How It Works

1. **Code Execution**: Your Python code runs in an isolated subprocess
2. **Monitoring**: The sandbox hooks into Python's import system, file operations, and network calls
3. **Logging**: Every action is logged and checked against security rules
4. **Reporting**: A summary report is generated showing what happened

## Seeing More Details

### Option 1: Save Detailed JSON Report
```bash
python sandbox_runner.py test_simple.py --report report.json
```
Then open `report.json` to see:
- Every import attempt with details
- All file operations
- Network attempts
- Full activity timeline

### Option 2: Test Different Scenarios

**Test blocked imports:**
```bash
python sandbox_runner.py test_restricted_import.py
```
This will show imports being blocked.

**Test file operations:**
```bash
python sandbox_runner.py test_file_operations.py
```
This will show file operations being blocked.

**Test with allowed file operations:**
```bash
python sandbox_runner.py test_file_operations.py --allow-file-read
```
This will allow file reads and show them in the report.

### Option 3: Use the Web Interface
1. Start the server: `python sandbox_server.py`
2. Open `test_localhost.html` in your browser
3. Enter code and see detailed output

## Understanding the Activity Report

The report shows:
- **What happened**: Every import, file op, network attempt
- **Whether it was allowed**: Each action is marked allowed/blocked
- **Why**: Reasons for blocking are provided
- **When**: Timestamps for each activity

## Example: Why One Import Was Blocked

When you see "Imports: 2 (allowed: 1, blocked: 1)", it means:
- The `math` module was imported successfully (allowed)
- But `math` internally might have tried to import something restricted, OR
- Another import in your code was blocked

To see exactly which imports were blocked, check the detailed report!

