# Ensure all required directories exist first
import os

# Directory initialization function to ensure proper deployment
def ensure_directories():
    dirs = [
        "data/user_progress",
        "static/images/histology/lymphatic",
        "static/images/histology/respiratory",
        "static/images/histology/digestive"
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

# Run directory initialization
ensure_directories()

# Main application continuation with all needed imports
from cloud_deploy_app_progress import progress_page
from cloud_deploy_app_quiz import quiz_page, render_quiz_question

# Complete main function
def main():
    """Main application entry point"""
    # Initialize a user identifier if not present
    initialize_user()
    
    # Apply custom theme
    apply_custom_theme()
    
    # Display sidebar and get navigation selection
    selected = sidebar_elements()
    
    # Check if navigation has been overridden by state
    if 'navigation' in st.session_state:
        selected = st.session_state['navigation']
        del st.session_state['navigation']
    
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
        quiz_page()
    elif selected == "Progress":
        progress_page()
    else:
        st.error("Invalid navigation selection")

# Run the application
if __name__ == "__main__":
    main()
