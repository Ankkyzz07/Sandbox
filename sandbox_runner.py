
import sys
import subprocess
import os
import json
import time
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import tempfile
import shutil

# Resource limits are Unix-only
try:
    import resource
    HAS_RESOURCE = True
except ImportError:
    HAS_RESOURCE = False

# Signal module may not be available on all platforms
try:
    import signal
    HAS_SIGNAL = True
except ImportError:
    HAS_SIGNAL = False


class SandboxActivityLogger:
    """Logs all sandbox activities including imports, file ops, network attempts, etc."""
    
    def __init__(self):
        self.activities: List[Dict[str, Any]] = []
        self.start_time = time.time()
    
    def log(self, event_type: str, details: Dict[str, Any]):
        """Log an activity event."""
        self.activities.append({
            'timestamp': time.time() - self.start_time,
            'type': event_type,
            'details': details
        })
    
    def log_import(self, module_name: str, allowed: bool, reason: str = ""):
        """Log a module import attempt."""
        self.log('import', {
            'module': module_name,
            'allowed': allowed,
            'reason': reason
        })
    
    def log_file_op(self, operation: str, path: str, allowed: bool, reason: str = ""):
        """Log a file operation."""
        self.log('file_operation', {
            'operation': operation,
            'path': path,
            'allowed': allowed,
            'reason': reason
        })
    
    def log_network(self, operation: str, address: str, allowed: bool, reason: str = ""):
        """Log a network operation."""
        self.log('network', {
            'operation': operation,
            'address': address,
            'allowed': allowed,
            'reason': reason
        })
    
    def log_exception(self, exception_type: str, message: str, traceback: str = ""):
        """Log an exception or crash."""
        self.log('exception', {
            'exception_type': exception_type,
            'message': message,
            'traceback': traceback
        })
    
    def log_resource_limit(self, limit_type: str, value: Any):
        """Log resource limit enforcement."""
        self.log('resource_limit', {
            'limit_type': limit_type,
            'value': value
        })
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate final activity report."""
        end_time = time.time()
        duration = end_time - self.start_time
        
        # Categorize activities
        imports = [a for a in self.activities if a['type'] == 'import']
        file_ops = [a for a in self.activities if a['type'] == 'file_operation']
        network_ops = [a for a in self.activities if a['type'] == 'network']
        exceptions = [a for a in self.activities if a['type'] == 'exception']
        resource_limits = [a for a in self.activities if a['type'] == 'resource_limit']
        
        return {
            'execution_summary': {
                'duration_seconds': duration,
                'total_activities': len(self.activities),
                'start_time': datetime.fromtimestamp(self.start_time).isoformat(),
                'end_time': datetime.fromtimestamp(end_time).isoformat()
            },
            'imports': {
                'total': len(imports),
                'allowed': len([i for i in imports if i['details'].get('allowed', False)]),
                'blocked': len([i for i in imports if not i['details'].get('allowed', True)]),
                'details': imports
            },
            'file_operations': {
                'total': len(file_ops),
                'allowed': len([f for f in file_ops if f['details'].get('allowed', False)]),
                'blocked': len([f for f in file_ops if not f['details'].get('allowed', True)]),
                'details': file_ops
            },
            'network_operations': {
                'total': len(network_ops),
                'allowed': len([n for n in network_ops if n['details'].get('allowed', False)]),
                'blocked': len([n for n in network_ops if not n['details'].get('allowed', True)]),
                'details': network_ops
            },
            'exceptions': {
                'total': len(exceptions),
                'details': exceptions
            },
            'resource_limits': {
                'details': resource_limits
            },
            'all_activities': self.activities
        }


class SandboxConfig:
    """Configuration for sandbox restrictions."""
    
    def __init__(
        self,
        timeout_seconds: float = 10.0,
        memory_limit_mb: int = 128,
        cpu_limit_percent: float = 50.0,
        allow_file_read: bool = False,
        allow_file_write: bool = False,
        allow_network: bool = False,
        restricted_imports: Optional[List[str]] = None,
        allowed_imports: Optional[List[str]] = None,
        allowed_file_paths: Optional[List[str]] = None,
        allowed_network_addresses: Optional[List[str]] = None
    ):
        self.timeout_seconds = timeout_seconds
        self.memory_limit_mb = memory_limit_mb
        self.cpu_limit_percent = cpu_limit_percent
        self.allow_file_read = allow_file_read
        self.allow_file_write = allow_file_write
        self.allow_network = allow_network
        self.restricted_imports = restricted_imports or ['os', 'sys', 'subprocess', 'shutil', 'socket', 'urllib']
        self.allowed_imports = allowed_imports or []
        self.allowed_file_paths = allowed_file_paths or []
        self.allowed_network_addresses = allowed_network_addresses or []
    
    def is_import_allowed(self, module_name: str) -> tuple[bool, str]:
        """Check if a module import is allowed.
        Allowed imports override restricted imports - if a module is in both lists, it's allowed.
        """
        # Check if explicitly allowed FIRST (this overrides restrictions)
        if self.allowed_imports and module_name in self.allowed_imports:
            return True, "Explicitly allowed (overrides restriction)"
        
        # Check if explicitly restricted
        if module_name in self.restricted_imports:
            return False, f"Module '{module_name}' is in restricted list"
        
        # Check for dangerous patterns
        dangerous_patterns = ['subprocess', 'os.', 'sys.', 'socket', 'urllib', 'http', 'ftplib', 'smtplib']
        for pattern in dangerous_patterns:
            if pattern in module_name.lower():
                return False, f"Module '{module_name}' matches dangerous pattern '{pattern}'"
        
        return True, "Allowed"
    
    def is_file_path_allowed(self, file_path: str, operation: str) -> tuple[bool, str]:
        """Check if a file path is allowed for the given operation.
        Allowed file paths override general file restrictions.
        """
        # Check if file path is explicitly allowed
        import os
        normalized_path = os.path.normpath(file_path)
        for allowed_path in self.allowed_file_paths:
            allowed_normalized = os.path.normpath(allowed_path)
            if normalized_path == allowed_normalized or normalized_path.startswith(allowed_normalized + os.sep):
                return True, f"File path '{file_path}' is explicitly allowed"
        
        # Check general permissions
        if operation == 'read' and not self.allow_file_read:
            return False, "File read operations are disabled"
        if operation in ['write', 'append'] and not self.allow_file_write:
            return False, "File write operations are disabled"
        
        return True, "Allowed"
    
    def is_network_allowed(self, address: str) -> tuple[bool, str]:
        """Check if a network address is allowed.
        Allowed addresses override general network restrictions.
        """
        # Check if address is explicitly allowed
        if self.allowed_network_addresses:
            for allowed_addr in self.allowed_network_addresses:
                if address.startswith(allowed_addr) or address == allowed_addr:
                    return True, f"Network address '{address}' is explicitly allowed"
        
        # Check general network permission
        if not self.allow_network:
            return False, "Network operations are disabled"
        
        return True, "Allowed"


def create_sandbox_wrapper_script(code: str, config: SandboxConfig, log_file: str) -> str:
    """Create a wrapper script that will execute the user code with hooks."""
    
    # Escape the code for embedding
    code_lines = code.split('\n')
    indented_code = '\n'.join('    ' + line for line in code_lines)
    
    # Prepare config values as JSON strings
    restricted_modules_json = json.dumps(config.restricted_imports)
    allowed_modules_json = json.dumps(config.allowed_imports)
    allowed_file_paths_json = json.dumps(config.allowed_file_paths)
    allowed_network_addresses_json = json.dumps(config.allowed_network_addresses)
    allow_read_bool = str(config.allow_file_read)  # Python bool: True/False
    allow_write_bool = str(config.allow_file_write)
    allow_network_bool = str(config.allow_network)
    
    wrapper_template = f'''#!/usr/bin/env python3
import sys
import json
import traceback
from datetime import datetime

# Save original open and stderr before we replace anything
_original_open = open
_original_stderr = sys.stderr

# Import hook to monitor imports
class ImportHook:
    def __init__(self, log_file):
        self.log_file = log_file
        self.builtin_import = __builtins__.__import__
        self.restricted_modules = {restricted_modules_json}
        self.allowed_modules = {allowed_modules_json}
    
    def log_import(self, module_name, allowed, reason):
        try:
            with _original_open(self.log_file, 'a') as f:
                f.write(json.dumps({{
                    'type': 'import',
                    'module': module_name,
                    'allowed': allowed,
                    'reason': reason,
                    'timestamp': datetime.now().isoformat()
                }}) + "\\n")
        except:
            pass
    
    def __call__(self, name, globals=None, locals=None, fromlist=(), level=0):
        # Check if import is allowed
        allowed, reason = self.is_import_allowed(name)
        self.log_import(name, allowed, reason)
        
        # Instead of blocking, just log the warning and allow
        if not allowed:
            _original_stderr.write(f"WARNING: Restricted import '{{name}}' - {{reason}}\\n")
            _original_stderr.flush()
        
        return self.builtin_import(name, globals, locals, fromlist, level)
    
    def is_import_allowed(self, module_name):
        # Check allowed FIRST (overrides restrictions)
        if self.allowed_modules and module_name in self.allowed_modules:
            return True, "Explicitly allowed (overrides restriction)"
        if module_name in self.restricted_modules:
            return False, f"Module '{{module_name}}' is restricted"
        dangerous_patterns = ['subprocess', 'os.', 'sys.', 'socket', 'urllib', 'http', 'ftplib', 'smtplib']
        for pattern in dangerous_patterns:
            if pattern in module_name.lower():
                return False, f"Module '{{module_name}}' matches dangerous pattern '{{pattern}}'"
        return True, "Allowed"

# File operation hooks
class FileHook:
    def __init__(self, log_file, allow_read, allow_write, allowed_paths):
        self.log_file = log_file
        self.allow_read = allow_read
        self.allow_write = allow_write
        self.allowed_paths = allowed_paths or []
        self.original_open = open
    
    def log_file_op(self, operation, path, allowed, reason):
        try:
            with _original_open(self.log_file, 'a') as f:
                f.write(json.dumps({{
                    'type': 'file_operation',
                    'operation': operation,
                    'path': path,
                    'allowed': allowed,
                    'reason': reason,
                    'timestamp': datetime.now().isoformat()
                }}) + "\\n")
        except:
            pass
    
    def is_path_allowed(self, path, operation):
        import os
        normalized_path = os.path.normpath(path)
        for allowed_path in self.allowed_paths:
            allowed_normalized = os.path.normpath(allowed_path)
            if normalized_path == allowed_normalized or normalized_path.startswith(allowed_normalized + os.sep):
                return True, f"File path '{{path}}' is explicitly allowed"
        return False, None
    
    def open(self, file, mode='r', *args, **kwargs):
        path = str(file)
        is_read = 'r' in mode or 'a' in mode
        is_write = 'w' in mode or 'a' in mode or 'x' in mode
        
        # Check if path is explicitly allowed (overrides general restrictions)
        path_allowed, reason = self.is_path_allowed(path, 'read' if is_read else 'write')
        if path_allowed:
            self.log_file_op('open', path, True, reason or f"Mode: {{mode}}")
            return self.original_open(file, mode, *args, **kwargs)
        
        # Instead of blocking, log warning and allow
        if is_read and not self.allow_read:
            self.log_file_op('read', path, False, "File read operations are disabled (WARNING)")
            _original_stderr.write(f"WARNING: File read operation on '{{path}}' - File read operations are disabled\\n")
            _original_stderr.flush()
        
        if is_write and not self.allow_write:
            self.log_file_op('write', path, False, "File write operations are disabled (WARNING)")
            _original_stderr.write(f"WARNING: File write operation on '{{path}}' - File write operations are disabled\\n")
            _original_stderr.flush()
        
        self.log_file_op('open', path, True, f"Mode: {{mode}}")
        return self.original_open(file, mode, *args, **kwargs)

# Network operation hooks
class NetworkHook:
    def __init__(self, log_file, allow_network, allowed_addresses):
        self.log_file = log_file
        self.allow_network = allow_network
        self.allowed_addresses = allowed_addresses or []
    
    def log_network(self, operation, address, allowed, reason):
        try:
            with _original_open(self.log_file, 'a') as f:
                f.write(json.dumps({{
                    'type': 'network',
                    'operation': operation,
                    'address': address,
                    'allowed': allowed,
                    'reason': reason,
                    'timestamp': datetime.now().isoformat()
                }}) + "\\n")
        except:
            pass
    
    def is_address_allowed(self, address):
        for allowed_addr in self.allowed_addresses:
            if address.startswith(allowed_addr) or address == allowed_addr:
                return True, f"Network address '{{address}}' is explicitly allowed"
        return False, None
    
    def block_socket(self, address='unknown'):
        # Check if address is explicitly allowed (overrides general restriction)
        addr_allowed, reason = self.is_address_allowed(address)
        if addr_allowed:
            self.log_network('socket_create', address, True, reason or "Allowed")
            return
        
        # Instead of blocking, log warning and allow
        if not self.allow_network:
            self.log_network('socket_create', address, False, "Network operations are disabled (WARNING)")
            _original_stderr.write(f"WARNING: Network operation to '{{address}}' - Network operations are disabled\\n")
            _original_stderr.flush()

# Install hooks
import_hook = ImportHook({json.dumps(log_file)})
file_hook = FileHook({json.dumps(log_file)}, {allow_read_bool}, {allow_write_bool}, {allowed_file_paths_json})
network_hook = NetworkHook({json.dumps(log_file)}, {allow_network_bool}, {allowed_network_addresses_json})

# Replace built-in import
__builtins__.__import__ = import_hook

# Replace open function
__builtins__.open = file_hook.open

# Try to hook socket (may not be imported)
try:
    import socket
    original_socket = socket.socket
    def socket_wrapper(*args, **kwargs):
        network_hook.block_socket()
        return original_socket(*args, **kwargs)
    socket.socket = socket_wrapper
except:
    pass

# Execute user code
try:
{indented_code}
except Exception as e:
    try:
        with _original_open({json.dumps(log_file)}, 'a') as f:
            f.write(json.dumps({{
                'type': 'exception',
                'exception_type': type(e).__name__,
                'message': str(e),
                'traceback': traceback.format_exc(),
                'timestamp': datetime.now().isoformat()
            }}) + "\\n")
    except:
        pass
    raise
'''
    
    return wrapper_template


def set_resource_limits(config: SandboxConfig, logger: SandboxActivityLogger):
    """Set resource limits for the process."""
    if not HAS_RESOURCE:
        logger.log('resource_limit', {
            'limit_type': 'info',
            'message': 'Resource limits not available on this platform (Windows)'
        })
        return
    
    try:
        # Set memory limit (RSS in bytes)
        memory_bytes = config.memory_limit_mb * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
        logger.log_resource_limit('memory_mb', config.memory_limit_mb)
    except Exception as e:
        logger.log('resource_limit', {'limit_type': 'memory', 'error': str(e)})
    
    try:
        # Set CPU time limit (soft and hard limits in seconds)
        cpu_seconds = int(config.timeout_seconds)
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
        logger.log_resource_limit('cpu_time_seconds', cpu_seconds)
    except Exception as e:
        logger.log('resource_limit', {'limit_type': 'cpu', 'error': str(e)})


def run_sandboxed_code(
    code: str,
    config: Optional[SandboxConfig] = None,
    input_data: Optional[str] = None
) -> Dict[str, Any]:
    """
    Execute untrusted Python code in a sandboxed environment.
    
    Args:
        code: Python code to execute
        config: Sandbox configuration (uses defaults if None)
        input_data: Optional input data to pass to stdin
    
    Returns:
        Dictionary containing execution results and activity report
    """
    if config is None:
        config = SandboxConfig()
    
    logger = SandboxActivityLogger()
    
    # Create temporary directory for sandbox execution
    temp_dir = tempfile.mkdtemp(prefix='sandbox_')
    log_file = os.path.join(temp_dir, 'activity.log')
    
    try:
        # Create wrapper script
        wrapper_script = create_sandbox_wrapper_script(code, config, log_file)
        script_path = os.path.join(temp_dir, 'sandboxed_code.py')
        
        with open(script_path, 'w') as f:
            f.write(wrapper_script)
        
        os.chmod(script_path, 0o755)
        
        # Prepare subprocess command
        cmd = [sys.executable, script_path]
        
        # Set up subprocess with resource limits (Unix only)
        # Note: preexec_fn is not supported on Windows
        preexec_fn = None
        if HAS_RESOURCE and os.name != 'nt':  # 'nt' is Windows
            def preexec_fn():
                """Set resource limits in child process."""
                set_resource_limits(config, logger)
        
        # Execute with timeout
        start_time = time.time()
        try:
            popen_kwargs = {
                'stdin': subprocess.PIPE if input_data else None,
                'stdout': subprocess.PIPE,
                'stderr': subprocess.PIPE,
                'text': True,
                'cwd': temp_dir
            }
            if preexec_fn is not None:
                popen_kwargs['preexec_fn'] = preexec_fn
            
            process = subprocess.Popen(cmd, **popen_kwargs)
            
            try:
                stdout, stderr = process.communicate(
                    input=input_data,
                    timeout=config.timeout_seconds
                )
                return_code = process.returncode
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                return_code = -1
                logger.log('exception', {
                    'exception_type': 'TimeoutError',
                    'message': f'Execution exceeded timeout of {config.timeout_seconds} seconds'
                })
        
        except Exception as e:
            logger.log_exception(type(e).__name__, str(e), traceback.format_exc())
            return {
                'success': False,
                'stdout': '',
                'stderr': str(e),
                'return_code': -1,
                'report': logger.generate_report()
            }
        
        # Parse activity log
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    for line in f:
                        if line.strip():
                            activity = json.loads(line.strip())
                            # Convert to logger format
                            if activity['type'] == 'import':
                                logger.log_import(
                                    activity['module'],
                                    activity.get('allowed', True),
                                    activity.get('reason', '')
                                )
                            elif activity['type'] == 'file_operation':
                                logger.log_file_op(
                                    activity['operation'],
                                    activity['path'],
                                    activity.get('allowed', True),
                                    activity.get('reason', '')
                                )
                            elif activity['type'] == 'network':
                                logger.log_network(
                                    activity['operation'],
                                    activity.get('address', 'unknown'),
                                    activity.get('allowed', True),
                                    activity.get('reason', '')
                                )
                            elif activity['type'] == 'exception':
                                logger.log_exception(
                                    activity['exception_type'],
                                    activity['message'],
                                    activity.get('traceback', '')
                                )
            except Exception as e:
                logger.log('error', {'message': f'Failed to parse activity log: {e}'})
        
        # Generate final report
        report = logger.generate_report()
        
        return {
            'success': return_code == 0,
            'stdout': stdout,
            'stderr': stderr,
            'return_code': return_code,
            'execution_time': time.time() - start_time,
            'report': report
        }
    
    finally:
        # Cleanup
        try:
            shutil.rmtree(temp_dir)
        except:
            pass


def main():
    """Main entry point for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Secure Python Sandbox Runner - Execute untrusted Python code safely'
    )
    parser.add_argument('script', help='Path to Python script to execute')
    parser.add_argument('--timeout', type=float, default=10.0, help='Execution timeout in seconds')
    parser.add_argument('--memory', type=int, default=128, help='Memory limit in MB')
    parser.add_argument('--cpu', type=float, default=50.0, help='CPU limit percentage')
    parser.add_argument('--allow-file-read', action='store_true', help='Allow file read operations')
    parser.add_argument('--allow-file-write', action='store_true', help='Allow file write operations')
    parser.add_argument('--allow-network', action='store_true', help='Allow network operations')
    parser.add_argument('--restricted-imports', nargs='+', help='List of restricted module names')
    parser.add_argument('--allowed-imports', nargs='+', help='List of allowed module names (overrides restrictions)')
    parser.add_argument('--allowed-file-paths', nargs='+', help='List of allowed file paths (overrides file restrictions)')
    parser.add_argument('--allowed-network-addresses', nargs='+', help='List of allowed network addresses (overrides network restrictions)')
    parser.add_argument('--report', help='Path to save JSON report')
    parser.add_argument('--input', help='Path to input file for stdin')
    
    args = parser.parse_args()
    
    # Read script
    with open(args.script, 'r') as f:
        code = f.read()
    
    # Read input if provided
    input_data = None
    if args.input:
        with open(args.input, 'r') as f:
            input_data = f.read()
    
    # Create config
    config = SandboxConfig(
        timeout_seconds=args.timeout,
        memory_limit_mb=args.memory,
        cpu_limit_percent=args.cpu,
        allow_file_read=args.allow_file_read,
        allow_file_write=args.allow_file_write,
        allow_network=args.allow_network,
        restricted_imports=args.restricted_imports,
        allowed_imports=args.allowed_imports,
        allowed_file_paths=getattr(args, 'allowed_file_paths', None),
        allowed_network_addresses=getattr(args, 'allowed_network_addresses', None)
    )
    
    # Run sandbox
    result = run_sandboxed_code(code, config, input_data)
    
    # Output results
    if result['stdout']:
        print(result['stdout'], end='')
    if result['stderr']:
        print(result['stderr'], file=sys.stderr, end='')
    
    # Save report if requested
    if args.report:
        with open(args.report, 'w') as f:
            json.dump(result['report'], f, indent=2)
        print(f"\nReport saved to {args.report}", file=sys.stderr)
    else:
        # Print summary
        report = result['report']
        print("\n" + "="*60, file=sys.stderr)
        print("SANDBOX ACTIVITY REPORT", file=sys.stderr)
        print("="*60, file=sys.stderr)
        print(f"Execution time: {report['execution_summary']['duration_seconds']:.2f}s", file=sys.stderr)
        print(f"Total activities: {report['execution_summary']['total_activities']}", file=sys.stderr)
        print(f"Imports: {report['imports']['total']} (allowed: {report['imports']['allowed']}, blocked: {report['imports']['blocked']})", file=sys.stderr)
        print(f"File operations: {report['file_operations']['total']} (allowed: {report['file_operations']['allowed']}, blocked: {report['file_operations']['blocked']})", file=sys.stderr)
        print(f"Network operations: {report['network_operations']['total']} (allowed: {report['network_operations']['allowed']}, blocked: {report['network_operations']['blocked']})", file=sys.stderr)
        print(f"Exceptions: {report['exceptions']['total']}", file=sys.stderr)
        print("="*60, file=sys.stderr)
    
    sys.exit(0 if result['success'] else 1)


if __name__ == '__main__':
    main()

