import streamlit as st

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
        st.session_state.quiz_result = {"score": 0, "total": 0, "difficulty": "intermediate"}
    
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
            category = st.selectbox(
                "Select Topic", 
                ["Any", "lymphatic", "respiratory", "digestive"], 
                index=0 if "quiz_category" not in st.session_state else 
                    ["Any", "lymphatic", "respiratory", "digestive"].index(st.session_state.get("quiz_category", "Any"))
            )
            
            # Remove the temporary category selection if exists
            if "quiz_category" in st.session_state:
                del st.session_state.quiz_category
        
        with col2:
            # Difficulty selection
            difficulty_options = ["beginner", "intermediate", "advanced"]
            default_difficulty = st.session_state.get("quiz_difficulty", "intermediate")
            difficulty_index = difficulty_options.index(default_difficulty) if default_difficulty in difficulty_options else 1
            
            difficulty = st.selectbox(
                "Select Difficulty", 
                difficulty_options, 
                index=difficulty_index
            )
            
            # Clear temp session state
            if "quiz_difficulty" in st.session_state:
                del st.session_state.quiz_difficulty
        
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
                st.session_state.quiz_result["difficulty"] = difficulty
                
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
                st.session_state.quiz_result = {
                    "score": score, 
                    "total": total, 
                    "difficulty": st.session_state.quiz_result["difficulty"]
                }
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
                        "difficulty": st.session_state.quiz_result["difficulty"],
                        "score": score,
                        "total": total,
                        "question_types": question_types
                    }
                    
                    # Update progress
                    update_quiz_history(st.session_state.user_id, quiz_record, most_common_category)
                
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
