#!/usr/bin/env python3
"""
Simple HTTP server for testing the sandbox runner on localhost
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
from sandbox_runner import run_sandboxed_code, SandboxConfig


class SandboxHandler(BaseHTTPRequestHandler):
    """HTTP request handler for sandbox API"""
    
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests - show API info"""
        if self.path == '/' or self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'status': 'running',
                'message': 'Sandbox Runner API',
                'endpoints': {
                    'POST /execute': 'Execute Python code in sandbox',
                    'GET /health': 'Health check'
                }
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Handle POST requests - execute code"""
        if self.path == '/execute':
            try:
                # Read request body
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                data = json.loads(body.decode('utf-8'))
                
                # Extract code and config
                code = data.get('code', '')
                if not code:
                    self.send_error(400, "Missing 'code' parameter")
                    return
                
                # Build config from request
                config = SandboxConfig(
                    timeout_seconds=float(data.get('timeout', 10.0)),
                    memory_limit_mb=int(data.get('memory', 128)),
                    allow_file_read=bool(data.get('allow_file_read', False)),
                    allow_file_write=bool(data.get('allow_file_write', False)),
                    allow_network=bool(data.get('allow_network', False)),
                    restricted_imports=data.get('restricted_imports', None),
                    allowed_imports=data.get('allowed_imports', None)
                )
                
                # Execute code
                result = run_sandboxed_code(code, config, data.get('input'))
                
                # Send response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                response = {
                    'success': result['success'],
                    'stdout': result['stdout'],
                    'stderr': result['stderr'],
                    'return_code': result['return_code'],
                    'execution_time': result.get('execution_time', 0),
                    'report': result['report']
                }
                
                self.wfile.write(json.dumps(response, indent=2).encode())
                
            except json.JSONDecodeError:
                self.send_error(400, "Invalid JSON")
            except Exception as e:
                self.send_error(500, f"Server error: {str(e)}")
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Override to customize logging"""
        print(f"[{self.address_string()}] {format % args}")


def run_server(port=8000):
    """Run the sandbox server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, SandboxHandler)
    print(f"Sandbox Runner API Server running on http://localhost:{port}")
    print(f"Health check: http://localhost:{port}/health")
    print(f"Execute code: POST http://localhost:{port}/execute")
    print("\nPress Ctrl+C to stop the server")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.shutdown()


if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run_server(port)

