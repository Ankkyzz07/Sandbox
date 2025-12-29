# Secure Python Sandbox Runner 🛡️

**A secure sandbox environment for executing untrusted Python code** with resource limits, behavior logging, restricted imports, and execution safety controls.

This project is ideal for:
- Code execution platforms
- Online IDEs & judge systems
- Education & experimentation
- Safe script execution environments

---

## 🛠 Tech Stack
| Component | Technology |
|--------|----------|
| Language | Python |
| Execution | Subprocess sandboxing |
| Security Controls | Resource limits, import hooks, file/network restriction |
| Logging | JSON-based activity reports |

---

## 🔥 Highlights
- Safe execution for unknown Python scripts
- Control file access, network calls, imports
- Execution timeout & memory limit handling
- Detailed logging + security monitoring
- CLI & programmatic usage supported

---


### Programmatic API

```python
from sandbox_runner import run_sandboxed_code, SandboxConfig

# Simple usage with defaults
code = """
print("Hello from sandbox!")
result = sum(range(1, 11))
print(f"Sum: {result}")
"""

result = run_sandboxed_code(code)
print(result['stdout'])
print(result['success'])

# Custom configuration
config = SandboxConfig(
    timeout_seconds=5.0,
    memory_limit_mb=128,
    allow_file_read=True,
    restricted_imports=['os', 'sys', 'subprocess']
)

result = run_sandboxed_code(code, config)

# Access detailed report
report = result['report']
print(f"Total activities: {report['execution_summary']['total_activities']}")
print(f"Imports: {report['imports']['total']}")
print(f"File operations: {report['file_operations']['total']}")
```

## Configuration Options

### SandboxConfig Parameters

- `timeout_seconds` (float): Maximum execution time in seconds (default: 10.0)
- `memory_limit_mb` (int): Maximum memory usage in MB (default: 128)
- `cpu_limit_percent` (float): CPU limit percentage (default: 50.0)
- `allow_file_read` (bool): Allow file read operations (default: False)
- `allow_file_write` (bool): Allow file write operations (default: False)
- `allow_network` (bool): Allow network operations (default: False)
- `restricted_imports` (List[str]): List of module names to block (default: ['os', 'sys', 'subprocess', 'shutil', 'socket', 'urllib'])
- `allowed_imports` (List[str]): Whitelist of allowed modules (overrides restrictions if specified)

## Activity Report Structure

The sandbox generates detailed activity reports in JSON format:

```json
{
  "execution_summary": {
    "duration_seconds": 0.123,
    "total_activities": 5,
    "start_time": "2025-12-05T04:19:00",
    "end_time": "2025-12-05T04:19:00"
  },
  "imports": {
    "total": 2,
    "allowed": 2,
    "blocked": 0,
    "details": [...]
  },
  "file_operations": {
    "total": 1,
    "allowed": 0,
    "blocked": 1,
    "details": [...]
  },
  "network_operations": {
    "total": 0,
    "allowed": 0,
    "blocked": 0,
    "details": []
  },
  "exceptions": {
    "total": 0,
    "details": []
  },
  "resource_limits": {
    "details": [...]
  },
  "all_activities": [...]
}
```

## Example Test Scripts

The repository includes several test scripts:

- `test_safe.py`: Safe code that should execute successfully
- `test_restricted_import.py`: Attempts restricted imports (should be blocked)
- `test_file_operations.py`: Attempts file operations (should be blocked)
- `test_network.py`: Attempts network operations (should be blocked)
- `test_timeout.py`: Long-running code (should timeout)
- `test_exception.py`: Code that raises exceptions (should be logged)

Run examples:

```bash
# Test safe code
python sandbox_runner.py test_safe.py

# Test restricted imports
python sandbox_runner.py test_restricted_import.py

# Test with custom config
python example_usage.py
```

## Security Considerations

⚠️ **Important**: This sandbox provides best-effort restrictions but is not a complete security solution. It should not be used for truly malicious code or in production environments without additional security measures.

### Limitations:

1. **Python-level restrictions**: The sandbox uses Python-level hooks which can potentially be bypassed
2. **Resource limits**: Depend on system capabilities and may not work on all platforms
3. **Import restrictions**: Can be bypassed through various Python mechanisms
4. **File operations**: Hooks can be bypassed using low-level file operations

### Recommended Additional Security:

- Use containerization (Docker) for better isolation
- Run in a VM or dedicated sandboxed environment
- Use system-level restrictions (SELinux, AppArmor)
- Implement additional monitoring and logging
- Use specialized sandboxing tools for production use

## Architecture

The sandbox works by:

1. **Creating a wrapper script** that installs hooks for imports, file operations, and network access
2. **Executing the wrapper** in a subprocess with resource limits
3. **Monitoring activities** through hook functions that log all operations
4. **Parsing activity logs** and generating comprehensive reports
5. **Cleaning up** temporary files and directories

## License

This project is provided as-is for educational and demonstration purposes.

## Contributing

This is a CodeJam challenge implementation. Feel free to use and modify as needed.

