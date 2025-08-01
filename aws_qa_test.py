#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AWS Production QA Testing - Verify iPhone fixes are working in production
"""

import requests
import json
import time
import sys
from datetime import datetime

def log_message(level, message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("[{}] [{}] {}".format(timestamp, level, message))

def run_aws_production_qa():
    """Run QA tests on AWS production deployment"""
    log_message("INFO", "🌐 Starting AWS Production QA Test")
    
    base_url = "http://3.88.17.81"
    results = {
        "test_suite": "AWS_Production_QA",
        "timestamp": datetime.now().isoformat(),
        "base_url": base_url,
        "platform": "AWS EC2 Production",
        "tests": [],
        "iphone_fixes_verification": []
    }
    
    # Test 1: Basic connectivity and health
    endpoints = [
        {"path": "/", "name": "root_page", "expected_content": "BOLAMIGA"},
        {"path": "/game", "name": "game_page", "expected_content": "gameCanvas"},
        {"path": "/api/health", "name": "health_api", "expected_content": "healthy"},
        {"path": "/debug", "name": "iphone_debug", "expected_content": "iPhone Chrome Canvas Debug"},
        {"path": "/minimal", "name": "minimal_working", "expected_content": "canvas"},
        {"path": "/comparison", "name": "comparison_test", "expected_content": "iPhone Game Comparison"}
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(base_url + endpoint["path"], timeout=10)
            content_check = endpoint["expected_content"] in response.text
            
            test_result = {
                "name": endpoint["name"],
                "status": "PASS" if response.status_code == 200 and content_check else "FAIL",
                "url": base_url + endpoint["path"],
                "http_status": response.status_code,
                "content_size": len(response.text),
                "content_check": content_check,
                "response_time_ms": int(response.elapsed.total_seconds() * 1000)
            }
            
            results["tests"].append(test_result)
            
            if test_result["status"] == "PASS":
                log_message("PASS", "✅ {} - {}ms - {}B".format(
                    endpoint["path"], 
                    test_result["response_time_ms"],
                    test_result["content_size"]
                ))
            else:
                log_message("FAIL", "❌ {} - HTTP {} - Content check: {}".format(
                    endpoint["path"],
                    response.status_code,
                    content_check
                ))
                
        except Exception as e:
            test_result = {
                "name": endpoint["name"],
                "status": "FAIL",
                "url": base_url + endpoint["path"],
                "error": str(e)
            }
            results["tests"].append(test_result)
            log_message("FAIL", "❌ {} - Error: {}".format(endpoint["path"], e))
    
    # Test 2: iPhone-specific fixes verification
    iphone_verifications = [
        {
            "feature": "iPhone Canvas Fix",
            "test": "Game page loads with iPhone-specific rendering code",
            "verification": "Check for iPhone platform detection and minimal rendering"
        },
        {
            "feature": "Touch Controls",
            "test": "Game page includes touch control buttons for mobile devices",
            "verification": "Check for touch-controls div and button elements"
        },
        {
            "feature": "Safe Area Support", 
            "test": "Base template includes viewport-fit=cover and safe area CSS",
            "verification": "Check for safe-area-inset CSS variables"
        },
        {
            "feature": "Performance Optimization",
            "test": "Game includes iPhone-specific performance configurations",
            "verification": "Check for iPhoneConfig object and frame rate limiting"
        }
    ]
    
    log_message("INFO", "🍎 Verifying iPhone fixes in production...")
    
    # Get game page content for detailed verification
    try:
        game_response = requests.get(base_url + "/game", timeout=10)
        game_content = game_response.text
        
        for verification in iphone_verifications:
            # Check for specific implementation markers
            checks = {
                "iPhone Canvas Fix": "currentPlatformConfig.platform.isIPhone" in game_content,
                "Touch Controls": "touch-controls" in game_content and "touch-fire" in game_content,
                "Safe Area Support": "viewport-fit=cover" in game_content and "safe-area-inset" in game_content,
                "Performance Optimization": "iPhoneConfig" in game_content and "targetFPS" in game_content
            }
            
            feature_implemented = checks.get(verification["feature"], False)
            
            verification_result = {
                "feature": verification["feature"],
                "status": "IMPLEMENTED" if feature_implemented else "MISSING",
                "test_description": verification["test"],
                "verification_method": verification["verification"]
            }
            
            results["iphone_fixes_verification"].append(verification_result)
            
            status_emoji = "✅" if feature_implemented else "❌"
            log_message("INFO", "{} {}: {}".format(
                status_emoji,
                verification["feature"],
                "IMPLEMENTED" if feature_implemented else "MISSING"
            ))
            
    except Exception as e:
        log_message("ERROR", "Failed to verify iPhone fixes: {}".format(e))
    
    # Calculate summary
    total_tests = len(results["tests"])
    passed_tests = len([t for t in results["tests"] if t["status"] == "PASS"])
    total_iphone_fixes = len(results["iphone_fixes_verification"])
    implemented_fixes = len([f for f in results["iphone_fixes_verification"] if f["status"] == "IMPLEMENTED"])
    
    results["summary"] = {
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": total_tests - passed_tests,
        "test_success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
        "iphone_fixes_total": total_iphone_fixes,
        "iphone_fixes_implemented": implemented_fixes,
        "iphone_fixes_rate": (implemented_fixes / total_iphone_fixes * 100) if total_iphone_fixes > 0 else 0
    }
    
    # Log final summary
    log_message("INFO", "📊 AWS Production QA Summary:")
    log_message("INFO", "  Endpoint Tests: {}/{} passed ({:.1f}%)".format(
        passed_tests, total_tests, results["summary"]["test_success_rate"]
    ))
    log_message("INFO", "  iPhone Fixes: {}/{} implemented ({:.1f}%)".format(
        implemented_fixes, total_iphone_fixes, results["summary"]["iphone_fixes_rate"]
    ))
    
    # Determine overall status
    if passed_tests == total_tests and implemented_fixes == total_iphone_fixes:
        log_message("PASS", "🎉 AWS Production: FULLY OPERATIONAL with all iPhone fixes")
        overall_status = "FULLY_OPERATIONAL"
        exit_code = 0
    elif passed_tests == total_tests:
        log_message("WARN", "⚠️  AWS Production: Endpoints working but some iPhone fixes missing")
        overall_status = "OPERATIONAL_WITH_ISSUES"
        exit_code = 1
    else:
        log_message("FAIL", "❌ AWS Production: Critical issues detected")
        overall_status = "CRITICAL_ISSUES"
        exit_code = 2
    
    results["overall_status"] = overall_status
    
    # Save report
    with open('aws-production-qa-report.json', 'w') as f:
        json.dump(results, f, indent=2)
    log_message("INFO", "📋 AWS Production QA report saved")
    
    return exit_code

if __name__ == "__main__":
    exit_code = run_aws_production_qa()
    sys.exit(exit_code)