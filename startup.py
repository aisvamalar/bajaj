#!/usr/bin/env python3
"""
Azure App Service startup script for the Document Intelligence API.
This script handles the startup process and launches the FastAPI application.
"""

import os
import sys
import logging
import subprocess
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def install_dependencies():
    """Install required dependencies for Azure deployment."""
    try:
        logger.info("Installing dependencies...")
        
        # Install system dependencies if needed
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Install requirements
        if os.path.exists("requirements-azure.txt"):
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements-azure.txt"])
            logger.info("Dependencies installed successfully from requirements-azure.txt")
        elif os.path.exists("requirements.txt"):
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            logger.info("Dependencies installed successfully from requirements.txt")
        else:
            logger.warning("No requirements file found")
            
    except Exception as e:
        logger.error(f"Failed to install dependencies: {e}")
        # Continue anyway, as dependencies might already be installed

def create_directories():
    """Create necessary directories for the application."""
    directories = ["data", "embeddings", "metadata", "chunks", "temp_downloads"]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created directory: {directory}")

def setup_environment():
    """Setup environment variables and configuration."""
    # Set default environment variables if not present
    if not os.getenv("NVIDIA_API_KEY"):
        logger.warning("NVIDIA_API_KEY not set. Please configure it in Azure App Service settings.")
    
    # Set Azure-specific configurations
    os.environ.setdefault("AZURE_DEPLOYMENT", "true")
    
    logger.info("Environment setup completed")

def test_imports():
    """Test if all required modules can be imported."""
    try:
        logger.info("Testing imports...")
        
        # Test basic imports
        import fastapi
        import uvicorn
        import requests
        import numpy
        import pandas
        
        # Test ML imports
        try:
            import torch
            logger.info("PyTorch imported successfully")
        except ImportError:
            logger.warning("PyTorch not available")
        
        try:
            import sentence_transformers
            logger.info("Sentence Transformers imported successfully")
        except ImportError:
            logger.warning("Sentence Transformers not available")
        
        try:
            from langchain_nvidia_ai_endpoints import ChatNVIDIA
            logger.info("LangChain NVIDIA imported successfully")
        except ImportError:
            logger.warning("LangChain NVIDIA not available")
        
        logger.info("All imports successful")
        return True
        
    except Exception as e:
        logger.error(f"Import test failed: {e}")
        return False

def main():
    """Main startup function for Azure deployment."""
    try:
        logger.info("Starting Azure deployment...")
        
        # Setup environment
        setup_environment()
        
        # Create necessary directories
        create_directories()
        
        # Test imports
        if not test_imports():
            logger.error("Import test failed. Check dependencies.")
            return
        
        # Import the FastAPI app
        try:
            from api import app
            logger.info("FastAPI app imported successfully")
        except Exception as e:
            logger.error(f"Failed to import FastAPI app: {e}")
            return
        
        # Get port from environment (Azure App Service sets WEBSITES_PORT)
        port = int(os.environ.get("WEBSITES_PORT", 8000))
        host = "0.0.0.0"  # Bind to all interfaces
        
        logger.info(f"Starting FastAPI application on {host}:{port}")
        
        # Start the FastAPI application
        import uvicorn
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info"
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 