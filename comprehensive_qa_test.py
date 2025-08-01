#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive QA Testing Suite for Bolamiga - Tests both localhost and AWS deployment
"""

import requests
import json
import time
import sys
from datetime import datetime

def log_message(level, message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("[{}] [{}] {}".format(timestamp, level, message))

def test_endpoint(base_url, endpoint, timeout=10):
    """Test a specific endpoint and return detailed results"""
    full_url = "{}{}".format(base_url, endpoint)
    try:
        response = requests.get(full_url, timeout=timeout)
        return {
            "url": full_url,
            "status_code": response.status_code,
            "response_time": response.elapsed.total_seconds(),
            "content_length": len(response.text),
            "success": 200 <= response.status_code < 400,
            "has_content": len(response.text) > 100,
            "error": None
        }
    except requests.exceptions.Timeout:
        return {
            "url": full_url,
            "status_code": None,
            "response_time": None,
            "content_length": 0,
            "success": False,
            "has_content": False,
            "error": "Connection timeout after {}s".format(timeout)
        }
    except requests.exceptions.ConnectionError:
        return {
            "url": full_url,
            "status_code": None,
            "response_time": None,
            "content_length": 0,
            "success": False,
            "has_content": False,
            "error": "Connection refused"
        }
    except Exception as e:
        return {
            "url": full_url,
            "status_code": None,
            "response_time": None,
            "content_length": 0,
            "success": False,
            "has_content": False,
            "error": str(e)
        }

def run_comprehensive_qa():
    """Run comprehensive QA tests on both localhost and AWS"""
    log_message("INFO", "🧪 Starting Comprehensive Bolamiga QA Test Suite")
    
    # Test targets
    targets = {
        "localhost": {
            "base_url": "http://localhost:5030",
            "description": "Local development server",
            "timeout": 5
        },
        "aws": {
            "base_url": "http://98.85.254.126",
            "description": "AWS EC2 production deployment (port 80)",
            "timeout": 15
        },
        "aws_direct": {
            "base_url": "http://98.85.254.126:5030",
            "description": "AWS EC2 direct port access (port 5030)",
            "timeout": 15
        }
    }
    
    # Endpoints to test
    endpoints = [
        "/",
        "/game", 
        "/api/health",
        "/api/highscores",
        "/debug",
        "/minimal",
        "/comparison"
    ]
    
    results = {
        "test_suite": "Comprehensive_Bolamiga_QA",
        "timestamp": datetime.now().isoformat(),
        "targets_tested": len(targets),
        "endpoints_tested": len(endpoints),
        "results": {}
    }
    
    # Test each target
    for target_name, target_config in targets.items():
        log_message("INFO", "🎯 Testing {}: {}".format(target_name.upper(), target_config["description"]))
        
        target_results = {
            "target_info": target_config,
            "endpoint_results": [],
            "summary": {
                "total_endpoints": len(endpoints),
                "successful_endpoints": 0,
                "failed_endpoints": 0,
                "avg_response_time": 0,
                "total_content_length": 0
            }
        }
        
        total_response_time = 0
        response_count = 0
        
        for endpoint in endpoints:
            log_message("INFO", "  Testing {}/{}{}".format(target_name, target_config["base_url"], endpoint))
            
            test_result = test_endpoint(
                target_config["base_url"], 
                endpoint, 
                target_config["timeout"]
            )
            
            target_results["endpoint_results"].append(test_result)
            
            if test_result["success"]:
                target_results["summary"]["successful_endpoints"] += 1
                log_message("PASS", "  ✅ {} - {}ms - {}B".format(
                    endpoint, 
                    int(test_result["response_time"] * 1000) if test_result["response_time"] else 0,
                    test_result["content_length"]
                ))
                
                if test_result["response_time"]:
                    total_response_time += test_result["response_time"]
                    response_count += 1
                    
                target_results["summary"]["total_content_length"] += test_result["content_length"]
            else:
                target_results["summary"]["failed_endpoints"] += 1
                log_message("FAIL", "  ❌ {} - Error: {}".format(
                    endpoint, 
                    test_result["error"] or "HTTP {}".format(test_result["status_code"])
                ))
        
        # Calculate averages
        if response_count > 0:
            target_results["summary"]["avg_response_time"] = total_response_time / response_count
        
        target_results["summary"]["success_rate"] = (
            target_results["summary"]["successful_endpoints"] / 
            target_results["summary"]["total_endpoints"] * 100
        )
        
        results["results"][target_name] = target_results
        
        # Log target summary
        log_message("INFO", "📊 {} Summary: {}/{} endpoints ({:.1f}% success rate)".format(
            target_name.upper(),
            target_results["summary"]["successful_endpoints"],
            target_results["summary"]["total_endpoints"],
            target_results["summary"]["success_rate"]
        ))
    
    # Overall analysis
    log_message("INFO", "🔍 Performing deployment analysis...")
    
    localhost_success = results["results"]["localhost"]["summary"]["success_rate"]
    aws_port80_success = results["results"]["aws"]["summary"]["success_rate"]  
    aws_port5030_success = results["results"]["aws_direct"]["summary"]["success_rate"]
    
    analysis = {
        "localhost_operational": localhost_success > 80,
        "aws_port80_operational": aws_port80_success > 80,
        "aws_port5030_operational": aws_port5030_success > 80,
        "deployment_status": "unknown"
    }
    
    if analysis["localhost_operational"] and analysis["aws_port80_operational"]:
        analysis["deployment_status"] = "fully_operational"
        log_message("PASS", "🎉 Full deployment operational - localhost and AWS working")
    elif analysis["localhost_operational"] and analysis["aws_port5030_operational"]:
        analysis["deployment_status"] = "aws_partial"
        log_message("WARN", "⚠️  AWS deployment partial - direct port works, nginx proxy may be down")
    elif analysis["localhost_operational"]:
        analysis["deployment_status"] = "localhost_only"
        log_message("WARN", "⚠️  Only localhost operational - AWS deployment not accessible")
    else:
        analysis["deployment_status"] = "critical_failure"
        log_message("ERROR", "🚨 Critical failure - no working endpoints detected")
    
    results["analysis"] = analysis
    
    # Save comprehensive report
    with open('comprehensive-qa-report.json', 'w') as f:
        json.dump(results, f, indent=2)
    log_message("INFO", "📋 Comprehensive report saved to comprehensive-qa-report.json")
    
    # Print final summary
    log_message("INFO", "🎯 COMPREHENSIVE QA SUMMARY:")
    log_message("INFO", "  Localhost: {:.1f}% success rate".format(localhost_success))
    log_message("INFO", "  AWS Port 80: {:.1f}% success rate".format(aws_port80_success))
    log_message("INFO", "  AWS Port 5030: {:.1f}% success rate".format(aws_port5030_success))
    log_message("INFO", "  Deployment Status: {}".format(analysis["deployment_status"].upper()))
    
    # Return appropriate exit code
    if analysis["deployment_status"] == "fully_operational":
        return 0
    elif analysis["deployment_status"] in ["aws_partial", "localhost_only"]:
        return 1
    else:
        return 2

if __name__ == "__main__":
    exit_code = run_comprehensive_qa()
    sys.exit(exit_code)