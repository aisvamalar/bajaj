#!/usr/bin/env python3
"""
Azure Deployment Script for Document Intelligence API
This script helps automate the deployment process to Azure App Service.
"""

import os
import sys
import subprocess
import json
import requests
from pathlib import Path

def check_prerequisites():
    """Check if all prerequisites are met."""
    print("🔍 Checking prerequisites...")
    
    # Check if Git is installed
    try:
        subprocess.run(["git", "--version"], check=True, capture_output=True)
        print("✅ Git is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Git is not installed. Please install Git first.")
        return False
    
    # Check if Azure CLI is installed
    try:
        subprocess.run(["az", "--version"], check=True, capture_output=True)
        print("✅ Azure CLI is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Azure CLI is not installed. You can still deploy via Azure Portal.")
    
    # Check if .env file exists
    if os.path.exists(".env"):
        print("✅ .env file found")
    else:
        print("⚠️  .env file not found. You'll need to set NVIDIA_API_KEY in Azure Portal.")
    
    # Check if required files exist
    required_files = ["api.py", "azure_startup.py", "azure-requirements.txt"]
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file} found")
        else:
            print(f"❌ {file} not found")
            return False
    
    return True

def setup_git():
    """Initialize Git repository if not already done."""
    if not os.path.exists(".git"):
        print("📁 Initializing Git repository...")
        subprocess.run(["git", "init"], check=True)
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Initial commit for Azure deployment"], check=True)
        print("✅ Git repository initialized")
    else:
        print("✅ Git repository already exists")

def create_azure_app():
    """Create Azure App Service using Azure CLI."""
    print("🚀 Creating Azure App Service...")
    
    # Get app name from user
    app_name = input("Enter your Azure App Service name (must be unique globally): ").strip()
    if not app_name:
        print("❌ App name is required")
        return None
    
    resource_group = input("Enter resource group name (or press Enter for 'fin-rag-rg'): ").strip() or "fin-rag-rg"
    region = input("Enter region (or press Enter for 'eastus'): ").strip() or "eastus"
    
    try:
        # Create resource group
        print(f"📦 Creating resource group: {resource_group}")
        subprocess.run([
            "az", "group", "create", 
            "--name", resource_group, 
            "--location", region
        ], check=True)
        
        # Create app service plan
        plan_name = f"{app_name}-plan"
        print(f"📋 Creating app service plan: {plan_name}")
        subprocess.run([
            "az", "appservice", "plan", "create",
            "--name", plan_name,
            "--resource-group", resource_group,
            "--sku", "F1",
            "--is-linux"
        ], check=True)
        
        # Create web app
        print(f"🌐 Creating web app: {app_name}")
        subprocess.run([
            "az", "webapp", "create",
            "--name", app_name,
            "--resource-group", resource_group,
            "--plan", plan_name,
            "--runtime", "PYTHON:3.11"
        ], check=True)
        
        print(f"✅ Azure App Service created successfully!")
        print(f"🌐 Your webhook URL will be: https://{app_name}.azurewebsites.net/hackrx/run")
        
        return {
            "app_name": app_name,
            "resource_group": resource_group,
            "region": region
        }
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create Azure resources: {e}")
        return None

def configure_environment_variables(app_name, resource_group):
    """Configure environment variables in Azure."""
    print("🔧 Configuring environment variables...")
    
    nvidia_key = input("Enter your NVIDIA API key: ").strip()
    if not nvidia_key:
        print("⚠️  No NVIDIA API key provided. You'll need to set it manually in Azure Portal.")
        return
    
    try:
        subprocess.run([
            "az", "webapp", "config", "appsettings", "set",
            "--name", app_name,
            "--resource-group", resource_group,
            "--settings", f"NVIDIA_API_KEY={nvidia_key}"
        ], check=True)
        print("✅ Environment variables configured")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to configure environment variables: {e}")
        print("Please set NVIDIA_API_KEY manually in Azure Portal")

def deploy_to_azure(app_name, resource_group):
    """Deploy the application to Azure."""
    print("🚀 Deploying to Azure...")
    
    try:
        # Use az webapp up for deployment
        subprocess.run([
            "az", "webapp", "up",
            "--name", app_name,
            "--resource-group", resource_group,
            "--runtime", "PYTHON:3.11",
            "--sku", "F1"
        ], check=True)
        
        print("✅ Deployment completed successfully!")
        print(f"🌐 Your webhook URL: https://{app_name}.azurewebsites.net/hackrx/run")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Deployment failed: {e}")
        print("You can still deploy manually via Azure Portal")

def test_deployment(app_name):
    """Test the deployed application."""
    print("🧪 Testing deployment...")
    
    url = f"https://{app_name}.azurewebsites.net/hackrx/run"
    
    # Simple health check
    try:
        response = requests.get(url.replace("/hackrx/run", "/docs"), timeout=10)
        if response.status_code == 200:
            print("✅ Application is running!")
            print(f"📚 API Documentation: {url.replace('/hackrx/run', '/docs')}")
        else:
            print(f"⚠️  Application might not be ready yet. Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Could not test deployment: {e}")
        print("The app might still be starting up. Please wait a few minutes and try again.")

def main():
    """Main deployment function."""
    print("🚀 Azure Deployment Script for Document Intelligence API")
    print("=" * 60)
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please fix the issues above and try again.")
        return
    
    print("\n" + "=" * 60)
    
    # Setup Git
    setup_git()
    
    print("\n" + "=" * 60)
    
    # Create Azure resources
    azure_config = create_azure_app()
    if not azure_config:
        print("\n❌ Failed to create Azure resources. Please try again.")
        return
    
    print("\n" + "=" * 60)
    
    # Configure environment variables
    configure_environment_variables(azure_config["app_name"], azure_config["resource_group"])
    
    print("\n" + "=" * 60)
    
    # Deploy application
    deploy_to_azure(azure_config["app_name"], azure_config["resource_group"])
    
    print("\n" + "=" * 60)
    
    # Test deployment
    test_deployment(azure_config["app_name"])
    
    print("\n" + "=" * 60)
    print("🎉 Deployment process completed!")
    print("\n📋 Next steps:")
    print("1. Wait 2-5 minutes for the app to fully start")
    print("2. Test your webhook URL with a sample request")
    print("3. Monitor logs in Azure Portal if needed")
    print("4. Set up spending alerts to avoid unexpected charges")

if __name__ == "__main__":
    main() 