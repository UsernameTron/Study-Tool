# Standard library imports
import os
import streamlit as st
import uuid

# Early initialization functions
def ensure_directories():
    """Ensure all required directories exist first"""
    dirs = [
        "data/user_progress",
        "static/images/histology/lymphatic",
        "static/images/histology/respiratory",
        "static/images/histology/digestive",
        "logs"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

# Run directory initialization
ensure_directories()

# Now import from application modules
from logging_config import configure_logging
logger = configure_logging()('main')

from user_progress import initialize_user_progress
from session_state import initialize_session_state
from cloud_deploy_app_progress import progress_page
from cloud_deploy_app_quiz import quiz_page, render_quiz_question
from cloud_deploy_app import sidebar_elements, apply_custom_theme, home_page, tabbed_study_interface

# Complete main function
def main():
    """Main application entry point"""
    logger.info("Starting application")
    
    # Initialize a user identifier if not present
    initialize_session_state()
    
    if "user_id" not in st.session_state or not st.session_state.user_id:
        user_id = str(uuid.uuid4())
        st.session_state.user_id = user_id
        initialize_user_progress(user_id)
        logger.info(f"Created new user: {user_id}")
    
    # Apply custom theme
    apply_custom_theme()
    
    # Display sidebar and get navigation selection
    selected = sidebar_elements()
    
    # Add debug logging
    logger.info(f"Navigation selection: {selected}")
    
    # Check if navigation has been overridden by state
    if 'navigation' in st.session_state:
        logger.info(f"Navigation override: {st.session_state['navigation']}")
        selected = st.session_state['navigation']
        # Don't delete the navigation state until after displaying the content
        # This prevents navigation loops. We'll delete it later, after the page is rendered.
        logger.info(f"Using navigation override: {selected}")
    
    # Display content based on selection
    if selected == "Home":
        home_page()
    elif selected == "Lymphatic System":
        tabbed_study_interface("lymphatic")
    elif selected == "Respiratory System":
        tabbed_study_interface("respiratory")
    elif selected == "Digestive System":
        tabbed_study_interface("digestive")
    elif selected == "Quiz":
        # Important: DO NOT clear navigation state for Quiz until user explicitly navigates away
        logger.info("Attempting to display quiz page")
        quiz_page()
        # DO NOT delete the navigation state here!
    elif selected == "Progress":
        progress_page()
    else:
        st.error("Invalid navigation selection")
        logger.error(f"Invalid navigation selection: {selected}")
    
    # Only clear navigation state AFTER this conditional block
    # and only if we're not on the Quiz page
    if 'navigation' in st.session_state and selected != "Quiz":
        logger.info(f"Clearing navigation state after rendering {selected}")
        del st.session_state['navigation']

# Run the application
if __name__ == "__main__":
    main()