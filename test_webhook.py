#!/usr/bin/env python3
"""
Test script for the Document Intelligence API webhook
Use this to test your deployed Azure webhook endpoint.
"""

import requests
import json
import sys
from datetime import datetime

def test_webhook_endpoint(base_url, api_token):
    """Test the webhook endpoint with a sample request."""
    
    # Test URL
    url = f"{base_url}/hackrx/run"
    
    # Sample request payload
    payload = {
        "questions": [
            "What is the main topic of this document?",
            "What are the key features mentioned?"
        ],
        "documents": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_token}"
    }
    
    print(f"🧪 Testing webhook endpoint: {url}")
    print(f"📤 Sending request with {len(payload['questions'])} questions...")
    
    try:
        # Send POST request
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        print(f"📊 Response Status: {response.status_code}")
        print(f"⏱️  Response Time: {response.elapsed.total_seconds():.2f} seconds")
        
        if response.status_code == 200:
            print("✅ Request successful!")
            
            # Parse and display response
            try:
                data = response.json()
                print("\n📋 Response Data:")
                print(f"   - Number of answers: {len(data.get('answers', []))}")
                
                if 'processing_info' in data:
                    print(f"   - Processing status: {data['processing_info'].get('status', 'unknown')}")
                
                if 'search_info' in data:
                    print(f"   - Search strategy: {data['search_info'].get('search_strategy', 'unknown')}")
                
                # Display answers
                print("\n💬 Answers:")
                for i, answer in enumerate(data.get('answers', []), 1):
                    print(f"   {i}. {answer[:200]}{'...' if len(answer) > 200 else ''}")
                
            except json.JSONDecodeError:
                print("⚠️  Response is not valid JSON")
                print(f"Raw response: {response.text[:500]}...")
                
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (60 seconds)")
        print("This might be normal for the first request as the app is starting up.")
        
    except requests.exceptions.ConnectionError:
        print("❌ Connection error")
        print("Please check if the webhook URL is correct and the app is running.")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_health_endpoint(base_url):
    """Test the health/status endpoint."""
    try:
        # Test API documentation endpoint
        docs_url = f"{base_url}/docs"
        response = requests.get(docs_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ API documentation is accessible")
            print(f"📚 Docs URL: {docs_url}")
        else:
            print(f"⚠️  API docs returned status {response.status_code}")
            
    except Exception as e:
        print(f"⚠️  Could not access API docs: {e}")

def main():
    """Main test function."""
    print("🧪 Document Intelligence API Webhook Tester")
    print("=" * 50)
    
    # Get webhook URL from user
    webhook_url = input("Enter your webhook URL (e.g., https://your-app.azurewebsites.net): ").strip()
    if not webhook_url:
        print("❌ Webhook URL is required")
        return
    
    # Remove trailing slash if present
    webhook_url = webhook_url.rstrip('/')
    
    # Get API token
    api_token = input("Enter your API token (or press Enter for default): ").strip()
    if not api_token:
        api_token = "9f40f077e610d431226b59eec99652153ccad94769da6779cc01725731999634"
        print("Using default API token")
    
    print(f"\n🌐 Testing webhook: {webhook_url}")
    print(f"🔑 Using API token: {api_token[:10]}...")
    print("=" * 50)
    
    # Test health endpoint
    print("\n1️⃣ Testing API health...")
    test_health_endpoint(webhook_url)
    
    # Test webhook endpoint
    print("\n2️⃣ Testing webhook endpoint...")
    test_webhook_endpoint(webhook_url, api_token)
    
    print("\n" + "=" * 50)
    print("🎉 Testing completed!")
    print("\n📋 Next steps:")
    print("1. If tests passed, your webhook is ready to use")
    print("2. If tests failed, check Azure Portal logs")
    print("3. Wait a few minutes and try again if the app is starting up")
    print("4. Use the webhook URL in your applications")

if __name__ == "__main__":
    main() 