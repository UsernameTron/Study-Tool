import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
from collections import Counter
import os

# Get logger
from logging_config import configure_logging
logger = configure_logging()('quiz')

# Import the quiz state management
from quiz_state import (
    initialize_quiz_state, 
    reset_quiz_state, 
    is_quiz_active, 
    is_quiz_submitted,
    activate_quiz
)

# Fix imports for required functions
from cloud_deploy_app import load_quiz_data
from user_progress import update_quiz_history

def quiz_page():
    """Display the quiz interface with improved state management"""
    st.title("Knowledge Quiz")
    
    # Initialize quiz state
    initialize_quiz_state()
    logger.info("Quiz page function called")
    
    # Configuration mode
    if not is_quiz_active():
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
            category = st.selectbox(
                "Select Topic", 
                ["Any", "lymphatic", "respiratory", "digestive"],
                key="quiz_category_select"
            )
        
        with col2:
            # Difficulty selection
            difficulty = st.selectbox(
                "Select Difficulty", 
                ["beginner", "intermediate", "advanced"],
                index=1,
                key="quiz_difficulty_select"
            )
        
        # Number of questions
        num_questions = st.slider("Number of Questions", min_value=5, max_value=20, value=10, key="quiz_num_questions")
        
        # Question types
        question_types = st.multiselect(
            "Question Types",
            ["free_response", "multiple_choice", "matching", "identification"],
            default=["free_response", "multiple_choice", "matching", "identification"],
            key="quiz_question_types"
        )
        
        # CRITICAL: Use a key for the start button to ensure it's unique
        if st.button("Start Quiz", key="start_quiz_button"):
            logger.info(f"Starting quiz: {category}, {difficulty}, {num_questions} questions")
            try:
                # Load quiz data
                quiz_data = load_quiz_data(difficulty)
                
                # Filter questions by category if specified
                if category != "Any":
                    available_questions = [q for q in quiz_data["questions"] if q.get("category", "") == category]
                else:
                    available_questions = quiz_data["questions"]
                
                # Filter by selected question types
                available_questions = [q for q in available_questions if q.get("type", "free_response") in question_types]
                
                logger.info(f"Found {len(available_questions)} available questions")
                
                if len(available_questions) >= num_questions:
                    # Randomly select questions
                    import random
                    selected_questions = random.sample(available_questions, num_questions)
                    
                    # Activate the quiz
                    activate_quiz(selected_questions, difficulty)
                    logger.info("Quiz activated with selected questions")
                    
                    # Rerun to show active quiz
                    st.rerun()
                else:
                    st.error(f"Not enough questions available. Only {len(available_questions)} found.")
            except Exception as e:
                logger.error(f"Error starting quiz: {str(e)}")
                st.error(f"Error starting quiz: {str(e)}")
    
    # Active quiz mode
    elif is_quiz_active() and not is_quiz_submitted():
        logger.info("Showing active quiz")
        
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
        
        # Action buttons
        col1, col2 = st.columns([3, 1])
        
        with col2:
            # CRITICAL: Use a key for the submit button
            if st.button("Submit Quiz", key="submit_quiz_button"):
                logger.info("Quiz submitted")
                
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
                st.session_state.quiz_result = {
                    "score": score, 
                    "total": total, 
                    "difficulty": st.session_state.quiz_result["difficulty"]
                }
                st.session_state.quiz_submitted = True
                
                # Update user progress
                if "user_id" in st.session_state:
                    # Determine category
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
                    update_quiz_history(st.session_state.user_id, quiz_record, most_common_category)
                
                st.rerun()
        
        with col1:
            # CRITICAL: Use a key for the cancel button
            if st.button("Cancel Quiz", key="cancel_quiz_button"):
                logger.info("Quiz cancelled")
                reset_quiz_state()
                # Navigate back to home
                st.session_state.navigation = "Home"
                st.rerun()
    
    # Results mode
    elif is_quiz_active() and is_quiz_submitted():
        logger.info("Showing quiz results")
        
        score = st.session_state.quiz_result["score"]
        total = st.session_state.quiz_result["total"]
        percentage = (score / max(1, total)) * 100
        
        st.markdown(f"""
        <div class="custom-card">
            <h3>Quiz Results</h3>
            <p>You scored <strong>{score}/{total}</strong> ({percentage:.1f}%)</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display score gauge chart
        score_data = pd.DataFrame({
            'category': ['Score'],
            'value': [percentage]
        })
        
        score_chart = alt.Chart(score_data).mark_arc(
            innerRadius=50,
            outerRadius=80,
            startAngle=0,
            endAngle=alt.expr.arc(datum.value / 100)
        ).encode(
            theta='value:Q',
            color=alt.condition(
                alt.datum.value > 80,
                alt.value('#2ecc71'),
                alt.condition(
                    alt.datum.value > 50,
                    alt.value('#f39c12'),
                    alt.value('#e74c3c')
                )
            )
        ).properties(width=200, height=200)
        
        text = alt.Chart(score_data).mark_text(
            align='center',
            baseline='middle',
            fontSize=20
        ).encode(
            text=alt.Text('value:Q', format='.0f')
        )
        
        score_display = alt.layer(score_chart, text)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.altair_chart(score_display, use_container_width=True)
        
        # Show detailed results
        st.subheader("Detailed Results")
        
        for i, question in enumerate(st.session_state.active_questions):
            st.markdown(f"<div class='quiz-result-item'>", unsafe_allow_html=True)
            st.write(f"**Question {i+1}**")
            render_quiz_question(question, True, st.session_state.user_responses)
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Feedback based on score
        if percentage >= 80:
            st.success("Excellent work! You have a strong understanding of this topic.")
        elif percentage >= 60:
            st.info("Good job! You have a solid grasp of the material, but there's room for improvement.")
        else:
            st.warning("You might want to review this topic more. Focus on the questions you missed.")
        
        # Action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            # CRITICAL: Use a key for the button
            if st.button("Take Another Quiz", key="another_quiz_button"):
                logger.info("Taking another quiz")
                reset_quiz_state()
                st.rerun()
        
        with col2:
            # CRITICAL: Use a key for the button
            if st.button("Return to Home", key="return_home_button"):
                logger.info("Returning to home")
                reset_quiz_state()
                st.session_state.navigation = "Home"
                st.rerun()

def render_quiz_question(question, is_submitted=False, user_responses=None):
    """Render a quiz question with improved UI"""
    q_id = question["id"]
    q_type = question["type"]
    
    st.markdown(f"<div class='quiz-question'>", unsafe_allow_html=True)
    st.markdown(f"**{question['question']}**", unsafe_allow_html=True)
    
    # Free response questions
    if q_type == "free_response":
        if not is_submitted:
            # Use a unique key for each input
            input_key = f"input_{q_id}_{id(question)}"
            user_answer = st.text_input(
                "Your answer:", 
                key=input_key,
                value=user_responses.get(q_id, "") if user_responses else "",
            )
            if user_responses is not None:
                user_responses[q_id] = user_answer
        else:
            user_answer = user_responses.get(q_id, "")
            expected = question["answer"]
            is_correct = user_answer.lower().strip() == expected.lower().strip()
            
            st.text_input(
                "Your answer:", 
                value=user_answer,
                key=f"result_{q_id}_{id(question)}",
                disabled=True,
            )
            
            if is_correct:
                st.markdown(f"<span style='color: green; font-weight: bold;'>✓ Correct!</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span style='color: red; font-weight: bold;'>✗ Incorrect.</span>", unsafe_allow_html=True)
                st.markdown(f"**Expected answer:** {expected}", unsafe_allow_html=True)
    
    # Multiple choice questions
    elif q_type == "multiple_choice":
        if not is_submitted:
            selected = st.radio(
                "Select your answer:",
                question["options"],
                key=f"input_{q_id}_{id(question)}",
                index=None,
            )
            if user_responses is not None and selected is not None:
                user_responses[q_id] = selected
        else:
            user_answer = user_responses.get(q_id, "")
            expected = question["answer"]
            is_correct = user_answer == expected
            
            options = question["options"]
            selected_idx = options.index(user_answer) if user_answer in options else None
            
            st.radio(
                "Select your answer:",
                options,
                key=f"result_{q_id}_{id(question)}",
                index=selected_idx,
                disabled=True,
            )
            
            if is_correct:
                st.markdown(f"<span style='color: green; font-weight: bold;'>✓ Correct!</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span style='color: red; font-weight: bold;'>✗ Incorrect.</span>", unsafe_allow_html=True)
                st.markdown(f"**Expected answer:** {expected}", unsafe_allow_html=True)
    
    # Matching questions
    elif q_type == "matching":
        pairs = question["pairs"]
        items = [p["item"] for p in pairs]
        matches = [p["match"] for p in pairs]
        
        if not is_submitted:
            # Create a match dropdown for each item
            for i, pair in enumerate(pairs):
                item = pair["item"]
                
                # Use columns for better layout
                col1, col2 = st.columns([1, 3])
                
                with col1:
                    st.markdown(f"**{item}:**", unsafe_allow_html=True)
                
                with col2:
                    selected = st.selectbox(
                        f"Match for {item}",
                        matches,
                        key=f"input_{q_id}_{i}_{id(question)}",
                    )
                    
                    # Store the answer
                    if user_responses is not None and selected is not None:
                        if q_id not in user_responses:
                            user_responses[q_id] = {}
                        user_responses[q_id][item] = selected
        else:
            correct_count = 0
            total_pairs = len(pairs)
            
            for pair in pairs:
                item = pair["item"]
                expected = pair["match"]
                user_match = user_responses.get(q_id, {}).get(item, "")
                is_correct = user_match == expected
                
                if is_correct:
                    correct_count += 1
                    st.markdown(f"**{item}** → {user_match} <span style='color: green; font-weight: bold;'>✓</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"**{item}** → {user_match} <span style='color: red; font-weight: bold;'>✗</span>", unsafe_allow_html=True)
                    st.markdown(f"&nbsp;&nbsp;&nbsp;&nbsp;*Should be:* {expected}", unsafe_allow_html=True)
            
            # Overall result for matching
            if correct_count == total_pairs:
                st.markdown(f"<span style='color: green; font-weight: bold;'>All matches correct!</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span style='color: red; font-weight: bold;'>{correct_count}/{total_pairs} correct matches</span>", unsafe_allow_html=True)
    
    # Identification questions
    elif q_type == "identification":
        # Show the image
        image_path = question.get("image_path", "")
        if os.path.exists(image_path):
            st.image(image_path, caption="Identify the labeled structure")
        else:
            st.error(f"Image not found: {image_path}")
        
        if not is_submitted:
            user_answer = st.text_input(
                "Your identification:", 
                key=f"input_{q_id}_{id(question)}",
                value=user_responses.get(q_id, "") if user_responses else "",
            )
            if user_responses is not None:
                user_responses[q_id] = user_answer
        else:
            user_answer = user_responses.get(q_id, "")
            expected = question["answer"]
            is_correct = user_answer.lower().strip() == expected.lower().strip()
            
            st.text_input(
                "Your identification:", 
                value=user_answer,
                key=f"result_{q_id}_{id(question)}",
                disabled=True,
            )
            
            if is_correct:
                st.markdown(f"<span style='color: green; font-weight: bold;'>✓ Correct!</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span style='color: red; font-weight: bold;'>✗ Incorrect.</span>", unsafe_allow_html=True)
                st.markdown(f"**Expected answer:** {expected}", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    return True if is_submitted and q_id in user_responses else False

# Explicitly export the required functions
__all__ = ['quiz_page', 'render_quiz_question']