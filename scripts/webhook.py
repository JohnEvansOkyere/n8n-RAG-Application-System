"""
Test script for n8n webhook endpoint
"""

import requests
import json
import uuid
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL")

def test_basic_chat():
    """Test basic chat functionality"""
    print("\n" + "="*50)
    print("TEST 1: Basic Chat Request")
    print("="*50)
    
    payload = {
        "message": "What is VexaAI?",
        "session_id": str(uuid.uuid4()),
        "user_id": str(uuid.uuid4())
    }
    
    print(f"\n📤 Sending request to: {WEBHOOK_URL}")
    print(f"📦 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\n✅ Status Code: {response.status_code}")
        print(f"📥 Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("\n✅ TEST PASSED")
            return True
        else:
            print("\n❌ TEST FAILED")
            return False
            
    except requests.exceptions.Timeout:
        print("\n❌ TEST FAILED: Request timeout")
        return False
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        return False


def test_empty_message():
    """Test validation with empty message"""
    print("\n" + "="*50)
    print("TEST 2: Empty Message Validation")
    print("="*50)
    
    payload = {
        "message": "",
        "session_id": str(uuid.uuid4()),
        "user_id": str(uuid.uuid4())
    }
    
    print(f"\n📤 Sending request with empty message")
    print(f"📦 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\n📊 Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print("✅ TEST PASSED: Empty message rejected")
            return True
        else:
            print("⚠️  TEST WARNING: Empty message accepted (should be rejected)")
            return False
            
    except Exception as e:
        print(f"✅ TEST PASSED: Validation error as expected - {str(e)}")
        return True


def test_missing_fields():
    """Test validation with missing required fields"""
    print("\n" + "="*50)
    print("TEST 3: Missing Required Fields")
    print("="*50)
    
    payload = {
        "message": "Test message"
        # Missing session_id and user_id
    }
    
    print(f"\n📤 Sending request with missing fields")
    print(f"📦 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\n📊 Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print("✅ TEST PASSED: Missing fields rejected")
            return True
        else:
            print("⚠️  TEST WARNING: Missing fields accepted (should be rejected)")
            return False
            
    except Exception as e:
        print(f"✅ TEST PASSED: Validation error as expected - {str(e)}")
        return True


def test_long_message():
    """Test with a long message"""
    print("\n" + "="*50)
    print("TEST 4: Long Message")
    print("="*50)
    
    long_message = "What is VexaAI? " * 100  # Create a long message
    
    payload = {
        "message": long_message,
        "session_id": str(uuid.uuid4()),
        "user_id": str(uuid.uuid4())
    }
    
    print(f"\n📤 Sending long message ({len(long_message)} chars)")
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60  # Longer timeout for processing
        )
        
        print(f"\n✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ TEST PASSED: Long message processed")
            return True
        else:
            print("❌ TEST FAILED")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        return False


def test_session_continuity():
    """Test multiple messages in same session"""
    print("\n" + "="*50)
    print("TEST 5: Session Continuity")
    print("="*50)
    
    session_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    
    messages = [
        "What is VexaAI?",
        "Tell me more about its features",
        "How can I get started?"
    ]
    
    print(f"\n📝 Testing {len(messages)} messages in same session")
    print(f"🔑 Session ID: {session_id}")
    
    for i, message in enumerate(messages, 1):
        print(f"\n--- Message {i}/{len(messages)} ---")
        
        payload = {
            "message": message,
            "session_id": session_id,
            "user_id": user_id
        }
        
        try:
            response = requests.post(
                WEBHOOK_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"✅ Message {i} sent successfully")
            else:
                print(f"❌ Message {i} failed")
                return False
                
        except Exception as e:
            print(f"❌ Message {i} error: {str(e)}")
            return False
    
    print("\n✅ TEST PASSED: All messages sent in same session")
    return True


def test_webhook_availability():
    """Test if webhook is accessible"""
    print("\n" + "="*50)
    print("TEST 0: Webhook Availability")
    print("="*50)
    
    print(f"\n🔍 Checking webhook at: {WEBHOOK_URL}")
    
    try:
        # Try a simple request
        response = requests.post(
            WEBHOOK_URL,
            json={"test": "ping"},
            timeout=5
        )
        
        print(f"✅ Webhook is accessible (Status: {response.status_code})")
        return True
        
    except requests.exceptions.Timeout:
        print("❌ Webhook timeout - Check if n8n is running")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - Check webhook URL and n8n status")
        return False
    except Exception as e:
        print(f"⚠️  Webhook check error: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("\n" + "🚀"*25)
    print("VexaAI RAG Application - Webhook Test Suite")
    print("🚀"*25)
    print(f"\nTimestamp: {datetime.now().isoformat()}")
    print(f"Webhook URL: {WEBHOOK_URL}")
    
    if not WEBHOOK_URL:
        print("\n❌ ERROR: N8N_WEBHOOK_URL not set in .env file")
        return
    
    results = []
    
    # Run tests
    results.append(("Webhook Availability", test_webhook_availability()))
    results.append(("Basic Chat", test_basic_chat()))
    results.append(("Empty Message Validation", test_empty_message()))
    results.append(("Missing Fields Validation", test_missing_fields()))
    results.append(("Long Message", test_long_message()))
    results.append(("Session Continuity", test_session_continuity()))
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! Your webhook is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the logs above for details.")


if __name__ == "__main__":
    main()