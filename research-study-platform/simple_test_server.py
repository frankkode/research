#!/usr/bin/env python3
"""
Simple test server to test authentication without all the complex dependencies
"""
import json
import sqlite3
import hashlib
import secrets
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
import os

class AuthHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        if self.path == '/simple/test/':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "success": True, 
                "message": "Simple test server is working!",
                "timestamp": "2025-07-21"
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_error(404)
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json')
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            
            if self.path == '/simple/register/':
                result = self.handle_register(data)
            elif self.path == '/simple/login/':
                result = self.handle_login(data)
            else:
                self.send_error(404)
                return
                
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            self.send_response(400)
            self.end_headers()
            error_response = {"success": False, "error": str(e)}
            self.wfile.write(json.dumps(error_response).encode())
    
    def handle_register(self, data):
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not email or not password:
            return {"success": False, "error": "All fields are required"}
        
        # Initialize database
        conn = sqlite3.connect('test_users.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users 
                     (id INTEGER PRIMARY KEY, username TEXT UNIQUE, 
                      email TEXT UNIQUE, password_hash TEXT, participant_id TEXT)''')
        
        # Check if user exists
        c.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
        if c.fetchone():
            conn.close()
            return {"success": False, "error": "Username or email already exists"}
        
        # Create user
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        participant_id = f"USER_{secrets.token_hex(4).upper()}"
        
        c.execute("INSERT INTO users (username, email, password_hash, participant_id) VALUES (?, ?, ?, ?)",
                 (username, email, password_hash, participant_id))
        user_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": "Registration successful!",
            "user": {
                "id": user_id,
                "username": username,
                "email": email,
                "participant_id": participant_id
            }
        }
    
    def handle_login(self, data):
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return {"success": False, "error": "Username and password are required"}
        
        # Check database
        conn = sqlite3.connect('test_users.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users 
                     (id INTEGER PRIMARY KEY, username TEXT UNIQUE, 
                      email TEXT UNIQUE, password_hash TEXT, participant_id TEXT)''')
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        c.execute("SELECT id, username, email, participant_id FROM users WHERE username = ? AND password_hash = ?",
                 (username, password_hash))
        user = c.fetchone()
        conn.close()
        
        if user:
            return {
                "success": True,
                "message": "Login successful!",
                "user": {
                    "id": user[0],
                    "username": user[1],
                    "email": user[2],
                    "participant_id": user[3]
                }
            }
        else:
            return {"success": False, "error": "Invalid username or password"}

if __name__ == '__main__':
    port = 8000
    server = HTTPServer(('localhost', port), AuthHandler)
    print(f"🚀 Simple test server running on http://localhost:{port}")
    print("📋 Available endpoints:")
    print("   GET  /simple/test/     - Test server connection")
    print("   POST /simple/register/ - Register new user")
    print("   POST /simple/login/    - Login user")
    print("\n🔧 Test with:")
    print(f"   curl http://localhost:{port}/simple/test/")
    print(f"   Open: http://localhost:3000/test-auth.html")
    print("\n🛑 Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n✅ Server stopped")