#!/usr/bin/env python3
"""
Fix Deployment Issues Script
This script helps fix common Azure deployment issues.
"""

import os
import sys
import subprocess
import json

def check_current_setup():
    """Check the current setup and identify issues."""
    print("🔍 Checking current setup...")
    print("=" * 40)
    
    issues = []
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        issues.append("❌ .env file not found")
    else:
        print("✅ .env file exists")
    
    # Check if requirements files exist
    if not os.path.exists("requirements-azure.txt"):
        issues.append("❌ requirements-azure.txt not found")
    else:
        print("✅ requirements-azure.txt exists")
    
    # Check if API key is set
    try:
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv("NVIDIA_API_KEY")
        if not api_key:
            issues.append("❌ NVIDIA_API_KEY not found in .env file")
        else:
            print("✅ NVIDIA_API_KEY found")
    except ImportError:
        issues.append("❌ python-dotenv not installed")
    
    # Check if GitHub workflow exists
    if not os.path.exists(".github/workflows/main_x2xcoders.yml"):
        issues.append("❌ GitHub workflow file not found")
    else:
        print("✅ GitHub workflow file exists")
    
    return issues

def fix_requirements():
    """Fix requirements file issues."""
    print("\n🔧 Fixing requirements file...")
    
    # Use the simplified requirements file
    if os.path.exists("requirements-azure.txt"):
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements-azure.txt"], 
                         check=True, capture_output=True)
            print("✅ Requirements installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install requirements: {e}")
            return False
    else:
        print("❌ requirements-azure.txt not found")
        return False

def setup_github_secrets():
    """Guide user to set up GitHub secrets."""
    print("\n🔑 Setting up GitHub Secrets...")
    print("=" * 40)
    print("1. Go to your GitHub repository")
    print("2. Click Settings → Secrets and variables → Actions")
    print("3. Add these secrets:")
    print("   - AZURE_WEBAPP_PUBLISH_PROFILE: Your Azure publish profile")
    print("   - NVIDIA_API_KEY: Your NVIDIA API key")
    print("\nTo get your publish profile:")
    print("1. Go to Azure Portal → Your App Service")
    print("2. Click 'Get publish profile'")
    print("3. Download and copy the content")

def setup_azure_environment():
    """Guide user to set up Azure environment variables."""
    print("\n🌐 Setting up Azure Environment Variables...")
    print("=" * 40)
    print("1. Go to Azure Portal → Your App Service")
    print("2. Click 'Settings' → 'Configuration'")
    print("3. Click 'New application setting'")
    print("4. Add:")
    print("   - Name: NVIDIA_API_KEY")
    print("   - Value: Your NVIDIA API key")
    print("5. Click 'OK' and 'Save'")

def test_local_setup():
    """Test the local setup."""
    print("\n🧪 Testing local setup...")
    
    try:
        # Test basic imports
        import fastapi
        import uvicorn
        print("✅ FastAPI and Uvicorn imported")
        
        # Test ML imports
        try:
            import torch
            print("✅ PyTorch imported")
        except ImportError:
            print("⚠️  PyTorch not available")
        
        # Test NVIDIA API
        try:
            from langchain_nvidia_ai_endpoints import ChatNVIDIA
            print("✅ LangChain NVIDIA imported")
        except ImportError:
            print("⚠️  LangChain NVIDIA not available")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def create_deployment_files():
    """Create necessary deployment files."""
    print("\n📁 Creating deployment files...")
    
    # Create directories
    directories = ["data", "embeddings", "metadata", "chunks", "temp_downloads"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Create .github/workflows directory if it doesn't exist
    os.makedirs(".github/workflows", exist_ok=True)
    print("✅ Created .github/workflows directory")

def main():
    """Main fix function."""
    print("🚀 Azure Deployment Fix Script")
    print("=" * 40)
    
    # Check current setup
    issues = check_current_setup()
    
    if issues:
        print(f"\nFound {len(issues)} issues:")
        for issue in issues:
            print(f"  {issue}")
        
        print("\n🔧 Fixing issues...")
        
        # Create deployment files
        create_deployment_files()
        
        # Fix requirements
        if not fix_requirements():
            print("❌ Failed to fix requirements")
            return
        
        # Test local setup
        if not test_local_setup():
            print("❌ Local setup test failed")
            return
        
        # Guide user through remaining setup
        setup_github_secrets()
        setup_azure_environment()
        
        print("\n✅ Setup completed!")
        print("\n📋 Next steps:")
        print("1. Set up GitHub secrets (see instructions above)")
        print("2. Set up Azure environment variables (see instructions above)")
        print("3. Push changes to trigger new deployment:")
        print("   git add .")
        print("   git commit -m 'Fix deployment issues'")
        print("   git push origin main")
        
    else:
        print("✅ No issues found! Your setup looks good.")
        print("\n📋 To deploy:")
        print("1. Make sure GitHub secrets are set")
        print("2. Make sure Azure environment variables are set")
        print("3. Push changes to trigger deployment")

if __name__ == "__main__":
    main() 