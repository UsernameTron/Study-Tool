import streamlit as st
import json
import os
import base64

# Page configuration
st.set_page_config(
    page_title="Study App",
    page_icon="📚",
    layout="wide"
)

# Load quiz data
@st.cache_data
def load_quiz_data():
    with open('data/quizzes.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# Load study content
@st.cache_data
def load_study_content(section):
    with open(os.path.join('data', 'knowledge', f'{section}.html'), 'r', encoding='utf-8') as file:
        return file.read()

# Navigation
def navigation():
    selected = st.sidebar.radio(
        "Navigation",
        ["Home", "Lymphatic System", "Respiratory System", "Digestive System", "Quiz"]
    )
    return selected

# Home page
def home_page():
    st.title("📚 Study Application")
    st.header("Welcome!")
    st.write("Select a study module from the sidebar or take a quiz to test your knowledge.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Lymphatic System")
        st.write("Learn about the network of vessels, organs, and tissues that help maintain fluid balance and defend against infections.")
        if st.button("Study Lymphatic System", key="btn_lymphatic"):
            st.session_state['navigation'] = "Lymphatic System"
            st.rerun()
    
    with col2:
        st.subheader("Respiratory System")
        st.write("Explore the system responsible for gas exchange between the body and the external environment.")
        if st.button("Study Respiratory System", key="btn_respiratory"):
            st.session_state['navigation'] = "Respiratory System"
            st.rerun()
    
    with col3:
        st.subheader("Digestive System")
        st.write("Learn about how the body processes food, extracts nutrients, and eliminates waste.")
        if st.button("Study Digestive System", key="btn_digestive"):
            st.session_state['navigation'] = "Digestive System"
            st.rerun()
    
    st.markdown("---")
    st.subheader("Test Your Knowledge")
    if st.button("Take Quiz", key="btn_quiz"):
        st.session_state['navigation'] = "Quiz"
        st.rerun()

# Study page
def study_page(section):
    if section == "Lymphatic System":
        content = load_study_content("lymphatic")
        st.title("Lymphatic System")
    elif section == "Respiratory System":
        content = load_study_content("respiratory")
        st.title("Respiratory System")
    elif section == "Digestive System":
        content = load_study_content("digestive")
        st.title("Digestive System")
    
    st.markdown(content, unsafe_allow_html=True)

# Quiz page
def quiz_page():
    st.title("Knowledge Quiz")
    st.write("Test your understanding of the systems you've studied.")
    
    quiz_data = load_quiz_data()
    
    # Initialize session state for quiz responses if not already done
    if 'quiz_responses' not in st.session_state:
        st.session_state.quiz_responses = {}
    
    submitted = False
    
    with st.form("quiz_form"):
        for q in quiz_data['questions']:
            qid = q['id']
            st.markdown(f"**{q['question']}**")
            
            # Pre-populate with any existing responses
            default_value = st.session_state.quiz_responses.get(qid, "")
            st.session_state.quiz_responses[qid] = st.text_input(
                "Your answer:", 
                key=f"input_{qid}", 
                value=default_value,
                label_visibility="collapsed"
            )
        
        submitted = st.form_submit_button("Submit Answers")
    
    # Display results after submission
    if submitted:
        st.markdown("### Results")
        correct_count = 0
        
        for q in quiz_data['questions']:
            qid = q['id']
            user_answer = st.session_state.quiz_responses.get(qid, "").strip().lower()
            expected = q['answer'].strip().lower()
            is_correct = user_answer == expected
            
            if is_correct:
                correct_count += 1
                st.success(f"**{q['question']}**  \nYour answer: {st.session_state.quiz_responses.get(qid, '')}  \n✅ Correct!")
            else:
                st.error(f"**{q['question']}**  \nYour answer: {st.session_state.quiz_responses.get(qid, '')}  \n❌ Incorrect. Expected: {q['answer']}")
        
        # Show overall score
        st.markdown(f"### Your Score: {correct_count}/{len(quiz_data['questions'])}")
        
        if correct_count == len(quiz_data['questions']):
            st.balloons()
            st.success("Perfect score! Excellent work! 🎉")
        elif correct_count >= len(quiz_data['questions']) * 0.8:
            st.success("Great job! You're doing well! 👍")
        elif correct_count >= len(quiz_data['questions']) * 0.6:
            st.info("Good effort! Keep studying to improve. 📚")
        else:
            st.warning("You may need more study time. Review the material and try again. 📖")
        
        # Button to retake quiz
        if st.button("Retake Quiz"):
            st.session_state.quiz_responses = {}
            st.rerun()

# Main app
def main():
    # Initialize session state for navigation if not already done
    if 'navigation' not in st.session_state:
        st.session_state['navigation'] = "Home"
    
    # Allow sidebar navigation to update the current page
    sidebar_selection = navigation()
    if sidebar_selection != st.session_state['navigation']:
        st.session_state['navigation'] = sidebar_selection
        st.rerun()
    
    # Display the currently selected page
    if st.session_state['navigation'] == "Home":
        home_page()
    elif st.session_state['navigation'] == "Lymphatic System":
        study_page("Lymphatic System")
    elif st.session_state['navigation'] == "Respiratory System":
        study_page("Respiratory System")
    elif st.session_state['navigation'] == "Digestive System":
        study_page("Digestive System")
    elif st.session_state['navigation'] == "Quiz":
        quiz_page()

if __name__ == "__main__":
    main()
