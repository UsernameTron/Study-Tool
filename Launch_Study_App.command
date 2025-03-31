#!/bin/bash

# Print header
echo "====================================="
echo "    Anatomy Study App Launcher     "
echo "====================================="
echo ""

# Store the absolute path to the project directory
PROJECT_DIR="/Users/cpconnor/CascadeProjects/study_app"

# Navigate to the project directory
cd "$PROJECT_DIR" || {
    echo "Error: Could not navigate to the project directory."
    echo "Please check if the following directory exists: $PROJECT_DIR"
    echo "Press any key to exit..."
    read -n 1
    exit 1
}

echo "Setting up environment..."

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    echo "Please install Python 3 and try again."
    echo "Press any key to exit..."
    read -n 1
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv || {
        echo "Error: Failed to create virtual environment."
        echo "Press any key to exit..."
        read -n 1
        exit 1
    }
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate || {
    echo "Error: Failed to activate virtual environment."
    echo "Press any key to exit..."
    read -n 1
    exit 1
}

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt || {
    echo "Error: Failed to install dependencies."
    echo "Press any key to exit..."
    read -n 1
    exit 1
}

# Verify deployment readiness
echo "Verifying deployment readiness..."
python verify_deployment.py || {
    echo "Warning: Some deployment checks failed."
    echo "Continuing anyway..."
}

# Run the application
echo "Starting application..."
echo "The application will open in your default web browser shortly..."
echo "Press Ctrl+C to stop the application when done."
echo ""
streamlit run cloud_deploy_app_main.py
