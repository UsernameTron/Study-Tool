#!/usr/bin/env python3
"""
Run all tests for the Anatomy Study App
"""
import os
import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('run_tests')

def main():
    """Run all tests and report results"""
    logger.info("Running tests...")
    
    # Check if pytest is installed
    try:
        import pytest
    except ImportError:
        logger.error("pytest not installed. Please install with: pip install pytest")
        return 1
    
    # Run the tests
    result = pytest.main(['-xvs', 'tests'])
    
    if result == 0:
        logger.info("All tests passed!")
    else:
        logger.error("Some tests failed.")
    
    return result

if __name__ == "__main__":
    sys.exit(main())