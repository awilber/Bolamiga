#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bolamiga QA Testing Suite
Comprehensive testing using available QA utilities
"""

import subprocess
import time
import json
import sys
import os

class BolamigaQATester:
    def __init__(self):
        self.project_name = "Bolamiga"
        self.project_path = os.getcwd()
        self.base_url = "http://localhost:5030"
        self.utils_path = "../utils"
        
    def log(self, message, level="INFO"):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print("[{}] [{}] {}".format(timestamp, level, message))
    
    def test_canvas_feature_progression(self):
        """Test iPhone canvas feature progression to identify breaking point"""
        self.log("🧪 Testing iPhone Canvas Feature Progression...")
        
        try:
            import urllib.request
            
            # Test endpoints in order of complexity
            test_endpoints = [
                ("/canvas-test", "Progressive Canvas Feature Tests"),
                ("/minimal", "Basic Shape Rendering (Known Working)"),
                ("/game", "Full Game Engine (Known Broken on iPhone)")
            ]
            
            results = {}
            
            for endpoint, description in test_endpoints:
                url = "{}{}".format(self.base_url, endpoint)
                try:
                    with urllib.request.urlopen(url, timeout=10) as response:
                        status_code = response.getcode()
                        content = response.read().decode('utf-8')
                        content_length = len(content)
                        
                        # Analyze content for iPhone compatibility indicators
                        has_canvas = "<canvas" in content
                        has_iphone_specific = "iPhone" in content
                        has_debug_mode = "iPhone Debug Mode" in content
                        has_platform_detection = "PlatformManager" in content
                        has_animation_loop = "requestAnimationFrame" in content
                        has_complex_rendering = "particle" in content.lower()
                        
                        results[endpoint] = {
                            "status": status_code,
                            "content_length": content_length,
                            "success": True,
                            "analysis": {
                                "has_canvas": has_canvas,
                                "has_iphone_specific": has_iphone_specific,
                                "has_debug_mode": has_debug_mode,
                                "has_platform_detection": has_platform_detection,
                                "has_animation_loop": has_animation_loop,
                                "has_complex_rendering": has_complex_rendering
                            },
                            "description": description
                        }
                        
                        self.log("✅ {}: {} ({} bytes)".format(endpoint, status_code, content_length))
                        
                        # Log specific findings
                        if has_debug_mode:
                            self.log("⚠️  {} contains iPhone Debug Mode fallback".format(endpoint))
                        if has_platform_detection:
                            self.log("📱 {} has platform detection logic".format(endpoint))
                        if has_complex_rendering:
                            self.log("🎮 {} includes complex game rendering".format(endpoint))
                            
                except Exception as e:
                    results[endpoint] = {
                        "error": str(e),
                        "success": False,
                        "description": description
                    }
                    self.log("❌ {}: {}".format(endpoint, e), "ERROR")
            
            # Analysis Summary
            self.log("📊 Canvas Feature Progression Analysis:")
            for endpoint, result in results.items():
                if result.get("success"):
                    analysis = result.get("analysis", {})
                    complexity_score = sum([
                        analysis.get("has_canvas", False),
                        analysis.get("has_animation_loop", False),
                        analysis.get("has_complex_rendering", False),
                        analysis.get("has_platform_detection", False)
                    ])
                    self.log("  {}: Complexity Level {} (iPhone ready: {})".format(
                        endpoint, 
                        complexity_score, 
                        "No" if analysis.get("has_debug_mode") else "Unknown"
                    ))
                    
            return True, results
            
        except Exception as e:
            self.log("❌ Canvas feature progression testing failed: {}".format(e), "ERROR")
            return False, {}
    
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
                "/api/highscores",
                "/canvas-test"
            ]
            
            results = {}
            for endpoint in endpoints:
                url = "{}{}".format(self.base_url, endpoint)
                try:
                    with urllib.request.urlopen(url, timeout=10) as response:
                        status_code = response.getcode()
                        content_length = len(response.read())
                        results[endpoint] = {
                            "status": status_code,
                            "content_length": content_length,
                            "success": True
                        }
                        self.log("✅ {}: {} ({} bytes)".format(endpoint, status_code, content_length))
                        
                except urllib.error.HTTPError as e:
                    results[endpoint] = {
                        "status": e.code,
                        "error": str(e),
                        "success": False
                    }
                    self.log("❌ {}: HTTP {} - {}".format(endpoint, e.code, e), "ERROR")
                    
                except Exception as e:
                    results[endpoint] = {
                        "error": str(e),
                        "success": False
                    }
                    self.log("❌ {}: {}".format(endpoint, e), "ERROR")
            
            # Check if at least root endpoint works
            success = results.get("/", {}).get("success", False)
            return success, results
            
        except Exception as e:
            self.log("❌ HTTP endpoint testing failed: {}".format(e), "ERROR")
            return False, {}
    
    def run_phase1_qa_suite(self):
        """Run Phase 1 specific QA tests"""
        self.log("🧪 Starting Phase 1 QA Test Suite...")
        
        test_results = {}
        
        try:
            # 1. Test canvas feature progression
            canvas_success, canvas_results = self.test_canvas_feature_progression()
            test_results["canvas_feature_progression"] = canvas_success
            
            # 2. Test HTTP endpoints
            http_success, http_results = self.test_http_endpoints()
            test_results["http_endpoints"] = http_success
            
            # Generate report
            report = {
                "project": self.project_name,
                "phase": "Phase 1: Canvas Rendering Fix",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "base_url": self.base_url,
                "test_results": test_results,
                "canvas_analysis": canvas_results,
                "http_analysis": http_results,
                "overall_status": "PASSED" if all(test_results.values()) else "NEEDS_WORK"
            }
            
            # Save report
            with open('qa-report-phase1.json', 'w') as f:
                json.dump(report, f, indent=2)
            
            # Print summary
            self.log("🎯 PHASE 1 QA TEST SUMMARY:")
            for test_name, result in test_results.items():
                status = "✅ PASSED" if result else "❌ FAILED"
                self.log("  {}: {}".format(test_name, status))
            
            overall_success = all(test_results.values())
            if overall_success:
                self.log("🎉 PHASE 1 QA TESTS PASSED!")
                self.log("🌐 Canvas Test URL: {}/canvas-test".format(self.base_url))
                self.log("📊 Ready for progressive iPhone testing")
            else:
                self.log("❌ SOME PHASE 1 QA TESTS FAILED - REVIEW REQUIRED", "ERROR")
            
            return overall_success
            
        except Exception as e:
            self.log("❌ Phase 1 QA suite execution failed: {}".format(e), "ERROR")
            return False

if __name__ == "__main__":
    tester = BolamigaQATester()
    success = tester.run_phase1_qa_suite()
    
    if success:
        print("\n🎯 PHASE 1 QA VERIFICATION COMPLETE!")
        print("Next steps:")
        print("• Test http://localhost:5030/canvas-test on iPhone Chrome")
        print("• Identify which test level breaks on iPhone")
        print("• Fix the specific iPhone Chrome incompatibility")
        print("• Verify game objects are visible on iPhone")
        sys.exit(0)
    else:
        print("\n❌ PHASE 1 QA TESTS FAILED - REVIEW REQUIRED")
        sys.exit(1)