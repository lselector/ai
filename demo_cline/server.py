#!/usr/bin/env python3
"""Simple HTTP server for static website on port 3000."""

import http.server
import socketserver
import os
import sys

# Configuration
PORT = 3000
# Serve from the website subdirectory
DIRECTORY = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'website'
)

# --------------------------------------------------------------
class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP request handler with CORS support."""
    
    # ----------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """Initialize handler with custom directory."""
        super().__init__(
            *args,
            directory=DIRECTORY,
            **kwargs
        )
    
    # ----------------------------------------------------------
    def end_headers(self):
        """Add CORS headers for local development."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header(
            'Cache-Control',
            'no-store, no-cache, must-revalidate'
        )
        super().end_headers()

# --------------------------------------------------------------
def start_server():
    """Start the HTTP server."""
    with socketserver.TCPServer(
        ("", PORT),
        MyHTTPRequestHandler
    ) as httpd:
        print(f"Server running at http://localhost:{PORT}/")
        print(f"Serving files from: {DIRECTORY}")
        print("Press Ctrl+C to stop the server")
        httpd.serve_forever()

# --------------------------------------------------------------
def main():
    """Main function to run the server."""
    try:
        start_server()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        sys.exit(0)
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"Error: Port {PORT} is already in use.")
            print("Stop other process or choose different port.")
            sys.exit(1)
        else:
            raise

# --------------------------------------------------------------
if __name__ == "__main__":
    main()
