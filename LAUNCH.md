# Launching the Anatomy Study App

This document provides instructions for launching the Anatomy Study App on your system.

## Quick Start

The easiest way to launch the application is using the desktop launcher:

1. Go to your Desktop
2. Double-click the `AnatomyStudyApp.command` file
3. The application will automatically:
   - Set up the required environment
   - Install any missing dependencies
   - Launch the application in your default web browser

## Manual Launch

If you prefer to launch the application manually:

1. Open Terminal
2. Navigate to the project directory:
   ```bash
   cd /Users/cpconnor/CascadeProjects/study_app
   ```

3. Activate the virtual environment:
   ```bash
   # If the virtual environment doesn't exist, create it
   python3 -m venv venv

   # Activate the environment
   source venv/bin/activate
   ```

4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Launch the application:
   ```bash
   streamlit run cloud_deploy_app_main.py
   ```

6. The application will open in your default web browser at http://localhost:8501

## Troubleshooting

If you encounter any issues when launching the application:

1. **Missing Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Port Already in Use:**
   Launch with a different port:
   ```bash
   streamlit run cloud_deploy_app_main.py --server.port 8502
   ```

3. **Permissions Issue with Desktop Launcher:**
   Reset permissions:
   ```bash
   chmod +x /Users/cpconnor/Desktop/AnatomyStudyApp.command
   ```

4. **Virtual Environment Issues:**
   Re-create the virtual environment:
   ```bash
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

## Cloud Access

If the application has been deployed to the cloud, it can be accessed at:

- **Render**: https://anatomy-study-app.onrender.com
- **Streamlit Cloud**: Check your Streamlit Cloud dashboard for the URL

No additional setup is required for cloud access; simply visit the URL in your web browser.
