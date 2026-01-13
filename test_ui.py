#!/usr/bin/env python3
"""
Terminal-based test for the Umbrasol Neural Interface.
This script verifies that the API and WebSocket endpoints are functional.
"""
import asyncio
import json
import sys
import websockets
import requests
from datetime import datetime

API_URL = "http://localhost:8091"
WS_URL = "ws://localhost:8091/ws/thoughts"

def test_health_endpoint():
    """Test the /health REST endpoint."""
    print("\n[TEST 1] Testing /health endpoint...")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Health endpoint OK")
            print(f"  Status: {data.get('status')}")
            print(f"  Version: {data.get('version')}")
            print(f"  Platform: {data.get('platform')}")
            print(f"  CPU: {data.get('telemetry', {}).get('cpu')}%")
            print(f"  RAM: {data.get('telemetry', {}).get('ram')}%")
            return True
        else:
            print(f"✗ Health endpoint returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Health endpoint failed: {e}")
        return False

def test_ui_endpoint():
    """Test that the UI is being served."""
    print("\n[TEST 2] Testing UI serving...")
    try:
        response = requests.get(API_URL, timeout=5)
        if response.status_code == 200 and "Umbrasol" in response.text:
            print(f"✓ UI is being served correctly")
            print(f"  Content length: {len(response.text)} bytes")
            return True
        else:
            print(f"✗ UI endpoint returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ UI endpoint failed: {e}")
        return False

async def test_websocket():
    """Test WebSocket connection and message exchange."""
    print("\n[TEST 3] Testing WebSocket connection...")
    try:
        async with websockets.connect(WS_URL) as websocket:
            print("✓ WebSocket connected successfully")
            
            # Send a test command
            test_command = {"command": "What is 2+2?", "voice": False}
            print(f"\n[TEST 4] Sending test command: {test_command['command']}")
            await websocket.send(json.dumps(test_command))
            print("✓ Command sent")
            
            # Wait for responses
            print("\n[TEST 5] Waiting for responses...")
            response_count = 0
            timeout = 30  # 30 seconds timeout
            
            try:
                async with asyncio.timeout(timeout):
                    while response_count < 10:  # Limit to 10 messages
                        message = await websocket.recv()
                        data = json.loads(message)
                        response_count += 1
                        
                        msg_type = data.get('type', 'unknown')
                        content = data.get('content', '')
                        
                        print(f"  [{response_count}] Type: {msg_type}")
                        if content:
                            print(f"      Content: {content[:100]}...")
                        
                        if msg_type == 'done':
                            print("\n✓ Received 'done' signal - conversation complete")
                            break
                            
            except asyncio.TimeoutError:
                print(f"\n⚠ Timeout after {timeout}s - received {response_count} messages")
            
            if response_count > 0:
                print(f"\n✓ WebSocket communication successful ({response_count} messages)")
                return True
            else:
                print("\n✗ No messages received from WebSocket")
                return False
                
    except Exception as e:
        print(f"✗ WebSocket test failed: {e}")
        return False

async def main():
    print("=" * 60)
    print("Umbrasol Neural Interface - Terminal Test Suite")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Test REST endpoints
    results.append(test_health_endpoint())
    results.append(test_ui_endpoint())
    
    # Test WebSocket
    ws_result = await test_websocket()
    results.append(ws_result)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED - Interface is fully functional")
        print("\nYou can now open http://localhost:8091 in your browser.")
        print("The interface should be fully interactive.")
        return 0
    else:
        print("\n✗ SOME TESTS FAILED - Interface may not work correctly")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
