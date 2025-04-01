# Create a new file: quiz_state.py
import streamlit as st
from logging_config import configure_logging

logger = configure_logging()('quiz_state')

def initialize_quiz_state():
    """Initialize quiz state variables if not already present"""
    quiz_state_vars = {
        "quiz_active": False,
        "quiz_submitted": False,
        "user_responses": {},
        "active_questions": [],
        "quiz_result": {"score": 0, "total": 0, "difficulty": "intermediate"},
        "quiz_category": None,
        "quiz_difficulty": "intermediate"
    }
    
    for key, default_value in quiz_state_vars.items():
        if key not in st.session_state:
            st.session_state[key] = default_value
            logger.info(f"Initialized quiz state variable: {key}")

def reset_quiz_state():
    """Reset quiz state to initial values"""
    st.session_state.quiz_active = False
    st.session_state.quiz_submitted = False
    st.session_state.user_responses = {}
    st.session_state.active_questions = []
    logger.info("Reset quiz state")

def is_quiz_active():
    """Check if quiz is active"""
    return st.session_state.get("quiz_active", False)

def is_quiz_submitted():
    """Check if quiz is submitted"""
    return st.session_state.get("quiz_submitted", False)

def activate_quiz(questions, difficulty):
    """Activate the quiz with selected questions"""
    st.session_state.quiz_active = True
    st.session_state.quiz_submitted = False
    st.session_state.user_responses = {}
    st.session_state.active_questions = questions
    st.session_state.quiz_result["difficulty"] = difficulty
    logger.info(f"Activated quiz with {len(questions)} questions, difficulty: {difficulty}")