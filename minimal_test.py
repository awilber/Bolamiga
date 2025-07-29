#!/usr/bin/env python3
"""
Minimal test to check if we can start a basic server
"""

print("Testing basic Python functionality...")

# Test 1: Basic imports
try:
    import os
    import sys
    print("✅ Basic imports work")
except Exception as e:
    print(f"❌ Basic imports failed: {e}")
    sys.exit(1)

# Test 2: Try to import Flask
try:
    import flask
    print("✅ Flask is available")
    flask_available = True
except ImportError:
    print("❌ Flask not available")
    flask_available = False

# Test 3: If Flask available, try minimal server
if flask_available:
    try:
        from flask import Flask
        app = Flask(__name__)
        
        @app.route('/')
        def hello():
            return "Hello from Bolamiga!"
        
        print("✅ Flask app created")
        
        # Try to start server (this should work)
        print("🚀 Attempting to start server on port 5030...")
        app.run(host='0.0.0.0', port=5030, debug=False)
        
    except Exception as e:
        print(f"❌ Flask server failed: {e}")
        sys.exit(1)
else:
    print("❌ Cannot test server without Flask")
    sys.exit(1)