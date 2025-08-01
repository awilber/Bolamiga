#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bolamiga iPhone QA Testing - CrossPlatformQA Simulation
"""

import requests
import json
import time
import sys
from datetime import datetime

def log_message(level, message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("[{}] [{}] {}".format(timestamp, level, message))

def run_iphone_qa_tests():
    """
    Simulate CrossPlatformQA testing for iPhone compatibility
    """
    log_message("INFO", "🚀 Starting Bolamiga iPhone CrossPlatformQA Test")
    
    base_url = "http://localhost:5030"
    results = {
        "test_suite": "iPhone_CrossPlatform_QA",
        "timestamp": datetime.now().isoformat(),
        "base_url": base_url,
        "platform": "iPhone Safari/Chrome",
        "tests": [],
        "critical_issues": [],
        "github_issues": []
    }
    
    # Test 1: Basic server connectivity
    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            results["tests"].append({
                "name": "server_connectivity",
                "status": "PASS",
                "description": "Server responds to HTTP requests"
            })
            log_message("PASS", "✅ Server connectivity test")
        else:
            results["tests"].append({
                "name": "server_connectivity",
                "status": "FAIL", 
                "description": "Server returned status {}".format(response.status_code)
            })
            log_message("FAIL", "❌ Server connectivity: {}".format(response.status_code))
    except Exception as e:
        results["tests"].append({
            "name": "server_connectivity",
            "status": "FAIL",
            "description": "Connection failed: {}".format(str(e))
        })
        log_message("FAIL", "❌ Server connectivity failed: {}".format(e))
    
    # Test 2: Game page accessibility
    try:
        response = requests.get(base_url + "/game", timeout=10)
        if response.status_code == 200 and "canvas" in response.text.lower():
            results["tests"].append({
                "name": "game_page_canvas",
                "status": "PASS",
                "description": "Game page loads with canvas element"
            })
            log_message("PASS", "✅ Game page with canvas")
        else:
            results["tests"].append({
                "name": "game_page_canvas",
                "status": "FAIL",
                "description": "Game page missing canvas or failed to load"
            })
            log_message("FAIL", "❌ Game page canvas missing")
    except Exception as e:
        results["tests"].append({
            "name": "game_page_canvas",
            "status": "FAIL",
            "description": "Game page request failed: {}".format(str(e))
        })
        log_message("FAIL", "❌ Game page failed: {}".format(e))
    
    # Test 3: iPhone debug endpoints
    debug_endpoints = ["/debug", "/minimal", "/comparison"]
    for endpoint in debug_endpoints:
        try:
            response = requests.get(base_url + endpoint, timeout=10)
            if response.status_code == 200:
                results["tests"].append({
                    "name": "debug_endpoint_{}".format(endpoint.replace("/", "")),
                    "status": "PASS",
                    "description": "iPhone debug endpoint {} accessible".format(endpoint)
                })
                log_message("PASS", "✅ Debug endpoint {}".format(endpoint))
            else:
                results["tests"].append({
                    "name": "debug_endpoint_{}".format(endpoint.replace("/", "")),
                    "status": "FAIL", 
                    "description": "Debug endpoint {} returned {}".format(endpoint, response.status_code)
                })
                log_message("FAIL", "❌ Debug endpoint {}: {}".format(endpoint, response.status_code))
        except Exception as e:
            results["tests"].append({
                "name": "debug_endpoint_{}".format(endpoint.replace("/", "")),
                "status": "FAIL",
                "description": "Debug endpoint {} failed: {}".format(endpoint, str(e))
            })
            log_message("FAIL", "❌ Debug endpoint {} failed: {}".format(endpoint, e))
    
    # Identify Critical iPhone Issues (from our debugging)
    critical_issues = [
        {
            "issue_id": "IPHONE_CANVAS_001",
            "title": "🚨 CRITICAL: iPhone Canvas Rendering Completely Broken",
            "severity": "CRITICAL",
            "description": "iPhone users see only dark green background instead of game",
            "affected_platforms": ["iOS Safari", "iOS Chrome"],
            "evidence": {
                "working_endpoint": "/minimal shows iPhone canvas works perfectly",
                "broken_endpoint": "/game shows only dark green background",
                "comparison_endpoint": "/comparison provides side-by-side evidence"
            },
            "root_cause": "Complex game initialization interferes with iPhone Canvas 2D context",
            "impact": "Complete game inaccessibility on mobile platform",
            "recommendation": "Replace main game iPhone rendering with proven minimal approach"
        },
        {
            "issue_id": "IPHONE_UX_002", 
            "title": "📱 Mobile UX: Missing iPhone Safe Area and Touch Optimization",
            "severity": "MAJOR",
            "description": "Missing safe area support, viewport meta, touch controls",
            "affected_platforms": ["iOS Safari", "iOS Chrome"],
            "missing_features": [
                "CSS safe-area-inset for iPhone notch/home indicator",
                "Proper viewport meta tag for mobile",
                "Touch-friendly game controls",
                "Responsive design adaptation"
            ],
            "impact": "Poor mobile experience, unusable interface",
            "recommendation": "Add mobile-first responsive design"
        },
        {
            "issue_id": "IPHONE_PERF_003",
            "title": "⚡ Performance: iPhone-Specific Optimization Needed", 
            "severity": "MAJOR",
            "description": "Game performance not optimized for iPhone limitations",
            "performance_issues": [
                "Targeting 60 FPS on iPhone (should be 24-30 FPS)",
                "Using desktop canvas size (should be limited for iPhone)",
                "No memory management for iOS Safari limitations",
                "Not handling iOS autoplay restrictions"
            ],
            "iphone_limitations": {
                "ios_safari_canvas_limit": "2048x2048 pixels max",
                "ios_safari_memory_limit": "64MB recommended",
                "ios_audio_restriction": "Requires user interaction", 
                "iphone_chrome_constraints": "Similar Canvas/memory limits"
            },
            "recommendation": "Add iPhone-specific performance configuration"
        }
    ]
    
    results["critical_issues"] = critical_issues
    
    # Generate GitHub Issues
    github_issues = []
    for issue in critical_issues:
        github_issue = {
            "title": issue["title"],
            "body": generate_github_issue_body(issue),
            "labels": get_github_labels(issue)
        }
        github_issues.append(github_issue)
        results["github_issues"].append(github_issue)
    
    # Calculate test summary
    total_tests = len(results["tests"])
    passed_tests = len([t for t in results["tests"] if t["status"] == "PASS"])
    failed_tests = total_tests - passed_tests
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    results["summary"] = {
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": failed_tests,
        "success_rate": success_rate,
        "critical_issues_count": len([i for i in critical_issues if i["severity"] == "CRITICAL"]),
        "major_issues_count": len([i for i in critical_issues if i["severity"] == "MAJOR"])
    }
    
    # Log results
    log_message("INFO", "📊 QA Test Summary:")
    log_message("INFO", "  Total Tests: {}".format(total_tests))
    log_message("INFO", "  Passed: {} ({:.1f}%)".format(passed_tests, success_rate))
    log_message("INFO", "  Failed: {}".format(failed_tests))
    log_message("INFO", "  Critical Issues: {}".format(results["summary"]["critical_issues_count"]))
    log_message("INFO", "  Major Issues: {}".format(results["summary"]["major_issues_count"]))
    
    # Save results
    with open('iphone-qa-report.json', 'w') as f:
        json.dump(results, f, indent=2)
    log_message("INFO", "📋 Report saved to iphone-qa-report.json")
    
    # Save GitHub issues  
    with open('github-issues.json', 'w') as f:
        json.dump(github_issues, f, indent=2)
    log_message("INFO", "📋 GitHub issues saved to github-issues.json")
    
    return results

def generate_github_issue_body(issue):
    """Generate GitHub issue body from issue data"""
    if issue["issue_id"] == "IPHONE_CANVAS_001":
        return """## Problem
iPhone users see only a dark green background instead of the game on both Safari and Chrome.

## Evidence  
- `/debug` endpoint shows iPhone Canvas 2D context works perfectly
- `/minimal` endpoint demonstrates working iPhone game rendering  
- `/game` endpoint fails despite using identical approach
- `/comparison` endpoint provides side-by-side evidence

## Root Cause
Complex game initialization in main game interferes with iPhone Canvas rendering, while minimal approach works flawlessly.

## Impact
- **Severity**: Critical
- **Affected Users**: All iPhone users (Safari + Chrome)  
- **Business Impact**: Complete game inaccessibility on mobile platform

## Solution
Replace main game iPhone rendering pipeline with proven minimal game approach:

```javascript
// iPhone: Use EXACT working approach from minimal game
if (currentPlatformConfig.platform.isIPhone) {
    ctx.fillStyle = '#000022';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    if (player) {
        ctx.fillStyle = '#00FF00';
        ctx.fillRect(player.x, player.y, player.width, player.height);
    }
    return; // Exit early - NO complex systems for iPhone
}
```

## Testing URLs
- Working: http://98.81.133.84:5030/minimal
- Broken: http://98.81.133.84:5030/game  
- Debug: http://98.81.133.84:5030/comparison

## Acceptance Criteria
- [ ] iPhone shows moving game elements (green player, red enemies, yellow bullets)
- [ ] Game runs at stable frame rate on iPhone
- [ ] Touch controls work for iPhone users
- [ ] No dark green screen or empty canvas issues"""
    
    elif issue["issue_id"] == "IPHONE_UX_002":
        return """## Problem
Bolamiga lacks proper mobile optimization for iPhone devices.

## Missing Features
1. **Safe Area Support**: No CSS safe-area-inset for iPhone notch/home indicator
2. **Viewport Meta Tag**: Missing proper mobile viewport configuration
3. **Touch Controls**: No touch-friendly game controls
4. **Responsive Design**: Fixed desktop layout doesn't adapt to mobile screens

## Impact
- **Severity**: Major
- **Affected Users**: iPhone and mobile users
- **UX Impact**: Poor mobile experience, unusable interface

## Implementation
Add mobile-first responsive design:

```html
<!-- Viewport meta tag -->
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">

<!-- Safe area CSS -->
.game-container {
    padding: env(safe-area-inset-top) env(safe-area-inset-right) env(safe-area-inset-bottom) env(safe-area-inset-left);
}

<!-- Touch controls -->
.touch-controls {
    display: none;
}

@media (pointer: coarse) {
    .touch-controls {
        display: block;
    }
}
```

## Acceptance Criteria
- [ ] Game respects iPhone safe areas (notch, home indicator)
- [ ] Touch controls appear on mobile devices
- [ ] Proper viewport scaling on all mobile devices
- [ ] Responsive layout adapts to mobile screen sizes"""
    
    elif issue["issue_id"] == "IPHONE_PERF_003":
        return """## Problem
Game performance on iPhone is suboptimal due to hardware limitations not being addressed.

## Performance Issues
1. **Frame Rate**: Targeting 60 FPS on iPhone (should be 24-30 FPS)
2. **Canvas Size**: Using desktop canvas size (should be limited for iPhone)
3. **Memory Usage**: No memory management for iOS Safari limitations
4. **Audio Restrictions**: Not handling iOS autoplay restrictions

## iPhone Limitations
- iOS Safari: Canvas limited to 2048x2048 pixels
- iOS Safari: Very limited memory (64MB recommended)
- iOS: Audio requires user interaction
- iPhone Chrome: Similar Canvas/memory constraints

## Implementation
Add iPhone-specific performance configuration:

```javascript
const iPhoneConfig = {
    maxCanvasSize: { width: 400, height: 300 },
    targetFPS: 24,
    maxMemoryUsage: 64, // MB
    audioRequiresInteraction: true,
    reducedEffects: true
};
```

## Acceptance Criteria
- [ ] Stable 24+ FPS on iPhone devices
- [ ] Canvas size appropriate for iPhone memory limits
- [ ] Audio works after user interaction
- [ ] No memory-related crashes on extended play"""
    
    return "Issue details: {}".format(issue["description"])

def get_github_labels(issue):
    """Get appropriate GitHub labels for issue"""
    labels = []
    
    if issue["severity"] == "CRITICAL":
        labels.extend(["bug", "critical", "mobile", "iPhone"])
    elif issue["severity"] == "MAJOR": 
        labels.extend(["enhancement", "mobile", "UX"])
    
    if "canvas" in issue["description"].lower():
        labels.append("canvas")
    
    if "performance" in issue["description"].lower():
        labels.append("performance")
        
    if "responsive" in issue["description"].lower():
        labels.append("responsive")
    
    return labels

if __name__ == "__main__":
    log_message("INFO", "🧪 Starting Bolamiga iPhone CrossPlatformQA Test")
    
    results = run_iphone_qa_tests()
    
    # Determine exit code
    critical_issues = results["summary"]["critical_issues_count"]
    failed_tests = results["summary"]["failed_tests"]
    
    if critical_issues > 0:
        log_message("ERROR", "🚨 Found {} CRITICAL issues requiring immediate attention".format(critical_issues))
        log_message("INFO", "📋 GitHub issues generated for all critical problems")
        sys.exit(2)  # Critical issues
    elif failed_tests > 0:
        log_message("WARN", "⚠️  Found {} failing tests".format(failed_tests))
        sys.exit(1)  # Test failures
    else:
        log_message("INFO", "✅ All tests passed - no critical issues found")
        sys.exit(0)  # Success