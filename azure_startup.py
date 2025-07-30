#!/usr/bin/env python3
"""
Azure App Service startup script for the Document Intelligence API.
This script handles the startup process and launches the FastAPI application.
"""

import os
import sys
import logging
import uvicorn
from startup import install_dependencies, create_directories, setup_environment

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main startup function for Azure deployment."""
    try:
        logger.info("Starting Azure deployment...")
        
        # Setup environment
        setup_environment()
        
        # Create necessary directories
        create_directories()
        
        # Import the FastAPI app
        from api import app
        
        # Get port from environment (Azure App Service sets WEBSITES_PORT)
        port = int(os.environ.get("WEBSITES_PORT", 8000))
        host = "0.0.0.0"  # Bind to all interfaces
        
        logger.info(f"Starting FastAPI application on {host}:{port}")
        
        # Start the FastAPI application
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