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
