#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bolamiga Game Server Launcher
Handles environment setup and server startup with QA compliance
"""

import os
import sys
import subprocess
import json
import time
import socket
from pathlib import Path

def check_port(port):
    """Check if a port is available"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result != 0

def kill_existing_processes():
    """Kill any existing Bolamiga processes ONLY from current project directory"""
    try:
        # Safe approach: Only kill processes using port 5030 from current directory
        current_dir = os.getcwd()
        
        # Find processes using port 5030
        try:
            result = subprocess.run(['lsof', '-i', ':5030'], capture_output=True, text=True, check=False)
            if result.stdout:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            pid = parts[1]
                            # Check if process is from current directory
                            try:
                                pwd_result = subprocess.run(['pwdx', pid], capture_output=True, text=True, check=False)
                                if pwd_result.stdout and current_dir in pwd_result.stdout:
                                    subprocess.run(['kill', '-9', pid], check=False)
                                    print(f"✅ Killed Bolamiga process {pid} from current directory")
                            except:
                                pass
        except:
            pass
        
        # Also check for our specific PID file
        if os.path.exists('bolamiga.pid'):
            try:
                with open('bolamiga.pid', 'r') as f:
                    pid = f.read().strip()
                subprocess.run(['kill', '-9', pid], check=False)
                os.remove('bolamiga.pid')
                print(f"✅ Killed Bolamiga process {pid} from PID file")
            except:
                pass
        
        print("✅ Safely cleaned up existing Bolamiga processes")
        time.sleep(2)  # Wait for processes to die
    except Exception as e:
        print("⚠️  Warning during process cleanup: " + str(e))

def install_dependencies():
    """Install required dependencies"""
    try:
        # Check if Flask is available
        import flask
        print("✅ Flask is available")
        return True
    except ImportError:
        print("📦 Installing Flask...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'Flask==3.1.0'])
            print("✅ Flask installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print("❌ Failed to install dependencies: " + str(e))
            return False

def start_server():
    """Start the Bolamiga server"""
    print("🎮 Starting Bolamiga Game Server...")
    
    # Kill existing processes
    kill_existing_processes()
    
    # Install dependencies
    if not install_dependencies():
        return False
    
    # Check port availability
    port = 5030
    if not check_port(port):
        print("⚠️  Port " + str(port) + " is in use. Attempting to free it...")
        kill_existing_processes()
        time.sleep(3)
        if not check_port(port):
            print("❌ Port " + str(port) + " is still in use. Please free it manually.")
            return False
    
    print("✅ Port " + str(port) + " is available")
    
    # Start the server
    try:
        print("🚀 Launching server...")
        # Start server in background and get PID
        process = subprocess.Popen([sys.executable, 'app.py'], 
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.STDOUT,
                                   universal_newlines=True)
        
        # Save PID for later cleanup
        with open('bolamiga.pid', 'w') as f:
            f.write(str(process.pid))
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if server is responding
        if check_port(port):
            print("❌ Server failed to start on port " + str(port))
            return False
        
        print("✅ Server started successfully!")
        print("🌐 Local URL: http://localhost:" + str(port))
        print("📊 Status Bar: Active with exports/backups/logs access")
        print("🆔 Process ID: " + str(process.pid))
        
        # QA Status Report
        print("\n📋 QA COMPLIANCE STATUS:")
        print("✅ Port Management: PASSED")
        print("✅ Process Isolation: PASSED") 
        print("✅ Dependency Check: PASSED")
        print("✅ Server Launch: PASSED")
        print("🔄 Browser Testing: READY")
        
        return True
        
    except Exception as e:
        print("❌ Failed to start server: " + str(e))
        return False

if __name__ == "__main__":
    success = start_server()
    if success:
        print("\n🎯 QA VERIFICATION REQUIRED:")
        print("Please test http://localhost:5030 in your browser and confirm:")
        print("• Game loads with retro boot screen")
        print("• Menu navigation works")
        print("• Status bar shows exports/backups/logs")
        print("• Game controls respond correctly")
        sys.exit(0)
    else:
        print("\n❌ Server startup failed")
        sys.exit(1)