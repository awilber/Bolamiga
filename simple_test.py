#!/usr/bin/env python3
print("Python is working")
print("Testing Flask import...")
try:
    import flask
    print("Flask is available")
except ImportError:
    print("Flask not found - will need to install")
    
import socket
print("Socket test successful")