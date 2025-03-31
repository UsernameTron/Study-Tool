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
# Quiz page with multiple question types
def quiz_page():
    st.title("Knowledge Quiz")
    
    # Initialize session state variables for quiz
    if "quiz_active" not in st.session_state:
        st.session_state.quiz_active = False
    if "quiz_submitted" not in st.session_state:
        st.session_state.quiz_submitted = False
    if "user_responses" not in st.session_state:
        st.session_state.user_responses = {}
    if "active_questions" not in st.session_state:
        st.session_state.active_questions = []
    if "quiz_result" not in st.session_state:
        st.session_state.quiz_result = {"score": 0, "total": 0}
    
    # If not in active quiz, show configuration options
    if not st.session_state.quiz_active:
        st.markdown("""
        <div class="custom-card">
            <h3>Test Your Knowledge</h3>
            <p>Configure your quiz options below and click Start Quiz to begin.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Quiz category selection
            category = st.selectbox("Select Topic", 
                ["Any", "lymphatic", "respiratory", "digestive"], 
                index=0 if "quiz_category" not in st.session_state else 
                    ["Any", "lymphatic", "respiratory", "digestive"].index(st.session_state.get("quiz_category", "Any"))
            )
            
            # Remove the temporary category selection if exists
            if "quiz_category" in st.session_state:
                del st.session_state.quiz_category
        
        with col2:
            # Difficulty selection
            difficulty = st.selectbox("Select Difficulty", 
                ["beginner", "intermediate", "advanced"], 
                index=1
            )
        
        # Number of questions
        num_questions = st.slider("Number of Questions", min_value=5, max_value=20, value=10)
        
        # Question types
        question_types = st.multiselect(
            "Question Types",
            ["free_response", "multiple_choice", "matching", "identification"],
            default=["free_response", "multiple_choice", "matching", "identification"]
        )
        
        if st.button("Start Quiz"):
            # Load quiz data
            quiz_data = load_quiz_data(difficulty)
            
            # Filter questions by category if specified
            if category != "Any":
                available_questions = [q for q in quiz_data["questions"] if q.get("category", "") == category]
            else:
                available_questions = quiz_data["questions"]
            
            # Filter by selected question types
            available_questions = [q for q in available_questions if q.get("type", "free_response") in question_types]
            
            if len(available_questions) >= num_questions:
                # Randomly select questions
                import random
                selected_questions = random.sample(available_questions, num_questions)
                
                # Set up the quiz
                st.session_state.quiz_active = True
                st.session_state.quiz_submitted = False
                st.session_state.user_responses = {}
                st.session_state.active_questions = selected_questions
                
                # Rerun to show the quiz
                st.rerun()
            else:
                st.error(f"Not enough questions available with the selected criteria. Only {len(available_questions)} questions found.")
    
    # If in active quiz, show questions
    elif st.session_state.quiz_active and not st.session_state.quiz_submitted:
        # Show questions
        st.markdown("""
        <div class="custom-card">
            <h3>Quiz in Progress</h3>
            <p>Answer all questions and submit your responses when done.</p>
        </div>
        """, unsafe_allow_html=True)
        
        for i, question in enumerate(st.session_state.active_questions):
            st.subheader(f"Question {i+1}")
            render_quiz_question(question, False, st.session_state.user_responses)
        
        submit_col1, submit_col2 = st.columns([3, 1])
        
        with submit_col2:
            if st.button("Submit Quiz"):
                # Calculate score
                score = 0
                total = len(st.session_state.active_questions)
                
                for question in st.session_state.active_questions:
                    q_id = question["id"]
                    q_type = question["type"]
                    
                    if q_type == "free_response" or q_type == "identification":
                        if q_id in st.session_state.user_responses:
                            user_answer = st.session_state.user_responses[q_id].lower().strip()
                            expected = question["answer"].lower().strip()
                            if user_answer == expected:
                                score += 1
                    
                    elif q_type == "multiple_choice":
                        if q_id in st.session_state.user_responses:
                            user_answer = st.session_state.user_responses[q_id]
                            expected = question["answer"]
                            if user_answer == expected:
                                score += 1
                    
                    elif q_type == "matching":
                        if q_id in st.session_state.user_responses:
                            user_matches = st.session_state.user_responses[q_id]
                            correct_count = 0
                            total_pairs = len(question["pairs"])
                            
                            for pair in question["pairs"]:
                                item = pair["item"]
                                expected = pair["match"]
                                user_match = user_matches.get(item, "")
                                
                                if user_match == expected:
                                    correct_count += 1
                            
                            # Award partial credit for matching questions
                            if correct_count == total_pairs:
                                score += 1
                
                # Store the result
                st.session_state.quiz_result = {"score": score, "total": total}
                st.session_state.quiz_submitted = True
                
                # Update user progress
                if "user_id" in st.session_state:
                    # Determine category (most common category among questions)
                    from collections import Counter
                    categories = [q.get("category", "general") for q in st.session_state.active_questions]
                    most_common_category = Counter(categories).most_common(1)[0][0]
                    
                    # Format for progress tracking
                    quiz_record = {
                        "timestamp": datetime.now().isoformat(),
                        "category": most_common_category,
                        "difficulty": difficulty,
                        "score": score,
                        "total": total,
                        "question_types": question_types
                    }
                    
                    # Update progress
                    update_quiz_history(st.session_state.user_id, quiz_record)
                
                # Rerun to show results
                st.rerun()
        
        with submit_col1:
            if st.button("Cancel Quiz"):
                st.session_state.quiz_active = False
                st.rerun()
    
    # If quiz submitted, show results
    elif st.session_state.quiz_active and st.session_state.quiz_submitted:
        # Show results
        score = st.session_state.quiz_result["score"]
        total = st.session_state.quiz_result["total"]
        percentage = (score / total) * 100
        
        st.markdown(f"""
        <div class="custom-card">
            <h3>Quiz Results</h3>
            <p>You scored <strong>{score}/{total}</strong> ({percentage:.1f}%)</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Create a gauge chart for the score
        score_chart = alt.Chart(pd.DataFrame({
            'category': ['Score'],
            'value': [percentage]
        })).mark_arc(
            innerRadius=50,
            outerRadius=80,
            startAngle=0,
            endAngle=alt.expr.arc(datum.value / 100)
        ).encode(
            theta='value:Q',
            color=alt.condition(
                alt.datum.value > 80,
                alt.value('#2ecc71'),  # Green for high scores
                alt.condition(
                    alt.datum.value > 50,
                    alt.value('#f39c12'),  # Orange for medium scores
                    alt.value('#e74c3c')  # Red for low scores
                )
            )
        ).properties(width=200, height=200)
        
        # Add text in the center
        text = alt.Chart(pd.DataFrame({
            'category': ['Score'],
            'value': [percentage]
        })).mark_text(
            align='center',
            baseline='middle',
            fontSize=20
        ).encode(
            text=alt.Text('value:Q', format='.0f')
        )
        
        # Combine the charts
        score_display = alt.layer(score_chart, text)
        
        # Show the chart in a centered column
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.altair_chart(score_display, use_container_width=True)
        
        # Show detailed results for each question
        st.subheader("Detailed Results")
        
        for i, question in enumerate(st.session_state.active_questions):
            st.write(f"**Question {i+1}**")
            render_quiz_question(question, True, st.session_state.user_responses)
        
        # Provide feedback based on score
        st.markdown("---")
        
        if percentage >= 80:
            st.success("Excellent work! You have a strong understanding of this topic.")
        elif percentage >= 60:
            st.info("Good job! You have a solid grasp of the material, but there's room for improvement.")
        else:
            st.warning("You might want to review this topic more. Focus on the questions you missed.")
        
        # Show buttons for next actions
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Take Another Quiz"):
                st.session_state.quiz_active = False
                st.session_state.quiz_submitted = False
                st.rerun()
        
        with col2:
            if st.button("Return to Home"):
                st.session_state.quiz_active = False
                st.session_state.quiz_submitted = False
                st.session_state.navigation = "Home"
                st.rerun()

# Interactive diagrams page
def interactive_diagrams_page():
    st.title("Interactive Anatomy Diagrams")
    
    # Check if a specific diagram was requested
    current_diagram = st.session_state.get("current_diagram", None)
    
    if current_diagram:
        # If a specific diagram was requested, jump to it
        if current_diagram == "lymphatic":
            system = "Lymphatic System"
        elif current_diagram == "respiratory":
            system = "Respiratory System"
        elif current_diagram == "digestive":
            system = "Digestive System"
        else:
            system = None
        
        # Clear the selection to prevent auto-jumping on refresh
        del st.session_state.current_diagram
    else:
        # Otherwise, let the user choose
        system = st.selectbox(
            "Select Anatomical System",
            ["Lymphatic System", "Respiratory System", "Digestive System"]
        )
    
    st.markdown("""
    <div class="custom-card">
        <h3>Interactive Learning</h3>
        <p>Click on different parts of the diagram to learn more about each component.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display the appropriate interactive diagram
    if system == "Lymphatic System":
        lymph_node_interactive()
    elif system == "Respiratory System":
        respiratory_system_interactive()
    elif system == "Digestive System":
        digestive_system_interactive()

# Progress tracking page
def progress_page():
    st.title("Your Learning Progress")
    
    if "user_id" not in st.session_state:
        st.warning("You need to be logged in to track your progress.")
        return
    
    user_progress = load_user_progress(st.session_state.user_id)
    
    # Overview statistics
    st.markdown("""
    <div class="custom-card">
        <h3>Learning Overview</h3>
        <p>Track your progress across different anatomical systems and quiz performance.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Extract the data
    viewed_sections = user_progress.get("viewed_sections", [])
    quiz_history = user_progress.get("quiz_history", [])
    mastery_levels = user_progress.get("mastery_levels", {})
    
    # Create columns for summary stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Topics Explored", len(viewed_sections))
    
    with col2:
        if quiz_history:
            avg_score = sum(q["score"] / q["total"] * 100 for q in quiz_history) / len(quiz_history)
            st.metric("Average Quiz Score", f"{avg_score:.1f}%")
        else:
            st.metric("Average Quiz Score", "N/A")
    
    with col3:
        if mastery_levels:
            avg_mastery = sum(mastery_levels.values()) / len(mastery_levels)
            max_level = 3  # Maximum mastery level is 3
            mastery_pct = (avg_mastery / max_level) * 100
            st.metric("Overall Mastery", f"{mastery_pct:.1f}%")
        else:
            st.metric("Overall Mastery", "0.0%")
    
    # Mastery level visualization
    st.subheader("Mastery by System")
    
    mastery_names = {0: "Not Started", 1: "Beginner", 2: "Intermediate", 3: "Expert"}
    systems = ["lymphatic", "respiratory", "digestive"]
    
    for system in systems:
        level = mastery_levels.get(system, 0)
        level_name = mastery_names.get(level, "Not Started")
        progress_pct = (level / 3) * 100  # 3 is max level
        
        cols = st.columns([1, 3])
        with cols[0]:
            st.write(f"{system.capitalize()}:")
        with cols[1]:
            st.write(f"{level_name} ({progress_pct:.0f}%)")
            st.progress(progress_pct / 100)
    
    # Quiz history visualization
    st.subheader("Quiz Performance History")
    
    if quiz_history:
        # Prepare data for the chart
        quiz_data = []
        for i, quiz in enumerate(quiz_history):
            score_pct = (quiz["score"] / quiz["total"]) * 100
            date = datetime.fromisoformat(quiz["timestamp"]).strftime("%Y-%m-%d")
            
            quiz_data.append({
                "Quiz": i+1,
                "Date": date,
                "Score": score_pct,
                "System": quiz["category"].capitalize(),
                "Difficulty": quiz["difficulty"].capitalize()
            })
        
        quiz_df = pd.DataFrame(quiz_data)
        
        # Create an interactive line chart
        history_chart = alt.Chart(quiz_df).mark_line(point=True).encode(
            x=alt.X('Quiz:O', title='Quiz Number'),
            y=alt.Y('Score:Q', title='Score (%)', scale=alt.Scale(domain=[0, 100])),
            color=alt.Color('System:N', legend=alt.Legend(title="System")),
            tooltip=['Quiz', 'Date', 'Score', 'System', 'Difficulty']
        ).properties(
            width=600,
            height=300
        ).interactive()
        
        st.altair_chart(history_chart, use_container_width=True)
        
        # Show a table of quiz history
        st.subheader("Quiz History")
        
        # Display as a table
        quiz_display_df = quiz_df[['Quiz', 'Date', 'System', 'Difficulty', 'Score']]
        quiz_display_df = quiz_display_df.sort_values('Quiz', ascending=False)
        st.dataframe(quiz_display_df, use_container_width=True)
    else:
        st.info("You haven't taken any quizzes yet. Start taking quizzes to track your progress!")
    
    # Study history
    st.subheader("Study Session History")
    
    if viewed_sections:
        # Format the data
        viewed_data = []
        for section in viewed_sections:
            viewed_data.append({
                "System": section.capitalize(),
                "Last Viewed": "Recently"  # Simplified for now
            })
        
        viewed_df = pd.DataFrame(viewed_data)
        st.dataframe(viewed_df, use_container_width=True)
    else:
        st.info("You haven't viewed any study materials yet. Start exploring the anatomy systems!")

# Search functionality
def search_box():
    search_query = st.sidebar.text_input("Search study materials:")
    
    if search_query:
        st.sidebar.markdown("---")
        st.sidebar.subheader("Search Results")
        
        # Search across all study materials
        sections = ["lymphatic", "respiratory", "digestive"]
        results = []
        
        for section in sections:
            content = load_study_content(section)
            matches = search_content(content, search_query)
            
            for match in matches:
                results.append({"section": section, "context": match})
        
        if results:
            for i, result in enumerate(results[:5]):  # Show top 5 results
                section = result["section"].capitalize()
                context = result["context"]
                
                # Highlight the search term in the context
                highlighted_context = context.replace(
                    search_query, 
                    f"<span class='search-highlight'>{search_query}</span>"
                )
                
                st.sidebar.markdown(f"<div class='search-result'>", unsafe_allow_html=True)
                st.sidebar.markdown(f"**{section} System**", unsafe_allow_html=True)
                st.sidebar.markdown(f"{highlighted_context}...", unsafe_allow_html=True)
                
                # Add a button to navigate to that section
                if st.sidebar.button(f"Go to {section} System", key=f"search_{i}"):
                    st.session_state['navigation'] = f"{section} System"
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

# Main app
def main():
    # Initialize user data
    initialize_user()
    
    # Apply custom theme
    apply_custom_theme()
    
    # Add search box in sidebar
    search_box()
    
    # Get current navigation
    if "navigation" not in st.session_state:
        st.session_state.navigation = "Home"
    
    # Sidebar navigation
    selected = sidebar_elements()
    
    # Update navigation based on sidebar selection
    if selected != st.session_state.navigation:
        st.session_state.navigation = selected
        st.rerun()
    
    # Display the appropriate page
    if st.session_state.navigation == "Home":
        home_page()
    elif st.session_state.navigation == "Lymphatic System":
        study_page("Lymphatic System")
    elif st.session_state.navigation == "Respiratory System":
        study_page("Respiratory System")
    elif st.session_state.navigation == "Digestive System":
        study_page("Digestive System")
    elif st.session_state.navigation == "Quiz":
        quiz_page()
    elif st.session_state.navigation == "Interactive Diagrams":
        interactive_diagrams_page()
    elif st.session_state.navigation == "Simulations":
        simulations_page()
    elif st.session_state.navigation == "Progress":
        progress_page()

if __name__ == "__main__":
    main()
