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
    with open('data/quizzes.json', 'r', encoding='utf-8') as f:
        all_quizzes = json.load(f)
        return all_quizzes.get(difficulty, all_quizzes.get("intermediate"))

# Load study content
@st.cache_data
def load_study_content(section):
    with open(os.path.join('data', 'knowledge', f'{section}.html'), 'r', encoding='utf-8') as file:
        return file.read()

# Navigation
def sidebar_elements():
    st.sidebar.title("Anatomy Study App")
    
    # Theme selector
    theme_col1, theme_col2 = st.sidebar.columns([1, 3])
    with theme_col1:
        st.write("Theme:")
    with theme_col2:
        if st.toggle("Dark Mode", value=st.session_state.get("dark_mode", False), key="toggle_theme"):
            st.session_state.dark_mode = True
        else:
            st.session_state.dark_mode = False
    
    st.sidebar.markdown("---")
    
    # Navigation options
    selected = st.sidebar.radio(
        "Navigation",
        ["Home", "Lymphatic System", "Respiratory System", "Digestive System", 
         "Quiz", "Interactive Diagrams", "Simulations", "Progress"]
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
    
    return selected

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
        st.subheader("Interactive Diagrams")
        st.write("Explore anatomical structures through interactive diagrams with detailed explanations.")
        if st.button("Open Interactive Diagrams", key="btn_diagrams"):
            st.session_state['navigation'] = "Interactive Diagrams"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
        st.subheader("Experimental Simulations")
        st.write("Engage with simulations based on real laboratory exercises to deepen your understanding.")
        if st.button("Try Simulations", key="btn_simulations"):
            st.session_state['navigation'] = "Simulations"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
        st.subheader("Knowledge Quizzes")
        st.write("Test your understanding with various question types at different difficulty levels.")
        if st.button("Take a Quiz", key="btn_quiz"):
            st.session_state['navigation'] = "Quiz"
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
            
            # Show a button to view full progress
            if st.button("View Full Progress Report", key="btn_progress"):
                st.session_state['navigation'] = "Progress"
                st.rerun()
        else:
            st.info("You haven't taken any quizzes yet. Start learning and test your knowledge!")

# Study page with visual learning components
def study_page(section):
    update_viewed_section(st.session_state.user_id, section.lower())
    
    if section == "Lymphatic System":
        content = load_study_content("lymphatic")
        st.title("Lymphatic System")
    elif section == "Respiratory System":
        content = load_study_content("respiratory")
        st.title("Respiratory System")
    elif section == "Digestive System":
        content = load_study_content("digestive")
        st.title("Digestive System")
    
    # Split into columns for content and visual aids
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Use CSS class for styling
        st.markdown(f'<div class="study-content">{content}</div>', unsafe_allow_html=True)
    
    with col2:
        st.subheader("Visual Learning")
        
        if section == "Lymphatic System":
            with st.expander("System Overview", expanded=True):
                st.image("static/images/lymph_node_base.png", caption="Lymphatic System Overview")
            
            with st.expander("Lymph Node Structure"):
                st.image("static/images/lymph_node_germinal_center.png", caption="Lymph Node with Germinal Center")
                
            with st.expander("Interactive Diagram"):
                st.write("Want to explore interactively?")
                if st.button("Open Lymphatic Interactive Diagram", key="open_lymph_diagram"):
                    st.session_state["navigation"] = "Interactive Diagrams"
                    st.session_state["current_diagram"] = "lymphatic"
                    st.rerun()
                
        elif section == "Respiratory System":
            with st.expander("System Overview", expanded=True):
                st.image("static/images/respiratory_base.png", caption="Respiratory System Overview")
            
            with st.expander("Alveoli Structure"):
                st.image("static/images/respiratory_alveoli.png", caption="Alveoli - Gas Exchange Units")
                
            with st.expander("Interactive Experiment"):
                st.write("Want to see how respiration changes during exercise?")
                if st.button("Open Respiratory Simulation", key="open_resp_sim"):
                    st.session_state["navigation"] = "Simulations"
                    st.session_state["current_simulation"] = "respiratory"
                    st.rerun()
                
        elif section == "Digestive System":
            with st.expander("System Overview", expanded=True):
                st.image("static/images/digestive_base.png", caption="Digestive System Overview")
            
            with st.expander("Digestive Organs"):
                st.image("static/images/digestive_stomach.png", caption="Stomach Structure")
                
            with st.expander("Interactive Experiment"):
                st.write("Want to see digestive enzyme activity?")
                if st.button("Open Digestive Simulation", key="open_digest_sim"):
                    st.session_state["navigation"] = "Simulations"
                    st.session_state["current_simulation"] = "digestive"
                    st.rerun()
    
    # Add a quiz section at the bottom
    st.markdown("---")
    st.subheader("Test Your Knowledge")
    
    category = section.lower().split()[0]  # Extract just the system name
    
    # Select questions for this category
    all_questions = []
    for difficulty in ["beginner", "intermediate"]:
        quiz_data = load_quiz_data(difficulty)
        category_questions = [q for q in quiz_data["questions"] if q.get("category", "") == category]
        all_questions.extend(category_questions[:2])  # Add up to 2 questions from each difficulty
    
    if all_questions:
        st.write(f"Try these sample questions about the {section}:")
        
        # Show only free response and multiple choice questions in this quick quiz
        for i, q in enumerate(all_questions):
            if q["type"] in ["free_response", "multiple_choice"]:
                with st.expander(f"Question {i+1}: {q['question']}"):
                    if q["type"] == "multiple_choice":
                        st.radio("Select your answer:", q["options"], key=f"sample_q_{i}")
                        st.write(f"**Answer:** {q['answer']}")
                    else:
                        st.text_input("Your answer:", key=f"sample_q_{i}")
                        st.write(f"**Answer:** {q['answer']}")
        
        st.write("Want a complete quiz?")
        if st.button("Take Full Quiz", key="take_full_quiz"):
            st.session_state['navigation'] = "Quiz"
            st.session_state['quiz_category'] = category
            st.rerun()
    else:
        st.write("No quiz questions available for this topic.")

# Function to handle different quiz question types
def render_quiz_question(question, is_submitted=False, user_responses=None):
    q_id = question["id"]
    q_type = question["type"]
    
    st.markdown(f"<div class='quiz-question'>", unsafe_allow_html=True)
    st.markdown(f"**{question['question']}**", unsafe_allow_html=True)
    
    if q_type == "free_response":
        if not is_submitted:
            # Display input field if not submitted
            user_answer = st.text_input(
                "Your answer:", 
                key=f"input_{q_id}",
                value=user_responses.get(q_id, "") if user_responses else "",
                label_visibility="collapsed"
            )
            # Store the answer
            if user_responses is not None:
                user_responses[q_id] = user_answer
        else:
            # Show results if submitted
            user_answer = user_responses.get(q_id, "")
            expected = question["answer"]
            is_correct = user_answer.lower().strip() == expected.lower().strip()
            
            st.text_input(
                "Your answer:", 
                value=user_answer,
                key=f"result_{q_id}",
                disabled=True,
                label_visibility="collapsed"
            )
            
            if is_correct:
                st.markdown(f"<span class='correct-answer'>✓ Correct!</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span class='incorrect-answer'>✗ Incorrect.</span>", unsafe_allow_html=True)
                st.markdown(f"**Expected answer:** {expected}", unsafe_allow_html=True)
    
    elif q_type == "multiple_choice":
        if not is_submitted:
            # Display options if not submitted
            selected = st.radio(
                "Select your answer:",
                question["options"],
                key=f"input_{q_id}",
                index=None,
                label_visibility="collapsed"
            )
            # Store the answer
            if user_responses is not None and selected is not None:
                user_responses[q_id] = selected
        else:
            # Show results if submitted
            user_answer = user_responses.get(q_id, "")
            expected = question["answer"]
            is_correct = user_answer == expected
            
            # Show disabled radio with user's selection
            options = question["options"]
            selected_idx = options.index(user_answer) if user_answer in options else None
            
            st.radio(
                "Select your answer:",
                options,
                key=f"result_{q_id}",
                index=selected_idx,
                disabled=True,
                label_visibility="collapsed"
            )
            
            if is_correct:
                st.markdown(f"<span class='correct-answer'>✓ Correct!</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span class='incorrect-answer'>✗ Incorrect.</span>", unsafe_allow_html=True)
                st.markdown(f"**Expected answer:** {expected}", unsafe_allow_html=True)
    
    elif q_type == "matching":
        pairs = question["pairs"]
        items = [p["item"] for p in pairs]
        matches = [p["match"] for p in pairs]
        
        if not is_submitted:
            # Create a match dropdown for each item
            for i, pair in enumerate(pairs):
                item = pair["item"]
                
                selected = st.selectbox(
                    f"{item}",
                    matches,
                    key=f"input_{q_id}_{i}",
                    index=None
                )
                
                # Store the answer
                if user_responses is not None and selected is not None:
                    if q_id not in user_responses:
                        user_responses[q_id] = {}
                    user_responses[q_id][item] = selected
        else:
            # Show results
            correct_count = 0
            total_pairs = len(pairs)
            
            for pair in pairs:
                item = pair["item"]
                expected = pair["match"]
                user_match = user_responses.get(q_id, {}).get(item, "")
                is_correct = user_match == expected
                
                if is_correct:
                    correct_count += 1
                    st.markdown(f"**{item}** → {user_match} <span class='correct-answer'>✓</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"**{item}** → {user_match} <span class='incorrect-answer'>✗</span>", unsafe_allow_html=True)
                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;*Should be:* {expected}", unsafe_allow_html=True)
            
            # Overall result for matching
            if correct_count == total_pairs:
                st.markdown(f"<span class='correct-answer'>All matches correct!</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span class='incorrect-answer'>{correct_count}/{total_pairs} correct matches</span>", unsafe_allow_html=True)
    
    elif q_type == "identification":
        # Show the image
        st.image(question["image_path"], caption="Identify the labeled structure")
        
        if not is_submitted:
            # Display input field if not submitted
            user_answer = st.text_input(
                "Your identification:", 
                key=f"input_{q_id}",
                value=user_responses.get(q_id, "") if user_responses else "",
                label_visibility="collapsed"
            )
            # Store the answer
            if user_responses is not None:
                user_responses[q_id] = user_answer
        else:
            # Show results if submitted
            user_answer = user_responses.get(q_id, "")
            expected = question["answer"]
            is_correct = user_answer.lower().strip() == expected.lower().strip()
            
            st.text_input(
                "Your identification:", 
                value=user_answer,
                key=f"result_{q_id}",
                disabled=True,
                label_visibility="collapsed"
            )
            
            if is_correct:
                st.markdown(f"<span class='correct-answer'>✓ Correct!</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span class='incorrect-answer'>✗ Incorrect.</span>", unsafe_allow_html=True)
                st.markdown(f"**Expected answer:** {expected}", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    return True if is_submitted and q_id in user_responses else False
