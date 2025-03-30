# Progress tracking page implementation
def progress_page():
    """Display user progress and analytics"""
    st.title("Learning Progress")
    
    if "user_id" not in st.session_state:
        st.warning("Please complete at least one quiz to see your progress.")
        return
    
    # Load user progress data
    user_progress = load_user_progress(st.session_state.user_id)
    
    # Create sections for different progress views
    st.markdown("""
    <div class="custom-card">
        <h3>Your Learning Journey</h3>
        <p>Track your progress across different anatomical systems and identify areas for improvement.</p>
    </div>
    """, unsafe_allow_html=True)
    
    tabs = st.tabs(["System Mastery", "Performance History", "Study Recommendations"])
    
    # System Mastery Tab
    with tabs[0]:
        st.subheader("System Mastery Levels")
        
        # Get mastery levels
        mastery_levels = user_progress.get("mastery_levels", {})
        systems = ["lymphatic", "respiratory", "digestive"]
        
        # Create mastery level data
        mastery_data = []
        for system in systems:
            level = mastery_levels.get(system, 0)
            mastery_data.append({
                "System": system.capitalize(),
                "Mastery": level,
                "Level": ["Not Started", "Beginner", "Intermediate", "Expert"][level]
            })
        
        # Display mastery levels as a chart
        mastery_df = pd.DataFrame(mastery_data)
        
        # Create a horizontal bar chart for mastery levels
        mastery_chart = alt.Chart(mastery_df).mark_bar().encode(
            x=alt.X('Mastery:Q', scale=alt.Scale(domain=[0, 3])),
            y=alt.Y('System:N', sort='-x'),
            color=alt.Color('Mastery:Q', scale=alt.Scale(
                domain=[0, 1, 2, 3],
                range=['#cccccc', '#f39c12', '#3498db', '#2ecc71']
            )),
            tooltip=['System', 'Level', 'Mastery']
        ).properties(
            width=600,
            height=200,
            title='System Mastery Levels'
        )
        
        # Add text labels
        text = mastery_chart.mark_text(
            align='left',
            baseline='middle',
            dx=5  # Slightly offset the text
        ).encode(
            text=alt.Text('Level:N')
        )
        
        # Combine chart with labels
        st.altair_chart(mastery_chart + text, use_container_width=True)
        
        # Calculate overall mastery
        if mastery_data:
            overall_mastery = sum(item["Mastery"] for item in mastery_data) / (len(mastery_data) * 3) * 100
            
            # Display overall mastery meter
            st.subheader("Overall Progress")
            st.progress(overall_mastery / 100)
            st.write(f"Overall mastery: {overall_mastery:.1f}%")
        else:
            st.info("No mastery data available yet. Complete quizzes to build your profile.")
    
    # Performance History Tab
    with tabs[1]:
        st.subheader("Quiz Performance History")
        
        # Get quiz history
        quiz_history = user_progress.get("quiz_history", [])
        
        if quiz_history:
            # Create DataFrame from quiz history
            history_data = []
            for quiz in quiz_history:
                date = datetime.fromisoformat(quiz["timestamp"]).strftime("%Y-%m-%d %H:%M")
                score_pct = (quiz["score"] / quiz["total"]) * 100 if quiz["total"] > 0 else 0
                history_data.append({
                    "Date": date,
                    "Timestamp": datetime.fromisoformat(quiz["timestamp"]),
                    "Category": quiz["category"].capitalize(),
                    "Difficulty": quiz["difficulty"].capitalize(),
                    "Score": score_pct,
                    "Points": f"{quiz['score']}/{quiz['total']}"
                })
            
            history_df = pd.DataFrame(history_data)
            
            # Show recent quiz results in a table
            st.markdown("### Recent Quiz Results")
            st.dataframe(
                history_df[["Date", "Category", "Difficulty", "Points", "Score"]].sort_values("Date", ascending=False),
                use_container_width=True
            )
            
            # Create a line chart showing progress over time
            if len(history_df) > 1:
                st.markdown("### Performance Over Time")
                
                # Create a selection for filtering by system
                system_selection = st.selectbox(
                    "Select system to track:",
                    ["All Systems"] + sorted(history_df["Category"].unique().tolist())
                )
                
                # Filter data based on selection
                if system_selection != "All Systems":
                    chart_data = history_df[history_df["Category"] == system_selection].copy()
                else:
                    chart_data = history_df.copy()
                
                # Sort by timestamp
                chart_data = chart_data.sort_values("Timestamp")
                
                # Create the chart
                if not chart_data.empty:
                    progress_chart = alt.Chart(chart_data).mark_line(point=True).encode(
                        x=alt.X('Timestamp:T', title='Date'),
                        y=alt.Y('Score:Q', title='Score (%)', scale=alt.Scale(domain=[0, 100])),
                        color=alt.Color('Category:N', title='System'),
                        tooltip=['Date:N', 'Category:N', 'Difficulty:N', 'Score:Q', 'Points:N']
                    ).properties(
                        width=600,
                        height=300,
                        title='Quiz Performance Over Time'
                    )
                    
                    st.altair_chart(progress_chart, use_container_width=True)
                    
                    # Calculate and display improvement metrics
                    if len(chart_data) >= 2:
                        first_score = chart_data.iloc[0]["Score"]
                        last_score = chart_data.iloc[-1]["Score"]
                        improvement = last_score - first_score
                        
                        if improvement > 0:
                            st.success(f"You've improved by {improvement:.1f}% since you started!")
                        elif improvement < 0:
                            st.warning(f"Your performance has decreased by {abs(improvement):.1f}%. Keep practicing!")
                        else:
                            st.info("Your performance has been consistent.")
                else:
                    st.info(f"No quiz data available for {system_selection}")
            else:
                st.info("Complete more quizzes to see your performance trends.")
        else:
            st.info("No quiz history available yet. Take quizzes to track your progress.")
    
    # Study Recommendations Tab
    with tabs[2]:
        st.subheader("Personalized Study Recommendations")
        
        # Get mastery levels and quiz history
        mastery_levels = user_progress.get("mastery_levels", {})
        quiz_history = user_progress.get("quiz_history", [])
        
        if mastery_levels and quiz_history:
            # Find weakest system
            weakest_system = min(mastery_levels.items(), key=lambda x: x[1])
            system_name = weakest_system[0]
            level = weakest_system[1]
            
            # Find recent performance
            recent_system_quizzes = [q for q in quiz_history if q["category"] == system_name][-3:] if quiz_history else []
            avg_score = sum(q["score"]/q["total"] for q in recent_system_quizzes) / len(recent_system_quizzes) if recent_system_quizzes else 0
            
            # Create recommendations based on mastery level and recent performance
            if level == 0:
                # Not started
                st.markdown("""
                <div class="recommendation-card">
                    <h4>🚀 Get Started with Your Learning</h4>
                    <p>You haven't begun studying some of the systems yet. Here's what we recommend:</p>
                    <ul>
                        <li>Start with the beginner content for each system</li>
                        <li>Take introductory quizzes to assess your baseline knowledge</li>
                        <li>Focus on understanding the basic structures and functions</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
                # Add direct links to get started
                for system, level in mastery_levels.items():
                    if level == 0:
                        st.markdown(f"**Start studying {system.capitalize()} System:**")
                        if st.button(f"Begin {system.capitalize()} System", key=f"begin_{system}"):
                            st.session_state.navigation = f"{system.capitalize()} System"
                            st.rerun()
            else:
                # Create focused recommendations for weakest system
                next_level = ["", "Beginner", "Intermediate", "Advanced"][min(level + 1, 3)]
                system_title = system_name.capitalize()
                
                st.markdown(f"""
                <div class="recommendation-card">
                    <h4>📝 Focused Study Plan: {system_title} System</h4>
                    <p>Based on your performance, we recommend focusing on the {system_title} System.</p>
                    <p>Current level: <strong>{["", "Beginner", "Intermediate", "Expert"][level]}</strong></p>
                    <p>Recent average score: <strong>{avg_score*100:.1f}%</strong></p>
                </div>
                """, unsafe_allow_html=True)
                
                # Create action buttons
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button(f"Study {system_title} System", key=f"study_{system_name}"):
                        st.session_state.navigation = f"{system_title} System"
                        st.rerun()
                
                with col2:
                    if st.button(f"Take {next_level} Quiz", key=f"quiz_{system_name}"):
                        st.session_state.quiz_category = system_name
                        st.session_state.quiz_difficulty = next_level.lower()
                        st.session_state.navigation = "Quiz"
                        st.rerun()
            
            # General study strategy based on overall progress
            overall_level = sum(mastery_levels.values()) / len(mastery_levels)
            
            if overall_level < 1:
                strategy_title = "Beginner Strategy"
                strategy_content = """
                <ul>
                    <li>Focus on learning the terminology and basic structures</li>
                    <li>Use the labeled diagrams to understand spatial relationships</li>
                    <li>Practice with beginner quizzes frequently</li>
                </ul>
                """
            elif overall_level < 2:
                strategy_title = "Intermediate Strategy"
                strategy_content = """
                <ul>
                    <li>Study the functional relationships between structures</li>
                    <li>Explore the histology slides to understand microscopic anatomy</li>
                    <li>Challenge yourself with intermediate difficulty quizzes</li>
                </ul>
                """
            else:
                strategy_title = "Advanced Strategy"
                strategy_content = """
                <ul>
                    <li>Focus on clinical correlations and pathophysiology</li>
                    <li>Use the interactive diagrams to solidify your understanding</li>
                    <li>Test your knowledge with advanced quizzes</li>
                </ul>
                """
            
            st.markdown(f"""
            <div class="recommendation-card">
                <h4>🎯 {strategy_title}</h4>
                {strategy_content}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Complete quizzes across different systems to receive personalized recommendations.")
