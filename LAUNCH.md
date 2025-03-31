# Launching the Anatomy Study App

This document provides comprehensive instructions for launching the Anatomy Study App on both local and cloud environments.

## Local Deployment

### Quick Start

The easiest way to launch the application is using the desktop launcher:

1. Go to your Desktop
2. Double-click the `Launch_Study_App.command` file
3. The application will automatically:
   - Set up the required environment
   - Install any missing dependencies
   - Launch the application in your default web browser

### Manual Launch

If you prefer to launch the application manually:

1. Open Terminal
2. Navigate to the project directory:
   ```bash
   cd /path/to/anatomy-study-app
   ```

3. Activate the virtual environment:
   ```bash
   # If the virtual environment doesn't exist, create it
   python3 -m venv venv

   # Activate the environment
   source venv/bin/activate   # On Windows: venv\Scripts\activate
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

### Troubleshooting Local Deployment

If you encounter any issues when launching the application locally:

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
   chmod +x /path/to/Desktop/Launch_Study_App.command
   ```

4. **Virtual Environment Issues:**
   Re-create the virtual environment:
   ```bash
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

5. **Missing Image Resources:**
   Verify image directories:
   ```bash
   python verify_deployment.py
   ```
   This will check for required resources and create placeholders if needed.

6. **Application Crashes on Startup:**
   Check the log files in the project directory for errors and ensure all required directories exist:
   ```bash
   mkdir -p data/user_progress static/images/histology/lymphatic static/images/histology/respiratory static/images/histology/digestive
   ```

## Cloud Deployment

### Deploying to Render

1. Push your code to GitHub:
   ```bash
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

2. Sign up or log in to [Render](https://render.com)

3. Create a new Web Service:
   - Connect your GitHub repository
   - Select the branch to deploy (usually `main`)
   - Render will automatically detect the `render.yaml` configuration
   - Click "Deploy"

4. Your application will be available at the URL provided by Render (typically `https://anatomy-study-app.onrender.com`)

### Deploying to Streamlit Cloud

1. Push your code to GitHub as described above

2. Go to [Streamlit Cloud](https://streamlit.io/cloud) and sign in with GitHub

3. Click "New app"

4. Configure your app:
   - Repository: Select your GitHub repository
   - Branch: Select the branch to deploy (usually `main`)
   - Main file path: `cloud_deploy_app_main.py`
   - Click "Deploy"

5. Your application will be available at the URL provided by Streamlit Cloud

### Cloud Access

Once deployed, the application can be accessed at:

- **Render**: Your custom URL (e.g., `https://anatomy-study-app.onrender.com`)
- **Streamlit Cloud**: Your assigned URL from the Streamlit dashboard

No additional setup is required for cloud access; simply visit the URL in your web browser.

### Troubleshooting Cloud Deployment

1. **Failed Deployment on Render:**
   - Check the build logs in the Render dashboard
   - Verify your `render.yaml` configuration is correct
   - Ensure all dependencies are properly specified in `requirements.txt`

2. **Failed Deployment on Streamlit Cloud:**
   - Check the deployment logs in Streamlit Cloud dashboard
   - Verify the entry point is correctly set to `cloud_deploy_app_main.py`
   - Check for any Python version compatibility issues

3. **Resource Limitations:**
   - Both Render and Streamlit Cloud have free tier limitations
   - Consider upgrading if you experience performance issues or timeouts

4. **Custom Domain Configuration:**
   - Both platforms support custom domains for professional deployments
   - Follow the platform-specific instructions for domain configuration
