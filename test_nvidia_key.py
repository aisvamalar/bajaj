#!/usr/bin/env python3
"""
Quick test script for NVIDIA API key
This script will test if your NVIDIA API key is working correctly.
"""

import os
import sys
from dotenv import load_dotenv

def test_api_key():
    """Test if the NVIDIA API key is working."""
    print("🔑 Testing NVIDIA API Key...")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Check if API key exists
    api_key = os.getenv("NVIDIA_API_KEY")
    
    if not api_key:
        print("❌ NVIDIA_API_KEY not found in environment")
        print("\n📝 To fix this:")
        print("1. Create a .env file in your project root")
        print("2. Add: NVIDIA_API_KEY=your_api_key_here")
        print("3. Get your API key from: https://ai.nvidia.com/")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    # Test the API key
    try:
        print("\n🧪 Testing API connection...")
        from langchain_nvidia_ai_endpoints import ChatNVIDIA
        
        # Try to initialize the LLM
        llm = ChatNVIDIA(model="meta/llama-3.1-70b-instruct")
        
        # Test with a simple request
        print("📤 Sending test request...")
        response = llm.invoke("Say hello in one sentence!")
        
        print("✅ API Key is working!")
        print(f"📥 Response: {response.content}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you have installed the required packages:")
        print("pip install langchain-nvidia-ai-endpoints")
        return False
        
    except Exception as e:
        print(f"❌ API Key test failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check if your API key is correct")
        print("2. Make sure you have internet connection")
        print("3. Try again in a few minutes (rate limiting)")
        print("4. Check if the model is available in your region")
        return False

def setup_env_file():
    """Help user create .env file."""
    print("\n📝 Creating .env file...")
    
    api_key = input("Enter your NVIDIA API key: ").strip()
    
    if not api_key:
        print("❌ API key is required")
        return False
    
    # Create .env file
    with open(".env", "w") as f:
        f.write(f"NVIDIA_API_KEY={api_key}\n")
    
    print("✅ .env file created successfully!")
    return True

def main():
    """Main function."""
    print("🚀 NVIDIA API Key Tester")
    print("=" * 40)
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        print("📁 .env file not found")
        create_env = input("Would you like to create one? (y/n): ").strip().lower()
        
        if create_env == 'y':
            if not setup_env_file():
                return
        else:
            print("❌ Cannot test without API key")
            return
    
    # Test the API key
    success = test_api_key()
    
    if success:
        print("\n🎉 Your NVIDIA API key is working correctly!")
        print("✅ You can now deploy to Azure")
    else:
        print("\n❌ API key test failed")
        print("Please check the troubleshooting steps above")

if __name__ == "__main__":
    main() 