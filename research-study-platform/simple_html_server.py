#!/usr/bin/env python3
import http.server
import socketserver
import os

PORT = 3001

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory="frontend/public", **kwargs)

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"🚀 HTML server running on http://localhost:{PORT}")
        print(f"📄 Access: http://localhost:{PORT}/auth-test.html")
        print("🛑 Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n✅ Server stopped")