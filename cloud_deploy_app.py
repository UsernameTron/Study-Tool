import streamlit as st
import json
import os
import base64
from datetime import datetime
import pandas as pd
import numpy as np
import uuid
import matplotlib.pyplot as plt
import altair as alt

# Import custom modules
from tabbed_interface import tabbed_study_interface
from search_utils import index_content, search_content, preprocess_text
from interactive_diagrams import lymph_node_interactive, respiratory_system_interactive, digestive_system_interactive
from simulations import respiratory_experiment_simulation, co2_reaction_simulation, simulations_page
from user_progress import load_user_progress, update_quiz_history, update_viewed_section

# Page configuration
st.set_page_config(
    page_title="Anatomy Study App",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom theme using CSS
def apply_custom_theme():
    with open("static/css/custom.css", "r") as css_file:
        css = css_file.read()
    
    # Inject CSS
    st.markdown(f"""
    <style>
    {css}
    </style>
    """, unsafe_allow_html=True)
    
    # Set dark/light mode classes
    if st.session_state.get("dark_mode", False):
        st.markdown("""
        <script>
        document.body.classList.add('dark-theme');
        </script>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <script>
        document.body.classList.remove('dark-theme');
        </script>
        """, unsafe_allow_html=True)

# Load quiz data
@st.cache_data
def load_quiz_data(difficulty="intermediate"):
    with open('data/enhanced_quizzes.json', 'r', encoding='utf-8') as f:
        all_quizzes = json.load(f)
        return all_quizzes.get(difficulty, all_quizzes.get("intermediate"))

# Sidebar navigation and elements
def sidebar_elements():
    st.sidebar.title("Anatomy Study App")
    
    # Theme selector
    theme_col1, theme_col2 = st.sidebar.columns([1, 3])
    with theme_col1:
        st.write("Theme:")
    with theme_col2:
        # Check if streamlit version supports toggle
        try:
            # Try to use toggle
            dark_mode = st.toggle("Dark Mode", value=st.session_state.get("dark_mode", False), key="toggle_theme")
            st.session_state.dark_mode = dark_mode
        except:
            # Fall back to checkbox for older Streamlit versions
            dark_mode = st.checkbox("Dark Mode", value=st.session_state.get("dark_mode", False), key="toggle_theme")
            st.session_state.dark_mode = dark_mode
    
    st.sidebar.markdown("---")
    
    # Navigation options
    selected = st.sidebar.radio(
        "Navigation",
        ["Home", "Lymphatic System", "Respiratory System", "Digestive System", 
         "Quiz", "Progress"]
    )
    
    # User information
    st.sidebar.markdown("---")
    
    # Show user progress summary
    if "user_id" in st.session_state:
        user_progress = load_user_progress(st.session_state.user_id)
        
        st.sidebar.subheader("Your Progress")
        
        # Display mastery levels
        mastery_levels = user_progress.get("mastery_levels", {})
        mastery_names = {0: "Not Started", 1: "Beginner", 2: "Intermediate", 3: "Expert"}
        
        for system, level in mastery_levels.items():
            level_name = mastery_names.get(level, "Not Started")
            progress_pct = (level / 3) * 100  # 3 is max level
            
            st.sidebar.text(f"{system.capitalize()}: {level_name}")
            st.sidebar.progress(progress_pct / 100)
    
    # Search box
    st.sidebar.markdown("---")
    st.sidebar.subheader("Search")
    search_query = st.sidebar.text_input("Search study materials:", key="search_box")
    
    if search_query:
        search_results(search_query)
    
    return selected

# Search functionality
def search_results(search_query):
    """Display search results in the sidebar"""
    st.sidebar.markdown("### Search Results")
    
    # Search across all study materials
    sections = ["lymphatic", "respiratory", "digestive"]
    results = []
    
    for section in sections:
        try:
            with open(os.path.join('data', 'knowledge', f'{section}.html'), 'r', encoding='utf-8') as file:
                content = file.read()
                # Use basic string search for simplicity
                if search_query.lower() in content.lower():
                    results.append({
                        "section": section,
                        "title": f"{section.capitalize()} System"
                    })
        except Exception as e:
            st.sidebar.error(f"Error searching {section}: {str(e)}")
    
    if results:
        for i, result in enumerate(results):
            section = result["section"]
            title = result["title"]
            
            st.sidebar.markdown(f"<div class='search-result'>", unsafe_allow_html=True)
            st.sidebar.markdown(f"**{title}**", unsafe_allow_html=True)
            
            # Add a button to navigate to that section
            if st.sidebar.button(f"Go to {title}", key=f"search_{i}"):
                st.session_state['navigation'] = title
                st.rerun()
            
            st.sidebar.markdown("</div>", unsafe_allow_html=True)
    else:
        st.sidebar.info("No results found.")

# Initialize user data if not present
def initialize_user():
    if "user_id" not in st.session_state:
        # Generate a unique user ID
        user_id = str(uuid.uuid4())
        st.session_state.user_id = user_id

# Home page
def home_page():
    st.title("🔬 Anatomy Study Application")
    
    # Welcome message in a custom card
    st.markdown("""
    <div class="custom-card">
        <h2>Welcome to Your Interactive Anatomy Learning Experience!</h2>
        <p>This application offers comprehensive study materials on anatomical systems with interactive features, 
        quizzes, and visual learning tools. Select a study module or explore our interactive features.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main content options in a grid
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="custom-card">
            <h3>Study Materials</h3>
            <p>Comprehensive content on major anatomical systems with visual aids and detailed explanations.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
        st.subheader("Lymphatic System")
        st.write("Learn about the network of vessels, organs, and tissues that help maintain fluid balance and defend against infections.")
        if st.button("Study Lymphatic System", key="btn_lymphatic"):
            st.session_state['navigation'] = "Lymphatic System"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
        st.subheader("Respiratory System")
        st.write("Explore the system responsible for gas exchange between the body and the external environment.")
        if st.button("Study Respiratory System", key="btn_respiratory"):
            st.session_state['navigation'] = "Respiratory System"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
        st.subheader("Digestive System")
        st.write("Learn about how the body processes food, extracts nutrients, and eliminates waste.")
        if st.button("Study Digestive System", key="btn_digestive"):
            st.session_state['navigation'] = "Digestive System"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="custom-card">
            <h3>Interactive Learning</h3>
            <p>Engage with interactive diagrams, simulations, and quizzes to enhance your understanding.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
        st.subheader("Knowledge Quizzes")
        st.write("Test your understanding with various question types and difficulty levels.")
        
        # Quick options for different quiz types
        quiz_col1, quiz_col2, quiz_col3 = st.columns(3)
        with quiz_col1:
            if st.button("Beginner Quiz", key="quiz_beginner"):
                st.session_state['navigation'] = "Quiz"
                st.session_state['quiz_difficulty'] = "beginner"
                st.rerun()
        with quiz_col2:
            if st.button("Intermediate Quiz", key="quiz_intermediate"):
                st.session_state['navigation'] = "Quiz"
                st.session_state['quiz_difficulty'] = "intermediate"
                st.rerun()
        with quiz_col3:
            if st.button("Advanced Quiz", key="quiz_advanced"):
                st.session_state['navigation'] = "Quiz"
                st.session_state['quiz_difficulty'] = "advanced"
                st.rerun()
                
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
        st.subheader("Progress Tracking")
        st.write("Monitor your learning progress across different anatomical systems.")
        if st.button("View Your Progress", key="btn_progress"):
            st.session_state['navigation'] = "Progress"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Recent activity and progress summary
    if "user_id" in st.session_state:
        st.markdown("---")
        st.subheader("Your Recent Activity")
        
        user_progress = load_user_progress(st.session_state.user_id)
        quiz_history = user_progress.get("quiz_history", [])
        
        if quiz_history:
            # Get the most recent 5 quiz results
            recent_quizzes = sorted(quiz_history[-5:], key=lambda x: x["timestamp"], reverse=True)
            
            quiz_data = []
            for quiz in recent_quizzes:
                date = datetime.fromisoformat(quiz["timestamp"]).strftime("%Y-%m-%d %H:%M")
                score_pct = (quiz["score"] / quiz["total"]) * 100
                quiz_data.append({
                    "Date": date,
                    "Category": quiz["category"].capitalize(),
                    "Difficulty": quiz["difficulty"].capitalize(),
                    "Score": f"{quiz['score']}/{quiz['total']} ({score_pct:.0f}%)"
                })
            
            quiz_df = pd.DataFrame(quiz_data)
            st.dataframe(quiz_df, use_container_width=True)
        else:
            st.info("You haven't taken any quizzes yet. Start learning and test your knowledge!")
