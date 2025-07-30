#!/usr/bin/env node

// Simple mobile verification test for Bolamiga iPhone fixes
const http = require('http');

const testURL = 'http://localhost:5030';
const iPhoneUserAgent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1';

console.log('📱 Testing Bolamiga iPhone Mobile Improvements');
console.log('==============================================');

// Test 1: Health check
console.log('\n🔍 Step 1: Testing server health...');
const healthReq = http.request(testURL + '/api/health', (res) => {
    let data = '';
    res.on('data', chunk => data += chunk);
    res.on('end', () => {
        const health = JSON.parse(data);
        console.log(health.status === 'healthy' ? '✅ Server healthy' : '❌ Server unhealthy');
        
        // Test 2: Game page with iPhone user agent
        console.log('\n🔍 Step 2: Testing game page with iPhone user agent...');
        const gameReq = http.request(testURL + '/game', {
            headers: { 'User-Agent': iPhoneUserAgent }
        }, (res) => {
            let gameData = '';
            res.on('data', chunk => gameData += chunk);
            res.on('end', () => {
                // Check for mobile improvements
                const hasPlatformManager = gameData.includes('PlatformManager');
                const hasEmergencyPositioning = gameData.includes('iPhone Emergency Positioning');
                const hasResponsivePositioning = gameData.includes('responsivePositioning');
                const hasSafeAreaSupport = gameData.includes('safe-area-inset');
                
                console.log(`${hasPlatformManager ? '✅' : '❌'} Platform detection system loaded`);
                console.log(`${hasEmergencyPositioning ? '✅' : '❌'} iPhone emergency positioning implemented`);
                console.log(`${hasResponsivePositioning ? '✅' : '❌'} Responsive positioning enabled`);
                console.log(`${hasSafeAreaSupport ? '✅' : '❌'} iPhone safe area support included`);
                
                // Check positioning values
                const mobileConfigMatch = gameData.match(/playerStartY:\s*([\d.]+)/);
                if (mobileConfigMatch) {
                    const playerY = parseFloat(mobileConfigMatch[1]);
                    const isHighEnough = playerY <= 0.40; // Should be 35% or higher on screen
                    console.log(`${isHighEnough ? '✅' : '❌'} Player positioned high enough (${Math.round(playerY * 100)}% from top)`);
                }
                
                console.log('\n📋 MOBILE TEST RESULTS SUMMARY');
                console.log('===============================');
                
                if (hasPlatformManager && hasEmergencyPositioning && hasResponsivePositioning && hasSafeAreaSupport) {
                    console.log('✅ ALL MOBILE IMPROVEMENTS DETECTED');
                    console.log('📱 iPhone users should now see their ship in the upper third of screen');
                    console.log('🎮 Ready for iPhone testing at: http://localhost:5030');
                } else {
                    console.log('❌ SOME MOBILE IMPROVEMENTS MISSING');
                    console.log('🔧 Check implementation and redeploy');
                }
                
                console.log('\n🚀 Next Steps:');
                console.log('1. Test on actual iPhone Safari browser');
                console.log('2. Check browser console for "iPhone Emergency Positioning" message');
                console.log('3. Verify ship is visible in upper portion of game area');
            });
        });
        gameReq.end();
    });
});

healthReq.on('error', (err) => {
    console.log('❌ Server not accessible:', err.message);
    console.log('💡 Make sure Bolamiga is running on port 5030');
});

healthReq.end();