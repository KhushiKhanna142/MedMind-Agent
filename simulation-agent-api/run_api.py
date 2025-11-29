"""
API Launcher Script for Simulation Agent

Run this script to start the Simulation Agent API server
"""

import uvicorn
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """
    Start the Simulation Agent API server
    """
    logger.info("=" * 60)
    logger.info("Starting Simulation Agent API Server")
    logger.info("=" * 60)
    
    uvicorn.run(
        "src.api.simulation_api:app",
        host="0.0.0.0",  # Allow external connections
        port=8000,
        reload=True,  # Auto-reload on code changes
        log_level="info"
    )


if __name__ == "__main__":
    main()
