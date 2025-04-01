import logging
import os

def configure_logging():
    """Configure centralized logging for the application"""
    # Ensure log directory exists
    os.makedirs("logs", exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("logs/application.log")
        ]
    )
    
    # Return logger for module use
    return logging.getLogger