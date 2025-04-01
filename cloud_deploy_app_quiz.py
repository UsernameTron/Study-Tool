import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from collections import Counter
import logging

# Get logger
from logging_config import configure_logging
logger = configure_logging()('quiz')

# Import required functions
from user_progress import update_quiz_history
from cloud_deploy_app import load_quiz_data

# Helper functions for quiz state management
def reset_quiz_state():
    """Reset quiz state to initial configuration mode"""
    st.session_state.quiz_active = False
    st.session_state.quiz_submitted = False
    st.session_state.user_responses = {}
    st.session_state.active_questions = []

def set_quiz_active(questions, difficulty):
    """Set quiz to active state with selected questions"""
    st.session_state.quiz_active = True
    st.session_state.quiz_submitted = False
    st.session_state.user_responses = {}
    st.session_state.active_questions = questions
    st.session_state.quiz_result = {"score": 0, "total": 0, "difficulty": difficulty}

def quiz_page():
    """Display the quiz interface with proper state management"""
    st.title("Knowledge Quiz")
    
    # Log that we've reached the quiz page
    logger.info("Quiz page function called")
    
    # Initialize session state variables for quiz if needed
    if "quiz_active" not in st.session_state:
        st.session_state.quiz_active = False
    if "quiz_submitted" not in st.session_state:
        st.session_state.quiz_submitted = False
    if "user_responses" not in st.session_state:
        st.session_state.user_responses = {}
    if "active_questions" not in st.session_state:
        st.session_state.active_questions = []
    if "quiz_result" not in st.session_state:
        st.session_state.quiz_result = {"score": 0, "total": 0, "difficulty": "intermediate"}
    
    # If not in active quiz, show configuration options
    if not st.session_state.quiz_active:
        logger.info("Showing quiz configuration")
        st.markdown("""
        <div class="custom-card">
            <h3>Test Your Knowledge</h3>
            <p>Configure your quiz options below and click Start Quiz to begin.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Quiz category selection
            category_options = ["Any", "lymphatic", "respiratory", "digestive"]
            default_index = 0
            
            if "quiz_category" in st.session_state and st.session_state.quiz_category in category_options:
                default_index = category_options.index(st.session_state.quiz_category)
                
            category = st.selectbox(
                "Select Topic", 
                category_options,
                index=default_index
            )
            
            # Store selected category
            if "quiz_category" in st.session_state:
                del st.session_state.quiz_category
        
        with col2:
            # Difficulty selection
            difficulty_options = ["beginner", "intermediate", "advanced"]
            default_difficulty = st.session_state.get("quiz_difficulty", "intermediate")
            
            try:
                difficulty_index = difficulty_options.index(default_difficulty)
            except ValueError:
                difficulty_index = 1  # Default to intermediate
                
            difficulty = st.selectbox(
                "Select Difficulty", 
                difficulty_options, 
                index=difficulty_index
            )
        
        # Number of questions
        num_questions = st.slider("Number of Questions", min_value=5, max_value=20, value=10)
        
        # Question types
        question_types = st.multiselect(
            "Question Types",
            ["free_response", "multiple_choice", "matching", "identification"],
            default=["free_response", "multiple_choice", "matching", "identification"]
        )
        
        # Start quiz button - critical section
        if st.button("Start Quiz"):
            logger.info(f"Starting quiz: category={category}, difficulty={difficulty}")
            try:
                # Load quiz data
                quiz_data = load_quiz_data(difficulty)
                logger.info(f"Loaded quiz data: {len(quiz_data['questions'])} questions available")
                
                # Filter questions by category if specified
                if category != "Any":
                    available_questions = [q for q in quiz_data["questions"] if q.get("category", "") == category]
                else:
                    available_questions = quiz_data["questions"]
                
                # Filter by selected question types
                available_questions = [q for q in available_questions if q.get("type", "free_response") in question_types]
                logger.info(f"Filtered to {len(available_questions)} questions")
                
                if len(available_questions) >= num_questions:
                    # Randomly select questions
                    import random
                    selected_questions = random.sample(available_questions, num_questions)
                    
                    # Set up the quiz
                    st.session_state.quiz_active = True
                    st.session_state.quiz_submitted = False
                    st.session_state.user_responses = {}
                    st.session_state.active_questions = selected_questions
                    st.session_state.quiz_result["difficulty"] = difficulty
                    
                    # Important: Don't call st.rerun() yet - finish the function first
                    logger.info("Quiz setup complete, state updated")
                else:
                    st.error(f"Not enough questions available with the selected criteria. Only {len(available_questions)} questions found.")
            except Exception as e:
                logger.error(f"Error starting quiz: {str(e)}")
                st.error(f"Error starting quiz: {str(e)}")
        
        # After all configuration is complete, trigger rerun if needed
        if st.session_state.quiz_active:
            logger.info("Rerunning after quiz activation")
            st.rerun()
    
    # If in active quiz, show questions
    elif st.session_state.quiz_active and not st.session_state.quiz_submitted:
        logger.info("Showing active quiz questions")
        # Show questions
        st.markdown("""
        <div class="custom-card">
            <h3>Quiz in Progress</h3>
            <p>Answer all questions and submit your responses when done.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display questions
        for i, question in enumerate(st.session_state.active_questions):
            st.subheader(f"Question {i+1}")
            render_quiz_question(question, False, st.session_state.user_responses)
        
        # Submit/cancel buttons
        submit_col1, submit_col2 = st.columns([3, 1])
        
        with submit_col2:
            if st.button("Submit Quiz", key="submit_quiz_button", use_container_width=True):
                logger.info("Quiz submitted")
                # Calculate score
                score = 0
                total = len(st.session_state.active_questions)
                
                # Score calculation logic
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
                st.session_state.quiz_result = {
                    "score": score, 
                    "total": total, 
                    "difficulty": st.session_state.quiz_result["difficulty"]
                }
                st.session_state.quiz_submitted = True
                
                # Update user progress
                if "user_id" in st.session_state:
                    # Determine category (most common category among questions)
                    categories = [q.get("category", "general") for q in st.session_state.active_questions]
                    most_common_category = Counter(categories).most_common(1)[0][0]
                    
                    # Format for progress tracking
                    quiz_record = {
                        "timestamp": datetime.now().isoformat(),
                        "category": most_common_category,
                        "difficulty": st.session_state.quiz_result["difficulty"],
                        "score": score,
                        "total": total,
                        "question_types": question_types
                    }
                    
                    # Update progress
                    try:
                        update_quiz_history(st.session_state.user_id, quiz_record, most_common_category)
                        logger.info(f"User progress updated: {st.session_state.user_id}")
                    except Exception as e:
                        logger.error(f"Error updating progress: {str(e)}")
        
        with submit_col1:
            if st.button("Cancel Quiz", key="cancel_quiz_button", use_container_width=True):
                logger.info("Quiz cancelled")
                reset_quiz_state()
        
        # After all quiz interaction is complete, trigger rerun if needed
        if st.session_state.quiz_submitted or not st.session_state.quiz_active:
            logger.info("Rerunning after quiz submission/cancellation")
            st.rerun()
    
    # If quiz submitted, show results
    elif st.session_state.quiz_active and st.session_state.quiz_submitted:
        logger.info("Showing quiz results")
        # Show results
        score = st.session_state.quiz_result["score"]
        total = st.session_state.quiz_result["total"]
        percentage = (score / max(1, total)) * 100  # Prevent division by zero
        
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
        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
        st.subheader("Detailed Results")
        
        for i, question in enumerate(st.session_state.active_questions):
            st.markdown(f"<div class='quiz-result-item'>", unsafe_allow_html=True)
            st.write(f"**Question {i+1}**")
            render_quiz_question(question, True, st.session_state.user_responses)
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Provide feedback based on score
        st.markdown("<div class='custom-card'>", unsafe_allow_html=True)
        
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
                logger.info("Resetting quiz for another attempt")
                reset_quiz_state()
        
        with col2:
            if st.button("Return to Home"):
                logger.info("Returning to home after quiz")
                reset_quiz_state()
                st.session_state.navigation = "Home"
        
        # After all result interaction is complete, trigger rerun if needed
        new_quiz = not st.session_state.quiz_active
        going_home = 'navigation' in st.session_state and st.session_state.navigation == "Home"
        
        if new_quiz or going_home:
            logger.info(f"Rerunning after quiz completion: new_quiz={new_quiz}, going_home={going_home}")
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

# Function to handle different quiz question types
def render_quiz_question(question, is_submitted=False, user_responses=None):
    """Render a quiz question with improved styling and layout"""
    q_id = question["id"]
    q_type = question["type"]
    
    st.markdown(f"<div class='quiz-question'>", unsafe_allow_html=True)
    st.markdown(f"**{question['question']}**", unsafe_allow_html=True)
    
    if q_type == "free_response":
        if not is_submitted:
            # Display input field with improved styling
            st.markdown("<div class='quiz-input-container'>", unsafe_allow_html=True)
            user_answer = st.text_input(
                "Your answer:", 
                key=f"input_{q_id}",
                value=user_responses.get(q_id, "") if user_responses else "",
                label_visibility="collapsed"
            )
            st.markdown("</div>", unsafe_allow_html=True)
            # Store the answer
            if user_responses is not None:
                user_responses[q_id] = user_answer
        else:
            # Show results with consistent styling
            user_answer = user_responses.get(q_id, "")
            expected = question["answer"]
            is_correct = user_answer.lower().strip() == expected.lower().strip()
            
            st.markdown("<div class='quiz-input-container'>", unsafe_allow_html=True)
            st.text_input(
                "Your answer:", 
                value=user_answer,
                key=f"result_{q_id}",
                disabled=True,
                label_visibility="collapsed"
            )
            st.markdown("</div>", unsafe_allow_html=True)
            
            if is_correct:
                st.markdown(f"<span class='correct-answer'>✓ Correct!</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span class='incorrect-answer'>✗ Incorrect.</span>", unsafe_allow_html=True)
                st.markdown(f"**Expected answer:** {expected}", unsafe_allow_html=True)
    
    elif q_type == "multiple_choice":
        if not is_submitted:
            # Display options with consistent styling
            st.markdown("<div class='quiz-input-container'>", unsafe_allow_html=True)
            selected = st.radio(
                "Select your answer:",
                question["options"],
                key=f"input_{q_id}",
                index=None,
                label_visibility="collapsed"
            )
            st.markdown("</div>", unsafe_allow_html=True)
            # Store the answer
            if user_responses is not None and selected is not None:
                user_responses[q_id] = selected
        else:
            # Show results with consistent styling
            user_answer = user_responses.get(q_id, "")
            expected = question["answer"]
            is_correct = user_answer == expected
            
            # Show disabled radio with user's selection
            options = question["options"]
            selected_idx = options.index(user_answer) if user_answer in options else None
            
            st.markdown("<div class='quiz-input-container'>", unsafe_allow_html=True)
            st.radio(
                "Select your answer:",
                options,
                key=f"result_{q_id}",
                index=selected_idx,
                disabled=True,
                label_visibility="collapsed"
            )
            st.markdown("</div>", unsafe_allow_html=True)
            
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
            # Create a match dropdown for each item with improved layout
            st.markdown("<div class='quiz-input-container'>", unsafe_allow_html=True)
            for i, pair in enumerate(pairs):
                item = pair["item"]
                
                st.markdown(f"<div class='matching-item'>", unsafe_allow_html=True)
                
                # Create three columns for better layout
                col1, col2, col3 = st.columns([3, 1, 6])
                
                with col1:
                    st.markdown(f"<div class='matching-item-label'>{item}</div>", unsafe_allow_html=True)
                
                with col2:
                    st.markdown("<div style='text-align: center; font-weight: bold;'>→</div>", unsafe_allow_html=True)
                
                with col3:
                    selected = st.selectbox(
                        f"Match for {item}",
                        matches,
                        key=f"input_{q_id}_{i}",
                        label_visibility="collapsed"
                    )
                
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Store the answer
                if user_responses is not None and selected is not None:
                    if q_id not in user_responses:
                        user_responses[q_id] = {}
                    user_responses[q_id][item] = selected
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            # Show results with improved layout
            st.markdown("<div class='quiz-input-container'>", unsafe_allow_html=True)
            correct_count = 0
            total_pairs = len(pairs)
            
            for pair in pairs:
                item = pair["item"]
                expected = pair["match"]
                user_match = user_responses.get(q_id, {}).get(item, "")
                is_correct = user_match == expected
                
                if is_correct:
                    correct_count += 1
                    st.markdown(f"<div class='matching-item'><div class='matching-item-label'>{item}</div> → {user_match} <span class='correct-answer'>✓</span></div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='matching-item'><div class='matching-item-label'>{item}</div> → {user_match} <span class='incorrect-answer'>✗</span></div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='margin-left: 20px; margin-bottom: 10px;'>Should be: {expected}</div>", unsafe_allow_html=True)
            
            # Overall result for matching
            if correct_count == total_pairs:
                st.markdown(f"<span class='correct-answer'>All matches correct!</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span class='incorrect-answer'>{correct_count}/{total_pairs} correct matches</span>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
    
    elif q_type == "identification":
        # Improved layout for identification questions
        st.markdown("<div class='identification-container'>", unsafe_allow_html=True)
        
        # Create columns for better layout
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # Show the image
            st.image(question["image_path"], caption="Identify the labeled structure", use_column_width=True)
        
        with col2:
            if not is_submitted:
                # Display input field with prompt
                st.markdown("<div class='identification-prompt'>What is this structure?</div>", unsafe_allow_html=True)
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
                # Show results with improved styling
                user_answer = user_responses.get(q_id, "")
                expected = question["answer"]
                is_correct = user_answer.lower().strip() == expected.lower().strip()
                
                st.markdown("<div class='identification-prompt'>Your answer:</div>", unsafe_allow_html=True)
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
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    return True if is_submitted and q_id in user_responses else False
