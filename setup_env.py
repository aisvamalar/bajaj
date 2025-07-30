#!/usr/bin/env python3
"""
Environment Variable Setup Script
This script helps you set up the NVIDIA_API_KEY environment variable.
"""

import os
import sys

def create_env_file():
    """Create .env file with NVIDIA API key."""
    print("🔧 Setting up NVIDIA API Key...")
    print("=" * 40)
    
    # Get API key from user
    api_key = input("Enter your NVIDIA API key: ").strip()
    
    if not api_key:
        print("❌ API key is required")
        return False
    
    # Validate API key format
    if not api_key.startswith("nvapi-"):
        print("⚠️  Warning: API key should start with 'nvapi-'")
        continue_anyway = input("Continue anyway? (y/n): ").strip().lower()
        if continue_anyway != 'y':
            return False
    
    # Create .env file
    try:
        with open(".env", "w") as f:
            f.write(f"NVIDIA_API_KEY={api_key}\n")
        
        print("✅ .env file created successfully!")
        print(f"📁 File location: {os.path.abspath('.env')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def check_env_file():
    """Check if .env file exists and has the API key."""
    if not os.path.exists(".env"):
        print("📁 .env file not found")
        return False
    
    try:
        with open(".env", "r") as f:
            content = f.read().strip()
        
        if "NVIDIA_API_KEY=" in content:
            print("✅ .env file exists and contains NVIDIA_API_KEY")
            return True
        else:
            print("⚠️  .env file exists but doesn't contain NVIDIA_API_KEY")
            return False
            
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return False

def show_azure_instructions():
    """Show instructions for setting up in Azure."""
    print("\n🌐 Azure Setup Instructions:")
    print("=" * 40)
    print("1. Go to Azure Portal: https://portal.azure.com")
    print("2. Find your App Service")
    print("3. Click 'Settings' → 'Configuration'")
    print("4. Click 'New application setting'")
    print("5. Set:")
    print("   - Name: NVIDIA_API_KEY")
    print("   - Value: Your API key")
    print("6. Click 'OK' and 'Save'")

def main():
    """Main setup function."""
    print("🚀 Environment Variable Setup")
    print("=" * 40)
    
    # Check if .env file already exists
    if check_env_file():
        overwrite = input("\n.env file already exists. Overwrite? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("Keeping existing .env file")
            show_azure_instructions()
            return
    
    # Create .env file
    if create_env_file():
        print("\n✅ Local setup completed!")
        
        # Test the setup
        print("\n🧪 Testing setup...")
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            api_key = os.getenv("NVIDIA_API_KEY")
            if api_key:
                print("✅ Environment variable loaded successfully!")
                print(f"🔑 API Key: {api_key[:10]}...")
            else:
                print("❌ Environment variable not loaded")
                
        except ImportError:
            print("⚠️  python-dotenv not installed. Install with: pip install python-dotenv")
        
        # Show Azure instructions
        show_azure_instructions()
        
    else:
        print("❌ Setup failed. Please try again.")

if __name__ == "__main__":
    main() 