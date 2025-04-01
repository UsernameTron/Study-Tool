#!/usr/bin/env python3
"""
Setup script for the Anatomy Study App
This script generates all required resources and validates the application
"""
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('setup_app')

def main():
    """Run all setup steps"""
    logger.info("Starting application setup...")
    
    # Ensure directories exist
    from image_utils import ensure_directories
    ensure_directories()
    logger.info("Directory structure verified")
    
    # Generate placeholder images
    try:
        from static.images.create_placeholder_images import create_placeholder_images
        create_placeholder_images()
        logger.info("Diagram placeholders generated successfully")
    except Exception as e:
        logger.error(f"Error generating diagram placeholders: {str(e)}")
    
    try:
        from static.images.generate_histology_placeholders import generate_histology_placeholders
        generate_histology_placeholders()
        logger.info("Histology placeholders generated successfully")
    except Exception as e:
        logger.error(f"Error generating histology placeholders: {str(e)}")
    
    # Run deployment verification
    try:
        from verify_deployment import DeploymentVerifier
        verifier = DeploymentVerifier()
        results = verifier.verify_all()
        if results["overall_status"] in ["READY FOR DEPLOYMENT", "READY WITH WARNINGS"]:
            logger.info("Deployment verification passed")
        else:
            logger.warning("Deployment verification failed. See logs for details.")
    except Exception as e:
        logger.error(f"Error running deployment verification: {str(e)}")
    
    logger.info("Setup complete!")

if __name__ == "__main__":
    main()