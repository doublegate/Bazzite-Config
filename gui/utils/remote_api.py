"""
Remote Management API - Web-based control interface
Provides RESTful API for remote management and monitoring
"""

import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any, Callable, Optional
from threading import Thread
from urllib.parse import urlparse, parse_qs


class BazziteOptimizerAPI(BaseHTTPRequestHandler):
    """HTTP request handler for the API"""

    # Class-level callbacks
    status_callback: Optional[Callable] = None
    apply_profile_callback: Optional[Callable] = None
    get_metrics_callback: Optional[Callable] = None

    def log_message(self, format, *args):
        """Override to use our logger"""
        logger = logging.getLogger(__name__)
        logger.debug(format % args)

    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == '/api/status':
            self._handle_status()
        elif path == '/api/metrics':
            self._handle_metrics()
        elif path == '/api/profiles':
            self._handle_list_profiles()
        elif path == '/health':
            self._handle_health()
        else:
            self._send_error(404, "Endpoint not found")

    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == '/api/profile/apply':
            self._handle_apply_profile()
        elif path == '/api/gaming-mode/enable':
            self._handle_gaming_mode(True)
        elif path == '/api/gaming-mode/disable':
            self._handle_gaming_mode(False)
        else:
            self._send_error(404, "Endpoint not found")

    def _handle_status(self):
        """Get system status"""
        if self.status_callback:
            status = self.status_callback()
        else:
            status = {
                "status": "unknown",
                "message": "Status callback not configured"
            }

        self._send_json_response(status)

    def _handle_metrics(self):
        """Get current metrics"""
        if self.get_metrics_callback:
            metrics = self.get_metrics_callback()
        else:
            metrics = {
                "error": "Metrics callback not configured"
            }

        self._send_json_response(metrics)

    def _handle_list_profiles(self):
        """List available profiles"""
        profiles = [
            {"name": "competitive", "description": "Maximum performance"},
            {"name": "balanced", "description": "Balanced performance"},
            {"name": "streaming", "description": "Optimized for streaming"},
            {"name": "creative", "description": "Creative workloads"}
        ]

        self._send_json_response({"profiles": profiles})

    def _handle_apply_profile(self):
        """Apply a profile"""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')

        try:
            data = json.loads(body)
            profile_name = data.get('profile')

            if not profile_name:
                self._send_error(400, "Profile name required")
                return

            if self.apply_profile_callback:
                result = self.apply_profile_callback(profile_name)
                self._send_json_response({"success": result, "profile": profile_name})
            else:
                self._send_error(500, "Apply profile callback not configured")

        except json.JSONDecodeError:
            self._send_error(400, "Invalid JSON")

    def _handle_gaming_mode(self, enable: bool):
        """Enable/disable gaming mode"""
        # Would call actual gaming mode toggle
        self._send_json_response({
            "success": True,
            "gaming_mode": "enabled" if enable else "disabled"
        })

    def _handle_health(self):
        """Health check endpoint"""
        self._send_json_response({"status": "healthy", "service": "bazzite-optimizer-api"})

    def _send_json_response(self, data: Dict[str, Any], status_code: int = 200):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def _send_error(self, status_code: int, message: str):
        """Send error response"""
        self._send_json_response({"error": message}, status_code)


class RemoteAPIServer:
    """Remote API server"""

    def __init__(self, port: int = 8080, auth_required: bool = True):
        self.port = port
        self.auth_required = auth_required
        self.server: Optional[HTTPServer] = None
        self.server_thread: Optional[Thread] = None
        self.logger = logging.getLogger(__name__)
        self.running = False

    def set_callbacks(self, status_callback=None, apply_profile_callback=None, get_metrics_callback=None):
        """Set callback functions"""
        BazziteOptimizerAPI.status_callback = status_callback
        BazziteOptimizerAPI.apply_profile_callback = apply_profile_callback
        BazziteOptimizerAPI.get_metrics_callback = get_metrics_callback

    def start(self):
        """Start the API server"""
        if self.running:
            self.logger.warning("Server already running")
            return False

        try:
            self.server = HTTPServer(('0.0.0.0', self.port), BazziteOptimizerAPI)
            self.server_thread = Thread(target=self.server.serve_forever, daemon=True)
            self.server_thread.start()
            self.running = True
            self.logger.info(f"Remote API server started on port {self.port}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start API server: {e}")
            return False

    def stop(self):
        """Stop the API server"""
        if not self.running:
            return

        try:
            if self.server:
                self.server.shutdown()
                self.server.server_close()
            self.running = False
            self.logger.info("Remote API server stopped")

        except Exception as e:
            self.logger.error(f"Error stopping server: {e}")

    def is_running(self) -> bool:
        """Check if server is running"""
        return self.running
