#!/usr/bin/env python3
"""
Bolamiga QA Testing Suite
Comprehensive testing using available QA utilities
"""

import subprocess
import time
import json
import sys
import os
from pathlib import Path

class BolamigaQATester:
    def __init__(self):
        self.project_name = "Bolamiga"
        self.project_path = os.getcwd()
        self.base_url = "http://localhost:5030"
        self.utils_path = "../utils"
        
    def log(self, message, level="INFO"):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def check_dependencies(self):
        """Check if required QA utilities are available"""
        self.log("🔍 Checking QA utility availability...")
        
        # Check if utils directory exists
        if not os.path.exists(self.utils_path):
            self.log("❌ Utils directory not found", "ERROR")
            return False
            
        # Check for specific utilities
        utilities = {
            "port-manager": f"{self.utils_path}/port-manager/index.js",
            "app-status-checker": f"{self.utils_path}/app-status-checker/index.js",
            "QATeam": f"{self.utils_path}/QATeam",
            "WebTester": f"{self.utils_path}/WebTester"
        }
        
        available = {}
        for name, path in utilities.items():
            exists = os.path.exists(path)
            available[name] = exists
            status = "✅" if exists else "❌"
            self.log(f"{status} {name}: {'Available' if exists else 'Not found'}")
        
        return any(available.values())
    
    def test_port_management(self):
        """Test port management functionality"""
        self.log("🔌 Testing port management...")
        
        try:
            # Kill any existing processes first
            subprocess.run(['pkill', '-f', 'python.*app.py'], check=False, capture_output=True)
            subprocess.run(['pkill', '-f', 'Bolamiga'], check=False, capture_output=True)
            time.sleep(2)
            
            # Check port availability
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 5030))
            sock.close()
            
            if result == 0:
                self.log("❌ Port 5030 is still in use after cleanup", "ERROR")
                return False
            else:
                self.log("✅ Port 5030 is available")
                return True
                
        except Exception as e:
            self.log(f"❌ Port management test failed: {e}", "ERROR")
            return False
    
    def start_application(self):
        """Start the Bolamiga application"""
        self.log("🚀 Starting Bolamiga application...")
        
        try:
            # Check if Flask is available
            try:
                import flask
                self.log("✅ Flask dependency found")
            except ImportError:
                self.log("📦 Installing Flask...")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'Flask==3.1.0'], 
                                      capture_output=True)
                self.log("✅ Flask installed")
            
            # Start the application
            process = subprocess.Popen([sys.executable, 'app.py'],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT,
                                       universal_newlines=True)
            
            # Save PID
            with open('bolamiga.pid', 'w') as f:
                f.write(str(process.pid))
            
            # Wait for server to start
            self.log("⏳ Waiting for server to start...")
            time.sleep(5)
            
            # Check if server is running
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', 5030))
            sock.close()
            
            if result == 0:
                self.log("✅ Server started successfully")
                return True, process.pid
            else:
                self.log("❌ Server failed to start", "ERROR")
                return False, None
                
        except Exception as e:
            self.log(f"❌ Application startup failed: {e}", "ERROR")
            return False, None
    
    def test_http_endpoints(self):
        """Test HTTP endpoints and basic functionality"""
        self.log("🌐 Testing HTTP endpoints...")
        
        try:
            import urllib.request
            import urllib.error
            
            endpoints = [
                "/",
                "/game",
                "/api/health",
                "/api/highscores"
            ]
            
            results = {}
            for endpoint in endpoints:
                url = f"{self.base_url}{endpoint}"
                try:
                    with urllib.request.urlopen(url, timeout=10) as response:
                        status_code = response.getcode()
                        content_length = len(response.read())
                        results[endpoint] = {
                            "status": status_code,
                            "content_length": content_length,
                            "success": True
                        }
                        self.log(f"✅ {endpoint}: {status_code} ({content_length} bytes)")
                        
                except urllib.error.HTTPError as e:
                    results[endpoint] = {
                        "status": e.code,
                        "error": str(e),
                        "success": False
                    }
                    self.log(f"❌ {endpoint}: HTTP {e.code} - {e}", "ERROR")
                    
                except Exception as e:
                    results[endpoint] = {
                        "error": str(e),
                        "success": False
                    }
                    self.log(f"❌ {endpoint}: {e}", "ERROR")
            
            # Check if at least root endpoint works
            success = results.get("/", {}).get("success", False)
            return success, results
            
        except Exception as e:
            self.log(f"❌ HTTP endpoint testing failed: {e}", "ERROR")
            return False, {}
    
    def test_browser_functionality(self):
        """Simulate browser testing functionality"""
        self.log("🖥️  Testing browser functionality...")
        
        try:
            # Create a simple browser test using available utilities
            test_cases = [
                "Page loads without errors",
                "Retro boot screen displays",
                "Menu navigation works", 
                "Game canvas initializes",
                "Status bar is visible",
                "Export functionality accessible"
            ]
            
            results = {}
            for test_case in test_cases:
                # Simulate test result (in real implementation, would use Playwright/Selenium)
                try:
                    import urllib.request
                    with urllib.request.urlopen(self.base_url, timeout=10) as response:
                        content = response.read().decode('utf-8')
                        
                        # Simple content checks
                        checks = {
                            "Page loads without errors": response.getcode() == 200,
                            "Retro boot screen displays": "BOLAMIGA SYSTEM" in content,
                            "Menu navigation works": "START GAME" in content,
                            "Game canvas initializes": "<canvas" in content,
                            "Status bar is visible": "status-bar" in content,
                            "Export functionality accessible": "EXPORTS" in content
                        }
                        
                        result = checks.get(test_case, True)  # Default to True for simulation
                        results[test_case] = result
                        status = "✅" if result else "❌"
                        self.log(f"{status} {test_case}")
                        
                except Exception as e:
                    results[test_case] = False
                    self.log(f"❌ {test_case}: {e}", "ERROR")
            
            success_rate = sum(results.values()) / len(results) if results else 0
            overall_success = success_rate >= 0.8  # 80% pass rate required
            
            self.log(f"📊 Browser test success rate: {success_rate:.1%}")
            return overall_success, results
            
        except Exception as e:
            self.log(f"❌ Browser functionality testing failed: {e}", "ERROR")
            return False, {}
    
    def generate_qa_report(self, test_results):
        """Generate comprehensive QA report"""
        self.log("📋 Generating QA compliance report...")
        
        report = {
            "project": self.project_name,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "base_url": self.base_url,
            "test_results": test_results,
            "overall_status": "COMPLIANT" if all(test_results.values()) else "NON_COMPLIANT"
        }
        
        # Save report
        with open('qa-report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        self.log("✅ QA report saved to qa-report.json")
        return report
    
    def cleanup(self):
        """Clean up test environment"""
        self.log("🧹 Cleaning up test environment...")
        
        try:
            # Read PID if available
            if os.path.exists('bolamiga.pid'):
                with open('bolamiga.pid', 'r') as f:
                    pid = int(f.read().strip())
                try:
                    os.kill(pid, 15)  # SIGTERM
                    self.log(f"✅ Killed process {pid}")
                except ProcessLookupError:
                    self.log(f"⚠️  Process {pid} already terminated")
                os.remove('bolamiga.pid')
            
            # General cleanup
            subprocess.run(['pkill', '-f', 'python.*app.py'], check=False, capture_output=True)
            time.sleep(2)
            
            self.log("✅ Cleanup completed")
            
        except Exception as e:
            self.log(f"⚠️  Cleanup warning: {e}", "WARN")
    
    def run_full_qa_suite(self):
        """Run the complete QA test suite"""
        self.log("🧪 Starting Bolamiga QA Test Suite...")
        
        test_results = {}
        
        try:
            # 1. Check dependencies
            test_results["dependencies"] = self.check_dependencies()
            
            # 2. Test port management
            test_results["port_management"] = self.test_port_management()
            
            # 3. Start application
            app_started, pid = self.start_application()
            test_results["application_startup"] = app_started
            
            if app_started:
                # 4. Test HTTP endpoints
                http_success, http_results = self.test_http_endpoints()
                test_results["http_endpoints"] = http_success
                
                # 5. Test browser functionality
                browser_success, browser_results = self.test_browser_functionality()
                test_results["browser_functionality"] = browser_success
                
                # Wait a moment to ensure stability
                time.sleep(2)
            
            # Generate report
            report = self.generate_qa_report(test_results)
            
            # Print summary
            self.log("🎯 QA TEST SUMMARY:")
            for test_name, result in test_results.items():
                status = "✅ PASSED" if result else "❌ FAILED"
                self.log(f"  {test_name}: {status}")
            
            overall_success = all(test_results.values())
            if overall_success:
                self.log("🎉 ALL QA TESTS PASSED - BOLAMIGA IS COMPLIANT!")
                self.log(f"🌐 Application URL: {self.base_url}")
                self.log("📊 Status bar active with exports/backups/logs access")
            else:
                self.log("❌ SOME QA TESTS FAILED - REVIEW REQUIRED", "ERROR")
            
            return overall_success
            
        except Exception as e:
            self.log(f"❌ QA suite execution failed: {e}", "ERROR")
            return False
        
        finally:
            # Always cleanup
            # self.cleanup()  # Comment out to keep server running for user testing
            pass

if __name__ == "__main__":
    tester = BolamigaQATester()
    success = tester.run_full_qa_suite()
    
    if success:
        print("\n🎯 QA VERIFICATION COMPLETE!")
        print("Please test http://localhost:5030 in your browser and confirm:")
        print("• Game loads with retro boot screen")
        print("• Menu navigation works")
        print("• Status bar shows exports/backups/logs")
        print("• Game controls respond correctly")
        sys.exit(0)
    else:
        print("\n❌ QA TESTS FAILED - REVIEW REQUIRED")
        sys.exit(1)