#!/usr/bin/env python3
"""
Start Bolamiga server with proper error handling
"""

import subprocess
import sys
import os
import time

def install_flask():
    """Install Flask if not available"""
    try:
        import flask
        print("✅ Flask is available")
        return True
    except ImportError:
        print("📦 Installing Flask...")
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', 'Flask==3.1.0'], 
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print("✅ Flask installed successfully")
                return True
            else:
                print(f"❌ Flask installation failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Flask installation error: {e}")
            return False

def start_server():
    """Start the Flask server"""
    if not install_flask():
        return False
    
    print("🚀 Starting Bolamiga server...")
    
    try:
        # Change to project directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Start server with explicit Python path
        cmd = [sys.executable, 'app.py']
        print(f"Running: {' '.join(cmd)}")
        
        # Start process
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        # Give it time to start
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Server started successfully")
            print("🌐 URL: http://localhost:5030")
            print(f"🆔 PID: {process.pid}")
            
            # Save PID for cleanup
            with open('server.pid', 'w') as f:
                f.write(str(process.pid))
            
            # Keep process running
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Shutting down server...")
                process.terminate()
                
            return True
        else:
            # Process died, get output
            stdout, stderr = process.communicate()
            print(f"❌ Server failed to start:")
            print(f"Output: {stdout}")
            if stderr:
                print(f"Error: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Server startup failed: {e}")
        return False

if __name__ == "__main__":
    success = start_server()
    sys.exit(0 if success else 1)